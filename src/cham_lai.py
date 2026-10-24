"""Cham lai cac du bao da luu khi nhom ABC/XYZ thay doi (VD sau src/cap_nhat_gia.py -> src/dac_trung.py), KHONG huan luyen lai.
Chay: python src/cham_lai.py   (sau dac_trung.py, truoc khi chay lai LightGBM / ARIMA / chon_mo_hinh)

- Mo hinh khong dung gia hay nhom ABC lam dau vao (naive, seasonal_naive_7, tb_truot_28, ets, croston_sba, tsb, prophet*):
  du bao giu nguyen, chi tinh lai cac chi so theo nhom (WMAPE_A/B/C...) bang save_results voi ghi chu cu.
- Mo hinh PHAI chay lai (xoa dong cu trong reports/ket_qua_mo_hinh.csv de khong bi dung lai ket qua cu):
  lightgbm* (dung gia_ban, abc_train lam dac trung), arima (chi chay cho nhom A), ket_hop*, trung_binh* (ghep tu LightGBM).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import PRED_DIR, RESULT, load, save_results  # noqa: E402

CHAY_LAI = ("lightgbm", "arima", "ket_hop", "trung_binh")

if __name__ == "__main__":
    df = load()
    res = pd.read_csv(RESULT, encoding="utf-8-sig")
    bo = res.mo_hinh.str.startswith(CHAY_LAI)
    res[~bo].to_csv(RESULT, index=False, encoding="utf-8-sig")
    print(f"Xoa {bo.sum()} dong can chay lai: {sorted(set(res[bo].mo_hinh))}")
    NHOM = ["y_cham", "abc_train", "xyz_train", "loai_nhu_cau"]
    for r in res[~bo].itertuples():
        f = f"{PRED_DIR}/{r.mo_hinh}_{r.tap}.csv"
        pred = pd.read_csv(f, encoding="utf-8-sig", parse_dates=["date", "moc"])
        # file du bao luu kem cot nhom LUC CHAY (score() doc cot nay) -> bo di, ghep lai tu dac trung moi (giong backtest)
        moi = pred.drop(columns=NHOM).merge(df[["date", "ma_sku"] + NHOM], on=["date", "ma_sku"], how="left")
        assert moi.y_cham.equals(pred.y_cham) or ((moi.y_cham - pred.y_cham).abs().max() < 1e-9), f"y_cham doi o {f}"
        s = save_results(r.mo_hinh, moi[pred.columns], df, r.tap, "" if pd.isna(r.ghi_chu) else r.ghi_chu)
        thay_doi = abs(s.WMAPE.iloc[0] - r.WMAPE) > 1e-12
        print(f"  {r.mo_hinh:18s} {r.tap:11s} WMAPE {s.WMAPE.iloc[0]:.4f}"
              f"{'  (KHAC truoc - kiem tra!)' if thay_doi else ''}  WMAPE_A {r.WMAPE_A:.3f} -> {s.WMAPE_A.iloc[0]:.3f}")
