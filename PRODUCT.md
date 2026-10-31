# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Người dùng chính: người lập kế hoạch kho** của một kho tổng (trung tâm phân phối) chuỗi siêu thị / bách hóa, 121 mã hàng. Mỗi ngày làm việc họ cần biết mã nào sắp hết, mã nào phải đặt, đặt bao nhiêu, và **tự ra quyết định** (chọn ngày, chỉnh mức phục vụ, xem điều gì xảy ra nếu…). Hệ thống chỉ cho ra kết quả khi người dùng tương tác (xác nhận của người dùng, 31/10).
- **Bối cảnh trình bày:** sinh viên ngành Logistics (hướng thực tập điều vận) dùng chính công cụ này để demo trước hội đồng bảo vệ đồ án (30–31/12/2026): thao tác trực tiếp, hội đồng xem hệ thống phản hồi theo từng thao tác.
- Người xem phụ: giảng viên hướng dẫn, hội đồng, nhà tuyển dụng thực tập (đọc kết quả, hỏi "nếu… thì sao").

## Product Purpose

Công cụ hỗ trợ quyết định đặt hàng: dự báo nhu cầu 28 ngày tới bằng AI (kết hợp LightGBM + Prophet theo nhóm hàng), tính tồn kho an toàn (SS), điểm đặt hàng (ROP), lượng đặt kinh tế (EOQ), cảnh báo mã cần xử lý theo ngày, và so sánh chính sách đặt hàng (AI so với dự báo đơn giản và hiện trạng). Thành công = người lập kế hoạch thấy ngay việc cần làm hôm nay, hiểu vì sao, và tự thử được phương án; hội đồng thấy rõ hệ thống chạy thật và đem lại lợi ích đo được (Fill Rate, chi phí, ngày thiếu hàng).

## Positioning

Không phải báo cáo tĩnh: mọi con số đọc trực tiếp từ cơ sở dữ liệu của dự án, có quy trình chạy lại được, đánh giá trung thực (chọn mô hình trên validation, test chạy một lần, thử độ nhạy tắc cảng / chi phí), và nói rõ cái gì là dữ liệu thật, cái gì là giả định.

## Operating Context

- Chạy trên laptop cá nhân (Windows, không cần mạng), mở bằng 1 lệnh `streamlit run app/dashboard.py`; dữ liệu từ SQLite `data/kho_hang.db` (chỉ đọc).
- Trình bày bằng máy chiếu ở trường (độ phân giải có thể thấp — suy luận, chưa xác nhận).
- Quy trình nghiệp vụ: kho ghi nhập – xuất – tồn → dự báo → SS/ROP/EOQ → cảnh báo, đề xuất đơn → người lập kế hoạch duyệt → mua hàng / điều vận lên kế hoạch xe.
- Giai đoạn kiểm tra là 12 tháng test (01/10/2025 – 29/09/2026); "hôm nay" trong công cụ là một ngày người dùng chọn trong giai đoạn này (phát lại mô phỏng).

## Capabilities and Constraints

- Hiện có (Streamlit, `app/dashboard.py` + `app/trang/`, từ 31/10): 4 màn Hôm nay (duyệt đơn, phiếu đặt hàng), Mặt hàng ("Thử nếu…"), Kịch bản & kết quả, Dữ liệu & phương pháp; bộ lọc chung, lọc chéo, đi sâu.
- Stack: Python + Streamlit + Altair (giữ theo quyết định `docs/09` mục 4 — suy luận người dùng không đổi; chưa hỏi lại). Mọi tính toán nặng (mô hình, mô phỏng) chạy bằng script trong `src/`, công cụ chỉ đọc kết quả; tính lại nhẹ (VD SS/ROP theo mức phục vụ người dùng chọn) được phép trong giao diện.
- Thuật ngữ bắt buộc dùng đúng: Fill Rate, SS (tồn kho an toàn), ROP (điểm đặt hàng), EOQ (lượng đặt kinh tế), MOQ, lead time, WMAPE, Bias, ABC/XYZ; luôn kèm giải thích ngắn bằng tiếng Việt.
- Ngôn ngữ giao diện: tiếng Việt.
- Duyệt đơn: chỉ giữ trong phiên làm việc + tải phiếu đặt hàng CSV (người dùng chọn phương án (a), 31/10); không ghi vào CSDL.

## Evidence on Hand

- Dữ liệu **mô phỏng** 121 mã × 1.096 ngày; giá 37 mã theo giá bán lẻ thị trường tra ngày 24/10/2026 (`data/reference/gia_thi_truong.csv`). Không có dữ liệu kho thật, không có khách hàng, đánh giá hay số liệu thật nào khác — không được bịa.
- Kết quả thật của dự án: `reports/ton_kho_so_sanh.md`, `reports/do_nhay.md`, `reports/bang_so_sanh_test.md`, `reports/ket_qua/k01–k07.png`, `docs/10_bao_cao_giai_doan_2.md`.

## Product Principles

1. **Việc cần làm hôm nay đi trước, giải thích theo sau:** mở ra là thấy mã nào phải xử lý; số liệu chi tiết chỉ hiện khi cần.
2. **Người dùng quyết định, hệ thống trả lời:** mọi màn hình chính có ít nhất một điều khiển làm thay đổi kết quả (ngày, mức phục vụ, kịch bản, mã hàng).
3. **Không có con số trần:** mỗi chỉ số kèm ý nghĩa bằng lời và so với mốc (dự báo đơn giản, hiện trạng).
4. **Trung thực:** luôn phân biệt dữ liệu mô phỏng / giả định / nguồn thật; không làm đẹp kết quả.
5. **Trình bày được:** đọc rõ khi chiếu, thao tác ít bước, không phải cuộn dài để thấy điều quan trọng.

## Accessibility & Inclusion

Trạng thái (hết hàng / cần đặt / dưới ROP / đủ hàng) luôn có chữ + biểu tượng, không chỉ dựa vào màu. Chữ và số đủ lớn để đọc trên máy chiếu.
