# Từ điển thuật ngữ viết tắt ngành Logistics & Quản lý tồn kho


> Chuyen tu `Từ điển thuật ngữ viết tắt ngành Logistics & Quản lý tồn kho.docx` bang `src/docx_sang_md.py`. Ban goc la file .docx.


## Từ điển thuật ngữ viết tắt ngành Logistics & Quản lý tồn kho

Oct 9, 2026

### Đọc phần nào trước

Tài liệu có khoảng 120 thuật ngữ chia thành 5 nhóm, nhưng đồ án dự báo tồn kho của bạn cần chắc trước 15 thuật ngữ dưới đây; phần còn lại tra khi gặp.

Mỗi bảng có 4 cột: viết tắt, tên đầy đủ (tiếng Anh), nghĩa tiếng Việt, và ghi chú (công thức, ví dụ hoặc lỗi hay nhầm). Công thức đặt ngay trong ghi chú để bạn chép vào Chương 2.

| Ưu tiên | Thuật ngữ | Vì sao cần cho đồ án | Xem ở nhóm |
|---|---|---|---|
| 1 | SKU | Đơn vị phân tích: mỗi SKU là một chuỗi thời gian cần dự báo | 1 |
| 2 | LT (Lead Time) | Quyết định Safety Stock và ROP | 1 |
| 3 | EOQ | Lượng đặt tối ưu mỗi lần | 1 |
| 4 | SS (Safety Stock) | Tồn kho đệm chống biến động | 1 |
| 5 | ROP | Điểm đặt hàng lại, đầu ra chính của đồ án | 1 |
| 6 | ABC / XYZ | Chọn SKU nào làm trước | 1 |
| 7 | Service Level / CSL | Đầu vào của công thức Safety Stock | 5 |
| 8 | Stockout | Hiện tượng làm sai lệch dữ liệu nhu cầu | 1, 5 |
| 9 | MAE, RMSE | Đo sai số mô hình | 2 |
| 10 | MAPE, WMAPE | Đo sai số theo phần trăm, chọn mô hình tốt nhất | 2 |
| 11 | Bias | Mô hình dự báo thừa hay thiếu | 2 |
| 12 | Prophet, ARIMA/SARIMA | Mô hình thường dùng trong đề tài | 2 |
| 13 | Fill Rate | KPI đo mức đáp ứng đơn | 5 |
| 14 | DOH / DIO, ITR | KPI đo hiệu quả tồn kho trước và sau khi áp dụng AI | 5 |
| 15 | WMS / ERP | Nơi bạn xin export dữ liệu ở đơn vị thực tập | 3 |

### Nhóm 1 — Tồn kho và hoạch định

