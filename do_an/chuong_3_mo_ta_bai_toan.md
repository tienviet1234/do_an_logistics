# CHƯƠNG 3. MÔ TẢ BÀI TOÁN VÀ DỮ LIỆU

> **Ghi chú cho người viết (xóa trước khi nộp)**
> - Bản nháp lần 1, soạn ngày 10/11/2026. Mọi con số lấy từ `reports/so_lieu_do_an.md` (mục 1 và 10.0), `docs/10` (mục 2, 3, 9.8, 10.13) và các báo cáo được ghi nguồn ngay dưới bảng. Không có số nào gõ tay; dữ liệu đổi thì chạy lại `python src/so_lieu_do_an.py` rồi sửa theo.
> - Theo quyết định 05/11: chưa thực tập, chưa có dữ liệu của đơn vị thực tập, nên chương này **mô tả bài toán**, không viết thực trạng một kho cụ thể. Cần giảng viên xác nhận.
> - Các chỗ **[CẦN TRÍCH DẪN: ...]** phải tự tra nguồn chính thức và điền; không để trống khi nộp.
> - Hình 3.x lấy từ `reports/eda/`; đánh số lại theo mẫu của trường.

Chương này trình bày bài toán mà đề tài giải quyết và dữ liệu dùng để giải quyết nó. Vì đề tài không sử dụng số liệu của một đơn vị cụ thể, bài toán được phát biểu cho một **kho tổng của chuỗi siêu thị nói chung**. Bài toán được kiểm tra trên hai bộ dữ liệu bổ sung cho nhau: bộ **M5** chứa số bán thật của chuỗi bán lẻ Walmart (Mỹ), và bộ **mô phỏng** được xây dựng để thể hiện các nghiệp vụ đặc thù của kho hàng tiêu dùng tại Việt Nam.

## 3.1. Bối cảnh: kho tổng của chuỗi siêu thị

Kho tổng (trung tâm phân phối) là điểm tập trung hàng hóa giữa các nhà cung cấp và hệ thống cửa hàng của một chuỗi bán lẻ. Hàng từ nhà cung cấp về kho theo đơn đặt hàng của kho, được lưu trữ, rồi xuất đi các cửa hàng theo nhu cầu bán ra của từng cửa hàng, và với một số chuỗi còn phục vụ thêm đơn hàng trực tuyến. [CẦN TRÍCH DẪN: mô tả mô hình trung tâm phân phối của chuỗi bán lẻ, ví dụ giáo trình quản trị logistics hoặc báo cáo công khai của một chuỗi siêu thị tại Việt Nam.]

Luồng hàng và luồng thông tin của kho tổng được mô tả như sau:

1. **Nhà cung cấp → kho tổng:** kho đặt hàng theo từng mã hàng (SKU); hàng về sau một khoảng thời gian chờ (lead time) khác nhau giữa các nhà cung cấp và dao động giữa các lần giao.
2. **Kho tổng → cửa hàng:** lượng xuất kho mỗi ngày phản ánh nhu cầu bán ra của hệ thống cửa hàng. Nhu cầu này chịu tác động của chu kỳ tuần, mùa vụ, ngày lễ, khuyến mãi và các sự kiện bất thường.
3. **Thông tin biết trước:** lịch ngày lễ, lịch khuyến mãi do bộ phận bán hàng lên trước, các đợt sale của sàn thương mại điện tử. Đây là những thông tin mà người lập kế hoạch có trong tay tại thời điểm đặt hàng.
4. **Thông tin không biết trước:** bão lũ, dịch bệnh, đơn hàng lớn đột xuất, nhà cung cấp giao chậm. Những yếu tố này có thể giải thích được sau khi đã xảy ra, nhưng không dùng được để dự báo.

