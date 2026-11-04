"""Test tru hang phien livestream. Chay: python -m pytest tests/test_tru_hang_live.py"""
import os
import sys
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from tru_hang_live import (GiaDinh, bang_muc_dat, cac_phuong_an, chay_phien, chi_phi_thua, chi_tieu, do_phu, doc_he_so_that, duong_lai, he_so_gia, lai_don_vi, mau_theo_giam, lai_phien, muc_nen_gan_nhat,  # noqa: E402
                           nap_nhu_cau, nen_truot, phat_lai, q_newsvendor, sinh_nhu_cau, tai_tro_hoa_von, ti_le_toi_han, ti_so_deal)


def test_lai_don_vi_tinh_tay():
    gd = GiaDinh(giam_gia=0.2, tai_tro=0.5, phi_san=0.1)
    # gia sau giam 80, nhan hang bu 10, gia von 60, phi san 8
    assert lai_don_vi(100, 60, gd) == pytest.approx(80 + 10 - 60 - 8)
    assert lai_don_vi(100, 90, GiaDinh(giam_gia=0.3, tai_tro=0, phi_san=0)) < 0


def test_chi_phi_thua_ba_truong_hop():
    gd = GiaDinh(ngay_xa_kho=73, tra_ncc=0.1, xa_hang=0.4)
    assert chi_phi_thua(100, 0.2, "ve_kho", gd) == pytest.approx(100 * 0.2 * 73 / 365)
    assert chi_phi_thua(100, 0.2, "tra_ncc", gd) == pytest.approx(10)
    assert chi_phi_thua(100, 0.2, "xa_hang", gd) == pytest.approx(40)
    with pytest.raises(ValueError):
        chi_phi_thua(100, 0.2, "khac", gd)


def test_ti_le_toi_han_va_ban_lo_khong_tru():
    assert ti_le_toi_han(3, 1) == 0.75
    assert ti_le_toi_han(1, 0) == 1
    assert ti_le_toi_han(0, 5) == 0 and ti_le_toi_han(-2, 5) == 0
    assert q_newsvendor(np.arange(1, 101), -5, 1) == 0
    assert q_newsvendor(np.arange(1, 101), 3, 1) == np.ceil(np.quantile(np.arange(1, 101), 0.75))


def test_newsvendor_dung_la_cuc_dai_lai():
    """Doi chieu cong thuc voi do tim toan bo: lai tinh truc tiep cao nhat dung o phan vi toi han."""
    g = np.random.default_rng(1)
    D = g.lognormal(4, 0.8, 200_000)
    for cu, co in [(3, 1), (1, 3), (10, 1)]:
        ds_q = np.quantile(D, np.linspace(0.01, 0.99, 99))
        lai = [(np.minimum(D, q) * cu - np.maximum(q - D, 0) * co).mean() for q in ds_q]
        tot = np.linspace(0.01, 0.99, 99)[int(np.argmax(lai))]
        assert abs(tot - cu / (cu + co)) <= 0.02


def test_chay_phien_tinh_tay_khong_bo_sung():
    D = np.array([[2.0, 3.0, 4.0, 5.0]])
    r = chay_phien(D, 6)
    assert r["ban"][0] == 6 and r["thieu"][0] == 8 and r["thua"][0] == 0 and r["het"][0]
    r2 = chay_phien(D, 20)
    assert r2["ban"][0] == 14 and r2["thua"][0] == 6 and not r2["het"][0] and r2["q2"][0] == 0


def test_bo_sung_tinh_tay():
    """4 don/gio, 10 gio, tru 12, hang ve sau 2 gio. Het gio 3: da ban 12, het; toc do 4; ve dau gio thu 6 (chi so 5).
    Con 5 gio phuc vu (5..9): can 20. Dat 20, gio 3 va 4 mat ban 8."""
    D = np.full((1, 10), 4.0)
    r = chay_phien(D, 12, True, gio_ve=2, tran=1000)
    assert r["q2"][0] == 20 and r["ban"][0] == 32 and r["thieu"][0] == 8 and r["thua"][0] == 0