Nhóm này là nền của Chương 2: nó trả lời câu hỏi “đặt bao nhiêu, khi nào đặt, giữ đệm bao nhiêu”.

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| SKU | Stock Keeping Unit | Mã quản lý tồn kho, mỗi biến thể hàng (vị, cỡ, quy cách) là 1 SKU | 1 sản phẩm có 3 cỡ thì là 3 SKU. Dự báo luôn làm ở mức SKU |
| LT | Lead Time | Thời gian từ lúc đặt hàng đến lúc hàng vào kho | Có trung bình và độ lệch chuẩn. LT dài và hay dao động thì Safety Stock phải cao |
| MOQ | Minimum Order Quantity | Số lượng đặt tối thiểu nhà cung cấp chấp nhận | Nếu EOQ nhỏ hơn MOQ thì phải đặt theo MOQ |
| EOQ | Economic Order Quantity | Lượng đặt hàng kinh tế, làm tổng chi phí đặt hàng + lưu kho nhỏ nhất | Giả định nhu cầu ổn định, nên chỉ là mốc tham chiếu khi nhu cầu có mùa vụ |
| S, H | Ordering cost, Holding cost | S: chi phí mỗi lần đặt. H: chi phí lưu 1 đơn vị trong 1 năm | H = tỷ lệ lưu kho × giá vốn, thường 15–30%/năm. Gom về cho đúng đơn vị thời gian |
| SS | Safety Stock | Tồn kho an toàn, đệm chống nhu cầu và LT biến động | Không phải tồn kho “dư”. Cao hơn khi muốn mức phục vụ cao hơn |
| ROP | Reorder Point | Điểm đặt hàng lại: tồn kho (cộng hàng đang về) chạm mức này thì phải đặt | ROP = nhu cầu/ngày × LT + SS |
| IP | Inventory Position | Tồn kho “thực chất” = tồn hiện có + hàng đang đặt − hàng thiếu nợ khách | So sánh IP, không so tồn hiện có, với ROP để tránh đặt trùng |
| OH / SOH | On Hand / Stock On Hand | Tồn kho hiện có thực tế trong kho | Cùng với OO (On Order, đang đặt) và BO (Backorder) tạo nên IP |
| (s,Q) | Continuous review policy | Theo dõi liên tục; tồn ≤ s thì đặt cố định Q | Chính là chính sách ROP + EOQ. Dữ liệu mô phỏng ở trên dùng chính sách này |
| (R,S) | Periodic review, order-up-to | Kiểm tra định kỳ mỗi R ngày, đặt để đưa tồn lên mức S | Hay gặp ở kho kiểm hàng hàng tuần. Safety Stock phải tính cho cả R + LT |
| ABC | ABC analysis | Phân loại theo giá trị: A ~70–80% giá trị, B ~15–20%, C còn lại | Nguyên lý Pareto 80/20. Quyết định SKU nào dự báo trước |
| XYZ | XYZ analysis | Phân loại theo độ ổn định nhu cầu qua hệ số biến thiên CV | X: CV thấp, dễ dự báo. Z: CV cao, khó. Ngưỡng thường dùng 0,5 và 1,0 (tuỳ doanh nghiệp) |
| CV | Coefficient of Variation | Hệ số biến thiên = độ lệch chuẩn / trung bình | CV càng cao thì Safety Stock càng lớn |
| FIFO | First In, First Out | Nhập trước xuất trước | Phổ biến nhất, nhất là hàng có hạn dùng |
| FEFO | First Expired, First Out | Hết hạn trước xuất trước | Dùng cho thực phẩm, sữa, dược. Khác FIFO khi lô nhập sau lại hết hạn sớm hơn |
| LIFO | Last In, First Out | Nhập sau xuất trước | Ít dùng ở kho hàng tiêu dùng, không phải phương pháp kế toán được chấp nhận theo chuẩn mực kế toán Việt Nam |
| JIT | Just In Time | Sản xuất / giao hàng đúng lúc cần, giảm tồn kho tối đa | Yêu cầu LT ổn định, nhà cung cấp gần |
| VMI | Vendor Managed Inventory | Nhà cung cấp tự quản lý và bổ sung tồn kho cho khách | Khách chia sẻ dữ liệu bán hàng và tồn kho cho nhà cung cấp |
| MRP | Material Requirements Planning | Hoạch định nhu cầu nguyên vật liệu dựa trên kế hoạch sản xuất | Kho nhà máy dùng; kho phân phối hàng tiêu dùng thường không dùng MRP |
| DRP | Distribution Requirements Planning | Hoạch định nhu cầu phân phối cho mạng lưới kho / đại lý | “MRP của bên phân phối” |
| S&OP | Sales and Operations Planning | Họp liên phòng ban hàng tháng, cân bằng dự báo bán với năng lực cung ứng | Đầu ra của dự báo AI thường được đưa vào đây |
| CPFR | Collaborative Planning, Forecasting and Replenishment | Nhà bán lẻ và nhà cung cấp cùng lập dự báo và bổ sung hàng | Giảm hiệu ứng Bullwhip |
| MTS / MTO / ATO / ETO | Make/Assemble/Engineer To Stock/Order/... | Sản xuất để tồn (MTS), theo đơn (MTO), lắp ráp theo đơn (ATO), thiết kế theo đơn (ETO) | Dự báo nhu cầu quan trọng nhất với MTS và hàng phân phối |
| BOM | Bill of Materials | Định mức nguyên vật liệu cấu thành 1 thành phẩm | Chủ yếu ở sản xuất |
| RM / WIP / FG | Raw Material / Work In Progress / Finished Goods | Nguyên liệu / bán thành phẩm đang sản xuất / thành phẩm | 3 loại tồn kho cơ bản của nhà máy. Kho phân phối chủ yếu chỉ có FG |
| Backorder | Backorder (BO) | Đơn hàng thiếu nợ, giao bù khi có hàng | Khác Lost Sales: khách hủy, mất doanh thu luôn |
| Stockout | Stockout / Out of Stock (OOS) | Hết hàng khi có nhu cầu | Dữ liệu bán khi stockout thấp hơn nhu cầu thật (“nhu cầu bị che”) |
| SLOB | Slow-moving and Obsolete | Hàng chậm luân chuyển và hàng lỗi thời | Mục tiêu của việc giảm tồn dư. Tồn âm thầm phí tiền và chỗ kho |
| Cycle Count | Cycle counting | Kiểm kê luân phiên theo nhóm SKU thay vì đóng kho kiểm cả năm | Thường kiểm nhóm A thường xuyên hơn |
| Kanban | Kanban | Thẻ tín hiệu bổ sung hàng khi dùng hết một thùng/bình | Dạng ROP đơn giản trên sàn sản xuất |
| Bullwhip | Bullwhip effect | Biến động nhu cầu bị khuếch đại dần khi đi ngược lên chuỗi cung ứng | Nguyên nhân: dự báo trên đơn đặt thay vì bán thật, đặt hàng theo lô, đầu cơ giá |

