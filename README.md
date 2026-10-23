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
    python src/tong_hop_ket_qua.py   # 7. bảng so sánh mọi mô hình -> reports/bang_so_sanh_test.md

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

## Tài liệu ngữ cảnh cho AI
- `CLAUDE.md`: điểm vào, quy tắc bắt buộc, thứ tự đọc.
- `docs/`: tình hình dự án, thuật ngữ, mô tả dữ liệu, lịch sale, sự kiện đột biến, thuật toán, nguyên nhân chi phí.
