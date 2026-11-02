"""Xuat du lieu tu CSDL sang CSV cho Power BI (mo hinh hinh sao: 3 bang danh muc dim_* + 3 bang su kien fact_*).
DOC TU CO SO DU LIEU (chi doc). Chay sau: python src/nap_database.py && python src/ton_kho.py
Chay: python src/xuat_power_bi.py
Ket qua: reports/power_bi/*.csv (UTF-8 co BOM, dau cham thap phan, ngay YYYY-MM-DD; khong luu git, chay lai de co)
         reports/power_bi/so_doi_chieu.md: so dung de tu kiem tra khi dung trang Power BI (huong dan: docs/12_power_bi.md)
Hang dang ve va trang thai canh bao tinh bang csdl.hang_dang_ve / csdl.trang_thai_ton_kho, giong dashboard app/dashboard.py.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from csdl import TRANG_THAI, doc, hang_dang_ve, trang_thai_ton_kho  # noqa: E402

OUT = "reports/power_bi"
MAIN = 0.95
NGAY_VI_DU = "2026-02-09"     # 8 ngay truoc Tet 2026, dung lam vi du canh bao (giong docs/10 muc 12)
os.makedirs(OUT, exist_ok=True)
CS_TEN = {"hien_trang": "Hiện trạng*", "cong_thuc_du_bao_moc": "Công thức + dự báo mốc",
          "cong_thuc_du_bao_ai": "Công thức + dự báo AI", "cong_thuc_du_bao_ai_hc": "AI + hiệu chỉnh lệch (đề xuất)"}
vn = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
files = []


def ghi(df, ten):
    df.to_csv(f"{OUT}/{ten}.csv", index=False, encoding="utf-8-sig", float_format="%.2f")
    files.append((ten, len(df), len(df.columns)))
    print(f"{ten}.csv: {len(df):,} dong x {len(df.columns)} cot")


# ------------------------------------------------------------------ bang danh muc (dim)
sku = doc("""SELECT s.ma_sku, s.ten_sku, s.nhom_hang, s.don_vi, p.abc_train AS abc, p.xyz_train AS xyz,
                    p.loai_nhu_cau, s.lead_time_tb, s.moq, s.gia_von, s.gia_ban, s.ma_ncc
             FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku) ORDER BY s.ma_sku""")
ghi(sku, "dim_sku")

cs = doc("SELECT ma_chinh_sach, mo_ta FROM chinh_sach")
cs["ten_chinh_sach"] = cs.ma_chinh_sach.map(CS_TEN)
cs["thu_tu"] = cs.ma_chinh_sach.map({c: i + 1 for i, c in enumerate(CS_TEN)})   # dung "Sort by column" trong Power BI
cs["de_xuat"] = (cs.ma_chinh_sach == "cong_thuc_du_bao_ai_hc").astype(int)
ghi(cs.sort_values("thu_tu")[["ma_chinh_sach", "ten_chinh_sach", "thu_tu", "de_xuat", "mo_ta"]], "dim_chinh_sach")

mp = doc("""SELECT ma_chinh_sach, ngay, ma_sku, nhu_cau, xuat, nhap, ton_cuoi, rop, dat_hang FROM mo_phong_ngay
            ORDER BY ma_chinh_sach, ma_sku, ngay""")
ds = pd.to_datetime(pd.Series(sorted(mp.ngay.unique())))
nghi = doc("SELECT ngay, ly_do FROM lich_ngay_nghi").set_index("ngay").ly_do
ngay = pd.DataFrame({"ngay": ds.dt.strftime("%Y-%m-%d"), "nam": ds.dt.year, "thang": ds.dt.month,
                     "thang_nam": ds.dt.strftime("%Y-%m"), "dau_tuan": (ds - pd.to_timedelta(ds.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d"),
                     "thu": ds.dt.weekday + 2})                                # 2 = thu Hai ... 8 = Chu nhat
ngay["ten_thu"] = ngay.thu.map(lambda t: "CN" if t == 8 else f"T{t}")
ngay["ly_do_nghi"] = ngay.ngay.map(nghi)
ngay["kho_nghi"] = ngay.ly_do_nghi.notna().astype(int)
ghi(ngay, "dim_ngay")

# ------------------------------------------------------------------ bang su kien (fact)
chon = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]
MOC = "tb_truot_28_tuan"     # du bao moc cap nhat moi tuan nhu mo hinh chon (docs/10 muc 9.6)
d = doc("""SELECT ma_mo_hinh, moc, ngay, ngay_thu, ma_sku, du_bao, thuc_te, thap_80, cao_80 FROM du_bao
           WHERE tap = 'test' AND ma_mo_hinh IN (?, ?)""", (chon, MOC))
d = d.sort_values("ngay_thu").drop_duplicates(["ma_mo_hinh", "ngay", "ma_sku"])     # moi ngay 1 dong: ban moi nhat
db = d.pivot(index=["ngay", "ma_sku"], columns="ma_mo_hinh", values="du_bao").reset_index()
db = db.rename(columns={chon: "du_bao_ai", MOC: "du_bao_moc"})
db = db.merge(d[d.ma_mo_hinh == chon][["ngay", "ma_sku", "moc", "thuc_te", "thap_80", "cao_80"]], on=["ngay", "ma_sku"])
ghi(db[["ngay", "ma_sku", "moc", "thuc_te", "du_bao_ai", "du_bao_moc", "thap_80", "cao_80"]], "fact_du_bao")

mp[["dat_hang", "rop"]] = mp[["dat_hang", "rop"]].astype(float)
gd = doc("SELECT ngay, ma_sku, qty_in FROM giao_dich_sach WHERE ngay >= ? AND ngay < date(?, '+60 day')",
         (mp.ngay.min(), mp.ngay.min()))
lt = sku.set_index("ma_sku").lead_time_tb
mp["dang_ve"] = pd.concat([hang_dang_ve(g, lt, gd) for _, g in mp.groupby("ma_chinh_sach", sort=False)])
mp["thieu"] = (mp.nhu_cau - mp.xuat).clip(lower=0)
mp["trang_thai"] = trang_thai_ton_kho(mp).where(mp.ma_chinh_sach != "hien_trang")   # hien trang khong co ROP
ghi(mp[["ma_chinh_sach", "ngay", "ma_sku", "nhu_cau", "xuat", "thieu", "nhap", "ton_cuoi", "rop", "dang_ve",
        "dat_hang", "trang_thai"]], "fact_ton_kho_ngay")

kq = doc("""SELECT k.ma_chinh_sach, k.muc_phuc_vu, k.ma_sku, k.nhu_cau, k.da_dap_ung, k.so_ngay_thieu, k.ton_tb,
                   k.gia_tri_ton_tb, k.so_lan_nhap, k.chi_phi_dat, k.chi_phi_luu, k.doanh_thu_mat, k.loi_nhuan_mat,
                   t.ss_tb, t.rop_tb, t.eoq_tb
            FROM ket_qua_ton_kho k LEFT JOIN tham_so_ton_kho t USING (ma_chinh_sach, muc_phuc_vu, ma_sku)
            ORDER BY k.ma_chinh_sach, k.muc_phuc_vu, k.ma_sku""")
ghi(kq, "fact_ket_qua_sku")

# ------------------------------------------------------------------ so doi chieu (tinh tu chinh cac file vua xuat)
v = doc("SELECT * FROM v_so_sanh_chinh_sach WHERE ROUND(muc_phuc_vu, 2) = ?", (MAIN,)).set_index("ma_chinh_sach")
k95 = kq[kq.muc_phuc_vu.round(2) == MAIN].groupby("ma_chinh_sach")
fr = 100 * k95.da_dap_ung.sum() / k95.nhu_cau.sum()
fr_ngay = 100 * mp.groupby("ma_chinh_sach").xuat.sum() / mp.groupby("ma_chinh_sach").nhu_cau.sum()
cp = (k95.chi_phi_dat.sum() + k95.chi_phi_luu.sum() + k95.loi_nhuan_mat.sum()) / 1e6
assert ((fr - v.fill_rate_pt).abs() < 0.01).all() and ((fr_ngay - fr).abs() < 0.01).all(), "Fill Rate lech CSDL"
assert ((cp - v.chi_phi_lien_quan_trieu).abs() < 0.1).all(), "chi phi lech CSDL"
cham = db.dropna(subset=["thuc_te"])
wm = lambda f: (cham.thuc_te - cham[f]).abs().sum() / cham.thuc_te.sum()
wm_csdl = doc("SELECT wmape FROM ket_qua_mo_hinh WHERE ma_mo_hinh = ? AND tap = 'test'", (chon,)).wmape.iloc[0]
assert abs(wm("du_bao_ai") - wm_csdl) < 0.001, f"WMAPE lech: {wm('du_bao_ai')} vs {wm_csdl}"
tt = mp[(mp.ngay == NGAY_VI_DU) & (mp.ma_chinh_sach == "cong_thuc_du_bao_ai_hc")].trang_thai.value_counts()
sku001 = cham[cham.ma_sku == "SKU001"]

L = ["# So doi chieu cho Power BI", "",
     "Sinh tu dong boi `python src/xuat_power_bi.py`, tinh tu chinh cac file CSV vua xuat va da doi chieu voi CSDL "
     "(lech thi script dung lai bao loi). Dung trang Power BI xong, so tren trang phai ra dung cac so duoi day. Du lieu mo phong.", "",
     "## 1. So dong moi file (buoi 1: nap du lieu)", "", "| File | So dong | So cot |", "|---|---:|---:|"]
L += [f"| `{t}.csv` | {vn(n, 0)} | {c} |" for t, n, c in files]
L += ["", f"## 2. Truoc – sau, muc phuc vu {MAIN:.0%} (buoi 2)", "",
      "Bang `fact_ket_qua_sku` co 3 muc phuc vu: **phai loc `muc_phuc_vu` = 0.95**, neu khong chi phi bi cong gap 3 "
      "(Fill Rate van dung vi la ty le).", "",
      "| Chinh sach | Fill Rate | Ngay-SKU thieu | Ton kho binh quan (trieu d) | Chi phi lien quan (trieu d) |", "|---|---:|---:|---:|---:|"]
for c in CS_TEN:
    L.append(f"| {CS_TEN[c]} | {vn(fr[c], 2)}% | {vn(k95.so_ngay_thieu.sum()[c], 0)} | "
             f"{vn(k95.gia_tri_ton_tb.sum()[c] / 1e6, 1)} | {vn(cp[c], 1)} |")
L += ["", "## 3. Du bao (buoi 3 va 5)", "",
      f"- WMAPE du bao AI ({chon}), ca 121 SKU, tap test: **{vn(wm('du_bao_ai'), 3)}** "
      f"(du bao moc TB truot 28 ngay: {vn(wm('du_bao_moc'), 3)}). Chi tinh dong co `thuc_te`.",
      f"- Rieng SKU001: WMAPE AI {vn((sku001.thuc_te - sku001.du_bao_ai).abs().sum() / sku001.thuc_te.sum(), 3)}, "
      f"tong thuc te {vn(sku001.thuc_te.sum(), 0)}, tong du bao AI cung ngay {vn(sku001.du_bao_ai.sum(), 0)}.",
      "", f"## 4. Canh bao ngay {pd.Timestamp(NGAY_VI_DU):%d/%m/%Y}, chinh sach AI + hieu chinh lech (buoi 5)", "",
      "| Trang thai | So SKU |", "|---|---:|"]
L += [f"| {s} | {int(tt.get(s, 0))} |" for s in TRANG_THAI]
with open(f"{OUT}/so_doi_chieu.md", "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"\nDa ghi {OUT}/so_doi_chieu.md (Fill Rate, chi phi, WMAPE khop CSDL)")
