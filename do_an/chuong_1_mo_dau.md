# CHƯƠNG 1. MỞ ĐẦU

> **Ghi chú cho người viết (xóa trước khi nộp)**
> - Bản nháp lần 1, soạn ngày 23/10/2026 từ `docs/08` (báo cáo GĐ1) và `docs/10` (báo cáo GĐ2).
> - Tên đề tài lấy theo Báo cáo Giai đoạn 1. Cần đối chiếu với tên **chính thức** trên quyết định giao đề tài; các tài liệu làm việc đang dùng tên rút gọn "Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho".
> - Các chỗ **[CẦN TRÍCH DẪN: ...]** là nhận định cần số liệu hoặc nguồn chính thức. Phải tự tra nguồn và điền, **không** để trống hoặc tự đặt số khi nộp.
> - Mục 1.4.2 và 1.7 phụ thuộc ý kiến giảng viên về việc dùng dữ liệu mô phỏng. Sửa lại sau khi có trả lời.
> - Đánh số mục theo mẫu của trường nếu khác.

**Tên đề tài:** Ứng dụng trí tuệ nhân tạo trong dự báo nhu cầu và tối ưu hóa quản lý tồn kho

## 1.1. Lý do chọn đề tài

Tồn kho là một trong những khoản mục chi phí lớn của hoạt động logistics. Giữ quá nhiều hàng làm tăng chi phí lưu kho, chi phí vốn và rủi ro hàng tồn đọng, hư hỏng, lỗi thời. Giữ quá ít hàng dẫn đến hết hàng, mất doanh thu và giảm mức độ hài lòng của khách hàng. [CẦN TRÍCH DẪN: tỷ trọng chi phí logistics trên GDP của Việt Nam và tỷ trọng chi phí tồn kho trong chi phí logistics, nguồn: Báo cáo Logistics Việt Nam của Bộ Công Thương hoặc tương đương.]

Mọi quyết định tồn kho, từ đặt bao nhiêu, đặt khi nào đến giữ bao nhiêu hàng dự phòng, đều bắt đầu từ một con số dự báo nhu cầu. Tại nhiều doanh nghiệp vừa và nhỏ, dự báo vẫn dựa trên kinh nghiệm của người lập kế hoạch hoặc trung bình đơn giản trên bảng tính. [CẦN TRÍCH DẪN: khảo sát hoặc nghiên cứu về mức độ ứng dụng công cụ dự báo tại doanh nghiệp Việt Nam.] Cách làm này khó xử lý các đặc điểm phổ biến của nhu cầu hàng tiêu dùng tại Việt Nam:

- **Mùa vụ mạnh và lệch lịch:** Tết Nguyên đán và Tết Trung thu theo âm lịch nên thay đổi ngày dương lịch mỗi năm; nhiều mặt hàng chỉ bán trong một mùa ngắn.
- **Nhiều sự kiện tác động:** ngày lễ, khuyến mãi, các đợt sale lớn của sàn thương mại điện tử (11.11, 12.12, Black Friday).
- **Cú sốc khó lường:** bão lũ làm nhu cầu nhu yếu phẩm tăng vọt trước và sau bão, đồng thời làm gián đoạn giao hàng (ví dụ bão số 3 Yagi tháng 9/2024).
- **Dữ liệu bán hàng bị "che":** những ngày hết hàng, lượng xuất kho thấp hơn nhu cầu thật; dùng trực tiếp số liệu này để dự báo sẽ dẫn đến dự báo thấp và tiếp tục hết hàng.

Các phương pháp trí tuệ nhân tạo và học máy, như Prophet hay các mô hình cây quyết định tăng cường (LightGBM, XGBoost), có khả năng đưa lịch lễ, khuyến mãi và nhiều yếu tố khác vào dự báo. Tuy nhiên, mô hình phức tạp không mặc nhiên tốt hơn phương pháp đơn giản; lợi ích thực tế chỉ được chứng minh khi so sánh công bằng với các phương pháp mốc và khi dự báo được chuyển thành quyết định tồn kho cụ thể. [CẦN TRÍCH DẪN: 1–2 nghiên cứu so sánh mô hình học máy và mô hình thống kê trong dự báo nhu cầu bán lẻ, ví dụ các cuộc thi dự báo M5.]

Từ những lý do trên, đề tài "Ứng dụng trí tuệ nhân tạo trong dự báo nhu cầu và tối ưu hóa quản lý tồn kho" được lựa chọn nhằm xây dựng một quy trình hoàn chỉnh, đi từ dữ liệu xuất nhập tồn đến dự báo, tham số tồn kho và đánh giá hiệu quả bằng mô phỏng.

## 1.2. Mục tiêu nghiên cứu