def test_bo_sung_khong_nhin_truoc():
    """Doi nhu cau SAU gio h khong duoc doi quyet dinh dat truoc gio h: so hang ve trong khoang truoc do phai nhu nhau."""
    g = np.random.default_rng(3)
    D = g.poisson(5, (200, 24)).astype(float)
    D2 = D.copy()
    D2[:, 12:] *= 10
    r, r2 = chay_phien(D, 30, True, gio_ve=2, tran=1e6), chay_phien(D2, 30, True, gio_ve=2, tran=1e6)
    assert np.array_equal(r["ban_gio"][:, :12], r2["ban_gio"][:, :12])
    # den het gio 12 ban nhu nhau, hang ve den gio 14 da dat tu truoc: gio 13 cua 2 ban chi khac do nhu cau, khong khac do nguon hang
    assert (r2["ban_gio"][:, 12] >= r["ban_gio"][:, 12]).all()


def test_het_hang_van_tiep_tuc_dat_bo_sung():
    """So ban = 0 khi het hang khong duoc lam he thong tuong nhu cau da het."""
    D = np.full((1, 24), 10.0)
    r = chay_phien(D, 30, True, gio_ve=4, tran=1e6)
    assert r["q2"][0] >= 10 * (24 - 3 - 4) * 0.9
    assert r["ban"][0] > 30


def test_tran_nguon_nhanh_va_gio_ve_qua_dai():
    D = np.full((1, 24), 10.0)
    assert chay_phien(D, 30, True, gio_ve=4, tran=50)["q2"][0] == 50
    r = chay_phien(D, 30, True, gio_ve=24, tran=1e6)
    assert r["q2"][0] == 0 and r["ban"][0] == chay_phien(D, 30)["ban"][0]


def test_q_mang_theo_phien():
    D = np.full((2, 4), 1.0)
    r = chay_phien(D, np.array([1.0, 10.0]))
    assert list(r["ban"]) == [1, 4] and list(r["thua"]) == [0, 6]


def test_lai_phien_tinh_tay():
    r = dict(ban=np.array([10.0]), thua=np.array([2.0]), q2=np.array([3.0]))
    assert lai_phien(r, 5, 1, 2)[0] == 10 * 5 - 2 * 1 - 3 * 2


def test_sinh_nhu_cau_dung_trung_binh_va_co_dinh_hat():
    gd = GiaDinh(p_xu_huong=0, huy_don=0.2, quy_mo=2)
    D = sinh_nhu_cau(100, [1.0, 1.0], gd, 5000, 1)
    assert D.shape == (5000, 24) and D.sum(axis=1).mean() == pytest.approx(100 * 2 * 0.8, rel=0.01)
    assert np.array_equal(D, sinh_nhu_cau(100, [1.0, 1.0], gd, 5000, 1))
    assert not np.array_equal(D, sinh_nhu_cau(100, [1.0, 1.0], gd, 5000, 2))


def test_len_xu_huong_tang_dung_he_so_va_dau_phien_chua_no():
    gd = GiaDinh(p_xu_huong=1, no_thap=4, no_cao=4, huy_don=0)
    D = sinh_nhu_cau(240, [1.0], gd, 4000, 2)
    assert D.sum(axis=1).mean() == pytest.approx(240 * 4, rel=0.01)
    assert D[:, :2].mean() == pytest.approx(10, rel=0.03)             # 2 gio dau luon chua no
    assert D[:, -1].mean() > 30


def test_du_lieu_vao_sai_bi_chan():
    with pytest.raises(ValueError):
        GiaDinh(so_gio=2)
    with pytest.raises(ValueError):
        GiaDinh(p_xu_huong=1.5)
    with pytest.raises(ValueError):
        GiaDinh(gio_ve=0)
    with pytest.raises(ValueError):
        GiaDinh(no_thap=5, no_cao=2)
    with pytest.raises(ValueError):
        sinh_nhu_cau(0, [1.0], GiaDinh(), 10, 1)
    with pytest.raises(ValueError):
        sinh_nhu_cau(10, [], GiaDinh(), 10, 1)
    with pytest.raises(ValueError):
        lai_don_vi(0, 10, GiaDinh())


