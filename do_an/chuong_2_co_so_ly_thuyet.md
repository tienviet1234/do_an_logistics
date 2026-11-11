# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

> **Ghi chú cho người viết (xóa trước khi nộp)**
> - Bản nháp lần 1, soạn ngày 10/11/2026 từ Báo cáo Giai đoạn 1 (`docs/Bao_cao_Giai_doan_1_Kien_thuc_can_chuan_bi.docx`), đã sửa theo bảng "điểm khác" trong `docs/08` (WMAPE thay MAPE, chu kỳ 7 và 365 thay 30, cửa sổ Tết 28 ngày, làm sạch theo đẳng thức kho, backtest cuốn chiếu).
> - Công thức trong chương này là công thức **hệ thống thực sự dùng** (`src/ton_kho.py`, `src/danh_gia.py`, `src/dac_trung.py`), để Chương 4 không mâu thuẫn với Chương 2.
> - Tài liệu tham khảo ghi theo tác giả – năm. Danh mục cuối chương là các công trình gốc có thật nhưng **phải tự mở bản gốc kiểm tra lại năm, tạp chí, số trang** trước khi nộp, và trình bày theo mẫu trích dẫn của trường. Chỗ **[CẦN TRÍCH DẪN: ...]** là nhận định chưa có nguồn.

Chương này trình bày cơ sở lý thuyết cho hai bước của bài toán đã nêu ở Chương 1: quản lý tồn kho và dự báo nhu cầu. Phần cuối chương trình bày cách đánh giá dự báo và tổng quan các nghiên cứu liên quan, từ đó xác định cách tiếp cận của đề tài.

## 2.1. Quản lý tồn kho

### 2.1.1. Tồn kho và các loại chi phí

Tồn kho là lượng hàng hóa doanh nghiệp giữ lại để đáp ứng nhu cầu trong tương lai. Tồn kho giúp kho phục vụ ngay khi có nhu cầu, tách nhịp nhập hàng với nhịp xuất hàng và hấp thụ những biến động không lường trước, nhưng đồng thời giữ vốn và phát sinh chi phí (Silver, Pyke và Thomas, 2017).

Các quyết định tồn kho cân bằng ba nhóm chi phí:

- **Chi phí đặt hàng (S):** phát sinh mỗi lần đặt hàng và gần như không phụ thuộc số lượng: lập đơn, xử lý chứng từ, nhận hàng, kiểm hàng, vận chuyển cố định mỗi chuyến.
- **Chi phí lưu kho (H):** tỉ lệ thuận với lượng hàng và thời gian giữ hàng: chi phí vốn, kho bãi, bảo hiểm, hao hụt, hư hỏng, lỗi thời. Thường được biểu diễn bằng một tỉ lệ *h* trên giá vốn mỗi năm, tức H = h × giá vốn.
- **Chi phí thiếu hàng:** phát sinh khi có nhu cầu mà không có hàng. Trong bán lẻ, khách thường không chờ mà mua chỗ khác hoặc mua mặt hàng khác, nên phần mất đi là doanh thu của lần bán đó (trường hợp *mất bán*, lost sales), khác với trường hợp khách chịu chờ hàng về (*nợ đơn*, backorder).

Đề tài đo chi phí thiếu hàng bằng **lợi nhuận mất**, tức số hàng không bán được nhân với (giá bán − giá vốn). Cách đo này lấy được trực tiếp từ dữ liệu giá, không cần giả định thêm một hệ số phạt khó kiểm chứng. Tổng ba khoản được gọi là **chi phí liên quan**:

> Chi phí liên quan = chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do thiếu hàng.

### 2.1.2. Lượng đặt hàng kinh tế (EOQ)

Mô hình lượng đặt hàng kinh tế (Economic Order Quantity, EOQ) tìm lượng đặt mỗi lần Q sao cho tổng chi phí đặt hàng và lưu kho trong năm nhỏ nhất (Harris, 1913). Với nhu cầu năm D, chi phí mỗi lần đặt S và chi phí lưu kho mỗi đơn vị mỗi năm H:

> Tổng chi phí(Q) = (D / Q) × S + (Q / 2) × H

Số lần đặt D/Q giảm khi Q tăng, còn tồn kho bình quân Q/2 tăng theo Q. Lấy đạo hàm và cho bằng 0:

> EOQ = √(2DS / H)

Mô hình giả định nhu cầu đều và biết trước, hàng về đúng hạn, không có chiết khấu theo số lượng. Các giả định này không đúng hoàn toàn với kho hàng tiêu dùng, nhưng EOQ vẫn là điểm xuất phát tốt vì đường tổng chi phí khá phẳng quanh điểm tối ưu: đặt lệch EOQ một khoảng vừa phải chỉ làm chi phí tăng ít (Silver, Pyke và Thomas, 2017). Khi nhà cung cấp có lượng đặt tối thiểu (MOQ), lượng đặt thực tế là max(EOQ, MOQ).

