"""Ket noi co so du lieu kho hang (SQLite) - dung chung cho moi buoc cua luong.
    from csdl import ket_noi, doc
    df = doc("SELECT * FROM v_xep_hang_mo_hinh")
"""
import sqlite3
from contextlib import closing

import numpy as np
import pandas as pd

DB_PATH = "data/kho_hang.db"
SCHEMA = "database/schema.sql"


def ket_noi(path=DB_PATH):
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")        # SQLite mac dinh TAT kiem tra khoa ngoai
    return con


def doc(sql, params=None, path=DB_PATH):
    with closing(ket_noi(path)) as con:
        return pd.read_sql_query(sql, con, params=params)


def ma_vi_du(path=DB_PATH):
    """Ma dung lam vi du tren bieu do / so doi chieu: ma dau tien nhom A-X (ban deu, gia tri cao), khong co thi ma dau tien."""
    d = doc("""SELECT ma_sku FROM phan_loai_sku ORDER BY (abc_train = 'A' AND xyz_train = 'X') DESC, ma_sku LIMIT 1""", path=path)
    return d.ma_sku.iloc[0]


def ngay_su_kien(ten, path=DB_PATH):
    """Cac ngay cua 1 su kien trong lich (rong neu du lieu khong co su kien do, VD Tet o du lieu nuoc ngoai)."""
    return doc("SELECT ngay FROM lich_su_kien WHERE ten_su_kien = ? ORDER BY ngay", (ten,), path=path).ngay.tolist()


def hang_dang_ve(m, lead_time_tb, gd):
    """Hang dang ve cuoi ngay (da dat, chua nhan) cho bang mo_phong_ngay cua 1 chinh sach - khong luu trong CSDL.
    Bao toan: = hang dang ve dau ky + tong da dat - tong da nhan.
    Hang dang ve dau ky = hang nhap trong L ngay dau ky theo du lieu (cung cach voi ton_kho.load_inputs), L = round(lead time TB).
    m: cot ngay, ma_sku, nhap, dat_hang, sap xep theo (ma_sku, ngay); lead_time_tb: Series theo ma_sku;
    gd: giao_dich_sach (ngay, ma_sku, qty_in) tu ngay dau ky. Hien trang khong luu lenh dat -> tra ve NaN."""
    if m.dat_hang.isna().all():
        return pd.Series(float("nan"), index=m.index)
    ngay0 = pd.Timestamp(m.ngay.min())
    L = lead_time_tb.map(lambda x: max(1, int(round(x))))
    gd = gd[(pd.to_datetime(gd.ngay) - ngay0).dt.days < gd.ma_sku.map(L)]
    by = m.groupby("ma_sku")
    return m.ma_sku.map(gd.groupby("ma_sku").qty_in.sum()).fillna(0) + by.dat_hang.cumsum().fillna(0) - by.nhap.cumsum()


def quy_tac_cua_ma(quy_tac_chinh_sach, xyz):
    """Quy tac luong dat ap cho 1 ma (nhu ton_kho.run): 'lai' = dat_den_muc cho nhom Z, eoq cho X / Y."""
    if quy_tac_chinh_sach == "lai":
        return "dat_den_muc" if xyz == "Z" else "eoq"
    return quy_tac_chinh_sach


def de_xuat_ngay(f, st, L, sigma, z, lt_std, S, H, moq, ip, quy_tac="eoq", r_cover=7):
    """SS, ROP, EOQ va luong dat cua 1 SKU tai 1 ngay, CUNG cong thuc ton_kho.simulate - dung cho "Thu neu..." o dashboard
    (doi muc phuc vu z, lead time L). Kiem tra tai lap: so voi mo_phong_ngay (rop, dat_hang).
    f: du bao 28 ngay cua dot dang dung (da nhan he so hieu chinh); st: vi tri ngay mai trong dot;
    sigma: do lech chuan sai so du bao trong L ngay; ip: trong kho + dang ve, chua tinh don hom nay;
    quy_tac: 'eoq' (boi so cua max(EOQ, MOQ)) hoac 'dat_den_muc' (dat du L + r_cover ngay + SS, toi thieu MOQ;
    r_cover = ton_kho.R_COVER)."""
    fw = lambda m: (f[st:st + m] if st < len(f) else f[-1:]).mean() * m
    ltd = fw(L)
    ss = z * np.sqrt(sigma ** 2 + (ltd / L) ** 2 * lt_std ** 2)
    rop = ltd + ss
    dbar = f.mean()
    eoq = np.sqrt(2 * dbar * 365 * S / H) if dbar > 0 else 0.0
    dat = 0.0
    if ip <= rop:
        if quy_tac == "eoq":
            q = max(eoq, moq)
            dat = float(np.ceil((np.floor((rop - ip) / q) + 1) * q))
        else:                                                # dat_den_muc
            dat = float(np.ceil(max(moq, fw(L + r_cover) + ss - ip)))
    return dict(ss=ss, rop=rop, eoq=eoq, dat=dat, ltd=ltd)


def chia_lop_mau(so_dem):
    """Chia cac so dem > 0 thanh toi da 4 lop mau theo phan vi (moi lop deu co ngay, ke ca khi loc con it ma).
    Tra ve [(tu, den), ...] lien tiep, phu tu 1 den gia tri lon nhat; khong co so nao > 0 -> []."""
    v = np.asarray(so_dem, dtype=float)
    v = v[v > 0]
    if not len(v):
        return []
    moc = sorted({int(np.ceil(np.quantile(v, q))) for q in (0.4, 0.75, 0.95)} | {int(v.max())})
    lop, tu = [], 1
    for den in moc:
        lop.append((tu, den))
        tu = den + 1
    return lop


TRANG_THAI = ["Hết hàng", "Đặt hàng hôm nay", "Dưới ROP, hàng đang về", "Đủ hàng"]   # thu tu uu tien


def trang_thai_ton_kho(m):
    """Canh bao cuoi ngay cho tung dong mo_phong_ngay (cot ton_cuoi, rop, dat_hang, nhu_cau, xuat), lay muc uu tien cao nhat:
    het hang va mat ban > cham ROP, dat hang hom nay > ton thuc duoi ROP (khong dat vi hang dang ve du bu) > du hang."""
    het = (m.ton_cuoi < 0.5) & (m.nhu_cau > m.xuat + 0.5)
    return pd.Series(np.select([het, m.dat_hang > 0, m.ton_cuoi < m.rop], TRANG_THAI[:3], TRANG_THAI[3]), index=m.index)