### 1.2.1. Mục tiêu tổng quát

Xây dựng và đánh giá một quy trình ứng dụng trí tuệ nhân tạo để dự báo nhu cầu theo ngày cho từng mã hàng (SKU) tại kho phân phối hàng tiêu dùng, từ đó xác định các tham số tồn kho và chứng minh mức cải thiện so với cách lập kế hoạch hiện có.

### 1.2.2. Mục tiêu cụ thể

1. Xây dựng bộ dữ liệu đầu vào và quy trình tiền xử lý: làm sạch dữ liệu xuất nhập tồn, nhận diện ngày hết hàng, xây dựng lịch các yếu tố tác động đến nhu cầu (ngày lễ, khuyến mãi, sale, bão lũ).
2. Phân tích đặc điểm nhu cầu và phân loại mã hàng theo ABC, XYZ và mức độ bán rời rạc.
3. Xây dựng và so sánh các mô hình dự báo: nhóm mô hình mốc (Naive, trung bình trượt, ETS, ARIMA, Croston/TSB) và nhóm mô hình trí tuệ nhân tạo (Prophet, LightGBM, học sâu LSTM, RNN, TiDE, N-HiTS, TFT) và các phương án kết hợp, trên cùng một khung đánh giá theo thời gian.
4. Từ kết quả dự báo, xác định lượng đặt hàng tối ưu (EOQ), tồn kho an toàn (Safety Stock) và điểm đặt hàng lại (Reorder Point) cho từng mã hàng.
5. Mô phỏng và so sánh chính sách tồn kho dựa trên dự báo với chính sách hiện có qua các chỉ tiêu: tỷ lệ đáp ứng (Fill Rate), số ngày hết hàng, tồn kho bình quân, số ngày tồn kho (DOH), tổng chi phí đặt hàng và lưu kho.
6. Đề xuất cách áp dụng kết quả cho doanh nghiệp.

**Chỉ tiêu đánh giá dự kiến** (cần giảng viên duyệt): mô hình được chọn giảm sai số dự báo (WMAPE) ít nhất 20% so với mô hình Seasonal Naive và thắng mô hình mốc tốt nhất; chính sách tồn kho đề xuất đạt Fill Rate từ 95% trở lên mà không làm tăng tồn kho bình quân so với hiện trạng.

## 1.3. Câu hỏi nghiên cứu

1. Mô hình trí tuệ nhân tạo cải thiện độ chính xác dự báo bao nhiêu so với các phương pháp đơn giản, và cải thiện ở nhóm mã hàng nào?
2. Các yếu tố nào (ngày lễ, khuyến mãi, mùa vụ, thứ trong tuần...) ảnh hưởng nhiều nhất đến nhu cầu?
3. Khi chuyển dự báo thành chính sách tồn kho, mức cải thiện về tỷ lệ đáp ứng, lượng tồn kho và chi phí là bao nhiêu?

## 1.4. Đối tượng và phạm vi nghiên cứu

### 1.4.1. Đối tượng nghiên cứu

Hoạt động dự báo nhu cầu và quản lý tồn kho theo từng mã hàng tại kho phân phối hàng tiêu dùng nhanh.

### 1.4.2. Phạm vi nghiên cứu

- **Không gian:** bài toán kho tổng của chuỗi siêu thị nói chung, không gắn với một đơn vị cụ thể. Bộ dữ liệu mô phỏng lấy bối cảnh miền Bắc Việt Nam; bộ M5 là số bán tại Mỹ.
- **Thời gian dữ liệu:** theo ngày. Bộ M5 từ 29/01/2011 đến 22/05/2016; bộ mô phỏng 36 tháng, từ 01/10/2023 đến 30/09/2026.
- **Mặt hàng:** mỗi bộ 121 mã hàng. Bộ mô phỏng gồm 17 nhóm (thực phẩm khô, đồ uống, bánh kẹo, hóa phẩm, gia dụng, văn phòng phẩm, hàng thời vụ...), từ 14 nhà cung cấp, thời gian giao hàng từ 1 đến 15 ngày. Bộ M5 gồm thực phẩm, gia dụng và hàng sở thích, tên hàng được nguồn dữ liệu ẩn; nhà cung cấp và thời gian giao hàng là giả định.
- **Dữ liệu:** đề tài không sử dụng số liệu của một đơn vị cụ thể mà dùng hai bộ dữ liệu với vai trò khác nhau. **Bộ M5** (số bán thật của Walmart, Mỹ, cộng 10 cửa hàng thành một kho tổng) là cơ sở chính để đánh giá dự báo; giá bán là số thật, còn tồn kho, chi phí và thời gian giao hàng là giả định. **Bộ mô phỏng** được xây dựng có chủ đích để minh họa các nghiệp vụ mà M5 không có: mùa vụ Việt Nam, ngày lễ, khuyến mãi, bão lũ (theo ngày bão thực tế), hết hàng và lỗi nhập liệu; ngày diễn ra các cơn bão và lịch thi đấu thể thao là số liệu thực tế, mức độ tác động là giả định. Kết quả tồn kho được báo trên cả hai bộ. Kết quả không phải số liệu của một kho Việt Nam; quy trình được thiết kế để thay bằng dữ liệu thật, chỉ cần giữ nguyên cấu trúc cột.
- **Nội dung:** dự báo nhu cầu với tầm 28 ngày; tham số tồn kho theo mô hình đặt hàng cố định (EOQ, SS, ROP); không nghiên cứu bài toán định tuyến vận tải và bố trí mặt bằng kho.