def test_tinh_chat_cac_phuong_an():
    """Thua cang re, tru cang nhieu; hang ve cang nhanh, Q dau cang it; ban lo thi khong tru."""
    gd = GiaDinh()
    a = cac_phuong_an(100, [1.0, 1.5, 2.0], 125000, 99000, 0.2, "ve_kho", gd, 2000)
    b = cac_phuong_an(100, [1.0, 1.5, 2.0], 125000, 99000, 0.2, "xa_hang", gd, 2000)
    assert a["ti_le"] > b["ti_le"] and a["phuong_an"]["newsvendor"]["q"] > b["phuong_an"]["newsvendor"]["q"]
    pa = a["phuong_an"]
    assert pa["newsvendor"]["lai"] >= pa["trung_binh"]["lai"] and pa["newsvendor"]["lai"] >= pa["ngay_thuong"]["lai"]
    assert pa["hai_buoc"]["lai"] >= pa["newsvendor"]["lai"] * 0.98
    assert pa["hai_buoc_giu_q"]["q"] == pa["newsvendor"]["q"]
    lo = cac_phuong_an(100, [1.0, 2.0], 100, 99, 0.2, "ve_kho", GiaDinh(giam_gia=0.3, tai_tro=0), 500)
    assert lo["cu"] < 0 and lo["phuong_an"]["newsvendor"]["q"] == 0 and lo["phuong_an"]["hai_buoc"]["q2"] == 0


def test_mau_cham_doc_lap_voi_mau_thiet_ke_va_gd_thuc_chi_doi_nhu_cau():
    gd = GiaDinh()
    a = cac_phuong_an(100, [1.0, 2.0], 125000, 99000, 0.2, "ve_kho", gd, 1000)
    b = cac_phuong_an(100, [1.0, 2.0], 125000, 99000, 0.2, "ve_kho", gd, 1000, gd_thuc=replace(gd, p_xu_huong=0.5))
    assert a["cu"] == b["cu"] and a["phuong_an"]["newsvendor"]["q"] == b["phuong_an"]["newsvendor"]["q"]
    assert b["tb_nhu_cau"] > a["tb_nhu_cau"]


def test_muc_nen_khong_nhin_truoc_va_bo_ngay_khuyen_mai():
    ngay = pd.date_range("2025-01-01", periods=10)
    s = pd.Series([1.0, 2, 3, 100, 5, 6, 7, 8, 9, 1000], index=ngay)
    bo = pd.Series([False, False, False, True] + [False] * 6, index=ngay)
    n = nen_truot(s, bo, cua_so=5, toi_thieu=2)
    assert np.isnan(n.iloc[1])                                         # 1 ngay truoc do: chua du 2
    assert n.iloc[2] == 1.5
    assert n.iloc[4] == 2                                              # bo 100 cua ngay khuyen mai
    assert n.iloc[9] == np.median([5, 6, 7, 8, 9])                     # khong tinh 1000 cua chinh ngay do


def test_ti_so_deal_va_nen_gan_nhat():
    ngay = pd.date_range("2025-01-01", periods=40)
    bang = pd.DataFrame({"A": [10.0] * 40}, index=ngay)
    bang.iloc[35:37, 0] = 30
    km = pd.DataFrame({"A": [False] * 40}, index=ngay)
    km.iloc[35:37, 0] = True
    nghi = np.zeros(40, dtype=bool)
    su_kien = np.zeros(40, dtype=bool)
    r = ti_so_deal(bang, km, nghi, su_kien)
    assert len(r) == 2 and (r.ti_so == 3).all() and (r.nen == 10).all()
    su_kien2 = su_kien.copy()
    su_kien2[35] = True
    assert len(ti_so_deal(bang, km, nghi, su_kien2)) == 1
    assert len(ti_so_deal(bang, km, nghi, su_kien, tu="2025-02-06")) == 1
    assert len(ti_so_deal(bang, km, nghi, su_kien, den="2025-02-05")) == 1
    assert muc_nen_gan_nhat(bang, km, nghi).A == 10


def test_do_phu():
    kiem = pd.DataFrame({"nhu_cau": [1.0, 2, 3, 4], "nen": [1.0, 1, 1, 1]})
    assert do_phu(np.array([2.0, 2.0]), kiem, [0.5]) == {"0.5": 50.0}
    assert do_phu(np.array([1.0]), kiem.iloc[:0]) == {}


def test_bang_muc_dat_tinh_tay_va_chi_dung_mau_thiet_ke():
    """2 loai phien: cham 1 don/gio, nhanh 10 don/gio. Sau gio 3, hang ve sau 2 gio, phien 8 gio: con 3 gio phuc vu."""
    D = np.vstack([np.full((50, 8), 1.0), np.full((50, 8), 10.0)])
    b = bang_muc_dat(D, 2, 0.5, so_nhom=2)
    assert list(b) == [3, 4, 5]                                         # sau gio 5 hang ve khong kip
    bien, muc = b[3]
    assert muc[np.searchsorted(bien, 1.0, side="right")] == 3 and muc[np.searchsorted(bien, 10.0, side="right")] == 30


