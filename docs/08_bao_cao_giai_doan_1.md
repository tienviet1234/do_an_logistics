# Báo cáo Giai đoạn 1: Kiến thức cần chuẩn bị (bản chuyển từ .docx)

## Tóm tắt cho AI (đọc phần này, chỉ mở toàn văn khi cần trích dẫn)
- Đồ án theo lộ trình **79 ngày**; Giai đoạn 1 = ngày 1–14 (chốt đề cương + Chương 2 cơ sở lý thuyết). Chương 3: thực trạng đơn vị thực tập; Chương 4: xây mô hình.
- **Luồng 8 bước (mục 6)** là khung của cả đồ án: 1 thu thập & làm sạch → 2 EDA → 3 baseline (MA, ARIMA) → 4 Prophet / XGBoost / LSTM → 5 đánh giá & chọn mô hình → 6 tính EOQ, SS, ROP → 7 dashboard (Streamlit hoặc Power BI) → 8 bảng so sánh "trước – sau" và đề xuất.
- Khuyến nghị nên giữ: dùng **độ lệch chuẩn sai số dự báo** làm σd khi tính SS (bước 6); ưu tiên SKU nhóm A; backtest cuốn chiếu; chọn mô hình đơn giản, dễ giải thích nếu sai số gần nhau.
- Hình 1–4 (sơ đồ) không chuyển được sang md, xem file .docx.

### Điểm báo cáo này KHÁC cách dự án đang làm (dự án được ưu tiên)
| Báo cáo GĐ1 nói | Dự án đang làm | Lý do |
|---|---|---|
| Thiếu dữ liệu: nội suy / forward-fill; ngoại lai: IQR, z-score | Suy `qty_out` từ đẳng thức kho (xuất = tồn đầu + nhập − tồn cuối) | Chính xác hơn khi có cột tồn; IQR dễ xóa nhầm đỉnh bão, sale |
| Chọn mô hình theo MAPE thấp nhất | Dùng **WMAPE**, MASE, Bias | MAPE hỏng khi nhu cầu ngày gần 0 (hàng thời vụ) |
| `seasonal_decompose(period=30)` | Dữ liệu ngày: chu kỳ 7 (tuần) và 365 (năm) | Không có chu kỳ 30 ngày rõ ràng |
| Ví dụ Prophet Tết `lower_window=-3` | Lịch dự án dùng −28 | Mua sắm Tết bắt đầu khoảng 4 tuần trước |
| Chia 80/20 một lần | Chia train/validation/test + backtest cuốn chiếu | Kết quả ổn định hơn |
| Cần 12–24 tháng dữ liệu | Có 36 tháng (mô phỏng) | Đủ 3 mùa Tết |

---
## Toàn văn


> Chuyen tu `Bao_cao_Giai_doan_1_Kien_thuc_can_chuan_bi.docx` bang `src/docx_sang_md.py`. Ban goc la file .docx.


BÁO CÁO CHUẨN BỊ KIẾN THỨC

GIAI ĐOẠN 1 — ĐỀ CƯƠNG & CƠ SỞ LÝ THUYẾT

Đề tài: Ứng dụng trí tuệ nhân tạo trong dự báo nhu cầu và tối ưu hóa quản lý tồn kho

Đồ án tốt nghiệp — Lộ trình thực hiện 79 ngày

Phạm vi: Ngày 1 – 14 (Giai đoạn 1)

## MỤC LỤC

1. Giới thiệu Giai đoạn 1	3

2. Sơ đồ luồng thực hiện Giai đoạn 1	3

3. Bản đồ kiến thức cần chuẩn bị	4

4. Chi tiết từng mảng kiến thức	4

4.1. Quản lý tồn kho	4

4.2. Dự báo nhu cầu (Demand Forecasting)	6

4.3. Công cụ và kỹ năng lập trình	8

4.4. Kỹ năng nghiên cứu khoa học	8

4.5. Kiến thức ngành logistics / kho vận	9

5. Khuyến nghị thứ tự ưu tiên (14 ngày)	9

6. Luồng chạy khi bắt tay vào build	10

7. Ứng dụng vào Logistics — các khâu được hỗ trợ	16

8. Kết luận	17

## 1. GIỚI THIỆU GIAI ĐOẠN 1

Giai đoạn 1 (ngày 1–14) là bước khởi đầu của đồ án tốt nghiệp, gồm hai nhiệm vụ chính: xây dựng và chốt đề cương chi tiết với giáo viên hướng dẫn, đồng thời hoàn thành Chương 2 — Cơ sở lý thuyết. Để hoàn thành tốt giai đoạn này, sinh viên cần chuẩn bị nền tảng kiến thức ở 5 mảng: quản lý tồn kho, dự báo nhu cầu, công cụ lập trình, kỹ năng nghiên cứu khoa học và kiến thức ngành logistics.

