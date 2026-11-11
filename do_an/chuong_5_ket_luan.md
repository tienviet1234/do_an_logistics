# CHƯƠNG 5. KẾT LUẬN VÀ ĐỀ XUẤT

> **Ghi chú cho người viết (xóa trước khi nộp)**
> - Bản nháp lần 1, soạn ngày 11/11/2026. Mọi con số lặp lại từ Chương 4; đối chiếu lại sau khi chạy lại toàn bộ hệ thống.
> - Đề xuất viết cho **kho tổng của chuỗi siêu thị nói chung**, không gắn với một đơn vị cụ thể (quyết định 05/11). Nếu sau này có đơn vị thực tập thì sửa mục 5.2 theo đơn vị đó.

## 5.1. Kết quả đạt được

Đề tài đã xây dựng một quy trình hoàn chỉnh, từ dữ liệu xuất nhập tồn đến quyết định đặt hàng hằng ngày, và đánh giá quy trình trên hai bộ dữ liệu: số bán thật M5 (Walmart) và bộ mô phỏng nghiệp vụ kho hàng tiêu dùng Việt Nam. Đối chiếu với các mục tiêu ở Chương 1:

| Mục tiêu | Kết quả |
|---|---|
| 1. Dữ liệu và tiền xử lý | Làm sạch theo đẳng thức tồn kho: sửa 687 dòng lỗi, đối chiếu đáp án không còn dòng sai, không xóa nhầm đỉnh nhu cầu thật; nhận diện đủ 4.050/4.050 ngày hết hàng và loại chúng khỏi nhu cầu. Lịch sự kiện gồm cả Tết và Trung thu theo âm lịch |
| 2. Phân tích nhu cầu, phân loại | Phân loại ABC, XYZ, Syntetos–Boylan tính trên tập huấn luyện. Hai bộ khác nhau rõ ở nhóm Z (40 mã so với 1 mã) và chu kỳ tuần |
| 3. Mô hình dự báo | So sánh trên cùng khung kiểm định cuốn chiếu 6 phương pháp mốc, Prophet, LightGBM, các phương án kết hợp, LSTM, RNN, TiDE, N-HiTS, TFT. Trên **số bán thật M5**, mô hình được chọn giảm WMAPE **13,8%** so với trung bình trượt (0,307 so với 0,356), Bias +3,1%. Trên bộ mô phỏng, mô hình giảm 54% so với Seasonal Naive và 39% so với trung bình trượt, Bias +3,0%, khoảng dự báo 80% và 95% đúng mức danh nghĩa |
| 4. Tham số tồn kho | SS tính từ sai số dự báo thực tế trong thời gian chờ hàng và độ dao động lead time; ROP theo dự báo; quy tắc lượng đặt chọn trên tập kiểm định (EOQ cho hàng ổn định, đặt đến mức cho hàng mùa vụ) |
| 5. Mô phỏng và so sánh | So với dự báo mốc dùng cùng công thức: chi phí liên quan giảm **35,3%** trên bộ mô phỏng nhưng chỉ **1,7%** trên M5. Trên bộ mô phỏng: Fill Rate 95,82%, tồn kho không cao hơn hiện trạng (−0,7%), số ngày-mã thiếu hàng giảm 53% |
| 6. Đề xuất áp dụng | Mục 5.2, kèm hệ thống hỗ trợ quyết định (dashboard 5 màn, dữ liệu cho Power BI) |

**Trả lời các câu hỏi nghiên cứu:**

1. *Trí tuệ nhân tạo cải thiện độ chính xác dự báo bao nhiêu, ở nhóm hàng nào?* Trên số bán thật, khoảng 14% so với trung bình trượt. Mức cải thiện lớn nhất nằm ở hàng mùa vụ và hàng theo sự kiện, nơi mô hình khai thác được lịch lễ và lịch âm; với hàng bán đều, mức cải thiện nhỏ.
2. *Yếu tố nào ảnh hưởng nhiều nhất đến nhu cầu?* Đặc điểm riêng của từng mã và mức bán gần đây quyết định phần lớn mức nhu cầu; trong các yếu tố lịch, Tết (tính theo âm lịch), chu kỳ tuần và các dịp lễ có cửa sổ ảnh hưởng dài là quan trọng nhất; khuyến mãi làm bán tăng mạnh mỗi lần (trung vị tăng khoảng 50–60% tùy cách đo) nhưng chỉ chiếm một phần nhỏ số ngày.
3. *Chuyển dự báo thành chính sách tồn kho thì cải thiện bao nhiêu?* Phụ thuộc mạnh vào cơ cấu mặt hàng: từ 1,7% (hàng chủ yếu bán đều) đến 35,3% (nhiều hàng mùa vụ) chi phí liên quan, trong đó khoảng 92% lợi ích trên bộ mô phỏng đến từ nhóm hàng mùa vụ.

