"""Bieu do ket qua cho Chuong 4 (GD E va GD F). DOC TU CO SO DU LIEU.
Chay: python src/nap_database.py && python src/ton_kho.py && python src/bieu_do_ket_qua.py
Dau ra: reports/ket_qua/k01..k07.png (k07 can chay src/do_nhay.py truoc), reports/bao_cao_bieu_do_ket_qua.md
Mau co dinh theo doi tuong (giong nhau o moi hinh): thuc te = den, AI duoc chon = xanh duong,
du bao moc (TB truot 28) = cam, Prophet = xanh ngoc, LightGBM = vang, hien trang = xam.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from kiem_tra_du_lieu import cac_moc_o_giua, nguon_du_lieu  # noqa: E402
from csdl import doc, ma_vi_du, ngay_su_kien  # noqa: E402

OUT = "reports/ket_qua"
REPORT = "reports/bao_cao_bieu_do_ket_qua.md"
os.makedirs(OUT, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e6e5e0"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
BAND = "#f0efec"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.titlecolor": INK, "axes.titleweight": "bold", "axes.titlesize": 12,
    "axes.titlelocation": "left", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "lines.linewidth": 1.8, "savefig.dpi": 200, "savefig.bbox": "tight", "legend.frameon": False,
})
NOTE = nguon_du_lieu()["ghi_chu"]
SO_MA = doc("SELECT COUNT(*) AS n FROM dm_sku").n.iloc[0]
TET_KY = [x for x in ngay_su_kien("tet") if doc("SELECT MIN(ngay) a, MAX(ngay) b FROM mo_phong_ngay").a.iloc[0] <= x <= doc("SELECT MAX(ngay) b FROM mo_phong_ngay").b.iloc[0]]
vn = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
CHON = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]
MOC = "tb_truot_28_tuan"     # du bao moc, cap nhat moi tuan nhu mo hinh duoc chon (docs/10 muc 9.6)
TEN = {CHON: "AI (kết hợp, cập nhật mỗi tuần, được chọn)", "ket_hop_v3": "AI v3 (cập nhật mỗi 28 ngày)", "lightgbm": "LightGBM",
       "lstm_tuan": "LSTM (không được chọn)", "rnn_tuan": "RNN (không được chọn)", "prophet": "Prophet", MOC: "TB trượt 28 ngày, cập nhật mỗi tuần (mốc)", "tb_truot_28": "TB trượt 28 ngày, mỗi 28 ngày",
       "seasonal_naive_7": "Seasonal Naive", "croston_sba": "Croston SBA", "tsb": "TSB", "ets": "ETS", "naive": "Naive"}
MAU = {CHON: BLUE, "ket_hop_v3": "#86b6ef", MOC: ORANGE, "tb_truot_28": "#f2b48f", "prophet": AQUA, "lightgbm": YELLOW}
CS_TEN = {"hien_trang": "Hiện trạng*", "cong_thuc_du_bao_moc": "Công thức + dự báo mốc",
          "cong_thuc_du_bao_ai": "Công thức + dự báo AI", "cong_thuc_du_bao_ai_hc": "AI + hiệu chỉnh lệch"}
CS_MAU = {"hien_trang": MUTED, "cong_thuc_du_bao_moc": ORANGE, "cong_thuc_du_bao_ai": "#86b6ef", "cong_thuc_du_bao_ai_hc": BLUE}

lines = []
def save(fig, name, caption, note=NOTE):
    fig.text(0.0, -0.06, note, fontsize=8, color=MUTED, ha="left", va="top", transform=fig.transFigure)
    fig.savefig(f"{OUT}/{name}"); plt.close(fig)
    lines.append(f"- `{name}`: {caption}")
    print(name)


# ---------- k01: xep hang mo hinh (WMAPE tap test) ----------
r = doc("""SELECT k.ma_mo_hinh, k.wmape, k.bias_pct FROM ket_qua_mo_hinh k JOIN mo_hinh m USING (ma_mo_hinh)
           WHERE k.tap = 'test' AND m.pham_vi LIKE 'Toan bo%' AND k.ma_mo_hinh IN ({})""".format(
        ",".join(f"'{m}'" for m in TEN)))
r = r.sort_values("wmape", ascending=True)
fig, ax = plt.subplots(figsize=(8, 4.2))
cols = [MAU.get(m, "#b7d3f6") for m in r.ma_mo_hinh]
bars = ax.barh([TEN[m] for m in r.ma_mo_hinh], r.wmape * 100, color=cols, height=0.62)
for b, v in zip(bars, r.wmape * 100):
    ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{vn(v)}%", va="center", fontsize=9, color=INK2)
ax.invert_yaxis(); ax.grid(axis="y", visible=False)
ax.set_xlabel("WMAPE trên tập test (%, thấp hơn là tốt hơn)")
ax.set_title("Sai số dự báo theo ngày của các mô hình (tập test)")
w_ = lambda m: vn(r[r.ma_mo_hinh == m].wmape.iloc[0] * 100)
save(fig, "k01_xep_hang_mo_hinh.png",
     f"AI được chọn (cập nhật mỗi tuần) sai {w_(CHON)}% (cùng mô hình cập nhật mỗi 28 ngày: {w_('ket_hop_v3')}%); "
     f"mốc TB trượt 28 ngày cập nhật mỗi tuần {w_(MOC)}% (mỗi 28 ngày: {w_('tb_truot_28')}%); Seasonal Naive {w_('seasonal_naive_7')}%. "
     "Hai mô hình cập nhật mỗi tuần chấm trên bản mới nhất cho mỗi ngày (cách dùng thật); các mô hình khác chấm trên mốc 28 ngày "
     "× 28 ngày.")

# ---------- k02: du bao vs thuc te quanh Tet 2026 va Trung thu 2026 (tong toan kho) ----------
def tong_moc(moc, models):
    d = doc(f"""SELECT ma_mo_hinh, ngay, SUM(du_bao) AS du_bao, SUM(thuc_te) AS thuc_te, COUNT(thuc_te) AS n
                FROM du_bao WHERE tap = 'test' AND moc = ? AND ma_mo_hinh IN ({",".join("?" * len(models))})
                GROUP BY ma_mo_hinh, ngay""", (moc, *models))
    d["ngay"] = pd.to_datetime(d.ngay)
    return d
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=False)
cac_moc = doc("SELECT DISTINCT moc FROM du_bao WHERE tap = 'test' AND ma_mo_hinh = ? ORDER BY moc", (CHON,)).moc.tolist()
dinh_k02 = []
for ax, (moc_ts, loai) in zip(axes, cac_moc_o_giua(cac_moc, {"Tết": ngay_su_kien("tet"), "Trung thu": ngay_su_kien("trung_thu")})):
    moc = moc_ts.strftime("%Y-%m-%d")
    ten = f"Mốc {moc_ts:%d/%m/%Y}" + (f" (trước {loai})" if loai else "")
    models = [CHON, MOC]
    d = tong_moc(moc, models)
    a = d[d.ma_mo_hinh == CHON].sort_values("ngay")
    act = a.thuc_te.where(a.n >= np.ceil(SO_MA * 100 / 121))   # chi ve ngay du ma co nhu cau tin duoc
    ax.plot(a.ngay, act, color=INK, linewidth=2.2, label="Thực tế (nhu cầu tin được)")
    for m in models:
        x = d[d.ma_mo_hinh == m].sort_values("ngay")
        ax.plot(x.ngay, x.du_bao, color=MAU[m], label=TEN[m], linestyle="-" if m == CHON else "--")
    ax.set_title(ten, fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m")); ax.set_ylim(bottom=0)
    ax.set_ylabel(f"Tổng {SO_MA} SKU (đơn vị/ngày)")
    dinh_k02.append(f"{ten}: đỉnh thực tế {vn(act.max(), 0)}, đỉnh dự báo AI {vn(a.du_bao.max(), 0)}, đỉnh mốc {vn(d[d.ma_mo_hinh == MOC].du_bao.max(), 0)}")
axes[0].legend(loc="upper left", fontsize=9)
fig.suptitle("Dự báo 28 ngày tới so với thực tế, tổng toàn kho", x=0.0, ha="left", fontweight="bold")
fig.tight_layout()
save(fig, "k02_du_bao_vs_thuc_te_tet.png", "; ".join(dinh_k02) + ". Ngày thiếu dữ liệu tin được (kho đóng cửa) để trống.")

# ---------- k03: WMAPE theo nhom XYZ ----------
g = doc(f"""SELECT ma_mo_hinh, wmape_x, wmape_y, wmape_z FROM ket_qua_mo_hinh
            WHERE tap = 'test' AND ma_mo_hinh IN ('{CHON}', 'prophet', 'lightgbm', '{MOC}')""").set_index("ma_mo_hinh")
order = [MOC, "prophet", "lightgbm", CHON]
fig, ax = plt.subplots(figsize=(8, 4))
x = np.arange(3); w = 0.2
for k, m in enumerate(order):
    vals = g.loc[m, ["wmape_x", "wmape_y", "wmape_z"]].values * 100
    bs = ax.bar(x + (k - 1.5) * w, vals, width=w - 0.02, color=MAU[m], label=TEN[m])
    if m in (CHON, MOC):
        for b, v in zip(bs, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{vn(v, 0)}", ha="center", fontsize=8, color=INK2)
ax.set_xticks(x, ["X (ổn định)", "Y", "Z (mùa vụ)"]); ax.grid(axis="x", visible=False)
ax.set_ylabel("WMAPE (%)"); ax.legend(fontsize=9, loc="upper left")
ax.set_title("Sai số dự báo theo nhóm hàng (tập test)")
save(fig, "k03_sai_so_theo_nhom.png", f"Lợi ích lớn nhất của AI ở nhóm mùa vụ Z (TB trượt {vn(g.loc[MOC, 'wmape_z'] * 100, 0)}% → "
     f"AI {vn(g.loc[CHON, 'wmape_z'] * 100, 0)}%); nhóm ổn định X chênh ít hơn ({vn(g.loc[MOC, 'wmape_x'] * 100, 0)}% → "
     f"{vn(g.loc[CHON, 'wmape_x'] * 100, 0)}%).")

# ---------- k04: tong gia tri ton kho theo ngay, 4 chinh sach ----------
t = doc("""SELECT m.ma_chinh_sach, m.ngay, SUM(m.ton_cuoi * s.gia_von) / 1e9 AS ty
           FROM mo_phong_ngay m JOIN dm_sku s USING (ma_sku) GROUP BY 1, 2""")
t["ngay"] = pd.to_datetime(t.ngay)
fig, ax = plt.subplots(figsize=(11, 4.2))
for cs in ["hien_trang", "cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]:
    x = t[t.ma_chinh_sach == cs].sort_values("ngay")
    ax.plot(x.ngay, x.ty, color=CS_MAU[cs], label=CS_TEN[cs], linewidth=2.2 if cs == "cong_thuc_du_bao_ai_hc" else 1.5)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
ax.set_ylabel("Giá trị tồn kho (tỷ đ)"); ax.set_ylim(bottom=0); ax.legend(fontsize=9, ncol=2, loc="upper left")
ax.set_title("Giá trị tồn kho cuối ngày theo chính sách (mô phỏng 12 tháng test, mức phục vụ 95%)")
save(fig, "k04_ton_kho_theo_thoi_gian.png", "Tồn kho theo thời gian của 4 chính sách" + ("; các đỉnh trước Tết là hàng chuẩn bị cho mùa cao điểm." if TET_KY else "."),
     NOTE + " *Hiện trạng: người lập kế hoạch trong dữ liệu biết trước nhu cầu kỳ vọng (lệch ±10%).")

# ---------- k05: bang truoc - sau (2 o: fill rate, chi phi lien quan) ----------
v = doc("SELECT * FROM v_so_sanh_chinh_sach WHERE muc_phuc_vu = 0.95").set_index("ma_chinh_sach")
order = ["hien_trang", "cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, col, ten, fmt in [(axes[0], "fill_rate_pt", "Tỷ lệ đáp ứng (Fill Rate, %)", lambda x: f"{vn(x, 1)}%"),
                          (axes[1], "chi_phi_lien_quan_trieu", "Chi phí liên quan (tỷ đ)", lambda x: vn(x / 1000, 2))]:
    vals = v.loc[order, col].values
    bs = ax.bar([CS_TEN[c] for c in order], vals, color=[CS_MAU[c] for c in order], width=0.6)
    for b, val in zip(bs, vals):
        ax.text(b.get_x() + b.get_width() / 2, val * 1.01, fmt(val), ha="center", va="bottom", fontsize=9, color=INK2)
    ax.set_title(ten, fontsize=11); ax.grid(axis="x", visible=False)
    ax.tick_params(axis="x", labelsize=8.5, rotation=12)
axes[0].set_ylim(80, 100); axes[0].axhline(95, color=MUTED, linestyle="--", linewidth=1)
axes[0].text(-0.45, 95.3, "mục tiêu 95%", fontsize=8, color=MUTED, ha="left", va="bottom")
axes[1].set_yticks(axes[1].get_yticks(), [vn(y / 1000, 0) for y in axes[1].get_yticks()])
fig.suptitle("Trước – sau: so sánh chính sách đặt hàng (12 tháng test, mức phục vụ 95%)", x=0.0, ha="left", fontweight="bold")
fig.tight_layout()
save(fig, "k05_truoc_sau.png", f"Chi phí liên quan = đặt hàng + lưu kho + lợi nhuận mất do thiếu hàng. Cùng công thức, AI giảm "
     f"{vn((1 - v.loc['cong_thuc_du_bao_ai_hc', 'chi_phi_lien_quan_trieu'] / v.loc['cong_thuc_du_bao_moc', 'chi_phi_lien_quan_trieu']) * 100, 0)}% so với dự báo mốc.",
     NOTE + " *Hiện trạng: người lập kế hoạch trong dữ liệu biết trước nhu cầu kỳ vọng (lệch ±10%), mạnh hơn thực tế.")

# ---------- k06: "rang cua" ton kho 1 SKU (mi goi) duoi chinh sach AI ----------
MA_VD = ma_vi_du()
ky = doc("SELECT MIN(ngay) a, MAX(ngay) b FROM mo_phong_ngay").iloc[0]
tam = pd.Timestamp(TET_KY[0]) if TET_KY else pd.Timestamp(ky.a) + (pd.Timestamp(ky.b) - pd.Timestamp(ky.a)) / 2
s = doc("""SELECT ngay, ton_cuoi, rop, dat_hang, nhap, nhu_cau FROM mo_phong_ngay
           WHERE ma_chinh_sach = 'cong_thuc_du_bao_ai_hc' AND ma_sku = ? AND ngay BETWEEN ? AND ?""",
        (MA_VD, (tam - pd.Timedelta(days=78)).strftime("%Y-%m-%d"), (tam + pd.Timedelta(days=42)).strftime("%Y-%m-%d")))
s["ngay"] = pd.to_datetime(s.ngay)
ten_sku, don_vi = doc("SELECT ten_sku, don_vi FROM dm_sku WHERE ma_sku = ?", (MA_VD,)).iloc[0]
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(s.ngay, s.ton_cuoi, color=BLUE, linewidth=1.8, label="Tồn cuối ngày", drawstyle="steps-post")
ax.plot(s.ngay, s.rop, color=ORANGE, linewidth=1.4, linestyle="--", label="Điểm đặt hàng (ROP)")
od = s[s.dat_hang > 0]
ax.scatter(od.ngay, od.ton_cuoi, s=36, color=INK, zorder=3, label="Ngày đặt hàng")
rc = s[s.nhap > 0]
ax.scatter(rc.ngay, rc.ton_cuoi, s=36, marker="^", color=AQUA, edgecolor=SURFACE, zorder=3, label="Hàng về")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m")); ax.set_ylim(bottom=0)
ax.set_ylabel(f"Đơn vị ({don_vi})"); ax.legend(fontsize=9, ncol=4, loc="upper left")
ax.set_title(f"Mô hình răng cưa: tồn kho, điểm đặt hàng và các lần đặt – {MA_VD} {ten_sku} (AI + hiệu chỉnh)")
save(fig, "k06_rang_cua_sku001.png", "Mỗi khi tồn + hàng đang về chạm ROP thì đặt hàng" + ("; ROP tăng trước Tết theo dự báo." if TET_KY else ".") + " Minh họa thực tế cho lý thuyết EOQ/ROP ở Chương 2.")

# ---------- k07: thu do nhay - tac cang va lead time dai them (can chay src/do_nhay.py truoc) ----------
try:
    dn = doc("SELECT * FROM v_do_nhay")
except Exception:
    dn = pd.DataFrame()
if len(dn):
    order = ["cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    for cs in order:
        goc = dn[(dn.ma_kich_ban == "goc") & (dn.ma_chinh_sach == cs)].fill_rate_pt.iloc[0]
        tc = dn[(dn.nhom == "tac_cang") & (dn.ma_chinh_sach == cs)].groupby("tham_so").fill_rate_pt.agg(["mean", "min", "max"])
        k = np.r_[0, tc.index.values]
        ax.fill_between(k, np.r_[goc, tc["min"]], np.r_[goc, tc["max"]], color=CS_MAU[cs], alpha=0.15, linewidth=0)
        ax.plot(k, np.r_[goc, tc["mean"]], color=CS_MAU[cs], marker="o", label=CS_TEN[cs])
        ax.text(k[-1] + 0.15, tc["mean"].iloc[-1], f"{vn(tc['mean'].iloc[-1])}%", va="center", fontsize=8.5, color=INK2)
    ax.set_xticks([0, 3, 5, 7], ["Không tắc", "+3 ngày", "+5 ngày", "+7 ngày"]); ax.set_xlim(-0.3, 7.9)
    ax.set_ylabel("Fill Rate (%)"); ax.legend(fontsize=9, loc="lower left")
    ax.set_title("Tắc cảng 3 tuần, hàng về trễ thêm\n(trung bình 13 đợt; dải màu: đợt tốt nhất – xấu nhất)", fontsize=10.5)
    ax = axes[1]
    kb = [("goc", "Bình thường"), ("lead_time_2", "LT +2 ngày,\nkhông cập nhật"), ("lead_time_2_cap_nhat", "LT +2 ngày,\ncó cập nhật")]
    x = np.arange(len(kb)); w = 0.26
    for j, cs in enumerate(order):
        vals = [dn[(dn.ma_kich_ban == m) & (dn.ma_chinh_sach == cs)].fill_rate_pt.iloc[0] for m, _ in kb]
        bs = ax.bar(x + (j - 1) * w, vals, width=w - 0.03, color=CS_MAU[cs])
        if cs == "cong_thuc_du_bao_ai_hc":
            for b, val in zip(bs, vals):
                ax.text(b.get_x() + b.get_width() / 2, val + 0.3, f"{vn(val)}%", ha="center", fontsize=8.5, color=INK2)
    ax.set_xticks(x, [t for _, t in kb], fontsize=9); ax.set_ylim(80, 100); ax.grid(axis="x", visible=False)
    ax.set_title("Lead time dài thêm 2 ngày cả năm\n(công thức có / không cập nhật lead time mới)", fontsize=10.5)
    ax.set_ylabel("Fill Rate (%)")
    fig.suptitle("Thử độ nhạy: chính sách tồn kho khi hàng về trễ (mức phục vụ 95%)", x=0.0, ha="left", fontweight="bold")
    fig.tight_layout()
    ai_ = dn[dn.ma_chinh_sach == "cong_thuc_du_bao_ai_hc"]
    goc_ = ai_[ai_.ma_kich_ban == "goc"].fill_rate_pt.iloc[0]
    giam_ = goc_ - ai_[ai_.nhom == "tac_cang"].groupby("tham_so").fill_rate_pt.mean()
    tc_ = dn[dn.nhom == "tac_cang"]
    re_ = tc_.loc[tc_.groupby("ma_kich_ban").chi_phi_lien_quan_trieu.idxmin()]
    so_re, so_dot = re_.ma_chinh_sach.isin(["cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]).sum(), len(re_)
    lt_ = lambda m: vn(goc_ - ai_[ai_.ma_kich_ban == m].fill_rate_pt.iloc[0])
    save(fig, "k07_do_nhay_lead_time.png", f"Tắc cảng tạm thời làm Fill Rate giảm {vn(giam_.min())}–{vn(giam_.max())} điểm; chính sách dùng dự báo AI rẻ nhất ở {so_re}/{so_dot} lần thử; "
         f"lead time dài ra lâu dài không cập nhật công thức thì giảm {lt_('lead_time_2')} điểm, có cập nhật thì giảm {lt_('lead_time_2_cap_nhat')} điểm.",
         NOTE + " Kịch bản theo docs/07; người lập kế hoạch không biết trước đợt tắc cảng.")
else:
    print("Bo qua k07: chua co ket qua do nhay (chay python src/do_nhay.py)")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("# Bieu do ket qua (Chuong 4)\n\n" + NOTE + " Hinh luu o `reports/ket_qua/`.\n\n" + "\n".join(lines) + "\n")
