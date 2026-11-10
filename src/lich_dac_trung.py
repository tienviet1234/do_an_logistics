"""Dac trung lich theo ngay (chung moi SKU): lich, ngay le / su kien, Tet, bao lu, sale. Tach tu dac_trung.py de dung chung
cho du lieu lich su va 28 ngay tuong lai (src/tuong_lai.py). Noi dung giu nguyen tung dong (co test doi chieu)."""
import numpy as np
import pandas as pd


def lich_theo_ngay(dates, lich, nghi, shock, SALE_WINDOW=(-3, 3)):
    """dates: DatetimeIndex. lich: lich_su_kien_prophet (ds da la ngay); nghi: lich_ngay_nghi_kho; shock: su_kien_dot_bien (tu_ngay, den_ngay la ngay)."""
    # ---------------- 2. Dac trung lich (theo ngay, chung moi SKU) ----------------
    cal = pd.DataFrame({"date": dates})
    cal["thu"] = cal.date.dt.weekday + 2                       # 2 = Thu Hai ... 8 = Chu Nhat (giong answer_key)
    cal["cuoi_tuan"] = (cal.date.dt.weekday >= 5).astype(int)
    cal["ngay_trong_thang"] = cal.date.dt.day
    cal["thang"] = cal.date.dt.month
    cal["tuan_trong_nam"] = cal.date.dt.isocalendar().week.astype(int).values
    cal["ngay_trong_nam"] = cal.date.dt.dayofyear
    cal["mua"] = cal.thang.map(lambda m: "Xuân" if m in (2, 3, 4) else "Hạ" if m in (5, 6, 7) else "Thu" if m in (8, 9, 10) else "Đông")
    cal["dau_thang"] = (cal.ngay_trong_thang <= 5).astype(int)
    cal["cuoi_thang"] = (cal.ngay_trong_thang >= cal.date.dt.days_in_month - 4).astype(int)

    # ---------------- 3. Ngay le, su kien (tu lich Prophet) ----------------
    # Bao tach rieng (muc do lay tu su_kien_dot_bien); cac su kien khac: 1 cot co / ten
    la_bao = lich.holiday.str.startswith("bao_")
    for name, g in lich[~la_bao].groupby("holiday"):
        flag = np.zeros(len(cal), dtype=int)
        for r in g.itertuples():
            lo, hi = r.ds + pd.Timedelta(days=int(r.lower_window)), r.ds + pd.Timedelta(days=int(r.upper_window))
            flag |= ((cal.date >= lo) & (cal.date <= hi)).values
        cal[f"sk_{name}"] = flag

    # so ngay den Tet gan nhat phia truoc / da qua Tet bao nhieu ngay
    tet = np.array(sorted(lich.loc[lich.holiday == "tet", "ds"]), dtype="datetime64[ns]")
    d = cal.date.values
    nxt = np.searchsorted(tet, d, side="left")
    prv = np.searchsorted(tet, d, side="right") - 1
    if len(tet):
        den = np.where(nxt < len(tet), (tet[np.minimum(nxt, len(tet) - 1)] - d) / np.timedelta64(1, "D"), np.nan)
        qua = np.where(prv >= 0, (d - tet[np.maximum(prv, 0)]) / np.timedelta64(1, "D"), np.nan)
    else:                                                       # du lieu khong co Tet (VD nuoc ngoai)
        den = qua = np.full(len(d), np.nan)
    cal["so_ngay_den_tet"] = np.clip(den, 0, 60)               # > 60 ngay coi nhu xa Tet
    cal["so_ngay_sau_tet"] = np.clip(qua, 0, 60)

    # nghi Tet (kho dong cua dip Tet)
    tet_nghi = set(nghi.loc[nghi.ten_ngay_nghi == "Nghỉ Tết Nguyên đán", "date"])
    cal["trong_tuan_tet"] = cal.date.isin(tet_nghi).astype(int)

    # ---------------- 4. Bao lu: muc do trong cua so -3 ... +14 ngay ----------------
    storms = shock[shock.nhom_ly_do == "Thiên tai"]
    lvl = np.zeros(len(cal))
    for r in storms.itertuples():
        lo, hi = r.tu_ngay - pd.Timedelta(days=3), r.tu_ngay + pd.Timedelta(days=14)
        m = ((cal.date >= lo) & (cal.date <= hi)).values
        lvl[m] = np.maximum(lvl[m], float(r.muc_do_0_1))
    cal["bao_lu_muc_do"] = lvl
    cal["bao_truoc"] = 0; cal["bao_sau"] = 0                    # pha mua tich tru (-3..0) va cuu tro (+1..+14)
    for r in storms.itertuples():
        k = (cal.date - r.tu_ngay).dt.days
        cal.loc[(k >= -3) & (k <= 0), "bao_truoc"] = 1
        cal.loc[(k >= 1) & (k <= 14), "bao_sau"] = 1

    # ---------------- 5. Sale san TMDT (chi 11.11, 12.12, Black Friday co hieu ung trong du lieu mo phong) ----------------
    sale_days = []
    for y in sorted(set(cal.date.dt.year)):
        sale_days += [pd.Timestamp(y, 11, 11), pd.Timestamp(y, 12, 12)]
        nov = pd.date_range(f"{y}-11-01", f"{y}-11-30")
        sale_days.append(nov[nov.weekday == 4][3])              # thu Sau thu 4 cua thang 11
    cal["ngay_sale"] = cal.date.isin(sale_days).astype(int)
    cal["cua_so_sale"] = 0
    for sd in sale_days:
        cal.loc[(cal.date >= sd + pd.Timedelta(days=SALE_WINDOW[0])) & (cal.date <= sd + pd.Timedelta(days=SALE_WINDOW[1])), "cua_so_sale"] = 1

    return cal
