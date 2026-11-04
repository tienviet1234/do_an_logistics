"""Test giao dien muc Chi so kho (man Kich ban & ket qua): khong loi o moi to hop bo loc, so tren man khop tinh doc lap tu CSDL.
Chay tai thu muc goc: python -m pytest tests/test_giao_dien_kho.py"""
import itertools
import os
import re
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from streamlit.testing.v1 import element_tree as et

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)
from chi_so_kho import chi_so_theo_nhom  # noqa: E402
from csdl import doc  # noqa: E402

APP = ROOT / "app"
VO = (f"import sys, runpy\nsys.path.insert(0, {str(APP)!r})\nimport chung as C\nC.kiem_tra_csdl(); C.khoi_tao(); C.giao_dien('ket-qua')\n"
      f"runpy.run_path({str(APP / 'trang' / 'ket_qua.py')!r}, run_name='__main__')\n")


def _chi_so(self):                                          # va loi AppTest 1.45: o chon dang trong -> None
    v = self.value
    v = [] if v is None else (v if isinstance(v, (list, tuple)) else [v])
    return [self.options.index(self.format_func(x)) for x in v]


et.ButtonGroup.indices = property(_chi_so)


@pytest.fixture(scope="module")
def at():
    a = AppTest.from_string(VO, default_timeout=300).run()
    assert not a.exception
    return a


def bang_kho(a):
    m = next(x.value for x in a.markdown if "Vòng quay (lần/năm)" in x.value)
    return {re.sub(r"<.*", "", h).replace("&nbsp;", "").strip(): (v, d) for h, v, d in re.findall(r"<tr[^>]*><td>(.*?)</td><td>([^<]*)</td><td>([^<]*)</td>", m)}


def tinh_tay(cs, lv, abc=None, xyz=None):
    p = doc("SELECT s.ma_sku, s.gia_von, q.abc_train a, q.xyz_train x FROM dm_sku s JOIN phan_loai_sku q USING (ma_sku)").set_index("ma_sku")
    if abc:
        p = p[p.a.isin(abc)]
    if xyz:
        p = p[p.x.isin(xyz)]
    k = doc("SELECT * FROM ket_qua_ton_kho WHERE ma_chinh_sach = ? AND ROUND(muc_phuc_vu, 2) = ?", (cs, lv))
    k = k[k.ma_sku.isin(p.index)]
    return chi_so_theo_nhom(k.assign(gia_von=k.ma_sku.map(p.gia_von), c=1), ["c"], doc("SELECT COUNT(DISTINCT ngay) AS n FROM mo_phong_ngay").n.iloc[0]).iloc[0]


def vn(v):
    return f"{v:,.1f}".replace(",", "_").replace(".", ",").replace("_", ".")


@pytest.mark.parametrize("lv", [0.90, 0.95, 0.99])
def test_so_tren_man_khop_tinh_doc_lap(at, lv):
    at.session_state["abc"], at.session_state["xyz"] = [], []
    at.session_state["kq_lv"] = lv
    at.run()
    assert not at.exception
    b = bang_kho(at)
    for cs, ten in [("cong_thuc_du_bao_ai_hc", "AI + hiệu chỉnh lệch"), ("cong_thuc_du_bao_moc", "Công thức + dự báo mốc"), ("hien_trang", "Hiện trạng*")]:
        r = tinh_tay(cs, lv)
        assert b[ten] == (vn(r.vong_quay), vn(r.doh)), f"{cs} {lv}: {b[ten]}"


@pytest.mark.parametrize("abc,xyz", [([], ["X"]), ([], ["Y"]), ([], ["Z"]), (["A"], []), (["B"], ["Z"]), (["C"], ["Z"]), (["C"], ["Y"]), (["A"], ["Y"]), (["A", "B"], ["X", "Z"])])
def test_moi_to_hop_bo_loc(at, abc, xyz):
    at.session_state["kq_lv"] = 0.95
    at.session_state["abc"], at.session_state["xyz"] = abc, xyz
    at.run()
    assert not at.exception, (abc, xyz, at.exception)
    r = tinh_tay("cong_thuc_du_bao_ai_hc", 0.95, abc, xyz)
    assert bang_kho(at)["AI + hiệu chỉnh lệch"] == (vn(r.vong_quay), vn(r.doh))


@pytest.mark.parametrize("cs", ["cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"])
def test_doi_chinh_sach_doi_bang_ton_du(at, cs):
    at.session_state["abc"], at.session_state["xyz"] = [], []
    at.session_state["cs"] = cs
    at.run()
    assert not at.exception
    assert any("Hàng tồn dư nhiều nhất" in m.value for m in at.markdown)
    d = at.dataframe[0].value if at.dataframe else None
    assert d is not None and len(d) == 10 and d.du.is_monotonic_decreasing and (d.du <= d.ton).all()


def test_thu_tu_cac_loc_khong_de_lai_loi(at):
    for abc, xyz in itertools.product([[], ["A"], ["C"]], [[], ["Z"]]):
        at.session_state["abc"], at.session_state["xyz"] = abc, xyz
        at.run()
        assert not at.exception
    at.session_state["abc"], at.session_state["xyz"] = [], []
