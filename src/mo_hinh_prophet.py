"""GD D: Prophet tung SKU, cham bang khung chung src/danh_gia.py.
- Holidays: lich le / the thao (data/reference/lich_su_kien_prophet.csv, CHI su kien biet truoc) + sale 11.11, 12.12, Black Friday.
- Bien them (regressor): khuyen_mai (lich bo phan ban hang gui truoc).
- Bao lu, nang nong, ret dam, dich benh: KHONG dua vao (khong biet truoc 28 ngay).
- Moi SKU 1 mo hinh, hoc tren toan bo lich su den moc; chay song song nhieu loi CPU.
Chay: python src/mo_hinh_prophet.py --thu          (1 moc test, do thoi gian)
      python src/mo_hinh_prophet.py                (validation: so sanh additive/multiplicative -> test voi kieu tot hon)
"""
import logging
import os
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, save_results, score, UNFORESEEABLE, RESULT  # noqa: E402

REF = "data/reference"
SALE_WINDOW = (-1, 1)
WORKERS = 4                    # 11 tien trinh bi loi BrokenProcessPool (nghi het RAM); 4 chay on dinh


def holidays_table():
    lich = pd.read_csv(f"{REF}/lich_su_kien_prophet.csv", encoding="utf-8-sig", parse_dates=["ds"])
    bad = {c.replace("sk_", "") for c in UNFORESEEABLE}
    lich = lich[~lich.holiday.str.startswith("bao_") & ~lich.holiday.isin(bad)]
    hol = lich[["holiday", "ds", "lower_window", "upper_window"]]
    sales = []
    for y in range(2023, 2028):
        nov = pd.date_range(f"{y}-11-01", f"{y}-11-30")
        for name, d in [("sale_11_11", pd.Timestamp(y, 11, 11)), ("sale_12_12", pd.Timestamp(y, 12, 12)),
                        ("black_friday", nov[nov.weekday == 4][3])]:
            sales.append((name, d, SALE_WINDOW[0], SALE_WINDOW[1]))
    return pd.concat([hol, pd.DataFrame(sales, columns=hol.columns)], ignore_index=True)


def _quiet():
    logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
    logging.getLogger("prophet").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore")


def fit_one(args):
    """Hoc 1 SKU, tra ve du bao cho cac ngay tuong lai. (Ham cap module de chay song song tren Windows.)"""
    sku, train, future, hol, mode = args
    _quiet()
    from prophet import Prophet
    if train.y.notna().sum() < 30 or train.y.fillna(0).sum() == 0:
        return pd.DataFrame({"ma_sku": sku, "date": future.ds, "du_bao": 0.0})
    m = Prophet(holidays=hol, seasonality_mode=mode, yearly_seasonality=True,
                weekly_seasonality=True, daily_seasonality=False)
    m.add_regressor("khuyen_mai")
    m.fit(train)
    fc = m.predict(future)
    return pd.DataFrame({"ma_sku": sku, "date": fc.ds.values, "du_bao": fc.yhat.values})


def make_model(mode, pool, hol):
    def fn(hist, fut):
        h = hist.assign(y=hist.y_cham)[["ma_sku", "date", "y", "khuyen_mai"]].rename(columns={"date": "ds"})
        f = fut[["ma_sku", "date", "khuyen_mai"]].rename(columns={"date": "ds"})
        jobs = [(sku, g[["ds", "y", "khuyen_mai"]].reset_index(drop=True),
                 f[f.ma_sku == sku][["ds", "khuyen_mai"]].reset_index(drop=True), hol, mode)
                for sku, g in h.groupby("ma_sku")]
        out = pd.concat(pool.map(fit_one, jobs, chunksize=4), ignore_index=True)
        out = fut[["date", "ma_sku", "la_ngay_nghi"]].merge(out, on=["date", "ma_sku"], how="left")
        out["du_bao"] = np.where(out.la_ngay_nghi == 1, 0, out.du_bao.fillna(0))
        return out[["date", "ma_sku", "du_bao"]]
    return fn


def keep_awake(on=True):
    """Windows: khong cho may ngu khi dang chay (lan chay 23/10 bi treo ~9 gio vi may ngu giua chung)."""
    if os.name == "nt":
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


def saved_result(name, kind):
    """Ket qua da luu trong reports/ket_qua_mo_hinh.csv (de chay tiep, khong chay lai). --lam-lai de bo qua."""
    if "--lam-lai" in sys.argv or not os.path.exists(RESULT):
        return None
    r = pd.read_csv(RESULT, encoding="utf-8-sig")
    r = r[(r.mo_hinh == name) & (r.tap == kind)]
    return r if len(r) else None


if __name__ == "__main__":
    _quiet()
    keep_awake(True)
    df = load()
    hol = holidays_table()
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_quiet) as pool:
        if "--thu" in sys.argv:
            t0 = time.time()
            p = backtest(make_model("multiplicative", pool, hol), df, folds("test")[:1], name="thu", verbose=False)
            print(f"1 moc, {p.ma_sku.nunique()} SKU, {WORKERS} loi CPU: {time.time() - t0:.0f} giay")
            print(score(p, df)[["WMAPE", "Bias_pct"]].round(3).to_string(index=False))
            sys.exit()
        best, best_w = None, np.inf
        for mode in ["additive", "multiplicative"]:
            name = f"prophet_{mode[:4]}"
            r = saved_result(name, "validation")
            if r is not None:
                print(f"{name}: da co ket qua validation, bo qua (chay lai: --lam-lai)", flush=True)
            else:
                p = backtest(make_model(mode, pool, hol), df, folds("validation"), name=f"{name}/validation")
                r = save_results(name, p, df, "validation", f"Prophet {mode}, holidays + sale + khuyen mai")
            print(r[["mo_hinh", "tap", "WMAPE", "WMAPE_tuan", "WMAPE_A", "Bias_pct"]].round(3).to_string(index=False, header=False), flush=True)
            if r.WMAPE.iloc[0] < best_w:
                best, best_w = mode, r.WMAPE.iloc[0]
        print(f"Chon seasonality_mode = {best} (WMAPE validation {best_w:.3f})", flush=True)
        p = backtest(make_model(best, pool, hol), df, folds("test"), name="prophet/test")
        r = save_results("prophet", p, df, "test", f"Prophet {best} (chon tren validation), holidays + sale + khuyen mai")
        print(r[["mo_hinh", "tap", "WMAPE", "WMAPE_tuan", "WMAPE_A", "Bias_pct"]].round(3).to_string(index=False, header=False), flush=True)
    keep_awake(False)
