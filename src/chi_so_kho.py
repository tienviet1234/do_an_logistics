"""Chi so kho: vong quay hang ton, so ngay ton kho (DOH), ton du. Ham thuan co test: tests/test_chi_so_kho.py.
- Vong quay (lan/nam) = gia von hang xuat quy doi 365 ngay / gia tri ton kho binh quan.
- So ngay ton kho (DOH) = gia tri ton kho binh quan / gia von hang xuat binh quan 1 ngay (vong quay x DOH = 365).
- Ton du = phan ton cuoi ngay vuot qua nhu cau THAT cua 28 ngay ke tiep (nhin lai sau khi da biet nhu cau, chi de CHAM chinh
  sach, khong dung de ra quyet dinh); 28 ngay cuoi ky khong du 28 ngay ke tiep nen khong tinh.
Chay: python src/chi_so_kho.py   (sau ton_kho.py) -> reports/chi_so_kho.md. Chi doc CSDL, khong ghi CSDL.
"""
import os
import sys

import numpy as np
import pandas as pd

CUA_SO_DU = 28


def vong_quay_doh(gia_von_xuat, ton_tb, so_ngay):
    """(vong quay lan/nam, DOH ngay). Khong xuat hang -> DOH vo cuc; khong ton kho -> vong quay vo cuc."""
    if so_ngay <= 0:
        raise ValueError("so_ngay phai > 0")
    if gia_von_xuat < 0 or ton_tb < 0:
        raise ValueError("gia von xuat va ton kho khong duoc am")
    if gia_von_xuat == 0:
        return (0.0 if ton_tb > 0 else float("nan"), float("inf") if ton_tb > 0 else float("nan"))
    if ton_tb == 0:
        return float("inf"), 0.0
    return gia_von_xuat * 365 / (so_ngay * ton_tb), ton_tb * so_ngay / gia_von_xuat


def chi_so_theo_nhom(k, by, so_ngay):
    """k: moi dong 1 ma (ket_qua_ton_kho) co cot da_dap_ung, gia_von, gia_tri_ton_tb. Cong gia tri roi moi chia, khong lay TB cac ty le."""
    x = k.assign(gv=k.da_dap_ung * k.gia_von).groupby(by)[["gv", "gia_tri_ton_tb"]].sum()
    so = [vong_quay_doh(a, b, so_ngay) for a, b in zip(x.gv, x.gia_tri_ton_tb)]
    return x.assign(vong_quay=[a for a, _ in so], doh=[b for _, b in so])


def ton_du_mot_ma(ton_cuoi, nhu_cau, cua_so=CUA_SO_DU):
    """Mang ton du tung ngay (don vi) theo thu tu ngay; ngay khong du cua so ke tiep la NaN."""
    ton, nc = np.asarray(ton_cuoi, dtype=float), np.asarray(nhu_cau, dtype=float)
    if len(ton) != len(nc):
        raise ValueError("ton_cuoi va nhu_cau phai cung do dai")
    ra = np.full(len(ton), np.nan)
    if len(ton) > cua_so:
        tl = np.concatenate([[0.0], np.cumsum(nc)])
        ke_tiep = tl[cua_so + 1:] - tl[1:len(nc) - cua_so + 1]        # tong nhu cau cua ngay t+1 ... t+cua_so
        ra[:len(ke_tiep)] = np.maximum(ton[:len(ke_tiep)] - ke_tiep, 0)
    return ra


def ton_du_theo_ma(m, gia_von):
    """m: mo phong theo ngay (ma_sku, ngay, ton_cuoi, nhu_cau). Tren cac ngay du cua so: gia tri ton binh quan, ton du binh quan, ti le ngay co du."""
    dong = []
    for ma, g in m.sort_values(["ma_sku", "ngay"]).groupby("ma_sku"):
        du = ton_du_mot_ma(g.ton_cuoi.values, g.nhu_cau.values)
        co = ~np.isnan(du)
        dong.append((ma, g.ton_cuoi.values[co].mean() * gia_von[ma] if co.any() else 0.0, du[co].mean() * gia_von[ma] if co.any() else 0.0))
    return pd.DataFrame(dong, columns=["ma_sku", "ton_tb", "du_tb"])


def bao_cao():
    sys.path.insert(0, os.path.dirname(__file__))
    from csdl import doc
    so_ngay = doc("SELECT COUNT(DISTINCT ngay) AS n FROM mo_phong_ngay").n.iloc[0]
    sku = doc("SELECT s.ma_sku, s.ten_sku, s.gia_von, p.xyz_train AS xyz FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku)").set_index("ma_sku")
    k = doc("SELECT * FROM ket_qua_ton_kho WHERE ROUND(muc_phuc_vu, 2) = 0.95")
    k = k.assign(gia_von=k.ma_sku.map(sku.gia_von), xyz=k.ma_sku.map(sku.xyz))
    tong = chi_so_theo_nhom(k, ["ma_chinh_sach"], so_ngay)
    nhom = chi_so_theo_nhom(k, ["ma_chinh_sach", "xyz"], so_ngay)
    du = {}
    for cs in tong.index:
        m = doc("SELECT ma_sku, ngay, ton_cuoi, nhu_cau FROM mo_phong_ngay WHERE ma_chinh_sach = ?", (cs,))
        du[cs] = ton_du_theo_ma(m, sku.gia_von).assign(ten=lambda f: f.ma_sku.map(sku.ten_sku), xyz=lambda f: f.ma_sku.map(sku.xyz))
    bang = pd.DataFrame({"vong_quay_lan_nam": tong.vong_quay.round(1), "so_ngay_ton": tong.doh.round(1),
                         "ton_tb_trieu": (tong.gia_tri_ton_tb / 1e6).round(1),
                         "ton_du_tb_trieu": [round(du[c].du_tb.sum() / 1e6, 1) for c in tong.index],
                         "ti_le_du_pt": [round(100 * du[c].du_tb.sum() / du[c].ton_tb.sum(), 1) for c in tong.index]})
    chon = "cong_thuc_du_bao_ai_hc"
    top = du[chon].sort_values("du_tb", ascending=False).head(10).assign(du_trieu=lambda f: (f.du_tb / 1e6).round(1))
    L = ["# Chỉ số kho", "", f"Mô phỏng {so_ngay} ngày của tập kiểm tra, mức phục vụ 95%. Dữ liệu mô phỏng, không phải số liệu kho thật.", "",
         "Tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng để ra quyết định); bỏ 28 ngày cuối kỳ.", "",
         "## Theo chính sách", "", bang.to_markdown(), "", "## Số ngày tồn kho theo nhóm XYZ", "",
         nhom.doh.unstack("xyz").round(1).to_markdown(), "", "## 10 mã tồn dư lớn nhất (AI + hiệu chỉnh)", "",
         top[["ma_sku", "ten", "xyz", "du_trieu"]].to_markdown(index=False), ""]
    open("reports/chi_so_kho.md", "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    bao_cao()