Người lập kế hoạch tại kho đối mặt với một mâu thuẫn: giữ nhiều hàng thì tốn chi phí lưu kho và có nguy cơ tồn đọng, nhất là với hàng có hạn sử dụng hoặc hàng chỉ bán trong một mùa; giữ ít hàng thì cửa hàng thiếu hàng và mất doanh thu. Mọi quyết định đặt hàng đều dựa trên một ước lượng về nhu cầu sắp tới. Vì vậy chất lượng dự báo nhu cầu, và cách chuyển dự báo thành lượng đặt hàng, quyết định trực tiếp chi phí và mức phục vụ của kho.

## 3.2. Phát biểu bài toán

### 3.2.1. Quyết định cần đưa ra

Với mỗi mã hàng, tại mỗi ngày làm việc, kho cần trả lời ba câu hỏi:

- **Có cần đặt hàng hôm nay không?** Đặt khi lượng tồn kho cộng hàng đang về không đủ phục vụ nhu cầu trong thời gian chờ hàng.
- **Đặt bao nhiêu?** Cân bằng giữa chi phí mỗi lần đặt hàng và chi phí giữ hàng trong kho.
- **Giữ bao nhiêu hàng dự phòng?** Đủ để hấp thụ sai số dự báo và dao động của thời gian giao hàng.

Để trả lời, bài toán được chia thành hai bước nối tiếp nhau:

1. **Dự báo nhu cầu** theo ngày cho từng mã hàng, tầm dự báo 28 ngày. Tầm 28 ngày được chọn để lớn hơn thời gian chờ hàng dài nhất trong dữ liệu (15 ngày), nên tại thời điểm đặt hàng luôn có dự báo phủ hết khoảng chờ.
2. **Chuyển dự báo thành tham số tồn kho:** tồn kho an toàn (Safety Stock, SS), điểm đặt hàng lại (Reorder Point, ROP) và lượng đặt hàng (Q, theo EOQ hoặc quy tắc được chọn), rồi vận hành chính sách đó qua từng ngày để đo kết quả.

### 3.2.2. Đầu vào, đầu ra, mục tiêu và ràng buộc

**Bảng 3.1. Phát biểu bài toán**

| Thành phần | Nội dung |
|---|---|
| **Đầu vào** | Lịch sử xuất kho theo ngày của từng mã; lịch thông tin biết trước (thứ trong tuần, ngày lễ, Tết âm lịch, khuyến mãi đã lên lịch, sale sàn thương mại điện tử); thông tin mã hàng (giá vốn, giá bán, nhóm hàng, nhà cung cấp); thông tin nhà cung cấp (lead time trung bình và độ lệch chuẩn, lượng đặt tối thiểu); chi phí đặt hàng mỗi lần, tỉ lệ chi phí lưu kho |
| **Đầu ra** | Dự báo nhu cầu 28 ngày tới cho từng mã, kèm khoảng dự báo; SS, ROP, Q của từng mã; danh sách mã cần đặt hôm nay và lượng đặt đề xuất |
| **Mục tiêu** | Giảm **chi phí liên quan** = chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do thiếu hàng, trong khi giữ mức phục vụ mục tiêu |
| **Ràng buộc** | Mức phục vụ mục tiêu 95% (xác suất không hết hàng trong một chu kỳ đặt hàng); lead time của từng nhà cung cấp; lượng đặt tối thiểu (MOQ); kho nghỉ một số ngày (Tết, lễ) nên không nhận, không xuất hàng; dự báo chỉ được dùng thông tin đã biết tại thời điểm lập |
| **Ràng buộc phụ** (phân tích riêng, Chương 4) | Hạn sử dụng của hàng dễ hỏng; sức chứa kho; gom đơn theo nhà cung cấp |

Lợi nhuận mất được đưa vào hàm mục tiêu thay cho một "chi phí thiếu hàng" ước đoán: khi cửa hàng hết hàng, khoản mất đi là phần lợi nhuận của số hàng không bán được (giá bán trừ giá vốn). Cách tính này dùng được ngay từ dữ liệu giá, không cần giả định thêm một hệ số phạt.

