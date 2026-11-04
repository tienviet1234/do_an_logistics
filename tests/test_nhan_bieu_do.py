"""Test dat nhan bieu do diem. Chay: python -m pytest tests/test_nhan_bieu_do.py"""
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from nhan_bieu_do import do_de_nhan, vi_tri_nhan  # noqa: E402

TEN = ["Hiện trạng*", "AI", "AI + hiệu chỉnh", "Dự báo mốc"]


def test_ca_gap_that_nhom_y_het_de():
    """Nhom Y: xen ke theo thu tu ton lam nhan AI de len Hien trang (da gap khi chup that)."""
    x, y = [475, 490, 515, 680], [97.95, 98.45, 97.6, 96.85]
    phai, le = vi_tri_nhan(x, y, TEN)
    assert do_de_nhan(x, y, TEN, le, phai) == 0
    assert do_de_nhan(x, y, TEN, [0, 1, 0, 1], phai) > 0              # cach cu de nhau that
    assert phai == [False, False, False, True]


def test_ca_gap_that_nhom_x_het_de_va_khong_cat_mep_phai():
    x, y = [3550, 3620, 4150, 5230], [95.55, 95.55, 95.55, 93.8]
    ten = ["AI", "AI + hiệu chỉnh", "Dự báo mốc", "Hiện trạng*"]
    phai, le = vi_tri_nhan(x, y, ten)
    assert do_de_nhan(x, y, ten, le, phai) == 0 and phai[-1] is True


def test_truong_hop_bien():
    assert vi_tri_nhan([], [], []) == ([], [])
    assert vi_tri_nhan([5], [5], ["A"]) == ([False], [0])            # 1 diem: khong chia cho 0
    p, le = vi_tri_nhan([5, 5], [5, 5], ["A", "B"])                   # trung nhau hoan toan: 2 nhan khac phia
    assert sorted(le) == [0, 1]
    with pytest.raises(ValueError):
        vi_tri_nhan([1], [1, 2], ["A"])