### 2.1.3. Nhu cầu không chắc chắn: tồn kho an toàn và điểm đặt hàng lại

Trong thực tế, nhu cầu trong thời gian chờ hàng (lead time, L) không biết trước. Nếu kho chỉ đặt hàng khi tồn vừa đủ cho nhu cầu *trung bình* trong L ngày, thì khoảng một nửa số lần nhu cầu thực sẽ vượt mức đó và kho hết hàng. **Tồn kho an toàn** (Safety Stock, SS) là phần giữ thêm để hấp thụ biến động này.

**Điểm đặt hàng lại** (Reorder Point, ROP) là mức tồn kho mà khi chạm tới thì phải đặt hàng:

> ROP = nhu cầu dự kiến trong L ngày + SS

Việc so sánh với ROP dùng **vị thế tồn kho** (inventory position, IP) = tồn thực có + hàng đã đặt đang trên đường về, để không đặt trùng khi hàng của lần trước chưa về.

**Công thức tồn kho an toàn.** Công thức quen thuộc trong giáo trình là:

> SS = z × σd × √L

trong đó σd là độ lệch chuẩn của nhu cầu ngày và z là hệ số của phân phối chuẩn ứng với mức phục vụ mong muốn (z = 1,28 với 90%; 1,645 với 95%; 2,33 với 99%). Công thức này có hai hạn chế khi áp dụng cùng một mô hình dự báo:

1. Khi đã có dự báo, phần không chắc chắn là **sai số dự báo**, không phải toàn bộ biến động của nhu cầu. Một mã có nhu cầu dao động mạnh nhưng theo quy luật (ví dụ tăng đều trước Tết) có thể dự báo khá đúng, nên không cần giữ dự phòng theo toàn bộ độ dao động đó. Vì vậy σ nên được đo từ sai số dự báo trong quá khứ (Silver, Pyke và Thomas, 2017; Báo cáo Giai đoạn 1 cũng khuyến nghị điều này).
2. √L chỉ đúng khi sai số các ngày độc lập với nhau. Sai số dự báo thực tế thường cùng chiều qua nhiều ngày liền (đã dự báo thấp thì thấp cả tuần), nên tổng sai số trong L ngày lớn hơn σd × √L.

Đề tài vì thế đo trực tiếp **độ lệch chuẩn của tổng sai số dự báo trong L ngày** (σ_LTD) trên tập kiểm định, cho từng mã, và cộng thêm phần biến động của chính lead time (độ lệch chuẩn σ_L):

> SS = z × √(σ_LTD² + d² × σ_L²)

với d là nhu cầu dự báo bình quân mỗi ngày. Số hạng thứ hai là phần dự phòng cho trường hợp nhà cung cấp giao trễ hơn trung bình (Silver, Pyke và Thomas, 2017).

**Mức phục vụ chu kỳ và Fill Rate.** Mức phục vụ dùng để chọn z ở trên là **mức phục vụ chu kỳ** (Cycle Service Level, CSL): xác suất không hết hàng trong một chu kỳ đặt hàng. Chỉ số kho quan tâm thực tế lại thường là **Fill Rate**: tỉ lệ nhu cầu được đáp ứng ngay từ kho. Hai chỉ số khác nhau: một chu kỳ có hết hàng vẫn có thể đáp ứng được phần lớn nhu cầu của chu kỳ đó, nên khi sai số được ước lượng đúng, Fill Rate thường cao hơn CSL; khi sai số bị ước lượng thấp (ví dụ với hàng mùa vụ), Fill Rate có thể thấp hơn mục tiêu (Axsäter, 2015). Đề tài đặt mục tiêu theo CSL và báo kết quả bằng Fill Rate.

### 2.1.4. Chính sách đặt hàng

Hai họ chính sách cơ bản (Silver, Pyke và Thomas, 2017; Axsäter, 2015):

- **Rà soát liên tục (s, Q):** theo dõi tồn kho mỗi ngày; khi IP giảm tới điểm s (= ROP) thì đặt một lượng cố định Q (thường là EOQ). Phù hợp với hàng bán quanh năm, nhu cầu tương đối ổn định.
- **Rà soát định kỳ (R, S), "đặt đến mức":** cứ mỗi R ngày kiểm tra một lần và đặt đủ để IP lên tới mức S, với S bằng nhu cầu dự kiến trong (L + R) ngày cộng tồn kho an toàn. Lượng đặt thay đổi theo dự báo, nên phù hợp với hàng có nhu cầu thay đổi mạnh theo mùa: Q cố định tính từ nhu cầu bình quân năm sẽ quá lớn lúc trái mùa và quá nhỏ lúc vào mùa.

