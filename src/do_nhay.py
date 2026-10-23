"""GD F bo sung: thu do nhay chinh sach ton kho voi cu soc lead time va chi phi (kich ban theo docs/07).
DOC TU CO SO DU LIEU, ghi nguoc vao CSDL (kich_ban_do_nhay, ket_qua_do_nhay, v_do_nhay). Chay sau: python src/ton_kho.py
Chay: python src/do_nhay.py      (~2 phut)
Ket qua: CSDL + reports/do_nhay.md

Dung lai nguyen ham mo phong cua ton_kho.py (cung nhu cau that, cung lead time ngau nhien, cung du bao), chi doi 1 yeu to:
  goc            : khong doi gi -> phai ra dung ket qua GD F (kiem tra).
  tac_cang k     : hang du kien VE trong 3 tuan tac cang thi ve tre them k ngay (k = 3, 5, 7). Chay 13 dot, moi dot bat dau
                   cach nhau 4 tuan, de khong chon dot co loi. Nguoi lap ke hoach KHONG biet truoc (tham so giu nguyen).
                   Gia dinh: moi SKU deu bi anh huong (thu thach nang nhat); docs/07 con ghi "ve don 1-2 ngay": chua mo phong rieng.
  lead_time +2   : moi don ve tre them 2 ngay ca nam (quy dinh tai trong, docs/07). Chay 2 lan: khong biet / co cap nhat
                   lead time trong cong thuc (L, sigma_LTD tinh lai tren validation2 voi L moi).
  chi_phi        : chi phi dat hang S +20% (cuoc tang; EOQ tu tinh lai), chi phi luu kho H +15% (gia dien, kho lanh).
Hien trang: don dat lay tu du lieu, khong co quy tac de chay lai khi lead time doi -> chi so duoc o kich ban goc va chi phi
(giu nguyen don, tinh lai chi phi). Muc phuc vu 95% (muc chinh), quy tac luong dat lay tu bang chinh_sach (chon o GD F).
"""
import os
import sys
from contextlib import closing

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from csdl import SCHEMA, doc, ket_noi  # noqa: E402
from ton_kho import MAIN, POLICIES, kpis, load_inputs, run  # noqa: E402

DAI_TAC = 21                     # 3 tuan tac cang
BUOC_DOT = 28                    # moi 4 tuan 1 dot -> 13 dot trong nam test
K_TAC = [3, 5, 7]
REPORT = "reports/do_nhay.md"
CONG_THUC = [p for p, v in POLICIES.items() if v[1] is not None]
TEN = {"hien_trang": "Hien trang*", "cong_thuc_du_bao_moc": "Du bao moc", "cong_thuc_du_bao_ai": "AI",
       "cong_thuc_du_bao_ai_hc": "AI + hieu chinh (de xuat)"}


def tao_bang():
    """Chay phan NHOM 6 cua schema.sql (IF NOT EXISTS) de dung duoc tren CSDL nap truoc khi co bang do nhay."""
    with open(SCHEMA, encoding="utf-8") as f:
        ddl = f.read().split("-- NHOM 6.", 1)[1]
    with closing(ket_noi()) as con:
        con.executescript("--" + ddl)


def hien_trang(inp):
    """KPI hien trang: don, nhap, xuat, ton lay tu du lieu; chi phi tinh theo tham so cua inp (de doi S, H)."""
    o = inp["obs"]
    return pd.DataFrame([dict(ma_chinh_sach="hien_trang", muc_phuc_vu=MAIN, ma_sku=r.ma_sku,
                              **kpis(inp["dem"][i], inp["closed"], r, o["qty_in"][i], o["qty_out"][i], o["ton_cuoi_ngay"][i]))
                         for i, r in enumerate(inp["sku"].itertuples())])


def chay(inp, rule, co_hien_trang):
    res = [run(inp, "test", pol, rule, [MAIN])[0] for pol in CONG_THUC]
    if co_hien_trang:
        res.append(hien_trang(inp))
    return pd.concat(res, ignore_index=True)


def tong(df):
    g = df.groupby("ma_chinh_sach")
    return pd.DataFrame({"fill_rate": 100 * g.da_dap_ung.sum() / g.nhu_cau.sum(), "ngay_thieu": g.so_ngay_thieu.sum(),
                         "ton_tb": g.gia_tri_ton_tb.sum() / 1e6,
                         "cplq": (g.chi_phi_dat.sum() + g.chi_phi_luu.sum() + g.loi_nhuan_mat.sum()) / 1e6})


