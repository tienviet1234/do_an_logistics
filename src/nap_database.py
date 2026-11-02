"""Nap toan bo du lieu vao co so du lieu kho hang (SQLite: data/kho_hang.db).
Xoa va tao lai tu database/schema.sql moi lan chay (chay lai bao nhieu lan cung ra cung ket qua).
Thu tu nap theo khoa ngoai: danh muc -> lich -> giao dich -> mo hinh / du bao.
Moi bang ghi 1 dong vao nhat_ky_chay; cuoi cung tu kiem tra toan ven du lieu.
Chay: python src/nap_database.py            (can chay truoc: lam_sach, dac_trung, cac mo hinh)
      python src/nap_database.py --bo-du-bao (bo qua bang du_bao cho nhanh)
"""
import glob
import os
import sys
from contextlib import closing
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from csdl import DB_PATH, SCHEMA, ket_noi  # noqa: E402
from danh_gia import UNFORESEEABLE, PRED_DIR, RESULT  # noqa: E402

REF = "data/reference"
MO_HINH_DUOC_CHON = "ket_hop_v4"                 # GD E vong 4: cap nhat moi tuan (docs/10 muc 9.6); truoc do: ket_hop_v3
TAPS = ("validation2", "validation", "test")     # thu tu quan trong: "validation2" truoc "validation"


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def csv(path):
    return pd.read_csv(path, encoding="utf-8-sig")


def ngay(s):
    return pd.to_datetime(s).dt.strftime("%Y-%m-%d")


def nap(con, bang, frame, buoc):
    """Ghi 1 bang (them vao bang da tao theo schema) + ghi nhat ky; loi thi ghi 'loi' roi dung."""
    cur = con.execute("INSERT INTO nhat_ky_chay (buoc, bang, bat_dau, trang_thai) VALUES (?,?,?,'dang_chay')",
                      (buoc, bang, now()))
    log_id = cur.lastrowid
    try:
        frame.to_sql(bang, con, if_exists="append", index=False, chunksize=20000)
        con.execute("UPDATE nhat_ky_chay SET ket_thuc=?, so_dong=?, trang_thai='thanh_cong' WHERE id=?",
                    (now(), len(frame), log_id))
        con.commit()
        print(f"  {bang:<20} {len(frame):>9,} dong")
    except Exception as e:
        con.rollback()
        con.execute("UPDATE nhat_ky_chay SET ket_thuc=?, trang_thai='loi', ghi_chu=? WHERE id=?",
                    (now(), str(e)[:500], log_id))
        con.commit()
        raise


def danh_muc():
    sku = csv(f"{REF}/sku_master.csv")
    ncc = pd.DataFrame({"ma_ncc": sorted(sku.nha_cung_cap.unique())})
    dm = sku.rename(columns={"nha_cung_cap": "ma_ncc", "phan_loai_ABC": "phan_loai_abc", "phan_loai_XYZ": "phan_loai_xyz",
                             "nhu_cau_tb_ngay": "nhu_cau_tb_ngay_mp", "xu_huong_nam": "xu_huong_nam_mp",
                             "cv_nhu_cau": "cv_nhu_cau_mp"})
    pl_path = "data/features/phan_loai_sku.csv"
    if not os.path.exists(pl_path):
        sys.exit("Thieu data/features/phan_loai_sku.csv -> chay truoc: python src/dac_trung.py")
    pl = csv(pl_path)[["ma_sku", "abc_train", "xyz_train", "cv_thang_train", "adi", "cv2", "loai_nhu_cau"]]
    return ncc, dm, pl