**Kết luận chính của đề tài:** trí tuệ nhân tạo có giá trị thực sự với kho tổng chủ yếu ở **hàng mùa vụ, hàng theo dịp lễ và sự kiện**. Với hàng bán đều quanh năm, phương pháp đơn giản (trung bình trượt cập nhật mỗi tuần) cộng tồn kho an toàn tính đúng cách đã cho kết quả gần như tương đương. Cải thiện lớn nhất đến từ **quy trình**: dùng số liệu mới nhất mỗi tuần, so sánh theo âm lịch, chọn quy tắc đặt hàng riêng cho hàng mùa vụ, và cập nhật tham số khi lead time thay đổi.

## 5.2. Đề xuất áp dụng cho kho tổng của chuỗi siêu thị

Đề xuất được sắp theo thứ tự ưu tiên, bắt đầu từ việc rẻ và chắc chắn có lợi.

**Bước 1: Chuẩn hóa dữ liệu và quy trình cập nhật (tháng 1–2).**
- Ghi đủ năm cột cho mỗi mã mỗi ngày: ngày, mã hàng, số nhập, số xuất, tồn cuối ngày. Đây là đầu vào duy nhất bắt buộc của hệ thống.
- Đánh dấu ngày hết hàng (tồn bằng 0 khi còn nhu cầu) để không lấy số bán ngày đó làm nhu cầu.
- Lập lịch sự kiện biết trước cho 28 ngày tới: ngày lễ, Tết, lịch khuyến mãi do bộ phận bán hàng gửi, sale sàn thương mại điện tử.
- Theo dõi lead time thực tế của từng nhà cung cấp hằng tháng và cập nhật vào công thức (mục 4.7.6: không cập nhật khi lead time dài thêm 2 ngày làm chi phí tăng 59%).

**Bước 2: Áp dụng cho hàng mùa vụ và hàng theo dịp trước (tháng 2–4).**
- Đây là nơi lợi ích lớn nhất: dùng mô hình có lịch lễ (kết hợp LightGBM và Prophet), quy tắc đặt đến mức thay vì EOQ, và với hàng chỉ bán một dịp thì cân nhắc đặt một lần trước mùa theo mô hình newsvendor.
- Dừng đặt khi hàng sẽ về sau khi mùa đã qua.

**Bước 3: Mở rộng cho nhóm A ổn định, rồi B và C (sau 3 tháng).**
- Với hàng ổn định, dùng công thức SS/ROP với dự báo cập nhật mỗi tuần; có thể bắt đầu bằng trung bình trượt và chỉ chuyển sang mô hình phức tạp hơn khi tập kiểm định cho thấy lợi ích rõ.
- Tự động hóa đề xuất đặt hàng cho nhóm A-X trước; người lập kế hoạch duyệt.

**Bước 4: Vận hành và theo dõi.**
- Mỗi tuần: cập nhật dữ liệu, chạy lại dự báo, xem màn "Hôm nay" để duyệt đơn.
- Mỗi quý: chạy lại vòng so sánh mô hình trên dữ liệu mới theo đúng luật (chọn trên tập kiểm định, không mặc định mô hình nào thắng).
- Gom đơn theo nhà cung cấp để chia sẻ chi phí phiếu; trước khi áp dụng cần đo tỉ lệ chi phí chung thực tế của một phiếu.

**Điều kiện để đề xuất có hiệu lực:** kho cần dữ liệu tồn kho đáng tin, lịch khuyến mãi gửi trước ít nhất 28 ngày, và một người chịu trách nhiệm cập nhật tham số. Mức lợi ích thực tế phải được đo lại trên dữ liệu của chính kho đó; các con số trong đồ án chỉ cho biết **hướng** và **nhóm hàng nên ưu tiên**.

## 5.3. Hạn chế

