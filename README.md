# Đồ án: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho

Dữ liệu là **mô phỏng** (không phải số liệu kho thật). Ngày bão trong lịch là ngày thật,
mức độ tác động và các đột biến khác là giả định.

## Cài đặt
    pip install -r requirements.txt

## Chạy
    python src/lam_sach.py      # làm sạch dữ liệu thô -> data/clean/, báo cáo -> reports/

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
