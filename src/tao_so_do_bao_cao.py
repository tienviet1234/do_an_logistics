"""Tao trang so do chi tiet cac luong bao cao: moi bao cao tu du lieu nao, chuong trinh nao, ra tep nao, dung o dau.
Kiem tra moi duong dan ghi trong so do co ton tai that (sai ten / thieu tep -> bao loi), nen so do khong lech voi du an.
Chay: python src/tao_so_do_bao_cao.py   -> trinh_bay/so_do_bao_cao.html (mo them ?luong=1 ... ?luong=6 de xem tung luong)
"""
import glob
import html
import os
import sys

OUT = "trinh_bay/so_do_bao_cao.html"

# Moi dong: (dau vao, chuong trinh, viec lam, tep bao cao / ket qua, dung o dau). Muc co dau / hoac * la duong dan duoc kiem tra.
LUONG = [
    ("Luồng 1. Báo cáo dữ liệu", "Từ dữ liệu thô đến các báo cáo mô tả dữ liệu. Đây là nền của mọi báo cáo phía sau.", [
        (["data/reference/gia_thi_truong.csv", "data/reference/sku_master_mo_phong.csv"], "src/cap_nhat_gia.py", "Cập nhật giá 37 mã theo giá bán lẻ thị trường",
         ["data/reference/sku_master.csv", "reports/cap_nhat_gia.md"], ["Word mục 1.4", "Danh mục mã hàng cho bước sau"]),
        (["data/raw/giao_dich_nhap_xuat_ton_THO.csv", "data/reference/sku_master.csv", "data/reference/lich_ngay_nghi_kho.csv"], "src/lam_sach.py",
         "Bỏ dòng trùng, sửa dòng lỗi, đánh dấu ngày hết hàng và ngày kho nghỉ", ["data/clean/giao_dich_sach.csv", "reports/dong_da_sua.csv", "reports/bao_cao_lam_sach.md"], ["Word mục 2.2"]),
        (["data/clean/giao_dich_sach.csv", "data/reference/lich_su_kien_prophet.csv", "data/reference/lich_khuyen_mai.csv", "data/reference/su_kien_dot_bien.csv"], "src/dac_trung.py",
         "Tạo đặc trưng lịch, lễ, khuyến mãi; phân nhóm ABC × XYZ", ["data/features/dac_trung.csv", "data/features/phan_loai_sku.csv", "reports/bao_cao_dac_trung.md"], ["Word mục 2.3, 2.4", "Đầu vào mọi mô hình dự báo"]),
        (["data/features/dac_trung.csv", "data/features/phan_loai_sku.csv"], "src/eda.py", "Phân tích mùa vụ, thứ trong tuần, tác động khuyến mãi",
         ["reports/eda/h0*.png", "reports/eda/thong_ke_mo_ta.csv", "reports/bao_cao_eda.md"], ["Word mục 2.5, Hình 2.1"]),
    ]),
    ("Luồng 2. Báo cáo dự báo", "Mỗi mô hình đi qua cùng một khung đánh giá (src/danh_gia.py), rồi được so sánh và chọn theo luật ghi trước.", [
        (["data/features/dac_trung.csv"], "src/mo_hinh_baseline.py", "Các mô hình mốc: lặp tuần trước, trung bình trượt, ETS, Croston, TSB, ARIMA",
         ["reports/du_bao/tb_truot_28_test.csv", "reports/ket_qua_mo_hinh.csv"], ["Word Bảng 3.1"]),
        (["data/features/dac_trung.csv", "data/reference/lich_su_kien_prophet.csv"], "src/mo_hinh_prophet.py", "Prophet: mỗi mã một mô hình",
         ["reports/du_bao/prophet_test.csv", "reports/ket_qua_mo_hinh.csv"], ["Word Bảng 3.1"]),
        (["data/features/dac_trung.csv"], "src/mo_hinh_lightgbm.py", "LightGBM: một mô hình chung 121 mã",
         ["reports/du_bao/lightgbm_test.csv", "reports/lightgbm_quan_trong.csv"], ["Word Bảng 3.1"]),
        (["reports/du_bao/prophet_test.csv", "reports/du_bao/lightgbm_test.csv"], "src/chon_mo_hinh.py", "Ghép theo nhóm XYZ, dò trọng số trên validation",
         ["reports/chon_mo_hinh.md", "reports/chon_mo_hinh_vong2.md"], ["Word Bảng 3.2 (vòng 2)"]),
        (["data/features/dac_trung.csv", "data/reference/lich_su_kien_prophet.csv", "reports/du_bao/prophet_test.csv"], "src/nang_cap_du_bao.py", "Dự báo theo tầm, lịch sự kiện, âm lịch",
         ["reports/du_bao/ket_hop_v3_test.csv", "reports/nang_cap_du_bao.md"], ["Word Bảng 3.2 (vòng 3)"]),
        (["data/features/dac_trung.csv", "reports/nang_cap_du_bao_trang_thai.json"], "src/nang_cap_du_bao_v4.py", "Cập nhật mỗi tuần, khoảng 80 / 95%, sàn sai số, bảng rủi ro",
         ["reports/du_bao/ket_hop_v4_test.csv", "reports/nang_cap_du_bao_v4.md", "reports/rui_ro_du_bao.md", "reports/rui_ro_du_bao.csv"], ["Word mục 3.5, Bảng 4.1", "Mô hình đang dùng"]),
        (["data/features/dac_trung.csv", "reports/du_bao/ket_hop_v4_test.csv"], "src/mo_hinh_dl.py", "Học sâu LSTM và RNN, ghép thử với mô hình đang dùng",
         ["reports/mo_hinh_dl.md", "reports/mo_hinh_dl_trang_thai.json"], ["docs/10 mục 9.7"]),
        (["reports/du_bao/*_test.csv"], "src/tong_hop_ket_qua.py", "Gom và xếp hạng mọi mô hình trên cùng tập kiểm tra", ["reports/bang_so_sanh_test.md", "reports/bang_so_sanh_test.csv"], ["Word Bảng 3.1"]),
    ]),
    ("Luồng 3. Báo cáo tồn kho", "Kết quả dự báo được nạp vào cơ sở dữ liệu, sau đó mô phỏng tồn kho đọc từ đó và ghi kết quả lại.", [
        (["data/clean/giao_dich_sach.csv", "reports/ket_qua_mo_hinh.csv", "reports/du_bao/ket_hop_v4_test.csv", "data/answer_key/nhu_cau_that.csv"], "src/nap_database.py",
         "Nạp mọi dữ liệu và dự báo vào CSDL, kiểm tra toàn vẹn. Nhu cầu thật chỉ dùng để chấm tồn kho", ["data/kho_hang.db"], ["Mọi báo cáo phía sau", "DB Browser for SQLite"]),
        (["data/kho_hang.db"], "src/ton_kho.py", "Tính SS, ROP, EOQ; chọn quy tắc đặt hàng trên validation2; mô phỏng 12 tháng, 4 chính sách, 3 mức phục vụ",
         ["reports/ton_kho_chon_quy_tac.md", "reports/ton_kho_so_sanh.md"], ["Word Bảng 5.1 đến 5.3", "Bảng tham_so_ton_kho, ket_qua_ton_kho, mo_phong_ngay"]),
        (["data/kho_hang.db"], "src/do_nhay.py", "Thử tắc cảng, lead time dài thêm, chi phí tăng", ["reports/do_nhay.md"], ["Word Bảng 6.1", "Bảng ket_qua_do_nhay"]),
        (["data/kho_hang.db"], "src/chi_so_kho.py", "Vòng quay, số ngày tồn kho, tồn dư theo chính sách và nhóm XYZ", ["reports/chi_so_kho.md"], ["Dashboard, màn Kịch bản & kết quả"]),
        (["data/kho_hang.db"], "src/gom_don.py", "Gom đơn theo nhà cung cấp: gom cùng ngày, đặt kèm; chỉ đọc CSDL", ["reports/gom_don.md", "reports/gom_don_trang_thai.json"], ["Dashboard, màn Kịch bản & kết quả"]),
        (["data/kho_hang.db"], "src/cham_diem_ncc.py", "Chấm điểm nhà cung cấp theo đúng hạn và độ ổn định; cảnh báo giao chậm", ["reports/cham_diem_ncc.md", "reports/cham_diem_ncc.csv"], ["Dashboard, màn Kịch bản & kết quả"]),
        (["data/kho_hang.db"], "src/rang_buoc_kho.py", "Hạn sử dụng theo lô (FIFO) và sức chứa theo vùng: hàng loại, trần lượng đặt, thuê ngoài hay cắt đơn", ["reports/rang_buoc_kho.md", "reports/rang_buoc_kho_trang_thai.json"], ["Dashboard, màn Kịch bản & kết quả"]),
        (["data/kho_hang.db"], "src/newsvendor_mua_vu.py", "Newsvendor cho hàng chỉ bán dịp lễ: đặt một lần trước mùa theo tỉ số Cu/Co, so với quy tắc hiện tại", ["reports/newsvendor_mua_vu.md", "reports/newsvendor_mua_vu_trang_thai.json"], ["Dashboard, màn Kịch bản & kết quả"]),
        (["du_lieu_nguon/m5", "data/m5", "du_lieu_nguon/dominicks/theo_tuan.csv.gz"], "src/nguon/m5_kho.py", "Dựng bộ dữ liệu kho từ số bán thật M5: giá thật, khuyến mãi suy từ giá, biên lãi Dominick's; số bán giữ nguyên", ["du_lieu_nguon/m5_kho/data/kho_hang.db", "du_lieu_nguon/m5_kho/reports/ton_kho_so_sanh.md"], ["Chương đánh giá của đồ án"]),
        (["data/kho_hang.db"], "src/do_nhay_chi_phi_dat.py", "Độ nhạy theo chi phí đặt S × 0,1 đến × 2: lợi ích AI có phụ thuộc giả định chi phí đặt không", ["reports/do_nhay_chi_phi_dat.md", "reports/do_nhay_chi_phi_dat_trang_thai.json"], ["Chương đánh giá của đồ án"]),
        (["data/kho_hang.db", "src/sinh_du_lieu.py"], "src/canh_bao_lech_v2.py", "Cảnh báo dự báo lệch (tracking signal theo tuần): lệch kéo dài và đột biến; vòng 1 ở src/canh_bao_lech.py", ["reports/canh_bao_lech_v2.md", "reports/canh_bao_lech.md"], ["Chương đánh giá của đồ án"]),
        (["data/features/dac_trung.csv", "data/reference"], "src/du_bao_tuong_lai.py", "Dự báo 28 ngày chưa xảy ra bằng mô hình đang chọn (lịch biết trước mở rộng: src/tuong_lai.py); M5: src/du_bao_tuong_lai_kc.py", ["reports/du_bao/ket_hop_v4_tuong_lai.csv", "reports/du_bao_tuong_lai.md"], ["Dashboard, màn Dự báo"]),
        (["data/kho_hang.db"], "src/tru_hang_live.py", "Trữ hàng cho phiên livestream: newsvendor hai bước, thử khi thực tế khác giả định, giá trị theo dõi theo giờ", ["reports/tru_hang_live.md", "reports/tru_hang_live_trang_thai.json"], ["Dashboard, màn Mặt hàng"]),
        (["data/dominicks", "data/kho_hang.db"], "src/phan_tich_dominicks.py", "Đối chiếu giả định với số bán thật Dominick's: hệ số deal, mức tài trợ, biên lãi, độ co giãn", ["reports/dominicks.md", "reports/dominicks_trang_thai.json", "reports/dominicks_he_so_deal.json", "reports/tru_hang_live_sau_doi_chieu.md"], ["Chương đánh giá của đồ án", "Dashboard, màn Mặt hàng"]),
    ]),
    ("Luồng 4. Báo cáo trình bày", "Mọi hình, bảng và màn hình đều đọc từ cơ sở dữ liệu, nên cùng một con số ở mọi nơi.", [
        (["data/kho_hang.db"], "src/bieu_do_ket_qua.py", "Vẽ 7 biểu đồ kết quả kèm chú thích tính từ dữ liệu", ["reports/ket_qua/k0*.png", "reports/bao_cao_bieu_do_ket_qua.md"], ["Word Hình 3.1, 3.2, 5.1, 5.2, 6.1"]),
        (["data/kho_hang.db"], "app/dashboard.py", "Dashboard 4 màn: Hôm nay, Mặt hàng, Kịch bản & kết quả, Dữ liệu & phương pháp", ["app/trang/hom_nay.py", "app/trang/mat_hang.py", "app/trang/ket_qua.py", "app/trang/du_lieu.py"], ["Demo trước hội đồng", "Người lập kế hoạch kho"]),
        (["data/kho_hang.db"], "src/xuat_power_bi.py", "Xuất mô hình hình sao và sổ đối chiếu số liệu", ["reports/power_bi/*.csv", "reports/power_bi/so_doi_chieu.md"], ["Power BI (docs/12)"]),
        (["data/kho_hang.db"], "src/tao_trang_luong.py", "Trang luồng nghiệp vụ, luồng dữ liệu, cơ sở dữ liệu", ["trinh_bay/luong_he_thong.html"], ["Trình bày nhiệm vụ của giảng viên"]),
    ]),
    ("Luồng 5. Báo cáo đồ án (Word)", "Số liệu được gom tự động rồi mới đưa vào văn bản, không gõ tay, và được đối chiếu lại với cơ sở dữ liệu.", [
        (["data/kho_hang.db", "reports/ket_qua_mo_hinh.csv", "reports/gom_don.md", "reports/cham_diem_ncc.md", "reports/tru_hang_live.md", "reports/dominicks.md"], "src/so_lieu_do_an.py", "Sổ số liệu đồ án: gom mọi số, ghi nguồn, đánh dấu phần chưa có", ["reports/so_lieu_do_an.md"], ["Nguồn số khi viết đồ án"]),
        (["data/kho_hang.db", "reports/nang_cap_du_bao_v4_trang_thai.json", "reports/ton_kho_chon_quy_tac.md", "reports/rui_ro_du_bao.csv"], "src/bao_cao_word/gom_so_lieu.py", "Gom mọi con số của báo cáo thành một tệp JSON", ["so_lieu.json"], ["Đầu vào của bước viết Word"]),
        (["so_lieu.json", "reports/ket_qua/k0*.png", "reports/eda/h04_chi_so_mua.png"], "src/bao_cao_word/tao_bao_cao.js", "Viết báo cáo: bìa, mục lục, 8 chương, phụ lục", ["reports/word/bao_cao_tong_hop_do_an.docx"], ["Nộp và in"]),
        (["reports/word/bao_cao_tong_hop_do_an.docx"], "Microsoft Word", "Cập nhật mục lục, xuất PDF, soát từng trang", ["reports/word/bao_cao_tong_hop_do_an.pdf"], ["Gửi giảng viên"]),
        (["data/kho_hang.db", "reports/nang_cap_du_bao_v4_trang_thai.json"], "src/bao_cao_word/doi_chieu.py", "Đối chiếu tự động các con số đã ghi trong tài liệu với cơ sở dữ liệu", ["Kết luận khớp / lệch"], ["Kiểm tra trước khi nộp"]),
    ]),
]
KHONG_PHAI_TEP = {"Microsoft Word", "so_lieu.json", "Kết luận khớp / lệch"}