1. **Không có số liệu của một kho Việt Nam cụ thể.** M5 là số bán thật của Mỹ, 10 cửa hàng, giai đoạn 2011–2016; bộ mô phỏng có bối cảnh Việt Nam nhưng không phải số thật. Kho tổng dựng từ M5 là xấp xỉ: lượng xuất thay bằng tổng số bán của cửa hàng; tồn kho, lead time, chi phí, nhà cung cấp đều là giả định.
2. **Bộ mô phỏng có lợi thế cho mô hình:** nhu cầu sinh từ chính lịch lễ và lịch khuyến mãi mà mô hình được biết; "hiện trạng" trong bộ mô phỏng lại mạnh hơn thực tế (người lập kế hoạch biết trước nhu cầu kỳ vọng). Hai sai lệch này đi ngược chiều nhau và không đo được chính xác.
3. **M5 không có cờ hết hàng**, nên nhu cầu bị che ở những ngày cửa hàng hết hàng không tách được.
4. **Mô phỏng tồn kho** giả định mất bán khi hết hàng (không nợ đơn), nhận hàng vào ngày kho mở cửa, chưa xét gom đủ xe, chiết khấu theo số lượng, sức chứa theo từng khu vực kho.
5. **Một số quyết định trông "kém" trên tập kiểm tra** (giữ mô hình kết hợp thay vì RNN trên bộ mô phỏng, giữ chính sách có hiệu chỉnh thay vì không hiệu chỉnh) vì đã chọn theo tập kiểm định. Đây là cái giá của việc không chọn theo đề thi; chênh lệch nhỏ nhưng được ghi lại.
6. **Cảnh báo dự báo lệch không đạt yêu cầu**; hệ thống chưa có cơ chế báo sớm khi mô hình bắt đầu sai.
7. **Giải thích theo yếu tố** chỉ có cho LightGBM và Prophet; phần học sâu (RNN) chỉ có con số tổng. Mô hình chưa phân biệt tốt mã nào tăng mạnh khi khuyến mãi (tương quan thứ hạng 0,39 với lịch sử).
8. **Dashboard phát lại kết quả mô phỏng** chứ chưa nối với hệ thống quản lý kho thật; quyết định duyệt đơn chỉ giữ trong phiên làm việc.

## 5.4. Hướng phát triển

1. **Áp dụng trên dữ liệu thật của một kho Việt Nam:** thay dữ liệu đầu vào (giữ nguyên cấu trúc cột) và chạy lại toàn bộ quy trình bằng một lệnh; đo lại mức lợi ích thực tế theo từng nhóm hàng.
2. **Chính sách riêng cho hàng mùa vụ:** kết hợp newsvendor với cập nhật giữa mùa, có tính hạn sử dụng và khả năng trả hàng nhà cung cấp.
3. **Thông tin bên ngoài:** đưa cảnh báo bão, dự báo thời tiết ngắn hạn vào dưới dạng điều chỉnh ngắn hạn khi có đủ dữ liệu lịch sử để học; với dữ liệu hiện có (1–2 trận bão), cách làm này chưa đạt.
4. **Tồn kho an toàn theo phân vị thực nghiệm** của sai số thay cho giả định phân phối chuẩn, nhất là cho hàng mùa vụ có sai số lệch một phía.
5. **Cảnh báo lệch dự báo:** thử các tín hiệu khác (theo nhóm hàng, theo tổng lead time) khi có dữ liệu dài hơn.
6. **Kết nối hệ thống quản lý kho:** đọc dữ liệu tự động hằng ngày, ghi lại quyết định duyệt đơn để học từ điều chỉnh của người lập kế hoạch.
7. **Phiên livestream và kênh trực tuyến:** hiện chỉ có phân tích dựa trên giả định; cần dữ liệu phiên thật để kiểm chứng.

## KẾT LUẬN

Đề tài "Ứng dụng trí tuệ nhân tạo trong dự báo nhu cầu và tối ưu hóa quản lý tồn kho" đã xây dựng một quy trình đi trọn từ dữ liệu xuất nhập tồn đến đề xuất đặt hàng hằng ngày cho kho tổng của chuỗi siêu thị, kèm một hệ thống hỗ trợ quyết định cho người lập kế hoạch. Quy trình được đánh giá công bằng: cùng khung kiểm định theo thời gian, luật chọn ghi trước khi chạy, tập kiểm tra chỉ dùng một lần, và được kiểm chứng trên cả số bán thật lẫn dữ liệu mô phỏng nghiệp vụ Việt Nam.

Kết quả cho thấy mô hình trí tuệ nhân tạo dự báo chính xác hơn phương pháp đơn giản trên số bán thật (giảm sai số khoảng 14%), nhưng giá trị của nó đối với tồn kho phụ thuộc mạnh vào cơ cấu mặt hàng: lớn ở hàng mùa vụ và hàng theo dịp, nhỏ ở hàng bán đều. Vì vậy, khi áp dụng, kho nên bắt đầu từ nhóm hàng mùa vụ, chuẩn hóa dữ liệu và cập nhật tham số đều đặn, và đo lại lợi ích trên dữ liệu của chính mình trước khi mở rộng.
