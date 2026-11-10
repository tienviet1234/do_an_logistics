"""Test cong thuc ghep khi chay mo hinh tren dashboard (khong can CSDL, khong hoc mo hinh)."""
import os
import sys

import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from chay_du_bao import ghep  # noqa: E402


def _ctx(kieu):
    fut = pd.DataFrame({"ma_sku": ["A"], "xyz_train": ["Y"]})
    ts = dict(lgb={"X": 0.9, "Y": 0.3, "Z": 0.0}, rnn={"X": 0.5, "Y": 0.4, "Z": 0.5})
    return dict(kieu=kieu, fut=fut, trong_so=ts)


def test_ghep_v4_theo_nhom():
    d = pd.to_datetime(["2026-10-01", "2026-10-02"])
    x, w = ghep(_ctx("v4"), "A", pd.DataFrame({"date": d, "du_bao": [10.0, 20.0]}), pd.DataFrame({"date": d, "du_bao": [30.0, 0.0]}))
    assert w == dict(nhom="Y", w_lgb=0.3)
    assert list(x.du_bao) == pytest.approx([0.3 * 10 + 0.7 * 30, 0.3 * 20])


def test_ghep_dl_hai_tang():
    d = pd.to_datetime(["2016-05-23"])
    x, w = ghep(_ctx("dl"), "A", pd.DataFrame({"date": d, "du_bao": [10.0]}), pd.DataFrame({"date": d, "du_bao": [30.0]}),
                pd.DataFrame({"date": d, "du_bao": [50.0]}))
    kh = 0.3 * 10 + 0.7 * 30
    assert w["w_rnn"] == 0.4 and x.du_bao.iloc[0] == pytest.approx(0.4 * 50 + 0.6 * kh)


def test_bat_khuyen_mai_chi_doi_ma_va_khoang_chon():
    from chay_du_bao import bat_khuyen_mai
    d = pd.date_range("2026-10-01", periods=5)
    fut = pd.DataFrame({"ma_sku": ["A"] * 5 + ["B"] * 5, "date": list(d) * 2, "khuyen_mai": 0, "thu": 2})
    f = bat_khuyen_mai(fut, "A", "2026-10-02", "2026-10-03")
    assert list(f[f.ma_sku == "A"].khuyen_mai) == [0, 1, 1, 0, 0] and f[f.ma_sku == "B"].khuyen_mai.sum() == 0
    assert fut.khuyen_mai.sum() == 0 and f.thu.equals(fut.thu)
    with pytest.raises(ValueError):
        bat_khuyen_mai(fut, "A", "2026-10-03", "2026-10-02")
    with pytest.raises(ValueError):
        bat_khuyen_mai(fut, "A", "2026-11-01", "2026-11-02")


def test_km_lich_su_tinh_tay():
    from chay_du_bao import km_lich_su
    ngay = pd.date_range("2026-01-01", periods=40)
    y = [10.0] * 40
    km = [0] * 40
    for i in (35, 36):
        km[i], y[i] = 1, 30.0                         # 2 ngay KM ban 30 so voi nen 10
    y[38] = None
    df = pd.DataFrame({"ma_sku": "A", "date": ngay, "la_ngay_nghi": 0, "khuyen_mai": km, "y_cham": y})
    r = km_lich_su(df, "A")
    assert r["so_ngay_km"] == 2 and r["ti_so_tho"] == pytest.approx(3.0) and r["ti_so_cung_mua"] == pytest.approx(3.0)
    n = 100                                                                       # KM roi vao mua cao: tho phong dai, cung mua thi khong
    mua = pd.DataFrame({"ma_sku": "A", "date": pd.date_range("2026-01-01", periods=n), "la_ngay_nghi": 0,
                        "khuyen_mai": [0] * 95 + [1, 1] + [0] * 3, "y_cham": [5.0] * 60 + [20.0] * 35 + [40.0, 40.0] + [20.0] * 3})
    r2 = km_lich_su(mua, "A")
    assert r2["ti_so_tho"] > 3 and r2["ti_so_cung_mua"] == pytest.approx(2.0, rel=0.25)
    r3 = km_lich_su(df.assign(khuyen_mai=0), "A")
    assert r3["so_ngay_km"] == 0 and r3["ti_so_tho"] != r3["ti_so_tho"] and r3["ti_so_cung_mua"] != r3["ti_so_cung_mua"]