### 3.2.3. Chỉ số đánh giá

Bài toán được đánh giá ở cả hai bước. Định nghĩa đầy đủ của từng chỉ số được trình bày ở Chương 2; bảng dưới tóm tắt chỉ số và lý do chọn.

**Bảng 3.2. Chỉ số đánh giá**

| Bước | Chỉ số | Vì sao dùng |
|---|---|---|
| Dự báo | **WMAPE** (sai số tuyệt đối có trọng số theo lượng bán) | Chỉ số chính. Không bị vô hạn khi nhu cầu bằng 0 như MAPE; mã bán nhiều có trọng số lớn hơn, đúng với tác động lên tồn kho |
| Dự báo | **Bias** (độ lệch có dấu) | Cho biết dự báo thừa hay thiếu có hệ thống; dự báo thiếu kéo theo hết hàng |
| Dự báo | MAE, RMSE, MASE | Bổ sung; MASE so với Seasonal Naive để biết mô hình có hơn cách đơn giản nhất không |
| Tồn kho | **Fill Rate** | Tỉ lệ nhu cầu được đáp ứng ngay từ kho |
| Tồn kho | Số ngày-mã thiếu hàng | Số lần cửa hàng gặp tình trạng hết hàng |
| Tồn kho | Tồn kho bình quân (giá trị), số ngày tồn (DOH), vòng quay | Vốn bị giữ trong kho |
| Tồn kho | **Chi phí liên quan** | Hàm mục tiêu ở Bảng 3.1; dùng để chọn chính sách |

Tiêu chí đạt được đặt ra từ đầu đề tài: mô hình dự báo được chọn giảm WMAPE ít nhất 20% so với Seasonal Naive; chính sách tồn kho dựa trên dự báo đạt Fill Rate từ 95% trở lên mà tồn kho bình quân không cao hơn cách đặt hàng hiện có.

## 3.3. Hai bộ dữ liệu

### 3.3.1. Vì sao dùng hai bộ dữ liệu

Đề tài không có số liệu xuất nhập tồn của một kho Việt Nam cụ thể. Các bộ dữ liệu công khai có số bán thật, như M5, lại thiếu những thông tin mà bài toán kho cần: không có tồn kho, không đánh dấu ngày hết hàng, không có nhà cung cấp, không có lịch khuyến mãi, tên hàng được ẩn danh, và không có các yếu tố riêng của Việt Nam như Tết âm lịch hay bão. Ngược lại, một bộ dữ liệu mô phỏng có thể chứa đủ các nghiệp vụ đó, nhưng quy luật của nó do chính người mô phỏng đặt ra, nên dễ làm mô hình trông tốt hơn thực tế.

Vì vậy hai bộ được dùng với vai trò khác nhau:

- **Bộ M5 (số bán thật)** là cơ sở chính để đánh giá **dự báo**: mô hình tốt đến đâu trên nhu cầu thật.
- **Bộ mô phỏng** dùng để xây dựng và minh họa **quy trình nghiệp vụ kho**: làm sạch dữ liệu có lỗi, nhận diện hết hàng, xử lý Tết và bão, hàng chỉ bán theo mùa, hạn sử dụng, gom đơn theo nhà cung cấp.
- Phần **tồn kho** được báo trên cả hai bộ, kể cả khi kết quả trên hai bộ khác nhau.

### 3.3.2. Bộ M5: số bán thật của Walmart

M5 là bộ dữ liệu của cuộc thi dự báo M5 (2020), gồm số bán theo ngày của khoảng 3.000 mã hàng tại 10 cửa hàng Walmart ở ba bang của Mỹ, kèm giá bán theo tuần và lịch sự kiện. [CẦN TRÍCH DẪN: Makridakis, Spiliotis, Assimakopoulos (2022), "M5 accuracy competition: Results, findings, and conclusions", International Journal of Forecasting.]

