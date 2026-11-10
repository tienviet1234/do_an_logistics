"""Test ham thuan cua do nhay theo chi phi dat (khong can CSDL)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from do_nhay_chi_phi_dat import doi_s, eoq_ngay_ban, ket_luan, loi_ich  # noqa: E402


def test_doi_s_chi_doi_chi_phi_dat():
    sku = pd.DataFrame({"ma_sku": ["A", "B"], "chi_phi_dat_hang": [100.0, 200.0], "gia_von": [5.0, 6.0]})
    r = doi_s(sku, 0.25)
    assert list(r.chi_phi_dat_hang) == [25.0, 50.0] and list(r.gia_von) == [5.0, 6.0]
    assert list(sku.chi_phi_dat_hang) == [100.0, 200.0]
    with pytest.raises(ValueError):
        doi_s(sku, 0)


def test_eoq_ngay_ban_tinh_tay():
    # D = 10/ngay, S = 365, H = 2 -> EOQ = sqrt(2 * 3650 * 365 / 2) = 1150,2 don vi = 115,02 ngay
    assert eoq_ngay_ban(10, 365, 2) == pytest.approx(np.sqrt(2 * 3650 * 365 / 2) / 10)
    assert np.isnan(eoq_ngay_ban(0, 365, 2))
    a = eoq_ngay_ban([10, 10], [100, 25], [2, 2])
    assert a[1] == pytest.approx(a[0] / 2)        # S giam 4 lan -> EOQ giam 2 lan


def test_loi_ich():
    assert loi_ich(200, 150) == pytest.approx(25.0)
    assert loi_ich(100, 110) == pytest.approx(-10.0)
    with pytest.raises(ValueError):
        loi_ich(0, 1)


def test_ket_luan_theo_nguong():
    assert ket_luan({0.1: 12.0, 1.0: 2.0})["phu_thuoc"]
    assert not ket_luan({0.1: 6.0, 1.0: 2.0})["phu_thuoc"]
    assert ket_luan({0.1: 7.0, 1.0: 2.0})["chenh_diem"] == pytest.approx(5.0) and ket_luan({0.1: 7.0, 1.0: 2.0})["phu_thuoc"]
    with pytest.raises(ValueError):
        ket_luan({1.0: 2.0})
