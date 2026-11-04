"""Kiem chung quy trinh tren 1 nguon du lieu khac (docs/10 muc 9.8). Chay TRONG thu muc lam viec cua nguon, sau src/nguon/*.py va dac_trung.py:
  cd du_lieu_nguon/m5
  python ../../src/kiem_chung_nguon.py --buoc tuan --mo_hinh tb_truot|lap_tuan|prophet|lightgbm|lstm|rnn [--tap test]
  python ../../src/kiem_chung_nguon.py --buoc chon           (chi dung validation2)
  python ../../src/kiem_chung_nguon.py --buoc test           (1 lan, chi bao cao; can da chay tuan --tap test)
  python ../../src/kiem_chung_nguon.py --buoc bao_cao        -> reports/kiem_chung.md
Moi mo hinh giu nguyen cau hinh da co; moi mo hinh cap nhat moi 7 ngay, cham tren ban moi nhat moi ngay.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from danh_gia import backtest, folds, keep_awake, load, save_results, score, score_week, seasonal_naive  # noqa: E402

VAL = "validation2"
DAY_DU = "reports/du_bao/day_du"
STATE = "reports/kiem_chung_trang_thai.json"
REPORT = "reports/kiem_chung.md"
GRID_W = np.round(np.arange(0, 1.01, 0.1), 1)
THU_TU = ["tb_truot", "lap_tuan", "prophet", "lightgbm", "rnn", "lstm", "ket_hop", "ket_hop_dl"]      # don gian -> phuc tap
CHENH = 0.005
COT = ["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]


def ban_moi_nhat(p):
    return p.sort_values("ngay_thu").drop_duplicates(["date", "ma_sku"]).sort_values(["moc", "ma_sku", "date"])


def wmape(p):
    g = p.dropna(subset=["y_cham"])
    return float((g.y_cham - g.du_bao).abs().sum() / g.y_cham.sum())


def chi_so(p, df):
    q = ban_moi_nhat(p)
    r = score(q, df).iloc[0]
    n = score(q, df, by="xyz_train").set_index("xyz_train").WMAPE
    return dict(WMAPE=float(r.WMAPE), Bias=float(r.Bias_pct), tuan=float(score_week(q)), **{k: float(v) for k, v in n.items()})


def ghep(a, b, w_by):
    """w * a + (1 - w) * b, w theo nhom XYZ; hai bang phai khop tung dong."""
    x = b[COT].merge(a[["date", "ma_sku", "moc", "du_bao"]], on=["date", "ma_sku", "moc"], suffixes=("_b", "_a"), validate="1:1")
    if not len(x) == len(a) == len(b):
        raise ValueError("Hai bo du bao khong khop dong")
    w = x.xyz_train.map(w_by).astype(float)
    x["du_bao"] = w * x.du_bao_a + (1 - w) * x.du_bao_b
    return x.drop(columns=["du_bao_a", "du_bao_b"])


def do_trong_so(a, b):
    w = {}
    for g in sorted(b.xyz_train.dropna().unique()):
        aa, bb = a[a.xyz_train == g], b[b.xyz_train == g]
        w[g] = float(min(GRID_W, key=lambda v: wmape(ban_moi_nhat(ghep(aa, bb, {g: v})))))
    return w


def chon_mo_hinh(bang, chenh=CHENH, thu_tu=THU_TU):
    """Luat: WMAPE thap nhat, chenh duoi nguong thi lay phuong an don gian hon. bang: {ten: WMAPE}."""
    tot = min(bang.values())
    return next(t for t in thu_tu if t in bang and bang[t] <= tot + chenh)


def doc(ten, tap):
    return pd.read_csv(f"{DAY_DU}/{ten}_{tap}.csv", parse_dates=["date", "moc"])


def doc_state():
    return json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}


def luu_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def tao_ham(ten, df):
    if ten == "lap_tuan":
        return seasonal_naive, None
    if ten == "tb_truot":
        import mo_hinh_baseline as M
        M.ACTIVE = ["tb_truot_28"]
        return M.model_fn("tb_truot_28"), None
    if ten == "lightgbm":
        import nang_cap_du_bao as N
        cats = {c: sorted(df[c].dropna().unique()) for c in N.CAT}
        sk = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
        return N.make_model({"A": True, "B": True, "params": {}}, cats, sk, N.lich_su_kien(df.date.unique())), None
    if ten == "prophet":
        from concurrent.futures import ProcessPoolExecutor
        import mo_hinh_prophet as P
        P._quiet()
        pool = ProcessPoolExecutor(max_workers=P.WORKERS, initializer=P._quiet)
        return P.make_model("additive", pool, P.holidays_table()), pool
    if ten in ("lstm", "rnn"):
        import mo_hinh_dl as D
        return D.make_model(D.DuLieu(df), ten, "l1", ten), None
    raise SystemExit(f"Khong co mo hinh {ten}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv
    buoc = a[a.index("--buoc") + 1]
    tap = a[a.index("--tap") + 1] if "--tap" in a else VAL
    keep_awake(True)
    os.makedirs(DAY_DU, exist_ok=True)
    df = load()
    st = doc_state()
    if buoc == "tuan":
        ten = a[a.index("--mo_hinh") + 1]
        moc = folds(tap, step=7)
        if "--thu" in a:
            moc = moc[:2]
        fn, pool = tao_ham(ten, df)
        t0 = time.time()
        p = backtest(fn, df, moc, name=ten, verbose=False)
        if pool:
            pool.shutdown()
        if "--thu" in a:
            print(ten, "thu 2 moc", round(time.time() - t0), "giay", {k: round(v, 3) for k, v in chi_so(p, df).items()})
            sys.exit()
        p.to_csv(f"{DAY_DU}/{ten}_{tap}.csv", index=False, encoding="utf-8-sig")
        save_results(ten, ban_moi_nhat(p), df, tap, f"{ten}, cap nhat moi 7 ngay, kiem chung (docs/10 muc 9.8)")
        print(ten, tap, round(time.time() - t0), "giay", {k: round(v, 3) for k, v in chi_so(p, df).items()}, flush=True)
    elif buoc == "chon":
        lg, pr = doc("lightgbm", VAL), doc("prophet", VAL)
        w1 = do_trong_so(lg, pr)
        kh = ghep(lg, pr, w1)
        kh.to_csv(f"{DAY_DU}/ket_hop_{VAL}.csv", index=False, encoding="utf-8-sig")
        bang = {t: wmape(ban_moi_nhat(doc(t, VAL))) for t in ["tb_truot", "lap_tuan", "prophet", "lightgbm", "lstm", "rnn"]}
        bang["ket_hop"] = wmape(ban_moi_nhat(kh))
        hs = min(["lstm", "rnn"], key=bang.get)
        w2 = do_trong_so(doc(hs, VAL), kh)
        kd = ghep(doc(hs, VAL), kh, w2)
        kd.to_csv(f"{DAY_DU}/ket_hop_dl_{VAL}.csv", index=False, encoding="utf-8-sig")
        bang["ket_hop_dl"] = wmape(ban_moi_nhat(kd))
        for t, p in [("ket_hop", kh), ("ket_hop_dl", kd)]:
            save_results(t, ban_moi_nhat(p), df, VAL, "kiem chung (docs/10 muc 9.8)")
        st["chon"] = dict(bang=bang, w_ket_hop=w1, hoc_sau=hs, w_ket_hop_dl=w2, chon=chon_mo_hinh(bang))
        print(json.dumps(st["chon"], ensure_ascii=False, indent=1))
    elif buoc == "test":
        q = st["chon"]
        if "test" in st:
            raise SystemExit("Luat 9.8: test chi chay mot lan")
        kh = ghep(doc("lightgbm", "test"), doc("prophet", "test"), q["w_ket_hop"])
        kd = ghep(doc(q["hoc_sau"], "test"), kh, q["w_ket_hop_dl"])
        kh.to_csv(f"{DAY_DU}/ket_hop_test.csv", index=False, encoding="utf-8-sig")
        kd.to_csv(f"{DAY_DU}/ket_hop_dl_test.csv", index=False, encoding="utf-8-sig")
        for t, p in [("ket_hop", kh), ("ket_hop_dl", kd)]:
            save_results(t, ban_moi_nhat(p), df, "test", "kiem chung (docs/10 muc 9.8)")
        st["test"] = {t: chi_so(doc(t, "test"), df) for t in THU_TU}
        print(json.dumps(st["test"], ensure_ascii=False, indent=1))
    elif buoc == "bao_cao":
        cac = THU_TU
        v = {t: chi_so(doc(t, VAL), df) for t in cac}
        t_ = st["test"]
        moc_tb = t_["tb_truot"]["WMAPE"]
        fm = lambda d: "| " + " | ".join(f"{k} | {d[k]['WMAPE']:.3f} | {d[k]['tuan']:.3f} | {100 * d[k]['Bias']:+.1f}% | {d[k].get('X', float('nan')):.3f} | {d[k].get('Y', float('nan')):.3f} | {d[k].get('Z', float('nan')):.3f}" for k in sorted(d, key=lambda x: d[x]['WMAPE'])) + " |"
        dau = "| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |\n|---|---:|---:|---:|---:|---:|---:|\n"
        dong = lambda d: dau + "\n".join(f"| {k} | {d[k]['WMAPE']:.3f} | {d[k]['tuan']:.3f} | {100 * d[k]['Bias']:+.1f}% | {d[k].get('X', float('nan')):.3f} | {d[k].get('Y', float('nan')):.3f} | {d[k].get('Z', float('nan')):.3f} |" for k in sorted(d, key=lambda x: d[x]['WMAPE']))
        ch = st["chon"]["chon"]
        L = ["# Kiểm chứng trên nguồn dữ liệu khác", "", "Luật ghi trước: docs/10 mục 9.8. Mô hình chọn trên validation2, test chạy một lần.", "",
             f"Mô hình chọn: **{ch}**; trọng số LightGBM trong ket_hop {st['chon']['w_ket_hop']}; học sâu dùng để ghép: {st['chon']['hoc_sau']}, trọng số {st['chon']['w_ket_hop_dl']}.", "",
             f"Trên test, mô hình chọn giảm WMAPE {100 * (1 - t_[ch]['WMAPE'] / moc_tb):.1f}% so với trung bình trượt.", "", "## Validation2", "", dong(v), "", "## Test", "", dong(t_), ""]
        open(REPORT, "w", encoding="utf-8").write("\n".join(L))
        print("\n".join(L))
        sys.exit()
    else:
        raise SystemExit(__doc__)
    luu_state(st)
    keep_awake(False)