Để dùng cho bài toán kho tổng, bộ M5 được chuyển đổi như sau (`src/nguon/m5.py` và `src/nguon/m5_kho.py`, có kiểm thử tự động):

- **Cộng số bán của 10 cửa hàng** thành nhu cầu của một kho tổng phục vụ 10 cửa hàng. Số bán được **giữ nguyên**, không chỉnh sửa.
- **Chọn mẫu 121 mã hàng** ngẫu nhiên, phân tầng theo phòng ban (thực phẩm, gia dụng, hàng sở thích), hạt giống cố định, không nhìn vào số bán khi chọn. Số mã bằng bộ mô phỏng để hai bộ so được với nhau về quy mô.
- Giữ nguyên năm của dữ liệu (2011–2016), **không đặt tên hàng giả** cho các mã đã bị ẩn danh.

**Bảng 3.3. Quy mô bộ M5 sau chuyển đổi**

| Hạng mục | Giá trị |
|---|---|
| Số mã / nhóm hàng / nhà cung cấp | 121 / 7 / 7 |
| Thời gian | 29/01/2011 – 22/05/2016 (1.941 ngày) |
| Số dòng (mã × ngày) | 234.861 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 10.0. Mỗi phòng ban của M5 được coi là một nhà cung cấp (giả định).*

### 3.3.3. Bộ mô phỏng: nghiệp vụ kho hàng tiêu dùng tại Việt Nam

Bộ mô phỏng được sinh bằng chương trình Python với hạt giống cố định (`src/sinh_du_lieu.py`), chạy lại ra đúng bộ dữ liệu. Bộ dữ liệu đại diện cho kho tổng của một chuỗi siêu thị, bách hóa ở miền Bắc: 17 nhóm hàng lẫn lộn, đơn vị tính theo thùng, giao hàng cho các cửa hàng của chuỗi.

**Bảng 3.4. Quy mô bộ mô phỏng**

| Hạng mục | Giá trị |
|---|---|
| Số mã / nhóm hàng / nhà cung cấp | 121 / 17 / 14 |
| Thời gian | 01/10/2023 – 30/09/2026 (1.096 ngày), gồm 3 mùa Tết và 3 mùa Trung thu |
| Số dòng thô / sạch / đã sửa | 132.814 / 132.616 / 687 |
| Lead time của nhà cung cấp | 1 – 15 ngày |

*Nguồn: `reports/so_lieu_do_an.md`, mục 1; `docs/10`, mục 2.*

Các hiện tượng được đưa vào dữ liệu gồm:

- **Mùa vụ và chu kỳ:** bốn mùa miền Bắc, chu kỳ tuần, xu hướng năm riêng từng mã; hàng chỉ bán dịp lễ (mứt Tết, bánh trung thu) gần như không bán ngoài mùa.
- **Ngày lễ:** 11 dịp lễ, mỗi dịp có cửa sổ ảnh hưởng trước và sau (Tết bắt đầu từ 28 ngày trước, Trung thu 25 ngày, Noel 20 ngày). Tết và Trung thu theo âm lịch nên đổi ngày dương lịch mỗi năm.
- **Khuyến mãi và sale:** 1.338 đợt khuyến mãi theo mã; các đợt sale 11.11, 12.12, Black Friday.
- **Cú sốc:** bão lũ theo ba pha (mua tích trữ trước bão, cứu trợ sau bão, giao hàng chậm), nắng nóng, rét đậm, dịch bệnh, tin đồn tăng giá, sự kiện thể thao, đơn hàng lớn đột xuất, nhà cung cấp giao chậm.
- **Vận hành:** kho nghỉ Tết và lễ, hết hàng, và các lỗi nhập liệu được cài sẵn (dòng trùng, thiếu số xuất, số xuất bị nhập sai gấp 10 hoặc 100 lần) để kiểm thử quy trình làm sạch.