Ba công thức cốt lõi (D là nhu cầu/năm, d là nhu cầu/ngày, σd là độ lệch chuẩn nhu cầu/ngày, z là hệ số theo mức phục vụ; z = 1,65 ứng với 95%):

EOQ = \sqrt{\frac{2DS}{H}} \qquad SS = z \cdot \sigma_d \cdot \sqrt{LT} \qquad ROP = d \cdot LT + SS

Công thức SS trên giả định LT cố định. Khi LT cũng dao động, dùng dạng đầy đủ: SS = z × √(LT×σd² + d²×σLT²), và bạn nên nêu cả hai dạng trong đồ án.

### Nhóm 2 — Dự báo nhu cầu và đo sai số

Nhóm này là phần “AI” của đồ án: mô hình nào dự báo và đo nó tốt hay tệ bằng chỉ số nào.

#### Khái niệm chuỗi thời gian

| Thuật ngữ | Nghĩa | Ghi chú |
|---|---|---|
| Time Series | Chuỗi dữ liệu theo thứ tự thời gian | Không được xáo trộn thứ tự khi chia train/test |
| Trend | Xu hướng dài hạn tăng hoặc giảm | Ví dụ: nhu cầu tăng 4%/năm |
| Seasonality | Tính mùa vụ, lặp lại theo chu kỳ cố định (tuần, tháng, năm) | Tết là mùa vụ năm; tuần là mùa vụ tuần |
| Cyclicality | Chu kỳ kinh tế dài, không cố định độ dài | Hay nhầm với Seasonality |
| Residual / Noise | Phần còn lại sau khi tách trend và mùa vụ | Residual lớn nghĩa là dữ liệu nhiễu, khó dự báo |
| Stationarity | Chuỗi dừng: trung bình và phương sai không đổi theo thời gian | ARIMA yêu cầu; kiểm bằng ADF test |
| ACF / PACF | Autocorrelation / Partial Autocorrelation Function | Biểu đồ giúp chọn tham số ARIMA |
| Lag | Độ trễ: giá trị của k kỳ trước | lag_7 là nhu cầu cùng thứ tuần trước |
| Horizon | Tầm dự báo: dự báo bao xa | Nên bằng hoặc lớn hơn Lead Time + chu kỳ kiểm hàng |
| Intermittent Demand | Nhu cầu rời rạc, nhiều ngày bằng 0 | Hàng chậm. Dùng Croston hoặc TSB thay vì ARIMA |
| Backtest / Walk-forward | Kiểm thử mô hình bằng cách lùi dần mốc thời gian | An toàn hơn k-fold ngẫu nhiên (tránh rò rỉ dữ liệu tương lai) |
| Overfitting | Mô hình học thuộc dữ liệu huấn luyện, kém trên dữ liệu mới | Sai số train thấp nhưng sai số test cao |

#### Mô hình dự báo

| Viết tắt | Tên đầy đủ | Dùng khi | Lưu ý |
|---|---|---|---|
| Naive / Seasonal Naive | Dự báo bằng giá trị kỳ trước / cùng kỳ năm trước | Mốc so sánh tối thiểu | Mô hình AI không thắng được Seasonal Naive thì không đáng triển khai |
| SMA / WMA | Simple / Weighted Moving Average | Chuỗi ổn định, không mùa vụ | WMA cho trọng số cao hơn cho dữ liệu gần |
| SES / Holt / Holt-Winters | Simple / Double / Triple Exponential Smoothing | Không xu hướng / có xu hướng / có xu hướng + mùa vụ | Nhanh, ít tham số |
| ETS | Error, Trend, Seasonal | Họ mô hình làm mượt mũ tổng quát | Thường là baseline mạnh |
| ARIMA | AutoRegressive Integrated Moving Average | Chuỗi dừng hoặc lấy sai phân để dừng | Tham số (p,d,q): bậc tự hồi quy, sai phân, trung bình trượt |
| SARIMA / SARIMAX | Seasonal ARIMA / + eXogenous | Có mùa vụ; X: thêm biến ngoại sinh như khuyến mãi, lễ | Chậm khi chuỗi theo ngày có mùa vụ năm (m = 365) |
| Prophet | Prophet (Meta) | Nhiều mùa vụ chồng nhau, có ngày lễ, dữ liệu thiếu | Định dạng vào gồm 2 cột ds (ngày) và y (giá trị) |
| RF / XGBoost / LightGBM | Random Forest / Extreme Gradient Boosting / Light Gradient Boosting | Dự báo bằng đặc trưng (lag, thứ, tháng, khuyến mãi) | Không tự hiểu thời gian, phải tự tạo lag features |
| LSTM / GRU | Long Short-Term Memory / Gated Recurrent Unit | Mạng nơ-ron hồi quy cho chuỗi dài | Cần nhiều dữ liệu; với 24 tháng dữ liệu thường không hơn hẳn mô hình cổ điển |
| Croston / TSB | Croston, Teunter-Syntetos-Babai | Nhu cầu rời rạc | Dự báo riêng khoảng cách giữa 2 đơn và quy mô đơn |