def ton_tai(p):
    return p in KHONG_PHAI_TEP or bool(glob.glob(p))


def kiem_tra():
    thieu = sorted({p for _, _, ds in LUONG for v, ct, _, r, _ in ds for p in [*v, ct, *r] if not ton_tai(p)})
    if "--chua_co_word" in sys.argv:   # chay lai tu dau (src/chay_lai_toan_bo.py): bao cao Word dung tay sau, chua co
        bo = [p for p in thieu if p.startswith("reports/word/")]
        thieu = [p for p in thieu if p not in bo]
        if bo:
            print("Bo qua kiem tra (bao cao Word chua dung trong lan chay nay):\n  " + "\n  ".join(bo))
    if thieu:
        sys.exit("Duong dan trong so do khong ton tai:\n  " + "\n  ".join(thieu))


def the(ds, lop):
    return "".join(f'<div class="{lop}">{html.escape(os.path.basename(x) if "/" in x else x)}'
                   f'{f"<small>{html.escape(os.path.dirname(x))}/</small>" if "/" in x else ""}</div>' for x in ds)


MUI = '<div class="mui"><svg width="20" height="16" viewBox="0 0 20 16" aria-hidden="true"><path d="M0 8h13" stroke="#5b6675" stroke-width="2"/><path d="M11 2l8 6-8 6z" fill="#5b6675"/></svg></div>'