Báo cáo này trình bày: (1) sơ đồ luồng thực hiện Giai đoạn 1, (2) bản đồ tổng quan các mảng kiến thức cần chuẩn bị, (3) nội dung chi tiết từng mảng, và (4) khuyến nghị thứ tự ưu tiên học tập trong 14 ngày.

## 2. SƠ ĐỒ LUỒNG THỰC HIỆN GIAI ĐOẠN 1

Giai đoạn 1 được chia thành 4 bước tuần tự, mỗi bước có sản phẩm đầu ra rõ ràng để làm cơ sở chuyển sang bước tiếp theo:

Hình 1. Sơ đồ luồng Giai đoạn 1 (Ngày 1–14)

## 3. BẢN ĐỒ KIẾN THỨC CẦN CHUẨN BỊ

Năm mảng kiến thức dưới đây có mối liên hệ chặt chẽ với nhau: kiến thức quản lý tồn kho và dự báo nhu cầu là nền tảng lý thuyết cốt lõi (Chương 2), công cụ lập trình là phương tiện triển khai, kỹ năng nghiên cứu khoa học giúp viết đề cương và tổng quan tài liệu đúng chuẩn học thuật, còn kiến thức ngành logistics giúp gắn lý thuyết với thực tế tại đơn vị thực tập.

Hình 2. Bản đồ 5 mảng kiến thức cần chuẩn bị cho Giai đoạn 1

## 4. CHI TIẾT TỪNG MẢNG KIẾN THỨC

### 4.1. Quản lý tồn kho

Đây là mảng kiến thức nền tảng nhất, bắt buộc phải nắm vững trước khi viết Chương 2. Các khái niệm cốt lõi được minh họa trong mô hình răng cưa dưới đây — thể hiện mối quan hệ giữa mức tồn kho, điểm đặt hàng lại và tồn kho an toàn theo thời gian.

Hình 3. Mô hình răng cưa minh họa EOQ, Reorder Point và Safety Stock

a) EOQ — Economic Order Quantity

EOQ là số lượng đặt hàng mỗi lần giúp tổng chi phí tồn kho (chi phí đặt hàng cộng chi phí lưu kho) là thấp nhất. Ý tưởng cốt lõi: đặt hàng ít lần với số lượng lớn thì tốn ít chi phí đặt hàng nhưng tốn nhiều chi phí lưu kho, và ngược lại — EOQ là điểm cân bằng giữa hai loại chi phí này. Công thức: EOQ = căn bậc hai của (2 × D × S / H), trong đó D là nhu cầu hàng năm (đơn vị/năm), S là chi phí mỗi lần đặt hàng, H là chi phí lưu kho mỗi đơn vị mỗi năm.

| Ví dụ minh họa — Tính EOQ Một kho có nhu cầu mặt hàng A là D = 12.000 đơn vị/năm. Chi phí mỗi lần đặt hàng S = 500.000 VNĐ/lần. Chi phí lưu kho H = 20.000 VNĐ/đơn vị/năm. EOQ = √(2 × 12.000 × 500.000 / 20.000) = √600.000 ≈ 775 đơn vị/lần đặt hàng. → Kho nên đặt khoảng 775 đơn vị mỗi lần, tương đương khoảng 15–16 lần đặt hàng trong năm (12.000 ÷ 775), thay vì đặt hàng tùy hứng theo cảm tính. |
|---|

b) Safety stock (Tồn kho an toàn)

Vì nhu cầu thực tế luôn biến động so với dự báo, kho cần giữ thêm một lượng hàng dự phòng để tránh thiếu hàng khi nhu cầu tăng đột biến hoặc nhà cung cấp giao trễ. Công thức phổ biến: Safety stock = Z × σd × căn bậc hai của lead time, trong đó Z là hệ số ứng với mức độ tin cậy mong muốn (tra bảng phân phối chuẩn), σd là độ lệch chuẩn của nhu cầu hàng ngày, lead time là thời gian từ lúc đặt hàng đến lúc nhận hàng.

| Ví dụ minh họa — Tính Safety stock Doanh nghiệp muốn đảm bảo mức phục vụ (service level) 95%, tra bảng được Z = 1,65. Độ lệch chuẩn nhu cầu hàng ngày σd = 15 đơn vị/ngày. Lead time (thời gian giao hàng) = 7 ngày. Safety stock = 1,65 × 15 × √7 = 1,65 × 15 × 2,65 ≈ 66 đơn vị. → Kho cần duy trì tối thiểu 66 đơn vị dự phòng để tránh thiếu hàng trong 95% trường hợp. |
|---|

c) Reorder point (Điểm đặt hàng lại)

Là mức tồn kho mà khi chạm tới, kho phải lập tức đặt hàng mới — vì hàng còn lại vừa đủ dùng trong thời gian chờ giao hàng (lead time) cộng thêm phần an toàn. Công thức: Reorder point = (nhu cầu trung bình mỗi ngày × lead time) + safety stock.

