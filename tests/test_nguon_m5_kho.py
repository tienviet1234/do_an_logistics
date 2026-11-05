"""Test bo du lieu kho dung tu M5. Chay: python -m pytest tests/test_nguon_m5_kho.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src", "nguon"))
from m5_kho import CHI_PHI_DAT, NGUON, TI_GIA, bien_lai_nhom, cac_dot_lien_tiep, danh_muc, giao_dich, lich_khuyen_mai, ton_theo_quy_tac, tuan_khuyen_mai  # noqa: E402


def test_quy_tac_kinh_nghiem_tinh_tay():
    D = [10.0] * 22
    nhap, xuat, ton = ton_theo_quy_tac(D, np.zeros(22, dtype=bool))
    # t = 0: chua co lich su nen khong dat, chua co hang. t = 7: TB 10, dat 21 x 10 = 210, ve t = 14
    assert xuat[:14].sum() == 0 and nhap[14] == 210 and xuat[14] == 10 and ton[14] == 200
    # t = 14: con 200, muc 210: dat them 10, ve t = 21
    assert nhap[21] == 10 and ton[20] == 140 and ton[21] == 140


def test_khong_nhin_truoc():
    D = np.full(40, 5.0)
    D2 = D.copy()
    D2[20:] = 500
    a, b = ton_theo_quy_tac(D, np.zeros(40, dtype=bool)), ton_theo_quy_tac(D2, np.zeros(40, dtype=bool))
    assert np.array_equal(a[0][:21], b[0][:21])                       # hang ve toi ngay 20 khong doi khi nhu cau tu ngay 20 doi


def test_bao_toan_hang_ngay_nghi_va_khong_am():
    g = np.random.default_rng(1)
    D = g.poisson(4, 200).astype(float)
    dong = np.arange(200) % 30 == 29
    nhap, xuat, ton = ton_theo_quy_tac(D, dong)
    assert np.allclose(nhap.cumsum() - xuat.cumsum(), ton) and (ton >= 0).all() and (xuat <= D + 1e-9).all()
    assert (nhap[dong] == 0).all() and (xuat[dong] == 0).all()
    with pytest.raises(ValueError):
        ton_theo_quy_tac([1.0], [False, False])


def test_truoc_len_ke_khong_dat():
    D = np.r_[np.zeros(30), np.full(30, 3.0)]
    nhap, _, _ = ton_theo_quy_tac(D, np.zeros(60, dtype=bool))
    assert nhap[:30].sum() == 0 and nhap.sum() > 0


def test_khuyen_mai_tu_gia():
    g = pd.Series([2.0, 2.0, 2.0, 2.0, 1.9, 1.5, 2.0, 2.0])
    assert list(tuan_khuyen_mai(g)) == [False, False, False, False, True, True, False, False]   # 1,9 = 95% van tinh
    assert not tuan_khuyen_mai(pd.Series([1.0, 0.5])).any()            # chua du 3 tuan truoc


def test_gop_dot_lien_tiep():
    d = cac_dot_lien_tiep(pd.to_datetime(["2015-01-03", "2015-01-10", "2015-02-07"]))
    assert d[0] == (pd.Timestamp("2015-01-03"), pd.Timestamp("2015-01-16"), 14) and d[1][2] == 7 and len(d) == 2


def test_lich_khuyen_mai_cat_o_cuoi_du_lieu():
    ngay = pd.date_range("2015-01-03", periods=6, freq="7D")
    t = pd.DataFrame({"ma_sku": "A", "ngay_dau_tuan": ngay, "gia": [2.0, 2.0, 2.0, 2.0, 2.0, 1.0]})
    k = lich_khuyen_mai(t, ngay[-1] + pd.Timedelta(days=2))
    assert len(k) == 1 and k.so_ngay[0] == 3 and k.tu_ngay[0] == "2015-02-07" and k.den_ngay[0] == "2015-02-09"
    assert lich_khuyen_mai(t.assign(gia=2.0), ngay[-1]).empty and list(lich_khuyen_mai(t.assign(gia=2.0), ngay[-1]).columns) == ["ma_sku", "tu_ngay", "den_ngay", "so_ngay"]


def test_bien_lai_tinh_tay_va_nhom_khac():
    g = pd.DataFrame({"nganh": ["cer", "lnd", "sha"], "doanh_thu": [100.0, 100.0, 200.0], "gia_von": [70.0, 80.0, 100.0]})
    b = bien_lai_nhom(g)
    assert b["FOODS"] == pytest.approx(0.3) and b["HOUSEHOLD"] == pytest.approx(0.2) and b["KHAC"] == pytest.approx(1 - 250 / 400)


def khung_sku():
    return pd.DataFrame({"ma_sku": ["FOODS_1_001", "HOBBIES_1_001"], "ten_sku": ["FOODS_1_001", "HOBBIES_1_001"], "nhom_hang": ["FOODS_1", "HOBBIES_1"], "loai_mua_vu": ["FOODS", "HOBBIES"], "gia_ban": [0.0, 0.0], "gia_von": [0.0, 0.0], "chi_phi_dat_hang": 20.0, "nha_cung_cap": "GIA_DINH"})


def test_danh_muc_quy_doi_va_khong_doi_ten():
    pl = pd.DataFrame({"ma_sku": ["FOODS_1_001", "HOBBIES_1_001"], "abc_train": ["A", "C"], "xyz_train": ["X", "Z"]})
    d = danh_muc(khung_sku(), pd.Series({"FOODS_1_001": 2.0, "HOBBIES_1_001": 4.0}), {"FOODS": 0.3, "KHAC": 0.25}, pl)
    assert d.gia_ban.tolist() == [2 * TI_GIA, 4 * TI_GIA] and d.gia_von.tolist() == [2 * TI_GIA * 0.7, 4 * TI_GIA * 0.75]
    assert d.ten_sku.tolist() == d.ma_sku.tolist()                     # ma an danh cua M5: khong dat ten hang gia
    assert d.nha_cung_cap.tolist() == ["NCC_FOODS_1", "NCC_HOBBIES_1"] and (d.chi_phi_dat_hang == CHI_PHI_DAT).all() and d.phan_loai_XYZ.tolist() == ["X", "Z"]
    with pytest.raises(ValueError):
        danh_muc(khung_sku(), pd.Series({"FOODS_1_001": 2.0}), {"FOODS": 0.3, "KHAC": 0.25}, pl)


def test_giao_dich_giu_nguyen_so_ban_that():
    n = 40
    g = pd.DataFrame({"date": pd.date_range("2015-01-01", periods=n).strftime("%Y-%m-%d"), "ma_sku": "A", "qty_in": 0.0, "qty_out": np.full(n, 3.0), "ton_cuoi_ngay": 0, "la_ngay_nghi": 0, "het_hang": 0, "co_sua": 0, "truoc_len_ke": 0})
    sach, nct = giao_dich(g)
    assert (nct.nhu_cau_that.values == g.qty_out.values).all()         # so ban that vao nhu cau, khong doi
    assert "truoc_len_ke" not in sach.columns and (sach.qty_out <= 3).all() and sach.het_hang.iloc[0] == 1 and np.allclose(sach.qty_in.cumsum() - sach.qty_out.cumsum(), sach.ton_cuoi_ngay)


def test_mo_ta_ai_dung_mo_hinh_chon():
    assert NGUON["mo_hinh_chon"] == "ket_hop_dl" and "RNN" in NGUON["mo_ta_ai"]


def test_nguon_luon_ghi_ro_khong_mao_nhan():
    assert NGUON["la_mo_phong"] is False and "M5" in NGUON["ghi_chu"] and "Walmart" in NGUON["ghi_chu"] and "giả định" in NGUON["ghi_chu"]
    assert "không phải số của một kho Việt Nam" in NGUON["mo_ta"] and "Dominick" in NGUON["that"]
