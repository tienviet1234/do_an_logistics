"""Buoc 2: tao dac trung (feature) cho mo hinh du bao.
Chay: python src/dac_trung.py
Dau vao : data/clean/giao_dich_sach.csv + data/reference/*.csv (KHONG dung answer_key lam dau vao)
Dau ra  : data/features/dac_trung.csv      (moi dong = 1 SKU x 1 ngay)
          data/features/phan_loai_sku.csv  (ABC, XYZ, ADI/CV2 tinh tren tap train)
          reports/bao_cao_dac_trung.md
"""
import os
import numpy as np
import pandas as pd

CLEAN = "data/clean/giao_dich_sach.csv"
REF = "data/reference"
OUT_DIR = "data/features"
REPORT = "reports/bao_cao_dac_trung.md"
TRAIN_END = pd.Timestamp("2025-09-30")   # het tap train (xem docs/09, GD B)
SALE_WINDOW = (-3, 3)                    # cua so sale lon, theo Tham_so_sale (muc 1)
LAGS = [1, 7, 14, 28, 35, 364]

lines = []
def say(s=""):
    print(s); lines.append(s)

def read(name):
    return pd.read_csv(f"{REF}/{name}", encoding="utf-8-sig")

# ---------------- 1. Doc du lieu ----------------
df = pd.read_csv(CLEAN, encoding="utf-8-sig", parse_dates=["date"])
sku = read("sku_master.csv")
lich = read("lich_su_kien_prophet.csv"); lich["ds"] = pd.to_datetime(lich.ds)
nghi = read("lich_ngay_nghi_kho.csv"); nghi["date"] = pd.to_datetime(nghi.date)
shock = read("su_kien_dot_bien.csv")
for c in ["tu_ngay", "den_ngay"]:
    shock[c] = pd.to_datetime(shock[c])
km = read("lich_khuyen_mai.csv")
for c in ["tu_ngay", "den_ngay"]:
    km[c] = pd.to_datetime(km[c])

df = df.sort_values(["ma_sku", "date"]).reset_index(drop=True)
dates = pd.DatetimeIndex(sorted(df.date.unique()))
say("# Bao cao tao dac trung\n")
say(f"- Dau vao: {len(df):,} dong, {df.ma_sku.nunique()} SKU, {dates.min().date()} den {dates.max().date()}")

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
den = np.where(nxt < len(tet), (tet[np.minimum(nxt, len(tet) - 1)] - d) / np.timedelta64(1, "D"), np.nan)
qua = np.where(prv >= 0, (d - tet[np.maximum(prv, 0)]) / np.timedelta64(1, "D"), np.nan)
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

df = df.merge(cal, on="date", how="left")

# ---------------- 6. Dac trung theo SKU x ngay ----------------
# khuyen mai (lich bo phan ban hang gui truoc)
km_rows = [(dd, r.ma_sku) for r in km.itertuples() for dd in pd.date_range(r.tu_ngay, r.den_ngay)]
km_set = pd.DataFrame(km_rows, columns=["date", "ma_sku"]).drop_duplicates().assign(khuyen_mai=1)
df = df.merge(km_set, on=["date", "ma_sku"], how="left")
df["khuyen_mai"] = df.khuyen_mai.fillna(0).astype(int)

# don B2B dot bien: KHONG biet truoc -> chi dung de loai khoi huan luyen / danh gia, khong dua vao mo hinh
b2b = shock[shock.nhom_ly_do == "Đơn B2B đột biến"]
b2b_rows = [(dd, r.ghi_chu_hoac_sku) for r in b2b.itertuples() for dd in pd.date_range(r.tu_ngay, r.den_ngay)]
b2b_set = pd.DataFrame(b2b_rows, columns=["date", "ma_sku"]).drop_duplicates().assign(don_b2b=1)
df = df.merge(b2b_set, on=["date", "ma_sku"], how="left")
df["don_b2b"] = df.don_b2b.fillna(0).astype(int)

# bien muc tieu: y = qty_out; y_cau = nhu cau tin duoc (bo ngay het hang, ngay kho dong cua)
df["y"] = df.qty_out
df["y_cau"] = df.qty_out.where((df.het_hang == 0) & (df.la_ngay_nghi == 0))

# ---------------- 7. Gia tri tre va trung binh truot (chi dung qua khu) ----------------
df = df.sort_values(["ma_sku", "date"]).reset_index(drop=True)
g = df.groupby("ma_sku").y
for k in LAGS:
    df[f"lag_{k}"] = g.shift(k)
past = g.shift(1)
df["tb_truot_7"] = past.groupby(df.ma_sku).transform(lambda s: s.rolling(7, min_periods=4).mean())
df["tb_truot_28"] = past.groupby(df.ma_sku).transform(lambda s: s.rolling(28, min_periods=14).mean())
df["dlc_truot_28"] = past.groupby(df.ma_sku).transform(lambda s: s.rolling(28, min_periods=14).std())
past28 = g.shift(28)                                        # dung cho du bao 28 ngay toi (chi biet den t-28)
df["tb_truot_28_tre28"] = past28.groupby(df.ma_sku).transform(lambda s: s.rolling(28, min_periods=14).mean())

