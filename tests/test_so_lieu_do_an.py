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


def test_dac_diem_tinh_dung_tren_csdl_nho(tmp_path):
    """Dac diem du lieu (dung cho ca 2 bo): ngay nghi khong vao chu ky tuan, ti le 0 chi tinh ngay mo cua, khong co CSDL -> chua co."""
    import sqlite3
    from so_lieu_do_an import dac_diem
    assert dac_diem(str(tmp_path / "khong_co.db")) == [CHUA_CO]
    f = str(tmp_path / "k.db")
    c = sqlite3.connect(f)
    ngay = pd.date_range("2024-01-01", periods=14)                 # 2 tuan, bat dau Thu Hai
    gd = pd.DataFrame([dict(ngay=d.strftime("%Y-%m-%d"), ma_sku=m, qty_out=(0 if m == "B" else 10 * (2 if d.dayofweek == 6 else 1)),
                            la_ngay_nghi=int(d.day == 3)) for d in ngay for m in ("A", "B")])
    gd.loc[gd.la_ngay_nghi == 1, "qty_out"] = 0
    gd.to_sql("giao_dich_sach", c, index=False)
    pd.DataFrame([dict(ma_sku="A", so_ngay=4), dict(ma_sku="A", so_ngay=6)]).to_sql("lich_khuyen_mai", c, index=False)
    pd.DataFrame([dict(ma_sku="A", abc_train="A", xyz_train="X", loai_nhu_cau="smooth"), dict(ma_sku="B", abc_train="C", xyz_train="Z", loai_nhu_cau="lumpy")]).to_sql("phan_loai_sku", c, index=False)
    c.close()
    t = "\n".join(dac_diem(f))
    assert "| Ngày kho nghỉ (cả kho) | 1 ngày |" in t
    assert "50,0%" in t                                         # ma B luon 0, ngay nghi khong tinh
    assert "2 / 1 / 5,0 ngày" in t and "smooth 1" in t and "lumpy 1" in t
    # chu ky tuan: Chu nhat gap doi ngay thuong, ngay nghi (Thu Tu 03/01) bi bo
    tb = (10 * 11 + 20 * 2) / 13
    assert t.splitlines()[-1] == "| " + " | ".join(so(v, 2) for v in [10 / tb] * 6 + [20 / tb]) + " |"
