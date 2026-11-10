"""Do nhay theo chi phi dat hang S. Luat ghi TRUOC khi chay: docs/10 muc 10.13. Chi doc CSDL, khong ghi CSDL, khong doi chinh sach.
Doi S cho moi ma (EOQ tinh lai); giu quy tac luong dat da chon, muc phuc vu 95%, du bao, hieu chinh, ton an toan; tap test.
Quy tac kinh nghiem / hien trang giu nguyen don, chi tinh lai chi phi (nhu do_nhay.py). S x 1 phai trung ket qua ton kho da co.
Chay (tai thu muc goc hoac thu muc nguon): python src/do_nhay_chi_phi_dat.py -> reports/do_nhay_chi_phi_dat.md, reports/do_nhay_chi_phi_dat_trang_thai.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HE_SO_S = [0.1, 0.25, 0.5, 1.0, 2.0]
NGUONG_DIEM = 5.0                               # luat: loi ich AI o S x 0,1 cao hon o S x 1 it nhat 5 diem %
REPORT = "reports/do_nhay_chi_phi_dat.md"
STATE = "reports/do_nhay_chi_phi_dat_trang_thai.json"
AI, MOC, HT = "cong_thuc_du_bao_ai_hc", "cong_thuc_du_bao_moc", "hien_trang"


def doi_s(sku, he_so):
    """Ban sao danh muc voi chi phi dat nhan he_so; cac cot khac giu nguyen."""
    if he_so <= 0:
        raise ValueError("he so S phai duong")
    return sku.assign(chi_phi_dat_hang=sku.chi_phi_dat_hang.astype(float) * he_so)


def eoq_ngay_ban(dbar, s, h):
    """Luong dat EOQ tinh bang so ngay ban: sqrt(2 * D_nam * S / H) / dbar = sqrt(2 * 365 * S / (dbar * H)). dbar <= 0 -> nan."""
    dbar, s, h = (np.asarray(x, dtype=float) for x in (dbar, s, h))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((dbar > 0) & (h > 0), np.sqrt(2 * 365 * s / (dbar * h)), np.nan)


def loi_ich(moc, ai):
    """Phan tram chi phi lien quan AI tiet kiem so voi du bao moc (duong la co loi)."""
    if moc <= 0:
        raise ValueError("chi phi du bao moc phai duong")
    return 100 * (moc - ai) / moc


def ket_luan(bang, nguong=NGUONG_DIEM):
    """bang: {he_so: loi_ich_%}. Dung luat ghi truoc: so S x 0,1 voi S x 1."""
    if 0.1 not in bang or 1.0 not in bang:
        raise ValueError("thieu muc S x 0,1 hoac S x 1")
    chenh = bang[0.1] - bang[1.0]
    return dict(chenh_diem=chenh, phu_thuoc=bool(chenh >= nguong))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from csdl import doc
    from do_nhay import chay, tong
    from kiem_tra_du_lieu import nguon_du_lieu
    from ton_kho import MAIN, load_inputs
    n = nguon_du_lieu()
    rule = doc("SELECT quy_tac_luong_dat FROM chinh_sach WHERE ma_chinh_sach = ?", (AI,)).quy_tac_luong_dat.iloc[0]
    te = load_inputs("test")
    sku = te["sku"]
    o = ~te["closed"]
    dbar = np.array([d[o].mean() for d in te["dem"]])
    h = (sku.ty_le_chi_phi_luu_kho * sku.gia_von).values.astype(float)
    print(f"{n['ten']}: test {te['ds'][0]} .. {te['ds'][-1]}, quy tac {rule}, muc phuc vu {MAIN:.0%}", flush=True)
    kq, chi_tiet = {}, {}
    for k in HE_SO_S:
        r = chay({**te, "sku": doi_s(sku, k)}, rule, True)
        t = tong(r)
        if k == 1.0:
            f = doc("SELECT * FROM ket_qua_ton_kho WHERE ROUND(muc_phuc_vu, 2) = ?", (MAIN,)).set_index(["ma_chinh_sach", "ma_sku"])
            g = r.set_index(["ma_chinh_sach", "ma_sku"]).loc[f.index]
            for c in ["da_dap_ung", "so_ngay_thieu", "gia_tri_ton_tb", "chi_phi_dat", "chi_phi_luu", "loi_nhuan_mat"]:
                assert np.allclose(g[c], f[c]), f"S x 1 lech ket qua ton kho o cot {c}"
            print("Kiem tra: S x 1 trung ket qua ton kho", flush=True)
        e = eoq_ngay_ban(dbar, sku.chi_phi_dat_hang.values * k, h)
        kq[k] = dict(eoq_ngay=float(np.nanmedian(e)), loi_ich=loi_ich(t.cplq[MOC], t.cplq[AI]),
                     **{f"{c}_{p}": float(t.loc[p, c]) for p in (AI, MOC, HT) for c in ("fill_rate", "ngay_thieu", "ton_tb", "cplq")})
        print(f"  S x {k}: EOQ {kq[k]['eoq_ngay']:.1f} ngay ban, loi ich AI {kq[k]['loi_ich']:+.1f}%", flush=True)
    kl = ket_luan({k: v["loi_ich"] for k, v in kq.items()})
    json.dump(dict(nguon=n["ten"], quy_tac=rule, ket_qua={str(k): v for k, v in kq.items()}, ket_luan=kl), open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    L = ["# Độ nhạy theo chi phí đặt hàng", "",
         f"Luật ghi trước: docs/10 mục 10.13. {'Dữ liệu mô phỏng' if n['la_mo_phong'] else 'Nguồn: ' + n['ten'] + '; chi phí, lead time là giả định'}. "
         f"Tập test, mức phục vụ 95%, quy tắc lượng đặt **{rule}** (giữ nguyên), EOQ tính lại theo S. Quy tắc kinh nghiệm / hiện trạng giữ nguyên đơn, chỉ tính lại chi phí. "
         "Đây là phân tích độ nhạy, không đổi giả định chính.", "",
         "| S so với gốc | EOQ (ngày bán, trung vị) | Lợi ích AI so với dự báo mốc | Fill AI + HC | Fill dự báo mốc | Ngày-mã thiếu AI + HC | Ngày-mã thiếu dự báo mốc | Tồn AI + HC (tr đ) | Tồn dự báo mốc (tr đ) | CP liên quan AI + HC (tr đ) | CP liên quan dự báo mốc (tr đ) | CP liên quan hiện trạng (tr đ) |",
         "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, v in kq.items():
        L.append(f"| × {so(k, 2)} | {so(v['eoq_ngay'])} | {'+' if v['loi_ich'] >= 0 else ''}{so(v['loi_ich'])}% | {so(v[f'fill_rate_{AI}'], 2)}% | {so(v[f'fill_rate_{MOC}'], 2)}% | "
                 f"{so(v[f'ngay_thieu_{AI}'], 0)} | {so(v[f'ngay_thieu_{MOC}'], 0)} | {so(v[f'ton_tb_{AI}'])} | {so(v[f'ton_tb_{MOC}'])} | {so(v[f'cplq_{AI}'])} | {so(v[f'cplq_{MOC}'])} | {so(v[f'cplq_{HT}'])} |")
    L += ["", f"**Theo luật:** lợi ích AI ở S × 0,1 {'cao hơn' if kl['chenh_diem'] >= 0 else 'thấp hơn'} ở S × 1 {so(abs(kl['chenh_diem']))} điểm %, "
          f"ngưỡng {so(NGUONG_DIEM)} điểm → **{'lợi ích AI phụ thuộc chi phí đặt' if kl['phu_thuoc'] else 'không phụ thuộc rõ'}**.", ""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