if __name__ == "__main__":
    tao_bang()
    rule = doc("SELECT quy_tac_luong_dat FROM chinh_sach WHERE quy_tac_luong_dat IS NOT NULL").quy_tac_luong_dat.iloc[0]
    te = load_inputs("test")
    n, ds = len(te["ds"]), te["ds"]
    print(f"Test {ds[0]} .. {ds[-1]}, quy tac luong dat {rule}, muc phuc vu {MAIN:.0%}")
    kb, kq = [], []

    def them(ma, nhom, mo_ta, inp, co_ht, tham_so=None, tu=None, den=None, biet=0):
        kb.append(dict(ma_kich_ban=ma, nhom=nhom, mo_ta=mo_ta, tham_so=tham_so, tu_ngay=tu, den_ngay=den, biet_truoc=biet))
        kq.append(chay(inp, rule, co_ht).assign(ma_kich_ban=ma))
        print(f"  xong {ma}")

    them("goc", "goc", "Không đổi (kết quả GĐ F)", te, True)

    t = np.arange(n)
    den_dk = t[None, :] + te["LT"]                                  # ngay hang du kien ve neu dat ngay t
    for w0 in range(0, n - DAI_TAC + 1, BUOC_DOT):
        trong = (den_dk >= w0) & (den_dk < w0 + DAI_TAC)
        for k in K_TAC:
            them(f"tac_cang_{k}_{ds[w0].replace('-', '')}", "tac_cang",
                 f"Tắc cảng 3 tuần: hàng dự kiến về {ds[w0]} .. {ds[w0 + DAI_TAC - 1]} về trễ thêm {k} ngày",
                 {**te, "LT": te["LT"] + k * trong}, False, k, ds[w0], ds[w0 + DAI_TAC - 1])

    lt2 = {**te, "LT": te["LT"] + 2}
    them("lead_time_2", "lead_time", "Mọi đơn về trễ thêm 2 ngày cả năm, công thức không cập nhật", lt2, False, 2)
    sku_lt = te["sku"].assign(lead_time_tb=te["sku"].lead_time_tb + 2)
    them("lead_time_2_cap_nhat", "lead_time", "Mọi đơn về trễ thêm 2 ngày cả năm, công thức cập nhật lead time +2",
         {**lt2, "sku": sku_lt}, False, 2, biet=1)
    them("chi_phi_dat_120", "chi_phi", "Chi phí đặt hàng S +20% (cước tăng), EOQ tính lại",
         {**te, "sku": te["sku"].assign(chi_phi_dat_hang=te["sku"].chi_phi_dat_hang * 1.2)}, True, 1.2, biet=1)
    them("chi_phi_luu_115", "chi_phi", "Chi phí lưu kho H +15% (giá điện, kho lạnh), EOQ tính lại",
         {**te, "sku": te["sku"].assign(ty_le_chi_phi_luu_kho=te["sku"].ty_le_chi_phi_luu_kho * 1.15)}, True, 1.15, biet=1)

    kb, kq = pd.DataFrame(kb), pd.concat(kq, ignore_index=True)

    # kiem tra: kich ban goc phai trung ket qua GD F
    f = doc("SELECT * FROM ket_qua_ton_kho WHERE ROUND(muc_phuc_vu, 2) = ?", (MAIN,)).set_index(["ma_chinh_sach", "ma_sku"])
    g = kq[kq.ma_kich_ban == "goc"].set_index(["ma_chinh_sach", "ma_sku"]).loc[f.index]
    for c in ["da_dap_ung", "so_ngay_thieu", "gia_tri_ton_tb", "chi_phi_dat", "chi_phi_luu", "loi_nhuan_mat"]:
        assert np.allclose(g[c], f[c]), f"kich ban goc lech GD F o cot {c}"
    print("Kiem tra: kich ban goc trung khop ket qua GD F")

    with closing(ket_noi()) as con:
        con.execute("DELETE FROM ket_qua_do_nhay")
        con.execute("DELETE FROM kich_ban_do_nhay")
        kb.to_sql("kich_ban_do_nhay", con, if_exists="append", index=False)
        kq.to_sql("ket_qua_do_nhay", con, if_exists="append", index=False)
        con.commit()
        bad = len(con.execute("PRAGMA foreign_key_check").fetchall())
    print(f"Da ghi CSDL: {len(kb)} kich ban, {len(kq)} dong (vi pham khoa ngoai: {bad})")

    # ------------------------------------------------------------------ bao cao
    v = doc("SELECT * FROM v_do_nhay")
    base = tong(kq[kq.ma_kich_ban == "goc"])
    fmt = lambda x, nd=1: f"{x:+.{nd}f}"
    L = ["# Thu do nhay chinh sach ton kho (GD F bo sung)", "",
         f"12 thang test ({ds[0]} .. {ds[-1]}), 121 SKU, muc phuc vu {MAIN:.0%}, quy tac luong dat **{rule}**. "
         "Kich ban theo `docs/07`. Du lieu mo phong. Kich ban goc trung khop ket qua GD F (da kiem tra trong script).",
         "Hien trang* chi so duoc o kich ban chi phi (don lay tu du lieu, khong chay lai duoc khi lead time doi).", "",
         "## 1. Kich ban goc", "", base.loc[[*CONG_THUC, "hien_trang"]].rename(index=TEN).round(2).to_markdown(), ""]

    tc = v[v.nhom == "tac_cang"].copy()
    tc["k"] = tc.tham_so.astype(int)
    tc = tc.merge(base.rename(columns=lambda c: c + "_goc"), left_on="ma_chinh_sach", right_index=True)
    tc["d_fr"] = tc.fill_rate_pt - tc.fill_rate_goc
    tc["d_cp"] = 100 * (tc.chi_phi_lien_quan_trieu / tc.cplq_goc - 1)
    rows = []
    for (k, p), x in tc.groupby(["k", "ma_chinh_sach"]):
        w = x.loc[x.fill_rate_pt.idxmin()]
        rows.append({"tre_them_ngay": k, "chinh_sach": TEN[p], "fill_rate_tb": x.fill_rate_pt.mean(),
                     "doi_fill_rate_tb_diem": x.d_fr.mean(), "doi_fill_rate_xau_nhat_diem": x.d_fr.min(),
                     "dot_xau_nhat": w.tu_ngay, "doi_cp_lien_quan_tb_pt": x.d_cp.mean(), "doi_cp_lien_quan_xau_nhat_pt": x.d_cp.max()})
    best = tc.loc[tc.groupby(["k", "tu_ngay"]).chi_phi_lien_quan_trieu.idxmin()].groupby("k").ma_chinh_sach.value_counts()
    so_dot = tc.tu_ngay.nunique()
    L += ["## 2. Tac cang 3 tuan (nguoi lap ke hoach khong biet truoc)", "",
          f"{so_dot} dot, moi dot bat dau cach nhau 4 tuan; bang ghi trung binh tren {so_dot} dot va dot xau nhat. "
          "`doi_*`: so voi kich ban goc (Fill Rate: diem %, chi phi lien quan: %).", "",
          pd.DataFrame(rows).round(2).to_markdown(index=False), "",
          "So dot moi chinh sach co chi phi lien quan thap nhat (trong 3 chinh sach theo cong thuc):", ""]
    L += [f"- Tre them {k} ngay: " + ", ".join(f"{TEN[p]} {c}/{so_dot}" for p, c in best[k].items()) for k in K_TAC]
    tet = tc[(tc.tu_ngay <= "2026-02-16") & (tc.tu_ngay > "2026-01-01")]
    L += ["", f"Dot truoc Tet (hang du kien ve {tet.tu_ngay.iloc[0]} tro di, Tet 17/02/2026):", "",
          tet.assign(chinh_sach=tet.ma_chinh_sach.map(TEN))[["k", "chinh_sach", "fill_rate_pt", "d_fr", "so_ngay_sku_thieu",
                                                              "chi_phi_lien_quan_trieu", "d_cp"]]
          .sort_values(["k", "chinh_sach"]).round(2).to_markdown(index=False), ""]

    def so_sanh(ma_list):
        x = v[v.ma_kich_ban.isin(ma_list)].merge(base.rename(columns=lambda c: c + "_goc"), left_on="ma_chinh_sach", right_index=True)
        x["doi_fill_rate_diem"] = x.fill_rate_pt - x.fill_rate_goc
        x["doi_ton_tb_pt"] = 100 * (x.ton_tb_trieu_vnd / x.ton_tb_goc - 1)
        x["doi_cp_lien_quan_pt"] = 100 * (x.chi_phi_lien_quan_trieu / x.cplq_goc - 1)
        x["chinh_sach"] = x.ma_chinh_sach.map(TEN)
        return x[["ma_kich_ban", "chinh_sach", "fill_rate_pt", "doi_fill_rate_diem", "so_ngay_sku_thieu", "ton_tb_trieu_vnd",
                  "doi_ton_tb_pt", "so_lan_nhap", "chi_phi_lien_quan_trieu", "doi_cp_lien_quan_pt"]
                 ].sort_values(["ma_kich_ban", "chinh_sach"]).round(2).to_markdown(index=False)

    L += ["## 3. Lead time dai them 2 ngay ca nam", "", so_sanh(["lead_time_2", "lead_time_2_cap_nhat"]), "",
          "## 4. Chi phi tang (co hien trang)", "", so_sanh(["chi_phi_dat_120", "chi_phi_luu_115"]), ""]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L[6:]))
