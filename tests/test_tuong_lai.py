"""Test dung 28 ngay tuong lai: mo rong lich theo dung quy tac, va dung cho khoang da qua phai trung dac_trung.csv."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
from tuong_lai import ThieuLichAmLich, khung_tuong_lai, mo_rong_lich, mo_rong_nghi  # noqa: E402

D = pd.Timestamp


def lich_mau():
    rows = [("le_30_4_2_9", D(f"{y}-04-30"), -7, 1) for y in (2024, 2025)] + [("le_30_4_2_9", D(f"{y}-09-02"), -7, 1) for y in (2024, 2025)]
    rows += [("tet", D("2024-02-10"), -28, 7), ("tet", D("2025-01-29"), -28, 7)]
    rows += [("nang_nong", D("2024-05-01"), -2, 1), ("nang_nong", D("2025-05-20"), -2, 1)]           # khong lap ngay co dinh
    rows += [("bao_yagi_2024", D("2024-09-07"), -3, 14)]
    return pd.DataFrame(rows, columns=["holiday", "ds", "lower_window", "upper_window"])


def test_mo_rong_ngay_co_dinh_tung_ngay_thang_rieng():
    mr, bo = mo_rong_lich(lich_mau(), D("2026-09-10"), am_lich={"tet": ["2026-02-17"]})
    le = sorted(mr[mr.holiday == "le_30_4_2_9"].ds.dt.strftime("%Y-%m-%d"))
    assert le == ["2024-04-30", "2024-09-02", "2025-04-30", "2025-09-02", "2026-04-30", "2026-09-02"]
    assert "nang_nong" in bo and not (mr.holiday == "nang_nong").sum() > 2
    assert sorted(mr[mr.holiday == "tet"].ds.dt.strftime("%Y-%m-%d")) == ["2024-02-10", "2025-01-29", "2026-02-17"]
    assert (mr.holiday.str.startswith("bao_")).sum() == 1                     # bao khong tu suy ra


def test_chi_them_khi_cua_so_cham_toi_ngay_cuoi():
    mr, _ = mo_rong_lich(lich_mau(), D("2026-04-25"), am_lich={"tet": ["2026-02-17", "2027-02-06"]})
    assert D("2026-04-30") in set(mr.ds) and D("2026-09-02") not in set(mr.ds)   # cua so 30/4 bat dau 23/4 <= 25/4
    mr2, _ = mo_rong_lich(lich_mau(), D("2026-04-22"), am_lich={"tet": ["2026-02-17", "2027-02-06"]})
    assert D("2026-04-30") not in set(mr2.ds)                                 # cua so bat dau 23/4 > 22/4


def test_het_bang_am_lich_thi_bao_loi():
    with pytest.raises(ThieuLichAmLich):
        mo_rong_lich(lich_mau(), D("2027-06-01"), am_lich={"tet": ["2026-02-17"]})


def test_nghi_tet_theo_do_lech_va_ngay_co_dinh():
    nghi = pd.DataFrame({"date": [D("2024-02-09"), D("2024-02-10"), D("2024-02-11"), D("2025-01-28"), D("2025-01-29"), D("2025-01-30"),
                                  D("2024-04-30"), D("2025-04-30"), D("2024-09-07")],
                         "ten_ngay_nghi": ["Nghỉ Tết Nguyên đán"] * 6 + ["Giải phóng miền Nam"] * 2 + ["Đóng cửa do bão Yagi"]})
    lich = pd.DataFrame({"holiday": ["tet", "tet", "tet"], "ds": [D("2024-02-10"), D("2025-01-29"), D("2026-02-17")],
                         "lower_window": -28, "upper_window": 7})
    nm = mo_rong_nghi(nghi, lich, D("2026-05-01"))
    moi = set(nm[nm.date > D("2025-12-31")].itertuples(index=False, name=None))
    assert moi == {(D("2026-02-16"), "Nghỉ Tết Nguyên đán"), (D("2026-02-17"), "Nghỉ Tết Nguyên đán"), (D("2026-02-18"), "Nghỉ Tết Nguyên đán"),
                   (D("2026-04-30"), "Giải phóng miền Nam")}                  # bao khong lap lai


@pytest.mark.skipif(not os.path.exists("data/features/dac_trung.csv"), reason="can du lieu mo phong")
@pytest.mark.parametrize("o", ["2024-01-20", "2025-12-01"])
def test_khung_trung_dac_trung_o_khoang_da_qua(o):
    from danh_gia import load
    from tuong_lai import doc_tham_chieu
    df = load()
    lich, nghi, shock, km = doc_tham_chieu()
    f, _ = khung_tuong_lai(df, o, lich, nghi, shock, km, mo_rong=False)
    g = df[(df.date > o) & (df.date <= D(o) + pd.Timedelta(days=28))][df.attrs["known_ahead"]].sort_values(["ma_sku", "date"]).reset_index(drop=True)
    assert f.shape == g.shape
    for c in f.columns:
        assert (f[c].astype(str) == g[c].astype(str)).all(), c
