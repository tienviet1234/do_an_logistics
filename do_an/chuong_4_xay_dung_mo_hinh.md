# CHƯƠNG 4. XÂY DỰNG MÔ HÌNH VÀ ĐÁNH GIÁ KẾT QUẢ

> **Ghi chú cho người viết (xóa trước khi nộp)**
> - Bản nháp lần 1, soạn ngày 10–11/11/2026. Số liệu lấy từ `reports/so_lieu_do_an.md` và `docs/10` (mục ghi ở cuối mỗi bảng). **Đang chạy lại toàn bộ hệ thống từ đầu trên một bản sạch** (`src/chay_lai_toan_bo.py`); khi xong phải đối chiếu lại mọi bảng trong chương này với sổ số liệu mới.
> - Thứ tự trình bày: quy trình → dữ liệu và đặc trưng → khung đánh giá → dự báo trên bộ mô phỏng → dự báo trên M5 (kết quả chính) → tồn kho trên hai bộ → nghiệp vụ bổ sung → hệ thống hỗ trợ quyết định → thảo luận.
> - Hình: `reports/eda/`, `reports/ket_qua/`, `reports/word/anh/`. Đánh số lại theo mẫu của trường.
> - Các kết quả âm tính (mô hình không đạt luật, cảnh báo lệch không đạt) được giữ nguyên trong chương này. Không xóa để "đẹp" kết quả.

Chương này trình bày cách xây dựng hệ thống, từ dữ liệu đến quyết định đặt hàng, và kết quả đánh giá trên hai bộ dữ liệu đã mô tả ở Chương 3. Nguyên tắc xuyên suốt: **mọi lựa chọn đều đưa ra trên tập kiểm định theo luật ghi trước khi chạy; tập kiểm tra chỉ chạy một lần để báo cáo**, kể cả khi kết quả trên tập kiểm tra gợi ý một lựa chọn khác.

## 4.1. Quy trình tổng thể

Hệ thống gồm năm khâu nối tiếp, mỗi khâu là một chương trình Python chạy độc lập, đọc đầu vào và ghi kết quả vào một cơ sở dữ liệu SQLite chung:

1. **Dữ liệu:** làm sạch, nhận diện hết hàng, dựng lịch sự kiện (Chương 3).
2. **Đặc trưng:** biến lịch, sự kiện, khuyến mãi, giá trị trễ thành các cột số.
3. **Dự báo:** chạy các mô hình trên cùng khung kiểm định cuốn chiếu, chọn và kết hợp mô hình trên tập kiểm định.
4. **Tồn kho:** tính SS, ROP, lượng đặt từ dự báo; mô phỏng vận hành kho 12 tháng để so sánh các chính sách.
5. **Hỗ trợ quyết định:** dashboard 5 màn đọc từ cơ sở dữ liệu, cùng dữ liệu xuất cho Power BI.

Cơ sở dữ liệu gồm các bảng danh mục (mã hàng, nhà cung cấp), lịch (sự kiện, ngày nghỉ, khuyến mãi), giao dịch (thô, sạch, nhật ký sửa lỗi), dự báo (mọi mô hình, mọi mốc), tham số và kết quả tồn kho, mô phỏng từng ngày, và kết quả thử độ nhạy. Mỗi lần nạp, chương trình tự kiểm tra toàn vẹn (tổng số xuất khớp tệp nguồn, không có mã lạ, mọi dòng thỏa đẳng thức tồn kho). Toàn bộ quy trình chạy lại được từ đầu bằng một lệnh (`python src/chay_lai_toan_bo.py`), trên một bản sạch chỉ có mã nguồn và dữ liệu đầu vào. [Hình 4.1: sơ đồ luồng hệ thống, `trinh_bay/so_do_bao_cao.html` hoặc `reports/so_do/bao_cao_0_tong_quan.png`.]

## 4.2. Phân tích khám phá

Phân tích khám phá được thực hiện trên bộ mô phỏng (8 hình, `reports/eda/h01–h08`), vì đây là bộ có đủ nghiệp vụ Việt Nam; đặc điểm của bộ M5 đã tóm tắt ở mục 3.4.

| Hình | Nội dung | Phát hiện |
|---|---|---|
| 4.2 | Tổng xuất kho theo ngày | Đỉnh lớn nhất trước Tết; đỉnh phụ tháng 9–10 (Trung thu, khai giảng, bão Yagi) |
| 4.3 | Sáu mã đại diện | Mỗi kiểu hàng có hình dạng nhu cầu riêng: ổn định, mùa vụ (bánh trung thu, mứt Tết), tăng khi bão (mì gói), rời rạc |
| 4.4 | Chu kỳ tuần | Thứ Bảy 1,16 lần mức trung bình, Chủ nhật 0,53 lần: chu kỳ 7 ngày là bắt buộc |
| 4.5 | Chỉ số mùa theo nhóm hàng | Đồ chơi mùa thu gấp 3,75 lần, đồ trang trí mùa đông 2,47 lần, kem mùa hạ 1,96 lần |
| 4.6 | Phân rã chuỗi | Xu hướng gần như đi ngang; mùa vụ năm mạnh; phần dư lớn ở tuần Tết vì Tết âm lịch đổi ngày mỗi năm, cần biến ngày lễ riêng |
| 4.7 | Ma trận ABC × XYZ | Bảng 3.6 |
| 4.8 | Phân loại Syntetos–Boylan | 58 đều, 54 thất thường, 9 rời rạc và thất thường |
| 4.9 | Tác động khuyến mãi | So trong cùng tháng: trung vị tăng 60%; 4 mã có hệ số dưới 1 |

*Nguồn: `reports/bao_cao_eda.md`; `docs/10`, mục 4.*

**Một bài học về nhiễu chéo.** Cách tính đầu tiên của Hình 4.9 so ngày khuyến mãi với mọi ngày không khuyến mãi, và cho thấy 11 mã như thể "khuyến mãi làm giảm bán". Nguyên nhân là khuyến mãi của các mã này thường rơi vào lúc trái mùa, khi nhu cầu vốn thấp; so như vậy là so lẫn tác động của khuyến mãi với tác động của mùa. Khi đổi sang so trong cùng tháng, hiện tượng này gần như biến mất. Đây là ví dụ cụ thể của nhiễu chéo (confounding): một yếu tố thứ ba (mùa vụ) ảnh hưởng đồng thời tới cả "có khuyến mãi" và "lượng bán".

**Hàm ý cho mô hình:** cần biến thứ trong tuần, biến ngày lễ có cửa sổ trước–sau, biến theo âm lịch cho Tết và Trung thu, biến khuyến mãi; nhóm Z và hàng mùa vụ là nơi mô hình có thông tin sự kiện được kỳ vọng thắng phương pháp mốc.

