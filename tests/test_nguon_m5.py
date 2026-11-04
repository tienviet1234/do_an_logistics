"""Test bo chuyen doi M5. So ban phai giu nguyen; chon mau khong phu thuoc so ban; ngay len ke khong bi lo qua thong tin biet truoc."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "nguon"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from kiem_tra_du_lieu import kiem_tra_giao_dich  # noqa: E402
from m5 import bang_giao_dich, chon_mau, danh_muc_ma, lich_su_kien, ngay_dong_cua  # noqa: E402


def dm(n_a=70, n_b=30):
    return pd.DataFrame({"item_id": [f"A_{i}" for i in range(n_a)] + [f"B_{i}" for i in range(n_b)], "dept_id": ["A"] * n_a + ["B"] * n_b, "cat_id": "C"})


def test_chon_mau_dung_ti_le_on_dinh_khong_trung():
    a, b = chon_mau(dm(), 10), chon_mau(dm().sample(frac=1, random_state=2), 10)
    assert a == b and len(set(a)) == 10                       # thu tu dau vao khong doi ket qua
    assert sum(x.startswith("A") for x in a) == 7 and sum(x.startswith("B") for x in a) == 3
    assert chon_mau(dm(), 10, hat_giong=1) != a
    assert len(chon_mau(dm(), 500)) == 100


def test_chia_phan_du():
    assert len(chon_mau(dm(1, 3), 3)) == 3 and len(chon_mau(pd.DataFrame({"item_id": list("abcdefg"), "dept_id": list("xxxyyzz")}), 5)) == 5


def test_ngay_dong_cua():
    s = pd.Series([100.0] * 9 + [5.0], index=pd.date_range("2020-12-16", periods=10))
    assert list(ngay_dong_cua(s)) == [pd.Timestamp("2020-12-25")]


def bang_ban():
    i = pd.date_range("2020-01-01", periods=5)
    return pd.DataFrame({"M1": [1, 0, 2, 0, 3], "M2": [0, 0, 4, 5, 0]}, index=i)


def test_so_ban_giu_nguyen():
    g = bang_giao_dich(bang_ban(), [])
    assert g.pivot(index="date", columns="ma_sku", values="qty_out").equals(bang_ban().astype(float).rename_axis("date").rename_axis("ma_sku", axis=1))


def test_truoc_len_ke_khong_cham_nhung_khong_lo_qua_ngay_nghi():
    g = bang_giao_dich(bang_ban(), []).set_index(["date", "ma_sku"])
    assert g.loc[(pd.Timestamp("2020-01-02"), "M2"), "het_hang"] == 1        # chua len ke: khong tinh la nhu cau
    assert g.loc[(pd.Timestamp("2020-01-02"), "M1"), "het_hang"] == 0        # da len ke, ban 0 la nhu cau that
    assert g.loc[(pd.Timestamp("2020-01-05"), "M2"), "het_hang"] == 0
    assert (g.la_ngay_nghi == 0).all()                                      # ngay nghi la thong tin biet truoc: khong duoc dung cho ngay len ke
    assert g.loc[(pd.Timestamp("2020-01-02"), "M2"), "truoc_len_ke"] == 1 and g.loc[(pd.Timestamp("2020-01-02"), "M1"), "truoc_len_ke"] == 0


def test_ngay_dong_cua_ap_cho_moi_ma():
    g = bang_giao_dich(bang_ban(), [pd.Timestamp("2020-01-03")])
    assert g[g.la_ngay_nghi == 1].date.nunique() == 1 and (g.la_ngay_nghi == 1).sum() == 2


@pytest.mark.parametrize("sai", [pd.DataFrame({"M": [-1, 1]}), pd.DataFrame({"M": [0, 0], "N": [1, 1]})])
def test_du_lieu_sai_bi_chan(sai):
    with pytest.raises(ValueError):
        bang_giao_dich(sai.set_axis(pd.date_range("2020-01-01", periods=2)), [])


def test_lich_su_kien_va_snap():
    cal = pd.DataFrame({"date": pd.date_range("2020-12-25", periods=2), "event_name_1": ["Christmas", np.nan], "event_type_1": ["National", np.nan],
                        "event_name_2": [np.nan, "Mother's day"], "event_type_2": [np.nan, "Cultural"], "snap_CA": [1, 0], "snap_TX": [0, 0], "snap_WI": [0, 1]})
    k = lich_su_kien(cal)
    assert set(k.holiday) == {"noel", "phu_nu_vn", "snap_ca", "snap_wi"}
    assert k[k.holiday == "snap_ca"].lower_window.iloc[0] == 0 and k[k.holiday == "noel"].lower_window.iloc[0] == -3


def test_danh_muc_thieu_gia_bi_chan_va_gia_von_la_gia_dinh():
    d = dm(1, 1)
    with pytest.raises(ValueError):
        danh_muc_ma(d, pd.Series({"A_0": 4.0}))
    r = danh_muc_ma(d, pd.Series({"A_0": 4.0, "B_0": 2.0}))
    assert r.gia_von.tolist() == [3.0, 1.5] and (r.nha_cung_cap == "GIA_DINH").all()


def test_ket_qua_qua_duoc_kiem_tra_dau_vao():
    i = pd.date_range("2018-01-01", periods=800)
    b = pd.DataFrame({"M1": np.ones(800, dtype=int), "M2": np.r_[np.zeros(300, dtype=int), np.ones(500, dtype=int)]}, index=i)
    assert kiem_tra_giao_dich(bang_giao_dich(b, []).assign(date=lambda d: d.date.dt.strftime("%Y-%m-%d")), ["M1", "M2"])[0] == []
