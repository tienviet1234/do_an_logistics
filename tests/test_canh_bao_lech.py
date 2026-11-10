"""Test canh bao du bao lech (khong can CSDL)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from canh_bao_lech import chon_nguong, danh_gia, lech_ke_tiep, sai_so_moi_nhat, tin_hieu  # noqa: E402


def du_bao(ma="A", tu="2026-01-01", so_ngay=40, f=10.0, y=10.0, moc_cach=7):
    """Du bao 28 ngay tu moi moc cach nhau moc_cach ngay, thuc te y."""
    ngay = pd.date_range(tu, periods=so_ngay)
    dong = []
    for m in ngay[::moc_cach]:
        for h in range(1, 29):
            dd = m + pd.Timedelta(days=h)
            dong.append(dict(ma_sku=ma, moc=m, ngay=dd, ngay_thu=h, du_bao=f, thuc_te=(y(dd) if callable(y) else y)))
    return pd.DataFrame(dong)


def test_lay_ban_moi_nhat_va_bo_ngay_thieu_thuc_te():
    d = pd.DataFrame({"ma_sku": ["A"] * 3, "ngay": ["2026-01-10"] * 2 + ["2026-01-11"], "moc": ["2026-01-01", "2026-01-08", "2026-01-08"],
                      "ngay_thu": [9, 2, 3], "du_bao": [5.0, 8.0, 1.0], "thuc_te": [10.0, 10.0, np.nan]})
    e = sai_so_moi_nhat(d)
    assert len(e) == 1 and e.e.iloc[0] == pytest.approx(2.0)


def test_khong_nhin_truoc():
    e = sai_so_moi_nhat(du_bao(y=lambda dd: 10.0 if dd <= pd.Timestamp("2026-01-30") else 1000.0, so_ngay=60))
    a = tin_hieu(e, "2026-01-30")
    assert a.ts.iloc[0] != a.ts.iloc[0] or abs(a.ts.iloc[0]) < 1e-9         # thuc te sau ngay lap phieu khong lam doi tin hieu
    assert a.tong.iloc[0] == pytest.approx(0.0)


def test_lech_deu_cho_ts_bang_so_ngay():
    e = sai_so_moi_nhat(du_bao(f=10.0, y=12.0, so_ngay=60))
    a = tin_hieu(e, "2026-02-20")
    assert a.n.iloc[0] == 28 and a.ts.iloc[0] == pytest.approx(28.0)       # moi ngay lech +2, MAD = 2
    b = tin_hieu(sai_so_moi_nhat(du_bao(f=12.0, y=10.0, so_ngay=60)), "2026-02-20")
    assert b.ts.iloc[0] == pytest.approx(-28.0)


def test_thieu_ngay_hoac_mad_0_thi_khong_co_tin_hieu():
    e = sai_so_moi_nhat(du_bao(f=10.0, y=10.0, so_ngay=60))
    assert np.isnan(tin_hieu(e, "2026-02-20").ts.iloc[0])                  # MAD = 0
    e2 = sai_so_moi_nhat(du_bao(f=10.0, y=12.0, so_ngay=20))
    assert np.isnan(tin_hieu(e2, "2026-01-10").ts.iloc[0])                 # moi 8 ngay co thuc te < 14


def test_lech_ke_tiep_tinh_tay():
    d = pd.DataFrame({"ma_sku": ["A", "A", "A", "B"], "du_bao": [10.0, 10.0, 10.0, 0.0], "thuc_te": [15.0, 15.0, np.nan, 3.0]})
    b = lech_ke_tiep(d)
    assert b["A"] == pytest.approx(0.5) and np.isnan(b["B"])


def bang(ts, b):
    idx = pd.MultiIndex.from_tuples([(f"M{i % 10}", f"2026-01-{1 + i // 10:02d}") for i in range(len(ts))], names=["ma_sku", "moc"])
    return pd.DataFrame({"ts": ts, "b": b}, index=idx)


def test_danh_gia_va_chon_nguong():
    ts = [10.0] * 10 + [0.5] * 90
    b = [0.5] * 10 + [0.05] * 90
    r = danh_gia(bang(ts, b), 4)
    assert r["so_canh_bao"] == 10 and r["ti_le"] == pytest.approx(0.1) and r["cung_chieu"] == pytest.approx(1.0) and r["boi"] == pytest.approx(10.0) and r["dat"]
    sai_chieu = danh_gia(bang(ts, [-0.5] * 10 + [0.05] * 90), 4)
    assert sai_chieu["cung_chieu"] == pytest.approx(0.0) and not sai_chieu["dat"]
    nhieu = danh_gia(bang([10.0] * 30 + [0.5] * 70, [0.5] * 30 + [0.05] * 70), 4)
    assert nhieu["ti_le"] == pytest.approx(0.3) and not nhieu["dat"]
    assert chon_nguong([dict(nguong=5, dat=True), dict(nguong=3, dat=False), dict(nguong=4, dat=True)]) == 4
    assert chon_nguong([dict(nguong=3, dat=False)]) is None