Đề tài dùng chung một khung kiểm tra mỗi ngày kho mở cửa (IP ≤ ROP thì đặt), và cho chọn trên tập kiểm định giữa ba quy tắc lượng đặt: theo EOQ, đặt đến mức, hoặc **lai** (EOQ cho nhóm nhu cầu ổn định X, Y; đặt đến mức cho nhóm biến động Z). Mọi tham số đều tính lại theo dự báo mới nhất, nên ROP và SS thay đổi theo thời gian chứ không cố định cả năm.

### 2.1.5. Phân loại mã hàng

**Phân tích ABC** dựa trên nguyên lý Pareto: một số ít mã hàng chiếm phần lớn giá trị. Các mã được xếp giảm dần theo giá trị xuất kho; nhóm A gồm các mã chiếm tới 75% giá trị tích lũy, nhóm B tới 92%, phần còn lại là nhóm C. Nhóm A cần được kiểm soát chặt nhất.

**Phân tích XYZ** phân loại theo độ ổn định của nhu cầu, đo bằng hệ số biến thiên (CV = độ lệch chuẩn / trung bình) của nhu cầu theo tháng: X (CV ≤ 0,5) nhu cầu ổn định, Y (0,5 < CV ≤ 1,0) dao động vừa, Z (CV > 1,0) biến động mạnh, thường là hàng mùa vụ. Ghép hai phân loại thành ma trận ABC × XYZ giúp chọn cách quản lý cho từng ô: A-X có thể tự động hóa, A-Z cần dự báo kỹ và theo dõi sát.

**Phân loại kiểu nhu cầu theo Syntetos và Boylan (2005)** dùng hai đại lượng: khoảng cách trung bình giữa hai lần có nhu cầu (ADI) và bình phương hệ số biến thiên của lượng nhu cầu khi có phát sinh (CV²). Với ngưỡng ADI = 1,32 và CV² = 0,49, nhu cầu được chia thành bốn kiểu: **đều** (smooth), **thất thường** (erratic, lượng dao động mạnh), **rời rạc** (intermittent, nhiều ngày bằng 0) và **rời rạc và thất thường** (lumpy). Kiểu nhu cầu gợi ý phương pháp dự báo phù hợp: nhu cầu rời rạc cần các phương pháp riêng như Croston hay TSB (mục 2.2.2).

### 2.1.6. Mô hình người bán báo (newsvendor) cho hàng một mùa

Với hàng chỉ bán trong một dịp ngắn (bánh trung thu, mứt Tết, đồ trang trí Noel), kho chỉ có một hoặc vài lần đặt hàng, hàng thừa sau dịp phải bán giảm giá hoặc trả lại. Khi đó bài toán không còn là "đặt khi nào" mà là "đặt bao nhiêu cho cả mùa". Mô hình newsvendor chọn lượng đặt Q* sao cho xác suất nhu cầu không vượt Q* bằng **tỉ số tới hạn** (Arrow, Harris và Marschak, 1951; Silver, Pyke và Thomas, 2017):

> P(nhu cầu ≤ Q*) = Cu / (Cu + Co)

trong đó Cu là thiệt hại mỗi đơn vị thiếu (lợi nhuận mất) và Co là thiệt hại mỗi đơn vị thừa (giá vốn trừ giá trị thu hồi). Hàng lãi cao, thừa ít thiệt thì nên đặt dư; hàng lãi thấp, thừa phải xả lỗ thì nên đặt sát.

### 2.1.7. Chỉ số đánh giá hiệu quả tồn kho

| Chỉ số | Cách tính | Ý nghĩa |
|---|---|---|
| Fill Rate | Lượng đáp ứng ngay / tổng nhu cầu | Mức phục vụ thực tế đối với cửa hàng |
| Số ngày-mã thiếu hàng | Số cặp (mã, ngày) có nhu cầu mà không đủ hàng | Tần suất hết hàng |
| Tồn kho bình quân | Trung bình giá trị tồn cuối ngày | Vốn bị giữ trong kho |
| Vòng quay tồn kho (ITR) | Giá vốn hàng xuất / tồn kho bình quân | Tồn kho quay vòng bao nhiêu lần một năm |
| Số ngày tồn (DOH) | 365 / ITR | Tồn hiện có đủ bán bao nhiêu ngày |
| Chi phí liên quan | Đặt hàng + lưu kho + lợi nhuận mất | Hàm mục tiêu của đề tài (mục 2.1.1) |

## 2.2. Dự báo nhu cầu

### 2.2.1. Chuỗi thời gian nhu cầu và các yếu tố tác động

