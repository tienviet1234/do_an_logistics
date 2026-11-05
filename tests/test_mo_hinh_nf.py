"""Test phan khung du lieu va luat cua TiDE, N-HiTS, TFT. Khong can NeuralForecast. Chay: python -m pytest tests/test_mo_hinh_nf.py"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from mo_hinh_nf import BATCH, chon_batch, dat_luat, ghep, tao_khung  # noqa: E402


def khung(o=59, sua_y_sau_moc=None):
    skus, T = ["A", "B"], 100
    ngay = pd.date_range("2020-01-01", periods=T)
    y = np.arange(200, dtype=float).reshape(2, T)
    co = np.ones((2, T), dtype=bool)
    co[:, o + 1:] = False
    y[:, o + 1:] = 0 if sua_y_sau_moc is None else sua_y_sau_moc
    x = np.arange(2 * T * 3, dtype=np.float32).reshape(2, T, 3)
    return tao_khung(skus, ngay, o, y, co, x, np.array([2.0, 4.0]), ["x0", "x1", "x2"])


def test_bang_hoc_chi_den_moc():
    hoc, tl = khung(59)
    assert hoc.ds.max() == pd.Timestamp("2020-02-29") and len(hoc) == 2 * 60
    assert tl.ds.min() == pd.Timestamp("2020-03-01") and tl.ds.max() == pd.Timestamp("2020-03-28") and len(tl) == 2 * 28


def test_tuong_lai_khong_co_nhu_cau():
    _, tl = khung(59)
    assert "y" not in tl.columns and "available_mask" not in tl.columns


def test_doi_nhu_cau_sau_moc_khong_doi_dau_vao():
    a_h, a_t = khung(59, 0.0)
    b_h, b_t = khung(59, 1e6)
    pd.testing.assert_frame_equal(a_h, b_h)
    pd.testing.assert_frame_equal(a_t, b_t)


def test_co_nhu_cau_sau_moc_bi_chan():
    co = np.ones((1, 90), dtype=bool)
    with pytest.raises(ValueError):
        tao_khung(["A"], pd.date_range("2020-01-01", periods=90), 50, np.zeros((1, 90)), co, np.zeros((1, 90, 1), dtype=np.float32), np.array([1.0]), ["x0"])


def test_chuan_hoa_va_dung_ma():
    hoc, tl = khung(59)
    a, b = hoc[hoc.unique_id == "A"], hoc[hoc.unique_id == "B"]
    assert a.y.iloc[1] == pytest.approx(1 / 2) and b.y.iloc[0] == pytest.approx(100 / 4)
    assert a.x0.iloc[1] == 3 and tl[tl.unique_id == "B"].x0.iloc[0] == 3 * (100 + 60)


def test_batch_khong_doi_bo_du_lieu_nho():
    assert chon_batch(1095, 63) == BATCH


def test_batch_giam_khi_du_lieu_lon():
    b = chon_batch(1941, 82)
    assert 4 <= b < BATCH
    assert (1941 - 83) * 84 * 84 * 4 / 2 ** 30 * b <= 0.7


def test_batch_giam_khi_them_ngay_hoac_bien():
    assert chon_batch(4000, 82) <= chon_batch(1941, 82) and chon_batch(1941, 200) <= chon_batch(1941, 82)


def test_batch_co_san_va_tran():
    assert chon_batch(10 ** 6, 500) == 4 and chon_batch(100, 1) == BATCH


def test_luat():
    nen = dict(WMAPE=0.358, Bias=0.055)
    assert dat_luat(dict(WMAPE=0.35, Bias=0.06), nen)
    assert not dat_luat(dict(WMAPE=0.354, Bias=0.05), nen)            # giam chua du
    assert not dat_luat(dict(WMAPE=0.35, Bias=0.08), nen)             # lech tang qua 1 diem (truong hop ket_hop_v5)
    assert dat_luat(dict(WMAPE=0.35, Bias=-0.06), nen)


def test_ghep_lech_dong_bi_chan():
    f = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "ma_sku": ["A"], "moc": pd.Timestamp("2019-12-31"), "ngay_thu": [1], "y_cham": [1.0],
                      "abc_train": "A", "xyz_train": "X", "loai_nhu_cau": "x", "du_bao": [2.0]})
    assert ghep(f.assign(du_bao=4.0), f, {"X": 0.5}).du_bao.iloc[0] == 3.0
    with pytest.raises(ValueError):
        ghep(f.iloc[:0], f, {"X": 0.5})