## 1.5. Phương pháp nghiên cứu

1. **Nghiên cứu tài liệu:** tổng hợp lý thuyết về quản lý tồn kho, dự báo chuỗi thời gian và học máy (Chương 2).
2. **Xây dựng và xử lý dữ liệu:** dựng bộ dữ liệu kho từ số bán M5 và mô phỏng dữ liệu bằng Python; với bộ mô phỏng, làm sạch dựa trên đẳng thức tồn kho (tồn cuối = tồn đầu + nhập − xuất); nhận diện ngày hết hàng để không coi lượng xuất ngày đó là nhu cầu.
3. **Thống kê mô tả và phân tích khám phá:** phân tích chu kỳ tuần, mùa vụ, tác động khuyến mãi; phân loại ABC/XYZ và phân loại nhu cầu theo Syntetos–Boylan.
4. **Mô hình hóa dự báo:** các mô hình thống kê (ETS, ARIMA, Croston, TSB), mô hình trí tuệ nhân tạo (Prophet, LightGBM), mô hình học sâu (LSTM, RNN, TiDE, N-HiTS, TFT) và kết hợp dự báo.
5. **Đánh giá theo thời gian (backtest cuốn chiếu):** chia dữ liệu theo trình tự thời gian (12 tháng cuối để kiểm tra, phần trước để huấn luyện), dự báo lặp lại tại nhiều mốc; đo bằng MAE, RMSE, WMAPE, MASE và Bias. Mô hình chỉ được sử dụng thông tin biết trước tại thời điểm dự báo.
6. **Mô hình tồn kho và mô phỏng:** tính EOQ, Safety Stock, Reorder Point từ kết quả dự báo; mô phỏng vận hành kho trong 12 tháng để so sánh các chính sách.

Công cụ: Python (pandas, statsforecast, Prophet, LightGBM, PyTorch, NeuralForecast), SQLite (cơ sở dữ liệu), Streamlit (dashboard), Power BI.

## 1.6. Ý nghĩa của đề tài

- **Ý nghĩa khoa học:** đề xuất một quy trình đánh giá công bằng giữa mô hình trí tuệ nhân tạo và phương pháp truyền thống, có xử lý các vấn đề thường bị bỏ qua: nhu cầu bị che do hết hàng, rò rỉ thông tin tương lai, và lựa chọn chỉ số sai số phù hợp với nhu cầu theo ngày.
- **Ý nghĩa thực tiễn:** cung cấp quy trình và công cụ có thể áp dụng cho kho phân phối khi có dữ liệu thật; chỉ ra nhóm mã hàng nào nên ưu tiên áp dụng mô hình nâng cao và nhóm nào chỉ cần phương pháp đơn giản.

## 1.7. Bố cục đồ án

Ngoài phần mở đầu, kết luận, tài liệu tham khảo và phụ lục, đồ án gồm 5 chương:

- **Chương 1. Mở đầu:** lý do, mục tiêu, phạm vi và phương pháp nghiên cứu.
- **Chương 2. Cơ sở lý thuyết:** quản lý tồn kho (EOQ, Safety Stock, Reorder Point, ABC/XYZ), dự báo nhu cầu, các mô hình thống kê và học máy, chỉ số đánh giá dự báo.
- **Chương 3. Mô tả bài toán và dữ liệu:** bối cảnh kho tổng chuỗi siêu thị, phát biểu bài toán, hai bộ dữ liệu và đặc điểm của chúng, quy trình tiền xử lý, giới hạn của dữ liệu.
- **Chương 4. Xây dựng mô hình và đánh giá kết quả:** phân tích khám phá, tạo đặc trưng, khung đánh giá, kết quả các mô hình dự báo, tham số tồn kho, mô phỏng và so sánh chính sách, dashboard.
- **Chương 5. Kết luận và đề xuất:** kết quả đạt được, đề xuất áp dụng, hạn chế và hướng phát triển.