| Ví dụ minh họa — Tính Reorder point Nhu cầu trung bình mỗi ngày d = 40 đơn vị/ngày. Lead time = 7 ngày; Safety stock = 66 đơn vị (kết quả ở trên). Reorder point = (40 × 7) + 66 = 280 + 66 = 346 đơn vị. → Khi tồn kho giảm còn 346 đơn vị, hệ thống phải kích hoạt lệnh đặt hàng ngay, vì lượng này chỉ đủ dùng trong thời gian chờ 7 ngày cộng phần dự phòng. |
|---|

d) ABC Analysis

Là phương pháp phân loại hàng hóa theo mức độ đóng góp vào tổng giá trị tồn kho, dựa trên nguyên lý Pareto (80/20): một số ít mặt hàng thường chiếm phần lớn giá trị. Nhóm A (khoảng 20% số SKU nhưng chiếm khoảng 70–80% giá trị) cần được kiểm soát chặt chẽ nhất; nhóm C (chiếm số lượng SKU nhiều nhất nhưng giá trị thấp) có thể quản lý đơn giản hơn.

| Ví dụ minh họa — Phân loại ABC Một kho có 3 nhóm sản phẩm với giá trị tồn kho hàng năm như sau: • Nhóm A: 10 SKU, chiếm 75% tổng giá trị tồn kho → kiểm kê hàng tuần, dự báo chi tiết theo từng SKU. • Nhóm B: 30 SKU, chiếm 20% tổng giá trị → kiểm kê hàng tháng, dự báo theo nhóm. • Nhóm C: 160 SKU, chỉ chiếm 5% tổng giá trị → kiểm kê theo quý, có thể dùng safety stock cố định thay vì mô hình phức tạp. → Đồ án nên ưu tiên áp dụng mô hình AI cho nhóm A trước, vì đây là nơi cải thiện dự báo mang lại giá trị lớn nhất. |
|---|

e) Cấu trúc chi phí tồn kho

Ba loại chi phí cần phân biệt rõ: chi phí đặt hàng (ordering cost — phát sinh mỗi lần đặt hàng, không phụ thuộc số lượng), chi phí lưu kho (holding cost — tỷ lệ thuận với lượng hàng tồn và thời gian lưu trữ, gồm chi phí kho bãi, bảo hiểm, hao hụt, vốn bị đọng), và chi phí thiếu hàng (stockout cost — chi phí cơ hội khi không đủ hàng bán, gồm mất doanh thu và mất uy tín khách hàng).

| Ví dụ minh họa — So sánh chi phí trước và sau khi tối ưu Trước khi áp dụng mô hình: kho đặt hàng không đều, tổng chi phí đặt hàng + lưu kho = 450 triệu VNĐ/năm, tỷ lệ thiếu hàng 12%. Sau khi áp dụng EOQ + reorder point: tổng chi phí giảm còn 360 triệu VNĐ/năm, tỷ lệ thiếu hàng giảm còn 4%. → Đây chính là loại kết quả "trước – sau" mà Chương 4 và Chương 5 của đồ án cần trình bày để chứng minh giá trị thực tiễn. |
|---|

### 4.2. Dự báo nhu cầu (Demand Forecasting)

Mảng kiến thức thứ hai, làm nền tảng cho Chương 4 (xây dựng mô hình). Cần nắm cả phương pháp thống kê truyền thống lẫn phương pháp học máy hiện đại để có cơ sở so sánh trong đồ án.

a) Chuỗi thời gian (Time series)

Dữ liệu bán hàng theo thời gian thường có 3 thành phần: xu hướng (trend — tăng/giảm dài hạn), tính mùa vụ (seasonality — lặp lại theo chu kỳ cố định như tuần, tháng, năm) và nhiễu (noise — biến động ngẫu nhiên). Nhận diện đúng 3 thành phần này quyết định việc chọn mô hình phù hợp.

| Ví dụ minh họa — Nhận diện tính mùa vụ Dữ liệu bán hàng của một kho bán đồ gia dụng cho thấy: doanh số tăng vọt vào tháng 12–1 (dịp Tết), giảm mạnh vào tháng 6–7, và có xu hướng tăng đều khoảng 8%/năm qua các năm. → Đây là dấu hiệu chuỗi thời gian có cả trend (tăng 8%/năm) lẫn seasonality (chu kỳ theo Tết) — cần chọn mô hình xử lý được cả hai yếu tố này, ví dụ Prophet hoặc SARIMA (ARIMA có thêm yếu tố mùa vụ). |
|---|

b) Phương pháp thống kê truyền thống

Moving Average (trung bình động) dự báo giá trị tiếp theo bằng trung bình cộng của n kỳ gần nhất — đơn giản nhưng phản ứng chậm với thay đổi đột ngột. ARIMA(p,d,q) là mô hình phức tạp hơn: p là số bậc tự hồi quy (dựa vào giá trị quá khứ), d là số lần lấy sai phân để làm chuỗi dừng (loại bỏ trend), q là số bậc trung bình trượt (dựa vào sai số dự báo quá khứ).

