"""Buoc 2: phan tich kham pha du lieu (EDA) - ve hinh cho Chuong 4.
Chay: python src/eda.py   (can chay src/dac_trung.py truoc)
Dau ra: reports/eda/h01..h08.png, reports/eda/thong_ke_mo_ta.csv, reports/bao_cao_eda.md
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
from matplotlib.colors import LinearSegmentedColormap
from statsmodels.tsa.seasonal import seasonal_decompose

FEAT = "data/features/dac_trung.csv"
PL = "data/features/phan_loai_sku.csv"
REF = "data/reference"
OUT = "reports/eda"
REPORT = "reports/bao_cao_eda.md"
os.makedirs(OUT, exist_ok=True)

# Bang mau (palette mac dinh da kiem dinh, che do sang)
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e6e5e0"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
BAND = "#f0efec"
DIVERGE = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#f2a27f", "#c4471a"])
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#2a78d6", "#104281"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.titlecolor": INK, "axes.titleweight": "bold", "axes.titlesize": 12,
    "axes.titlelocation": "left", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "lines.linewidth": 1.6, "savefig.dpi": 200, "savefig.bbox": "tight",
})
NOTE = "Dữ liệu mô phỏng, không phải số liệu kho thật."
vn = lambda v, nd=2: f"{v:.{nd}f}".replace(".", ",")   # so thap phan kieu Viet Nam

lines = []
def say(s=""):
    print(s); lines.append(s)

def save(fig, name, caption):
    fig.text(0.0, -0.07, NOTE, fontsize=8, color=MUTED, ha="left", va="top", transform=fig.transFigure)
    fig.savefig(f"{OUT}/{name}"); plt.close(fig)
    say(f"- `{name}`: {caption}")

df = pd.read_csv(FEAT, encoding="utf-8-sig", parse_dates=["date"])
pl = pd.read_csv(PL, encoding="utf-8-sig")
lich = pd.read_csv(f"{REF}/lich_su_kien_prophet.csv", encoding="utf-8-sig", parse_dates=["ds"])
shock = pd.read_csv(f"{REF}/su_kien_dot_bien.csv", encoding="utf-8-sig", parse_dates=["tu_ngay"])
open_ = df[df.la_ngay_nghi == 0]
say("# Bao cao phan tich kham pha (EDA)\n")
say(NOTE + " Hinh luu o `reports/eda/`.\n")
say("## Hinh")

# ---------- h01: tong xuat kho toan kho theo ngay ----------
tot = df.groupby("date").y.sum()
tot_open = tot[df.groupby("date").la_ngay_nghi.max() == 0]
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(tot_open.index, tot_open.values, color="#b7d3f6", linewidth=0.8)
ax.plot(tot_open.rolling(7, center=True).mean(), color=BLUE, linewidth=2)
ymax = tot_open.max()
for r in lich[lich.holiday == "tet"].itertuples():
    ax.axvspan(r.ds + pd.Timedelta(days=r.lower_window), r.ds + pd.Timedelta(days=r.upper_window), color=BAND, zorder=0)
    ax.text(r.ds, ymax * 1.02, f"Tết {r.ds.year}", ha="center", fontsize=8, color=INK2)
yagi = shock.loc[shock.su_kien.str.contains("Yagi"), "tu_ngay"].iloc[0]
ax.axvline(yagi, color=MUTED, linestyle="--", linewidth=1)
ax.text(yagi, ymax * 0.93, " Bão Yagi", fontsize=8, color=INK2)
ax.set_title("Tổng lượng xuất kho theo ngày, toàn kho (121 SKU)")
ax.set_ylabel("Đơn vị / ngày")
ax.text(0.99, 0.02, "Đường đậm: trung bình 7 ngày · Vùng xám: mùa Tết (−28 đến +7 ngày)", transform=ax.transAxes,
        ha="right", fontsize=8, color=INK2)
ax.set_ylim(0, ymax * 1.1)
save(fig, "h01_tong_xuat_theo_ngay.png", "tổng xuất theo ngày (bỏ ngày kho đóng cửa): đỉnh lớn nhất trước Tết, đỉnh phụ tháng 9–10 (Trung thu, khai giảng, bão), Chủ nhật tụt rõ.")

# ---------- h02: 6 SKU dai dien (small multiples) ----------
def pick(cond, n):
    return pl[cond].sort_values("cv_thang_train").ma_sku.head(n).tolist()
reps = [("Nhóm X (ổn định)", s) for s in pick(pl.xyz_train == "X", 2)]
names = df.drop_duplicates("ma_sku").set_index("ma_sku")
for kw in ["Bánh trung thu", "Mứt Tết"]:
    m = names[names.index.isin(pl.ma_sku) & pl.set_index("ma_sku").ten_sku.str.contains(kw).reindex(names.index).fillna(False)]
    if len(m): reps.append((f"Mùa vụ ({kw.lower()})", m.index[0]))
mi = pl[pl.ten_sku.str.contains("Mì gói")].ma_sku.head(1).tolist()
if mi: reps.append(("Hàng tăng khi bão", mi[0]))
lump = pl[pl.loai_nhu_cau.str.startswith("lumpy")].ma_sku.head(1).tolist()
if lump: reps.append(("Bán rời rạc (lumpy)", lump[0]))
fig, axes = plt.subplots(len(reps) // 2 + len(reps) % 2, 2, figsize=(11, 2.4 * ((len(reps) + 1) // 2)), sharex=True)
for ax, (lab, s) in zip(axes.flat, reps):
    ser = df[df.ma_sku == s].set_index("date").y
    ax.plot(ser.index, ser.values, color="#b7d3f6", linewidth=0.6)
    ax.plot(ser.rolling(7, center=True).mean(), color=BLUE, linewidth=1.6)
    ten = pl.set_index("ma_sku").ten_sku[s]
    ax.set_title(f"{lab}: {s} {ten if len(ten) <= 30 else ten[:29] + '…'}", fontsize=9.5)
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylim(bottom=0)
for ax in axes.flat[len(reps):]:
    ax.set_visible(False)
fig.suptitle("Chuỗi nhu cầu của các SKU đại diện (mỗi ô một thang đo riêng)", x=0.0, ha="left", fontweight="bold")
fig.tight_layout()
save(fig, "h02_sku_dai_dien.png", "6 SKU đại diện cho các kiểu nhu cầu: ổn định, mùa vụ dịp lễ, tăng khi bão, rời rạc.")

# ---------- h03: chu ky tuan ----------
wk = open_.copy()
wk["ti_le"] = wk.y / wk.groupby("ma_sku").y.transform("mean")
dow = wk.groupby("thu").ti_le.mean()
labels = {2: "T2", 3: "T3", 4: "T4", 5: "T5", 6: "T6", 7: "T7", 8: "CN"}
fig, ax = plt.subplots(figsize=(7, 3.6))
bars = ax.bar([labels[i] for i in dow.index], dow.values, color=BLUE, width=0.6)
ax.axhline(1, color=MUTED, linewidth=1)
for b, v in zip(bars, dow.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, vn(v), ha="center", fontsize=8.5, color=INK2)
ax.set_title("Chu kỳ tuần: nhu cầu theo thứ so với trung bình (1,0)")
ax.set_ylabel("Hệ số so với TB của SKU")
ax.grid(axis="x", visible=False)
save(fig, "h03_chu_ky_tuan.png", f"thứ Bảy cao nhất ({vn(dow.max())}), Chủ nhật thấp nhất ({vn(dow.min())}) → cần biến thứ trong tuần / chu kỳ 7 ngày.")

# ---------- h04: chi so mua theo nhom hang ----------
mua_order = ["Xuân", "Hạ", "Thu", "Đông"]
si = wk.groupby(["nhom_hang", "mua"]).ti_le.mean().unstack()[mua_order]
si = si.loc[(si.max(axis=1) - si.min(axis=1)).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(7, 0.42 * len(si) + 1.2))
lim = np.log(4)                                             # cat o 0,25 va 4 de 2 phia doi xung
im = ax.imshow(np.log(si.values), cmap=DIVERGE, vmin=-lim, vmax=lim, aspect="auto")
ax.set_xticks(range(4), mua_order); ax.set_yticks(range(len(si)), si.index)
for i in range(si.shape[0]):
    for j in range(4):
        v = si.values[i, j]
        ax.text(j, i, vn(v), ha="center", va="center", fontsize=8.5, color="#ffffff" if abs(np.log(v)) > lim * 0.6 else INK)
ax.grid(False); ax.spines[:].set_visible(False); ax.tick_params(length=0)
ax.set_title("Chỉ số mùa theo nhóm hàng (1,0 = bình thường)")
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
ticks = [0.25, 0.5, 1, 2, 4]
cb.set_ticks(np.log(ticks)); cb.set_ticklabels(["≤0,25", "0,5", "1", "2", "≥4"]); cb.outline.set_visible(False)
save(fig, "h04_chi_so_mua.png", "nhóm hàng xếp theo độ chênh giữa các mùa; cam = bán nhiều hơn TB, xanh = bán ít hơn.")

# ---------- h05: tach xu huong / mua vu (theo tuan, chu ky 52) ----------
# TB moi ngay kho mo cua trong tuan; tuan nghi Tet (kho dong ca 7 ngay) -> noi suy
weekly = tot_open.resample("W-MON").mean().iloc[1:-1].interpolate()
dec = seasonal_decompose(weekly, model="multiplicative", period=52)
fig, axes = plt.subplots(4, 1, figsize=(11, 7.5), sharex=True)
for ax, (ser, t) in zip(axes, [(weekly, "Chuỗi gốc (TB xuất mỗi ngày mở cửa, theo tuần)"), (dec.trend, "Xu hướng (trend)"),
                               (dec.seasonal, "Mùa vụ năm (hệ số)"), (dec.resid, "Phần dư (nhiễu, cú sốc)")]):
    ax.plot(ser.index, ser.values, color=BLUE, linewidth=1.4)
    ax.set_title(t, fontsize=10)
axes[3].axhline(1, color=MUTED, linewidth=1)
fig.suptitle("Phân rã chuỗi tổng xuất theo tuần (nhân tính, chu kỳ 52 tuần)", x=0.0, ha="left", fontweight="bold")
fig.tight_layout()
growth = dec.trend.dropna()
save(fig, "h05_phan_ra_mua_vu.png", f"xu hướng gần như đi ngang (dao động {growth.min():,.0f}–{growth.max():,.0f} đơn vị/ngày, các chỗ lõm do bão và Tết lệch ngày); mùa vụ năm rõ: đỉnh trước Tết, Trung thu, Noel; phần dư lớn ở các tuần Tết (Tết âm lịch đổi ngày mỗi năm) → cần biến ngày lễ, không chỉ chu kỳ 52 tuần.".replace(f"{growth.min():,.0f}", f"{growth.min():,.0f}".replace(",", ".")).replace(f"{growth.max():,.0f}", f"{growth.max():,.0f}".replace(",", ".")))

# ---------- h06: ma tran ABC x XYZ ----------
mt = pd.crosstab(pl.abc_train, pl.xyz_train).reindex(index=["A", "B", "C"], columns=["X", "Y", "Z"], fill_value=0)
fig, ax = plt.subplots(figsize=(4.8, 3.8))
ax.imshow(mt.values, cmap=SEQ, vmin=0, aspect="auto")
for i in range(3):
    for j in range(3):
        v = mt.values[i, j]
        ax.text(j, i, str(v), ha="center", va="center", fontsize=13, fontweight="bold", color="#ffffff" if v > mt.values.max() * 0.5 else INK)
ax.set_xticks(range(3), ["X (ổn định)", "Y", "Z (biến động)"]); ax.set_yticks(range(3), ["A (giá trị cao)", "B", "C"])
ax.grid(False); ax.spines[:].set_visible(False); ax.tick_params(length=0)
ax.set_title("Ma trận ABC × XYZ (số SKU, tính trên tập train)")
save(fig, "h06_ma_tran_abc_xyz.png", f"A-X {mt.loc['A', 'X']} SKU (dễ dự báo, giá trị cao), A-Z {mt.loc['A', 'Z']} SKU (giá trị cao nhưng khó dự báo: ưu tiên mô hình AI).")

# ---------- h07: ADI - CV2 (Syntetos-Boylan) ----------
cats = [("smooth", "Đều (smooth)", BLUE), ("erratic", "Thất thường (erratic)", ORANGE), ("lumpy", "Rời rạc (lumpy)", AQUA)]
fig, ax = plt.subplots(figsize=(7, 4.5))
for key, lab, col in cats:
    s = pl[pl.loai_nhu_cau.str.startswith(key)]
    ax.scatter(s.adi, s.cv2, s=36, color=col, edgecolor=SURFACE, linewidth=1, label=f"{lab}: {len(s)}")
ax.axvline(1.32, color=MUTED, linestyle="--", linewidth=1); ax.axhline(0.49, color=MUTED, linestyle="--", linewidth=1)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: vn(v, 1) if v < 1 else f"{v:g}"))
ax.set_xlabel("ADI: khoảng cách TB giữa 2 ngày có bán (ngày)"); ax.set_ylabel("CV²: độ biến động lượng bán")
ax.legend(frameon=True, facecolor=SURFACE, edgecolor=GRID, loc="center right")
ax.set_title("Phân loại nhu cầu theo Syntetos–Boylan (ngưỡng ADI 1,32 · CV² 0,49)")
save(fig, "h07_adi_cv2.png", "phần lớn SKU bán hằng ngày (ADI < 1,32); nhóm lumpy cần Croston/TSB.")

# ---------- h08: tac dong khuyen mai ----------
base = open_[(open_.het_hang == 0)]
# so sanh trong CUNG thang de loai anh huong mua vu (hang chi ban dip le duoc KM trai mua)
base = base.assign(thang_nam=base.date.dt.to_period("M"))
mm = base.groupby(["ma_sku", "thang_nam", "khuyen_mai"]).y.mean().unstack()
mm = mm[(mm[0] > 0) & mm[1].notna()]
lift = (mm[1] / mm[0]).groupby(level=0).median().dropna()
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.hist(lift, bins=25, color=BLUE, edgecolor=SURFACE, linewidth=1)
ax.axvline(lift.median(), color=INK2, linewidth=1.2)
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True)); ax.set_ylim(top=ax.get_ylim()[1] * 1.12)
ax.text(lift.median(), ax.get_ylim()[1] * 0.97, f"trung vị {vn(lift.median())}  ", fontsize=9, color=INK2, ha="right", va="top")
ax.set_xlabel("Hệ số tăng: TB ngày có KM ÷ TB ngày không KM, trong cùng tháng")
ax.set_ylabel("Số SKU")
ax.set_title("Khuyến mãi làm nhu cầu tăng bao nhiêu (theo từng SKU)")
ax.grid(axis="x", visible=False)
save(fig, "h08_tac_dong_khuyen_mai.png", f"so trong cùng tháng: trung vị khuyến mãi làm bán tăng {(lift.median() - 1) * 100:.0f}% ({(lift < 1).sum()} SKU dưới 1,0); biến khuyến mãi cần có trong mô hình.")

# ---------- Thong ke mo ta theo SKU ----------
st = open_.groupby("ma_sku").y.agg(tb="mean", dlc="std", nho_nhat="min", lon_nhat="max", ty_le_ngay_0=lambda s: (s == 0).mean())
st = st.round(3).join(pl.set_index("ma_sku")[["ten_sku", "abc_train", "xyz_train", "loai_nhu_cau"]])
st.to_csv(f"{OUT}/thong_ke_mo_ta.csv", encoding="utf-8-sig")
say("\n## Thong ke mo ta")
say(f"- `thong_ke_mo_ta.csv`: TB, do lech chuan, min, max, ty le ngay ban 0 cua tung SKU (ngay kho mo cua).")
say(f"- TB xuat/ngay moi SKU: tu {st.tb.min():.1f} den {st.tb.max():.1f}; ty le ngay ban 0 cao nhat: {st.ty_le_ngay_0.max() * 100:.1f}%")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
