"""Du bao 28 ngay TUONG LAI (chua co thuc te) bang mo hinh dang chon, dung ngay cuoi cua du lieu.
Bo mo phong: ket_hop_v4 = LightGBM (cau hinh vong 3) + Prophet additive, ghep theo nhom XYZ (cung cach nang_cap_du_bao_v4.py --buoc test).
Khoang du bao 80% / 95%: phan vi sai so tu moi dong da co thuc te truoc ngay lap (cung ham khoang_online).
Chay:
  python src/du_bao_tuong_lai.py --kiem_lai   chay lai MOC TUAN CUOI cua tap test, phai trung du bao da luu (dieu kien truoc khi tin ket qua tuong lai)
  python src/du_bao_tuong_lai.py              -> reports/du_bao/ket_hop_v4_tuong_lai.csv (nap vao CSDL voi tap 'tuong_lai'), reports/du_bao_tuong_lai.md/.json
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from danh_gia import HORIZON, PRED_DIR, du_bao_mot_moc, folds, load  # noqa: E402

V3_STATE = "reports/nang_cap_du_bao_trang_thai.json"
RA = f"{PRED_DIR}/ket_hop_v4_tuong_lai.csv"
REPORT, STATE = "reports/du_bao_tuong_lai.md", "reports/du_bao_tuong_lai.json"
COT = ["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]


def gan_cot(p, fut):
    """Them cot nhom (abc, xyz, loai nhu cau) tu khung tuong lai; y_cham de trong (chua xay ra)."""
    t = fut[["ma_sku", "abc_train", "xyz_train", "loai_nhu_cau"]].drop_duplicates("ma_sku")
    return p.merge(t, on="ma_sku", how="left").assign(y_cham=np.nan)


def chay_v4(hist, fut, o, cal, hol, workers=None):
    """Chay 2 thanh phan cua ket_hop_v4 tai moc o va ghep. Tra ve (ghep, lgb, prophet)."""
    from concurrent.futures import ProcessPoolExecutor
    import mo_hinh_prophet as P
    import nang_cap_du_bao as N
    cfg_w = json.load(open(V3_STATE, encoding="utf-8"))
    cats = {c: sorted(hist[c].dropna().unique()) for c in N.CAT}
    sk_cols = [c for c in hist.attrs["known_ahead"] if c.startswith("sk_")]
    t0 = time.time()
    l = du_bao_mot_moc(N.make_model(cfg_w["cfg"], cats, sk_cols, cal), hist, fut, o)
    print(f"  LightGBM: {time.time() - t0:.0f}s", flush=True)
    P._quiet()
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers or P.WORKERS, initializer=P._quiet) as pool:
        p = du_bao_mot_moc(P.make_model("additive", pool, hol), hist, fut, o)
    print(f"  Prophet: {time.time() - t0:.0f}s", flush=True)
    p, l = gan_cot(p, fut), gan_cot(l, fut)
    return N.blend(p, l, cfg_w["w"]), l, p


def khoang(qua_khu, moi):
    """Khoang 80/95% cho dong moi: phan vi sai so theo (nhom XYZ, tam du bao) tu moi dong qua khu da co thuc te (cung nang_cap_du_bao_v4)."""
    import nang_cap_du_bao_v4 as V
    x = pd.concat([qua_khu.assign(_moi=0), moi.assign(_moi=1)], ignore_index=True)
    x = x.rename(columns={"y_cham": "y", "du_bao": "f"}).assign(den=lambda q: q.date, tam=lambda q: V.tam(q.ngay_thu))
    o = moi.moc.iloc[0]
    x.loc[x._moi == 0, "moc"] = x.loc[x._moi == 0, "moc"].where(x.loc[x._moi == 0, "moc"] < o, o - pd.Timedelta(days=1))
    k = V.khoang_online(x[x._moi.eq(1) | (x.den <= o)], ["xyz_train", "tam"])
    k = k[k._moi == 1].rename(columns={"y": "y_cham", "f": "du_bao", "lo80": "thap_80", "hi80": "cao_80", "lo95": "thap_95", "hi95": "cao_95"})
    return k.drop(columns=["den", "tam", "_moi"])


def ghi_csdl(k, mh):
    """Thay cac dong tap 'tuong_lai' trong bang du_bao (cung dinh dang nap_database); thuc te de trong."""
    from contextlib import closing
    from csdl import ket_noi
    x = pd.DataFrame({"ma_mo_hinh": mh, "tap": "tuong_lai", "moc": pd.to_datetime(k.moc).dt.strftime("%Y-%m-%d").values,
                      "ngay": pd.to_datetime(k.date).dt.strftime("%Y-%m-%d").values, "ma_sku": k.ma_sku.values, "ngay_thu": k.ngay_thu.values,
                      "du_bao": k.du_bao.values, "thuc_te": np.nan, "thap_80": k.thap_80.values, "cao_80": k.cao_80.values,
                      "thap_95": k.thap_95.values, "cao_95": k.cao_95.values})
    with closing(ket_noi()) as con:
        con.execute("DELETE FROM du_bao WHERE tap = 'tuong_lai'")
        x.to_sql("du_bao", con, if_exists="append", index=False)
        con.commit()
        return con.execute("SELECT COUNT(*) FROM du_bao WHERE tap = 'tuong_lai'").fetchone()[0]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    import mo_hinh_prophet as P
    import nang_cap_du_bao as N
    from tuong_lai import doc_tham_chieu, khung_tuong_lai
    df = load()
    if "--kiem_lai" in sys.argv:
        o = folds("test", step=7)[-1]
        hist = df[df.date <= o]
        fut = df[(df.date > o) & (df.date <= o + pd.Timedelta(days=HORIZON))][df.attrs["known_ahead"]].copy()
        print(f"Kiem lai moc {o.date()} (moc tuan cuoi cua test)", flush=True)
        g, _, _ = chay_v4(hist, fut, o, N.lich_su_kien(df.date.unique()), P.holidays_table())
        cu = pd.read_csv(f"{PRED_DIR}/ket_hop_v4_test.csv", parse_dates=["date", "moc"])
        cu = cu[cu.moc == o]
        x = cu.merge(g, on=["date", "ma_sku"], suffixes=("_cu", "_moi"))
        lech = (x.du_bao_cu - x.du_bao_moi).abs()
        print(f"So dong: luu {len(cu)}, chay lai {len(g)}, khop {len(x)}; lech tuyet doi lon nhat {lech.max():.3e}, tong du bao {x.du_bao_cu.sum():.1f} / {x.du_bao_moi.sum():.1f}")
        print("KET LUAN:", "TRUNG" if len(x) == len(cu) == len(g) and lech.max() < 1e-6 else "KHAC")
        sys.exit()
    o = df.date.max()
    lich, nghi, shock, km = doc_tham_chieu()
    fut, ghi = khung_tuong_lai(df, o, lich, nghi, shock, km)
    from tuong_lai import mo_rong_lich
    lich_mr, _ = mo_rong_lich(lich, fut.date.max())
    cal = N.lich_su_kien(np.concatenate([df.date.unique(), fut.date.unique()]), ev=lich_mr)
    print(f"Du bao tuong lai tu {o.date()}: {fut.date.min().date()} .. {fut.date.max().date()}, {fut.ma_sku.nunique()} ma", flush=True)
    g, l, p = chay_v4(df, fut, o, cal, P.holidays_table(lich=lich_mr))
    qua_khu = pd.concat([pd.read_csv(f"{PRED_DIR}/ket_hop_v4_{t}.csv", parse_dates=["date", "moc"])[COT] for t in ("validation2", "test")], ignore_index=True)
    k = khoang(qua_khu, g[COT])
    k = k.merge(l[["date", "ma_sku", "du_bao"]].rename(columns={"du_bao": "lgb"}), on=["date", "ma_sku"]).merge(
        p[["date", "ma_sku", "du_bao"]].rename(columns={"du_bao": "prophet"}), on=["date", "ma_sku"])
    k = k.sort_values(["ma_sku", "date"])
    k[COT + ["thap_80", "cao_80", "thap_95", "cao_95"]].to_csv(RA, index=False, encoding="utf-8-sig")
    k.to_csv(RA.replace(".csv", "_thanh_phan.csv").replace(PRED_DIR, "reports"), index=False, encoding="utf-8-sig")
    tong = k.groupby("date")[["du_bao"]].sum()
    ghi.update(mo_hinh="ket_hop_v4", ngay_lap=str(o.date()), so_dong=int(len(k)), thieu_khoang=int(k.thap_80.isna().sum()),
               tong_28_ngay=float(k.du_bao.sum()))
    json.dump(ghi, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    so = lambda v: f"{v:,.0f}".replace(",", ".")
    L = ["# Dự báo 28 ngày tương lai", "", f"Ngày lập: **{o.date()}** (ngày cuối của dữ liệu). Mô hình **ket_hop_v4**. Các ngày dưới đây **chưa xảy ra**, chưa có số thật để so.", "",
         f"- Lịch biết trước mở rộng theo quy tắc của lịch hiện có (`src/tuong_lai.py`). Sự kiện không tự suy ra (không biết trước hoặc không lặp theo ngày cố định): {', '.join(ghi['su_kien_khong_tu_suy_ra']) or 'không'}.",
         f"- Khuyến mãi có lịch gửi trước trong 28 ngày: {ghi['khuyen_mai_co_lich']} dòng mã-ngày" + (" (chưa có lịch khuyến mãi: coi như không khuyến mãi)." if not ghi['khuyen_mai_co_lich'] else "."),
         f"- Ngày kho nghỉ: {', '.join(ghi['ngay_nghi']) or 'không'}.", "",
         "Khoảng 80% / 95% có cho **từng mã** (cột thap_80, cao_80...). Không cộng các khoảng của từng mã thành khoảng của tổng: tổng các khoảng rộng hơn khoảng thật của tổng.", "",
         "| Ngày | Thứ | Tổng dự báo toàn kho |", "|---|---|---:|"]
    thu = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]
    L += [f"| {d.date()} | {thu[d.weekday()]} | {so(r.du_bao)} |" for d, r in tong.iterrows()]
    L += ["", "## Kiểm tra độ hợp lý (tính tự động từ dữ liệu)", "", "| So sánh, trung bình mỗi ngày | Số bán / dự báo |", "|---|---:|"]
    for lui in (364, 728):                                  # cung ky 1 va 2 nam truoc (cung thu trong tuan)
        x = df[df.date.isin(fut.date.unique() - pd.Timedelta(days=lui))]
        if len(x):
            L.append(f"| Cùng kỳ {lui // 364} năm trước ({x.date.min().date()} … {x.date.max().date()}) | {so(x.groupby('date').y.sum().mean())} |")
            L.append(f"| Cùng kỳ {lui // 364} năm trước, bỏ dòng có khuyến mãi | {so(x[x.khuyen_mai == 0].groupby('date').y.sum().mean())} |")
    gan = df[df.date > o - pd.Timedelta(days=28)]
    L.append(f"| 28 ngày gần nhất trước ngày lập | {so(gan.groupby('date').y.sum().mean())} |")
    L.append(f"| **Dự báo 28 ngày tới** | **{so(tong.du_bao.mean())}** |")
    L += ["", "Dự báo coi như không có khuyến mãi nếu chưa có lịch gửi trước; sự kiện theo âm lịch (Tết, Trung thu) rơi vào ngày khác nhau mỗi năm nên cùng kỳ năm trước có thể có hoặc không có sự kiện."]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:8]))
    print(f"Da ghi {RA}: {len(k)} dong, thieu khoang {ghi['thieu_khoang']}")
    print(f"Da ghi CSDL: {ghi_csdl(k, 'ket_hop_v4')} dong (tap 'tuong_lai')")
