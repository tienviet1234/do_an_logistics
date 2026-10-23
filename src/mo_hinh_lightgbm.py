"""GD D: LightGBM - 1 mo hinh chung cho ca 121 SKU (global model), cham bang khung chung src/danh_gia.py.
Dac trung:
- Biet truoc (lich, le, sale, khuyen mai, thong tin SKU): lay tu khung danh gia (KNOWN_AHEAD).
- Gia tri tre CHI tu 28 ngay tro ve truoc (lag >= tam du bao) -> du bao duoc ca 28 ngay toi tu 1 moc
  ma khong can du bao de quy; tinh lai ben trong tung moc tu du lieu qua khu (khong lay tu file dac trung).
- Bao, nang nong, ret dam, dich benh: KHONG dua vao (khong biet truoc 28 ngay).
Muc tieu: y_cham (bo ngay het hang, kho dong cua, don B2B dot bien).
Chay: python src/mo_hinh_lightgbm.py --thu   (1 moc test, do thoi gian)
      python src/mo_hinh_lightgbm.py         (validation: so sanh ham mat mat -> test voi ham tot hon)
Ket qua them: reports/lightgbm_quan_trong.csv (do quan trong dac trung, trung binh cac moc test)
"""
import os
import sys
import time

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, save_results, score, HORIZON, keep_awake, saved_result  # noqa: E402

CAT = ["ma_sku", "nhom_hang", "loai_mua_vu", "abc_train", "xyz_train", "loai_nhu_cau", "mua"]
NUM_KNOWN = ["thu", "cuoi_tuan", "ngay_trong_thang", "thang", "tuan_trong_nam", "ngay_trong_nam", "dau_thang",
             "cuoi_thang", "so_ngay_den_tet", "so_ngay_sau_tet", "trong_tuan_tet", "ngay_sale", "cua_so_sale",
             "khuyen_mai", "gia_ban", "lead_time_tb"]
LAG_FEATS = ["lag_28", "lag_35", "lag_42", "lag_49", "lag_364", "tb7_tre28", "tb28_tre28", "dlc28_tre28"]
OBJECTIVES = {"l2": {"objective": "regression"}, "tweedie": {"objective": "tweedie", "tweedie_variance_power": 1.2}}
BASE_PARAMS = dict(n_estimators=600, learning_rate=0.05, num_leaves=63, min_child_samples=50, subsample=0.8,
                   subsample_freq=1, colsample_bytree=0.8, random_state=42, n_jobs=4, verbose=-1)
_importance = []


def add_lags(hist, fut):
    """Gia tri tre >= 28 ngay, tinh tu cot y (qty_out) cua qua khu; tuong lai de trong (NaN) truoc khi dich."""
    a = pd.concat([hist[["ma_sku", "date", "y"]], fut[["ma_sku", "date"]].assign(y=np.nan)], ignore_index=True)
    a = a.sort_values(["ma_sku", "date"]).reset_index(drop=True)
    g = a.groupby("ma_sku").y
    for k in [28, 35, 42, 49, 364]:
        a[f"lag_{k}"] = g.shift(k)
    s28 = g.shift(HORIZON)
    gs = s28.groupby(a.ma_sku)
    a["tb7_tre28"] = gs.transform(lambda s: s.rolling(7, min_periods=4).mean())
    a["tb28_tre28"] = gs.transform(lambda s: s.rolling(28, min_periods=14).mean())
    a["dlc28_tre28"] = gs.transform(lambda s: s.rolling(28, min_periods=14).std())
    return a.drop(columns="y")


def make_model(obj, cats, sk_cols, keep_importance=False):
    feats = CAT + NUM_KNOWN + sk_cols + LAG_FEATS

    def prep(frame):
        x = frame[feats].copy()
        for c in CAT:
            x[c] = pd.Categorical(x[c], categories=cats[c])
        return x

    def fn(hist, fut):
        lags = add_lags(hist, fut)
        tr = hist.drop(columns=[c for c in LAG_FEATS if c in hist.columns]).merge(lags, on=["ma_sku", "date"])
        tr = tr[tr.y_cham.notna() & tr.lag_28.notna()]
        te = fut.merge(lags, on=["ma_sku", "date"], how="left")
        m = lgb.LGBMRegressor(**BASE_PARAMS, **OBJECTIVES[obj])
        m.fit(prep(tr), tr.y_cham)
        if keep_importance:
            _importance.append(pd.Series(m.booster_.feature_importance("gain"), index=feats))
        out = te[["date", "ma_sku", "la_ngay_nghi"]].copy()
        out["du_bao"] = np.where(out.la_ngay_nghi == 1, 0, m.predict(prep(te)))
        return out[["date", "ma_sku", "du_bao"]]
    return fn


if __name__ == "__main__":
    keep_awake(True)
    df = load()
    cats = {c: sorted(df[c].dropna().unique()) for c in CAT}
    sk_cols = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
    cols = ["WMAPE", "WMAPE_tuan", "WMAPE_A", "Bias_pct"]
    if "--thu" in sys.argv:
        t0 = time.time()
        p = backtest(make_model("tweedie", cats, sk_cols), df, folds("test")[:1], name="thu", verbose=False)
        print(f"1 moc: {time.time() - t0:.0f} giay")
        print(score(p, df)[["WMAPE", "Bias_pct"]].round(3).to_string(index=False))
        sys.exit()
    best, best_w = None, np.inf
    for obj in OBJECTIVES:
        name = f"lightgbm_{obj}"
        r = saved_result(name, "validation")
        if r is None:
            p = backtest(make_model(obj, cats, sk_cols), df, folds("validation"), name=f"{name}/validation")
            r = save_results(name, p, df, "validation", f"LightGBM chung 121 SKU, ham mat mat {obj}, lag >= 28")
        print(name, "validation", r[cols].round(3).to_string(index=False, header=False), flush=True)
        if r.WMAPE.iloc[0] < best_w:
            best, best_w = obj, r.WMAPE.iloc[0]
    print(f"Chon ham mat mat = {best} (WMAPE validation {best_w:.3f})", flush=True)
    p = backtest(make_model(best, cats, sk_cols, keep_importance=True), df, folds("test"), name="lightgbm/test")
    r = save_results("lightgbm", p, df, "test", f"LightGBM chung 121 SKU, {best} (chon tren validation), lag >= 28")
    print("lightgbm test", r[cols].round(3).to_string(index=False, header=False), flush=True)
    imp = pd.concat(_importance, axis=1).mean(axis=1)
    imp = (imp / imp.sum()).sort_values(ascending=False).rename("ty_trong").round(4)
    imp.to_csv("reports/lightgbm_quan_trong.csv", encoding="utf-8-sig", index_label="dac_trung")
    print("Top 12 dac trung (ty trong gain):")
    print(imp.head(12).to_string())
    keep_awake(False)
