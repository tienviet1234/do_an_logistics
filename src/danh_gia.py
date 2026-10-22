"""Buoc 5 (chuan bi): khung danh gia chung cho moi mo hinh du bao.
- Chia du lieu THEO THOI GIAN, backtest cuon chieu (rolling origin), tam du bao 28 ngay.
- Chi so: MAE, RMSE, WMAPE, MASE (so voi Seasonal Naive 7 ngay tren train), Bias = mean(A - F).
- Cham diem chi tren ngay "cau tin duoc": bo ngay kho dong cua, ngay het hang, ngay don B2B dot bien.

Dung trong script mo hinh:
    from danh_gia import load, folds, backtest, score, save_results
    def my_model(hist, future):   # hist: cac dong date <= origin; future: 28 ngay toi, CHI co cot biet truoc
        return future[["date", "ma_sku"]].assign(du_bao=...)
    pred = backtest(my_model, load(), folds("test"))

Chay rieng file nay: kiem tra khung bang 2 mo hinh moc Naive va Seasonal Naive.
    python src/danh_gia.py
"""
import os
import time
import numpy as np
import pandas as pd

FEAT = "data/features/dac_trung.csv"
TRAIN_END = pd.Timestamp("2025-09-30")
DATA_END = pd.Timestamp("2026-09-30")
HORIZON = 28
STEP = 28
VAL_START = pd.Timestamp("2025-03-31")      # moc dau validation (do tham so)
PRED_DIR = "reports/du_bao"
RESULT = "reports/ket_qua_mo_hinh.csv"

# Cot duoc phep nhin thay o 28 ngay tuong lai (biet truoc tai thoi diem du bao).
# Bao lu KHONG nam trong danh sach: ngoai doi chi biet truoc 3-5 ngay.
KNOWN_AHEAD = ["date", "ma_sku", "thu", "cuoi_tuan", "ngay_trong_thang", "thang", "tuan_trong_nam", "ngay_trong_nam",
               "mua", "dau_thang", "cuoi_thang", "so_ngay_den_tet", "so_ngay_sau_tet", "trong_tuan_tet",
               "la_ngay_nghi", "ngay_sale", "cua_so_sale", "khuyen_mai",
               "nhom_hang", "loai_mua_vu", "gia_ban", "lead_time_tb", "nha_cung_cap",
               "abc_train", "xyz_train", "loai_nhu_cau"]


def load(path=FEAT):
    df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=["date"])
    known = KNOWN_AHEAD + [c for c in df.columns if c.startswith("sk_")]
    df.attrs["known_ahead"] = [c for c in known if c in df.columns]
    # cot "y_cham": nhu cau dung de cham diem (rong = khong cham)
    df["y_cham"] = df.y_cau.where(df.don_b2b == 0)
    return df


def folds(kind="test"):
    """Danh sach moc du bao (origin). Du bao cho origin+1 ... origin+HORIZON."""
    start, end = (TRAIN_END, DATA_END) if kind == "test" else (VAL_START, TRAIN_END)
    out, o = [], start
    while o + pd.Timedelta(days=HORIZON) <= end:
        out.append(o); o += pd.Timedelta(days=STEP)
    return out


