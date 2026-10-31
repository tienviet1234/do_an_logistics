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


def de_xuat_ngay(f, st, L, sigma, z, lt_std, S, H, moq, ip):
    """SS, ROP, EOQ va luong dat cua 1 SKU tai 1 ngay, CUNG cong thuc ton_kho.simulate (quy tac eoq) - dung cho "Thu neu..."
    o dashboard (doi muc phuc vu z, lead time L). Kiem tra tai lap: so voi mo_phong_ngay (rop, dat_hang).
    f: du bao 28 ngay cua dot dang dung (da nhan he so hieu chinh); st: vi tri ngay mai trong dot (1..28);
    sigma: do lech chuan sai so du bao trong L ngay; ip: trong kho + dang ve, chua tinh don hom nay."""
    fw = lambda m: (f[st:st + m] if st < len(f) else f[-1:]).mean() * m
    ltd = fw(L)
    ss = z * np.sqrt(sigma ** 2 + (ltd / L) ** 2 * lt_std ** 2)
    rop = ltd + ss
    dbar = f.mean()
    eoq = np.sqrt(2 * dbar * 365 * S / H) if dbar > 0 else 0.0
    dat = 0.0
    if ip <= rop:
        q = max(eoq, moq)
        dat = float(np.ceil((np.floor((rop - ip) / q) + 1) * q))
    return dict(ss=ss, rop=rop, eoq=eoq, dat=dat, ltd=ltd)


TRANG_THAI = ["Hết hàng", "Đặt hàng hôm nay", "Dưới ROP, hàng đang về", "Đủ hàng"]   # thu tu uu tien


def trang_thai_ton_kho(m):
    """Canh bao cuoi ngay cho tung dong mo_phong_ngay (cot ton_cuoi, rop, dat_hang, nhu_cau, xuat), lay muc uu tien cao nhat:
    het hang va mat ban > cham ROP, dat hang hom nay > ton thuc duoi ROP (khong dat vi hang dang ve du bu) > du hang."""
    het = (m.ton_cuoi < 0.5) & (m.nhu_cau > m.xuat + 0.5)
    return pd.Series(np.select([het, m.dat_hang > 0, m.ton_cuoi < m.rop], TRANG_THAI[:3], TRANG_THAI[3]), index=m.index)
