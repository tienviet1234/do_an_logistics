"""Test gom don. Quan trong nhat: khong dat kem thi phai trung dung mo phong dang dung. Chay: python -m pytest tests/test_gom_don.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from gom_don import chi_phi_phieu, giu_dat_kem, gom_cung_ngay, mo_phong, so_luong, tach_loi_ich, tong_ket  # noqa: E402


def test_phieu_mot_dong_dung_bang_chi_phi_cu():
    for t in [0, 0.3, 0.5, 1]:
        assert chi_phi_phieu([120000], t) == pytest.approx(120000)


def test_phieu_nhieu_dong_tinh_tay():
    assert chi_phi_phieu([100, 200], 0.5) == pytest.approx(0.5 * 200 + 0.5 * 300)
    assert chi_phi_phieu([100, 200], 0) == 300 and chi_phi_phieu([100, 200], 1) == 200 and chi_phi_phieu([], 0.5) == 0
    with pytest.raises(ValueError):
        chi_phi_phieu([1], 1.5)


def test_gom_cung_ngay_tinh_tay():
    dat = np.array([[5, 0, 1], [7, 0, 0], [3, 2, 0]])      # 3 ma, 3 ngay
    r = gom_cung_ngay(dat, ["N1", "N1", "N2"], [100, 200, 300], 0.5)
    assert r["so_dong"] == 5 and r["so_phieu"] == 4          # ngay 0: N1 (2 dong) + N2; ngay 1: N2; ngay 2: N1
    assert r["chi_phi_rieng"] == 100 + 200 + 300 + 300 + 100
    assert r["chi_phi_gom"] == pytest.approx(0.5 * 200 + 0.5 * 300 + 300 + 300 + 100)


def test_khong_co_don_va_sai_kich_thuoc():
    assert gom_cung_ngay(np.zeros((2, 3)), ["a", "b"], [1, 1])["so_phieu"] == 0
    with pytest.raises(ValueError):
        gom_cung_ngay(np.zeros((2, 3)), ["a"], [1, 1])


def test_gom_khong_bao_gio_dat_hon_va_khong_tang_chi_phi():
    rng = np.random.default_rng(1)
    dat = rng.integers(0, 2, (9, 40))
    r = gom_cung_ngay(dat, list("aaabbbccc"), rng.integers(100, 300, 9), 0.5)
    assert r["chi_phi_gom"] <= r["chi_phi_rieng"] and r["so_phieu"] <= r["so_dong"]


def test_so_luong_cung_cong_thuc():
    assert so_luong("eoq", 50, 100, 30, 10, 0, 0) == 60                       # bo so 30 de vuot muc 100
    assert so_luong("eoq", 100, 100, 30, 10, 0, 0) == 30                       # dung bang muc van dat 1 lo
    assert so_luong("eoq", 50, 100, 5, 40, 0, 0) == 80                         # MOQ lon hon EOQ
    assert so_luong("dat_den_muc", 50, 100, 0, 10, 80, 20) == 50
    assert so_luong("dat_den_muc", 99, 100, 0, 10, 80, 20) == 10               # toi thieu MOQ


def khung(n=120, lt=2):
    sku = pd.DataFrame({"ma_sku": ["A", "B", "C"], "ma_ncc": ["N1", "N1", "N2"], "chi_phi_dat_hang": [100.0, 200.0, 300.0], "ty_le_chi_phi_luu_kho": 0.2, "gia_von": 10.0,
                        "gia_ban": 12.0, "moq": 1.0, "lead_time_tb": float(lt), "lead_time_std": 0.5, "xyz_train": ["X", "Z", "X"]})
    rng = np.random.default_rng(3)
    return dict(sku=sku, dem=rng.poisson(10, (3, n)).astype(float), closed=np.arange(n) % 30 == 29, LT=np.full((3, n), lt), init=[50.0, 50.0, 50.0], pipe0=[[], [], []])


def test_bao_toan_hang():
    inp = khung()
    ra = mo_phong(inp, np.full((3, 5, 28), 10.0), np.array([5.0, 5.0, 5.0]), 1.64, 28, k_ngay=2)
    dang_ve = np.array(inp["init"]) + ra["nhap"].sum(1) - ra["xuat"].sum(1) - ra["ton"][:, -1]
    assert np.allclose(dang_ve, 0)
    assert (ra["xuat"] <= inp["dem"] + 1e-9).all() and (ra["ton"] >= 0).all()


def test_ngay_nghi_khong_dat_khong_nhan_khong_ban():
    inp = khung()
    ra = mo_phong(inp, np.full((3, 5, 28), 10.0), np.array([5.0, 5.0, 5.0]), 1.64, 28, k_ngay=2)
    for c in ["nhap", "xuat", "dat"]:
        assert (ra[c][:, inp["closed"]] == 0).all()


def test_dat_kem_chi_khi_cung_nha_cung_cap_co_ma_phai_dat():
    inp = khung()
    inp["init"] = [0.0, 1000.0, 1000.0]                    # A phai dat ngay dau; B cung N1 nhieu hang; C khac N1
    F = np.full((3, 5, 28), 10.0)
    r0 = mo_phong(inp, F, np.zeros(3), 1.64, 28, k_ngay=0)
    assert r0["dat"][0, 0] > 0 and r0["dat"][1, 0] == 0
    # sau khi ban ngay dau B, C con 40: tren ROP (20 + 1,64 x 10 x 0,5 = 28,2), duoi muc dat kem (28,2 + 3 x 10 = 58,2)
    inp["init"] = [0.0, inp["dem"][1, 0] + 40.0, inp["dem"][2, 0] + 40.0]
    r1 = mo_phong(inp, F, np.zeros(3), 1.64, 28, k_ngay=3)
    assert r1["dat"][1, 0] > 0                             # B cung nha cung cap voi A: dat kem
    assert r1["dat"][2, 0] == 0                            # C nha cung cap khac: khong dat kem
    r2 = mo_phong(inp, F, np.zeros(3), 1.64, 28, k_ngay=0)
    assert r2["dat"][1, 0] == 0                            # k = 0: khong dat kem


def test_luat_giu_dat_kem():
    goc = dict(cp_gom=1000.0, fill_rate=96.0)
    assert giu_dat_kem(dict(cp_gom=990.0, fill_rate=96.0), goc)
    assert not giu_dat_kem(dict(cp_gom=996.0, fill_rate=96.0), goc)         # giam chua du 0,5%
    assert not giu_dat_kem(dict(cp_gom=900.0, fill_rate=95.7), goc)         # Fill Rate giam qua 0,2 diem


def test_tach_loi_ich_cong_lai_dung_tong():
    goc = dict(chi_phi_gom=100.0, luu=50.0, loi_nhuan_mat=30.0)
    moi = dict(chi_phi_gom=80.0, luu=60.0, loi_nhuan_mat=10.0)
    t = tach_loi_ich(moi, goc)
    assert t == dict(dat_hang=20.0, luu_kho=-10.0, loi_nhuan_mat=20.0, tong=30.0)


def test_tong_ket_khop_cong_thuc_chi_phi():
    inp = khung()
    ra = mo_phong(inp, np.full((3, 5, 28), 10.0), np.array([5.0, 5.0, 5.0]), 1.64, 28)
    t = tong_ket(inp, ra, 0.5)
    assert t["cp_gom"] == pytest.approx(t["chi_phi_gom"] + t["luu"] + t["loi_nhuan_mat"]) and t["cp_gom"] <= t["cp_rieng"]


@pytest.mark.parametrize("tap", ["test"])
def test_khong_dat_kem_trung_dung_mo_phong_dang_dung(tap):
    """Doi chieu voi CSDL: k = 0 phai cho dung luong dat, ton, xuat tung ma tung ngay cua chinh sach AI + hieu chinh."""
    from csdl import doc
    from gom_don import chuan_bi
    inp, F, sig, z, buoc = chuan_bi(tap)
    ra = mo_phong(inp, F, sig, z, buoc)
    m = doc("SELECT ngay, ma_sku, xuat, ton_cuoi, dat_hang, nhap FROM mo_phong_ngay WHERE ma_chinh_sach = 'cong_thuc_du_bao_ai_hc'")
    for cot, ten in [("xuat", "xuat"), ("ton_cuoi", "ton"), ("dat_hang", "dat"), ("nhap", "nhap")]:
        b = m.pivot(index="ma_sku", columns="ngay", values=cot).reindex(index=inp["sku"].ma_sku, columns=inp["ds"]).values
        assert np.allclose(np.nan_to_num(b), ra[ten], atol=1e-6), cot