Giá bán của 37 mã được cập nhật theo giá bán lẻ tra công khai tại thời điểm làm đề tài (24/10/2026; nguồn từng mã ghi trong `data/reference/gia_thi_truong.csv`), vì một số giá mô phỏng ban đầu lệch xa giá thật. Giá vốn suy từ giá bán và biên lãi giả định của từng mã.

### 3.3.4. Phần nào là số thật, phần nào là giả định

Đây là điểm cần đọc kỹ trước khi đọc kết quả ở Chương 4. Bảng 3.5 tách rõ nguồn gốc của từng thành phần dữ liệu.

**Bảng 3.5. Nguồn gốc các thành phần dữ liệu**

| Thành phần | Bộ M5 | Bộ mô phỏng |
|---|---|---|
| Nhu cầu (số xuất kho) | **Thật**: tổng số bán 10 cửa hàng Walmart | Mô phỏng |
| Giá bán | **Thật**: giá Walmart theo tuần, trung bình theo mã, quy đổi 25.000 đ/USD (tỉ giá là giả định); không phải giá Việt Nam | 37 mã theo giá bán lẻ thật tại Việt Nam, còn lại mô phỏng |
| Giá vốn | Biên lãi gộp **đo từ dữ liệu thật Dominick's** (một chuỗi siêu thị khác ở Mỹ, 1989–1997) theo nhóm: thực phẩm 22,0%, gia dụng 16,6%, hàng khác 21,4% | Giả định theo mã |
| Lịch sự kiện | **Thật**: lịch sự kiện của M5 (lễ, thể thao, ngày phát tem phiếu thực phẩm) | Ngày lễ, ngày bão, lịch thi đấu thể thao là ngày **thật**; mức tác động là giả định |
| Khuyến mãi | **Suy từ giá thật**: tuần có giá trung bình toàn chuỗi ≤ 95% trung vị 8 tuần trước | Mô phỏng |
| Tồn kho, hàng nhập, hết hàng | Không có trong M5. Tồn kho được tạo bằng một quy tắc đặt hàng kinh nghiệm (giả định) để làm phương án "hiện trạng" | Mô phỏng theo chính sách đặt hàng (s, Q) dựa trên dự báo có sai lệch của người lập kế hoạch |
| Lead time, chi phí đặt, chi phí lưu kho | **Giả định**: lead time 7 ± 1,5 ngày, chi phí đặt 165.000 đ/lần, lưu kho 20%/năm, MOQ 1 | Giả định theo nhà cung cấp và theo mã |

