"""Test cham diem nha cung cap va canh bao giao cham. Chay: python -m pytest tests/test_cham_diem_ncc.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from cham_diem_ncc import bang_don, canh_bao, cham_diem, danh_gia_canh_bao, xep_lop  # noqa: E402


def don(ncc, tre, hen=3):
    return pd.DataFrame({"ma": "A", "ncc": ncc, "t": range(len(tre)), "hen": hen, "thuc": [hen + x for x in tre], "tre": tre, "ve": [t + hen + x for t, x in enumerate(tre)]})


def test_bang_don_tinh_tay():
    dat = np.array([[5, 0, 1], [0, 2, 0]])
    lt = np.array([[3, 9, 7], [9, 4, 9]])
    d = bang_don(dat, lt, ["A", "B"], ["N1", "N2"], [3.0, 4.4])
    assert d.to_dict("list") == {"ma": ["A", "A", "B"], "ncc": ["N1", "N1", "N2"], "t": [0, 2, 1], "hen": [3, 3, 4], "thuc": [3, 7, 4], "tre": [0, 4, 0], "ve": [3, 9, 5]}


def test_khong_co_don():
    d = bang_don(np.zeros((1, 3)), np.ones((1, 3)), ["A"], ["N"], [1.0])
    assert d.empty and cham_diem(d).empty and canh_bao(d) == {}


def test_diem_tinh_tay():
    b = cham_diem(don("N", [0, 0, 0, 0])).iloc[0]
    assert b.diem == pytest.approx(100) and b.dung_han_pt == 100 and b.xep_loai == "Tốt"
    b2 = cham_diem(don("N", [0, 0, 5, 5])).iloc[0]                     # lech chuan 2,5; dung han 50%
    assert b2.dung_han_pt == 50 and b2.diem == pytest.approx(100 * (0.6 * 0.5 + 0.4 * 0.5)) and b2.tre_max == 5 and b2.tre_tu_3_pt == 50


def test_tre_mot_ngay_van_dung_han_va_ve_som_khong_cong_tre():
    b = cham_diem(don("N", [1, -2, 1, -2])).iloc[0]
    assert b.dung_han_pt == 100 and b.tre_tb == 0.5


def test_xep_hang_tu_tot_den_kem():
    b = cham_diem(pd.concat([don("XAU", [6, 6, 0, 7]), don("TOT", [0, 0, 0, 0])]))
    assert list(b.ncc) == ["TOT", "XAU"] and b.diem.iloc[0] > b.diem.iloc[1]


def test_xep_lop_bien():
    assert [xep_lop(x) for x in (85, 84.9, 70, 69.9, 0)] == ["Tốt", "Trung bình", "Trung bình", "Cần theo dõi", "Cần theo dõi"]


def test_canh_bao_chi_dung_don_da_ve_va_du_so_don():
    assert canh_bao(don("N", [5] * 3), so_don=4, nguong=2) == {"N": []}           # chua du 4 don
    d = don("N", [0, 0, 0, 0, 5, 5, 5, 5, 5])
    r = canh_bao(d, so_don=4, nguong=2)["N"]
    # trung binh 4 don gan nhat >= 2 lan dau o don thu 6 (0, 0, 5, 5); ngay do la ngay don do VE, khong phai ngay dat
    assert r[0] == 5 + 3 + 5


def test_danh_gia_canh_bao():
    bao = {"N1": [12, 200], "N2": [50]}
    r = danh_gia_canh_bao(bao, {"N1": [(10, 20)], "N3": [(5, 6)]}, [(45, 55)], bien=5)
    assert r["so_dot"] == 2 and r["phat_hien"] == 1 and r["ngay_cho"] == [2]
    assert r["tong_ngay_canh_bao"] == 3 and r["bao_nham"] == 1                      # ngay 200 cua N1 khong thuoc cua so nao