Nhu cầu theo ngày của một mã hàng là một chuỗi thời gian, thường gồm các thành phần: **xu hướng** (tăng giảm dài hạn), **mùa vụ** (lặp lại theo chu kỳ cố định: tuần, năm), **ảnh hưởng của sự kiện** (ngày lễ, khuyến mãi) và **phần ngẫu nhiên** (Hyndman và Athanasopoulos, 2021). Với dữ liệu theo ngày, hai chu kỳ có ý nghĩa là 7 ngày (thói quen mua sắm trong tuần) và 365 ngày (mùa trong năm); không có chu kỳ 30 ngày rõ ràng.

Tại Việt Nam có thêm một khó khăn: Tết Nguyên đán và Tết Trung thu tính theo âm lịch nên rơi vào ngày dương lịch khác nhau mỗi năm. Mô hình chỉ dựa vào chu kỳ 365 ngày sẽ đặt đỉnh Tết sai chỗ; cần đưa lịch các dịp này vào mô hình dưới dạng biến sự kiện, kèm **cửa sổ ảnh hưởng**: sức mua Tết bắt đầu tăng khoảng bốn tuần trước Tết, không chỉ vài ngày.

Để dự báo dùng được trong thực tế, cần phân biệt hai loại yếu tố:

- **Yếu tố biết trước** tại thời điểm dự báo: thứ trong tuần, ngày lễ, Tết, lịch khuyến mãi đã lên, lịch sale của sàn thương mại điện tử. Được phép đưa vào mô hình.
- **Yếu tố không biết trước:** bão lũ, dịch bệnh, đơn hàng đột xuất. Có thể giải thích nhu cầu sau khi đã xảy ra, nhưng nếu đưa vào mô hình như một biến đầu vào thì kết quả kiểm tra sẽ đẹp giả tạo, vì khi dự báo thật không có thông tin này (rò rỉ thông tin tương lai, mục 2.3.2).

**Nhu cầu bị che (demand censoring).** Số liệu ghi nhận được là lượng *bán* hoặc *xuất*, không phải nhu cầu. Ở những ngày hết hàng, lượng bán bằng lượng còn trong kho, thấp hơn nhu cầu thật. Nếu dùng nguyên số này để học, mô hình sẽ dự báo thấp, dẫn đến đặt ít và lại hết hàng: một vòng luẩn quẩn. Cách xử lý đơn giản và an toàn là đánh dấu các ngày hết hàng và **không dùng chúng** làm nhu cầu khi huấn luyện và chấm điểm (Nahmias, 1994).

### 2.2.2. Các phương pháp mốc (thống kê truyền thống)

Các phương pháp đơn giản được dùng làm **mốc so sánh**: một mô hình phức tạp chỉ có giá trị khi tốt hơn rõ rệt các phương pháp này.

- **Naive:** dự báo bằng giá trị gần nhất. **Seasonal Naive** (chu kỳ 7): dự báo mỗi ngày bằng giá trị cùng thứ tuần trước. Đây là mốc tối thiểu mà mọi mô hình phải vượt.
- **Trung bình trượt** (moving average): trung bình n ngày gần nhất, dự báo phẳng cho cả tầm. Đơn giản, ổn định, phản ứng chậm với thay đổi.
- **San bằng mũ và ETS:** trung bình có trọng số giảm dần theo thời gian; họ ETS (Error, Trend, Seasonal) mở rộng thêm thành phần xu hướng và mùa vụ, chọn dạng mô hình theo tiêu chí thông tin (Hyndman và Athanasopoulos, 2021).
- **ARIMA(p, d, q):** mô hình tự hồi quy (p bậc), lấy sai phân d lần để chuỗi dừng, trung bình trượt của sai số (q bậc); SARIMA thêm thành phần mùa vụ (Box và Jenkins, 1970).
- **Croston và SBA:** dành cho nhu cầu rời rạc. Croston (1972) tách chuỗi thành hai phần, lượng nhu cầu khi có phát sinh và khoảng cách giữa hai lần phát sinh, san bằng mũ từng phần rồi lấy tỉ số. Syntetos và Boylan (2005) chỉ ra phương pháp này bị lệch và đề xuất hệ số hiệu chỉnh (SBA).
- **TSB** (Teunter, Syntetos và Babai, 2011): san bằng mũ **xác suất có nhu cầu** thay vì khoảng cách, nên cập nhật được cả khi mã ngừng bán, phù hợp với hàng sắp lỗi thời hoặc hết mùa.

### 2.2.3. Prophet

Prophet (Taylor và Letham, 2018) mô hình hóa chuỗi thời gian dưới dạng tổng các thành phần:

> y(t) = xu hướng(t) + mùa vụ(t) + ngày lễ(t) + tác động của biến thêm(t) + sai số

