"""So so lieu de viet do an: gom moi so lieu ve 1 tep, doc tu CSDL va tep ket qua, ghi ro nguon va phan nao chua co. KHONG ghi so bang tay.
Chay lai sau moi buoc: python src/so_lieu_do_an.py  -> reports/so_lieu_do_an.md
"""
import json
import os
import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RA = "reports/so_lieu_do_an.md"
CHUA_CO = "⏳ Chưa có kết quả."


def so(v, nd=1):
    return f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pt(v, nd=1):
    """Ti le -> phan tram co dau."""
    return f"{'+' if v > 0 else '−' if v < 0 else ''}{so(abs(100 * v), nd)}%"


def bang(dau, dong):
    return ["| " + " | ".join(dau) + " |", "|" + "---|" * len(dau)] + ["| " + " | ".join(str(x) for x in d) + " |" for d in dong]


def doc_tep(f):
    """Noi dung tep bao cao (bo tieu de dau); khong co -> bao chua co, khong loi."""
    if not os.path.exists(f):
        return [CHUA_CO]
    L = open(f, encoding="utf-8").read().splitlines()
    return L[1:] if L and L[0].startswith("# ") else L


def doc_json(f):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None


def muc_mo_hinh(kq, ten, tap):
    x = kq[(kq.mo_hinh == ten) & (kq.tap == tap)]
    return None if x.empty else x.iloc[0]


def bang_mo_hinh(kq, ds, tap):
    dong = []
    for ten, nhan in ds:
        r = muc_mo_hinh(kq, ten, tap)
        if r is not None:
            dong.append((r.WMAPE, [nhan, so(r.WMAPE, 3), so(r.WMAPE_tuan, 3), pt(r.Bias_pct), so(r.WMAPE_X, 3), so(r.WMAPE_Y, 3), so(r.WMAPE_Z, 3)]))
    return bang(["Mô hình", "WMAPE ngày", "WMAPE tuần", "Bias", "X", "Y", "Z"], [d for _, d in sorted(dong, key=lambda x: x[0])])


MO_HINH = [("ket_hop_v4", "Kết hợp v4, cập nhật tuần (đang dùng)"), ("ket_hop_v3", "Kết hợp v3, cập nhật 28 ngày"), ("ket_hop_theo_nhom_v2", "Kết hợp theo nhóm v2"), ("lightgbm", "LightGBM"), ("lgb_v3_AB", "LightGBM theo tầm"),
           ("prophet", "Prophet"), ("prophet_addi", "Prophet additive"), ("lstm_tuan", "LSTM"), ("rnn_tuan", "RNN"), ("ket_hop_v5", "Ghép v4 + LSTM (không đạt luật)"), ("tide_tuan", "TiDE"), ("nhits_tuan", "N-HiTS"), ("tft_tuan", "TFT gọn"),
           ("ket_hop_nf", "Ghép v4 + mô hình mới"), ("tb_truot_28_tuan", "TB trượt 28 ngày, cập nhật tuần"), ("tb_truot_28", "TB trượt 28 ngày"), ("croston_sba", "Croston SBA"), ("tsb", "TSB"), ("ets", "ETS"), ("naive", "Naive"), ("seasonal_naive_7", "Seasonal Naive")]