## 4.3. Đặc trưng

Bảng đặc trưng của bộ mô phỏng có 132.616 dòng × 64 cột (`src/dac_trung.py`):

| Nhóm | Nội dung | Biết trước? |
|---|---|---|
| Lịch | Thứ, cuối tuần, tháng, tuần và ngày trong năm, mùa, đầu/cuối tháng | Có |
| Ngày lễ, sự kiện | 17 cờ sự kiện có cửa sổ trước–sau; số ngày đến/sau Tết, Trung thu, Noel và các dịp khác | Có |
| Sale, khuyến mãi | 11.11, 12.12, Black Friday; lịch khuyến mãi theo mã | Có |
| Giá trị trễ, trượt | Số bán 7, 14, 28 … 364 ngày trước; trung bình và độ lệch chuẩn trượt; **số bán cùng ngày âm lịch năm trước** | Chỉ dùng phần đã có tại mốc |
| Mã hàng | Nhóm hàng, loại mùa vụ, ABC/XYZ và kiểu nhu cầu (tính trên tập huấn luyện), giá | Có |
| Bão, thời tiết, dịch bệnh | Cờ sự kiện | **Không**: chỉ dùng để giải thích và loại khỏi chấm điểm, không đưa vào mô hình |

Hai quyết định để tránh rò rỉ thông tin:

- Phân loại ABC/XYZ trong danh mục gốc tính trên cả 36 tháng, tức có nhìn vào giai đoạn kiểm tra. Phân loại được tính lại chỉ trên tập huấn luyện; 2 mã đổi nhóm ABC, 3 mã đổi nhóm XYZ. Mô hình dùng bản tính lại.
- Mục tiêu học và chấm (`y_cham`) bỏ các ngày hết hàng, kho đóng cửa và đơn hàng lớn đột xuất (đơn B2B không biết trước): 8.706 dòng hết hàng hoặc kho đóng cửa được bỏ khỏi mục tiêu.

**Số bán cùng ngày âm lịch năm trước** là đặc trưng riêng cho Việt Nam: vì Tết và Trung thu lệch vài tuần mỗi năm theo dương lịch, giá trị "cùng ngày năm trước" (364 ngày) đặt đỉnh Tết sai chỗ. Đặc trưng âm lịch dịch theo khoảng cách giữa hai Tết (hoặc hai Trung thu) gần nhất, nên so đúng "8 ngày trước Tết năm nay" với "8 ngày trước Tết năm ngoái".

## 4.4. Khung đánh giá

**Chia tập theo thời gian** (bộ mô phỏng; bộ M5 chia theo cùng quy tắc, tự suy từ ngày cuối dữ liệu):

- Huấn luyện: 01/10/2023 – 30/09/2025 (24 tháng, đủ 2 mùa Tết).
- Kiểm định (validation2): 13 mốc từ 30/09/2024 đến 01/09/2025, cùng ngày với các mốc kiểm tra nhưng sớm hơn một năm, nên có đủ Tết, Trung thu và bão.
- Kiểm tra (test): 12 tháng cuối, 01/10/2025 – 30/09/2026.

**Kiểm định cuốn chiếu:** tại mỗi mốc, mô hình học từ dữ liệu đến mốc và dự báo 28 ngày tiếp theo. Ban đầu các mốc cách nhau 28 ngày; từ vòng 4 các mốc cách nhau **7 ngày**, đúng như cách dùng thực tế là cập nhật dự báo mỗi tuần, và mỗi ngày được chấm trên bản dự báo **mới nhất** có trước nó.

**Chỉ số:** WMAPE theo ngày (chỉ số chính), WMAPE theo tuần, Bias, MASE, và WMAPE theo nhóm X, Y, Z (Chương 2, mục 2.3.1). Chỉ chấm trên nhu cầu tin được (`y_cham`).

**Luật chọn, ghi trước khi chạy, dùng chung cho mọi vòng:** chọn phương án có WMAPE kiểm định thấp nhất; chỉ thay mô hình đang dùng nếu WMAPE giảm ít nhất 0,005 và |Bias| không tăng quá 1 điểm phần trăm; chênh lệch nhỏ hơn thì giữ phương án đơn giản hơn.

**Kiểm tra không nhìn trước:** mọi ngày dự báo nằm sau mốc; giá trị trễ ở ngày xa nhất bằng đúng số bán ngày mốc; với mô hình học sâu, đổi toàn bộ nhu cầu sau mốc thành số ngẫu nhiên thì đầu vào mô hình không đổi.

## 4.5. Kết quả dự báo trên bộ mô phỏng

Bộ mô phỏng được dùng để xây dựng và chọn mô hình qua 5 vòng. Mỗi vòng có luật ghi trước, chọn trên kiểm định.

### 4.5.1. Phương pháp mốc

Trong các phương pháp mốc, **trung bình trượt 28 ngày** tốt nhất (WMAPE test 0,640, giảm 17,2% so với Seasonal Naive 0,773). Seasonal Naive kém nhất dù dữ liệu có chu kỳ tuần rõ, vì chép nguyên một tuần là chép cả nhiễu của tuần đó. ARIMA chạy cho 28 mã nhóm A nhưng vẫn kém Croston trên nhóm này (0,493 so với 0,484) mà chậm gấp khoảng 20 lần, nên không mở rộng. ETS dự báo thừa có hệ thống (Bias −16,7%). Croston và TSB không thắng ngay cả ở nhóm "rời rạc và thất thường", vì 9 mã nhóm này trong dữ liệu là hàng thời vụ chứ không phải hàng bán lẻ tẻ ngẫu nhiên. **Điểm yếu chung là nhóm Z**: phương pháp mốc tốt nhất vẫn sai 127%, vì không phương pháp nào biết sắp tới Tết hay Trung thu.

### 4.5.2. Prophet và LightGBM

- **Prophet** (mỗi mã một mô hình, lịch lễ và khuyến mãi biết trước, dạng cộng chọn trên kiểm định): WMAPE test 0,454, giảm 29% so với trung bình trượt. Lợi thế đến từ lịch lễ: nhóm Z giảm từ 1,272 xuống 0,638, nhóm X chỉ cải thiện nhẹ (0,408 → 0,383).
- **LightGBM** (một mô hình chung cho 121 mã, hàm mất mát Tweedie chọn trên kiểm định): WMAPE test 0,399, chính xác nhất theo ngày ở thời điểm đó, nhanh hơn Prophet khoảng 20 lần. Nhưng **dự báo thiếu hàng mùa vụ trước cao điểm**: Bias nhóm Z +40,2%. Với kho, thiếu hàng trước Tết là sai lầm đắt nhất.

