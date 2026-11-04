"""Test so so lieu do an: so khop nguon, phan chua co ket qua khong lam hong tep. Chay: python -m pytest tests/test_so_lieu_do_an.py"""
import os
import sys

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from so_lieu_do_an import CHUA_CO, RA, bang, doc_tep, ghi, pt, so, tao  # noqa: E402


def test_dinh_dang_so_kieu_viet_nam():
    assert so(1234.5) == "1.234,5" and so(0.356, 3) == "0,356" and so(1234, 0) == "1.234"
    assert pt(0.03) == "+3,0%" and pt(-0.353) == "−35,3%" and pt(0) == "0,0%"


def test_bang_markdown():
    assert bang(["A", "B"], [[1, 2]]) == ["| A | B |", "|---|---|", "| 1 | 2 |"]


def test_tep_chua_co_khong_loi(tmp_path):
    assert doc_tep(tmp_path / "khong_co.md") == [CHUA_CO]
    f = tmp_path / "a.md"
    f.write_text("# Tieu de\n\nNoi dung", encoding="utf-8")
    assert doc_tep(f) == ["", "Noi dung"]


def test_tao_khong_ghi_de_bao_cao(tmp_path):
    """Chay test khong duoc doi reports/so_lieu_do_an.md."""
    truoc = open(RA, "rb").read() if os.path.exists(RA) else None
    L = tao()
    assert (open(RA, "rb").read() if os.path.exists(RA) else None) == truoc
    f = tmp_path / "con" / "so.md"
    assert ghi(["a", "b"], str(f)) == str(f) and f.read_text(encoding="utf-8") == "a\nb"
    assert L


def test_so_trong_so_khop_nguon():
    from csdl import doc
    van_ban = "\n".join(tao())
    kq = pd.read_csv("reports/ket_qua_mo_hinh.csv", encoding="utf-8-sig")
    r = kq[(kq.mo_hinh == "ket_hop_v4") & (kq.tap == "test")].iloc[0]
    assert so(r.WMAPE, 3) in van_ban and pt(r.Bias_pct) in van_ban
    v = doc("SELECT * FROM v_so_sanh_chinh_sach WHERE ma_chinh_sach = 'cong_thuc_du_bao_ai_hc' AND ROUND(muc_phuc_vu, 2) = 0.95").iloc[0]
    assert f"{so(v.fill_rate_pt, 2)}%" in van_ban and so(v.chi_phi_lien_quan_trieu) in van_ban
    assert "mô phỏng" in van_ban and "## 10." in van_ban