| Ví dụ minh họa — Moving Average 3 kỳ Doanh số 5 tháng gần nhất (đơn vị): Tháng 1 = 100, Tháng 2 = 120, Tháng 3 = 90, Tháng 4 = 150, Tháng 5 = 130. Dự báo Tháng 6 = trung bình cộng của Tháng 3, 4, 5 = (90 + 150 + 130) / 3 = 123,3 đơn vị. → Đây là cách tính thủ công, dễ hiểu, thường dùng làm mô hình baseline (đường cơ sở) để so sánh mức cải thiện khi chuyển sang ARIMA hoặc Prophet. |
|---|

c) Prophet

Prophet phân rã chuỗi thời gian thành 3 thành phần cộng lại: xu hướng (trend), mùa vụ (seasonality — theo tuần/năm) và ngày lễ (holidays — có thể khai báo thủ công các dịp đặc biệt như Tết Nguyên Đán). Ưu điểm lớn nhất là cho phép khai báo trực tiếp các ngày lễ đặc thù của Việt Nam, điều mà ARIMA không hỗ trợ sẵn.

| Ví dụ minh họa — Khai báo ngày lễ Tết trong Prophet holidays = pd.DataFrame({ 'holiday': 'tet', 'ds': pd.to_datetime(['2024-02-10', '2025-01-29']), 'lower_window': -3, 'upper_window': 7 }) → Khai báo này giúp mô hình hiểu rằng doanh số sẽ biến động bất thường trong khoảng 3 ngày trước đến 7 ngày sau Tết, thay vì coi đó là nhiễu ngẫu nhiên — giúp dự báo chính xác hơn đáng kể so với ARIMA thông thường cho thị trường Việt Nam. |
|---|

d) Chỉ số đánh giá mô hình: MAE, RMSE, MAPE

MAE (Mean Absolute Error) là trung bình trị tuyệt đối của sai số, dễ hiểu nhưng không phạt nặng các sai số lớn. RMSE (Root Mean Squared Error) bình phương sai số trước khi lấy trung bình rồi khai căn — phạt nặng các dự báo sai lệch lớn, phù hợp khi sai số lớn gây hậu quả nghiêm trọng (như thiếu hàng nặng). MAPE (Mean Absolute Percentage Error) tính theo phần trăm, giúp so sánh giữa các mặt hàng có quy mô khác nhau.

| Ví dụ minh họa — Tính MAE, RMSE, MAPE Giá trị thực tế 5 kỳ: 100, 120, 90, 150, 130. Giá trị dự báo: 110, 115, 95, 140, 135. Sai số: -10, +5, -5, +10, -5. MAE = (10+5+5+10+5)/5 = 7 đơn vị. RMSE = √[(100+25+25+100+25)/5] = √55 ≈ 7,4 đơn vị. MAPE = (10%+4,2%+5,6%+6,7%+3,8%)/5 ≈ 6,1%. → MAPE ≈ 6% thường được xem là mức dự báo khá tốt trong thực tế bán lẻ/kho vận (dưới 10% là chấp nhận được, dưới 20% là mức phổ biến). |
|---|

### 4.3. Công cụ và kỹ năng lập trình

Không cần thành thạo lập trình, chỉ cần đủ kỹ năng để triển khai và trực quan hóa mô hình đã chọn ở mảng 4.2. Dưới đây là một quy trình tối giản bằng Python để đi từ dữ liệu thô đến kết quả dự báo.

| Ví dụ minh họa — Quy trình tối giản với Prophet (Python) import pandas as pd from prophet import Prophet df = pd.read_csv('sales.csv')  # cột 'ds' (ngày), 'y' (doanh số) model = Prophet(yearly_seasonality=True, holidays=holidays) model.fit(df) future = model.make_future_dataframe(periods=30)  # dự báo 30 ngày tới forecast = model.predict(future) → Chỉ với khoảng 6–7 dòng lệnh, đã có thể tạo ra dự báo 30 ngày tới kèm khoảng tin cậy (yhat_lower, yhat_upper) — đây là điểm mạnh giúp Prophet phù hợp cho người mới bắt đầu với Python. |
|---|

| Chủ đề | Nội dung cần nắm |
|---|---|
| Python cơ bản | pandas (xử lý dữ liệu), matplotlib/seaborn (vẽ biểu đồ). |
| Thư viện chuyên dụng | statsmodels (ARIMA), prophet, scikit-learn (nếu dùng thêm ML). |
| Excel nâng cao | Phương án thay thế để làm baseline nếu chưa quen Python. |

### 4.4. Kỹ năng nghiên cứu khoa học

Cần thiết ngay trong giai đoạn viết đề cương và tổng quan tài liệu (ngày 7–14). Kỹ năng quan trọng nhất không phải là đọc nhiều, mà là biết cách so sánh các nghiên cứu để tìm ra điều chưa ai làm.