#### Chỉ số đo sai số

| Viết tắt | Tên đầy đủ | Ý nghĩa | Điểm cần biết |
|---|---|---|---|
| ME / Bias | Mean Error | Sai số trung bình có dấu: dương là dự báo thấp hơn thực tế (nếu tính thực tế trừ dự báo) | Bias lệch một chiều làm tồn kho dư hoặc thiếu đều đặn. Nêu rõ quy ước dấu trong báo cáo |
| MAE | Mean Absolute Error | Sai số tuyệt đối trung bình, cùng đơn vị với hàng | Dễ hiểu, không phạt nặng sai số lớn |
| MSE / RMSE | Mean Squared Error / Root MSE | Bình phương sai số rồi khai căn | Phạt nặng sai số lớn; RMSE ≥ MAE |
| MAPE | Mean Absolute Percentage Error | Sai số phần trăm trung bình | Hỏng khi nhu cầu gần 0 (chia cho 0) và thiên về phạt dự báo cao |
| sMAPE | Symmetric MAPE | MAPE đối xứng | Vẫn kém ở nhu cầu rất nhỏ |
| WMAPE | Weighted MAPE | Tổng sai số tuyệt đối chia tổng nhu cầu thực | Ít bị nhiễu bởi ngày nhỏ. Nên dùng thay MAPE cho dữ liệu theo ngày |
| MASE | Mean Absolute Scaled Error | MAE chia cho MAE của mô hình Naive | Dưới 1 là tốt hơn Naive; so sánh được giữa nhiều SKU |
| FA | Forecast Accuracy | Độ chính xác dự báo, thường = 1 − WMAPE | Chỉ số doanh nghiệp hay báo cáo |
| FVA | Forecast Value Added | Mức cải thiện so với dự báo cũ (hay Naive) | Chứng minh mô hình AI có giá trị |
| TS | Tracking Signal | Tổng sai số tích lũy / MAE | Ngoài khoảng ±4 đến ±6 là dấu hiệu dự báo bị lệch, cần huấn luyện lại |
| CI / PI | Confidence / Prediction Interval | Khoảng tin cậy của dự báo | Prophet trả về yhat_lower và yhat_upper, dùng để chọn Safety Stock |

Công thức ba chỉ số hay dùng nhất (A là thực tế, F là dự báo):

MAE = \frac{1}{n}\sum |A_t - F_t| \qquad RMSE = \sqrt{\frac{1}{n}\sum (A_t - F_t)^2} \qquad WMAPE = \frac{\sum |A_t - F_t|}{\sum A_t}

### Nhóm 3 — Kho vận, hệ thống và chứng từ

Bạn sẽ gặp nhóm này ngay lúc đi thực tập: dữ liệu lấy từ WMS/ERP, và mỗi dòng nhập–xuất sinh ra từ một chứng từ như GRN hay GI.

