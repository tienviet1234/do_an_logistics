"""GD E vong 3: nang cap du bao LightGBM. Luat giu / bo ghi TRUOC khi chay: docs/10 muc 9.4.
  A - du bao theo tam: 3 mo hinh cho ngay thu 1-7, 8-14, 15-28 sau moc, moi mo hinh dung gia tri tre >= cuoi tam
      (tam 1-7 dung tre 7, 14, 21, 28...). Khong nhin truoc: ngay o+h chi dung so ban den ngay o.
  B - dac trung lich su kien (biet truoc): so ngay den / sau tung su kien; so ban cung ngay AM LICH nam truoc
      (dich theo khoang cach giua 2 Tet / 2 Trung thu gan nhat, vi 2 dip nay doi ngay duong lich moi nam).
  F - do tham so: 8 cau hinh boc ngau nhien (hat giong co dinh) tu luoi ghi san.
  ghep - ghep voi Prophet theo nhom XYZ, trong so do tren validation2 (nhu chon_mo_hinh.py vong 2).
Chay tung buoc (moi buoc in ket luan theo luat):
  python src/nang_cap_du_bao.py --buoc goc   (tai lap LightGBM cu, kiem tra code)
  python src/nang_cap_du_bao.py --buoc A | B | F | ghep | test
Ket qua: reports/ket_qua_mo_hinh.csv (ten lgb_v3_*), reports/du_bao/, reports/nang_cap_du_bao.md
"""
import json
import os
import sys
import time

import lightgbm as lgb
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, save_results, score, score_week, keep_awake, RESULT, PRED_DIR  # noqa: E402
from mo_hinh_lightgbm import CAT, NUM_KNOWN, OBJECTIVES, BASE_PARAMS  # noqa: E402

VAL = "validation2"
BUCKETS = [(1, 7), (8, 14), (15, 28)]
EVENTS = ["trung_thu", "noel", "halloween", "khai_giang", "valentine", "quoc_te_phu_nu", "phu_nu_vn", "nha_giao",
          "thieu_nhi", "le_30_4_2_9", "the_thao"]
CLIP_DEN, CLIP_SAU = 60, 14
NGUONG_WMAPE, NGUONG_BIAS = 0.005, 0.01                 # luat docs/10 muc 9.4
LUOI = dict(num_leaves=[31, 63, 127], learning_rate=[0.03, 0.05, 0.08], n_estimators=[400, 600, 1000],
            tweedie_variance_power=[1.1, 1.2, 1.3, 1.5], min_child_samples=[20, 50, 100], colsample_bytree=[0.6, 0.8, 1.0])
SEED_LUOI = 20261030
STATE = "reports/nang_cap_du_bao_trang_thai.json"          # cau hinh dang giu sau moi buoc
REPORT = "reports/nang_cap_du_bao.md"
GRID_W = np.round(np.arange(0, 1.01, 0.1), 1)


# ------------------------------------------------------------------ dac trung lich (tinh 1 lan theo ngay)
def lich_su_kien(dates):
    """Theo tung ngay: so ngay den / sau moi su kien biet truoc; do dich (ngay) de lay cung ngay am lich nam truoc."""
    ev = pd.read_csv("data/reference/lich_su_kien_prophet.csv", encoding="utf-8-sig", parse_dates=["ds"])
    d = pd.DatetimeIndex(sorted(dates))
    out = pd.DataFrame({"date": d})
    for e in EVENTS:
        x = np.sort(ev.loc[ev.holiday == e, "ds"].values)
        if not len(x):                                                      # du lieu khong co su kien nay: coi nhu rat xa
            out[f"den_{e}"], out[f"sau_{e}"] = float(CLIP_DEN), float(CLIP_SAU)
            continue
        i = np.searchsorted(x, d.values)                                    # lan xay ra tiep theo (>= ngay)
        den = np.where(i < len(x), (x[np.minimum(i, len(x) - 1)] - d.values) / np.timedelta64(1, "D"), np.inf)
        j = np.searchsorted(x, d.values, side="right") - 1                  # lan gan nhat da qua (<= ngay)
        sau = np.where(j >= 0, (d.values - x[np.maximum(j, 0)]) / np.timedelta64(1, "D"), np.inf)
        out[f"den_{e}"] = np.minimum(den, CLIP_DEN)
        out[f"sau_{e}"] = np.minimum(sau, CLIP_SAU)
    # cung ngay am lich nam truoc: moc am lich gan nhat (Tet hoac Trung thu) -> dich = moc do - lan truoc cung loai
    best_dist, shift = np.full(len(d), np.inf), np.full(len(d), np.nan)
    for e in ["tet", "trung_thu"]:
        x = np.sort(ev.loc[ev.holiday == e, "ds"].values)
        if not len(x):
            continue
        for k in range(1, len(x)):
            dist = np.abs((d.values - x[k]) / np.timedelta64(1, "D"))
            better = dist < best_dist
            best_dist = np.where(better, dist, best_dist)
            shift = np.where(better, (x[k] - x[k - 1]) / np.timedelta64(1, "D"), shift)
        dist0 = np.abs((d.values - x[0]) / np.timedelta64(1, "D"))      # lan dau: khong co lan truoc -> NaN
        nan0 = dist0 < best_dist
        best_dist, shift = np.where(nan0, dist0, best_dist), np.where(nan0, np.nan, shift)
    out["dich_am_lich"] = shift
    return out


