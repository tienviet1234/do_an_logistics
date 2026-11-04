"""Test han su dung va suc chua. Chay: python -m pytest tests/test_rang_buoc_kho.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from gom_don import mo_phong  # noqa: E402
from rang_buoc_kho import (THE_TICH_MAC_DINH, ban_fifo, bo_het_han, cat_theo_cho, chan_doan, chi_tieu_chua, ton_vuot_nhu_cau, chi_tieu_han, giu_phuong_an, han_cua_ma, mo_phong_kho, so_ngay_duoc_giao,  # noqa: E402
                           the_tich_cua_ma, the_tich_vung, uoc_luong_luc_ve, vung_cua_ma, vuot_suc_chua)


def khung(n=120, lt=2, muc=10):
    sku = pd.DataFrame({"ma_sku": ["A", "B", "C"], "ma_ncc": ["N1", "N1", "N2"], "chi_phi_dat_hang": [100.0, 200.0, 300.0], "ty_le_chi_phi_luu_kho": 0.2, "gia_von": 10.0,
                        "gia_ban": 12.0, "moq": 1.0, "lead_time_tb": float(lt), "lead_time_std": 0.5, "xyz_train": ["X", "Z", "X"]})
    rng = np.random.default_rng(3)
    return dict(sku=sku, dem=rng.poisson(muc, (3, n)).astype(float), closed=np.arange(n) % 30 == 29, LT=np.full((3, n), lt), init=[50.0, 50.0, 50.0], pipe0=[[], [], []])


F = np.full((3, 5, 28), 10.0)
SIG = np.array([5.0, 5.0, 5.0])


def test_han_theo_tu_khoa_nhom_va_ma_khong_xet():
    assert han_cua_ma("Sữa chua Vinamilk lốc 4 hộp", "Sữa") == 30
    assert han_cua_ma("Sữa tươi Vinamilk 1L thùng 12", "Sữa") == 180
    assert han_cua_ma("Sữa gì đó mới", "Sữa") == 180                     # theo nhom
    assert han_cua_ma("Rượu vang Đà Lạt chai", "Đồ uống") is None
    assert han_cua_ma("Bột giặt OMO 3kg", "Hóa phẩm") is None
    assert han_cua_ma("Trà thượng hạng hộp quà biếu", "Quà tặng") is None  # "trà" o nhom khong phai thuc pham
    assert han_cua_ma("Kem chống nắng Nivea 50ml", "Mỹ phẩm") is None
    assert han_cua_ma("Mì gói Hảo Hảo thùng 30 gói", "Thực phẩm khô") == 180


def test_the_tich_va_vung():
    assert the_tich_cua_ma("Cây thông Noel 1m2", "cái") == 120
    assert the_tich_cua_ma("Coca-Cola lon 330ml thùng 24", "thùng") == 25
    assert the_tich_cua_ma("Hàng lạ", "kiểu lạ") == THE_TICH_MAC_DINH
    assert vung_cua_ma("Kem Wall's hộp 1L", "Kem & đông lạnh") == 1 and vung_cua_ma("Sữa chua Vinamilk", "Sữa") == 1 and vung_cua_ma("Sữa tươi", "Sữa") == 0


def test_quy_tac_mot_phan_ba():
    assert so_ngay_duoc_giao(30) == 10 and so_ngay_duoc_giao(30, 0.5) == 5 and so_ngay_duoc_giao(1) == 1 and so_ngay_duoc_giao(None) is None


def test_bo_het_han_va_fifo_tinh_tay():
    lo = [[5, 10.0], [7, 20.0], [9, 30.0]]
    assert bo_het_han(lo, 4) == 0 and len(lo) == 3
    assert bo_het_han(lo, 5) == 10 and lo == [[7, 20.0], [9, 30.0]]
    ban_fifo(lo, 25)
    assert lo == [[9, 25.0]]                                               # lo ve truoc ban truoc
    ban_fifo(lo, 25)
    assert lo == []


def test_cat_theo_cho_tinh_tay():
    assert cat_theo_cho(100, 2.0, 500.0, 10) == 100                         # du cho
    assert cat_theo_cho(100, 2.0, 100.0, 10) == 50                          # chi con cho cho 50
    assert cat_theo_cho(100, 2.0, 10.0, 10) == 0                            # con cho 5 < MOQ
    assert cat_theo_cho(100, 2.0, -5.0, 10) == 0
    assert uoc_luong_luc_ve(100, 10, 3, 2.0) == 140 and uoc_luong_luc_ve(10, 10, 3, 2.0) == 0


def test_vuot_suc_chua_tinh_tay():
    tt = the_tich_vung(np.array([[1.0, 5.0], [2.0, 2.0]]), [10.0, 4.0], [0, 1])
    assert tt.tolist() == [[10.0, 50.0], [8.0, 8.0]]
    v = vuot_suc_chua(tt, [20.0, 8.0])
    assert v["lit_ngay"] == 30 and v["so_ngay"] == 1 and v["theo_vung"] == [30, 0] and v["dinh_pt"] == [250, 100]


def test_khong_rang_buoc_trung_mo_phong_dang_dung():
    inp = khung()
    a, b = mo_phong(inp, F, SIG, 1.64, 28), mo_phong_kho(inp, F, SIG, 1.64, 28)
    for c in ("nhap", "xuat", "ton", "dat"):
        assert np.array_equal(a[c], b[c]), c
    assert (b["huy"] == 0).all() and b["so_lan_cat"] == 0


def test_han_rat_dai_khong_loai_gi_va_trung_khong_han():
    inp = khung()
    a, b = mo_phong_kho(inp, F, SIG, 1.64, 28), mo_phong_kho(inp, F, SIG, 1.64, 28, [10_000] * 3)
    assert (b["huy"] == 0).all() and np.array_equal(a["ton"], b["ton"]) and np.array_equal(a["dat"], b["dat"])


def test_bao_toan_hang_khi_co_han():
    inp = khung()
    r = mo_phong_kho(inp, F, SIG, 1.64, 28, [3, None, 3])
    du = np.array(inp["init"]) + r["nhap"].sum(1) - r["xuat"].sum(1) - r["huy"].sum(1) - r["ton"][:, -1]
    assert np.allclose(du, 0)
    assert r["huy"][1].sum() == 0 and r["huy"][0].sum() > 0 and (r["ton"] >= 0).all()


def test_hang_het_han_tinh_tay():
    """Khong nhu cau, khong dat (ROP = 0): ton dau ky 50, duoc giao 6 ngay nen da dung nua khoang: bo het o dau ngay chi so 3."""
    inp = khung(n=10)
    inp["sku"] = inp["sku"].iloc[:1]
    inp.update(dem=np.zeros((1, 10)), closed=np.zeros(10, dtype=bool), LT=np.full((1, 10), 2), init=[50.0], pipe0=[[]])
    r = mo_phong_kho(inp, np.zeros((1, 5, 28)), np.zeros(1), 1.64, 28, [6])
    assert r["huy"][0, 3] == 50 and r["huy"][0].sum() == 50 and r["ton"][0, 2] == 50 and r["ton"][0, 3] == 0


def test_lo_ve_sau_con_han_rieng():
    """Hang ve ngay 2 duoc giao 4 ngay: bo o ngay 6, khong bo cung lo dau."""
    inp = khung(n=10)
    inp["sku"] = inp["sku"].iloc[:1]
    inp.update(dem=np.zeros((1, 10)), closed=np.zeros(10, dtype=bool), LT=np.full((1, 10), 2), init=[50.0], pipe0=[[(2, 30.0)]])
    r = mo_phong_kho(inp, np.zeros((1, 5, 28)), np.zeros(1), 1.64, 28, [4])
    assert r["huy"][0, 2] == 50 and r["huy"][0, 6] == 30 and r["huy"][0].sum() == 80


def test_ngay_nghi_khong_bo_khong_nhan_khong_ban():
    inp = khung()
    r = mo_phong_kho(inp, F, SIG, 1.64, 28, [3, 3, 3])
    for c in ("nhap", "xuat", "dat", "huy"):
        assert (r[c][:, inp["closed"]] == 0).all(), c


def test_tran_han_chan_luong_dat():
    inp = khung()
    inp["sku"] = inp["sku"].assign(chi_phi_dat_hang=1e7)            # EOQ rat lon
    ng = [2, 2, 2]
    r0 = mo_phong_kho(inp, F, SIG, 1.64, 28, ng)
    r1 = mo_phong_kho(inp, F, SIG, 1.64, 28, ng, tran_han=True)
    assert r0["dat"][0].max() > 20 and r1["dat"][0].max() <= 20      # 10/ngay x 2 ngay
    assert r1["huy"].sum() < r0["huy"].sum()
    inp["sku"] = inp["sku"].assign(moq=100.0)
    r2 = mo_phong_kho(inp, F, SIG, 1.64, 28, ng, tran_han=True)
    assert r2["dat"][0][r2["dat"][0] > 0].min() >= 100                # khong dat duoi MOQ du co tran


def test_cat_don_giu_trong_suc_chua_va_uu_tien_ma_it_ton():
    inp = khung()
    tt, vung = np.array([1.0, 1.0, 1.0]), np.array([0, 0, 0])
    goc = mo_phong_kho(inp, F, SIG, 1.64, 28)
    dinh = the_tich_vung(goc["ton"], tt, vung).max(axis=1)
    cap = [dinh[0] * 0.5, 0.0]
    b = mo_phong_kho(inp, F, SIG, 1.64, 28, the_tich=tt, vung=vung, suc_chua=cap)
    assert b["so_lan_cat"] > 0 and the_tich_vung(b["ton"], tt, vung).max() < dinh[0] and b["dat"].sum() < goc["dat"].sum()
    # A het hang, B, C day kho: chi con cho cho 1 ma thi A duoc dat
    inp2 = khung(n=3)
    inp2.update(dem=np.zeros((3, 3)), closed=np.zeros(3, dtype=bool), LT=np.full((3, 3), 2), init=[0.0, 0.0, 5.0], pipe0=[[], [], []])
    F2 = np.full((3, 5, 28), 10.0)
    r = mo_phong_kho(inp2, F2, np.zeros(3), 1.64, 28, the_tich=tt, vung=vung, suc_chua=[1.0, 0.0])
    assert r["dat"].sum(axis=1)[2] == 0                               # C con hang: dat sau, khong con cho


def test_cat_don_theo_tung_vung():
    inp = khung()
    tt, vung = np.array([1.0, 1.0, 1.0]), np.array([0, 0, 1])
    r = mo_phong_kho(inp, F, SIG, 1.64, 28, the_tich=tt, vung=vung, suc_chua=[1e9, 0.0])
    assert r["dat"][2].sum() == 0 and r["dat"][0].sum() > 0           # kho lanh het cho khong anh huong kho thuong


def test_chi_tieu_cong_dung_va_luat():
    inp = khung()
    r = mo_phong_kho(inp, F, SIG, 1.64, 28, [3, 3, 3])
    t = chi_tieu_han(inp, r)
    assert t["huy_gia_tri"] == pytest.approx(r["huy"].sum() * 10) and t["cp_tong"] == pytest.approx(t["cp_gom"] + t["huy_gia_tri"])
    assert chi_tieu_han(inp, r, ti_le_mat=0.5)["cp_tong"] == pytest.approx(t["cp_gom"] + 0.5 * t["huy_gia_tri"])
    assert chi_tieu_han(inp, r, np.array([0]))["huy_sl"] == r["huy"][0].sum()
    tt, vung = np.ones(3), np.zeros(3, dtype=int)
    c = chi_tieu_chua(inp, r, tt, vung, [10.0, 0.0], gia_thue=2.0)
    assert c["thue"] == pytest.approx(c["lit_ngay"] * 2) and c["cp_chua"] == pytest.approx(c["cp_gom"] + c["thue"])
    goc = dict(cp_tong=1000.0, fill_rate=96.0)
    assert giu_phuong_an(dict(cp_tong=990.0, fill_rate=96.0), goc) and not giu_phuong_an(dict(cp_tong=996.0, fill_rate=96.0), goc) and not giu_phuong_an(dict(cp_tong=900.0, fill_rate=95.7), goc)


def test_ton_vuot_nhu_cau_tinh_tay_va_bo_ngay_cuoi():
    ton = np.array([[10.0, 10.0, 10.0, 10.0]])
    D = np.array([[0.0, 3.0, 3.0, 99.0]])
    vuot, tong = ton_vuot_nhu_cau(ton, D, [2.0], so_ngay=2)
    # ngay 0: 2 ngay sau ban 6 nen vuot 4; ngay 1: 3 + 99 nen khong vuot; 2 ngay cuoi khong tinh
    assert vuot[0] == pytest.approx(4 * 2) and tong[0] == pytest.approx(20 * 2)
    with pytest.raises(ValueError):
        ton_vuot_nhu_cau(ton, D, [2.0], so_ngay=4)


def test_chan_doan_chi_ra_dung_ma_lech_va_hang_dip_le():
    inp = khung()
    inp["sku"] = inp["sku"].assign(ten_sku=["a", "b", "c"], loai_mua_vu=["Quanh năm", "Chỉ dịp Tết", "Quanh năm"])
    ra = mo_phong_kho(inp, F, SIG, 1.64, 28)
    ton = ra["ton"].copy()
    ton[1] += 1000                                                     # ma B ton lech xa
    n = inp["dem"].shape[1]
    inp["obs"] = dict(ton_cuoi_ngay=ra["ton"].copy(), qty_in=ra["nhap"].copy())
    ra_han = dict(huy=np.array([[0.0] * n, [5.0] * n, [0.0] * n]))
    cap = float(ton[[0, 2]].sum(axis=0).max())                         # vua du cho A + C: chi B lam vuot
    assert vuot_suc_chua(the_tich_vung(ton, [1.0, 1.0, 1.0], [0, 0, 0]), [cap, 1.0])["so_ngay"] > 0
    c = chan_doan(inp, dict(ra, ton=ton), ra_han, [1.0, 1.0, 1.0], [0, 0, 0], [cap, 1.0])
    assert c["top"][0]["ma"] == "B" and c["top"][0]["lit_tb"] == pytest.approx(ton[1].mean())
    assert c["loai_dip_le_pt"] == 100 and c["so_ma_loai"] == 1 and c["so_ma_dip_le"] == 1 and c["vuot_z_pt"] > 50
    assert c["bo_ma_lon_nhat"]["so_ngay"] == 0                         # bo B thi khong con vuot


def test_du_lieu_vao_sai():
    inp = khung()
    with pytest.raises(ValueError):
        mo_phong_kho(inp, F, SIG, 1.64, 28, [3])
    with pytest.raises(ValueError):
        mo_phong_kho(inp, F, SIG, 1.64, 28, suc_chua=[1.0, 1.0])


def test_khong_rang_buoc_trung_csdl():
    """Doi chieu voi CSDL: phai cho dung luong dat, ton, xuat tung ma tung ngay cua chinh sach AI + hieu chinh."""
    from csdl import doc
    from gom_don import chuan_bi
    inp, Ft, sig, z, buoc = chuan_bi("test")
    ra = mo_phong_kho(inp, Ft, sig, z, buoc)
    m = doc("SELECT ngay, ma_sku, xuat, ton_cuoi, dat_hang, nhap FROM mo_phong_ngay WHERE ma_chinh_sach = 'cong_thuc_du_bao_ai_hc'")
    for cot, ten in [("xuat", "xuat"), ("ton_cuoi", "ton"), ("dat_hang", "dat"), ("nhap", "nhap")]:
        b = m.pivot(index="ma_sku", columns="ngay", values=cot).reindex(index=inp["sku"].ma_sku, columns=inp["ds"]).values
        assert np.allclose(np.nan_to_num(b), ra[ten], atol=1e-6), cot