#### Hệ thống, nhận dạng và thiết bị

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| WMS | Warehouse Management System | Phần mềm quản lý kho: vị trí, nhập xuất, tồn | Nguồn dữ liệu chính của đồ án |
| ERP | Enterprise Resource Planning | Phần mềm quản trị doanh nghiệp tổng thể (mua, bán, kho, kế toán) | SAP, Oracle, Odoo, MISA... Là nơi có giá vốn và đơn mua |
| TMS | Transportation Management System | Phần mềm quản lý vận tải: tuyến, xe, cước | Nối với WMS khi giao hàng |
| OMS | Order Management System | Quản lý đơn hàng từ nhiều kênh bán | Quan trọng với thương mại điện tử |
| WCS / WES | Warehouse Control / Execution System | Lớp điều khiển thiết bị tự động (băng tải, robot) / điều phối công việc | Nằm giữa WMS và máy móc |
| EDI | Electronic Data Interchange | Trao đổi chứng từ điện tử giữa các bên (đơn hàng, ASN) | Thay email và giấy tờ |
| API | Application Programming Interface | Giao diện để phần mềm nói chuyện với phần mềm | Cách hiện đại để lấy dữ liệu WMS về Python |
| BI | Business Intelligence | Phần mềm báo cáo và dashboard | Power BI, Tableau, Streamlit (dùng trong đồ án) |
| IoT | Internet of Things | Cảm biến gắn mạng (nhiệt độ, vị trí) | Dùng trong kho lạnh |
| Barcode / QR | Barcode / Quick Response | Mã vạch / mã vuông để máy quét đọc nhanh | QR chứa nhiều thông tin hơn |
| RFID | Radio Frequency Identification | Nhận dạng bằng sóng vô tuyến, đọc được nhiều thẻ cùng lúc | Đắt hơn barcode, độ chính xác kiểm kê cao hơn |
| GS1 | GS1 standards | Tổ chức tiêu chuẩn mã sản phẩm và chứng từ toàn cầu | Nền tảng của GTIN, EAN và SSCC |
| GTIN / EAN / UPC | Global Trade Item Number / European / Universal Product Code | Mã sản phẩm toàn cầu in trên bao bì | Việt Nam dùng mã EAN-13 (bắt đầu 893) |
| SSCC | Serial Shipping Container Code | Mã định danh riêng cho từng pallet / thùng gửi | Dùng để truy vết pallet |
| LPN | License Plate Number | Mã định danh nội bộ cho pallet / thùng trong WMS | Gắn nhiều SKU vào 1 mã |
| RF | Radio Frequency (scanner) | Máy quét cầm tay kết nối WMS | Công nhân quét khi nhập, lấy, xuất |
| AS/RS | Automated Storage and Retrieval System | Hệ thống cất và lấy hàng tự động | Đầu tư lớn, kho quy mô lớn |
| AGV / AMR | Automated Guided Vehicle / Autonomous Mobile Robot | Xe tự hành theo làn cố định / tự tìm đường | AMR linh hoạt hơn |
| PTL | Pick To Light | Đèn báo vị trí lấy hàng | Tăng tốc độ soạn hàng |

#### Quy trình và chứng từ trong kho

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| PR | Purchase Requisition | Phiếu đề nghị mua hàng nội bộ | Chưa gửi nhà cung cấp |
| RFQ | Request For Quotation | Yêu cầu báo giá | Trước PO |
| PO | Purchase Order | Đơn đặt mua gửi nhà cung cấp | Mốc “đặt hàng” khi tính Lead Time |
| SO | Sales Order | Đơn bán hàng của khách | Nguồn ra nhu cầu của kho |
| ASN | Advance Shipping Notice | Thông báo giao hàng trước từ nhà cung cấp | Giúp kho chuẩn bị nhân lực và chỗ |
| GR / GRN | Goods Receipt / Goods Receipt Note | Phiếu nhập kho; ghi nhận hàng đã về | Mỗi dòng GRN tạo ra qty_in trong dữ liệu |
| GI | Goods Issue | Phiếu xuất kho | Mỗi dòng GI tạo ra qty_out |
| DN / D/O | Delivery Note / Delivery Order | Phiếu giao hàng | Khác D/O của hãng tàu (lệnh giao hàng) ở nhóm 4 |
| PL | Packing List | Phiếu đóng gói: số kiện, trọng lượng | Đi kèm lô hàng |
| POD | Proof Of Delivery | Chứng từ khách ký nhận hàng | Căn cứ tính doanh thu và giải quyết khiếu nại |
| QC / QA | Quality Control / Quality Assurance | Kiểm tra chất lượng / đảm bảo chất lượng | Kho thường có điểm QC lúc nhận hàng |
| RTV / RMA | Return To Vendor / Return Merchandise Authorization | Trả hàng nhà cung cấp / cho phép khách trả hàng | Gọi chung là Reverse Logistics |
| Putaway | Putaway | Đưa hàng mới nhận vào đúng vị trí lưu trữ | Sau GRN |
| Picking | Order picking | Lấy hàng theo đơn | Thường là khâu tốn nhân công nhất trong kho |
| Wave / Batch / Zone picking | Wave / Batch / Zone picking | Soạn theo đợt giờ / gộp nhiều đơn / chia khu | Mỗi cách phù hợp quy mô đơn khác nhau |
| Slotting | Slotting | Sắp xếp SKU vào vị trí tối ưu | SKU nhóm A đặt gần cửa xuất |
| SLOC / Bin | Storage Location / Bin location | Mã vị trí lưu trữ (dãy-kệ-tầng-ô) | Ví dụ A-03-2-04 |
| Cross-docking | Cross-docking | Hàng nhận về chuyển thẳng ra xe giao, không lưu kho | Giảm tồn kho và thời gian |
| Replenishment | Replenishment | Bổ sung hàng từ khu lưu trữ sang khu soạn hàng; hoặc từ nhà cung cấp về kho | Hai nghĩa, cần nói rõ ngữ cảnh |
| Kitting | Kitting | Gộp nhiều SKU thành bộ bán | Ví dụ combo quà Tết |
| Dock-to-Stock | Dock-to-Stock time | Thời gian từ lúc xe tới cửa kho đến lúc hàng sẵn sàng bán | Chỉ số hiệu suất nhập kho |
| DC / RDC / CDC / FC | Distribution / Regional / Central Distribution Center / Fulfillment Center | Trung tâm phân phối (khu vực / trung tâm) / trung tâm xử lý đơn online | Kho của bạn có thể là DC |
| UoM | Unit of Measure | Đơn vị tính (cái, thùng, pallet) | Phải quy đổi về cùng một UoM trước khi dự báo |
| Pallet / Carton | Pallet / Carton | Tấm kê hàng / thùng | Pallet chuẩn phổ biến 1,2 × 1,0 m |