Mùa vụ tuần và năm được biểu diễn bằng chuỗi Fourier; ngày lễ được khai báo bằng một bảng gồm tên dịp, ngày diễn ra và cửa sổ trước–sau, nên đưa được Tết âm lịch với cửa sổ dài vào mô hình một cách trực tiếp; biến thêm (regressor) dùng cho các yếu tố biết trước như khuyến mãi. Mô hình có dạng cộng (additive) hoặc nhân (multiplicative) theo xu hướng. Ưu điểm lớn của Prophet là **dễ giải thích**: dự báo của mỗi ngày tách được thành từng thành phần có ý nghĩa. Hạn chế là mỗi mã hàng học một mô hình riêng, không học được kinh nghiệm chung giữa các mã.

### 2.2.4. Học máy: cây quyết định tăng cường (LightGBM)

**Cây quyết định tăng cường theo gradient** (gradient boosting) xây dựng lần lượt nhiều cây quyết định nhỏ, mỗi cây sau học phần sai số còn lại của các cây trước (Friedman, 2001). LightGBM (Ke và cộng sự, 2017) là một cách cài đặt nhanh của phương pháp này, chia nhánh theo lá và gom giá trị thành các khoảng, xử lý được hàng trăm nghìn dòng dữ liệu trong vài phút. Trong cuộc thi dự báo M5, các mô hình dạng này chiếm ưu thế ở nhóm đứng đầu (Makridakis, Spiliotis và Assimakopoulos, 2022).

Khi áp dụng cho dự báo nhu cầu, mô hình học máy không tự hiểu thứ tự thời gian; mọi thông tin phải được đưa vào dưới dạng **đặc trưng** (cột đầu vào):

- **Đặc trưng lịch biết trước:** thứ trong tuần, ngày trong tháng, tháng, số ngày đến/sau từng dịp lễ, khuyến mãi, sale.
- **Giá trị trễ (lag) và thống kê trượt** của nhu cầu quá khứ: bán cùng thứ tuần trước, trung bình 28 ngày, cùng kỳ năm trước. Điều kiện bắt buộc: chỉ dùng số liệu đã có tại thời điểm dự báo. Với tầm dự báo h ngày, giá trị trễ phải cách ít nhất h ngày, hoặc dùng cách **dự báo trực tiếp theo tầm**: mỗi nhóm tầm (1–7, 8–14, 15–28 ngày) một mô hình riêng, mỗi mô hình chỉ dùng giá trị trễ không ngắn hơn tầm của nó.
- **Đặc điểm mã hàng:** nhóm hàng, nhóm ABC/XYZ, giá.

Một mô hình chung (global model) được học trên **tất cả** các mã cùng lúc, nhờ đó mã ít dữ liệu học được quy luật từ các mã tương tự.

**Hàm mất mát Tweedie.** Nhu cầu theo ngày không âm, nhiều số 0 và lệch phải. Hàm mất mát bình phương (L2) giả định sai số đối xứng nên không hợp với dữ liệu này. Phân phối Tweedie với tham số lũy thừa 1 < p < 2 là phân phối hỗn hợp Poisson–Gamma, có khối xác suất tại 0 và đuôi dài, phù hợp với nhu cầu bán lẻ (Jørgensen, 1987). Mô hình Tweedie dùng hàm liên kết logarit: dự báo = exp(tổng đóng góp của các cây), nên đóng góp của từng yếu tố trở thành **hệ số nhân** lên một mức nền. Tính chất này được dùng để giải thích dự báo ở mục 2.2.7.

### 2.2.5. Học sâu

**Mạng nơ-ron hồi quy** (Recurrent Neural Network, RNN) xử lý chuỗi theo từng bước thời gian, mang theo một trạng thái ẩn tóm tắt quá khứ. RNN đơn giản khó học các phụ thuộc xa do gradient bị triệt tiêu; **LSTM** (Long Short-Term Memory) thêm các cổng điều khiển việc ghi nhớ và quên để khắc phục (Hochreiter và Schmidhuber, 1997).

Gần đây có thêm các kiến trúc thiết kế riêng cho dự báo nhiều bước:

- **N-HiTS** (Challu và cộng sự, 2023): ghép nhiều khối mạng, mỗi khối học chuỗi ở một độ phân giải thời gian khác nhau.
- **TiDE** (Das và cộng sự, 2023): mạng nhiều lớp mã hóa – giải mã, tốc độ nhanh, nhận được biến biết trước cho các ngày tương lai.
- **TFT** (Temporal Fusion Transformer; Lim và cộng sự, 2021): dùng cơ chế chú ý (attention) để chọn biến và đoạn thời gian quan trọng.

Học sâu cần nhiều dữ liệu và nhiều tài nguyên tính toán, khó giải thích hơn, và với chuỗi bán lẻ theo ngày không phải lúc nào cũng tốt hơn cây tăng cường (Makridakis, Spiliotis và Assimakopoulos, 2022). Vì vậy đề tài đưa các mô hình học sâu vào cùng một khung đánh giá và chỉ dùng khi chúng thắng trên tập kiểm định.