def tao():
    from csdl import doc
    kq = pd.read_csv("reports/ket_qua_mo_hinh.csv", encoding="utf-8-sig")
    n = doc("""SELECT (SELECT COUNT(*) FROM dm_sku) sku, (SELECT COUNT(DISTINCT nhom_hang) FROM dm_sku) nhom, (SELECT COUNT(*) FROM dm_nha_cung_cap) ncc, (SELECT COUNT(*) FROM giao_dich_sach) dong,
                      (SELECT COUNT(DISTINCT ngay) FROM giao_dich_sach) ngay, (SELECT MIN(ngay) FROM giao_dich_sach) tu, (SELECT MAX(ngay) FROM giao_dich_sach) den, (SELECT COUNT(*) FROM giao_dich_tho) tho,
                      (SELECT COUNT(*) FROM nhat_ky_sua_loi) sua, (SELECT AVG(het_hang) FROM giao_dich_sach WHERE la_ngay_nghi = 0) het""").iloc[0]
    abc = doc("SELECT abc_train a, xyz_train x, COUNT(*) n FROM phan_loai_sku GROUP BY 1, 2").pivot(index="a", columns="x", values="n").fillna(0).astype(int)
    v = doc("SELECT * FROM v_so_sanh_chinh_sach ORDER BY muc_phuc_vu, ma_chinh_sach")
    nhom = doc("""SELECT p.xyz_train x, k.ma_chinh_sach cs, 100.0 * SUM(da_dap_ung) / SUM(nhu_cau) fr, SUM(gia_tri_ton_tb) / 1e6 ton, SUM(loi_nhuan_mat) / 1e6 ln
                  FROM ket_qua_ton_kho k JOIN phan_loai_sku p USING (ma_sku) WHERE ROUND(muc_phuc_vu, 2) = 0.95 GROUP BY 1, 2""")
    dn = doc("SELECT * FROM v_do_nhay")
    v4 = doc_json("reports/nang_cap_du_bao_v4_trang_thai.json") or {}
    dl = doc_json("reports/mo_hinh_dl_trang_thai.json") or {}
    L = ["# Sổ số liệu đồ án", "", f"Tạo tự động lúc {datetime.now():%d/%m/%Y %H:%M} bằng `python src/so_lieu_do_an.py`: mọi số đọc từ CSDL và tệp kết quả, không ghi tay. Khi viết đồ án lấy số ở đây.",
         "", "**Lưu ý chung:** các số ở mục 1–9 là kết quả trên **dữ liệu mô phỏng**, không phải số liệu kho thật. Dữ liệu đổi thì số đổi, và mô hình được chọn có thể đổi.", "",
         "## 1. Dữ liệu (nguồn: CSDL)", ""]
    L += bang(["Hạng mục", "Giá trị"], [["Số mã / nhóm hàng / nhà cung cấp", f"{int(n.sku)} / {int(n.nhom)} / {int(n.ncc)}"], ["Thời gian", f"{n.tu} – {n.den} ({so(n.ngay, 0)} ngày)"], ["Dòng thô / sạch / đã sửa", f"{so(n.tho, 0)} / {so(n.dong, 0)} / {so(n.sua, 0)}"],
                                         ["Tỉ lệ ngày-mã hết hàng", f"{so(100 * n.het)}%"]])
    L += ["", "Ma trận ABC × XYZ (số mã):", ""] + bang(["ABC \\ XYZ"] + list(abc.columns), [[a] + list(abc.loc[a]) for a in abc.index])
    L += ["", "## 2. Dự báo trên tập kiểm tra (nguồn: `reports/ket_qua_mo_hinh.csv`)", ""] + bang_mo_hinh(kq, MO_HINH, "test")
    L += ["", "## 3. Dự báo trên validation2 (dùng để chọn mô hình)", ""] + bang_mo_hinh(kq, MO_HINH, "validation2")
    L += ["", "## 4. Sàn sai số và khoảng dự báo (nguồn: `reports/nang_cap_du_bao_v4_trang_thai.json`)", ""]
    if v4.get("san") and v4.get("test"):
        kh = v4["test"]["khoang"]
        L += [f"Sàn sai số theo ngày: {so(v4['san'][0], 3)} (X {so(v4['san'][1]['X'], 3)}, Y {so(v4['san'][1]['Y'], 3)}, Z {so(v4['san'][1]['Z'], 3)}).", ""]
        L += bang(["Mức", "Theo ngày: đúng", "Tổng lead time: đúng"], [[f"{m}%", f"{so(kh['theo_ngay'][m]['phu'])}%", f"{so(kh['lead_time'][m]['phu'])}%"] for m in ("80", "95")])
        L += ["", f"Sai số trên tổng lead time (test): {so(v4['test']['test']['v4']['lead_time'], 3)}."]
    else:
        L.append(CHUA_CO)
    L += ["", "## 5. Bảng rủi ro (nguồn: `reports/rui_ro_du_bao.md`)", ""] + doc_tep("reports/rui_ro_du_bao.md")
    L += ["", "## 6. Tồn kho theo chính sách và mức phục vụ (nguồn: CSDL, `v_so_sanh_chinh_sach`)", ""]
    L += bang(["Chính sách", "Mức phục vụ", "Fill Rate", "Ngày-mã thiếu", "Tồn TB (tr đ)", "Số lần nhập", "CP đặt + lưu", "LN mất", "CP liên quan"],
              [[r.ma_chinh_sach, f"{100 * r.muc_phuc_vu:.0f}%", f"{so(r.fill_rate_pt, 2)}%", so(r.so_ngay_sku_thieu, 0), so(r.ton_tb_trieu_vnd), so(r.so_lan_nhap, 0), so(r.tong_chi_phi_trieu), so(r.loi_nhuan_mat_trieu), so(r.chi_phi_lien_quan_trieu)] for r in v.itertuples()])
    L += ["", "Theo nhóm XYZ, mức phục vụ 95%:", ""] + bang(["Nhóm", "Chính sách", "Fill Rate", "Tồn TB (tr đ)", "LN mất (tr đ)"], [[r.x, r.cs, f"{so(r.fr)}%", so(r.ton), so(r.ln)] for r in nhom.itertuples()])
    L += ["", "## 7. Thử độ nhạy (nguồn: CSDL, `v_do_nhay`; chi tiết `reports/do_nhay.md`)", ""]
    ai = dn[dn.ma_chinh_sach == "cong_thuc_du_bao_ai_hc"]
    goc = ai[ai.nhom == "goc"].iloc[0]
    d_nhay = [["Gốc", f"{so(goc.fill_rate_pt, 2)}%", so(goc.chi_phi_lien_quan_trieu)]]
    for k, g in ai[ai.nhom == "tac_cang"].groupby("tham_so"):
        d_nhay.append([f"Tắc cảng +{int(k)} ngày (TB {len(g)} đợt)", f"{so(g.fill_rate_pt.mean(), 2)}%", so(g.chi_phi_lien_quan_trieu.mean())])
    for r in ai[~ai.nhom.isin(["goc", "tac_cang"])].itertuples():
        d_nhay.append([r.ma_kich_ban, f"{so(r.fill_rate_pt, 2)}%", so(r.chi_phi_lien_quan_trieu)])
    L += bang(["Kịch bản (AI + hiệu chỉnh)", "Fill Rate", "CP liên quan (tr đ)"], d_nhay)
    L += ["", "## 8. Logistics bổ sung", "", "### 8.1. Chỉ số kho (nguồn: `reports/chi_so_kho.md`)", ""] + doc_tep("reports/chi_so_kho.md")
    L += ["", "### 8.2. Gom đơn (nguồn: `reports/gom_don.md`)", ""] + doc_tep("reports/gom_don.md")
    L += ["", "### 8.3. Chấm điểm nhà cung cấp (nguồn: `reports/cham_diem_ncc.md`)", ""] + doc_tep("reports/cham_diem_ncc.md")
    L += ["", "### 8.4. Trữ hàng cho phiên livestream (nguồn: `reports/tru_hang_live.md`; dữ liệu không có phiên live thật, phần lớn tham số là giả định)", ""] + doc_tep("reports/tru_hang_live.md")
    L += ["", "### 8.5. Đối chiếu giả định với dữ liệu thật Dominick's (nguồn: `reports/dominicks.md`; siêu thị Mỹ 1989–1997)", ""] + doc_tep("reports/dominicks.md")
    L += ["", "### 8.6. Trữ hàng livestream, bản sau đối chiếu (nguồn: `reports/tru_hang_live_sau_doi_chieu.md`)", ""] + doc_tep("reports/tru_hang_live_sau_doi_chieu.md")
    L += ["", "### 8.7. Hạn sử dụng và sức chứa (nguồn: `reports/rang_buoc_kho.md`; hạn, thể tích, sức chứa là giả định)", ""] + doc_tep("reports/rang_buoc_kho.md")
    L += ["", "### 8.8. Newsvendor cho hàng chỉ bán dịp lễ (nguồn: `reports/newsvendor_mua_vu.md`)", ""] + doc_tep("reports/newsvendor_mua_vu.md")
    L += ["", "## 9. Học sâu trên dữ liệu mô phỏng", "", "### 9.1. LSTM, RNN (nguồn: `reports/mo_hinh_dl.md`)", ""]
    if dl.get("quyet_dinh"):
        L += [f"Quyết định theo luật: giữ **{dl['quyet_dinh']['chon']}**; học sâu tốt hơn trên validation2: {dl['quyet_dinh']['hoc_sau_tot_hon']}; trọng số ghép {dl['quyet_dinh']['w']}."]
    else:
        L.append(CHUA_CO)
    L += ["", "### 9.2. TiDE, N-HiTS, TFT (nguồn: `reports/mo_hinh_nf.md`)", ""] + doc_tep("reports/mo_hinh_nf.md")
    L += ["", "## 10. Kiểm chứng trên dữ liệu thật M5 (số bán thật, không phải mô phỏng)", "", "### 10.1. Các mô hình (nguồn: `du_lieu_nguon/m5/reports/kiem_chung.md`)", ""] + doc_tep("du_lieu_nguon/m5/reports/kiem_chung.md")
    L += ["", "### 10.2. TiDE, N-HiTS, TFT trên M5 (nguồn: `du_lieu_nguon/m5/reports/mo_hinh_nf.md`)", ""] + doc_tep("du_lieu_nguon/m5/reports/mo_hinh_nf.md")
    L += ["", "### 10.3. Tồn kho trên bộ dữ liệu dựng từ M5 (nguồn: `du_lieu_nguon/m5_kho/reports/ton_kho_so_sanh.md`; lead time, chi phí, tồn kho là giả định)", ""] + doc_tep("du_lieu_nguon/m5_kho/reports/ton_kho_so_sanh.md")
    L += ["", "## 11. Nguồn dữ liệu công khai cần trích dẫn", "", "- M5 Forecasting: bản sao Zenodo record 12636070, gốc từ Kaggle (Walmart, University of Nicosia). Zenodo ghi CC BY 4.0, người đăng là bên thứ ba: cần hỏi giảng viên.",
          "- Dominick's Dataset: Kilts Center for Marketing, University of Chicago Booth School of Business. Chỉ dùng cho nghiên cứu học thuật, phải ghi nguồn.", "",
          "## 12. Hình cho đồ án", "", "- Kết quả: `reports/ket_qua/k01`–`k07`. Khám phá dữ liệu: `reports/eda/h01`–`h08`. Sơ đồ: `reports/so_do/`.", "",
          "## 13. Luật và quyết định", "", "Toàn bộ luật ghi trước, kết quả từng vòng và nhật ký: `docs/10_bao_cao_giai_doan_2.md` (mục 9.4–9.9, 10.2–10.7, mục 14).", ""]
    return L


def ghi(L, ra=RA):
    """Ghi so so lieu ra tep. Tach khoi tao(): test goi tao() khong duoc doi bao cao (da gap: chay test tren ban thieu du lieu M5 lam mat bang M5)."""
    os.makedirs(os.path.dirname(ra) or ".", exist_ok=True)
    open(ra, "w", encoding="utf-8").write("\n".join(L))
    return ra


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    noi_dung = tao()
    print(f"Da ghi {ghi(noi_dung)}: {len(noi_dung)} dong")
