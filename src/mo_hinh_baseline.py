"""GD C: mo hinh moc (baseline) chinh thuc, cham bang khung chung src/danh_gia.py.
Mo hinh: Trung binh truot 28 ngay, ETS (tu chon, chu ky 7), ARIMA (tu chon, chu ky 7), Croston SBA, TSB.
ARIMA cham (~3 giay/SKU/moc) nen chi chay cho SKU nhom A (abc_train = A); so sanh voi mo hinh khac qua cot WMAPE_A.
Chay: python src/mo_hinh_baseline.py            (validation + test, moi mo hinh)
      python src/mo_hinh_baseline.py --thu       (chi 1 moc test, de do thoi gian)
Ket qua: them dong vao reports/ket_qua_mo_hinh.csv, du bao chi tiet reports/du_bao/<mo_hinh>_<tap>.csv
"""
import os
import sys
import time
import warnings
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, save_results, HORIZON  # noqa: E402

warnings.filterwarnings("ignore")
os.environ["NIXTLA_ID_AS_COL"] = "1"
from statsforecast import StatsForecast  # noqa: E402
from statsforecast.models import AutoETS, AutoARIMA, CrostonSBA, TSB, WindowAverage  # noqa: E402

FIT_DAYS = 365          # chi hoc 365 ngay gan nhat (du 1 chu ky nam ngan, chay nhanh)
CHI_NHOM_A = {"arima"}  # mo hinh chi chay cho SKU nhom A

MODELS = {              # ten luu ket qua -> (doi tuong statsforecast, ghi chu)
    "tb_truot_28": (WindowAverage(window_size=28, alias="tb_truot_28"), "TB 28 ngay gan nhat, du bao phang"),
    "ets": (AutoETS(season_length=7, alias="ets"), "ETS tu chon (Holt-Winters), chu ky tuan"),
    "arima": (AutoARIMA(season_length=7, alias="arima"), "ARIMA/SARIMA tu chon, chu ky tuan; CHI 31 SKU nhom A, so sanh qua WMAPE_A"),
    "croston_sba": (CrostonSBA(alias="croston_sba"), "Croston co hieu chinh SBA, cho hang roi rac"),
    "tsb": (TSB(alpha_d=0.2, alpha_p=0.2, alias="tsb"), "TSB alpha 0,2, cho hang roi rac"),
}

_cache = {}


def _series(hist):
    """Chuoi nhu cau tin duoc theo ngay cho tung SKU, FIT_DAYS ngay cuoi.
    Ngay het hang / kho dong cua (y_cau rong) -> noi suy tu ngay ben canh."""
    end = hist.date.max()
    h = hist[hist.date > end - pd.Timedelta(days=FIT_DAYS)][["ma_sku", "date", "y_cau"]]
    h = h.sort_values(["ma_sku", "date"])
    h["y"] = h.groupby("ma_sku").y_cau.transform(lambda s: s.interpolate(limit_direction="both")).fillna(0)
    return h.rename(columns={"ma_sku": "unique_id", "date": "ds"})[["unique_id", "ds", "y"]]


def _forecast_all(hist):
    """Chay tat ca mo hinh 1 lan cho 1 moc, luu vao bo nho tam."""
    # n_jobs=1: chay song song (n_jobs=-1) bi loi BrokenProcessPool tren Windows
    o = hist.date.max()
    if o not in _cache:
        s = _series(hist)
        nhom_a = hist.loc[hist.abc_train == "A", "ma_sku"].unique()
        fast = [m for k, (m, _) in MODELS.items() if k not in CHI_NHOM_A]
        slow = [m for k, (m, _) in MODELS.items() if k in CHI_NHOM_A]
        fc = StatsForecast(models=fast, freq="D", n_jobs=1).forecast(df=s, h=HORIZON)
        if slow:
            fa = StatsForecast(models=slow, freq="D", n_jobs=1).forecast(df=s[s.unique_id.isin(nhom_a)], h=HORIZON)
            fc = fc.merge(fa, on=["unique_id", "ds"], how="left")
        _cache[o] = fc.rename(columns={"unique_id": "ma_sku", "ds": "date"})
    return _cache[o]


def model_fn(name):
    def fn(hist, fut):
        fc = _forecast_all(hist)[["ma_sku", "date", name]]
        out = fut[["date", "ma_sku", "la_ngay_nghi"]].merge(fc, on=["ma_sku", "date"], how="left")
        if name in CHI_NHOM_A:
            out = out[out[name].notna()]                                    # chi SKU nhom A
        out["du_bao"] = np.where(out.la_ngay_nghi == 1, 0, out[name].fillna(0))   # kho dong cua: khong xuat
        return out[["date", "ma_sku", "du_bao"]]
    return fn


if __name__ == "__main__":
    df = load()
    if "--thu" in sys.argv:
        t0 = time.time()
        _forecast_all(df[df.date <= folds("test")[0]])
        print(f"1 moc, {df.ma_sku.nunique()} SKU, {len(MODELS)} mo hinh: {time.time() - t0:.0f} giay")
        sys.exit()
    for kind in ["validation", "test"]:
        fo = folds(kind)
        _cache.clear()
        for name, (_, note) in MODELS.items():
            p = backtest(model_fn(name), df, fo, name=f"{name}/{kind}")
            r = save_results(name, p, df, kind, note)
            print(r[["mo_hinh", "tap", "WMAPE", "WMAPE_tuan", "WMAPE_A", "MASE", "Bias_pct"]].round(3).to_string(index=False, header=False), flush=True)
    print("Da ghi reports/ket_qua_mo_hinh.csv")