### 2.2.6. Kết hợp dự báo

Lấy trung bình có trọng số của dự báo từ nhiều mô hình khác nhau thường cho sai số thấp hơn từng mô hình riêng lẻ, vì sai số của các mô hình khác bản chất bù trừ nhau một phần (Bates và Granger, 1969; Makridakis, Spiliotis và Assimakopoulos, 2020). Kết quả này lặp lại ở nhiều cuộc thi dự báo. Trọng số kết hợp phải được chọn trên dữ liệu không dùng để báo cáo kết quả (tập kiểm định), và có thể khác nhau giữa các nhóm mã: một mô hình tốt cho hàng ổn định chưa chắc tốt cho hàng mùa vụ.

### 2.2.7. Giải thích dự báo

Người lập kế hoạch cần biết **vì sao** mô hình đưa ra một con số trước khi tin nó. Hai cách giải thích được dùng:

- **Phân rã thành phần** (Prophet): dự báo bằng tổng xu hướng, mùa tuần, mùa năm, ngày lễ, khuyến mãi.
- **Đóng góp của từng đặc trưng** cho mô hình cây: phương pháp SHAP chia giá trị dự báo của một dòng thành mức nền cộng đóng góp của từng đặc trưng, tổng các phần bằng đúng dự báo (Lundberg và Lee, 2017); với mô hình cây có thuật toán tính chính xác (TreeSHAP; Lundberg và cộng sự, 2020). Với mô hình Tweedie (liên kết logarit), đóng góp cộng trên thang logarit trở thành hệ số nhân: dự báo = mức nền × hệ số nhóm yếu tố 1 × hệ số nhóm yếu tố 2 × …

## 2.3. Đánh giá dự báo

### 2.3.1. Chỉ số sai số

Với A là giá trị thực, F là dự báo, n là số điểm chấm:

| Chỉ số | Công thức | Nhận xét |
|---|---|---|
| MAE | (1/n) Σ \|A − F\| | Dễ hiểu, cùng đơn vị với nhu cầu; không so được giữa các mã khác quy mô |
| RMSE | √[(1/n) Σ (A − F)²] | Phạt nặng sai số lớn |
| MAPE | (1/n) Σ \|A − F\| / A | Theo phần trăm, nhưng **không xác định khi A = 0** và rất lớn khi A gần 0; không dùng được cho nhu cầu theo ngày có nhiều ngày bằng 0 |
| **WMAPE** | Σ \|A − F\| / Σ A | Sai số tuyệt đối chia tổng nhu cầu; không bị hỏng khi có ngày bằng 0, mã bán nhiều có trọng số lớn hơn. **Chỉ số chính của đề tài** |
| MASE | MAE của mô hình / MAE của Seasonal Naive trên tập huấn luyện | Dưới 1 nghĩa là tốt hơn mốc (Hyndman và Koehler, 2006) |
| Bias | (1/n) Σ (A − F) | Dương: dự báo thấp hơn thực tế, dễ hết hàng; âm: dự báo thừa, tồn kho cao |

Một chỉ số sai số trung bình không cho biết dự báo lệch về phía nào, nên luôn báo kèm Bias. WMAPE được tính cả theo **ngày** và theo **tuần** (cộng nhu cầu và dự báo theo tuần trước khi tính): quyết định đặt hàng phụ thuộc tổng nhu cầu trong thời gian chờ hàng, nên sai số theo tuần gần với tác động thực tế hơn.

Mức cải thiện so với một phương pháp mốc được gọi là **giá trị gia tăng của dự báo** (Forecast Value Added, FVA): một bước trong quy trình dự báo chỉ đáng giữ nếu làm sai số giảm so với bước đơn giản hơn (Gilliland, 2010).

### 2.3.2. Kiểm định theo thời gian và rò rỉ thông tin

Với chuỗi thời gian, không được chia dữ liệu ngẫu nhiên như các bài toán học máy thông thường, vì mô hình sẽ được học từ những ngày nằm sau ngày cần dự báo. Cách đánh giá đúng là **kiểm định cuốn chiếu** (rolling origin, backtest; Tashman, 2000): chọn nhiều **mốc** dự báo; tại mỗi mốc, mô hình chỉ được học từ dữ liệu đến mốc đó và dự báo cho tầm phía sau; sau đó dời mốc về phía trước và lặp lại. Sai số được tính trên tất cả các mốc, nên kết quả ổn định hơn một lần chia duy nhất.

Dữ liệu được chia thành ba phần theo thời gian:

- **Tập huấn luyện:** để mô hình học.
- **Tập kiểm định:** để chọn mô hình, tham số, trọng số kết hợp, quy tắc tồn kho.
- **Tập kiểm tra:** chỉ dùng **một lần** để báo cáo kết quả cuối cùng. Nếu nhìn kết quả trên tập kiểm tra rồi quay lại chỉnh mô hình, tập kiểm tra trở thành một tập kiểm định thứ hai và con số báo cáo sẽ lạc quan hơn thực tế.