def backtest(model_fn, df, origins, name="", verbose=True):
    known = df.attrs["known_ahead"]
    res = []
    t0 = time.time()
    for i, o in enumerate(origins, 1):
        hist = df[df.date <= o]
        fut = df[(df.date > o) & (df.date <= o + pd.Timedelta(days=HORIZON))][known].copy()
        p = model_fn(hist, fut)
        p = p[["date", "ma_sku", "du_bao"]].reset_index(drop=True)
        p["du_bao"] = p.du_bao.clip(lower=0)
        p["moc"] = np.full(len(p), np.datetime64(o, "ns"))  # mang (khong gan scalar: loi concat cua pandas 2.1)
        p["ngay_thu"] = (p.date - o).dt.days.values        # 1..28: du bao truoc bao nhieu ngay
        res.append(p)
        if verbose:
            print(f"  {name} moc {i}/{len(origins)} ({o.date()}) - {time.time() - t0:.0f}s", end="\r")
    if verbose:
        print()
    out = pd.concat(res, ignore_index=True)
    return out.merge(df[["date", "ma_sku", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau"]], on=["date", "ma_sku"], how="left")


def mase_scale(df):
    """MAE trong mau cua Seasonal Naive 7 ngay tren tap train, theo tung SKU (mau so cua MASE)."""
    tr = df[df.date <= TRAIN_END].sort_values(["ma_sku", "date"])
    lag7 = tr.groupby("ma_sku").y_cham.shift(7)
    err = (tr.y_cham - lag7).abs()
    return err.groupby(tr.ma_sku).mean()


def _metrics(g, scale):
    a, f = g.y_cham, g.du_bao
    e = a - f
    sku_mae = e.abs().groupby(g.ma_sku).mean()
    s = scale.reindex(sku_mae.index)
    return pd.Series({
        "so_diem": len(g),
        "MAE": e.abs().mean(),
        "RMSE": np.sqrt((e ** 2).mean()),
        "WMAPE": e.abs().sum() / a.sum(),
        "MASE": (sku_mae / s).replace([np.inf, -np.inf], np.nan).mean(),
        "Bias": e.mean(),
        "Bias_pct": e.sum() / a.sum(),                     # duong = du bao thieu (de het hang)
    })


def score(pred, df, by=None):
    """Bang chi so. by=None: toan bo; by='abc_train' / 'xyz_train' / 'loai_nhu_cau' / 'ma_sku': theo nhom."""
    scale = mase_scale(df)
    g = pred.dropna(subset=["y_cham"])
    if by is None:
        return _metrics(g, scale).to_frame().T
    return g.groupby(by).apply(lambda x: _metrics(x, scale)).reset_index()


def score_week(pred):
    """WMAPE tren tong 7 ngay (quyet dinh dat hang thuong theo tuan / theo lead time)."""
    g = pred.dropna(subset=["y_cham"]).copy()
    g["tuan"] = (g.ngay_thu - 1) // 7
    w = g.groupby(["moc", "ma_sku", "tuan"])[["y_cham", "du_bao"]].sum()
    return (w.y_cham - w.du_bao).abs().sum() / w.y_cham.sum()


def save_results(name, pred, df, kind="test", note=""):
    """Luu du bao chi tiet + them/ghi de 1 dong vao bang ket qua chung."""
    os.makedirs(PRED_DIR, exist_ok=True)
    pred.to_csv(f"{PRED_DIR}/{name}_{kind}.csv", index=False, encoding="utf-8-sig")
    row = score(pred, df).assign(WMAPE_tuan=score_week(pred))
    row.insert(0, "tap", kind); row.insert(0, "mo_hinh", name); row["ghi_chu"] = note
    for grp in ["abc_train", "xyz_train"]:
        t = score(pred, df, by=grp).set_index(grp).WMAPE
        for k, v in t.items():
            row[f"WMAPE_{k}"] = v
    old = pd.read_csv(RESULT, encoding="utf-8-sig") if os.path.exists(RESULT) else pd.DataFrame()
    if len(old):
        old = old[~((old.mo_hinh == name) & (old.tap == kind))]
    out = pd.concat([old, row], ignore_index=True)
    out.to_csv(RESULT, index=False, encoding="utf-8-sig")
    return row


# ---------------- 2 mo hinh moc de kiem tra khung ----------------
def _last_week(hist):
    """7 ngay gan nhat co cau tin duoc cua tung SKU (ngay het hang / dong cua -> lay gia tri hop le truoc do)."""
    h = hist.sort_values(["ma_sku", "date"]).copy()
    h["v"] = h.y_cau.groupby(h.ma_sku).ffill()
    return h.groupby("ma_sku").tail(7)


def naive(hist, fut):
    last = _last_week(hist).groupby("ma_sku").v.last()
    return fut.assign(du_bao=fut.ma_sku.map(last).fillna(0).values)


def seasonal_naive(hist, fut):
    lw = _last_week(hist)
    lw = lw.assign(thu=lw.date.dt.weekday)
    m = lw.set_index(["ma_sku", "thu"]).v
    key = list(zip(fut.ma_sku, fut.date.dt.weekday))
    return fut.assign(du_bao=m.reindex(key).fillna(0).values)


if __name__ == "__main__":
    df = load()
    fv, ft = folds("validation"), folds("test")
    print(f"Validation: {len(fv)} moc ({fv[0].date()} .. {fv[-1].date()}), Test: {len(ft)} moc ({ft[0].date()} .. {ft[-1].date()}), tam {HORIZON} ngay")
    for name, fn, note in [("naive", naive, "Lay ngay gan nhat"), ("seasonal_naive_7", seasonal_naive, "Lap lai tuan gan nhat")]:
        for kind, fo in [("validation", fv), ("test", ft)]:
            p = backtest(fn, df, fo, name=f"{name}/{kind}")
            r = save_results(name, p, df, kind, note)
            print(r[["mo_hinh", "tap", "so_diem", "MAE", "RMSE", "WMAPE", "WMAPE_tuan", "MASE", "Bias_pct"]].round(3).to_string(index=False))
    print(f"\nDa ghi {RESULT} va {PRED_DIR}/")
