"""Test luat chon mo hinh va ghep du bao o vong kiem chung. Chay: python -m pytest tests/test_kiem_chung_nguon.py"""
import os
import sys

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from kiem_chung_nguon import ban_moi_nhat, chon_mo_hinh, do_trong_so, ghep, wmape  # noqa: E402


def khung(du_bao, y=(10.0, 10.0), xyz=("X", "Z")):
    return pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-01-02"]), "ma_sku": ["A", "B"], "moc": pd.Timestamp("2019-12-31"), "ngay_thu": [1, 2],
                         "y_cham": list(y), "abc_train": "A", "xyz_train": list(xyz), "loai_nhu_cau": "x", "du_bao": list(du_bao)})


def test_chon_thap_nhat_khi_chenh_ro():
    assert chon_mo_hinh({"tb_truot": 0.6, "lightgbm": 0.4, "ket_hop": 0.3}) == "ket_hop"


def test_chenh_duoi_nguong_lay_phuong_an_don_gian_hon():
    assert chon_mo_hinh({"lightgbm": 0.400, "lstm": 0.398, "ket_hop_dl": 0.396}) == "lightgbm"
    assert chon_mo_hinh({"lightgbm": 0.400, "ket_hop_dl": 0.394}) == "ket_hop_dl"


def test_ghep_theo_nhom():
    r = ghep(khung([0.0, 0.0]), khung([10.0, 10.0]), {"X": 1.0, "Z": 0.0}).sort_values("ma_sku")
    assert r.du_bao.tolist() == [0.0, 10.0]


def test_ghep_lech_dong_bi_chan():
    with pytest.raises(ValueError):
        ghep(khung([1.0, 1.0]).iloc[:1], khung([1.0, 1.0]), {"X": 1.0, "Z": 1.0})


def test_do_trong_so_chon_ben_dung():
    tot, xau = khung([10.0, 10.0]), khung([0.0, 0.0])
    assert do_trong_so(tot, xau) == {"X": 1.0, "Z": 1.0}
    assert do_trong_so(xau, tot) == {"X": 0.0, "Z": 0.0}


def test_ban_moi_nhat_va_wmape():
    p = pd.concat([khung([1.0, 1.0]).assign(ngay_thu=[8, 9]), khung([10.0, 5.0])])
    q = ban_moi_nhat(p)
    assert len(q) == 2 and sorted(q.du_bao) == [5.0, 10.0] and wmape(q) == pytest.approx(0.25)
    assert wmape(khung([10.0, 10.0], y=(10.0, None))) == 0