**Rò rỉ thông tin tương lai** (data leakage) xảy ra khi mô hình, trong lúc kiểm tra, dùng một thông tin mà khi dự báo thật sẽ không có: ví dụ giá trị trễ ngắn hơn tầm dự báo, biến bão lũ của chính ngày cần dự báo, hay phân nhóm ABC tính trên cả giai đoạn kiểm tra. Đề tài ghi các luật chọn **trước khi chạy** và kiểm tra tự động rằng mô hình không nhìn thấy dữ liệu sau mốc.

### 2.3.3. Khoảng dự báo

Một con số dự báo đơn lẻ không cho biết độ tin cậy. **Khoảng dự báo** 80% hoặc 95% cho biết khoảng mà nhu cầu thực có khả năng rơi vào. Thay vì giả định sai số theo phân phối chuẩn, có thể lấy **phân vị thực nghiệm** của sai số dự báo đã quan sát trong quá khứ, cho từng nhóm mã và từng tầm dự báo (Hyndman và Athanasopoulos, 2021). Khoảng dự báo tốt là khoảng mà tỉ lệ thực tế rơi vào gần với mức danh nghĩa.

### 2.3.4. Tín hiệu theo dõi

Mô hình đang tốt có thể trở nên kém khi thị trường thay đổi. **Tín hiệu theo dõi** (tracking signal) = tổng sai số tích lũy / độ lệch tuyệt đối trung bình (MAD). Khi giá trị tuyệt đối vượt một ngưỡng (thường 4 đến 6), dự báo được coi là đang lệch có hệ thống và cần xem lại (Brown, 1959; Silver, Pyke và Thomas, 2017).

## 2.4. Tổng quan nghiên cứu liên quan

**Mô hình học máy so với phương pháp thống kê.** Các cuộc thi dự báo quy mô lớn cho thấy câu trả lời phụ thuộc dữ liệu. Ở cuộc thi M4 (100.000 chuỗi đa lĩnh vực), các phương pháp kết hợp và lai thống kê – học máy đứng đầu, còn các mô hình học máy thuần túy thường kém phương pháp thống kê đơn giản (Makridakis, Spiliotis và Assimakopoulos, 2020). Ở cuộc thi M5 (số bán Walmart theo ngày, nhiều mã có liên quan với nhau), các mô hình LightGBM học chung trên nhiều chuỗi chiếm ưu thế (Makridakis, Spiliotis và Assimakopoulos, 2022). Nghĩa là học máy có lợi thế khi có nhiều chuỗi liên quan và nhiều thông tin bổ trợ (lịch, giá, sự kiện), đúng là tình huống của một kho hàng tiêu dùng.

**Từ dự báo đến quyết định tồn kho.** Phần lớn nghiên cứu dự báo đánh giá bằng chỉ số sai số, nhưng sai số thấp hơn chưa chắc dẫn đến tồn kho tốt hơn: tác động lên tồn kho phụ thuộc lượng đặt, thời gian chờ hàng, cách tính tồn kho an toàn và đặc điểm từng nhóm hàng. Một số nghiên cứu đề xuất đánh giá dự báo bằng kết quả tồn kho thay vì chỉ bằng sai số (Syntetos, Boylan và Disney, 2009). [CẦN TRÍCH DẪN: 1–2 nghiên cứu áp dụng mô hình học máy dự báo nhu cầu kết hợp tính tồn kho an toàn, điểm đặt hàng lại cho bán lẻ hoặc kho phân phối, ưu tiên nghiên cứu tại Việt Nam nếu có.]

**Khoảng trống mà đề tài hướng tới.** Từ tổng quan trên, đề tài không đặt mục tiêu chứng minh "trí tuệ nhân tạo luôn tốt hơn", mà xây dựng một quy trình đi trọn từ dữ liệu đến quyết định đặt hàng, đánh giá công bằng (cùng khung kiểm định, luật chọn ghi trước, tập kiểm tra dùng một lần) và đo lợi ích bằng chỉ số tồn kho, trên cả số bán thật lẫn dữ liệu mô phỏng nghiệp vụ Việt Nam, để chỉ ra **trí tuệ nhân tạo có giá trị ở nhóm hàng nào**.

## 2.5. Tóm tắt chương và khung lý thuyết của đề tài