Độ quan trọng đặc trưng của LightGBM: mã hàng 35,5%, trung bình 7 ngày (tính đến 28 ngày trước) 10,8%, số bán cùng ngày năm trước 7,7%, loại mùa vụ 7,3%, số ngày đến Tết 5,5%. Khuyến mãi chỉ xếp hạng 13 dù làm bán tăng 60%: khuyến mãi chỉ chiếm khoảng 8% số ngày, và độ quan trọng kiểu "gain" đo tổng đóng góp chứ không đo độ lớn tác động mỗi lần.

### 4.5.3. Chọn mô hình: bài học về tập kiểm định

Hai mô hình mạnh ở hai chỗ khác nhau, nên các phương án kết hợp được thử: dự báo = w × LightGBM + (1 − w) × Prophet, với w chung hoặc theo nhóm XYZ.

**Vòng 1** dùng tập kiểm định là 6 mốc tháng 4–9/2025, một giai đoạn không có Tết hay cao điểm lớn. Luật chọn ra LightGBM. Trên test, phương án trung bình hai mô hình lại tốt hơn ở mọi chỉ số. Nguyên nhân: giai đoạn kiểm định "êm" không làm lộ điểm yếu dự báo thiếu trước cao điểm của LightGBM. Đề tài **không** đổi sang phương án trung bình dựa trên kết quả test, vì như vậy là chọn theo đề thi.

**Vòng 2** chỉ đổi một điều: tập kiểm định thành 13 mốc cùng ngày với các mốc test nhưng sớm hơn một năm (validation2), có đủ mùa cao điểm. Validation2 lộ đúng điểm yếu của LightGBM (Bias +12,9%, sát mức +11,7% trên test), và thứ hạng trên validation2 khớp với test. Phương án được chọn là **kết hợp theo nhóm XYZ** (w LightGBM: X 0,9, Y 1,0, Z 0,6): hàng ổn định dựa gần hết vào LightGBM, hàng mùa vụ lấy 40% từ Prophet. WMAPE test 0,375.

**Bài học phương pháp:** tập kiểm định phải có cùng đặc điểm với giai đoạn sẽ áp dụng mô hình, ở đây là phải có mùa cao điểm.

### 4.5.4. Vòng 3: dùng dữ liệu đúng nghiệp vụ

Chẩn đoán trên validation2 cho thấy dự báo 1–7 ngày tới không chính xác hơn 15–28 ngày tới, vì LightGBM chỉ dùng số bán từ 28 ngày trước trở về, trong khi 58% mã có lead time không quá 7 ngày. Ba cải tiến được thử lần lượt, mỗi bước chỉ giữ nếu đạt luật:

| Bước (validation2) | WMAPE | Bias | Theo luật |
|---|---:|---:|---|
| Gốc (LightGBM cũ) | 0,403 | +12,9% | — |
| A: dự báo theo tầm (3 mô hình cho ngày 1–7, 8–14, 15–28) | 0,392 | +11,8% | Giữ |
| B: thêm lịch sự kiện và số bán cùng ngày âm lịch năm trước | 0,385 | +10,2% | Giữ |
| F: dò 8 cấu hình tham số | 0,384 | +9,8% | Bỏ (chỉ giảm 0,0016) |
| Ghép với Prophet theo nhóm XYZ (`ket_hop_v3`) | **0,379** | +7,1% | Thay mô hình vòng 2 |

*Nguồn: `docs/10`, mục 9.4; `reports/nang_cap_du_bao.md`.*

Trên test, `ket_hop_v3` đạt WMAPE 0,368 và **Bias +3,9%, lần đầu nằm trong ngưỡng ±5%**. Độ chính xác tăng nhờ cách dùng dữ liệu đúng nghiệp vụ (dùng số bán gần nhất cho dự báo ngắn hạn, so theo âm lịch), không nhờ chỉnh tham số.

### 4.5.5. Vòng 4: cập nhật mỗi tuần và khoảng dự báo

| Bước (validation2) | WMAPE | Bias | Theo luật |
|---|---:|---:|---|
| Đang giữ `ket_hop_v3` (cập nhật mỗi 28 ngày) | 0,379 | +7,1% | |
| B1: tự hiệu chỉnh lệch từ sai số đã qua | 0,383 | +3,5% | Bỏ: lệch giảm một nửa nhưng WMAPE tăng |
| B2: cảnh báo bão 4 ngày trước | 0,384 | +5,8% | Bỏ: sai số trong cửa sổ bão tăng |
| **B3: cập nhật dự báo mỗi tuần** (`ket_hop_v4`) | **0,358** | +5,5% | Giữ |
| Sàn sai số (đối chiếu) | ≈ 0,286 | | |

*Nguồn: `docs/10`, mục 9.5. Sàn sai số là sai số còn lại nếu biết đúng nhu cầu kỳ vọng từng ngày; chỉ tính được trên dữ liệu mô phỏng.*

Ba điều rút ra:

1. **Sửa lệch ở khâu dự báo làm WMAPE tệ đi.** Với nhu cầu lệch phải, con số làm WMAPE nhỏ nhất là trung vị, thấp hơn trung bình; nên dự báo "hơi thấp" lại là tối ưu theo WMAPE. Lệch được xử lý ở khâu tồn kho (hệ số hiệu chỉnh, mục 4.7).
2. **Rủi ro hiếm như bão không sửa được bằng một hệ số cố định** khi chỉ có một vài trận để học; xử lý bằng khoảng dự báo và tồn kho an toàn.
3. **Cải thiện lớn nhất đến từ quy trình** (dùng số liệu mới nhất mỗi tuần), không từ mô hình phức tạp hơn.

**Khoảng dự báo 80% và 95%** lấy theo phân vị thực nghiệm của sai số, học trực tuyến qua các mốc (mốc k chỉ học từ dòng đã có thực tế tại mốc). Trên test, tỉ lệ thực tế rơi vào khoảng 80% là 80,9%, khoảng 95% là 96,0%; với tổng nhu cầu trong lead time là 81,3% và 95,5%. Các tỉ lệ này khớp mức danh nghĩa.

### 4.5.6. Vòng 5: học sâu

LSTM, RNN (mã hóa – giải mã, một mô hình chung cho 121 mã, cấu hình cố định trước khi chạy) và ba mô hình TiDE, N-HiTS, TFT (thư viện NeuralForecast) được đưa vào cùng khung đánh giá. Theo luật, **hệ thống giữ `ket_hop_v4`**: không ứng viên nào vừa giảm WMAPE validation2 ít nhất 0,005 vừa giữ được Bias (phương án ghép v4 với LSTM giảm WMAPE 0,0065 nhưng |Bias| tăng 2,2 điểm; phương án ghép v4 với TFT giảm WMAPE 0,006 — từ 0,358 xuống 0,352 — nhưng |Bias| tăng 1,8 điểm, từ +5,5% lên +7,3%, vượt mức tối đa 1 điểm).

