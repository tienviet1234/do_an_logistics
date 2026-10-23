# Đồ án: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho

Dữ liệu là **mô phỏng** (không phải số liệu kho thật). Ngày bão trong lịch là ngày thật,
mức độ tác động và các đột biến khác là giả định.

## Cài đặt
    pip install -r requirements.txt

## Chạy (theo thứ tự, mở terminal tại thư mục do_an_logistics)
    python src/lam_sach.py      # 1. làm sạch dữ liệu thô -> data/clean/, báo cáo -> reports/bao_cao_lam_sach.md
    python src/dac_trung.py     # 2. tạo đặc trưng -> data/features/, báo cáo -> reports/bao_cao_dac_trung.md
    python src/eda.py           # 3. vẽ 8 hình khám phá -> reports/eda/, nhận xét -> reports/bao_cao_eda.md
    python src/danh_gia.py      # 4. chạy khung đánh giá với Naive, Seasonal Naive -> reports/ket_qua_mo_hinh.csv
    python src/mo_hinh_baseline.py   # 5. mô hình mốc: TB trượt, ETS, ARIMA (nhóm A), Croston, TSB (~45 phút)
    python src/mo_hinh_prophet.py    # 6. Prophet từng SKU (~25 phút; chạy tiếp được, --lam-lai để chạy lại từ đầu)
    python src/mo_hinh_lightgbm.py   # 7. LightGBM chung 121 SKU (~2 phút) + độ quan trọng đặc trưng
    python src/mo_hinh_lightgbm.py --tap validation2 ; python src/mo_hinh_prophet.py --tap validation2   # 8. dự báo trên validation vòng 2 (~15 phút)
    python src/chon_mo_hinh.py --vong 2   # 9. chọn/kết hợp mô hình -> reports/chon_mo_hinh_vong2.md
    python src/tong_hop_ket_qua.py   # 10. bảng so sánh mọi mô hình -> reports/bang_so_sanh_test.md
    python src/nap_database.py       # 11. đẩy toàn bộ dữ liệu + kết quả vào CSDL data/kho_hang.db, tự kiểm tra toàn vẹn (~2 phút)
    python src/tao_trang_luong.py    # 12. trang trình bày luồng hệ thống -> trinh_bay/luong_he_thong.html (mở bằng trình duyệt)
    python src/ton_kho.py            # 13. GĐ F: chọn quy tắc trên validation, mô phỏng tồn kho 12 tháng test, ghi CSDL -> reports/ton_kho_so_sanh.md
    python src/do_nhay.py            # 13b. thử độ nhạy: tắc cảng, lead time dài thêm, chi phí tăng -> CSDL, reports/do_nhay.md (~2 phút)
    python src/bieu_do_ket_qua.py    # 14. 7 biểu đồ kết quả cho Chương 4 (đọc CSDL) -> reports/ket_qua/
    streamlit run app/dashboard.py   # 15. GĐ G: dashboard 5 khu (chỉ đọc CSDL), tự mở trình duyệt http://localhost:8501
    python src/xuat_power_bi.py      # 16. xuất CSV cho Power BI -> reports/power_bi/ (hướng dẫn: docs/12_power_bi.md)
    python src/xem_database.py       # chạy các truy vấn mẫu trong database/truy_van_mau.sql

Lệnh phụ (ít dùng):
    python src/sinh_du_lieu.py <thu_muc_ra>                 # sinh lại toàn bộ dữ liệu mô phỏng (ra 1 thư mục, tự chia vào data/)
    python src/docx_sang_md.py <file.docx> <file.md>        # chuyển file Word sang Markdown
    python src/md_sang_docx.py                              # chuyển báo cáo GĐ2 (.md) sang Word -> reports/word/

## Thư mục
- data/raw: dữ liệu thô có lỗi cài sẵn (thiếu qty_out, nhập sai gấp 10-100 lần, dòng trùng)
- data/reference: SKU master, lịch lễ (định dạng Prophet), ngày nghỉ kho, sự kiện đột biến, lịch khuyến mãi theo SKU
- data/answer_key: bản sạch gốc và nhật ký lỗi, chỉ dùng để kiểm tra script, không đưa vào mô hình
- data/clean: kết quả sau làm sạch
- src: sinh_du_lieu.py (sinh lại dữ liệu), lam_sach.py
- reports: báo cáo làm sạch và 2 file Excel tổng hợp
- app: dashboard.py (GĐ G, Streamlit, chỉ đọc CSDL `data/kho_hang.db`); giao diện: `.streamlit/config.toml`

## Tài liệu ngữ cảnh cho AI
- `CLAUDE.md`: điểm vào, quy tắc bắt buộc, thứ tự đọc.
- `docs/`: tình hình dự án, thuật ngữ, mô tả dữ liệu, lịch sale, sự kiện đột biến, thuật toán, nguyên nhân chi phí.