def test_quy_tac_2_dat_theo_bang_va_khong_nhin_truoc():
    D = np.full((1, 8), 10.0)
    # toc do 10 > bien 5 nen dung nhom 2. Muc can giam dan nhu bang that: 30, 20, 10 (cac gio con lai sau khi hang ve)
    bang_ = {3: (np.array([5.0]), np.array([0.0, 30.0])), 4: (np.array([5.0]), np.array([0.0, 20.0])), 5: (np.array([5.0]), np.array([0.0, 10.0]))}
    r = chay_phien(D, 30, True, gio_ve=2, tran=1000, bang_dat=bang_)
    # het gio 3 da het 30, dat 30 ve dau gio chi so 5; 2 gio sau hang sap ve da du muc can nen khong dat them. Gio 3, 4 mat ban 20
    assert r["q2"][0] == 30 and r["ban"][0] == 60 and r["thieu"][0] == 20 and r["thua"][0] == 0
    g = np.random.default_rng(5)
    tk = g.poisson(5, (2000, 24)).astype(float)
    bang_that = bang_muc_dat(tk, 3, 0.8)
    a = g.poisson(5, (100, 24)).astype(float)
    a2 = a.copy()
    a2[:, 10:] *= 20
    r1, r2 = chay_phien(a, 40, True, 3, 1e6, 0, bang_that), chay_phien(a2, 40, True, 3, 1e6, 0, bang_that)
    assert np.array_equal(r1["ban_gio"][:, :10], r2["ban_gio"][:, :10])


def test_quy_tac_2_khong_dat_khi_lai_sau_phu_phi_am():
    """Phu phi lon hon lai: phien giu nguyen nhu newsvendor, khong co don bo sung."""
    a = cac_phuong_an(100, [1.0, 2.0], 125000, 99000, 0.2, "ve_kho", GiaDinh(phu_phi_nhanh=0.5), 500)
    assert a["phuong_an"]["hai_buoc_2"]["q2"] == 0 and a["phuong_an"]["hai_buoc_2"]["lai"] == a["phuong_an"]["newsvendor"]["lai"]


def test_tran_bien_truoc_lon_hon_moi_phuong_an():
    a = cac_phuong_an(100, [1.0, 1.5, 2.0], 125000, 99000, 0.2, "ve_kho", GiaDinh(), 2000)
    assert a["lai_biet_truoc"] == pytest.approx(a["cu"] * a["tb_nhu_cau"])
    assert all(a["lai_biet_truoc"] >= v["lai"] for v in a["phuong_an"].values())
    lo = cac_phuong_an(100, [1.0, 2.0], 100, 99, 0.2, "ve_kho", GiaDinh(giam_gia=0.3, tai_tro=0), 500)
    assert lo["lai_biet_truoc"] == 0


def test_chi_tinh_mot_lan_khong_co_hai_buoc():
    a = cac_phuong_an(100, [1.0, 2.0], 125000, 99000, 0.2, "ve_kho", GiaDinh(), 500, hai_buoc=False)
    assert set(a["phuong_an"]) == {"ngay_thuong", "trung_binh", "newsvendor"}


def test_tai_tro_hoa_von_dung_bang_lai_khong():
    gd = GiaDinh(giam_gia=0.2, phi_san=0.1)
    f = tai_tro_hoa_von(100, 80, gd)
    assert f is not None and 0 < f < 1 and lai_don_vi(100, 80, replace(gd, tai_tro=f)) == pytest.approx(0)
    assert tai_tro_hoa_von(100, 50, gd) == 0                            # khong can tai tro van co lai
    assert tai_tro_hoa_von(100, 120, gd) is None                        # tai tro het van lo
    assert tai_tro_hoa_von(100, 120, GiaDinh(giam_gia=0)) is None


def test_duong_lai_cao_nhat_gan_newsvendor():
    gd = GiaDinh()
    d = duong_lai(200, [1.0, 1.5, 2.0], 7000, 1600, gd, n=4000, so_diem=200)
    assert d.q.iloc[0] == 0 and d.lai.iloc[0] == 0 and d.q.is_monotonic_increasing
    tong = sinh_nhu_cau(200, [1.0, 1.5, 2.0], gd, 4000, 20261104).sum(axis=1)
    assert d.q[d.lai.idxmax()] == pytest.approx(np.quantile(tong, 7000 / 8600), rel=0.08)


def test_duong_lai_gioi_han_truc():
    d = duong_lai(200, [1.0, 5.0], 7000, 1600, GiaDinh(), n=500, so_diem=30, q_max=123)
    assert len(d) == 30 and d.q.iloc[-1] == 123


