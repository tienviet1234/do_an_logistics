"""Doi chieu so lieu vong 4 (01/11) ghi trong tai lieu voi CSDL / file ket qua."""
import json
import sys
sys.path.insert(0, "src")
import pandas as pd
from csdl import doc, TRANG_THAI, trang_thai_ton_kho, hang_dang_ve

loi = []


def kiem(ten, thuc, ghi, sai=0.051):
    ok = abs(float(thuc) - ghi) <= sai
    print(f"{'OK ' if ok else 'SAI'} {ten}: tai lieu {ghi} | du lieu {round(float(thuc), 4)}")
    if not ok:
        loi.append(ten)


m = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]
print("Mo hinh chon:", m); loi += [] if m == "ket_hop_v4" else ["mo hinh chon"]
k = doc("SELECT * FROM ket_qua_mo_hinh WHERE tap = 'test'").set_index("ma_mo_hinh")
kiem("v4 WMAPE", k.wmape["ket_hop_v4"], 0.356, 0.0005); kiem("v4 Bias %", 100 * k.bias_pct["ket_hop_v4"], 3.0)
kiem("v4 tuan", k.wmape_tuan["ket_hop_v4"], 0.203, 0.0005); kiem("v4 Z", k.wmape_z["ket_hop_v4"], 0.477, 0.0005)
kiem("v3 WMAPE", k.wmape["ket_hop_v3"], 0.368, 0.0005); kiem("moc tuan", k.wmape["tb_truot_28_tuan"], 0.584, 0.0005)
kiem("moc 28", k.wmape["tb_truot_28"], 0.640, 0.0005)
st = json.load(open("reports/nang_cap_du_bao_v4_trang_thai.json", encoding="utf-8"))["test"]
kiem("lead time v4", st["test"]["v4"]["lead_time"], 0.214, 0.0005); kiem("lead time v3", st["test_cung_dong"]["v3_lead_time"], 0.233, 0.0005)
kh = st["khoang"]
for ten, g, a, b in [("ngay", "theo_ngay", 80.9, 96.0), ("lead time", "lead_time", 81.3, 95.5)]:
    kiem(f"phu 80 {ten}", kh[g]["80"]["phu"], a); kiem(f"phu 95 {ten}", kh[g]["95"]["phu"], b)

v = doc("SELECT * FROM v_so_sanh_chinh_sach WHERE ROUND(muc_phuc_vu,2)=0.95").set_index("ma_chinh_sach")
cot = ["fill_rate_pt", "so_ngay_sku_thieu", "ton_tb_trieu_vnd", "so_lan_nhap", "tong_chi_phi_trieu", "loi_nhuan_mat_trieu", "chi_phi_lien_quan_trieu"]
for cs, vals in {"hien_trang": (93.57, 1564, 11993.6, 1910, 2766.8, 3693.3, 6460.1),
                 "cong_thuc_du_bao_moc": (91.69, 916, 19669.7, 3575, 4567.0, 4444.0, 9011.0),
                 "cong_thuc_du_bao_ai": (95.33, 793, 9208.7, 3467, 2427.4, 2902.2, 5329.6),
                 "cong_thuc_du_bao_ai_hc": (95.82, 735, 11906.0, 3192, 2915.7, 2912.4, 5828.1)}.items():
    for c, g in zip(cot, vals):
        kiem(f"{cs} {c}", v.loc[cs, c], g, 0.006 if c == "fill_rate_pt" else 0.06)
a, b, h = v.loc["cong_thuc_du_bao_ai_hc"], v.loc["cong_thuc_du_bao_moc"], v.loc["hien_trang"]
pc = lambda x, y: 100 * (x / y - 1)
kiem("CPLQ vs moc", pc(a.chi_phi_lien_quan_trieu, b.chi_phi_lien_quan_trieu), -35.3)
kiem("CPLQ vs HT", pc(a.chi_phi_lien_quan_trieu, h.chi_phi_lien_quan_trieu), -9.8)
kiem("ton vs HT", pc(a.ton_tb_trieu_vnd, h.ton_tb_trieu_vnd), -0.7)
kiem("ton vs moc", pc(a.ton_tb_trieu_vnd, b.ton_tb_trieu_vnd), -39.5)
kiem("thieu vs HT", pc(a.so_ngay_sku_thieu, h.so_ngay_sku_thieu), -53, 0.5)
kiem("nhap vs HT", pc(a.so_lan_nhap, h.so_lan_nhap), 67, 0.5)
kiem("ton vs v3", pc(a.ton_tb_trieu_vnd, 16377.3), -27, 0.5); kiem("CPLQ vs v3", pc(a.chi_phi_lien_quan_trieu, 6672.7), -12.7)
lv = doc("SELECT ROUND(muc_phuc_vu,2) m, chi_phi_lien_quan_trieu c FROM v_so_sanh_chinh_sach WHERE ma_chinh_sach='cong_thuc_du_bao_ai_hc'").set_index("m").c
for m_, c_ in [(0.9, 5994.2), (0.95, 5828.1), (0.99, 5376.2)]:
    kiem(f"CPLQ muc {m_}", lv[m_], c_)
