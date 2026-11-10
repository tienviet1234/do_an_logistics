"""Du bao 28 ngay TUONG LAI cho nguon du lieu kiem chung (VD M5), mo hinh ket_hop_dl = RNN ghep voi (LightGBM + Prophet), docs/10 muc 9.8.
Chay TRONG thu muc nguon (VD du_lieu_nguon/m5). Lich biet truoc cua 28 ngay toi lay tu lich goc cua nguon (M5: calendar.csv qua src/nguon/m5.py).
  python ../../src/du_bao_tuong_lai_kc.py --kiem_lai ../../data/m5   LightGBM, Prophet tai moc tuan cuoi cua test: phai trung du bao da luu
  python ../../src/du_bao_tuong_lai_kc.py --rnn ../../data/m5        RNN: chay lai chuoi moc test (kiem moc cuoi), hoc tiep den ngay cuoi, du bao 28 ngay
  python ../../src/du_bao_tuong_lai_kc.py ../../data/m5              LightGBM + Prophet tuong lai, ghep voi RNN -> reports/du_bao/day_du/ket_hop_dl_tuong_lai.csv
RNN hoc tiep qua tung moc (30 luot o moc dau, 4 luot o moi moc sau) nen khong chay 1 moc rieng duoc: phai di lai ca chuoi nhu khi dung that.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "nguon"))
from danh_gia import HORIZON, du_bao_mot_moc, folds, load  # noqa: E402

DAY_DU = "reports/du_bao/day_du"
STATE_KC = "reports/kiem_chung_trang_thai.json"
REPORT, STATE = "reports/du_bao_tuong_lai.md", "reports/du_bao_tuong_lai.json"
COT = ["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]


def lich_day_du(goc, den):
    """Lich su kien cua nguon den ngay `den` (gom 28 ngay tuong lai), cung ham dung tep tham chieu."""
    import m5
    cal = pd.read_csv(f"{goc}/calendar.csv", parse_dates=["date"])
    if cal.date.max() < den:
        raise ValueError(f"Lich goc chi den {cal.date.max().date()}, can den {pd.Timestamp(den).date()}")
    return m5.lich_su_kien(cal[cal.date <= den])


def khung(df, goc):
    from tuong_lai import doc_tham_chieu, khung_tuong_lai
    o = df.date.max()
    lich = lich_day_du(goc, o + pd.Timedelta(days=HORIZON))
    _, nghi, shock, km = doc_tham_chieu()
    fut, ghi = khung_tuong_lai(df, o, lich, nghi, shock, km, mo_rong=False)
    ghi["su_kien_tuong_lai"] = lich[lich.ds > o].holiday.value_counts().to_dict()
    return o, lich, fut, ghi


def lgb_prophet(hist, fut, o, cal, hol):
    from concurrent.futures import ProcessPoolExecutor
    import mo_hinh_prophet as P
    import nang_cap_du_bao as N
    cats = {c: sorted(hist[c].dropna().unique()) for c in N.CAT}
    sk = [c for c in hist.attrs["known_ahead"] if c.startswith("sk_")]
    t0 = time.time()
    l = du_bao_mot_moc(N.make_model({"A": True, "B": True, "params": {}}, cats, sk, cal), hist, fut, o)       # cung cau hinh kiem_chung_nguon
    print(f"  LightGBM: {time.time() - t0:.0f}s", flush=True)
    P._quiet()
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=P.WORKERS, initializer=P._quiet) as pool:
        p = du_bao_mot_moc(P.make_model("additive", pool, hol), hist, fut, o)
    print(f"  Prophet: {time.time() - t0:.0f}s", flush=True)
    t = fut[["ma_sku", "abc_train", "xyz_train", "loai_nhu_cau"]].drop_duplicates("ma_sku")
    return [x.merge(t, on="ma_sku", how="left").assign(y_cham=np.nan) for x in (l, p)]


def rnn_chuoi(d, mocs, cap, da_hoc, ham="l1"):
    """Hoc tiep RNN qua cac moc (dung cach mo_hinh_dl.make_model). Tra ve du bao (S, 28) cua moc cuoi."""
    import torch
    import mo_hinh_dl as D
    f = None
    for moc in mocs:
        m = d.theo_moc(moc)
        t0 = time.time()
        for k, (mh, opt) in enumerate(cap):
            torch.manual_seed(D.HAT_GIONG[k] + m["o"])
            D.hoc(mh, opt, d, m, ham, *((D.LUOT_TIEP, D.LR_TIEP) if da_hoc[0] else (D.LUOT_DAU, D.LR_DAU)))
        da_hoc[0] = True
        f = np.mean([D.du_doan(mh, d, m) for mh, _ in cap], axis=0)
        print(f"  rnn moc {moc.date()}: {time.time() - t0:.0f}s", flush=True)
    return f, m


def ra_bang(f, d, moc, fut):
    ra = fut[["date", "ma_sku", "la_ngay_nghi"]].copy()
    i, j = ra.ma_sku.map(d.i_sku).values, (ra.date - moc).dt.days.values - 1
    ra["du_bao"] = np.clip(np.where(ra.la_ngay_nghi == 1, 0, f[i, j]), 0, None)        # chan duoi 0 nhu backtest (du_bao_mot_moc)
    return ra[["date", "ma_sku", "du_bao"]]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv
    goc = a[-1]
    df = load()
    known = df.attrs["known_ahead"]
    if "--kiem_lai" in a:
        import mo_hinh_prophet as P
        import nang_cap_du_bao as N
        o = folds("test", step=7)[-1]
        hist, fut = df[df.date <= o], df[(df.date > o) & (df.date <= o + pd.Timedelta(days=HORIZON))][known].copy()
        print(f"Kiem lai LightGBM, Prophet tai moc {o.date()}", flush=True)
        l, p = lgb_prophet(hist, fut, o, N.lich_su_kien(df.date.unique()), P.holidays_table())
        for ten, x in [("lightgbm", l), ("prophet", p)]:
            cu = pd.read_csv(f"{DAY_DU}/{ten}_test.csv", parse_dates=["date", "moc"])
            cu = cu[cu.moc == o].merge(x, on=["date", "ma_sku"], suffixes=("_cu", "_moi"))
            print(f"  {ten}: khop {len(cu)} dong, lech lon nhat {(cu.du_bao_cu - cu.du_bao_moi).abs().max():.3e}")
        sys.exit()
    o, lich, fut, ghi = khung(df, goc)
    if "--rnn" in a:
        import torch
        import mo_hinh_dl as D
        d0 = D.DuLieu(df)
        so_dt = d0.co_dinh.shape[2] + 6
        cap = []
        for hg in D.HAT_GIONG:
            torch.manual_seed(hg)
            mh = D.MaHoaGiaiMa("rnn", so_dt, d0.so_nhom).to(D.TB)
            cap.append((mh, torch.optim.Adam(mh.parameters(), lr=D.LR_DAU)))
        da_hoc = [False]
        mocs = folds("test", step=7)
        f, m = rnn_chuoi(d0, mocs, cap, da_hoc)
        cu = pd.read_csv(f"{DAY_DU}/rnn_test.csv", parse_dates=["date", "moc"])
        cu = cu[cu.moc == mocs[-1]]
        x = cu.merge(ra_bang(f, d0, mocs[-1], df[(df.date > mocs[-1]) & (df.date <= mocs[-1] + pd.Timedelta(days=HORIZON))]), on=["date", "ma_sku"], suffixes=("_cu", "_moi"))
        lech = (x.du_bao_cu - x.du_bao_moi).abs()
        kiem = dict(moc=str(mocs[-1].date()), dong=int(len(x)), lech_lon_nhat=float(lech.max()), lech_tuong_doi_tong=float(lech.sum() / x.du_bao_cu.sum()),
                    tong_cu=float(x.du_bao_cu.sum()), tong_moi=float(x.du_bao_moi.sum()))
        print("Kiem lai RNN moc cuoi test:", kiem, flush=True)
        df_ext = pd.concat([df, fut.assign(y_cham=np.nan)], ignore_index=True)
        df_ext.attrs = df.attrs
        d1 = D.DuLieu(df_ext, ev=lich)
        them = list(pd.date_range(mocs[-1] + pd.Timedelta(days=7), o, freq="7D"))
        them = [x for x in them if x < o] + [o]
        f, m = rnn_chuoi(d1, them, cap, da_hoc)
        r = ra_bang(f, d1, o, fut)
        r.assign(moc=o, ngay_thu=(r.date - o).dt.days).to_csv(f"{DAY_DU}/rnn_tuong_lai.csv", index=False, encoding="utf-8-sig")
        json.dump(dict(kiem_lai=kiem, hoc_tiep=[str(x.date()) for x in them]), open("reports/rnn_tuong_lai.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Da ghi {DAY_DU}/rnn_tuong_lai.csv: {len(r)} dong", flush=True)
        sys.exit()
    # LightGBM + Prophet tuong lai, ghep voi RNN theo trong so da chon
    import mo_hinh_prophet as P
    import nang_cap_du_bao as N
    from du_bao_tuong_lai import ghi_csdl, khoang
    from kiem_chung_nguon import ghep
    chon = json.load(open(STATE_KC, encoding="utf-8"))["chon"]
    assert chon["chon"] == "ket_hop_dl" and chon["hoc_sau"] == "rnn", "script nay danh cho mo hinh ket_hop_dl (RNN)"
    cal = N.lich_su_kien(np.concatenate([df.date.unique(), fut.date.unique()]), ev=lich)
    print(f"Du bao tuong lai tu {o.date()}: {fut.date.min().date()} .. {fut.date.max().date()}", flush=True)
    l, p = lgb_prophet(df, fut, o, cal, P.holidays_table(lich=lich))
    rnn = pd.read_csv(f"{DAY_DU}/rnn_tuong_lai.csv", parse_dates=["date", "moc"])
    rnn = rnn.assign(du_bao=rnn.du_bao.clip(lower=0))                                         # chan duoi 0 nhu backtest (du_bao_mot_moc)
    rnn = rnn.merge(l[["date", "ma_sku", "abc_train", "xyz_train", "loai_nhu_cau"]], on=["date", "ma_sku"]).assign(y_cham=np.nan)
    kh = ghep(l, p, chon["w_ket_hop"])
    kd = ghep(rnn, kh, chon["w_ket_hop_dl"])
    qua_khu = pd.concat([pd.read_csv(f"{DAY_DU}/ket_hop_dl_{t}.csv", parse_dates=["date", "moc"])[COT] for t in ("validation2", "test")], ignore_index=True)
    k = khoang(qua_khu, kd[COT]).sort_values(["ma_sku", "date"])
    k[COT + ["thap_80", "cao_80", "thap_95", "cao_95"]].to_csv(f"{DAY_DU}/ket_hop_dl_tuong_lai.csv", index=False, encoding="utf-8-sig")
    tp = k.merge(l[["date", "ma_sku", "du_bao"]].rename(columns={"du_bao": "lgb"}), on=["date", "ma_sku"]).merge(
        p[["date", "ma_sku", "du_bao"]].rename(columns={"du_bao": "prophet"}), on=["date", "ma_sku"]).merge(
        rnn[["date", "ma_sku", "du_bao"]].rename(columns={"du_bao": "rnn"}), on=["date", "ma_sku"])
    tp.to_csv("reports/ket_hop_dl_tuong_lai_thanh_phan.csv", index=False, encoding="utf-8-sig")
    tong = k.groupby("date").du_bao.sum()
    ghi.update(mo_hinh="ket_hop_dl", ngay_lap=str(o.date()), so_dong=int(len(k)), thieu_khoang=int(k.thap_80.isna().sum()), tong_28_ngay=float(tong.sum()))
    json.dump(ghi, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    so = lambda v: f"{v:,.0f}".replace(",", ".")
    thu = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]
    L = ["# Dự báo 28 ngày tương lai", "", f"Ngày lập: **{o.date()}** (ngày cuối của dữ liệu). Mô hình **ket_hop_dl** (RNN ghép với LightGBM + Prophet). Các ngày dưới đây **chưa xảy ra**.", "",
         f"- Lịch biết trước lấy từ lịch gốc của nguồn: {', '.join(f'{k} {v}' for k, v in ghi['su_kien_tuong_lai'].items())}.",
         "- Nguồn không có lịch khuyến mãi gửi trước: coi như không khuyến mãi.", "",
         "Khoảng 80% / 95% có cho **từng mã**; không cộng thành khoảng của tổng.", "", "| Ngày | Thứ | Tổng dự báo toàn kho |", "|---|---|---:|"]
    L += [f"| {dd.date()} | {thu[dd.weekday()]} | {so(v)} |" for dd, v in tong.items()]
    L += ["", "## Kiểm tra độ hợp lý (tính tự động từ dữ liệu)", "", "| So sánh, trung bình mỗi ngày | Số bán / dự báo |", "|---|---:|"]
    for lui in (364, 728):
        x = df[df.date.isin(fut.date.unique() - pd.Timedelta(days=lui))]
        if len(x):
            L.append(f"| Cùng kỳ {lui // 364} năm trước ({x.date.min().date()} … {x.date.max().date()}) | {so(x.groupby('date').y.sum().mean())} |")
    L += [f"| 28 ngày gần nhất trước ngày lập | {so(df[df.date > o - pd.Timedelta(days=28)].groupby('date').y.sum().mean())} |", f"| **Dự báo 28 ngày tới** | **{so(tong.mean())}** |"]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[-6:]))
    print(f"Da ghi {DAY_DU}/ket_hop_dl_tuong_lai.csv: {len(k)} dong, thieu khoang {ghi['thieu_khoang']}")