def luong(i, ten, mo_ta, ds):
    dong = "".join(
        f'<div class="dong"><div class="o vao">{the(v, "tep")}</div>{MUI}<div class="o ct"><b>{html.escape(os.path.basename(ct))}</b><span>{html.escape(viec)}</span></div>{MUI}'
        f'<div class="o ra">{the(r, "tep bc")}</div>{MUI}<div class="o dung">{"".join(f"<div>{html.escape(x)}</div>" for x in d)}</div></div>'
        for v, ct, viec, r, d in ds)
    return (f'<section class="luong" id="luong_{i}"><h1>{html.escape(ten)}</h1><p>{html.escape(mo_ta)}</p><div class="dau"><div>Đầu vào</div><i></i><div>Chương trình</div><i></i>'
            f'<div>Báo cáo, tệp kết quả</div><i></i><div>Dùng ở đâu</div></div>{dong}<div class="chan">Dữ liệu mô phỏng. Đồ án: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho.</div></section>')


def tong_quan():
    khoi = "".join(f'<div class="khoi k{i}"><b>{html.escape(t.split(". ")[1])}</b>' + "".join(f"<div>{html.escape(os.path.basename(p))}</div>" for _, _, _, r, _ in ds for p in r if p.endswith(".md") or p.endswith(".docx") or p.endswith(".html"))
                   + "</div>" + ('<div class="mui"><svg width="20" height="16" viewBox="0 0 20 16" aria-hidden="true"><path d="M0 8h13" stroke="#5b6675" stroke-width="2"/><path d="M11 2l8 6-8 6z" fill="#5b6675"/></svg></div>' if i < len(LUONG) else "")
                   for i, (t, _, ds) in enumerate(LUONG, 1))
    return (f'<section class="luong" id="luong_0"><h1>Tổng quan các luồng báo cáo</h1><p>Năm luồng nối tiếp nhau. Chữ trong mỗi khối là các tệp báo cáo chính của luồng đó; chi tiết ở từng sơ đồ tiếp theo.</p>'
            f'<div class="tq">{khoi}</div><div class="chan">Dữ liệu mô phỏng. Đồ án: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho.</div></section>')


