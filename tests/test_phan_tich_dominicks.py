"""Test doi chieu Dominick's. Chay: python -m pytest tests/test_phan_tich_dominicks.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from phan_tich_dominicks import (DAI_GIAM, TUAN_SU_KIEN, ben_trong, bien_lai, chia_dai, chi_so_ma, he_so_gon, phu_theo_dai, thu_sau_doi_chieu, dat_phu, gop_khoi, gop_nganh, loc_du_mau, mau_deal, muc_tai_tro, phu_theo_thoi_gian,  # noqa: E402
                                 quy_mo_theo_gia, sau_khuyen_mai, tach_thoi_gian, theo_do_sau, tom_tat_he_so)


def tuan(gia, so, co=None, von=None, n_ch=100, so_ch=50, dau=1000):
    """Bang 1 ma theo tuan, bat dau tu tuan khong phai tuan le. gia, so: danh sach theo tuan."""
    n = len(gia)
    gia, so = np.array(gia, dtype=float), np.array(so, dtype=float)
    von = np.array(von, dtype=float) if von is not None else gia * 0.7
    return pd.DataFrame({"WEEK": range(dau, dau + n), "move": so, "doanh_thu": gia * so, "gia_von": von * so, "so_cua_hang": so_ch,
                         "so_co": np.array(co if co is not None else [0] * n) * so_ch, "n_ch": n_ch})


def test_gop_khoi_tinh_tay_bo_dong_xau_va_don_gia_theo_goi():
    d = pd.DataFrame({"STORE": [1, 2, 3, 4, 5, 6], "UPC": [9] * 6, "WEEK": [1] * 6, "MOVE": [6, 4, 3, 0, 5, 5], "QTY": [3, 1, 1, 1, 1, 1],
                      "PRICE": [6.0, 3.0, 3.0, 0.0, 3.0, 3.0], "SALE": ["B", None, None, None, None, None], "PROFIT": [25.0, 50.0, 50.0, 0.0, 50.0, 95.0], "OK": [1, 1, 0, 1, 1, 1]})
    a, ch = gop_khoi(d)
    r = a.iloc[0]
    # dong 3 OK = 0, dong 4 gia = 0, dong 6 lai 95% bi bo. Don gia dong 1 = 6/3 = 2 (tai lieu: Sales = Price * Move / Qty)
    assert r.move == 6 + 4 + 5 and r.doanh_thu == pytest.approx(2 * 6 + 3 * 4 + 3 * 5)
    assert r.gia_von == pytest.approx(12 * 0.75 + 12 * 0.5 + 15 * 0.5) and r.so_cua_hang == 3 and r.so_co == 1
    assert sorted(ch.STORE) == [1, 2, 5]


def test_gop_nganh_dem_cua_hang_cua_ca_nganh():
    a1 = pd.DataFrame({"UPC": [1], "WEEK": [5], "move": [2], "doanh_thu": [4.0], "gia_von": [2.0], "so_cua_hang": [1], "so_co": [0]})
    a2 = pd.DataFrame({"UPC": [1, 2], "WEEK": [5, 5], "move": [3, 1], "doanh_thu": [6.0, 1.0], "gia_von": [3.0, 1.0], "so_cua_hang": [1, 1], "so_co": [1, 0]})
    g = gop_nganh([a1, a2], [pd.DataFrame({"WEEK": [5], "STORE": [10]}), pd.DataFrame({"WEEK": [5, 5], "STORE": [10, 11]})])
    assert g[g.UPC == 1].move.iloc[0] == 5 and (g.n_ch == 2).all()


def test_nhan_khuyen_mai_bang_co_hoac_bang_gia():
    co = [0] * 8 + [1] + [0] * 3
    gia = [2.0] * 8 + [2.0, 2.0, 1.8, 2.0]                       # tuan chi so 8: co co, gia khong doi; chi so 10: khong co, gia giam 10%
    r = chi_so_ma(tuan(gia, [100] * 12, co))
    assert list(r.km) == [False] * 8 + [True, False, True, False] and r.co[8] and not r.co[10]


def test_muc_nen_khong_nhin_truoc_va_bo_tuan_khuyen_mai():
    gia = [2.0] * 5 + [1.0] + [2.0] * 3
    so = [100.0, 100, 110, 110, 120, 999, 100, 100, 5000]
    r = chi_so_ma(tuan(gia, so))
    assert np.isnan(r.nen[2])                                      # moi 2 tuan truoc do: chua du 3
    assert r.nen[3] == pytest.approx(np.median([100, 100, 110]) / 100)
    assert r.nen[6] == pytest.approx(np.median([100, 100, 110, 110, 120]) / 100)   # bo 999 cua tuan khuyen mai
    assert r.nen[8] == pytest.approx(np.median([100, 100, 110, 110, 120, 100, 100]) / 100)   # khong tinh 5000 cua chinh tuan do


def test_tuan_khong_ban_khong_duoc_tinh_la_tuan_thuong_va_duoc_bo():
    g = tuan([2.0] * 6, [100.0] * 6).drop(index=[3])
    r = chi_so_ma(g)
    assert len(r) == 5 and 1003 not in set(r.WEEK)


def test_he_so_deal_va_muc_giam_tinh_tay():
    gia = [2.0] * 9 + [1.5]
    r = chi_so_ma(tuan(gia, [100.0] * 9 + [300.0])).assign(nganh="a", UPC=1)
    x = mau_deal(r)
    assert len(x) == 1 and x.ti_so.iloc[0] == pytest.approx(3) and x.giam.iloc[0] == pytest.approx(0.25)


def test_loc_mau_nho_va_tuan_le():
    r = chi_so_ma(tuan([2.0] * 9 + [1.5], [5.0] * 10)).assign(nganh="a", UPC=1)
    assert len(mau_deal(r)) == 0                                   # nen 5/tuan < 20
    r2 = chi_so_ma(tuan([2.0] * 9 + [1.5], [100.0] * 10, so_ch=5)).assign(nganh="a", UPC=1)
    assert len(mau_deal(r2)) == 0                                  # it cua hang
    assert len(TUAN_SU_KIEN) == 62
    r3 = chi_so_ma(tuan([2.0] * 9 + [1.5], [100.0] * 9 + [300.0], dau=330 - 9)).assign(nganh="a", UPC=1)
    assert r3.WEEK.iloc[-1] == 330 and len(mau_deal(r3)) == 1      # tuan 330 khong phai tuan le
    r4 = chi_so_ma(tuan([2.0] * 9 + [1.5], [100.0] * 9 + [300.0], dau=329 - 9)).assign(nganh="a", UPC=1)
    assert r4.WEEK.iloc[-1] == 329 and len(mau_deal(r4)) == 0      # tuan 329 la New-Year
    assert len(loc_du_mau(r4)) >= 1


def test_chuan_hoa_theo_so_cua_hang_ca_nganh():
    g = tuan([2.0] * 9 + [1.5], [100.0] * 9 + [200.0], n_ch=100)
    g.loc[g.index[-1], "n_ch"] = 200                               # so cua hang tang gap doi: ban gap doi khong phai la tang nhu cau
    x = mau_deal(chi_so_ma(g).assign(nganh="a", UPC=1))
    assert x.ti_so.iloc[0] == pytest.approx(1)


def test_tai_tro_tinh_tay():
    gia = [2.0] * 9 + [1.5]
    von = [1.4] * 9 + [1.0]
    r = chi_so_ma(tuan(gia, [100.0] * 10, von=von)).assign(nganh="a", UPC=1)
    assert muc_tai_tro(r)[0] == pytest.approx((1.4 - 1.0) / (2.0 - 1.5)) and muc_tai_tro(r)[1] == 1
    khong = chi_so_ma(tuan([2.0] * 10, [100.0] * 10)).assign(nganh="a", UPC=1)
    assert muc_tai_tro(khong) is None


def test_bien_lai_tinh_tay():
    gia = [2.0] * 9 + [1.5]
    von = [1.4] * 9 + [1.2]
    b = bien_lai(chi_so_ma(tuan(gia, [100.0] * 10, von=von)).assign(nganh="a", UPC=1))
    assert b["thuong"] == pytest.approx(0.3) and b["km"] == pytest.approx(0.2) and b["ti_le_tuan_km"] == 10 and b["co_trong_km"] == 0


def test_do_co_gian_tinh_tay():
    giam = np.array([0.07, 0.15, 0.25, 0.4])
    x = pd.DataFrame({"giam": giam, "ti_so": (1 - giam) ** -2.5})
    d = theo_do_sau(x)
    assert d["co_gian"] == pytest.approx(2.5) and d["dai"][0]["n"] == 1 and d["dai"][1]["n"] == 1 and d["dai"][1]["p50"] == pytest.approx(0.85 ** -2.5)
    assert d["dai"][4]["n"] == 0 and np.isnan(d["dai"][4]["p50"])


def test_sau_khuyen_mai_tinh_tay():
    gia = [2.0] * 9 + [1.5] + [2.0]
    so = [100.0] * 9 + [300.0] + [60.0]
    b = chi_so_ma(tuan(gia, so)).assign(nganh="a", UPC=1)
    s = sau_khuyen_mai(b)
    assert s["n"] == 1 and s["p50"] == pytest.approx(0.6)


def test_tach_thoi_gian_theo_tung_nganh():
    x = pd.DataFrame({"nganh": ["a", "a", "b", "b"], "WEEK": [10, 80, 100, 390], "ti_so": [1.0, 2, 3, 4]})
    d, s = tach_thoi_gian(x, {"a": (1, 100), "b": (1, 400)})
    assert list(d.WEEK) == [10, 100] and list(s.WEEK) == [80, 390]


def test_phu_va_dat_phu():
    g = np.random.default_rng(1)
    x = pd.DataFrame({"nganh": "a", "WEEK": g.integers(1, 301, 20000), "ti_so": g.lognormal(0, 0.5, 20000)})
    p = phu_theo_thoi_gian(x, {"a": (1, 300)})
    assert dat_phu(p["gop"]) and p["so_dau"] + p["so_sau"] == 20000 and "a" in p["theo_nganh"]
    assert not dat_phu({"0.5": 44.0, "0.75": 75.0, "0.9": 90.0})
    y = x.assign(ti_so=np.where(x.WEEK > 200, x.ti_so * 3, x.ti_so))    # thoi ky sau tang gap 3: phep kiem phai bao khong dat
    assert not dat_phu(phu_theo_thoi_gian(y, {"a": (1, 300)})["gop"])


def test_tom_tat_he_so():
    t = tom_tat_he_so([1.0] * 8 + [3.0, 10.0])
    assert t["n"] == 10 and t["tu_3"] == 20 and t["tu_5"] == 10 and t["tu_10"] == 10 and t["p50"] == 1


def test_ben_trong_bao_dung_truong_hop_thua():
    tot = {"newsvendor": {"lai": 5}, "ngay_thuong": {"lai": 4}, "trung_binh": {"lai": 3}}
    kem = {"newsvendor": {"lai": 2}, "ngay_thuong": {"lai": 4}, "trung_binh": {"lai": 3}}
    r = ben_trong({"h": {"0.2": {"mo_phong": tot, "that": kem}}})
    assert r == {"h": ["p = 0.2, Q theo that"]}


def _mau_dai(n=4000):
    g = np.random.default_rng(2)
    giam = g.uniform(0.05, 0.9, n)
    return pd.DataFrame({"nganh": "a", "WEEK": g.integers(1, 301, n), "giam": giam, "ti_so": (1 - giam) ** -3 * g.lognormal(0, 0.3, n)})


def test_chia_dai_khong_trung_khong_sot():
    x = _mau_dai()
    d = chia_dai(x)
    assert list(d) == DAI_GIAM and sum(len(v) for v in d.values()) == len(x)


def test_he_so_gon_tinh_dung_va_tang_theo_do_sau():
    x = _mau_dai()
    h = he_so_gon(x, 3.0, 0.43, so_diem=100)
    assert h["co_gian"] == 3 and h["tai_tro"] == 0.43 and [(d["tu"], d["den"]) for d in h["dai"]] == DAI_GIAM
    assert all(len(d["phan_vi"]) == 100 and d["phan_vi"] == sorted(d["phan_vi"]) for d in h["dai"])
    p50 = [d["p50"] for d in h["dai"]]
    assert p50 == sorted(p50)
    d0 = h["dai"][0]
    assert d0["n"] == ((x.giam >= 0.05) & (x.giam < 0.1)).sum() and np.median(d0["phan_vi"]) == pytest.approx(d0["p50"], rel=0.02)


def test_phu_theo_dai_bat_duoc_lech_o_dung_dai():
    x = _mau_dai(40000)
    lech = (x.WEEK > 200) & (x.giam >= 0.1) & (x.giam < 0.2)
    x.loc[lech, "ti_so"] *= 3
    p = phu_theo_dai(x, {"a": (1, 300)})
    assert p["0.05-0.1"]["dat"] and not p["0.1-0.2"]["dat"] and p["0.05-0.1"]["so_nganh"] == 1


def test_thu_sau_doi_chieu_cham_dung_va_bao_thua():
    ds = pd.DataFrame({"ma_sku": ["A"], "gia_ban": [125000.0], "gia_von": [80000.0], "ty_le_chi_phi_luu_kho": [0.2]})
    x = _mau_dai()
    dau, sau = x[x.WEEK <= 200], x[x.WEEK > 200]
    bang, thua = thu_sau_doi_chieu(ds, pd.Series({"A": 100.0}), dau, sau, 0.45)
    assert len(bang) == 3 * 3 * 2 and {r["giam"] for r in bang} == {0.1, 0.15, 0.3} and all(r["so_ma_lai"] == 1 for r in bang)
    assert isinstance(thua, list)


def test_quy_mo_theo_gia():
    assert quy_mo_theo_gia(0.15, 3) == 1 and quy_mo_theo_gia(0.3, 0) == 1
    assert quy_mo_theo_gia(0.3, 2) == pytest.approx((0.7 / 0.85) ** -2) and quy_mo_theo_gia(0.3, 2) > 1 > quy_mo_theo_gia(0.1, 2)


def test_cham_bang_he_so_khac_voi_he_so_tinh_q():
    from tru_hang_live import GiaDinh, cac_phuong_an
    a = cac_phuong_an(100, [1.0], 125000, 99000, 0.2, "ve_kho", GiaDinh(), 500, hai_buoc=False)
    b = cac_phuong_an(100, [1.0], 125000, 99000, 0.2, "ve_kho", GiaDinh(), 500, hai_buoc=False, he_so_deal_thuc=[3.0])
    assert a["phuong_an"]["newsvendor"]["q"] == b["phuong_an"]["newsvendor"]["q"]      # Q chi theo he so de tinh
    assert b["tb_nhu_cau"] == pytest.approx(3 * a["tb_nhu_cau"], rel=0.05)