def lag_feats(L, B):
    f = [f"lag_{L}", f"lag_{L + 7}", f"lag_{L + 14}", f"lag_{L + 21}", "lag_364", f"tb7_tre{L}", f"tb28_tre{L}", f"dlc28_tre{L}"]
    return f + (["lag_am", "tb7_am"] if B else [])


def add_lags(hist, fut, L, cal, B):
    """Gia tri tre >= L ngay tinh tu y (qty_out) qua khu; tuong lai la NaN truoc khi dich -> khong nhin truoc."""
    a = pd.concat([hist[["ma_sku", "date", "y"]], fut[["ma_sku", "date"]].assign(y=np.nan)], ignore_index=True)
    a = a.sort_values(["ma_sku", "date"]).reset_index(drop=True)
    g = a.groupby("ma_sku").y
    for k in [L, L + 7, L + 14, L + 21, 364]:
        a[f"lag_{k}"] = g.shift(k)
    gs = g.shift(L).groupby(a.ma_sku)
    a[f"tb7_tre{L}"] = gs.transform(lambda s: s.rolling(7, min_periods=4).mean())
    a[f"tb28_tre{L}"] = gs.transform(lambda s: s.rolling(28, min_periods=14).mean())
    a[f"dlc28_tre{L}"] = gs.transform(lambda s: s.rolling(28, min_periods=14).std())
    if B:
        tb7 = g.transform(lambda s: s.rolling(7, center=True, min_periods=4).mean())   # TB 7 ngay quanh 1 ngay
        a["tb7_tam"] = tb7
        a = a.merge(cal[["date", "dich_am_lich"]], on="date", how="left")
        a["ngay_am"] = a.date - pd.to_timedelta(a.dich_am_lich, unit="D")
        ref = a[["ma_sku", "date", "y", "tb7_tam"]].rename(columns={"date": "ngay_am", "y": "lag_am", "tb7_tam": "tb7_am"})
        a = a.merge(ref, on=["ma_sku", "ngay_am"], how="left")
        cut = hist.date.max()                         # chi lay ngay am lich da qua (cua so 7 ngay cung phai da qua)
        bad = a.ngay_am + pd.Timedelta(days=3) > cut
        a.loc[bad, ["lag_am", "tb7_am"]] = np.nan
        a = a.drop(columns=["tb7_tam", "dich_am_lich", "ngay_am"])
    return a.drop(columns="y")