**Ghi nhận trung thực:** trên test, RNN (0,349), phương án ghép v4 với LSTM (0,351), phương án ghép v4 với TFT (0,354) và LSTM (0,355) đều có WMAPE **thấp hơn** `ket_hop_v4` (0,356), đổi lại dự báo thiếu nhiều hơn (Bias +7,2%, +4,8%, +5,0%, +5,2% so với +3,0%). Quyết định không đổi vì đã chọn trên validation2 và chênh lệch nhỏ. Một giải thích có thể là validation2 bắt đầu khi mới có một năm dữ liệu, trong khi học sâu cần nhiều dữ liệu hơn; giải thích này **chưa được kiểm chứng**.

### 4.5.7. Tổng hợp trên tập kiểm tra (bộ mô phỏng)

**Bảng 4.x. WMAPE trên tập kiểm tra, bộ mô phỏng (chọn lọc)**

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---:|---:|---:|---:|---:|---:|
| **Kết hợp v4, cập nhật tuần (đang dùng)** | **0,356** | 0,203 | +3,0% | 0,310 | 0,378 | 0,477 |
| RNN (không đạt luật trên validation2) | 0,349 | 0,209 | +7,2% | 0,301 | 0,367 | 0,474 |
| Kết hợp v4 + TFT (không đạt luật) | 0,354 | 0,205 | +5,0% | 0,308 | 0,370 | 0,477 |
| LSTM (không đạt luật) | 0,355 | 0,210 | +5,2% | 0,314 | 0,383 | 0,459 |
| Kết hợp v3, cập nhật 28 ngày | 0,368 | 0,226 | +3,9% | 0,319 | 0,392 | 0,496 |
| LightGBM | 0,399 | 0,269 | +11,7% | 0,312 | 0,391 | 0,638 |
| TFT | 0,425 | 0,302 | +17,1% | 0,322 | 0,409 | 0,710 |
| Prophet | 0,454 | 0,257 | −4,9% | 0,383 | 0,486 | 0,638 |
| TiDE | 0,477 | 0,357 | +17,8% | 0,373 | 0,446 | 0,767 |
| TB trượt 28 ngày, cập nhật tuần | 0,584 | 0,443 | −0,2% | 0,391 | 0,558 | 1,116 |
| TB trượt 28 ngày | 0,640 | 0,511 | −0,8% | 0,408 | 0,653 | 1,272 |
| Croston SBA | 0,651 | 0,516 | +0,4% | 0,395 | 0,589 | 1,365 |
| Seasonal Naive | 0,773 | 0,598 | −11,0% | 0,475 | 0,597 | 1,636 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 2; dòng "Kết hợp v4 + TFT": `reports/bang_so_sanh_test.md` (`ket_hop_nf`) và `reports/mo_hinh_nf.md`. Bias dương là dự báo thấp hơn thực tế.*

Mô hình đang dùng giảm WMAPE **54%** so với Seasonal Naive và **39%** so với trung bình trượt cùng cập nhật mỗi tuần (0,356 so với 0,584), đạt tiêu chí "giảm ít nhất 20%" và Bias trong ±5%. Tuy nhiên, như Chương 3 đã nêu, nhu cầu mô phỏng được sinh từ chính các yếu tố mà mô hình biết trước, nên con số này **lạc quan hơn thực tế**. Mục 4.6 cho thấy lạc quan đến đâu.

## 4.6. Kết quả dự báo trên số bán thật M5

Quy trình được chạy lại trên bộ M5 với **cấu hình mô hình giữ nguyên, không dò thêm**: trung bình trượt 28 ngày, lặp tuần trước, Prophet, LightGBM theo tầm, LSTM, RNN, tất cả cập nhật mỗi 7 ngày. Trọng số ghép dò trên validation2 của M5. Ba câu hỏi kiểm chứng được ghi trước khi chạy: (a) mô hình chọn có thấp hơn trung bình trượt trên test không; (b) thứ hạng các mô hình có giống bộ mô phỏng không; (c) mức giảm sai số so với trung bình trượt lớn đến đâu so với 39% của bộ mô phỏng.

**Bảng 4.x. Kết quả trên M5, tập kiểm tra**

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---:|---:|---:|---:|---:|---:|
| **Ghép RNN với (LightGBM + Prophet), được chọn** | **0,307** | 0,162 | +3,1% | 0,299 | 0,328 | 0,930 |
| RNN | 0,311 | 0,170 | +4,4% | 0,303 | 0,331 | 0,906 |
| LightGBM + Prophet | 0,313 | 0,164 | +2,0% | 0,305 | 0,337 | 0,989 |
| LightGBM | 0,314 | 0,165 | +2,0% | 0,306 | 0,337 | 1,001 |
| LSTM | 0,317 | 0,178 | +4,6% | 0,308 | 0,343 | 0,792 |
| TB trượt 28 ngày | 0,356 | 0,187 | +0,4% | 0,343 | 0,390 | 0,989 |
| Prophet | 0,389 | 0,250 | +1,1% | 0,350 | 0,502 | 1,038 |
| Lặp tuần trước | 0,420 | 0,200 | +0,5% | 0,410 | 0,446 | 1,173 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 10.1. Mô hình được chọn trên validation2 (WMAPE 0,331); nhóm Z của M5 chỉ có 1 mã.*

**Trả lời ba câu hỏi ghi trước:**

- **(a) Có, nhưng ít hơn nhiều:** mô hình được chọn giảm WMAPE **13,8%** so với trung bình trượt.
- **(b) Giống một phần.** Trên cả hai bộ, mô hình ghép và học sâu đứng đầu, sát nhau, và Prophet kém LightGBM. Khác biệt: trên M5, trung bình trượt (0,356) **tốt hơn Prophet** (0,389), còn trên bộ mô phỏng trung bình trượt kém xa Prophet.
- **(c) Mức giảm 13,8% trên số thật, so với 39% trên bộ mô phỏng**, chỉ bằng khoảng một phần ba. Đây là con số quan trọng nhất của phần dự báo: dữ liệu mô phỏng có quy luật rõ, sinh từ chính các yếu tố mà mô hình được biết trước, nên làm trí tuệ nhân tạo trông tốt hơn nhiều so với trên số bán thật. **Con số 39% không được trình bày như hiệu quả dự kiến khi áp dụng thực tế.**

