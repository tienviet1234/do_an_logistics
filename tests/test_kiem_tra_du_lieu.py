"""Test: he thong khong phu thuoc 1 bo du lieu cu the. Chay tai thu muc goc: python -m pytest tests/test_kiem_tra_du_lieu.py"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from kiem_tra_du_lieu import LoiDuLieu, cac_moc_o_giua, dam_bao_hop_le, kiem_tra_giao_dich, moc_thoi_gian, ngay_mac_dinh, ngay_cuoi_cua, nguon_du_lieu  # noqa: E402


def bang(so_ngay=800, ma=("A", "B"), bat_dau="2020-01-01"):
    ngay = pd.date_range(bat_dau, periods=so_ngay).strftime("%Y-%m-%d")
    return pd.concat([pd.DataFrame({"date": ngay, "ma_sku": m, "qty_in": 1.0, "qty_out": 1.0, "ton_cuoi_ngay": 5, "la_ngay_nghi": 0, "het_hang": 0}) for m in ma], ignore_index=True)


def test_moc_khop_du_lieu_hien_tai():
    """Chia tap dung nhu cac moc tung ghi cung: ket qua tren du lieu hien tai khong doi."""
    m = moc_thoi_gian("2026-09-30")
    assert m["DATA_END"] == pd.Timestamp("2026-09-30") and m["TRAIN_END"] == pd.Timestamp("2025-09-30")
    assert m["VAL2_START"] == pd.Timestamp("2024-09-30") and m["VAL_START"] == pd.Timestamp("2025-03-31")


def test_moc_doi_theo_du_lieu_khac():
    m = moc_thoi_gian("2016-05-22")
    assert m["TRAIN_END"] == pd.Timestamp("2015-05-23") and m["VAL2_START"] == pd.Timestamp("2014-05-23")
    assert m["VAL2_START"] < m["VAL_START"] < m["TRAIN_END"] < m["DATA_END"]


def test_du_lieu_tot_khong_loi():
    assert kiem_tra_giao_dich(bang(), ["A", "B"]) == ([], [])


@pytest.mark.parametrize("sua,chu", [
    (lambda d: d.drop(columns="qty_out"), "Thieu cot"),
    (lambda d: d.iloc[0:0], "rong"),
    (lambda d: d.assign(date="abc"), "ngay khong doc"),
    (lambda d: pd.concat([d, d.iloc[[0]]]), "trung"),
    (lambda d: d.assign(qty_out=-1.0), "am"),
    (lambda d: d.assign(qty_out="x"), "khong phai so"),
])
def test_loi_bi_chan(sua, chu):
    loi, _ = kiem_tra_giao_dich(sua(bang()))
    assert any(chu in x for x in loi), loi


def test_du_lieu_qua_ngan_bi_chan():
    assert any("can it nhat" in x for x in kiem_tra_giao_dich(bang(100))[0])


def test_ma_la_bi_chan_ma_thieu_chi_canh_bao():
    loi, _ = kiem_tra_giao_dich(bang(), ["A"])
    assert any("khong co trong danh muc" in x for x in loi)
    loi, cb = kiem_tra_giao_dich(bang(), ["A", "B", "C"])
    assert not loi and any("khong co giao dich" in x for x in cb)


def test_ma_moi_len_ke_muon_chi_canh_bao():
    d = bang()
    moi = d[(d.ma_sku == "A") | (d.date >= "2021-01-01")]
    loi, cb = kiem_tra_giao_dich(moi)
    assert not loi and any("khong du moi ngay" in x for x in cb)


def test_nhieu_ngay_ban_0_canh_bao():
    assert any("ban bang 0" in x for x in kiem_tra_giao_dich(bang().assign(qty_out=0.0))[1])


def test_dam_bao_hop_le_nem_loi():
    with pytest.raises(LoiDuLieu):
        dam_bao_hop_le(bang(100))
    dam_bao_hop_le(bang())


def test_ngay_cuoi_cua_tep(tmp_path):
    f = tmp_path / "a.csv"
    bang(10).to_csv(f, index=False)
    assert ngay_cuoi_cua(f) == pd.Timestamp("2020-01-10")


def test_ngay_mac_dinh():
    mo = pd.date_range("2025-10-01", "2026-09-29").strftime("%Y-%m-%d").tolist()
    assert ngay_mac_dinh(mo, ["2025-01-29", "2026-02-17", "2027-02-06"]) == "2026-02-09"      # dung ngay dang dung
    assert ngay_mac_dinh(mo, []) == mo[len(mo) // 2]                                         # khong co Tet (VD du lieu nuoc ngoai)
    assert ngay_mac_dinh(["2020-01-01"], ["2030-01-01"]) == "2020-01-01"
    with pytest.raises(LoiDuLieu):
        ngay_mac_dinh([])


def test_cac_moc_lay_lan_gan_nhat_moi_loai():
    """Hoi quy: Trung thu co 2 lan trong ky (06/10/2025 va 25/09/2026), phai lay lan sau (ban dau chon nham lan truoc)."""
    moc = pd.date_range("2025-09-30", periods=49, freq="7D")
    r = cac_moc_o_giua(moc, {"Tết": ["2026-02-17"], "Trung thu": ["2025-10-06", "2026-09-25"]})
    assert r == [(pd.Timestamp("2026-01-20"), "Tết"), (pd.Timestamp("2026-09-01"), "Trung thu")]


def test_cac_moc_khong_co_su_kien_van_ve_duoc():
    moc = pd.date_range("2025-09-30", periods=13, freq="28D")
    r = cac_moc_o_giua(moc, {"Tết": [], "Trung thu": ["2010-01-01"]})
    assert len(r) == 2 and all(ten is None for _, ten in r) and r[0][0] < r[1][0]
    assert cac_moc_o_giua([], {"Tết": ["2026-01-01"]}) == []


def test_nguon_mac_dinh_va_tep_rieng(tmp_path):
    assert nguon_du_lieu(tmp_path)["la_mo_phong"] is True
    (tmp_path / "data" / "reference").mkdir(parents=True)
    (tmp_path / "data" / "reference" / "nguon_du_lieu.json").write_text('{"ten": "M5", "la_mo_phong": false}', encoding="utf-8")
    n = nguon_du_lieu(tmp_path)
    assert n["ten"] == "M5" and n["la_mo_phong"] is False and "ghi_chu" in n