# ---------------- 8. Phan loai SKU tren TAP TRAIN (tranh nhin thay tuong lai) ----------------
tr = df[(df.date <= TRAIN_END) & (df.la_ngay_nghi == 0)].merge(sku[["ma_sku", "gia_von"]], on="ma_sku")
val = (tr.qty_out * tr.gia_von).groupby(tr.ma_sku).sum().sort_values(ascending=False)
cum = val.cumsum() / val.sum()
abc = pd.Series(np.where(cum <= 0.75, "A", np.where(cum <= 0.92, "B", "C")), index=val.index)
mth = tr.groupby(["ma_sku", tr.date.dt.to_period("M")]).qty_out.sum()
cv_m = mth.groupby(level=0).std() / mth.groupby(level=0).mean()
xyz = pd.Series(np.where(cv_m <= 0.5, "X", np.where(cv_m <= 1.0, "Y", "Z")), index=cv_m.index)

def adi_cv2(s):                                             # Syntetos-Boylan
    nz = s[s > 0]
    adi = len(s) / max(len(nz), 1)
    cv2 = (nz.std() / nz.mean()) ** 2 if len(nz) > 1 else np.nan
    return pd.Series({"adi": adi, "cv2": cv2})

sb = tr[tr.het_hang == 0].groupby("ma_sku").qty_out.apply(adi_cv2).unstack()
sb["loai_nhu_cau"] = np.select(
    [(sb.adi < 1.32) & (sb.cv2 < 0.49), (sb.adi < 1.32), (sb.cv2 < 0.49)],
    ["smooth (đều)", "erratic (thất thường)", "intermittent (rời rạc)"], "lumpy (rời rạc + thất thường)")
pl = pd.DataFrame({"abc_train": abc, "cv_thang_train": cv_m.round(3), "xyz_train": xyz}).join(sb.round(3))
pl.index.name = "ma_sku"
pl = pl.reset_index().merge(sku[["ma_sku", "ten_sku", "phan_loai_ABC", "phan_loai_XYZ"]], on="ma_sku")

static = sku[["ma_sku", "nhom_hang", "loai_mua_vu", "gia_ban", "lead_time_tb", "nha_cung_cap"]]
df = df.merge(static, on="ma_sku", how="left").merge(pl[["ma_sku", "abc_train", "xyz_train", "loai_nhu_cau"]], on="ma_sku", how="left")

# ---------------- 9. Ghi file ----------------
os.makedirs(OUT_DIR, exist_ok=True)
df.to_csv(f"{OUT_DIR}/dac_trung.csv", index=False, encoding="utf-8-sig")
pl.to_csv(f"{OUT_DIR}/phan_loai_sku.csv", index=False, encoding="utf-8-sig")

sk_cols = [c for c in df.columns if c.startswith("sk_")]
say(f"- Dau ra: {len(df):,} dong x {df.shape[1]} cot -> {OUT_DIR}/dac_trung.csv")
say(f"- Cot su kien ({len(sk_cols)}): {', '.join(sk_cols)}")
say(f"- Ngay co bao (muc > 0): {(cal.bao_lu_muc_do > 0).sum()} ngay; ngay sale: {cal.ngay_sale.sum()}; dong khuyen mai: {df.khuyen_mai.sum():,}")
say(f"- Dong don B2B dot bien (loai khoi huan luyen): {df.don_b2b.sum()}")
say(f"- y_cau bo trong (het hang hoac kho dong cua): {df.y_cau.isna().sum():,} dong")
say("\n## Phan loai SKU tren tap train (den " + str(TRAIN_END.date()) + ")")
say("- ABC: " + str(pl.abc_train.value_counts().sort_index().to_dict()) + "  (sku_master tinh tren 36 thang: " + str(sku.phan_loai_ABC.value_counts().sort_index().to_dict()) + ")")
say("- XYZ: " + str(pl.xyz_train.value_counts().sort_index().to_dict()) + "  (sku_master: " + str(sku.phan_loai_XYZ.value_counts().sort_index().to_dict()) + ")")
say("- Loai nhu cau (ADI/CV2): " + str(pl.loai_nhu_cau.value_counts().to_dict()))
say(f"- SKU doi nhom ABC so voi sku_master: {(pl.abc_train != pl.phan_loai_ABC).sum()}; doi XYZ: {(pl.xyz_train != pl.phan_loai_XYZ).sum()}")

# ---------------- 10. Kiem tra voi dap an (chi de kiem tra, khong dua vao mo hinh) ----------------
ak_path = "data/answer_key/giao_dich_nhap_xuat_ton_SACH.csv"
if os.path.exists(ak_path):
    ak = pd.read_csv(ak_path, encoding="utf-8-sig", parse_dates=["date"])
    m = df.merge(ak, on=["date", "ma_sku"], suffixes=("", "_ak"))
    say("\n## Doi chieu voi answer_key (ty le dong khop)")
    for c in ["thu", "mua", "khuyen_mai", "trong_tuan_tet", "bao_lu_muc_do"]:
        say(f"- {c}: {(m[c] == m[c + '_ak']).mean() * 100:.2f}%")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