def lich():
    ev = csv(f"{REF}/lich_su_kien_prophet.csv")
    khong_biet = {c.replace("sk_", "") for c in UNFORESEEABLE}
    ev = pd.DataFrame({"ten_su_kien": ev.holiday, "ngay": ngay(ev.ds), "cua_so_truoc": ev.lower_window,
                       "cua_so_sau": ev.upper_window,
                       "biet_truoc_28_ngay": (~(ev.holiday.str.startswith("bao_") | ev.holiday.isin(khong_biet))).astype(int),
                       "ghi_chu": ev.ghi_chu})
    nghi = csv(f"{REF}/lich_ngay_nghi_kho.csv")
    nghi = pd.DataFrame({"ngay": ngay(nghi.date), "ly_do": nghi.ten_ngay_nghi})
    km = csv(f"{REF}/lich_khuyen_mai.csv")
    sk = csv(f"{REF}/su_kien_dot_bien.csv").rename(columns={"muc_do_0_1": "muc_do"})
    return ev, nghi, km, sk


def giao_dich():
    raw_path = "data/raw/giao_dich_nhap_xuat_ton_THO.csv"
    tho = csv(raw_path).rename(columns={"date": "ngay"}).assign(nguon_file=os.path.basename(raw_path))
    sach = csv("data/clean/giao_dich_sach.csv").rename(columns={"date": "ngay"})
    sua = csv("reports/dong_da_sua.csv").rename(columns={"date": "ngay"})
    nct = csv("data/answer_key/nhu_cau_that.csv")          # dap an: chi de cham chinh sach ton kho (GD F)
    nct = pd.DataFrame({"ngay": nct.date, "ma_sku": nct.ma_sku, "nhu_cau": nct.nhu_cau_that})
    return tho, sach, sua, nct


def mo_hinh_va_du_bao(bo_du_bao=False):
    kq = csv(RESULT)
    files = sorted(glob.glob(f"{PRED_DIR}/*.csv"))
    parsed = []
    for f in files:
        base = os.path.basename(f)[:-4]
        tap = next(t for t in TAPS if base.endswith("_" + t))
        parsed.append((base[: -len(tap) - 1], tap, f))
    ten = sorted(set(kq.mo_hinh) | {m for m, _, _ in parsed})
    mo_ta = kq.groupby("mo_hinh").ghi_chu.last()
    so_a = int((csv("data/features/phan_loai_sku.csv").abc_train == "A").sum())     # ARIMA chi chay nhom A (doi khi gia doi)
    mh = pd.DataFrame({"ma_mo_hinh": ten, "mo_ta": [mo_ta.get(t) for t in ten],
                       "pham_vi": [f"Chi {so_a} SKU nhom A" if t == "arima" else "Toan bo 121 SKU" for t in ten],
                       "duoc_chon": [int(t == MO_HINH_DUOC_CHON) for t in ten]})
    kq = kq.rename(columns={"mo_hinh": "ma_mo_hinh"}).rename(columns=str.lower)
    kq = kq[[c for c in ["ma_mo_hinh", "tap", "so_diem", "mae", "rmse", "wmape", "wmape_tuan", "mase", "bias", "bias_pct",
                         "wmape_a", "wmape_b", "wmape_c", "wmape_x", "wmape_y", "wmape_z"] if c in kq.columns]]
    du_bao = []
    if not bo_du_bao:
        for m, tap, f in parsed:
            d = csv(f)
            x = pd.DataFrame({"ma_mo_hinh": m, "tap": tap, "moc": ngay(d.moc), "ngay": ngay(d.date),
                              "ma_sku": d.ma_sku, "ngay_thu": d.ngay_thu, "du_bao": d.du_bao, "thuc_te": d.y_cham})
            for c in ["thap_80", "cao_80", "thap_95", "cao_95"]:                  # khoang du bao (neu mo hinh co)
                x[c] = d[c] if c in d else np.nan
            du_bao.append(x)
    return mh, kq, (pd.concat(du_bao, ignore_index=True) if du_bao else None)