g = doc("SELECT p.xyz_train x, k.ma_chinh_sach cs, SUM(k.gia_tri_ton_tb)/1e6 t FROM ket_qua_ton_kho k JOIN phan_loai_sku p USING(ma_sku) "
        "WHERE ROUND(muc_phuc_vu,2)=0.95 GROUP BY 1,2").set_index(["x", "cs"]).t
kiem("X ton vs HT", pc(g[("X", "cong_thuc_du_bao_ai_hc")], g[("X", "hien_trang")]), -29, 0.5)
kiem("Z ton AI hc", g[("Z", "cong_thuc_du_bao_ai_hc")], 7730.3, 0.06); kiem("Z ton moc", g[("Z", "cong_thuc_du_bao_moc")], 14838.2, 0.06)
q = doc("SELECT quy_tac_luong_dat FROM chinh_sach WHERE ma_chinh_sach='cong_thuc_du_bao_ai_hc'").iloc[0, 0]
print("Quy tac:", q); loi += [] if q == "lai" else ["quy tac"]
qt = open("reports/ton_kho_chon_quy_tac.md", encoding="utf-8").read()
for so in ["4054.95", "4361.59", "4448.44", "4537.87", "4715.61", "4984.6"]:
    if so not in qt:
        loi.append("quy tac validation2 " + so); print("SAI quy tac", so)

dn = doc("SELECT * FROM v_do_nhay"); ai = dn[dn.ma_chinh_sach == "cong_thuc_du_bao_ai_hc"]
goc = ai[ai.nhom == "goc"].iloc[0]
kiem("goc FR", goc.fill_rate_pt, 95.82, 0.006); kiem("goc CP", goc.chi_phi_lien_quan_trieu, 5828.1)
for kk, fr, cp in [(3, 95.33, 6168.8), (5, 94.84, 6510.2), (7, 94.30, 6859.2)]:
    y = ai[(ai.nhom == "tac_cang") & (ai.tham_so == kk)]
    kiem(f"tac cang +{kk} FR", y.fill_rate_pt.mean(), fr, 0.006); kiem(f"tac cang +{kk} CP", y.chi_phi_lien_quan_trieu.mean(), cp, 0.06)
w = ai[(ai.nhom == "tac_cang") & (ai.tham_so == 7)].sort_values("fill_rate_pt").iloc[0]
kiem("xau nhat FR", w.fill_rate_pt, 93.32, 0.006); kiem("xau nhat CP", w.chi_phi_lien_quan_trieu, 7184.4)
for mm, fr, cp in [("lead_time_2", 90.76, 9250.4), ("lead_time_2_cap_nhat", 95.39, 6044.2), ("chi_phi_dat_120", 95.92, 5821.2), ("chi_phi_luu_115", 95.91, 6076.2)]:
    y = ai[ai.ma_kich_ban == mm].iloc[0]; kiem(f"{mm} FR", y.fill_rate_pt, fr, 0.006); kiem(f"{mm} CP", y.chi_phi_lien_quan_trieu, cp)
c = dn[dn.nhom == "tac_cang"]; rr = c.loc[c.groupby("ma_kich_ban").chi_phi_lien_quan_trieu.idxmin()]
kiem("AI re nhat /39", rr.ma_chinh_sach.isin(["cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]).sum(), 39, 0)

mp = doc("SELECT * FROM mo_phong_ngay WHERE ma_chinh_sach='cong_thuc_du_bao_ai_hc' AND ngay='2026-02-09'")
dem = trang_thai_ton_kho(mp).value_counts()
for s_, n in zip(TRANG_THAI, [0, 8, 44, 69]):
    kiem(f"09/02 {s_}", dem.get(s_, 0), n, 0)
print("\nKET LUAN:", "TAT CA KHOP" if not loi else f"{len(loi)} cho LECH: {loi}")
sys.exit(1 if loi else 0)