| Ví dụ minh họa — Cách xác định khoảng trống nghiên cứu (research gap) Sau khi đọc 8 bài báo liên quan, bạn nhận thấy: 5 bài áp dụng ARIMA/Prophet để dự báo nhu cầu nhưng dừng lại ở bước dự báo, không liên kết với việc tính safety stock hay reorder point; 3 bài còn lại tối ưu tồn kho nhưng dùng số liệu dự báo thủ công, không dùng AI. → Khoảng trống: "Chưa có nghiên cứu kết hợp trực tiếp kết quả dự báo bằng AI với việc tính toán động (dynamic) safety stock và reorder point cho một kho thực tế tại Việt Nam." Đây chính là điểm đồ án của bạn có thể đóng góp. |
|---|

| Ví dụ minh họa — Trích dẫn tài liệu tham khảo (ví dụ theo kiểu APA) Trong bài viết: "Prophet đã được chứng minh hiệu quả trong dự báo bán lẻ có tính mùa vụ cao (Nguyen & Tran, 2022)." Trong danh mục tài liệu tham khảo: Nguyen, V. A., & Tran, T. B. (2022). Ứng dụng mô hình Prophet trong dự báo nhu cầu bán lẻ tại Việt Nam. Tạp chí Khoa học Kinh tế, 18(3), 45–58. → Luôn trích dẫn ngay tại chỗ sử dụng ý tưởng của tác giả khác, không chỉ liệt kê ở cuối bài, để tránh bị coi là đạo văn. |
|---|

### 4.5. Kiến thức ngành logistics / kho vận

Giúp gắn kết phần lý thuyết với thực tế tại đơn vị thực tập, phục vụ cho Chương 3 (thực trạng) ở giai đoạn sau.

| Ví dụ minh họa — Tính Inventory Turnover và Fill Rate Giá vốn hàng bán (COGS) trong năm = 2.400.000.000 VNĐ. Giá trị tồn kho trung bình trong năm = 300.000.000 VNĐ. Inventory turnover = COGS / Tồn kho trung bình = 2.400.000.000 / 300.000.000 = 8 lần/năm. → Nghĩa là toàn bộ tồn kho được bán ra và nhập lại 8 lần trong năm; con số càng cao thường thể hiện quản lý tồn kho càng hiệu quả (ít vốn bị đọng). Trong 1.000 đơn hàng nhận được, kho đáp ứng đủ và đúng hạn 950 đơn. Fill rate = 950 / 1.000 = 95%. → Đây là chỉ số nên đưa vào Chương 3 để mô tả thực trạng, và dùng lại ở Chương 5 để so sánh mức cải thiện sau khi áp dụng mô hình đề xuất. |
|---|

| Chủ đề | Nội dung cần nắm |
|---|---|
| Quy trình vận hành kho | Nhập kho, lưu trữ, xuất kho, kiểm kê. |
| KPI quản lý kho | Inventory turnover (vòng quay tồn kho), fill rate (tỷ lệ đáp ứng đơn hàng). |

## 5. KHUYẾN NGHỊ THỨ TỰ ƯU TIÊN (14 NGÀY)

Với quỹ thời gian 14 ngày của Giai đoạn 1, nên phân bổ công sức theo mức độ ưu tiên sau:

| STT | Mảng kiến thức | Mức ưu tiên | Lý do |
|---|---|---|---|
| 1 | Quản lý tồn kho | Cao — bắt buộc | Là nền tảng của toàn bộ Chương 2 và Chương 4 |
| 2 | Dự báo nhu cầu (ARIMA, Prophet) | Cao — bắt buộc | Quyết định trực tiếp chất lượng mô hình ở Chương 4 |
| 3 | Nghiên cứu khoa học | Cao — bắt buộc | Cần ngay để viết đề cương và tổng quan tài liệu |
| 4 | Công cụ lập trình (Python) | Trung bình | Chỉ cần đủ dùng, không cần chuyên sâu |
| 5 | Ngành logistics/kho vận | Trung bình | Có thể vừa học vừa tìm hiểu qua thực tập |

## 6. LUỒNG CHẠY KHI BẮT TAY VÀO BUILD

Sau khi hoàn thành Giai đoạn 1 (đề cương và lý thuyết), quy trình kỹ thuật để triển khai thực tế được chia thành 8 bước tuần tự, nhóm theo 3 giai đoạn: chuẩn bị dữ liệu, xây mô hình, và tối ưu/đầu ra.

Hình 4. Luồng chạy 8 bước khi bắt tay vào build dự án

Bước 1: Thu thập & làm sạch dữ liệu

Nên làm gì:

- Xác định các trường dữ liệu tối thiểu cần có: ngày giao dịch, mã SKU, số lượng nhập, số lượng xuất, tồn kho cuối kỳ.

- Đặt mục tiêu thu thập tối thiểu 12–24 tháng dữ liệu lịch sử để mô hình học được tính mùa vụ theo năm.

- Ưu tiên lấy dữ liệu của nhóm SKU loại A (theo ABC analysis) trước, vì đây là nơi giá trị cải thiện lớn nhất.

Làm như thế nào:

- Liên hệ bộ phận quản lý kho/IT tại đơn vị thực tập để xin export dữ liệu từ hệ thống quản lý kho (WMS/ERP) hoặc file Excel đang dùng.

