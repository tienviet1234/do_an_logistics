"""Test chi so kho. Chay tai thu muc goc: python -m pytest tests/test_chi_so_kho.py"""
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from chi_so_kho import chi_so_theo_nhom, ton_du_mot_ma, ton_du_theo_ma, vong_quay_doh  # noqa: E402


def test_vong_quay_tinh_tay():
    vq, doh = vong_quay_doh(3650, 100, 365)                 # xuat 10/ngay, ton 100
    assert vq == pytest.approx(36.5) and doh == pytest.approx(10)


def test_vong_quay_nhan_doh_luon_bang_365():
    for x, t, n in [(287e9, 11.9e9, 364), (5, 7, 30), (1, 1000, 100)]:
        vq, doh = vong_quay_doh(x, t, n)
        assert vq * doh == pytest.approx(365)


def test_quy_doi_ve_365_ngay():
    assert vong_quay_doh(1000, 100, 182)[0] == pytest.approx(1000 * 365 / (182 * 100))


def test_truong_hop_bien():
    vq, doh = vong_quay_doh(0, 100, 365)                    # co ton, khong xuat: dong von mai mai
    assert vq == 0 and math.isinf(doh)
    vq, doh = vong_quay_doh(100, 0, 365)                    # co xuat, khong ton
    assert math.isinf(vq) and doh == 0
    assert all(math.isnan(v) for v in vong_quay_doh(0, 0, 365))
    with pytest.raises(ValueError):
        vong_quay_doh(1, 1, 0)
    with pytest.raises(ValueError):
        vong_quay_doh(-1, 1, 1)


def test_cong_gia_tri_truoc_khi_chia():
    k = pd.DataFrame({"nhom": ["a", "a"], "da_dap_ung": [100.0, 0.0], "gia_von": [10.0, 10.0], "gia_tri_ton_tb": [10.0, 90.0]})
    r = chi_so_theo_nhom(k, ["nhom"], 100).iloc[0]
    assert r.doh == pytest.approx(100 * 100 / 1000)         # 10 ngay; neu lay TB 2 ty le se ra vo cuc


def test_ton_du_tinh_tay():
    # ton 10 moi ngay, nhu cau 1/ngay, cua so 3: 3 ngay ke tiep can 3 -> du 7; 3 ngay cuoi khong du cua so
    du = ton_du_mot_ma([10] * 6, [1] * 6, cua_so=3)
    assert du[:3].tolist() == [7, 7, 7] and np.isnan(du[3:]).all()


def test_ton_du_khong_am_va_khong_tinh_nhu_cau_hom_nay():
    assert ton_du_mot_ma([1, 1, 1], [0, 5, 5], cua_so=2)[0] == 0
    assert ton_du_mot_ma([10, 0, 0, 0], [99, 1, 1, 0], cua_so=2)[0] == 8      # nhu cau ngay 0 khong tinh, chi ngay 1, 2


def test_chuoi_ngan_hon_cua_so_khong_loi():
    assert np.isnan(ton_du_mot_ma([1, 2], [1, 1], cua_so=5)).all()
    with pytest.raises(ValueError):
        ton_du_mot_ma([1], [1, 2])


def test_ton_du_theo_ma_xep_ngay_va_khong_lan_giua_cac_ma():
    n = 30
    d = pd.date_range("2026-01-01", periods=n).strftime("%Y-%m-%d")
    a = pd.DataFrame({"ma_sku": "A", "ngay": d, "ton_cuoi": 100.0, "nhu_cau": 1.0})     # du 72 moi ngay
    b = pd.DataFrame({"ma_sku": "B", "ngay": d, "ton_cuoi": 5.0, "nhu_cau": 100.0})     # khong du
    tron = pd.concat([a, b]).sample(frac=1, random_state=1)
    r = ton_du_theo_ma(tron, pd.Series({"A": 2.0, "B": 3.0})).set_index("ma_sku")
    assert r.du_tb.A == pytest.approx(72 * 2) and r.du_tb.B == 0
    assert r.ton_tb.A == pytest.approx(200) and r.ton_tb.B == pytest.approx(15)


def test_doi_chieu_voi_co_so_du_lieu():
    """Hai nguon doc lap trong CSDL (tong hop theo ma, mo phong theo ngay) phai cho cung vong quay."""
    from csdl import doc
    so_ngay = doc("SELECT COUNT(DISTINCT ngay) AS n FROM mo_phong_ngay").n.iloc[0]
    assert so_ngay > 0
    gia = doc("SELECT ma_sku, gia_von FROM dm_sku").set_index("ma_sku").gia_von
    for cs in ["cong_thuc_du_bao_ai_hc", "cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "hien_trang"]:
        k = doc("SELECT * FROM ket_qua_ton_kho WHERE ma_chinh_sach = ? AND ROUND(muc_phuc_vu, 2) = 0.95", (cs,))
        r = chi_so_theo_nhom(k.assign(gia_von=k.ma_sku.map(gia), c=1), ["c"], so_ngay).iloc[0]
        m = doc("SELECT ma_sku, xuat, ton_cuoi FROM mo_phong_ngay WHERE ma_chinh_sach = ?", (cs,))
        vq2, doh2 = vong_quay_doh((m.xuat * m.ma_sku.map(gia)).sum(), (m.ton_cuoi * m.ma_sku.map(gia)).sum() / so_ngay, so_ngay)
        assert r.vong_quay == pytest.approx(vq2, rel=1e-3) and r.doh == pytest.approx(doh2, rel=1e-3)