def make_model(cfg, cats, sk_cols, cal):
    """cfg: A (dict bool), B (bool), params (dict LightGBM). Tra ham (hist, fut) -> du bao, dung trong backtest()."""
    ev_cols = [c for c in cal.columns if c.startswith(("den_", "sau_"))] if cfg["B"] else []
    buckets = BUCKETS if cfg["A"] else [(1, 28)]
    params = {**BASE_PARAMS, **OBJECTIVES["tweedie"], **cfg.get("params", {})}

    def fn(hist, fut):
        o = hist.date.max()
        h = hist.drop(columns=[c for c in hist.columns if c.startswith(("lag_", "tb7_tre", "tb28_tre", "dlc28_tre"))])
        if cfg["B"]:
            h, fut = h.merge(cal[["date"] + ev_cols], on="date", how="left"), fut.merge(cal[["date"] + ev_cols], on="date", how="left")
        outs = []
        for lo, hi in buckets:
            L = 28 if not cfg["A"] else hi
            lf = lag_feats(L, cfg["B"])
            feats = CAT + NUM_KNOWN + sk_cols + ev_cols + lf
            lags = add_lags(hist, fut, L, cal, cfg["B"])
            tr = h.merge(lags, on=["ma_sku", "date"])
            tr = tr[tr.y_cham.notna() & tr[f"lag_{L}"].notna()]
            te = fut[((fut.date - o).dt.days >= lo) & ((fut.date - o).dt.days <= hi)].merge(lags, on=["ma_sku", "date"], how="left")
            prep = lambda x: x[feats].assign(**{c: pd.Categorical(x[c], categories=cats[c]) for c in CAT})
            m = lgb.LGBMRegressor(**params)
            m.fit(prep(tr), tr.y_cham)
            out = te[["date", "ma_sku", "la_ngay_nghi"]].copy()
            out["du_bao"] = np.where(out.la_ngay_nghi == 1, 0, m.predict(prep(te)))
            outs.append(out[["date", "ma_sku", "du_bao"]])
        return pd.concat(outs, ignore_index=True)
    return fn


# ------------------------------------------------------------------ chi so phu: sai so tren tong lead time
def wmape_lead_time(pred):
    lt = pd.read_csv("data/reference/sku_master.csv", encoding="utf-8-sig").set_index("ma_sku").lead_time_tb
    p = pred.dropna(subset=["y_cham"])
    p = p[p.ngay_thu <= p.ma_sku.map(lt.round().clip(lower=1))]
    s = p.groupby(["moc", "ma_sku"])[["y_cham", "du_bao"]].sum()
    return (s.y_cham - s.du_bao).abs().sum() / s.y_cham.sum()


def chay(ten, cfg, df, cats, sk_cols, cal, kind=VAL, ghi_chu=""):
    t0 = time.time()
    p = backtest(make_model(cfg, cats, sk_cols, cal), df, folds(kind), name=f"{ten}/{kind}")
    r = save_results(ten, p, df, kind, ghi_chu or json.dumps(cfg, ensure_ascii=False))
    r = r.assign(WMAPE_LT=wmape_lead_time(p), giay=round(time.time() - t0))
    print(f"{ten:16s} {kind:11s} WMAPE {r.WMAPE.iloc[0]:.4f}  tuan {r.WMAPE_tuan.iloc[0]:.4f}  Bias {r.Bias_pct.iloc[0]:+.4f}  "
          f"Z {r.WMAPE_Z.iloc[0]:.3f}  lead time {r.WMAPE_LT.iloc[0]:.4f}  ({r.giay.iloc[0]} giay)", flush=True)
    return r


def giu(moi, cu):
    """Luat docs/10 muc 9.4: WMAPE giam >= 0,005 va |Bias| khong tang qua 1 diem %."""
    dw = cu.WMAPE.iloc[0] - moi.WMAPE.iloc[0]
    db = abs(moi.Bias_pct.iloc[0]) - abs(cu.Bias_pct.iloc[0])
    ok = dw >= NGUONG_WMAPE and db <= NGUONG_BIAS
    print(f"  -> WMAPE giam {dw:+.4f} (can >= {NGUONG_WMAPE}), |Bias| tang {db:+.4f} (toi da {NGUONG_BIAS}): "
          f"{'GIU' if ok else 'BO'}", flush=True)
    return ok


def doc_state():
    return json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {"cfg": {"A": False, "B": False, "params": {}},
                                                                                       "ten": "lgb_v3_goc", "nhat_ky": []}


def luu_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def kq(ten, kind=VAL):
    r = pd.read_csv(RESULT, encoding="utf-8-sig")
    return r[(r.mo_hinh == ten) & (r.tap == kind)]


