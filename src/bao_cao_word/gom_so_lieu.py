"""Gom so lieu cho bao cao Word tu CSDL va file ket qua (khong ghi so theo tri nho). Chay tai thu muc goc du an."""
import json
import sys
sys.path.insert(0, "src")
import pandas as pd
from csdl import doc, TRANG_THAI, trang_thai_ton_kho

vn = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
out = {}
n = doc("""SELECT (SELECT COUNT(*) FROM dm_sku) sku, (SELECT COUNT(DISTINCT nhom_hang) FROM dm_sku) nhom,
                  (SELECT COUNT(*) FROM giao_dich_sach) dong, (SELECT COUNT(DISTINCT ngay) FROM giao_dich_sach) ngay,
                  (SELECT COUNT(*) FROM giao_dich_tho) tho, (SELECT COUNT(*) FROM nhat_ky_sua_loi) sua,
                  (SELECT AVG(het_hang) FROM giao_dich_sach WHERE la_ngay_nghi = 0) het,
                  (SELECT COUNT(*) FROM dm_nha_cung_cap) ncc, (SELECT COUNT(*) FROM lich_khuyen_mai) km,
                  (SELECT COUNT(*) FROM su_kien_dot_bien) sk, (SELECT COUNT(*) FROM lich_su_kien) le""").iloc[0]
out["du_lieu"] = {k: (float(v) if k == "het" else int(v)) for k, v in n.items()}
loi = doc("SELECT loai_loi, COUNT(*) n FROM nhat_ky_sua_loi GROUP BY 1 ORDER BY 2 DESC")
out["loi"] = loi.values.tolist()
ab = doc("SELECT abc_train a, xyz_train x, COUNT(*) n FROM phan_loai_sku GROUP BY 1, 2")
out["abcxyz"] = ab.values.tolist()
r = doc("SELECT * FROM ket_qua_mo_hinh").set_index(["ma_mo_hinh", "tap"])
def m(mh, tap="test"):
    x = r.loc[(mh, tap)]
    return {c: (None if pd.isna(x[c]) else float(x[c])) for c in ["wmape", "wmape_tuan", "bias_pct", "wmape_x", "wmape_y", "wmape_z", "wmape_a"]}
out["mo_hinh"] = {mh: m(mh) for mh in ["naive", "seasonal_naive_7", "tb_truot_28", "tb_truot_28_tuan", "ets", "croston_sba", "tsb", "arima",
                                       "prophet", "lightgbm", "ket_hop_theo_nhom_v2", "ket_hop_v3", "ket_hop_v4"]}
out["mo_hinh_val2"] = {mh: m(mh, "validation2") for mh in ["ket_hop_v3", "ket_hop_v4", "tb_truot_28_tuan"]}
v4 = json.load(open("reports/nang_cap_du_bao_v4_trang_thai.json", encoding="utf-8"))
out["v4"] = v4
v = doc("SELECT * FROM v_so_sanh_chinh_sach").assign(m=lambda f: f.muc_phuc_vu.round(2))
out["ton_kho"] = v[v.m == 0.95].set_index("ma_chinh_sach")[["fill_rate_pt", "so_ngay_sku_thieu", "ton_tb_trieu_vnd", "so_lan_nhap",
                                                            "tong_chi_phi_trieu", "loi_nhuan_mat_trieu", "chi_phi_lien_quan_trieu"]].to_dict("index")
out["muc_phuc_vu"] = v[v.ma_chinh_sach == "cong_thuc_du_bao_ai_hc"][["m", "fill_rate_pt", "chi_phi_lien_quan_trieu"]].values.tolist()
g = doc("""SELECT p.xyz_train x, k.ma_chinh_sach cs, 100.0*SUM(da_dap_ung)/SUM(nhu_cau) fr, SUM(gia_tri_ton_tb)/1e6 ton,
                  SUM(loi_nhuan_mat)/1e6 ln FROM ket_qua_ton_kho k JOIN phan_loai_sku p USING(ma_sku)
           WHERE ROUND(muc_phuc_vu,2)=0.95 GROUP BY 1,2""")
out["nhom"] = g.values.tolist()
qt = open("reports/ton_kho_chon_quy_tac.md", encoding="utf-8").read().splitlines()
out["quy_tac_md"] = [l for l in qt if l.startswith("|")]
dn = doc("SELECT * FROM v_do_nhay")
ai = dn[dn.ma_chinh_sach == "cong_thuc_du_bao_ai_hc"]
goc = ai[ai.nhom == "goc"].iloc[0]
rows = [["Gốc", goc.fill_rate_pt, 0.0, goc.chi_phi_lien_quan_trieu, 0.0]]
for k_ in [3, 5, 7]:
    y = ai[(ai.nhom == "tac_cang") & (ai.tham_so == k_)]
    rows.append([f"Tắc cảng, trễ +{k_} ngày (TB 13 đợt)", y.fill_rate_pt.mean(), y.fill_rate_pt.mean() - goc.fill_rate_pt,
                 y.chi_phi_lien_quan_trieu.mean(), 100 * (y.chi_phi_lien_quan_trieu.mean() / goc.chi_phi_lien_quan_trieu - 1)])
w = ai[(ai.nhom == "tac_cang") & (ai.tham_so == 7)].sort_values("fill_rate_pt").iloc[0]
rows.append(["Tắc cảng +7 ngày, đợt xấu nhất (trước Tết)", w.fill_rate_pt, w.fill_rate_pt - goc.fill_rate_pt, w.chi_phi_lien_quan_trieu,
             100 * (w.chi_phi_lien_quan_trieu / goc.chi_phi_lien_quan_trieu - 1)])
for mm, ten in [("lead_time_2", "Lead time +2 ngày, không cập nhật công thức"), ("lead_time_2_cap_nhat", "Lead time +2 ngày, có cập nhật"),
                ("chi_phi_dat_120", "Chi phí đặt hàng +20%"), ("chi_phi_luu_115", "Chi phí lưu kho +15%")]:
    y = ai[ai.ma_kich_ban == mm].iloc[0]
    rows.append([ten, y.fill_rate_pt, y.fill_rate_pt - goc.fill_rate_pt, y.chi_phi_lien_quan_trieu,
                 100 * (y.chi_phi_lien_quan_trieu / goc.chi_phi_lien_quan_trieu - 1)])
out["do_nhay"] = [[a, float(b), float(c), float(d), float(e)] for a, b, c, d, e in rows]
mp = doc("SELECT * FROM mo_phong_ngay WHERE ma_chinh_sach='cong_thuc_du_bao_ai_hc' AND ngay='2026-02-09'")
out["canh_bao_0902"] = trang_thai_ton_kho(mp).value_counts().reindex(TRANG_THAI).fillna(0).astype(int).to_dict()
out["rui_ro"] = pd.read_csv("reports/rui_ro_du_bao.csv", encoding="utf-8-sig").fillna("").to_dict("records")
out["bang"] = doc("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'").values.tolist()
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print("ok", list(out))