- Dùng pandas để đọc và kiểm tra tổng quan: df.info(), df.isnull().sum() để biết cột nào thiếu dữ liệu.

- Xử lý missing values: với dữ liệu chuỗi thời gian, nên dùng nội suy (interpolate) hoặc forward-fill thay vì xóa dòng, để không làm gãy chuỗi ngày.

- Xử lý outliers: dùng phương pháp IQR (loại giá trị ngoài khoảng Q1 − 1.5×IQR đến Q3 + 1.5×IQR) hoặc z-score, nhưng cần kiểm tra thủ công trước khi loại bỏ — đôi khi giá trị "bất thường" lại là do khuyến mãi/Tết, không phải lỗi dữ liệu.

| Ví dụ minh họa — Làm sạch dữ liệu cơ bản df['date'] = pd.to_datetime(df['date']) df = df.sort_values('date').set_index('date') df['qty'] = df['qty'].interpolate(method='time')  # nội suy theo thời gian Q1, Q3 = df['qty'].quantile([0.25, 0.75]) IQR = Q3 - Q1 df_clean = df[(df['qty'] >= Q1 - 1.5*IQR) & (df['qty'] <= Q3 + 1.5*IQR)] |
|---|

Bước 2: Phân tích khám phá dữ liệu (EDA)

Nên làm gì:

- Vẽ biểu đồ xu hướng theo thời gian cho từng SKU nhóm A để quan sát bằng mắt trước khi đưa vào mô hình.

- Kiểm tra xem chuỗi có tính mùa vụ rõ ràng không (theo tuần, theo tháng, theo dịp lễ).

- Tính các thống kê mô tả cơ bản: trung bình, độ lệch chuẩn, giá trị lớn nhất/nhỏ nhất theo từng SKU.

Làm như thế nào:

- Dùng matplotlib/seaborn để vẽ line chart doanh số theo thời gian.

- Dùng hàm seasonal_decompose của statsmodels để tách chuỗi thành 3 phần: trend, seasonal, residual — nhìn vào đồ thị residual để đánh giá độ "nhiễu" của dữ liệu.

| Ví dụ minh họa — Tách trend/seasonal from statsmodels.tsa.seasonal import seasonal_decompose result = seasonal_decompose(df_clean['qty'], model='additive', period=30) result.plot()  # hiển thị 4 biểu đồ: gốc, trend, seasonal, residual → Nếu biểu đồ seasonal cho thấy chu kỳ lặp lại rõ ràng theo tháng, đây là căn cứ để chọn Prophet hoặc SARIMA thay vì ARIMA thường ở bước 3–4. |
|---|

Bước 3: Xây mô hình baseline

Nên làm gì:

- Chia tập dữ liệu thành train/test theo thời gian — ví dụ 80% dữ liệu đầu để train, 20% dữ liệu cuối để test — tuyệt đối không random split vì sẽ làm rò rỉ thông tin tương lai.

- Xây mô hình Moving Average trước để có con số so sánh nhanh, sau đó xây ARIMA để có baseline chính thức.

Làm như thế nào:

- Với ARIMA, cần xác định 3 tham số (p, d, q): dùng biểu đồ ACF/PACF (autocorrelation) để ước lượng p và q; dùng kiểm định ADF (Augmented Dickey-Fuller) để xác định d (số lần lấy sai phân cần thiết để chuỗi dừng).

- Nếu không chắc chọn tham số nào, có thể dùng auto_arima (thư viện pmdarima) để tự động dò tham số tối ưu.

| Ví dụ minh họa — ARIMA với auto_arima from pmdarima import auto_arima train, test = df_clean['qty'][:-30], df_clean['qty'][-30:] model = auto_arima(train, seasonal=False, suppress_warnings=True) print(model.summary())  # xem tham số (p,d,q) mà auto_arima chọn forecast = model.predict(n_periods=30) |
|---|

Bước 4: Xây mô hình Prophet / ML

Nên làm gì:

- Cấu hình Prophet với yearly_seasonality bật lên nếu có đủ ≥ 1 năm dữ liệu, và khai báo danh sách ngày lễ Tết/khuyến mãi đặc thù.

- Nếu muốn thử mô hình nâng cao hơn (XGBoost, LSTM), cần tạo thêm các đặc trưng (feature) như: ngày trong tuần, tháng, có phải cuối tuần không, số ngày đến Tết gần nhất.

Làm như thế nào:

- Với Prophet, chuẩn bị dữ liệu đúng định dạng 2 cột 'ds' (ngày) và 'y' (giá trị cần dự báo).

- Khai báo holidays như ví dụ ở mục 4.2, rồi fit model và predict.

- Với XGBoost, dùng cách tiếp cận supervised learning: biến bài toán time series thành bài toán hồi quy bằng cách tạo các lag features (giá trị của 1, 7, 30 ngày trước làm input).