def blend(p, l, w_by):
    x = p[["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]].merge(
        l[["date", "ma_sku", "moc", "du_bao"]], on=["date", "ma_sku", "moc"], suffixes=("_p", "_l"))
    w = x.xyz_train.map(w_by).astype(float)
    x["du_bao"] = w * x.du_bao_l + (1 - w) * x.du_bao_p
    return x.drop(columns=["du_bao_p", "du_bao_l"])


if __name__ == "__main__":
    buoc = sys.argv[sys.argv.index("--buoc") + 1] if "--buoc" in sys.argv else None
    keep_awake(True)
    df = load()
    cats = {c: sorted(df[c].dropna().unique()) for c in CAT}
    sk_cols = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
    cal = lich_su_kien(df.date.unique())
    st = doc_state()

    if buoc == "goc":
        r = chay("lgb_v3_goc", {"A": False, "B": False, "params": {}}, df, cats, sk_cols, cal)
        cu = kq("lightgbm_tweedie")
        print(f"  Tai lap LightGBM cu: WMAPE {r.WMAPE.iloc[0]:.4f} so voi {cu.WMAPE.iloc[0]:.4f} "
              f"({'KHOP' if abs(r.WMAPE.iloc[0] - cu.WMAPE.iloc[0]) < 1e-9 else 'LECH - kiem tra code!'})")
        st = {"cfg": {"A": False, "B": False, "params": {}}, "ten": "lgb_v3_goc", "nhat_ky": [["goc", float(r.WMAPE.iloc[0])]]}
    elif buoc in ("A", "B"):
        cfg = {**st["cfg"], buoc: True}
        ten = f"lgb_v3_{''.join(k for k in 'AB' if cfg[k])}"
        r = chay(ten, cfg, df, cats, sk_cols, cal)
        ok = giu(r, kq(st["ten"]))
        st["nhat_ky"].append([buoc, float(r.WMAPE.iloc[0]), "giu" if ok else "bo"])
        if ok:
            st["cfg"], st["ten"] = cfg, ten
    elif buoc == "F":
        rng = np.random.default_rng(SEED_LUOI)
        best_ten, best = st["ten"], kq(st["ten"])
        for i in range(8):
            params = {k: (v[rng.integers(len(v))]).item() if hasattr(v[0], "item") else v[rng.integers(len(v))] for k, v in LUOI.items()}
            params = {k: (float(v) if isinstance(v, float) else int(v)) for k, v in params.items()}
            cfg = {**st["cfg"], "params": params}
            r = chay(f"lgb_v3_F{i + 1}", cfg, df, cats, sk_cols, cal)
            print("  ", params)
            if r.WMAPE.iloc[0] < best.WMAPE.iloc[0]:
                best_ten, best, best_cfg = f"lgb_v3_F{i + 1}", r, cfg
        if best_ten != st["ten"]:
            ok = giu(best, kq(st["ten"]))
            st["nhat_ky"].append(["F", float(best.WMAPE.iloc[0]), best_ten, "giu" if ok else "bo"])
            if ok:
                st["cfg"], st["ten"] = best_cfg, best_ten
        else:
            print("  -> khong cau hinh nao tot hon: BO")
            st["nhat_ky"].append(["F", None, "bo"])
    elif buoc == "ghep":
        pv = pd.read_csv(f"{PRED_DIR}/prophet_addi_{VAL}.csv", parse_dates=["date", "moc"])
        lv = pd.read_csv(f"{PRED_DIR}/{st['ten']}_{VAL}.csv", parse_dates=["date", "moc"])
        w = {g: float(min(GRID_W, key=lambda w: score(blend(pv[pv.xyz_train == g], lv[lv.xyz_train == g], {g: w}), df).WMAPE.iloc[0]))
             for g in ["X", "Y", "Z"]}
        b = blend(pv, lv, w)
        r = save_results("ket_hop_v3", b, df, VAL, f"w LightGBM = {w} (do tren {VAL}); LightGBM: {st['ten']}")
        r = r.assign(WMAPE_LT=wmape_lead_time(b))
        print(f"ket_hop_v3 {VAL} WMAPE {r.WMAPE.iloc[0]:.4f} Bias {r.Bias_pct.iloc[0]:+.4f} Z {r.WMAPE_Z.iloc[0]:.3f} "
              f"lead time {r.WMAPE_LT.iloc[0]:.4f}  trong so {w}")
        ok = giu(r, kq("ket_hop_theo_nhom_v2"))
        st["nhat_ky"].append(["ghep", float(r.WMAPE.iloc[0]), w, "thay mo hinh dang dung" if ok else "giu mo hinh cu"])
        st["w"], st["thay"] = w, bool(ok)
    elif buoc == "test":
        assert "w" in st, "chay --buoc ghep truoc"
        r = chay(f"{st['ten']}", st["cfg"], df, cats, sk_cols, cal, kind="test")
        pt = pd.read_csv(f"{PRED_DIR}/prophet_test.csv", parse_dates=["date", "moc"])
        lt = pd.read_csv(f"{PRED_DIR}/{st['ten']}_test.csv", parse_dates=["date", "moc"])
        b = blend(pt, lt, st["w"])
        r = save_results("ket_hop_v3", b, df, "test", f"w LightGBM = {st['w']} (do tren {VAL}); LightGBM: {st['ten']}")
        print(f"ket_hop_v3 test WMAPE {r.WMAPE.iloc[0]:.4f} tuan {score_week(b):.4f} Bias {r.Bias_pct.iloc[0]:+.4f} "
              f"Z {r.WMAPE_Z.iloc[0]:.3f} lead time {wmape_lead_time(b):.4f}")
        st["nhat_ky"].append(["test", float(r.WMAPE.iloc[0])])
    elif buoc == "bao_cao":
        r = pd.read_csv(RESULT, encoding="utf-8-sig")
        cot = ["mo_hinh", "tap", "WMAPE", "WMAPE_tuan", "Bias_pct", "WMAPE_X", "WMAPE_Y", "WMAPE_Z", "WMAPE_A"]
        ds = ["lightgbm_tweedie", "lgb_v3_goc", "lgb_v3_A", "lgb_v3_AB"] + [f"lgb_v3_F{i}" for i in range(1, 9)] + \
             ["prophet_addi", "ket_hop_theo_nhom_v2", "ket_hop_v3"]
        v = r[(r.tap == VAL) & r.mo_hinh.isin(ds)].set_index("mo_hinh").reindex(ds).dropna(how="all").reset_index()
        lt = {}
        for m in v.mo_hinh:
            f = f"{PRED_DIR}/{m}_{VAL}.csv"
            if os.path.exists(f):
                lt[m] = wmape_lead_time(pd.read_csv(f, parse_dates=["date", "moc"]))
        v["WMAPE_lead_time"] = v.mo_hinh.map(lt)
        t = r[(r.tap == "test") & r.mo_hinh.isin(["lightgbm", st["ten"], "prophet", "ket_hop_theo_nhom_v2", "ket_hop_v3"])]
        lt_t = {m: wmape_lead_time(pd.read_csv(f"{PRED_DIR}/{m}_test.csv", parse_dates=["date", "moc"])) for m in t.mo_hinh
                if os.path.exists(f"{PRED_DIR}/{m}_test.csv")}
        t = t.assign(WMAPE_lead_time=t.mo_hinh.map(lt_t))
        L = ["# Nang cap du bao (GD E vong 3)", "", "Luat ghi truoc khi chay: docs/10 muc 9.4. Chon tren validation2, "
             "test chay 1 lan. Du lieu mo phong.", "", "## Nhat ky theo luat", ""]
        L += [f"- {x}" for x in st["nhat_ky"]]
        L += ["", f"Cau hinh giu: `{json.dumps(st['cfg'], ensure_ascii=False)}`; trong so ghep (LightGBM theo XYZ): {st.get('w')}; "
              f"thay mo hinh dang dung: **{st.get('thay')}**", "", "## Validation2", "",
              v[cot[:1] + cot[2:] + ["WMAPE_lead_time"]].round(4).to_markdown(index=False), "",
              "## Test (chi bao cao)", "", t[cot + ["WMAPE_lead_time"]].round(4).to_markdown(index=False), ""]
        open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
        print("\n".join(L))
        sys.exit()
    else:
        sys.exit("Dung: --buoc goc | A | B | F | ghep | test | bao_cao")
    luu_state(st)
    print("Trang thai:", json.dumps(st, ensure_ascii=False))
    keep_awake(False)