Ba mô hình TiDE, N-HiTS, TFT trên M5 đều kém mô hình đang dùng (WMAPE test 0,328; 0,341; 0,325, Bias +5,5% đến +10,9%); phương án ghép thêm TiDE không đạt luật thay mô hình trên validation2 (`reports/so_lieu_do_an.md`, mục 10.2). Một điểm đáng chú ý là trên M5, mô hình được chọn có dùng học sâu (RNN), còn trên bộ mô phỏng thì không. M5 có hơn 5 năm dữ liệu so với 3 năm của bộ mô phỏng; đây có thể là lý do học sâu đóng góp được vào mô hình ghép, nhưng điều này chưa được kiểm chứng riêng.

## 4.7. Chính sách tồn kho

### 4.7.1. Thiết kế mô phỏng

Mô phỏng vận hành kho trong 12 tháng của tập kiểm tra, cho 121 mã. Mọi chính sách dùng **chung** nhu cầu thật (kể cả nhu cầu ở ngày hết hàng, chỉ dùng để chấm), thời gian giao hàng thực tế (bốc ngẫu nhiên một lần với hạt giống cố định, cộng chậm do bão và nhà cung cấp), tồn kho ban đầu, chi phí và mức phục vụ. Mỗi ngày kho mở cửa: nếu tồn hiện có cộng hàng đang về không vượt ROP thì đặt hàng; hết hàng thì mất bán. Chỉ dùng dự báo của mốc gần nhất đã qua.

Bốn chính sách được so sánh:

| Chính sách | Mô tả |
|---|---|
| Hiện trạng | Bộ mô phỏng: đơn hàng có sẵn trong dữ liệu, người lập kế hoạch dùng đường nhu cầu kỳ vọng của tương lai, chỉ lệch ±10%: **đối thủ mạnh hơn thực tế**. Bộ M5: không có tồn kho thật, dùng một quy tắc kinh nghiệm (mỗi 7 ngày đặt đủ 21 ngày bán theo trung bình 28 ngày trước) |
| Công thức + dự báo mốc | SS, ROP, lượng đặt theo Chương 2, dự báo bằng trung bình trượt 28 ngày cập nhật mỗi tuần |
| Công thức + dự báo AI | Như trên, dự báo bằng mô hình đã chọn |
| AI + hiệu chỉnh lệch | Như trên, dự báo nhân thêm hệ số hiệu chỉnh lệch theo nhóm XYZ ước lượng trên validation2 |

**So sánh chính là AI với dự báo mốc dùng cùng công thức, cùng tần suất cập nhật**: chỉ khác nhau ở dự báo, nên chênh lệch đo đúng giá trị của dự báo.

### 4.7.2. Chọn quy tắc lượng đặt: vấn đề của hàng chỉ bán dịp lễ

Vòng đầu dùng EOQ cho mọi mã. Kết quả cho thấy ở nhóm Z, chính sách AI giữ tồn gần gấp đôi hiện trạng, phần lớn chênh lệch nằm ở 5 mã chỉ bán dịp lễ (cây thông Noel, bánh quy Noel, đồ hóa trang và kẹo Halloween, dây đèn LED). Cơ chế: gần lễ dự báo tăng vọt, ROP tăng vọt, công thức đặt nhiều lần EOQ, hàng về khi mùa đã qua, nên vừa thiếu trong mùa vừa tồn tới cuối năm. **EOQ giả định nhu cầu đều**, không hợp với hàng thời vụ.

Vì phát hiện này đến từ tập kiểm tra, cách sửa được chọn trên validation2 theo luật mới: ba quy tắc lượng đặt (EOQ; đặt đến mức; lai = EOQ cho nhóm X, Y và đặt đến mức cho nhóm Z) × hai chính sách AI, chọn cặp có chi phí liên quan thấp nhất. Với dự báo cập nhật mỗi tuần, cặp được chọn là **quy tắc lai, AI + hiệu chỉnh** (chi phí liên quan validation2 4,05 tỷ đồng, so với 4,36 tỷ của EOQ). Quy tắc này được áp cho mọi chính sách theo công thức rồi chạy test một lần.

### 4.7.3. Kết quả trên bộ mô phỏng

**Bảng 4.x. Trước – sau, tập kiểm tra, mức phục vụ 95%, bộ mô phỏng**

| Chỉ số | Hiện trạng | Công thức + dự báo mốc | Công thức + dự báo AI | **AI + hiệu chỉnh** |
|---|---:|---:|---:|---:|
| Fill Rate | 93,57% | 91,69% | 95,33% | **95,82%** |
| Số ngày-mã thiếu hàng | 1.564 | 916 | 793 | **735** |
| Tồn kho bình quân (triệu đ) | 11.993,6 | 19.669,7 | 9.208,7 | 11.906,0 |
| Số lần nhập hàng | 1.910 | 3.575 | 3.467 | 3.192 |
| Chi phí đặt + lưu (triệu đ) | 2.766,8 | 4.567,0 | 2.427,4 | 2.915,7 |
| Lợi nhuận mất (triệu đ) | 3.693,3 | 4.444,0 | 2.902,2 | 2.912,4 |
| **Chi phí liên quan (triệu đ)** | 6.460,1 | 9.011,0 | 5.329,6 | 5.828,1 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 6. Dữ liệu mô phỏng.*

- **So với dự báo mốc dùng cùng công thức:** Fill Rate tăng 4,1 điểm, số ngày-mã thiếu giảm 20%, tồn kho giảm 39,5%, **chi phí liên quan giảm 35,3%**.
- **So với hiện trạng** (đối thủ biết trước nhu cầu kỳ vọng): Fill Rate tăng 2,3 điểm, số ngày-mã thiếu giảm 53%, tồn kho thấp hơn 0,7%, chi phí liên quan giảm 9,8%; đổi lại số lần nhập hàng tăng 67%.
- **Ghi nhận trung thực:** trên test, chính sách AI **không** hiệu chỉnh còn rẻ hơn (5,33 tỷ so với 5,83 tỷ) nhưng Fill Rate thấp hơn (95,33%). Trên validation2, AI + hiệu chỉnh rẻ hơn, nên theo luật vẫn giữ AI + hiệu chỉnh.

**Theo nhóm hàng (mức phục vụ 95%):**

| Nhóm | Chính sách | Fill Rate | Tồn TB (triệu đ) | Lợi nhuận mất (triệu đ) |
|---|---|---:|---:|---:|
| X | AI + hiệu chỉnh | 95,6% | 3.663,3 | 2.381,8 |
| X | Dự báo mốc | 95,6% | 4.151,9 | 2.509,9 |
| X | Hiện trạng | 93,8% | 5.180,2 | 2.749,6 |
| Z | AI + hiệu chỉnh | 96,1% | 7.730,3 | 390,3 |
| Z | Dự báo mốc | 79,8% | 14.838,2 | 1.801,4 |
| Z | Hiện trạng | 91,9% | 6.340,5 | 805,0 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 6.*