def kiem_tra(con):
    """Kiem tra toan ven sau khi nap. Tra ve danh sach (ten kiem tra, ket qua, dat?)."""
    q = lambda sql: con.execute(sql).fetchone()[0]
    sach = csv("data/clean/giao_dich_sach.csv")
    out = [
        ("Khoa ngoai bi vi pham (PRAGMA foreign_key_check)", len(con.execute("PRAGMA foreign_key_check").fetchall()), None),
        ("Toan ven file (PRAGMA integrity_check)", q("PRAGMA integrity_check"), "ok"),
        ("So dong giao_dich_sach = file CSV", q("SELECT COUNT(*) FROM giao_dich_sach"), len(sach)),
        ("Tong qty_out trong DB = file CSV", round(q("SELECT SUM(qty_out) FROM giao_dich_sach")), round(sach.qty_out.sum())),
        ("SKU trong giao dich khong co trong danh muc",
         q("SELECT COUNT(DISTINCT ma_sku) FROM giao_dich_tho WHERE ma_sku NOT IN (SELECT ma_sku FROM dm_sku)"), 0),
        ("Dong vi pham dang thuc kho (ton cuoi = ton dau + nhap - xuat)", q("""
            SELECT COUNT(*) FROM (
              SELECT ton_cuoi_ngay - (LAG(ton_cuoi_ngay) OVER (PARTITION BY ma_sku ORDER BY ngay) + qty_in - qty_out) AS lech
              FROM giao_dich_sach) WHERE ABS(lech) > 0.5"""), 0),
        ("Mo hinh duoc chon", q("SELECT GROUP_CONCAT(ma_mo_hinh) FROM mo_hinh WHERE duoc_chon = 1"), MO_HINH_DUOC_CHON),
    ]
    return [(t, v, (v == 0) if e is None else (v == e)) for t, v, e in out]


if __name__ == "__main__":
    bo_du_bao = "--bo-du-bao" in sys.argv
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    with closing(ket_noi()) as con:
        with open(SCHEMA, encoding="utf-8") as f:
            con.executescript(f.read())
        con.execute("PRAGMA foreign_keys = ON")
        print(f"Tao moi {DB_PATH} tu {SCHEMA}")
        ncc, dm, pl = danh_muc()
        print("1. Danh muc"); nap(con, "dm_nha_cung_cap", ncc, "1_danh_muc"); nap(con, "dm_sku", dm, "1_danh_muc")
        nap(con, "phan_loai_sku", pl, "1_danh_muc")
        ev, nghi, km, sk = lich()
        print("2. Lich va su kien"); nap(con, "lich_su_kien", ev, "2_lich"); nap(con, "lich_ngay_nghi", nghi, "2_lich")
        nap(con, "lich_khuyen_mai", km, "2_lich"); nap(con, "su_kien_dot_bien", sk, "2_lich")
        tho, sach, sua, nct = giao_dich()
        print("3. Giao dich"); nap(con, "giao_dich_tho", tho, "3_giao_dich"); nap(con, "giao_dich_sach", sach, "3_giao_dich")
        nap(con, "nhat_ky_sua_loi", sua, "3_giao_dich"); nap(con, "nhu_cau_that", nct, "3_giao_dich")
        mh, kq, db = mo_hinh_va_du_bao(bo_du_bao)
        print("4. Mo hinh va du bao"); nap(con, "mo_hinh", mh, "4_mo_hinh"); nap(con, "ket_qua_mo_hinh", kq, "4_mo_hinh")
        if db is not None:
            nap(con, "du_bao", db, "4_mo_hinh")
        print("\nKiem tra toan ven:")
        ok_all = True
        for ten, v, ok in kiem_tra(con):
            ok_all &= bool(ok)
            print(f"  [{'DAT' if ok else 'LOI'}] {ten}: {v}")
        con.execute("VACUUM")
    print(f"\n{'Hoan tat' if ok_all else 'CO LOI'} - {DB_PATH}: {os.path.getsize(DB_PATH) / 1e6:.0f} MB")
    sys.exit(0 if ok_all else 1)