### Nhóm 4 — Vận tải và thương mại quốc tế

Nhóm này dành cho khi hàng nhập khẩu hoặc xuất khẩu; nó giải thích vì sao Lead Time của một số SKU dài và hay dao động.

#### Incoterms (điều kiện giao hàng)

Incoterms quy định ai trả cước, ai chịu rủi ro và chỗ chuyển giao rủi ro. Bản hiện hành là Incoterms 2020.

| Viết tắt | Tên đầy đủ | Người bán lo đến đâu | Lưu ý |
|---|---|---|---|
| EXW | Ex Works | Chỉ để hàng sẵn tại xưởng người bán | Người mua chịu gần như toàn bộ chi phí và rủi ro |
| FCA | Free Carrier | Giao cho người vận chuyển do người mua chỉ định | Dùng cho mọi phương thức vận tải |
| FOB | Free On Board | Đã xếp hàng lên tàu tại cảng đi | Chỉ áp dụng đường biển và thủy nội địa. Rất phổ biến ở Việt Nam |
| CFR | Cost and Freight | FOB + cước tàu đến cảng đến | Rủi ro vẫn chuyển sang người mua khi hàng lên tàu |
| CIF | Cost, Insurance and Freight | CFR + bảo hiểm hàng hóa | Chỉ đường biển |
| CPT / CIP | Carriage Paid To / Carriage and Insurance Paid To | Tương tự CFR / CIF nhưng cho mọi phương thức | CIP yêu cầu mức bảo hiểm cao hơn CIF |
| DAP | Delivered At Place | Giao tới địa điểm đến, chưa dỡ và chưa thông quan nhập | Người mua lo thông quan nhập khẩu |
| DDP | Delivered Duty Paid | Giao tới nơi đã thông quan và đã nộp thuế | Người bán chịu trách nhiệm cao nhất |

#### Thuật ngữ vận tải và chứng từ xuất nhập khẩu

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| 3PL / 4PL | Third / Fourth Party Logistics | Thuê ngoài dịch vụ logistics / thuê đơn vị tích hợp quản lý nhiều 3PL | 3PL: kho, vận tải. 4PL: hoạch định tổng thể |
| FF | Freight Forwarder | Công ty giao nhận, sắp xếp vận chuyển | Không sở hữu tàu |
| NVOCC | Non-Vessel Operating Common Carrier | Người vận chuyển không có tàu, đứng tên phát hành House B/L | Phổ biến hơn ở hàng lẻ (LCL) |
| FCL / LCL | Full / Less than Container Load | Hàng nguyên container / hàng lẻ ghép | LCL rẻ hơn khi ít hàng nhưng chậm và dễ trễ |
| FTL / LTL | Full / Less than Truckload | Thuê nguyên xe / ghép hàng | Tương tự FCL và LCL nhưng đường bộ |
| TEU / FEU | Twenty-foot / Forty-foot Equivalent Unit | Đơn vị container 20 feet / 40 feet | 1 FEU = 2 TEU |
| CBM | Cubic Meter | Thể tích (m³) | Cước LCL tính theo CBM hoặc tấn, lấy cái lớn hơn |
| GW / NW | Gross Weight / Net Weight | Trọng lượng cả bao bì / trọng lượng hàng |  |
| CY / CFS | Container Yard / Container Freight Station | Bãi container / kho ghép, đóng rút hàng lẻ | CY dành cho FCL, CFS dành cho LCL |
| ICD | Inland Container Depot | Cảng cạn nội địa, nơi thông quan hàng | Ví dụ ICD Tân Cảng, ICD Long Bình |
| ETD / ETA | Estimated Time of Departure / Arrival | Giờ đi / đến dự kiến | ATD, ATA là giờ thực tế (Actual) |
| POL / POD | Port of Loading / Port of Discharge | Cảng xếp / cảng dỡ | POD ở đây khác POD (Proof of Delivery) ở nhóm 3 |
| B/L, MBL, HBL | Bill of Lading, Master / House B/L | Vận đơn đường biển; do hãng tàu / do forwarder phát hành | Là chứng từ sở hữu hàng hóa |
| AWB | Air Waybill | Vận đơn hàng không | Không phải chứng từ sở hữu hàng (khác B/L đường biển) |
| D/O | Delivery Order | Lệnh giao hàng của hãng tàu để lấy hàng tại cảng | Cần để lấy container |
| CI / PL | Commercial Invoice / Packing List | Hóa đơn thương mại / phiếu đóng gói | Bộ chứng từ thông quan cơ bản |
| C/O | Certificate of Origin | Giấy chứng nhận xuất xứ | Giúp hưởng ưu đãi thuế (EVFTA, RCEP...) |
| HS Code | Harmonized System Code | Mã phân loại hàng hóa hải quan | Dùng để xác định thuế suất |
| L/C, T/T | Letter of Credit, Telegraphic Transfer | Thư tín dụng / chuyển tiền | Hai hình thức thanh toán quốc tế phổ biến |
| THC | Terminal Handling Charge | Phí xếp dỡ tại cảng | Một phần trong cước |
| DEM / DET | Demurrage / Detention | Phí lưu container tại bãi / lưu container ngoài bãi quá hạn | Phát sinh khi lấy hàng chậm, làm tăng chi phí |
| Last Mile / Line Haul / Milk Run | Last Mile / Line Haul / Milk Run | Chặng giao cuối / vận chuyển đường dài giữa các kho / chuyến gom hàng vòng tròn nhiều nhà cung cấp | Last Mile thường là khâu tốn chi phí nhất |
| Reefer / Dry | Refrigerated / Dry container | Container lạnh / container khô | Hàng thực phẩm tươi dùng reefer |