Ở hàng ổn định (X), chính sách AI đáp ứng cao hơn hiện trạng mà tồn kho thấp hơn 29%. Ở hàng mùa vụ (Z), khác biệt lớn nhất là so với dự báo mốc: trung bình trượt không biết sắp tới mùa nên vừa thiếu hàng trong mùa (Fill Rate 79,8%) vừa giữ tồn gấp đôi.

**Mức phục vụ:** chi phí liên quan của AI + hiệu chỉnh ở 90%, 95%, 99% lần lượt là 5,99; 5,83; 5,38 tỷ đồng. Lợi nhuận mất lớn so với chi phí lưu kho nên mức phục vụ cao hơn có lợi hơn trong dữ liệu này. Mức 95% đã chốt trước nên không đổi; muốn đổi phải chọn lại trên validation2.

### 4.7.4. Kết quả trên bộ M5

**Bảng 4.x. Tập kiểm tra, mức phục vụ 95%, bộ kho dựng từ M5**

| Chính sách | Fill Rate | Ngày-mã thiếu | Tồn TB (triệu đ) | Số lần nhập | Chi phí liên quan (triệu đ) |
|---|---:|---:|---:|---:|---:|
| AI + hiệu chỉnh | 99,71% | 126 | 1.623,3 | 1.500 | 594,9 |
| AI | 99,64% | 127 | 1.584,4 | 1.511 | 597,2 |
| Dự báo mốc | 99,67% | 112 | 1.658,6 | 1.483 | 605,1 |
| Quy tắc kinh nghiệm | 99,38% | 303 | 1.195,0 | 5.830 | 1.245,0 |

*Nguồn: `docs/10`, mục 10.13; `du_lieu_nguon/m5_kho/reports/ton_kho_so_sanh.md`. Lead time, chi phí, tồn kho là giả định.*

**Trên số bán thật, lợi ích của dự báo AI đối với tồn kho gần như biến mất:** so với dự báo mốc, chi phí liên quan chỉ giảm 1,7%, tồn kho giảm 2,1%, Fill Rate tăng 0,04 điểm, và số ngày-mã thiếu còn cao hơn (126 so với 112). Hai bộ không so trực tiếp được với nhau về "hiện trạng" vì đối thủ khác nhau, nhưng so sánh AI với dự báo mốc (cùng công thức) thì so được: **35,3% trên bộ mô phỏng so với 1,7% trên M5**.

### 4.7.5. Vì sao lợi ích khác nhau giữa hai bộ

Giả thuyết đầu tiên là chi phí đặt hàng giả định (165.000 đ/lần) làm lượng đặt lớn (khoảng 35 ngày bán), che gần hết sai số dự báo. Giả thuyết này được kiểm tra bằng thử độ nhạy theo chi phí đặt (luật ghi trước: "lợi ích AI phụ thuộc chi phí đặt" nếu lợi ích ở S × 0,1 cao hơn ở S × 1 ít nhất 5 điểm):

| Chi phí đặt so với gốc | M5: lượng đặt (ngày bán) | M5: lợi ích AI | Mô phỏng: lượng đặt (ngày bán) | Mô phỏng: lợi ích AI |
|---:|---:|---:|---:|---:|
| × 0,1 | 11,6 | +6,4% | 4,8 | +37,1% |
| × 0,5 | 26,0 | +2,6% | 10,8 | +36,5% |
| × 1 (gốc) | 36,7 | +1,7% | 15,3 | +35,3% |
| × 2 | 51,9 | +0,1% | 21,6 | +34,9% |

*Nguồn: `docs/10`, mục 10.13; `reports/do_nhay_chi_phi_dat.md`. Lợi ích AI = mức giảm chi phí liên quan của AI + hiệu chỉnh so với dự báo mốc.*

Theo luật, ở **cả hai bộ** lợi ích "không phụ thuộc rõ" vào chi phí đặt (M5 tăng 4,7 điểm, mô phỏng 1,8 điểm), nên giả thuyết ban đầu **sai** và đã được đính chính.

**Lời giải thích có số liệu:** trên bộ mô phỏng, **nhóm Z (40 mã mùa vụ) đóng góp 91,6% mức giảm tồn kho và 92,1% mức giảm lợi nhuận mất** của AI + hiệu chỉnh so với dự báo mốc; dự báo mốc ở nhóm này chỉ đạt Fill Rate 79,8%. Bộ M5 chỉ có 1 mã nhóm Z, và dự báo mốc đã đạt 99,7% ở nhóm X. Nói cách khác, **trí tuệ nhân tạo có giá trị chủ yếu ở hàng mùa vụ, hàng theo sự kiện**; với hàng bán đều, trung bình trượt cộng tồn kho an toàn đã đủ.

Kết luận này phù hợp với kết quả dự báo: lợi thế của mô hình đến từ thông tin lịch lễ và mùa vụ (mục 4.5.2), mà hàng bán quanh năm thì không có thông tin đó để khai thác.

### 4.7.6. Thử độ nhạy (bộ mô phỏng)

Mỗi kịch bản chỉ đổi một yếu tố, chạy lại nguyên hàm mô phỏng, chính sách AI + hiệu chỉnh, mức phục vụ 95%:

| Kịch bản | Fill Rate | Chi phí liên quan (triệu đ) | Đổi chi phí |
|---|---:|---:|---:|
| Gốc | 95,82% | 5.828,1 | |
| Tắc cảng +3 ngày (trung bình 13 đợt) | 95,33% | 6.168,8 | +5,8% |
| Tắc cảng +7 ngày (trung bình 13 đợt) | 94,30% | 6.859,2 | +17,7% |
| Lead time +2 ngày, **không** cập nhật công thức | 90,76% | 9.250,4 | +58,7% |
| Lead time +2 ngày, **có** cập nhật | 95,39% | 6.044,2 | +3,7% |
| Chi phí lưu kho +15% | 95,91% | 6.076,2 | +4,3% |

*Nguồn: `reports/so_lieu_do_an.md`, mục 7; `docs/10`, mục 11.1. Mức tác động của các kịch bản là giả định.*