*Nguồn: `docs/10`, mục 2 và 10.13; biên lãi Dominick's: `reports/dominicks.md`. Tài liệu của Dominick's yêu cầu ghi nguồn khi sử dụng. [CẦN TRÍCH DẪN: James M. Kilts Center for Marketing, University of Chicago Booth School of Business, Dominick's Dataset.]*

Vì nhu cầu của bộ mô phỏng được sinh ra từ chính các yếu tố mà mô hình được biết trước (lịch lễ, khuyến mãi, mùa vụ), mô hình trí tuệ nhân tạo trên bộ này có lợi thế mà trên số bán thật không có. Chương 4 cho thấy mức chênh này lớn đến đâu, và đó là lý do kết quả dự báo chính được báo trên bộ M5.

## 3.4. Đặc điểm của dữ liệu

### 3.4.1. Phân loại mã hàng theo ABC và XYZ

Phân loại ABC (theo giá trị xuất kho) và XYZ (theo độ biến động nhu cầu theo tháng, hệ số biến thiên) được tính **trên tập huấn luyện**, tức chỉ dùng dữ liệu trước giai đoạn kiểm tra, để việc phân nhóm không dùng thông tin tương lai.

**Bảng 3.6. Ma trận ABC × XYZ (số mã)**

| | Mô phỏng: X | Mô phỏng: Y | Mô phỏng: Z | M5: X | M5: Y | M5: Z |
|---|---:|---:|---:|---:|---:|---:|
| A | 20 | 3 | 5 | 27 | 14 | 0 |
| B | 19 | 6 | 15 | 26 | 8 | 0 |
| C | 32 | 1 | 20 | 31 | 14 | 1 |
| **Cộng** | **71** | **10** | **40** | **84** | **36** | **1** |

*Nguồn: `reports/so_lieu_do_an.md`, mục 1 và 10.0.*

Khác biệt lớn nhất giữa hai bộ nằm ở **nhóm Z**: bộ mô phỏng có 40 mã nhu cầu biến động mạnh theo mùa, bộ M5 chỉ có 1 mã. Điều này phản ánh đúng bản chất hai nguồn: danh mục kho Việt Nam được mô phỏng có nhiều hàng theo mùa và theo dịp lễ (bánh trung thu, mứt Tết, đồ trang trí Noel, đồ chơi Trung thu), còn mẫu 121 mã M5 chủ yếu là hàng bán quanh năm. Chương 4 cho thấy đặc điểm này quyết định phần lớn khác biệt về lợi ích của dự báo bằng trí tuệ nhân tạo giữa hai bộ.

### 3.4.2. Kiểu nhu cầu, chu kỳ tuần và khuyến mãi

**Bảng 3.7. Đặc điểm nhu cầu của hai bộ**

| Đặc điểm | Bộ mô phỏng | Bộ M5 |
|---|---|---|
| Xuất kho mỗi ngày mở cửa (toàn kho): trung bình / trung vị | 7.435 / 6.864 thùng | 1.146 / 1.124 đơn vị |
| Xuất mỗi mã mỗi ngày: trung vị | 28,0 | 3,0 |
| Tỉ lệ ngày-mã có xuất bằng 0 | 6,8% | 30,1% |
| Ngày kho nghỉ | 38 ngày | 5 ngày |
| Khuyến mãi: số đợt / số mã có | 1.338 / 121 | 157 / 67 (suy từ giá) |
| Kiểu nhu cầu (Syntetos–Boylan) | đều 58, thất thường 54, rời rạc và thất thường 9 | đều 92, rời rạc 17, thất thường 7, rời rạc và thất thường 5 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 1 ("Đặc điểm thêm") và 10.0. Với M5, các ngày trước khi một mã lên kệ được tính là ngày bán 0 nhưng không dùng để chấm điểm dự báo.*

**Bảng 3.8. Chu kỳ tuần (xuất trung bình theo thứ chia cho trung bình mọi ngày mở cửa)**

| Bộ | Thứ Hai | Thứ Ba | Thứ Tư | Thứ Năm | Thứ Sáu | Thứ Bảy | Chủ nhật |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mô phỏng | 1,02 | 1,05 | 1,04 | 1,07 | 1,15 | 1,16 | 0,53 |
| M5 | 0,96 | 0,89 | 0,87 | 0,87 | 0,98 | 1,23 | 1,20 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 1 và 10.0.*

Ba nhận xét rút ra từ hai bảng trên:

1. **Quy mô mỗi mã khác nhau nhiều.** Một mã M5 trung vị chỉ bán 3 đơn vị mỗi ngày cho cả 10 cửa hàng, gần một phần ba số ngày-mã không bán được đơn vị nào. Nhu cầu nhỏ và rời rạc làm sai số tương đối lớn hơn, và lượng đặt hàng tối ưu tính bằng số ngày bán dài hơn.
2. **Chu kỳ tuần ngược nhau.** Bộ mô phỏng thấp nhất vào Chủ nhật (0,53), được thiết kế theo kho tổng giao hàng cho cửa hàng ít vào ngày này; M5 cao nhất vào cuối tuần (Thứ Bảy 1,23, Chủ nhật 1,20) vì đó là số bán lẻ của cửa hàng. Đây là giới hạn của cách dựng kho tổng từ M5: lượng xuất kho được thay bằng tổng số bán của cửa hàng, nên không có độ trễ và cách gom chuyến giữa kho và cửa hàng. Mô hình dự báo học được chu kỳ tuần từ dữ liệu nên vẫn áp dụng được cho cả hai trường hợp.
3. **Khuyến mãi của M5 là ước lượng.** M5 không ghi lịch khuyến mãi; 157 đợt được suy ra từ những tuần giá giảm rõ so với mức thường, cùng quy tắc đã dùng với dữ liệu Dominick's. Ở Dominick's, nơi có cả giá và cờ khuyến mãi, 82,8% số mã-tuần khuyến mãi có cờ, phần còn lại chỉ nhận ra nhờ giá (`reports/dominicks.md`): giá là dấu hiệu khuyến mãi dùng được, nhưng quy tắc suy chưa được đối chiếu với lịch khuyến mãi thật của Walmart.

Hình 3.1 và Hình 3.2 minh họa chu kỳ tuần và ma trận ABC × XYZ của bộ mô phỏng (`reports/eda/h03_chu_ky_tuan.png`, `reports/eda/h06_ma_tran_abc_xyz.png`). Phân tích khám phá đầy đủ được trình bày ở Chương 4.

## 3.5. Tiền xử lý dữ liệu

### 3.5.1. Bộ mô phỏng: làm sạch theo đẳng thức tồn kho

Bản dữ liệu thô của bộ mô phỏng chứa các lỗi được cài sẵn, giống những lỗi thường gặp khi nhập liệu thủ công tại kho.

**Bảng 3.9. Lỗi trong bản thô và cách xử lý**

| Lỗi | Số lượng | Cách xử lý |
|---|---:|---|
| Dòng trùng hoàn toàn | 198 | Loại bỏ |
| Số xuất bị thiếu | 530 | Suy ra từ đẳng thức tồn kho |
| Số xuất bị nhập sai gấp 10 hoặc 100 lần | 157 | Suy ra từ đẳng thức tồn kho |

*Nguồn: `docs/10`, mục 3; `reports/bao_cao_lam_sach.md`.*

**Nguyên lý sửa lỗi:** với mỗi mã, mỗi ngày phải thỏa đẳng thức

> tồn cuối ngày = tồn đầu ngày + nhập trong ngày − xuất trong ngày.

Chỉ những dòng vi phạm đẳng thức mới bị sửa, bằng cách tính lại số xuất từ ba cột còn lại. Cách này khác với cách phổ biến là loại bỏ giá trị ngoại lai theo khoảng tứ phân vị (IQR): đột biến thật như mua tích trữ trước bão hay đợt sale vẫn khớp với tồn kho, nên không bị coi là lỗi, trong khi IQR dễ xóa nhầm chính các đỉnh nhu cầu này.

**Kết quả:** 687 dòng được sửa; đối chiếu với bản đáp án của bộ mô phỏng, không còn dòng nào sai; đủ 132.616 dòng; tồn kho không âm; không có xuất kho vào ngày kho nghỉ.

**Nhận diện hết hàng.** Ngày tồn cuối bằng 0 được đánh dấu là ngày hết hàng: 4.225 dòng (3,19%). Đối chiếu đáp án, cách đánh dấu bắt được đủ 4.050/4.050 ngày hết hàng thật, kèm 175 ngày tồn về 0 nhưng vẫn đủ hàng cho khách. Ở những ngày hết hàng, lượng xuất thấp hơn nhu cầu thật (nhu cầu bị che, *demand censoring*), nên các ngày này **không được dùng làm nhu cầu** khi huấn luyện và chấm điểm mô hình. Đánh dấu thừa 175 ngày là an toàn, vì chỉ làm bớt dữ liệu chứ không đưa số sai vào mô hình.

**Điều kiện áp dụng cho dữ liệu thật:** cách sửa dựa vào cột tồn cuối ngày đáng tin. Với dữ liệu thật, cần kiểm chéo thêm với chứng từ nhập xuất trước khi sửa.

### 3.5.2. Bộ M5: giữ nguyên số bán, ghi rõ giới hạn

Với M5, nguyên tắc là **không chỉnh số bán**. Các bước xử lý được cố định trước khi xem kết quả mô hình (`docs/10`, mục 9.8):

- **Ngày trước khi mã lên kệ** không được chấm điểm dự báo (số bán bằng 0 ở những ngày này không phải nhu cầu bằng 0).
- **Ngày kho nghỉ:** ngày có tổng số bán toàn chuỗi dưới 20% trung vị được coi là ngày đóng cửa; có 5 ngày như vậy.
- **Sự kiện:** lấy từ lịch của M5, cửa sổ ảnh hưởng từ 3 ngày trước đến 1 ngày sau sự kiện; ngày phát tem phiếu thực phẩm (SNAP) là thông tin biết trước.
- **Khuyến mãi:** suy từ giá như Bảng 3.5.

**Giới hạn không xử lý được:** M5 không có cờ hết hàng, nên những ngày cửa hàng thật sự hết hàng được ghi nhận như ngày nhu cầu thấp. Sai số dự báo và nhu cầu ở các ngày đó bị hiểu thấp hơn thực tế.

### 3.5.3. Chia dữ liệu theo thời gian

Ở cả hai bộ, dữ liệu được chia **theo thứ tự thời gian**, không chia ngẫu nhiên, vì trong thực tế mô hình chỉ có quá khứ để học:

- **Tập kiểm tra (test):** 12 tháng cuối của dữ liệu. Chỉ dùng để báo cáo kết quả cuối cùng, không dùng để chọn mô hình hay tham số.
- **Tập kiểm định (validation2):** 12 tháng ngay trước tập kiểm tra, cùng mùa vụ với tập kiểm tra. Mọi lựa chọn (mô hình, trọng số kết hợp, quy tắc lượng đặt) đều đưa ra trên tập này, theo luật được ghi lại trước khi chạy.
- **Tập huấn luyện:** toàn bộ phần trước đó.

Cách chia được tính tự động từ ngày cuối của dữ liệu, nên áp dụng được cho bất kỳ bộ dữ liệu nào có cùng cấu trúc. Cách dự báo lặp lại tại nhiều mốc trong mỗi tập (backtest cuốn chiếu) được trình bày ở Chương 4.

## 3.6. Giới hạn của dữ liệu

1. **Không có số liệu của một kho Việt Nam cụ thể.** Bộ M5 là số bán thật nhưng của Mỹ, giai đoạn 2011–2016, quy mô 10 cửa hàng; bộ mô phỏng có bối cảnh Việt Nam nhưng không phải số thật. Kết quả của đề tài là kết quả của **quy trình** trên hai bộ dữ liệu này, không phải hiệu quả dự kiến của một kho cụ thể.
2. **Kho tổng dựng từ M5 là xấp xỉ.** Lượng xuất kho được thay bằng tổng số bán của cửa hàng; tồn kho, lead time, chi phí và nhà cung cấp đều là giả định.
3. **Nhu cầu bị che ở M5 không tách được** do không có cờ hết hàng.
4. **Bộ mô phỏng có lợi thế cho mô hình.** Nhu cầu được sinh từ chính các yếu tố mô hình biết trước, nên kết quả dự báo trên bộ này lạc quan hơn trên số thật.
5. **Các giả định chi phí ảnh hưởng tới kết quả tồn kho.** Chương 4 có phần thử độ nhạy theo chi phí đặt hàng, thời gian giao hàng và chi phí lưu kho để kiểm tra mức ảnh hưởng.

Quy trình được thiết kế để thay bằng dữ liệu thật của một kho khi có: chỉ cần giữ nguyên cấu trúc cột (ngày, mã hàng, số nhập, số xuất, tồn cuối ngày) và bổ sung danh mục mã hàng, nhà cung cấp; mọi bước từ làm sạch đến mô phỏng tồn kho chạy lại không phải sửa chương trình.