### Nhóm 5 — KPI và mức độ phục vụ

Chương kết quả của đồ án nên chứng minh hiệu quả bằng ít nhất một KPI về dịch vụ (Fill Rate, Stockout) và một KPI về vốn (DOH, ITR), trước và sau khi áp dụng dự báo.

| Viết tắt | Tên đầy đủ | Nghĩa tiếng Việt | Ghi chú |
|---|---|---|---|
| KPI | Key Performance Indicator | Chỉ số đo hiệu suất chủ chốt | Chỉ nên chọn 3 đến 5 KPI |
| SLA | Service Level Agreement | Cam kết mức dịch vụ giữa hai bên | Ví dụ: giao trong 24 giờ, 98% đúng hẹn |
| Service Level / CSL | (Cycle) Service Level | Xác suất không hết hàng trong một chu kỳ đặt hàng | Đầu vào chọn z: 90% → 1,28; 95% → 1,65; 99% → 2,33 |
| Fill Rate | Fill Rate | Tỷ lệ nhu cầu được đáp ứng ngay từ tồn kho | Khác CSL: Fill Rate đo theo số lượng, CSL đo theo chu kỳ |
| OTD / OTIF | On Time Delivery / On Time In Full | Giao đúng hẹn / giao đúng hẹn và đủ số lượng | OTIF khắt khe hơn OTD. Nhiều siêu thị phạt khi OTIF thấp |
| POR | Perfect Order Rate | Tỷ lệ đơn hoàn hảo: đúng hẹn, đủ, không hư, đúng chứng từ | KPI tổng hợp khắt khe nhất |
| IRA | Inventory Record Accuracy | Độ chính xác tồn kho sổ sách so với thực tế | Nếu IRA thấp thì dữ liệu đầu vào dự báo cũng sai |
| COGS | Cost Of Goods Sold | Giá vốn hàng bán | Dùng tính ITR |
| ITR | Inventory Turnover Ratio | Vòng quay tồn kho: số lần tồn kho được bán hết trong năm | Càng cao càng tốt, nhưng quá cao có thể dễ hết hàng |
| DOH / DOI / DIO / DSI | Days On Hand / Days of Inventory / Days Inventory Outstanding / Days Sales of Inventory | Số ngày tồn kho còn đủ bán | Bốn tên gọi cùng một ý tùy ngành. WOC (Weeks of Cover) là theo tuần |
| GMROI | Gross Margin Return On Inventory | Lợi nhuận gộp trên mỗi đồng vốn tồn kho | Quan trọng với bán lẻ |
| CCC | Cash-to-Cash Cycle | Thời gian tiền bị “khóa”: DIO + DSO − DPO | DSO là ngày thu tiền, DPO là ngày trả tiền nhà cung cấp |
| Stockout Rate | Stockout Rate | Tỷ lệ ngày (hoặc đơn) bị hết hàng | Dữ liệu mô phỏng ở trên khoảng 3% |
| Dead Stock % | Dead Stock ratio | Tỷ lệ tồn kho không phát sinh xuất trong một thời gian | Thường 6 đến 12 tháng |
| Carrying Cost % | Inventory Carrying Cost | Chi phí lưu kho/năm so với giá trị tồn | Gồm vốn, kho, bảo hiểm, hao hụt |
| TCO | Total Cost of Ownership | Tổng chi phí sở hữu một mặt hàng hoặc hệ thống | Đặt, vận chuyển, lưu kho, hỏng |
| Pick Accuracy | Pick Accuracy | Tỷ lệ dòng soạn đúng | Mục tiêu thường trên 99,5% |
| UPH / LPH | Units / Lines Per Hour | Năng suất soạn hàng mỗi giờ | KPI nhân công kho |
| OEE | Overall Equipment Effectiveness | Hiệu quả thiết bị = sẵn sàng × hiệu suất × chất lượng | Chủ yếu nhà máy, ít dùng cho đồ án này |
| Space Utilization | Space Utilization | Tỷ lệ sử dụng diện tích / thể tích kho | Thường nhắm khoảng 80%, cao hơn sẽ nghẽn |
| SCOR | Supply Chain Operations Reference | Mô hình tham chiếu đo lường chuỗi cung ứng | 6 khâu: Plan, Source, Make, Deliver, Return, Enable |