| Ví dụ minh họa — Tạo lag features cho XGBoost df_ml = df_clean.copy() df_ml['lag_1'] = df_ml['qty'].shift(1) df_ml['lag_7'] = df_ml['qty'].shift(7) df_ml['lag_30'] = df_ml['qty'].shift(30) df_ml['month'] = df_ml.index.month df_ml = df_ml.dropna() → Sau bước này, mỗi dòng dữ liệu trở thành một bộ (đặc trưng → nhãn) mà XGBoost có thể học như bài toán hồi quy thông thường. |
|---|

Bước 5: Đánh giá & chọn mô hình

Nên làm gì:

- Tính MAE, RMSE, MAPE cho tất cả các mô hình đã xây (Moving Average, ARIMA, Prophet, ML nếu có) trên cùng một tập test để so sánh công bằng.

- Không chỉ nhìn vào chỉ số trung bình — nên vẽ biểu đồ dự báo chồng lên giá trị thực tế để kiểm tra bằng mắt xem mô hình có bắt được đỉnh/đáy mùa vụ không.

Làm như thế nào:

- Nên dùng time series cross-validation (rolling window) thay vì chỉ đánh giá trên một đoạn test duy nhất, để kết quả đáng tin cậy hơn — Prophet có sẵn hàm cross_validation cho việc này.

- Lập bảng so sánh các mô hình theo từng chỉ số, chọn mô hình có MAPE thấp nhất nhưng vẫn đơn giản, dễ giải thích khi bảo vệ đồ án.

| Ví dụ minh họa — Cross-validation với Prophet from prophet.diagnostics import cross_validation, performance_metrics df_cv = cross_validation(model, initial='365 days', period='30 days', horizon='30 days') df_perf = performance_metrics(df_cv) print(df_perf[['horizon', 'mae', 'rmse', 'mape']].mean()) |
|---|

Bước 6: Tính EOQ, Safety stock, Reorder point

Nên làm gì:

- Áp dụng các công thức đã trình bày ở mục 4.1 cho từng SKU, dựa trên kết quả dự báo vừa chọn ở bước 5 thay vì số liệu lịch sử thô.

- Dùng độ lệch chuẩn của phần sai số dự báo (residual) làm σd trong công thức Safety stock — vì đây phản ánh đúng độ không chắc chắn của mô hình, chính xác hơn độ lệch chuẩn nhu cầu thô.

Làm như thế nào:

- Viết một hàm Python tính EOQ, Safety stock, Reorder point, sau đó lặp (loop) qua danh sách SKU để áp dụng hàng loạt, tránh tính tay từng SKU.

| Ví dụ minh họa — Hàm tính tồn kho tối ưu import math def calc_inventory(D, S, H, sigma_d, lead_time, Z=1.65): eoq = math.sqrt(2 * D * S / H) safety_stock = Z * sigma_d * math.sqrt(lead_time) d_avg = D / 365 reorder_point = d_avg * lead_time + safety_stock return {'EOQ': eoq, 'Safety_stock': safety_stock, 'Reorder_point': reorder_point} for sku in sku_list: result = calc_inventory(D=demand[sku], S=500000, H=20000, sigma_d=residual_std[sku], lead_time=7) |
|---|

Bước 7: Xây dashboard

Nên làm gì:

- Xác định trước 3–4 chỉ số/biểu đồ quan trọng nhất cần hiển thị: dự báo vs thực tế, cảnh báo tồn kho thấp/dư thừa, KPI theo SKU — tránh nhồi nhét quá nhiều biểu đồ khiến dashboard rối.

Làm như thế nào:

- Nếu quen giao diện kéo-thả và muốn trình bày chuyên nghiệp khi bảo vệ: dùng Power BI hoặc Tableau, kết nối trực tiếp vào file Excel/CSV kết quả xuất ra từ Python.

- Nếu muốn thể hiện kỹ năng lập trình và cần cập nhật động: dùng Streamlit — chỉ cần vài chục dòng Python là có dashboard chạy trên trình duyệt.

| Ví dụ minh họa — Dashboard tối giản với Streamlit import streamlit as st st.title('Dashboard dự báo & tồn kho') sku = st.selectbox('Chọn SKU', sku_list) st.line_chart(forecast_df[sku][['actual', 'forecast']]) if current_stock[sku] < reorder_point[sku]: st.warning(f'{sku}: Tồn kho dưới điểm đặt hàng lại — cần đặt hàng ngay!') |
|---|

Bước 8: Báo cáo kết quả & đề xuất

Nên làm gì:

- Tổng hợp một bảng so sánh "trước – sau" rõ ràng: chi phí tồn kho, tỷ lệ thiếu hàng, độ chính xác dự báo — đây là phần giám khảo sẽ nhìn vào đầu tiên.

- Chuẩn bị sẵn 2–3 biểu đồ trực quan nhất (không phải bảng số liệu thô) để đưa vào slide bảo vệ.

Làm như thế nào:

