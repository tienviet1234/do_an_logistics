"""Test newsvendor hang chi ban dip le. Chay: python -m pytest tests/test_newsvendor_mua_vu.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from newsvendor_mua_vu import (bang_cap_mua, cac_mua, chi_phi_du, chon_phuong_an, lap_ke_hoach, mua_dai_hon_han, mau_r, ngay_dat_cua, q_mua, su_kien_cua_ma, tong_mua, ton_sau_mua)  # noqa: E402
from rang_buoc_kho import mo_phong_kho, trang_thai_mua  # noqa: E402

LICH = pd.DataFrame({"ten_su_kien": ["noel", "noel", "noel", "tet"], "ngay": ["2023-12-24", "2024-12-24", "2025-12-24", "2024-02-10"], "cua_so_truoc": [-20, -20, -20, -28], "cua_so_sau": [1, 1, 1, 7]})


def khung(n=60, q=None):
    sku = pd.DataFrame({"ma_sku": ["A", "B"], "ma_ncc": ["N1", "N2"], "chi_phi_dat_hang": [100.0, 100.0], "ty_le_chi_phi_luu_kho": 0.2, "gia_von": 10.0, "gia_ban": 12.0, "moq": 1.0,
                        "lead_time_tb": 2.0, "lead_time_std": 0.5, "xyz_train": ["Z", "X"], "loai_mua_vu": ["Chỉ dịp Noel", "Quanh năm"], "ten_sku": ["a", "b"], "nhom_hang": ["x", "x"], "don_vi": ["cái", "cái"]})
    return dict(sku=sku, dem=np.zeros((2, n)), closed=np.zeros(n, dtype=bool), LT=np.full((2, n), 2), init=[0.0, 0.0], pipe0=[[], []], ds=[str(d.date()) for d in pd.date_range("2025-01-01", periods=n)])


def test_su_kien_cua_ma():
    assert su_kien_cua_ma("Chỉ dịp Tết") == "tet" and su_kien_cua_ma("Chỉ dịp Trung thu") == "trung_thu"
    assert su_kien_cua_ma("Quanh năm") is None and su_kien_cua_ma("Chỉ dịp lạ") is None and su_kien_cua_ma(None) is None


def test_cac_mua_dung_cua_so_va_thu_tu():
    m = cac_mua(LICH, "noel")
    assert len(m) == 3 and m[0] == (pd.Timestamp("2023-12-04"), pd.Timestamp("2023-12-25")) and m[0][0] < m[1][0]
    assert cac_mua(LICH, "khong_co") == []


def test_tong_mua_khong_du_lieu_thi_none():
    c = pd.Series(1.0, index=pd.date_range("2025-01-01", periods=10))
    assert tong_mua(c, pd.Timestamp("2025-01-02"), pd.Timestamp("2025-01-04")) == 3
    assert tong_mua(c, pd.Timestamp("2024-12-31"), pd.Timestamp("2025-01-04")) is None        # thieu dau mua: khong coi la mua day du
    assert tong_mua(c, pd.Timestamp("2025-01-08"), pd.Timestamp("2025-01-12")) is None


def test_bang_cap_mua_va_mau_r_khong_nhin_truoc():
    idx = pd.date_range("2023-01-01", "2026-01-31")
    c = {"A": pd.Series(1.0, index=idx), "B": pd.Series(2.0, index=idx)}
    cap = bang_cap_mua(c, {"A": "noel", "B": "noel"}, LICH)
    assert len(cap) == 4 and (cap.truoc == [22, 22, 44, 44]).all() and (cap.nay == cap.truoc).all()
    cap = cap.assign(nay=[11.0, 33.0, 44.0, 66.0])
    r = mau_r(cap, "A", pd.Timestamp("2025-01-01"))                                          # chi cac cap ket thuc truoc ngay dat
    assert sorted(r) == [0.5, 1.0]
    assert len(mau_r(cap, "A", pd.Timestamp("2024-12-25"))) == 0                             # dung ngay ket thuc: chua biet
    r2 = mau_r(cap, "A", pd.Timestamp("2024-11-01"), cung_nam=(pd.Timestamp("2024-12-01"), pd.Timestamp("2024-12-31")))
    assert list(r2) == [1.0]                                                                 # bo chinh ma A


def test_q_mua_tinh_tay():
    r = np.array([0.8, 1.0, 1.2])
    assert q_mua(100, r, 1, 1, 5) == 100                                                     # phan vi 50%
    assert q_mua(100, r, 3, 1, 5) == np.ceil(100 * np.quantile(r, 0.75))
    assert q_mua(100, r, 1, 3, 5) == np.ceil(100 * np.quantile(r, 0.25))
    assert q_mua(1, r, 1, 1, 50) == 50                                                       # toi thieu MOQ
    assert q_mua(100, r, 0, 1, 5) == 0 and q_mua(100, r, -1, 1, 5) == 0                      # ban lo
    assert q_mua(100, np.array([]), 1, 1, 5) is None


def test_chi_phi_du_theo_han():
    assert chi_phi_du(100, 0.2, 180) == 100 and chi_phi_du(100, 0.2, 180, 0.5) == 50
    assert chi_phi_du(100, 0.2, None) == 20                                                  # khong han: 1 nam luu kho


def test_ngay_dat_tinh_tay():
    assert ngay_dat_cua(pd.Timestamp("2025-12-04"), 10, 2.4) == pd.Timestamp("2025-12-04") - pd.Timedelta(days=15)     # 10 + ceil(4,8)
    assert ngay_dat_cua(pd.Timestamp("2025-12-04"), 10, 0) == pd.Timestamp("2025-11-24")


def test_trang_thai_mua():
    m = [dict(t_dat=5, t_dau=10, t_cuoi=20, q=50.0, bo_sung=False)]
    da = set()
    assert trang_thai_mua(m, 4, 2, da) == (True, None)                                       # ngoai mua: quy tac thuong
    assert trang_thai_mua(m, 5, 2, da) == (False, 50.0)                                      # ngay dat
    assert trang_thai_mua(m, 6, 2, da) == (False, None)                                      # chi dat 1 lan
    assert trang_thai_mua(m, 21, 2, da) == (True, None)
    m2 = [dict(m[0], bo_sung=True)]
    da2 = {0}
    assert trang_thai_mua(m2, 8, 2, da2) == (False, None)                                    # truoc mua chua bo sung
    assert trang_thai_mua(m2, 12, 2, da2) == (True, None)                                    # trong mua, hang ve kip
    assert trang_thai_mua(m2, 19, 2, da2) == (False, None)                                   # hang ve sau khi het mua


def test_mo_phong_dat_mot_lan_tru_hang_da_co():
    inp = khung()
    inp["dem"][0, 30:40] = 10
    inp["init"] = [30.0, 0.0]
    kh = {0: [dict(t_dat=20, t_dau=30, t_cuoi=45, q=100.0, bo_sung=False)]}
    F = np.zeros((2, 10, 28))
    r = mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach=kh)
    assert r["dat"][0, 20] == 70 and r["dat"][0, :46].sum() == 70                            # 100 - 30 da co, dung 1 lan; sau mua quy tac thuong lai chay
    assert r["nhap"][0, 22] == 70 and r["xuat"][0].sum() == 100 and r["ton"][0, 45] == 0


def test_mo_phong_du_hang_khong_dat_va_ngay_nghi_doi_ngay_mo():
    inp = khung()
    inp["init"] = [200.0, 0.0]
    kh = {0: [dict(t_dat=20, t_dau=30, t_cuoi=45, q=100.0, bo_sung=False)]}
    F = np.zeros((2, 10, 28))
    assert mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach=kh)["dat"][0].sum() == 0
    inp2 = khung()
    inp2["init"] = [40.0, 0.0]                                       # con hang: quy tac thuong khong dat truoc ngay dat (ROP = 0)
    inp2["closed"][20] = True
    r = mo_phong_kho(inp2, F, np.zeros(2), 1.64, 7, ke_hoach=kh)
    assert r["dat"][0, 20] == 0 and r["dat"][0, 21] == 60 and r["dat"][0, :46].sum() == 60


def test_trong_mua_chan_quy_tac_thuong_va_bo_sung_mo_lai():
    inp = khung()
    inp["dem"][0] = 5
    inp["init"] = [0.0, 0.0]
    F = np.full((2, 10, 28), 5.0)
    kh = {0: [dict(t_dat=10, t_dau=20, t_cuoi=40, q=10.0, bo_sung=False)]}
    r = mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach=kh)
    assert r["dat"][0, 11:41].sum() == 0 and r["dat"][0, :10].sum() > 0 and r["dat"][0, 41:].sum() > 0
    kh2 = {0: [dict(kh[0][0], bo_sung=True)]}
    r2 = mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach=kh2)
    assert r2["dat"][0, 20:39].sum() > 0 and r2["dat"][0, 11:20].sum() == 0


def test_khong_ke_hoach_khong_doi_va_ma_khac_khong_anh_huong():
    inp = khung()
    inp["dem"][:] = 5
    F = np.full((2, 10, 28), 5.0)
    a, b = mo_phong_kho(inp, F, np.zeros(2), 1.64, 7), mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach={})
    assert np.array_equal(a["dat"], b["dat"])
    c = mo_phong_kho(inp, F, np.zeros(2), 1.64, 7, ke_hoach={0: [dict(t_dat=10, t_dau=20, t_cuoi=40, q=10.0, bo_sung=False)]})
    assert np.array_equal(a["dat"][1], c["dat"][1])                                          # ma B quy tac thuong giu nguyen


def test_lap_ke_hoach_khong_nhin_truoc_va_bo_qua_mua_khong_cham_duoc():
    idx = pd.date_range("2023-01-01", "2026-03-31")
    c = {"A": pd.Series(1.0, index=idx)}
    cap = pd.DataFrame({"ma": ["Z", "Z"], "cuoi": [pd.Timestamp("2024-12-25"), pd.Timestamp("2025-12-25")], "truoc": [10.0, 10.0], "nay": [10.0, 90.0]})
    inp = khung(n=400)
    inp["ds"] = [str(d.date()) for d in pd.date_range("2025-01-01", periods=400)]
    kh, bq = lap_ke_hoach(inp, LICH, cap, c, [None, None])
    assert list(kh) == [0] and len(kh[0]) == 1
    m = kh[0][0]
    assert m["t_dau"] == (pd.Timestamp("2025-12-04") - pd.Timestamp("2025-01-01")).days
    assert m["q"] == 22                                                                      # cap 2025 chua ket thuc luc dat: r chi co 1,0
    c2 = {"A": c["A"].copy()}
    c2["A"]["2025-12-01":] = 999                                                             # doi nhu cau sau ngay dat khong doi Q
    assert lap_ke_hoach(inp, LICH, cap, c2, [None, None])[0][0][0]["q"] == 22
    ngan = khung(n=30)
    ngan["ds"] = [str(d.date()) for d in pd.date_range("2025-12-02", periods=30)]    # ngay dat 01/12, dau ky 02/12
    kh2, bq2 = lap_ke_hoach(ngan, LICH, cap, c, [None, None])
    assert not kh2 and len(bq2) == 1                                                         # ngay dat truoc dau ky: giu quy tac thuong


def test_mua_dai_hon_han():
    kh = {0: [dict(t_dat=0, t_cuoi=30)], 1: [dict(t_dat=0, t_cuoi=10)], 2: [dict(t_dat=0, t_cuoi=99)]}
    assert mua_dai_hon_han(kh, [20, 20, None]) == {0}                 # ma 2 khong han: khong xet


def test_ton_sau_mua():
    inp = khung()
    ra = dict(ton=np.zeros((2, 60)))
    ra["ton"][0, 45] = 7
    assert ton_sau_mua(inp, ra, {0: [dict(t_cuoi=45)]}) == 70


def test_luat_chon():
    goc = dict(cp_tong=1000.0, fill_rate=96.0)
    pa = dict(a=dict(cp_tong=990.0, fill_rate=95.6), b=dict(cp_tong=980.0, fill_rate=95.7), c=dict(cp_tong=900.0, fill_rate=95.4), d=dict(cp_tong=998.0, fill_rate=96.0))
    assert chon_phuong_an(goc, pa) == "b"                                                    # c re nhat nhung giam qua 0,5 diem; d giam chua du
    assert chon_phuong_an(goc, dict(d=pa["d"])) is None
    assert chon_phuong_an(dict(cp_tong=1000.0, fill_rate=95.2), dict(e=dict(cp_tong=900.0, fill_rate=94.9))) is None    # duoi 95%


def test_khong_ke_hoach_trung_csdl():
    from csdl import doc
    from gom_don import chuan_bi
    inp, Ft, sig, z, buoc = chuan_bi("test")
    ra = mo_phong_kho(inp, Ft, sig, z, buoc, ke_hoach={})
    m = doc("SELECT ngay, ma_sku, dat_hang, ton_cuoi FROM mo_phong_ngay WHERE ma_chinh_sach = 'cong_thuc_du_bao_ai_hc'")
    for cot, ten in [("dat_hang", "dat"), ("ton_cuoi", "ton")]:
        b = m.pivot(index="ma_sku", columns="ngay", values=cot).reindex(index=inp["sku"].ma_sku, columns=inp["ds"]).values
        assert np.allclose(np.nan_to_num(b), ra[ten], atol=1e-6), cot