Công thức của bốn chỉ số hay dùng nhất:

ITR = \frac{COGS}{\text{Tồn kho bình quân}} \qquad DOH = \frac{365}{ITR} \qquad FillRate = \frac{\text{Số lượng giao đủ}}{\text{Số lượng đặt}} \qquad GMROI = \frac{\text{Lợi nhuận gộp}}{\text{Tồn kho bình quân (giá vốn)}}

### Các thuật ngữ nối với nhau thế nào

Một SKU đi qua chu trình dưới đây; mỗi bước sinh ra một chứng từ, và các chứng từ ấy chính là dữ liệu bạn sẽ export.

- Tồn kho chạm ROP → lập PR, gửi RFQ nếu cần so giá

- Chốt nhà cung cấp → phát hành PO (bắt đầu tính LT)

- Nhà cung cấp gửi ASN, xe tới kho → QC rồi lập GRN (sinh qty_in)

- Putaway vào SLOC, IP được cập nhật

- Khách đặt SO → Picking → GI (sinh qty_out)

- Giao bằng xe, khách ký POD → đo OTIF, Fill Rate

Ví dụ số cho một SKU: nhu cầu d = 100 đơn vị/ngày (D = 36.500/năm), σd = 30, LT = 5 ngày, mức phục vụ 95% (z = 1,65), giá vốn 50.000 đ, S = 150.000 đ/lần, h = 20%/năm nên H = 10.000 đ/đơn vị/năm.

| Chỉ số | Cách tính | Kết quả |
|---|---|---|
| EOQ | √(2 × 36.500 × 150.000 / 10.000) | khoảng 1.046 đơn vị |
| SS | 1,65 × 30 × √5 | khoảng 111 đơn vị |
| ROP | 100 × 5 + 111 | 611 đơn vị |

Hiểu là: khi IP tụt xuống 611 thì đặt khoảng 1.046 đơn vị (nếu lớn hơn MOQ).

#### Cặp thuật ngữ dễ nhầm

| Cặp | Khác nhau chỗ nào |
|---|---|
| POD (Proof of Delivery) và POD (Port of Discharge) | Cùng viết tắt; đọc ngữ cảnh. Một bên là chứng từ giao hàng, một bên là cảng dỡ |
| DN và D/O | DN là phiếu giao hàng nội bộ; D/O là lệnh của hãng tàu để nhận container |
| Service Level và Fill Rate | Service Level là xác suất không hết hàng; Fill Rate là phần trăm số lượng được đáp ứng. Hai số thường khác nhau |
| MAPE và WMAPE | MAPE lấy trung bình tỷ lệ sai từng ngày; WMAPE chia tổng sai cho tổng nhu cầu nên ít bị ngày nhỏ làm lệch |
| Demand và Sales | Demand là nhu cầu thật; Sales/qty_out là lượng ra thực tế, thấp hơn demand khi hết hàng |
| Lead Time và Cycle Time | Lead Time tính từ lúc đặt đến lúc nhận; Cycle Time tính cho một công đoạn nội bộ |
| ITR và DOH | ITR là số lần quay/năm; DOH là số ngày tồn; hai số nghịch đảo của nhau (DOH = 365 / ITR) |
| CIF và CIP | CIF chỉ dùng đường biển và mức bảo hiểm thấp hơn; CIP dùng mọi phương thức |

Tài liệu được tổng hợp từ kiến thức chuyên ngành phổ biến (APICS/ASCM, GS1, Incoterms 2020) và chưa đối chiếu từng định nghĩa với nguồn trực tuyến. Khi trích trong đồ án, bạn nên dẫn giáo trình hoặc bài báo gốc cho các công thức chính.