- **Tắc cảng tạm thời** chỉ làm Fill Rate giảm 0,5–1,5 điểm; chính sách dùng dự báo AI có chi phí thấp nhất ở cả 39 lần thử (13 đợt × 3 mức trễ). Đợt nguy hiểm nhất là ngay trước Tết, đúng lúc tồn kho đang được đẩy lên cho cao điểm.
- **Lead time dài ra lâu dài mà không cập nhật tham số** nguy hiểm hơn nhiều: Fill Rate giảm 5,1 điểm, chi phí tăng 59%. Cập nhật lead time vào công thức thì gần như hồi phục. **Công thức chỉ tốt khi tham số được cập nhật**; kho cần theo dõi lead time thực tế của từng nhà cung cấp.

## 4.8. Các nghiệp vụ kho bổ sung

Ngoài quyết định đặt hàng chính, một số nghiệp vụ được phân tích riêng, mỗi phần có luật ghi trước và báo cả kết quả bất lợi. Phần lớn chạy trên bộ mô phỏng vì M5 không có dữ liệu tương ứng (tên hàng, hạn sử dụng, thể tích).

| Nghiệp vụ | Cách làm | Kết quả chính |
|---|---|---|
| Chỉ số kho | Vòng quay, số ngày tồn, tồn dư (phần vượt nhu cầu 28 ngày kế tiếp) | Mô phỏng: AI + hiệu chỉnh vòng quay 24,2 lần/năm, 15,1 ngày tồn (dự báo mốc 14,2 lần, 25,7 ngày); M5: số ngày tồn chỉ giảm 2,3% so với dự báo mốc |
| Gom đơn theo nhà cung cấp | Gom các mã cùng nhà cung cấp cùng ngày vào một phiếu; đặt kèm mã sắp tới điểm đặt (k ngày) | Mô phỏng: gom cùng ngày −1,1% chi phí; đặt kèm k = 1 (chọn trên validation2) −4,7%, tồn +2,5%. M5: gom cùng ngày −5,8%; đặt kèm k = 3 thêm −4,0%, tồn +8,3%. Phụ thuộc giả định tỉ lệ chi phí chung của phiếu |
| Chấm điểm nhà cung cấp | 60% đúng hạn + 40% độ ổn định; cảnh báo khi 8 đơn gần nhất trễ trung bình ≥ 2 ngày | Test: 3.285 đơn, đúng hạn 77,6%. Cảnh báo bắt được đợt giao chậm nhưng **chậm 18–21 ngày**, dài hơn chính đợt đó: dùng để nhận ra nhà cung cấp đang xấu đi, không để phản ứng sớm |
| Hàng chỉ bán dịp lễ | Newsvendor (Chương 2, mục 2.1.6) so với quy tắc hiện tại | Validation2 chọn "newsvendor, đặt một lần" trong môi trường có hạn sử dụng; chi tiết `reports/newsvendor_mua_vu.md` |
| Hạn sử dụng, sức chứa | Hàng quá hạn bị loại; trần lượng đặt theo hạn; đỉnh thể tích kho | Giá trị hàng loại tập trung ở vài mã thời vụ (bánh trung thu, mứt Tết); chi tiết `reports/rang_buoc_kho.md`. Hạn dùng, thể tích là giả định |
| Đối chiếu giả định với Dominick's | Đo hệ số tăng bán khi khuyến mãi, biên lãi gộp, tài trợ của nhà sản xuất trên dữ liệu thật của một chuỗi siêu thị Mỹ | Biên lãi dùng làm giá vốn cho bộ M5 (mục 3.3.4); giả định của phần trữ hàng cho phiên livestream được chạy lại với số đo thật, báo cả trước và sau đối chiếu (`reports/dominicks.md`, `reports/tru_hang_live_sau_doi_chieu.md`) |

### 4.8.1. Cảnh báo dự báo bắt đầu lệch: một kết quả âm tính

Mục tiêu: báo sớm cho người lập kế hoạch khi một mã đang bị dự báo lệch kéo dài, bằng tín hiệu theo dõi (Chương 2, mục 2.3.4). Luật ghi trước yêu cầu cảnh báo phải (a) cùng chiều với lệch thật ở phần lớn trường hợp, (b) những mã bị cảnh báo phải lệch nhiều hơn rõ rệt so với mã không bị cảnh báo, (c) tỉ lệ cảnh báo không quá cao. Hai vòng được thử (theo ngày, rồi theo tuần kèm đo riêng thay đổi đột ngột).

Kết quả: **không ngưỡng nào đạt luật ở cả hai bộ**. Ở ngưỡng 4, trên M5, 72,8% cảnh báo cùng chiều với lệch thật, nhưng mã bị cảnh báo chỉ lệch gấp 1,32 lần mã không bị cảnh báo; trên bộ mô phỏng chỉ 50,2% cùng chiều. Phần đo thay đổi đột ngột phát hiện được 32,1% số lần nhưng báo nhầm gấp 6,4 lần. Theo luật, tính năng này **không đưa vào hệ thống**; kết quả được giữ lại vì cho biết với dự báo cập nhật mỗi tuần, phần lệch còn lại phần lớn là nhiễu ngắn hạn, khó báo trước.

## 4.9. Hệ thống hỗ trợ quyết định

### 4.9.1. Dashboard

Dashboard viết bằng Streamlit, **chỉ đọc** cơ sở dữ liệu, chạy trên máy không cần mạng. Người dùng chính là người lập kế hoạch kho. Giao diện dựng như một bộ phiếu kế hoạch đặt hàng, gồm 5 màn:

| Màn | Người dùng làm gì |
|---|---|
| Hôm nay | Chọn một ngày làm "hôm nay"; xem số mã hết hàng, cần đặt, tồn dưới ROP nhưng hàng đang về, đủ hàng; duyệt, sửa hoặc bỏ qua từng đơn đề xuất (mỗi dòng ghi lý do bằng số); tải phiếu đặt hàng theo nhà cung cấp; lịch 12 tháng để nhảy tới ngày nhiều việc |
| Dự báo | Xem 28 ngày chưa xảy ra; bấm cho mô hình chạy; xem vì sao ra con số; thử nếu bật khuyến mãi (mục 4.9.2) |
| Mặt hàng | Tồn kho 12 tháng của một mã cùng ROP và các lần đặt; dự báo so với thực tế; "Thử nếu": kéo mức phục vụ và số ngày hàng về chậm, SS, ROP, lượng đặt tính lại ngay |
| Kịch bản & kết quả | Bảng trước – sau theo mức phục vụ; theo nhóm XYZ; thử độ nhạy; chỉ số kho; gom đơn |
| Dữ liệu & phương pháp | Dữ liệu là gì, phần nào thật, phần nào giả định; các bước của hệ thống; xếp hạng mô hình; công thức |

