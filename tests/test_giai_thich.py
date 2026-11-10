"""Test giai thich du bao: moi cot co dung 1 nhom; tong dong gop = log du bao (LightGBM Tweedie); du_doan_lai trung du bao goc."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from giai_thich import TEN_NHOM, gom_nhom, he_so, nhom_cua  # noqa: E402


def test_moi_cot_mot_nhom():
    from mo_hinh_lightgbm import CAT, NUM_KNOWN
    from nang_cap_du_bao import lag_feats
    cot = CAT + NUM_KNOWN + lag_feats(7, True) + lag_feats(28, True) + ["sk_tet", "sk_snap_ca", "den_noel", "sau_the_thao"]
    nh = {c: nhom_cua(c) for c in cot}
    assert set(nh.values()) <= set(TEN_NHOM)
    assert nh["lag_7"] == nh["tb28_tre7"] == "Mức bán gần đây" and nh["lag_364"] == nh["lag_am"] == "Cùng kỳ năm trước"
    assert nh["khuyen_mai"] == "Khuyến mãi" and nh["sk_snap_ca"] == "Lễ, sự kiện biết trước" and nh["thu"] == "Thứ trong tuần"
    with pytest.raises(ValueError):
        nhom_cua("cot_la")


def test_gom_nhom_va_he_so_tinh_tay():
    dg = pd.DataFrame({"date": [pd.Timestamp("2026-10-01")], "ma_sku": ["A"], "la_ngay_nghi": [0], "du_bao": [np.exp(1.0)],
                       "dg_goc": [np.log(2.0)], "dg_lag_7": [np.log(1.5)], "dg_thu": [np.log(0.8)], "dg_khuyen_mai": [0.0],
                       "dg_lag_364": [1.0 - np.log(2.0) - np.log(1.5) - np.log(0.8)]})
    g = gom_nhom(dg)
    assert g.du_bao_tho.iloc[0] == pytest.approx(np.e)
    nen, hs = he_so(g.iloc[0])
    assert nen == pytest.approx(2.0)
    d = dict(hs)
    assert d["Mức bán gần đây"] == pytest.approx(1.5) and d["Thứ trong tuần"] == pytest.approx(0.8) and d["Khuyến mãi"] == pytest.approx(1.0)
    assert nen * np.prod([v for _, v in hs]) == pytest.approx(np.e)


def test_lightgbm_dong_gop_cong_lai_bang_du_bao_va_du_doan_lai_trung():
    """Mo hinh that tren du lieu nho: du_doan_lai (khong hoc lai) trung du bao cua fn; exp(tong dong gop) = du bao."""
    import nang_cap_du_bao as N
    rng = np.random.default_rng(0)
    ngay = pd.date_range("2025-01-01", periods=420)
    dong = []
    for i, ma in enumerate(["A", "B", "C"]):
        y = rng.poisson(10 + 5 * i + 4 * (ngay.weekday >= 5))
        dong.append(pd.DataFrame({"date": ngay, "ma_sku": ma, "y": y, "y_cham": y.astype(float)}))
    df = pd.concat(dong, ignore_index=True)
    from mo_hinh_lightgbm import CAT, NUM_KNOWN
    for c in NUM_KNOWN:
        df[c] = 0
    df["thu"], df["cuoi_tuan"], df["thang"] = df.date.dt.weekday + 2, (df.date.dt.weekday >= 5).astype(int), df.date.dt.month
    for c in CAT:
        if c != "ma_sku":
            df[c] = "x"
    df["la_ngay_nghi"] = 0
    o = ngay[-29]
    hist, fut = df[df.date <= o], df[df.date > o].drop(columns=["y", "y_cham"])
    cats = {c: sorted(df[c].unique()) for c in CAT}
    cal = pd.DataFrame({"date": ngay, "dich_am_lich": np.nan})
    fn = N.make_model({"A": True, "B": False, "params": {"n_estimators": 30}}, cats, [], cal)
    p = fn(hist, fut).sort_values(["ma_sku", "date"]).reset_index(drop=True)
    r = fn.du_doan_lai(fut, dong_gop=True).sort_values(["ma_sku", "date"]).reset_index(drop=True)
    assert np.allclose(p.du_bao.values, r.du_bao.values)
    cot = [c for c in r.columns if c.startswith("dg_")]
    assert np.allclose(np.exp(r[cot].fillna(0).sum(axis=1)), r.du_bao, rtol=1e-6)
    g = gom_nhom(r)
    assert np.allclose(g.du_bao_tho, r.du_bao, rtol=1e-6)
    f2 = fut.assign(khuyen_mai=1)
    assert len(fn.du_doan_lai(f2)) == len(p)
