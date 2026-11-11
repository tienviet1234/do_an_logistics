"""Test so sanh ket qua chay lai: sai so so lieu, cot chu, khoa (mo_hinh, tap), che do chay chua xong, bo dong thoi diem."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from so_sanh_chay_lai import so_csv, so_tep  # noqa: E402


def ghi(p, df):
    df.to_csv(p, index=False, encoding="utf-8-sig")
    return str(p)


def test_so_lieu_trong_sai_so_la_giong(tmp_path):
    a = ghi(tmp_path / "a.csv", pd.DataFrame({"x": [1.0, 1000.0], "ten": ["p", "q"]}))
    b = ghi(tmp_path / "b.csv", pd.DataFrame({"x": [1.0 + 1e-9, 1000.0 * (1 + 1e-8)], "ten": ["p", "q"]}))
    assert so_csv(a, b) is None


def test_so_lieu_lech_va_chu_khac_bi_bat(tmp_path):
    a = ghi(tmp_path / "a.csv", pd.DataFrame({"x": [1.0, 2.0], "ten": ["p", "q"]}))
    assert "cot x" in so_csv(a, ghi(tmp_path / "b.csv", pd.DataFrame({"x": [1.0, 2.01], "ten": ["p", "q"]})))
    assert "cot ten" in so_csv(a, ghi(tmp_path / "c.csv", pd.DataFrame({"x": [1.0, 2.0], "ten": ["p", "r"]})))
    assert "so dong" in so_csv(a, ghi(tmp_path / "d.csv", pd.DataFrame({"x": [1.0], "ten": ["p"]})))
    assert "NaN" not in str(so_csv(a, a))


def test_ket_qua_mo_hinh_so_theo_khoa_va_che_do_chua_xong(tmp_path):
    a = ghi(tmp_path / "ket_qua_mo_hinh.csv", pd.DataFrame({"mo_hinh": ["m1", "m2", "m3"], "tap": ["test"] * 3, "WMAPE": [0.3, 0.4, 0.5]}))
    d = tmp_path / "moi"
    d.mkdir()
    b = ghi(d / "ket_qua_mo_hinh.csv", pd.DataFrame({"mo_hinh": ["m2", "m1"], "tap": ["test"] * 2, "WMAPE": [0.4, 0.3]}))
    assert so_tep(a, b, "reports/ket_qua_mo_hinh.csv") == "so dong 3 / 2"          # chay xong: thieu dong la khac
    assert so_tep(a, b, "reports/ket_qua_mo_hinh.csv", giao=True) is None            # chua xong: chi so dong chung, khong phu thuoc thu tu
    c = ghi(d / "k2.csv", pd.DataFrame({"mo_hinh": ["m1"], "tap": ["test"], "WMAPE": [0.31]}))
    assert "WMAPE" in so_tep(a, c, "x/ket_qua_mo_hinh.csv", giao=True)


def test_van_ban_bo_dong_thoi_diem(tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("# T\nTạo tự động lúc 10/11/2026 16:41\nso 1\n", encoding="utf-8")
    b.write_text("# T\nTạo tự động lúc 11/11/2026 09:00\nso 1\n", encoding="utf-8")
    assert so_tep(str(a), str(b), "a.md") is None
    b.write_text("# T\nTạo tự động lúc 11/11/2026 09:00\nso 2\n", encoding="utf-8")
    assert "1 dong khac" in so_tep(str(a), str(b), "a.md")
