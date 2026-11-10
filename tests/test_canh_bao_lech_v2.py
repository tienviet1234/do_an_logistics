"""Test canh bao du bao lech vong 2 (khong can CSDL)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from canh_bao_lech_v2 import (cap_su_kien, danh_gia_dot_bien, doc_dap_an, he_so_cua_ma, khong_su_kien, lech_ke_tiep_ban,  # noqa: E402
                              moc_phat_hien, sai_so_ban, tin_hieu_tuan)


def chuoi(ma="A", tu="2026-01-01", so_ngay=120, f=10.0, y=10.0):
    ngay = pd.date_range(tu, periods=so_ngay)
    d = pd.DataFrame({"ma_sku": ma, "ngay": ngay, "ngay_thu": 1, "du_bao": f})
    ban = pd.DataFrame({"ma_sku": ma, "ngay": ngay, "qty_out": [y(x) if callable(y) else y for x in ngay], "la_ngay_nghi": 0})
    return d, ban


def test_sai_so_ban_bo_ngay_nghi_va_lay_ban_moi_nhat():
    d = pd.DataFrame({"ma_sku": ["A", "A", "A"], "ngay": ["2026-01-10", "2026-01-10", "2026-01-11"], "ngay_thu": [9, 2, 3], "du_bao": [5.0, 8.0, 1.0]})
    ban = pd.DataFrame({"ma_sku": ["A", "A"], "ngay": ["2026-01-10", "2026-01-11"], "qty_out": [10.0, 4.0], "la_ngay_nghi": [0, 1]})
    e = sai_so_ban(d, ban)
    assert len(e) == 1 and e.e.iloc[0] == pytest.approx(2.0)


def test_tin_hieu_tuan_tinh_tay():
    # 13 tuan: 9 tuan dau sai so tuan +7 / -7 xen ke, 4 tuan cuoi moi ngay +1 -> tong 4 tuan = 28, MAD = 7 -> TS = 4
    goc = pd.Timestamp("2026-04-01")
    ngay = pd.date_range(goc - pd.Timedelta(days=90), goc)
    def y(x):
        j = (goc - x).days // 7
        return 11.0 if j < 4 else (11.0 if j % 2 == 0 else 9.0)
    d, ban = chuoi(tu=ngay[0], so_ngay=len(ngay), y=y)
    t = tin_hieu_tuan(sai_so_ban(d, ban), goc)
    assert t.rsfe.iloc[0] == pytest.approx(28.0) and t.mad.iloc[0] == pytest.approx(7.0) and t.ts.iloc[0] == pytest.approx(4.0)


def test_khong_nhin_truoc_va_thieu_tuan():
    goc = pd.Timestamp("2026-04-01")
    d, ban = chuoi(tu="2026-01-01", so_ngay=200, y=lambda x: (10.0 + (1 if x.day % 2 else -1)) if x <= goc else 999.0)
    a = tin_hieu_tuan(sai_so_ban(d, ban), goc)
    assert abs(a.rsfe.iloc[0]) < 20                                   # so ban sau ngay lap phieu khong vao tin hieu
    d2, ban2 = chuoi(tu="2026-03-20", so_ngay=13, y=12.0)
    assert np.isnan(tin_hieu_tuan(sai_so_ban(d2, ban2), "2026-04-01").ts.iloc[0])   # chi 2 tuan du lieu


def test_lech_ke_tiep_ban():
    d = pd.DataFrame({"ma_sku": ["A", "A"], "ngay": ["2026-01-02", "2026-01-03"], "du_bao": [10.0, 10.0]})
    ban = pd.DataFrame({"ma_sku": ["A", "A"], "ngay": ["2026-01-02", "2026-01-03"], "qty_out": [15.0, 99.0], "la_ngay_nghi": [0, 1]})
    assert lech_ke_tiep_ban(d, ban)["A"] == pytest.approx(0.5)


def test_doc_dap_an_khong_chay_trinh_sinh():
    dot, aff = doc_dap_an()
    assert dot and all(len(x) == 3 for x in dot) and "dich_cum" in aff and "nang_nong" in aff


def test_he_so_va_cap_su_kien():
    assert he_so_cua_ma("Khẩu trang y tế", {"Khẩu trang": 2.0, "y tế": 0.3}) == 0.3       # tu khoa sau ghi de, nhu trinh sinh
    ten = {"A": "Khẩu trang", "B": "Dầu gió", "C": "Bút bi"}
    cap, ngan = cap_su_kien(ten, [("dich_cum", "2026-01-01", "2026-01-20"), ("dich_cum", "2026-02-01", "2026-02-03")],
                            {"dich_cum": {"Khẩu trang": 2.0, "Dầu gió": 0.3}})
    assert [c[0] for c in cap] == ["A"] and ngan == 1


def test_moc_phat_hien_va_khong_su_kien():
    moc = list(pd.date_range("2026-01-01", periods=10, freq="7D"))
    assert moc_phat_hien(pd.Timestamp("2026-01-03"), moc) == pd.Timestamp("2026-01-15")      # 01-08 moi thay 6 ngay
    cap = [("A", "k", pd.Timestamp("2026-02-01"), pd.Timestamp("2026-02-10"), 1.0)]
    assert not khong_su_kien("A", pd.Timestamp("2026-02-15"), cap) and khong_su_kien("A", pd.Timestamp("2026-04-01"), cap)
    assert khong_su_kien("B", pd.Timestamp("2026-02-15"), cap)


def test_danh_gia_dot_bien():
    moc = list(pd.date_range("2026-01-01", periods=12, freq="7D"))
    cap = [(f"M{i}", "k", pd.Timestamp("2026-02-01"), pd.Timestamp("2026-02-20"), 1.0) for i in range(4)]
    m_det = moc_phat_hien(pd.Timestamp("2026-02-01"), moc)
    idx, v = [], []
    for i in range(10):
        for m in moc:
            idx.append((f"M{i}", m))
            v.append(8.0 if (i < 3 and m == m_det) else 1.0)
    ts = pd.Series(v, index=pd.MultiIndex.from_tuples(idx, names=["ma_sku", "moc"]))
    r = danh_gia_dot_bien(ts, cap, moc, 4)
    assert r["so_cap_dot"] == 4 and r["phat_hien"] == pytest.approx(0.75) and r["nen_duong"] == pytest.approx(0.0) and r["dat"]
    r2 = danh_gia_dot_bien(ts, cap, moc, 9)
    assert r2["phat_hien"] == pytest.approx(0.0) and not r2["dat"]