| Vấn đề của bài toán | Cơ sở lý thuyết | Áp dụng ở Chương 4 |
|---|---|---|
| Dữ liệu có lỗi nhập liệu | Đẳng thức tồn kho | Làm sạch, không xóa đỉnh nhu cầu thật |
| Ngày hết hàng che nhu cầu thật | Nhu cầu bị che (2.2.1) | Bỏ ngày hết hàng khi học và chấm điểm |
| Mã hàng khác nhau về giá trị và độ ổn định | ABC, XYZ, Syntetos–Boylan (2.1.5) | Phân nhóm trên tập huấn luyện, báo kết quả theo nhóm |
| Mùa vụ, Tết âm lịch, khuyến mãi | Thành phần chuỗi thời gian, yếu tố biết trước (2.2.1) | Đặc trưng lịch có cửa sổ, lịch âm |
| Cần biết mô hình phức tạp có đáng dùng | Phương pháp mốc, FVA (2.2.2, 2.3.1) | So sánh với Naive, trung bình trượt, ETS, Croston, TSB |
| Chọn mô hình dự báo | Prophet, LightGBM, học sâu, kết hợp (2.2.3–2.2.6) | Chọn trên tập kiểm định, kiểm tra một lần |
| Đánh giá công bằng | WMAPE, Bias, kiểm định cuốn chiếu, rò rỉ thông tin (2.3) | Luật ghi trước khi chạy |
| Chuyển dự báo thành lượng đặt | EOQ, SS theo sai số dự báo, ROP, (s, Q) và (R, S) (2.1.2–2.1.4) | Mô phỏng 12 tháng, so sánh chính sách |
| Hàng chỉ bán một mùa | Newsvendor (2.1.6) | Phân tích riêng cho hàng dịp lễ |
| Người dùng cần tin dự báo | Phân rã thành phần, SHAP (2.2.7); khoảng dự báo (2.3.3) | Màn "Dự báo" trên dashboard |

## Tài liệu tham khảo của chương (cần kiểm tra lại với bản gốc)

- Arrow, K. J., Harris, T., & Marschak, J. (1951). Optimal inventory policy. *Econometrica*, 19(3), 250–272.
- Axsäter, S. (2015). *Inventory Control* (3rd ed.). Springer.
- Bates, J. M., & Granger, C. W. J. (1969). The combination of forecasts. *Operational Research Quarterly*, 20(4), 451–468.
- Box, G. E. P., & Jenkins, G. M. (1970). *Time Series Analysis: Forecasting and Control*. Holden-Day.
- Brown, R. G. (1959). *Statistical Forecasting for Inventory Control*. McGraw-Hill.
- Challu, C., Olivares, K. G., Oreshkin, B. N., Garza, F., Mergenthaler-Canseco, M., & Dubrawski, A. (2023). N-HiTS: Neural hierarchical interpolation for time series forecasting. *Proceedings of the AAAI Conference on Artificial Intelligence*, 37(6).
- Croston, J. D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly*, 23(3), 289–303.
- Das, A., Kong, W., Leach, A., Mathur, S., Sen, R., & Yu, R. (2023). Long-term forecasting with TiDE: Time-series dense encoder. *Transactions on Machine Learning Research*.
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of Statistics*, 29(5), 1189–1232.
- Gilliland, M. (2010). *The Business Forecasting Deal*. Wiley.
- Harris, F. W. (1913). How many parts to make at once. *Factory, The Magazine of Management*, 10(2), 135–136.
- Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735–1780.
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts.
- Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting*, 22(4), 679–688.
- Jørgensen, B. (1987). Exponential dispersion models. *Journal of the Royal Statistical Society, Series B*, 49(2), 127–162.
- Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*, 30.
- Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T. (2021). Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. *International Journal of Forecasting*, 37(4), 1748–1764.
- Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.
- Lundberg, S. M., Erion, G., Chen, H., et al. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2, 56–67.
- Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2020). The M4 Competition: 100,000 time series and 61 forecasting methods. *International Journal of Forecasting*, 36(1), 54–74.
- Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and conclusions. *International Journal of Forecasting*, 38(4), 1346–1364.
- Nahmias, S. (1994). Demand estimation in lost sales inventory systems. *Naval Research Logistics*, 41(6), 739–757.
- Silver, E. A., Pyke, D. F., & Thomas, D. J. (2017). *Inventory and Production Management in Supply Chains* (4th ed.). CRC Press.
- Syntetos, A. A., & Boylan, J. E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303–314.
- Syntetos, A. A., Boylan, J. E., & Disney, S. M. (2009). Forecasting for inventory planning: A 50-year review. *Journal of the Operational Research Society*, 60(sup1), S149–S160.
- Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: An analysis and review. *International Journal of Forecasting*, 16(4), 437–450.
- Taylor, S. J., & Letham, B. (2018). Forecasting at scale. *The American Statistician*, 72(1), 37–45.
- Teunter, R. H., Syntetos, A. A., & Babai, M. Z. (2011). Intermittent demand: Linking forecasting to inventory obsolescence. *European Journal of Operational Research*, 214(3), 606–615.