- Dùng lại các số liệu đã tính ở bước 5 (độ chính xác mô hình) và bước 6 (chi phí tồn kho tối ưu) để lập bảng so sánh — không cần tính toán gì thêm, chỉ cần trình bày lại cho rõ ràng.

- Viết đề xuất cụ thể, khả thi cho đơn vị thực tập — ví dụ: "áp dụng reorder point tự động cho nhóm SKU A trước, mở rộng dần sang nhóm B/C sau 3 tháng thử nghiệm" — tránh đề xuất chung chung như "nên áp dụng AI vào quản lý kho".

| Ví dụ minh họa — Lưu ý khi triển khai thực tế Quy trình trên không nên làm tuần tự cứng nhắc từng bước xong mới chuyển bước sau. Bước 1–2 (dữ liệu) thường phải quay lại chỉnh sửa nhiều lần sau khi đã thử mô hình ở bước 3–4, vì lúc đó mới phát hiện dữ liệu thiếu hoặc cần bổ sung thêm biến (feature) mới. → Nên xem đây là một vòng lặp có phản hồi (feedback loop) giữa bước dữ liệu và bước mô hình, thay vì một đường thẳng một chiều. |
|---|

## 7. ỨNG DỤNG VÀO LOGISTICS — CÁC KHÂU ĐƯỢC HỖ TRỢ

Dự án tập trung vào dự báo nhu cầu và tồn kho — đây là mắt xích đầu vào của cả chuỗi logistics, nên khi triển khai tốt sẽ tạo hiệu ứng lan tỏa sang nhiều khâu khác trong chuỗi cung ứng.

| Chủ đề | Nội dung cần nắm |
|---|---|
| Quản lý kho bãi (Warehousing) | Bố trí không gian kho hợp lý theo dự báo, ưu tiên chỗ cho SKU nhóm A sắp tăng nhu cầu; giảm tình trạng kho chật cứng hàng tồn không cần thiết hoặc trống chỗ vì thiếu hàng; lập kế hoạch nhân sự bốc xếp theo khối lượng dự kiến. |
| Thu mua / Đặt hàng (Procurement) | EOQ và reorder point giúp bộ phận mua hàng biết chính xác khi nào đặt, đặt bao nhiêu — tránh đặt hàng khẩn cấp chi phí cao hoặc đặt dư thừa; có thể thương lượng tốt hơn với nhà cung cấp nhờ kế hoạch đặt hàng ổn định. |
| Vận tải (Transportation) | Biết trước khối lượng hàng cần nhập/xuất theo tuần/tháng giúp lên kế hoạch xe tải, container hiệu quả hơn; gộp đơn hàng dự báo được để tối ưu tải trọng mỗi chuyến, giảm chi phí vận chuyển trên mỗi đơn vị hàng. |
| Quản lý chuỗi cung ứng (Supply Chain Planning) | Dự báo nhu cầu là đầu vào quan trọng cho S&OP (Sales & Operations Planning) — nếu các bộ phận bán hàng, sản xuất, kho đều dùng chung một con số dự báo đáng tin cậy, sẽ giảm tình trạng mỗi bên tự đoán một kiểu. |
| Dịch vụ khách hàng (Customer Service) | Giảm tỷ lệ thiếu hàng (stockout) đồng nghĩa với tăng fill rate — khách hàng nhận đủ đơn hàng đúng hạn hơn, giảm tình trạng phải xin lỗi vì hết hàng. |
| Ra quyết định quản lý (Management Decision-making) | Dashboard trực quan hóa giúp quản lý cấp cao nhìn được bức tranh tổng thể (xu hướng nhu cầu, tình trạng tồn kho, cảnh báo) để ra quyết định nhanh, không phải chờ báo cáo Excel thủ công mỗi tuần. |

| Ví dụ minh họa — Lưu ý khi trình bày trong đồ án Vì phạm vi thực tập là kho bãi, các ứng dụng mở rộng (vận tải, S&OP, dịch vụ khách hàng...) nên đưa vào mục "Hướng phát triển" ở cuối đồ án, không phải phần kết quả chính. Phần kết quả chính nên tập trung chứng minh chắc chắn ở tồn kho và dự báo — nơi có dữ liệu thực tế để đối chứng, tránh bị hỏi vặn khi bảo vệ về những phần chưa đo lường được. |
|---|

## 8. KẾT LUẬN

Giai đoạn 1 không đòi hỏi kiến thức chuyên sâu ở tất cả các mảng, nhưng cần hiểu đúng và đủ về quản lý tồn kho cùng dự báo nhu cầu để đặt nền móng vững chắc cho toàn bộ đồ án. Kỹ năng nghiên cứu khoa học và công cụ lập trình đóng vai trò hỗ trợ, có thể vừa học vừa làm trong quá trình triển khai.

Hoàn thành tốt Giai đoạn 1 sẽ giúp các giai đoạn tiếp theo (thu thập dữ liệu, xây dựng mô hình) diễn ra thuận lợi hơn, vì đã có nền tảng lý thuyết và đề cương rõ ràng được GVHD phê duyệt.
