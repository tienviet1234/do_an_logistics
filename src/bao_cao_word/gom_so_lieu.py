"""Gom so lieu cho bao cao Word tu CSDL va file ket qua (khong ghi so theo tri nho). Chay tai thu muc goc du an."""
import json
import os
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
# ---------------------------------------------------------------- phan logistics bo sung va kiem chung (doc tep ket qua, thieu tep thi None)
def doc_json(f):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


def dong_ket_qua(f, ds):
    """Dong WMAPE, Bias theo mo hinh va tap tu 1 tep ket_qua_mo_hinh.csv; thieu thi None."""
    if not os.path.exists(f):
        return None
    k = pd.read_csv(f, encoding="utf-8-sig")
    ra = {}
    for mh in ds:
        ra[mh] = {}
        for tap in ("validation2", "test"):
            x = k[(k.mo_hinh == mh) & (k.tap == tap)]
            ra[mh][tap] = None if x.empty else dict(wmape=float(x.WMAPE.iloc[0]), bias=float(x.Bias_pct.iloc[0]), wmape_x=None if pd.isna(x.WMAPE_X.iloc[0]) else float(x.WMAPE_X.iloc[0]), wmape_z=None if pd.isna(x.WMAPE_Z.iloc[0]) else float(x.WMAPE_Z.iloc[0]))
    return ra


def bo_chuoi_dai(x):
    """Bo cac danh sach theo tung ma trong trang thai newsvendor, chi giu so tong."""
    if isinstance(x, dict):
        return {k: bo_chuoi_dai(v) for k, v in x.items() if k not in ("nhap", "ton_cuoi", "ke_hoach_mot_lan", "bo_qua")}
    return x


kho = [l.split("|")[1:-1] for l in open("reports/chi_so_kho.md", encoding="utf-8") if l.startswith("| cong_thuc") or l.startswith("| hien_trang")]
out["kho"] = {r[0].strip(): [float(v) for v in r[1:6]] for r in kho[:4]}
out["gom"] = doc_json("reports/gom_don_trang_thai.json")
out["ncc"] = doc_json("reports/cham_diem_ncc_trang_thai.json")
ncc = pd.read_csv("reports/cham_diem_ncc.csv", encoding="utf-8-sig").sort_values("diem", ascending=False)
out["ncc_bang"] = dict(dau=ncc.iloc[0].to_dict(), cuoi=ncc.iloc[-1].to_dict(), loai=ncc.xep_loai.value_counts().to_dict(), so=int(len(ncc)))
out["rb"] = doc_json("reports/rang_buoc_kho_trang_thai.json")
out["nv"] = bo_chuoi_dai(doc_json("reports/newsvendor_mua_vu_trang_thai.json"))
out["live"] = doc_json("reports/tru_hang_live_trang_thai.json")
out["live_sau"] = doc_json("reports/tru_hang_live_sau_doi_chieu_trang_thai.json")
out["dom"] = doc_json("reports/dominicks_trang_thai.json")
out["dl"] = dong_ket_qua("reports/ket_qua_mo_hinh.csv", ["ket_hop_v4", "ket_hop_v5", "lstm_tuan", "rnn_tuan", "tide_tuan", "nhits_tuan", "tft_tuan", "ket_hop_nf", "tb_truot_28_tuan"])
out["nf"] = doc_json("reports/mo_hinh_nf_trang_thai.json")
out["m5"] = dong_ket_qua("du_lieu_nguon/m5/reports/ket_qua_mo_hinh.csv", ["ket_hop_dl", "ket_hop", "lightgbm", "rnn", "lstm", "tb_truot", "prophet", "lap_tuan", "tide_tuan", "nhits_tuan", "tft_tuan", "ket_hop_nf"])
out["m5_chon"] = (doc_json("du_lieu_nguon/m5/reports/kiem_chung_trang_thai.json") or {}).get("chon")
# ---------------------------------------------------------------- du bao tuong lai, man Du bao, nghiep vu tren M5, do nhay, canh bao lech
import sqlite3  # noqa: E402


def tuong_lai(f_du_bao, f_ghi, f_dac_trung):
    """Du bao 28 ngay chua xay ra: TB / ngay toan kho, so voi cung ky 1, 2 nam truoc (bo dong co khuyen mai) va 28 ngay gan nhat."""
    if not os.path.exists(f_du_bao):
        return None
    d = pd.read_csv(f_du_bao, parse_dates=["date"])
    g = d.groupby("date").du_bao.sum()
    ft = pd.read_csv(f_dac_trung, usecols=["date", "y", "khuyen_mai"], parse_dates=["date"], encoding="utf-8-sig")
    ra = {**(doc_json(f_ghi) or {}), **dict(tb=float(g.mean()), so_ma=int(d.ma_sku.nunique()), so_dong=int(len(d)), thieu_khoang=int(d.thap_80.isna().sum()),
                                           gan=float(ft[ft.date > ft.date.max() - pd.Timedelta(days=28)].groupby("date").y.sum().mean()))}
    for lui in (364, 728):
        x = ft[ft.date.isin(g.index - pd.Timedelta(days=lui))]
        ra[f"cung_ky_{lui // 364}"] = float(x.groupby("date").y.sum().mean()) if len(x) else None
        ra[f"cung_ky_{lui // 364}_khong_km"] = float(x[x.khuyen_mai == 0].groupby("date").y.sum().mean()) if len(x) else None
    return ra