Dashboard có bộ lọc chung (ngày, chính sách, nhóm ABC, nhóm XYZ), lọc chéo (bấm một ô trạng thái hoặc một ngày trên lịch thì mọi biểu đồ đổi theo) và đi sâu (bấm một dòng để mở màn Mặt hàng). Mỗi biểu đồ kèm "Cách đọc" và "Phát hiện"; phần phát hiện được tính từ dữ liệu, không ghi tay. Cùng một dashboard chạy được trên cả hai bộ dữ liệu bằng cách đổi thư mục nguồn.

**Kiểm chứng:** hàm "Thử nếu" dùng đúng công thức của mô phỏng, tái lập đủ 127.776/127.776 dòng ROP và lượng đặt của mô phỏng; mọi màn được thử bằng thao tác chuột thật trong trình duyệt, trên cả màn hình máy tính và điện thoại.

[Hình 4.x – 4.y: các màn dashboard, `reports/word/anh/`.]

### 4.9.2. Màn Dự báo: mô hình dự đoán và giải thích

Màn này trả lời trực tiếp câu hỏi "hệ thống có thực sự dự đoán hay chỉ đọc lại dữ liệu đã có", theo góp ý của giảng viên hướng dẫn.

**Dự báo cho ngày chưa xảy ra.** Mô hình đang dùng dự báo 28 ngày **sau ngày cuối của dữ liệu**, dùng lịch biết trước được mở rộng tự động (ngày lễ lặp lại theo dương lịch, Tết và Trung thu theo bảng âm lịch, không suy ra các sự kiện không biết trước). Trước khi tin kết quả tương lai, chương trình chạy lại mốc kiểm tra cuối cùng và phải ra **trùng** dự báo đã lưu. Kiểm tra độ hợp lý:

| Trung bình mỗi ngày | Bộ mô phỏng | Bộ M5 |
|---|---:|---:|
| Dự báo 28 ngày tới | 5.719 | 1.350 |
| Cùng kỳ năm trước | 7.543 (không tính ngày khuyến mãi: 6.490) | 1.255 |
| Cùng kỳ 2 năm trước | 5.567 (không tính ngày khuyến mãi) | 1.395 |
| 28 ngày gần nhất | 9.472 | 1.456 |

*Nguồn: `reports/so_lieu_do_an.md`, mục 8.12.*

Dự báo bộ mô phỏng thấp hơn 28 ngày gần nhất vì giai đoạn đó là mùa Trung thu; 28 ngày tới chưa có lịch khuyến mãi gửi trước nên mô hình coi như không khuyến mãi, và mức dự báo gần với cùng kỳ hai năm trước không khuyến mãi.

**Mô hình chạy khi bấm.** Người dùng chọn một mã và bấm "Chạy mô hình": hệ thống đọc dữ liệu, dựng 28 ngày tương lai, học lại LightGBM trên toàn bộ lịch sử và Prophet cho mã đó, rồi ghép theo trọng số đã chọn; từng bước hiện trên màn hình kèm thời gian (khoảng 30–40 giây). Kết quả được đối chiếu với bản đã lưu trong cơ sở dữ liệu và trùng tới sai số làm tròn của máy.

**Giải thích theo yếu tố.** Với một ngày bất kỳ trong 28 ngày tới, màn hình hiện công thức ghép (ví dụ: 90% × LightGBM + 10% × Prophet), rồi tách từng phần:

- LightGBM: mức nền nhân với hệ số của 9 nhóm yếu tố (đặc điểm mã hàng, mức bán gần đây, cùng kỳ năm trước, lễ và sự kiện, thứ trong tuần, khuyến mãi, thời điểm trong tháng và năm, Tết, sale sàn thương mại điện tử). Các hệ số lấy từ đóng góp SHAP của mô hình cây; vì mô hình dùng liên kết logarit, tích các hệ số bằng đúng dự báo.
- Prophet: xu hướng cộng mùa tuần, mùa năm, ngày lễ, khuyến mãi.
- Trên M5, phần RNN chỉ có con số tổng: mạng nơ-ron không tách được đóng góp theo yếu tố. Màn hình nói rõ điều này.

**Thử nếu bật khuyến mãi.** Người dùng chọn một khoảng ngày, hệ thống bật khuyến mãi trong khoảng đó và dự báo lại **không học lại mô hình**, so với dự báo gốc và với mức tăng **lịch sử cùng mùa** của chính mã đó (tỉ số giữa ngày khuyến mãi và trung bình 28 ngày không khuyến mãi trước đó). Trên toàn kho (121 mã, khuyến mãi 7 ngày), mô hình tăng trung vị × 1,61, lịch sử cùng mùa × 1,65; tương quan thứ hạng giữa hai cách đo là 0,39. Nghĩa là mô hình học được mức tác động chung khá đúng, nhưng chưa phân biệt tốt mã nào tăng mạnh, mã nào tăng ít khi khuyến mãi. Bộ M5 không có lịch khuyến mãi gốc nên phần này được ẩn.

## 4.10. Thảo luận

1. **Dự báo:** trên số bán thật, mô hình kết hợp (cây tăng cường + Prophet + RNN) giảm sai số 13,8% so với trung bình trượt. Trên dữ liệu mô phỏng mức giảm là 39%, nhưng con số này lạc quan vì dữ liệu sinh từ chính các yếu tố mô hình biết trước.
2. **Tồn kho:** giá trị của dự báo tốt hơn phụ thuộc mạnh vào cơ cấu mặt hàng. Khi có nhiều hàng mùa vụ, hàng theo dịp (bộ mô phỏng), chi phí liên quan giảm 35%; khi hàng chủ yếu bán đều (M5), chỉ giảm 1,7%. Khoảng 92% lợi ích trên bộ mô phỏng nằm ở nhóm Z.
3. **Quy trình quan trọng hơn mô hình:** những cải thiện lớn nhất đến từ cách dùng dữ liệu (dự báo theo tầm, so theo âm lịch, cập nhật mỗi tuần, chọn quy tắc đặt hàng riêng cho hàng mùa vụ), không từ mô hình phức tạp hơn hay dò tham số.
4. **Kỷ luật đánh giá:** tập kiểm định "êm" đã từng chọn nhầm mô hình; luật ghi trước và tập kiểm tra dùng một lần khiến một số quyết định trông "kém" trên test (giữ `ket_hop_v4` thay vì RNN, giữ AI + hiệu chỉnh thay vì AI) nhưng đảm bảo con số báo cáo không bị chọn theo đề thi.
5. **Kết quả âm tính có giá trị:** học sâu không đạt luật trên bộ mô phỏng, cảnh báo lệch không đạt luật ở cả hai bộ, giả thuyết về chi phí đặt bị bác bỏ. Các kết quả này cho biết hệ thống không nên làm gì.

Chương 5 tổng kết các kết quả này thành đề xuất áp dụng cho kho tổng của chuỗi siêu thị.
