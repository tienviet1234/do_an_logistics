# Thuật ngữ và công thức cốt lõi

Bản đầy đủ khoảng 120 thuật ngữ nằm ở `docs/Từ điển thuật ngữ viết tắt ngành Logistics & Quản lý tồn kho.docx`. Bản Markdown: `docs/02b_tu_dien_day_du.md`.

## Quản lý tồn kho
| Viết tắt | Đầy đủ | Nghĩa |
|---|---|---|
| SKU | Stock Keeping Unit | Mã quản lý tồn kho; mỗi biến thể (vị, cỡ, quy cách) là 1 SKU |
| LT | Lead Time | Thời gian từ lúc đặt hàng đến lúc hàng vào kho |
| EOQ | Economic Order Quantity | Lượng đặt tối ưu mỗi lần: EOQ = √(2DS/H) |
| S, H | Ordering cost, Holding cost | S: chi phí mỗi lần đặt. H = tỷ lệ lưu kho × giá vốn (đơn vị/năm) |
| SS | Safety Stock | Tồn kho an toàn: SS = z·σd·√LT |
| ROP | Reorder Point | Điểm đặt hàng lại: ROP = d·LT + SS |
| (s,Q) | Chính sách rà soát liên tục | Tồn hiện có ≤ s thì đặt cố định Q |
| IP | Inventory Position | Tồn thực + hàng đang đặt − hàng thiếu nợ khách |
| MOQ | Minimum Order Quantity | Số lượng đặt tối thiểu nhà cung cấp chấp nhận |
| ABC | ABC analysis | Phân loại theo giá trị: A ≤75% giá trị xuất tích lũy, B đến 92%, C còn lại |
| XYZ | XYZ analysis | Theo độ ổn định nhu cầu (CV theo tháng): X ≤0,5; Y ≤1,0; Z >1,0 |
| CV | Coefficient of Variation | Độ lệch chuẩn / trung bình |
| Stockout | Out of stock | Hết hàng khi có nhu cầu; dữ liệu bán lúc này thấp hơn cầu thật |
| SLOB | Slow-moving and Obsolete | Hàng chậm luân chuyển và lỗi thời |
| DOH | Days On Hand | Số ngày tồn kho còn đủ bán |
| ITR | Inventory Turnover Ratio | Vòng quay tồn kho = COGS / tồn kho bình quân; DOH = 365 / ITR |
| Fill Rate | Fill Rate | Tỷ lệ nhu cầu được đáp ứng ngay từ tồn kho |
| CSL | Cycle Service Level | Xác suất không hết hàng trong một chu kỳ đặt hàng; z = 1,28 (90%), 1,65 (95%), 2,33 (99%) |

Ký hiệu: D nhu cầu năm, d nhu cầu trung bình ngày, σd độ lệch chuẩn nhu cầu ngày, z hệ số theo mức phục vụ.
Khi LT cũng dao động: SS = z × √(LT·σd² + d²·σLT²).

## Dự báo và đánh giá
| Thuật ngữ | Nghĩa |
|---|---|
| Time series | Chuỗi dữ liệu theo thời gian; không được xáo trộn thứ tự khi chia train/test |
| Trend, Seasonality, Residual | Xu hướng, tính mùa vụ lặp theo chu kỳ cố định, phần còn lại (nhiễu) |
| Lag | Giá trị của k kỳ trước (lag_7 là cùng thứ tuần trước) |
| Horizon | Tầm dự báo; nên bằng hoặc lớn hơn LT cộng chu kỳ kiểm hàng |
| Intermittent demand | Nhu cầu rời rạc, nhiều ngày bằng 0; dùng Croston hoặc TSB |
| Backtest / walk-forward | Kiểm thử mô hình bằng cách lùi dần mốc thời gian; tốt hơn k-fold ngẫu nhiên |
| Overfitting | Mô hình học thuộc dữ liệu huấn luyện; sai số train thấp nhưng test cao |
| MAE | Sai số tuyệt đối trung bình |
| RMSE | Căn bình phương sai số trung bình; phạt nặng sai số lớn |
| MAPE | Sai số phần trăm; hỏng khi nhu cầu gần 0 |
| WMAPE | Tổng sai số / tổng nhu cầu thực; nên dùng cho dữ liệu theo ngày |
| MASE | MAE chia MAE của Naive trên tập train; dữ liệu theo ngày nên dùng Seasonal Naive chu kỳ 7 (m = 7). Dưới 1 là tốt hơn mốc |
| Bias | Sai số trung bình có dấu, quy ước trong đồ án: Bias = (1/n)Σ(A−F); dương là dự báo thấp hơn thực tế (dễ hết hàng) |
| FVA | Mức cải thiện so với dự báo cũ hoặc Naive |

Công thức: MAE = (1/n)Σ|A−F|; RMSE = √((1/n)Σ(A−F)²); WMAPE = Σ|A−F| / ΣA.

## Mô hình dự báo
Naive, Seasonal Naive (mốc so sánh tối thiểu), SMA/WMA, SES/Holt/Holt-Winters, ETS, ARIMA, SARIMA/SARIMAX, Prophet (đầu vào gồm 2 cột ds, y và bảng holidays), Random Forest / XGBoost / LightGBM (cần tự tạo đặc trưng lag, thứ, tháng, khuyến mãi), LSTM/GRU (cần nhiều dữ liệu; với 36 tháng theo ngày mỗi SKU thường không hơn mô hình cổ điển), Croston/TSB (nhu cầu rời rạc).
