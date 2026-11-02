"""Test doc lua chon tren bieu do va cap nhat bo loc trong callback (hoi quy loi Vega 'Unrecognized data set', 02/11)."""
import datetime as dt
import inspect
import os
import sys
from pathlib import Path

import pytest
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
os.chdir(ROOT)
import chung as C  # noqa: E402


@pytest.fixture(autouse=True)
def trang_thai():
    st.session_state.clear()
    st.session_state.update(ngay=dt.date(2026, 2, 9), cs=C.CS_GOI_Y)
    yield
    st.session_state.clear()


@pytest.mark.parametrize("su_kien", [None, {}, {"selection": {}}, {"selection": {"chon_ngay": []}}])
def test_chua_chon_gi(su_kien):
    assert C.gia_tri_chon(su_kien, "chon_ngay", "ngay") is None


def test_doc_dung_gia_tri():
    assert C.gia_tri_chon({"selection": {"chon_ngay": [{"ngay": "2025-12-03"}]}}, "chon_ngay", "ngay") == "2025-12-03"


def test_khi_chon_ngay_doi_ngay_lap_phieu():
    st.session_state["k"] = {"selection": {"chon_ngay": [{"ngay": "2025-12-03"}]}}
    C.khi_chon_ngay("k")
    assert st.session_state.ngay == dt.date(2025, 12, 3)


def test_bo_chon_khong_doi_ngay():
    st.session_state["k"] = {"selection": {"chon_ngay": []}}
    C.khi_chon_ngay("k")
    assert st.session_state.ngay == dt.date(2026, 2, 9)


def test_khi_chon_cs():
    st.session_state["k"] = {"selection": {"chon_cs": [{"ma_chinh_sach": "cong_thuc_du_bao_moc"}]}}
    C.khi_chon_cs("k")
    assert st.session_state.cs == "cong_thuc_du_bao_moc"


def test_hien_trang_khong_doi_chinh_sach():
    st.session_state["k"] = {"selection": {"chon_cs": [{"ma_chinh_sach": "hien_trang"}]}}
    C.khi_chon_cs("k")
    assert st.session_state.cs == C.CS_GOI_Y


def test_cac_man_khong_goi_rerun_khi_ve_bieu_do():
    """st.rerun() giua luc ve la nguyen nhan loi; bo loc phai cap nhat trong callback."""
    for f in ["hom_nay", "ket_qua", "mat_hang"]:
        src = (ROOT / "app" / "trang" / f"{f}.py").read_text(encoding="utf-8")
        assert 'on_select="rerun", selection_mode="chon' not in src, f
    assert "st.rerun" not in inspect.getsource(C.khi_chon_ngay) + inspect.getsource(C.dat_ngay) + inspect.getsource(C.khi_chon_cs)


def test_dac_ta_nhung_khong_co_bo_du_lieu_dat_ten():
    """Hoi quy loi Vega "Unrecognized data set": khong duoc co datasets / data.name, ca voi bieu do nhieu lop dung chung bang."""
    import altair as alt
    import pandas as pd
    f = pd.DataFrame({"d": pd.date_range("2026-01-01", periods=3), "y": [1.0, None, 3.0], "n": ["a", "b", "c"]})
    goc = alt.Chart(f).encode(x="d:T", y="y:Q")
    for bd in [goc.mark_line(), goc.mark_line() + goc.mark_point()]:
        spec = C.dac_ta_nhung(bd)
        assert "datasets" not in spec
        assert "values" in spec["data"] and len(spec["data"]["values"]) == 3 and "name" not in spec["data"]
        assert spec["data"]["values"][1]["y"] is None                      # thieu du lieu van la rong, khong thanh so
        assert spec["data"]["values"][0]["d"].startswith("2026-01-01")      # ngay giu dung, khong doi mui gio
    assert alt.data_transformers.consolidate_datasets is True             # khong de lai thay doi toan cuc cho code khac


def test_it_hon_5000_dong_van_nhung_duoc():
    import altair as alt
    import pandas as pd
    f = pd.DataFrame({"x": range(6000), "y": range(6000)})
    assert len(C.dac_ta_nhung(alt.Chart(f).mark_point().encode(x="x:Q", y="y:Q"))["data"]["values"]) == 6000


def test_moi_bieu_do_deu_qua_ve_bd():
    for f in ["hom_nay", "ket_qua", "mat_hang", "du_lieu"]:
        src = (ROOT / "app" / "trang" / f"{f}.py").read_text(encoding="utf-8")
        assert "altair_chart(" not in src and "vega_lite_chart(" not in src, f