def test_phat_lai_khop_tung_gio():
    gd = GiaDinh(gio_ve=2)
    a = phat_lai(100, [1.0], 40, 125000, 99000, 0.2, "ve_kho", gd, True, 7, n=500)
    assert len(a) == 24 and (a.ban <= a.nhu_cau).all() and (a.ban_cd.diff().fillna(a.ban_cd) == a.ban).all()
    assert (a.ban_cd <= a.hang_co).all() and a.hang_co.iloc[0] == 40
    for h in np.flatnonzero(a.dat.values > 0):                          # hang dat cuoi gio h co mat tu gio h + 3
        assert a.hang_co.iloc[h + 3] - a.hang_co.iloc[h + 2] >= a.dat.iloc[h]
    # cung hat, phien lien xu huong co tong nhu cau lon hon phien thuong
    b = phat_lai(100, [1.0], 40, 125000, 99000, 0.2, "ve_kho", gd, False, 7, n=500)
    assert a.nhu_cau.sum() > b.nhu_cau.sum()
    # phu phi lon hon lai: khong dat
    c = phat_lai(100, [1.0], 40, 125000, 99000, 0.2, "ve_kho", replace(gd, phu_phi_nhanh=0.5), True, 7, n=500)
    assert c.dat.sum() == 0 and (c.hang_co == 40).all()


def test_doc_truyen_vao_duoc_dung_thay_csdl():
    goi = []

    def doc(sql, params=()):
        goi.append(sql)
        if "nhu_cau_that" in sql:
            return pd.DataFrame({"ngay": ["2025-01-01", "2025-01-02"], "ma_sku": ["A", "A"], "nhu_cau": [1.0, 2.0]})
        return pd.DataFrame(columns=["ma_sku", "tu_ngay", "den_ngay", "ngay", "cua_so_truoc", "cua_so_sau"])
    bang, km, nghi, su_kien = nap_nhu_cau(doc)
    assert len(goi) == 4 and list(bang.A) == [1, 2] and not km.values.any() and not nghi.any() and not su_kien.any()


def test_co_gian_doi_nhu_cau_dung_cong_thuc_va_mac_dinh_khong_doi():
    assert he_so_gia(GiaDinh()) == 1 and he_so_gia(GiaDinh(giam_gia=0.3)) == 1          # co_gian = 0: giong muc 10.8
    gd = GiaDinh(giam_gia=0.3, co_gian=3.0, p_xu_huong=0)
    assert he_so_gia(gd) == pytest.approx((0.7 / 0.85) ** -3) and he_so_gia(GiaDinh(giam_gia=0.15, co_gian=3.0)) == 1
    a = sinh_nhu_cau(100, [1.0], GiaDinh(p_xu_huong=0), 4000, 1).sum(axis=1).mean()
    b = sinh_nhu_cau(100, [1.0], gd, 4000, 1).sum(axis=1).mean()
    assert b == pytest.approx(a * he_so_gia(gd), rel=0.01)
    with pytest.raises(ValueError):
        GiaDinh(co_gian=-1)


def test_chon_dai_theo_muc_giam():
    hs = dict(dai=[dict(tu=0.05, den=0.1, phan_vi=[1.0]), dict(tu=0.1, den=0.2, phan_vi=[2.0]), dict(tu=0.2, den=0.5, phan_vi=[3.0])])
    assert [mau_theo_giam(hs, g)[0] for g in (0.0, 0.05, 0.1, 0.15, 0.199, 0.2, 0.49, 0.5, 0.9)] == [1, 1, 2, 2, 2, 3, 3, 3, 3]


def test_doc_he_so_that(tmp_path):
    assert doc_he_so_that(tmp_path / "khong_co.json") is None
    f = tmp_path / "a.json"
    f.write_text('{"co_gian": 3, "dai": []}', encoding="utf-8")
    assert doc_he_so_that(f)["co_gian"] == 3


def test_chi_tieu_khop_tinh_tay():
    D = np.array([[1.0, 1.0], [5.0, 5.0]])
    r = chay_phien(D, 4)
    c = chi_tieu(r, D, 4, 10, 1, 0)
    assert c["lai"] == pytest.approx(((2 * 10 - 2) + (4 * 10)) / 2)
    assert c["p_het"] == 50 and c["thieu"] == 3 and c["thua"] == 1 and c["fill"] == pytest.approx(100 * 6 / 12)