def ton_kho_db(f_db):
    """Ket qua ton kho 95% theo chinh sach tu CSDL: Fill Rate, ngay-ma thieu, ton TB, chi phi lien quan (trieu d)."""
    c = sqlite3.connect(f"file:{f_db}?mode=ro", uri=True)
    k = pd.read_sql("SELECT * FROM ket_qua_ton_kho WHERE ROUND(muc_phuc_vu, 2) = 0.95", c)
    g = k.groupby("ma_chinh_sach")
    return {cs: dict(fill=float(100 * x.da_dap_ung.sum() / x.nhu_cau.sum()), thieu=int(x.so_ngay_thieu.sum()), ton=float(x.gia_tri_ton_tb.sum() / 1e6),
                     cp=float((x.chi_phi_dat.sum() + x.chi_phi_luu.sum() + x.loi_nhuan_mat.sum()) / 1e6)) for cs, x in g}


def ti_trong_z(f_db):
    """Phan giam ton kho va loi nhuan mat cua AI + hieu chinh so voi du bao moc: ti trong cua nhom Z (phan loai tren tap huan luyen)."""
    c = sqlite3.connect(f"file:{f_db}?mode=ro", uri=True)
    k = pd.read_sql("""SELECT k.ma_chinh_sach, p.xyz_train AS xyz, SUM(k.gia_tri_ton_tb) AS ton, SUM(k.loi_nhuan_mat) AS lnm FROM ket_qua_ton_kho k
                       JOIN phan_loai_sku p USING (ma_sku) WHERE ROUND(k.muc_phuc_vu, 2) = 0.95 GROUP BY 1, 2""", c).set_index(["ma_chinh_sach", "xyz"])
    d = k.loc["cong_thuc_du_bao_moc"] - k.loc["cong_thuc_du_bao_ai_hc"]
    so_z = int(pd.read_sql("SELECT COUNT(*) AS n FROM phan_loai_sku WHERE xyz_train = 'Z'", c).n.iloc[0])
    fill_moc_z = pd.read_sql("""SELECT 100.0 * SUM(da_dap_ung) / SUM(nhu_cau) AS f FROM ket_qua_ton_kho k JOIN phan_loai_sku p USING (ma_sku)
                                WHERE ROUND(muc_phuc_vu, 2) = 0.95 AND ma_chinh_sach = 'cong_thuc_du_bao_moc' AND xyz_train = 'Z'""", c).f.iloc[0]
    return dict(ton=float(d.ton.get("Z", 0) / d.ton.sum()), lnm=float(d.lnm.get("Z", 0) / d.lnm.sum()), so_z=so_z, fill_moc_z=float(fill_moc_z))


M5K = "du_lieu_nguon/m5_kho"
out["tl"] = dict(mp=tuong_lai("reports/du_bao/ket_hop_v4_tuong_lai.csv", "reports/du_bao_tuong_lai.json", "data/features/dac_trung.csv"),
                 m5=tuong_lai("du_lieu_nguon/m5/reports/du_bao/day_du/ket_hop_dl_tuong_lai.csv", "du_lieu_nguon/m5/reports/du_bao_tuong_lai.json",
                              "du_lieu_nguon/m5/data/features/dac_trung.csv"))
out["rnn_kl"] = doc_json("du_lieu_nguon/m5/reports/rnn_tuong_lai.json")
out["ss_km"] = doc_json("reports/so_sanh_khuyen_mai.json")
out["dn_s"] = dict(mp=doc_json("reports/do_nhay_chi_phi_dat_trang_thai.json"), m5=doc_json(f"{M5K}/reports/do_nhay_chi_phi_dat_trang_thai.json"))
out["cb2"] = dict(mp=doc_json("reports/canh_bao_lech_v2_trang_thai.json"), m5=doc_json(f"{M5K}/reports/canh_bao_lech_v2_trang_thai.json"))
out["m5_gom"] = doc_json(f"{M5K}/reports/gom_don_trang_thai.json")
out["m5_tk"] = ton_kho_db(f"{M5K}/data/kho_hang.db") if os.path.exists(f"{M5K}/data/kho_hang.db") else None
out["tk_db"] = ton_kho_db("data/kho_hang.db")
out["z"] = ti_trong_z("data/kho_hang.db")
out["z_m5"] = int(pd.read_sql("SELECT COUNT(*) AS n FROM phan_loai_sku WHERE xyz_train = 'Z'", sqlite3.connect(f"file:{M5K}/data/kho_hang.db?mode=ro", uri=True)).n.iloc[0])
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print("ok", list(out))