CSS = """
:root { --muc:#1f2a37; --phu:#5b6675; --vien:#c9d2dc; }
* { box-sizing:border-box; } body { margin:0; background:#fff; color:var(--muc); font-family:"Segoe UI",Arial,sans-serif; }
.luong { width:1280px; padding:26px 30px 20px; display:none; } .luong.hien { display:block; }
h1 { font-size:22px; margin:0 0 4px; } p { color:var(--phu); font-size:13.5px; margin:0 0 14px; }
.dau,.dong { display:grid; grid-template-columns:3fr 22px 3.1fr 22px 3fr 22px 2.1fr; gap:6px; align-items:stretch; }
.dau { font-size:12px; font-weight:700; color:var(--phu); letter-spacing:.03em; text-transform:uppercase; margin-bottom:6px; }
.dong { margin-bottom:9px; } .o { border:1px solid var(--vien); border-radius:8px; padding:7px 9px; font-size:12.5px; line-height:1.34; }
.vao { background:#f4f6f8; } .ct { background:#fdf3dc; border-color:#d9b873; } .ra { background:#e8f1fb; border-color:#9dbfe0; } .dung { background:#e6f4ea; border-color:#a5cfb1; }
.ct b { display:block; font-family:Consolas,monospace; font-size:13.5px; margin-bottom:2px; } .ct span { color:#3d4652; }
.tep { font-family:Consolas,monospace; font-size:12px; overflow-wrap:anywhere; margin-bottom:3px; } .tep:last-child { margin-bottom:0; } .tep small { display:block; font-size:10.5px; color:var(--phu); margin-top:-1px; }
.bc { font-weight:600; } .bc small { font-weight:400; } .dung div { margin-bottom:3px; } .dung div:last-child { margin-bottom:0; }
.mui { display:flex; align-items:center; justify-content:center; }
.chan { margin-top:10px; font-size:11.5px; color:var(--phu); }
.tq { display:flex; gap:5px; align-items:stretch; } .khoi { flex:1; min-width:0; border:1px solid var(--vien); border-radius:8px; padding:9px 9px; font:11.5px/1.45 Consolas,monospace; overflow-wrap:anywhere; }
.khoi b { display:block; font:700 14px/1.3 "Segoe UI",Arial,sans-serif; margin-bottom:7px; } .khoi div { margin-bottom:4px; }
.k1 { background:#eef2f6; } .k2 { background:#fdf3dc; } .k3 { background:#e6f4ea; } .k4 { background:#e8f1fb; } .k5 { background:#fbe9e7; }
"""

if __name__ == "__main__":
    kiem_tra()
    than = tong_quan() + "".join(luong(i, *x) for i, x in enumerate(LUONG, 1))
    js = ('<script>const so=new URLSearchParams(location.search).get("luong");document.querySelectorAll(".luong").forEach(s=>{if(so===null||s.id==="luong_"+so)s.classList.add("hien");});</script>')
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Luồng báo cáo</title><style>{CSS}</style></head><body>{than}{js}</body></html>')
    print("Da ghi", OUT, "| moi duong dan deu ton tai")
