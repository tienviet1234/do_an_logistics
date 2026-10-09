# Bố trí thuật toán và bảng so sánh mô hình


## Sheet: Bo_tri_mo_hinh

| Các thuật toán nằm ở đâu trong quy trình |  |  |  |
|---|---|---|---|
| Theo mục 6 của báo cáo Giai đoạn 1 (Bước 3 đến Bước 5, tương ứng Chương 4 của đồ án). |  |  |  |
| Bước | Mô hình | Vai trò | Dữ liệu cần |
| 3. Baseline | Naive / Seasonal Naive, Moving Average | Mốc so sánh tối thiểu | qty_out theo ngày |
| 3. Baseline | ETS (làm mượt mũ), ARIMA / SARIMA | Baseline chính thức | qty_out; SARIMAX thêm biến ngoại sinh |
| 4. Mô hình chính | Prophet | Mùa vụ, ngày lễ, dữ liệu thiếu | Sheet Lich_su_kien (định dạng holidays), cột khuyen_mai |
| 4. Học máy | XGBoost / LightGBM | Dự báo bằng đặc trưng | Lag, thứ, tháng, số ngày đến Tết, cờ sale, bao_lu_muc_do |
| 4. Tùy chọn | LSTM / GRU | Mô hình nâng cao | Cần nhiều dữ liệu, tạo chuỗi trượt (sliding window) |
| 4. Bổ sung | Croston / TSB | Hàng bán rời rạc | SKU có nhiều ngày bằng 0 |
| 5. Chọn mô hình | MAE, RMSE, WMAPE, backtest | So sánh công bằng trên cùng tập test | Chia train/test theo thời gian |

## Sheet: Truoc_va_sau_khi_chay

| Điều gì quyết định trước được, điều gì phải chờ chạy |  |  |
|---|---|---|
| Hạng mục | Thời điểm biết | Giải thích |
| Danh sách mô hình đưa vào thi (shortlist) | Quyết định trước | Dựa trên đặc điểm dữ liệu: mùa vụ, ngày lễ, hàng rời rạc, số điểm dữ liệu |
| Các bước và vị trí trong quy trình | Quyết định trước | Theo mục 6 của báo cáo |
| Quy tắc chọn mô hình | Quyết định trước | Sai số thấp nhất nhưng vẫn dễ giải thích khi bảo vệ |
| Chỉ số đánh giá và cách chia train/test | Quyết định trước | MAE, RMSE, WMAPE; chia theo thời gian, không chia ngẫu nhiên |
| Mô hình nào thắng | Chờ chạy | Phụ thuộc dữ liệu thật của kho, không đoán trước được |
| Mô hình nào thắng cho nhóm SKU nào | Chờ chạy | Kết quả thường không đồng đều giữa các nhóm hàng |
| Tham số tốt nhất (p,d,q, cửa sổ ngày lễ, độ sâu cây, số lớp LSTM) | Chờ chạy | Tìm bằng thử nghiệm trên tập validation |

## Sheet: Goi_y_theo_nhom_SKU

| Gợi ý mô hình nên thử theo nhóm SKU |  |  |
|---|---|---|
| Đây là gợi ý ban đầu để rút gọn danh sách thi, không phải kết luận; kết quả thật do backtest quyết định. |  |  |
| Nhóm | Đặc điểm | Mô hình nên thử |
| Nhóm X: nhu cầu ổn định | Biến thiên thấp, mùa vụ nhẹ | ETS, ARIMA / SARIMA, Prophet |
| Nhóm Z: mùa vụ mạnh hoặc theo sự kiện | Đỉnh theo Tết, Trung thu, mùa nóng lạnh, khai giảng | Prophet có holidays, XGBoost / LightGBM với đặc trưng sự kiện |
| Hàng bán rời rạc | Nhiều ngày bằng 0 | Croston, TSB |
| Nhu yếu phẩm khi bão lũ | Tăng đột ngột, chỉ biết trước 3 đến 5 ngày | XGBoost / Prophet với biến ngoại sinh bao_lu_muc_do; xem phần bão là cú sốc |
| Toàn bộ SKU cùng lúc | Nhiều chuỗi có đặc điểm chung | Mô hình chung (global) như XGBoost hoặc LSTM huấn luyện trên mọi SKU |

## Sheet: Luu_y_LSTM

| Lưu ý về LSTM với dữ liệu hiện có |  |
|---|---|
| Vấn đề | Nội dung |
| Số điểm dữ liệu | Mỗi SKU khoảng 1.096 điểm theo ngày; hơi ít để LSTM chạy riêng từng SKU, và hiếm khi hơn hẳn Prophet hay XGBoost. |
| Cách có cơ hội tốt hơn | Huấn luyện một mô hình chung cho cả 121 SKU, thêm đặc trưng SKU, nhóm hàng, giá. |
| Khó khăn | Cần tinh chỉnh nhiều, khó giải thích khi bảo vệ. |
| Cách làm an toàn | Xây ARIMA / ETS, Prophet, XGBoost cho Chương 4; thử LSTM như phần mở rộng. Nếu LSTM không thắng, đó vẫn là kết quả đáng viết vào đồ án. |

## Sheet: Bang_so_sanh

| Bảng so sánh mô hình (điền sau khi chạy) |  |  |  |  |  |
|---|---|---|---|---|---|
| Ô vàng là ô nhập. Dòng VÍ DỤ chỉ để xem định dạng và không tính vào xếp hạng; xóa hoặc bỏ qua khi dùng. |  |  |  |  |  |
| Mô hình | MAE | RMSE | WMAPE | Hạng theo WMAPE | Ghi chú |
| VÍ DỤ (không tính) | 12.4 | 18.9 | 0.213 |  | Dòng minh họa định dạng; WMAPE nhập dạng phần trăm (0,213 là 21,3%) |
| Seasonal Naive |  |  |  |  |  |
| Moving Average |  |  |  |  |  |
| ETS |  |  |  |  |  |
| ARIMA / SARIMA |  |  |  |  |  |
| Prophet |  |  |  |  |  |
| XGBoost / LightGBM |  |  |  |  |  |
| LSTM / GRU |  |  |  |  |  |
| Croston / TSB |  |  |  |  |  |
| Mô hình có WMAPE thấp nhất | Chưa có dữ liệu |  |  |  |  |
| WMAPE thấp nhất |  |  |  |  |  |
| Mức cải thiện so với Seasonal Naive |  |  |  |  |  |
| Chú thích: WMAPE = tổng sai số tuyệt đối ÷ tổng nhu cầu thực. Chạy tất cả mô hình trên cùng một tập test. Nếu hai mô hình gần ngang nhau, chọn mô hình đơn giản và dễ giải thích hơn. |  |  |  |  |  |