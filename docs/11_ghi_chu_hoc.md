# Sổ ghi chú học: kho, điều vận và dữ liệu

Mỗi bước của đồ án là một bài. Mỗi bài có 4 phần: **kiến thức logistics**, **kỹ năng dữ liệu**, **liên hệ với điều vận**, **câu hỏi tự kiểm tra** (cũng là câu hỏi phỏng vấn thực tập hay gặp). Ví dụ lấy từ chính dữ liệu dự án (dữ liệu mô phỏng).

Cách dùng: đọc bài sau khi bước đó xong, tự trả lời câu hỏi trước khi mở phần gợi ý. Chỗ nào chưa hiểu thì đánh dấu ❓ ngay cạnh để hỏi lại.

---

## Bài 1. Làm sạch dữ liệu = đối soát tồn kho

**Kiến thức logistics**
- **Đẳng thức kho:** tồn cuối = tồn đầu + nhập − xuất. Đây là nguyên tắc kế toán kho cơ bản, cũng là cách kiểm kê phát hiện chênh lệch.
- Trong dự án, khi ô `qty_out` bị thiếu hoặc nhập sai (gấp 10, gấp 100 lần), ta suy ngược lại: xuất = tồn đầu + nhập − tồn cuối. Sửa được 687 dòng, đối chiếu đáp án không sai dòng nào.
- **Hết hàng ≠ hết nhu cầu.** Ngày tồn về 0, khách vẫn muốn mua nhưng kho không có để xuất. Số xuất ngày đó thấp hơn nhu cầu thật, gọi là nhu cầu bị che (demand censoring). Có 4.225 dòng như vậy (3,19%).

**Kỹ năng dữ liệu:** phát hiện dòng trùng; phân biệt **lỗi nhập liệu** (lệch đẳng thức kho) với **đột biến thật** (bão, sale vẫn khớp đẳng thức). Không xóa số lớn chỉ vì nó lớn.

**Liên hệ điều vận:** số xuất kho là cơ sở để lên kế hoạch xe. Nếu dữ liệu có dòng nhập sai gấp 100 lần mà không sửa, kế hoạch xe ngày đó sẽ sai hoàn toàn.

**Câu hỏi tự kiểm tra**
1. Tồn đầu 120, nhập 50, tồn cuối 40. Xuất bao nhiêu?
2. Vì sao không được coi số bán ngày hết hàng là nhu cầu?
3. Một ngày xuất gấp 8 lần bình thường. Làm sao biết đó là lỗi nhập hay đơn lớn thật?

<details><summary>Gợi ý</summary>

1. 120 + 50 − 40 = 130.
2. Vì khách vẫn muốn mua nhưng không có hàng. Dùng số đó để dự báo sẽ dự báo thấp, rồi lại hết hàng tiếp: một vòng luẩn quẩn.
3. Kiểm tra đẳng thức kho. Nếu tồn cuối cũng giảm tương ứng thì hàng đã thật sự ra khỏi kho, đó là đơn lớn thật. Nếu tồn không đổi thì là lỗi nhập. Sau đó hỏi thêm bộ phận bán hàng.
</details>

---

## Bài 2. Đặc trưng = những gì làm nhu cầu thay đổi (demand drivers)

**Kiến thức logistics:** nhu cầu tăng giảm có lý do: thứ trong tuần, mùa, ngày lễ, khuyến mãi, sale, bão, dịch bệnh. Người lập kế hoạch giỏi là người biết **lý do** chứ không chỉ nhìn con số.

**Kỹ năng dữ liệu**
- Biến lịch thành cột số 0/1, ví dụ `sk_tet = 1` nếu hôm đó nằm trong cửa sổ 28 ngày trước Tết đến 7 ngày sau.
- **Giá trị trễ (lag):** `lag_7` = số bán cùng thứ tuần trước.
- **Không được nhìn trước tương lai (rò rỉ dữ liệu).** Phân loại ABC/XYZ trong `sku_master` tính trên cả 36 tháng, tức có dùng cả dữ liệu tương lai. Tính lại trên giai đoạn huấn luyện thì 8 SKU đổi nhóm ABC.

**Liên hệ điều vận:** điều vận cũng dùng "demand drivers": thấy sắp tới Tết hay sale 11.11 là biết phải đặt thuê xe sớm.

**Câu hỏi tự kiểm tra**
1. Kể 5 yếu tố làm nhu cầu một mặt hàng thay đổi.
2. Vì sao đơn B2B đột biến không được dùng làm biến dự báo?
3. "Rò rỉ dữ liệu" là gì? Cho một ví dụ.

<details><summary>Gợi ý</summary>

1. Thứ trong tuần, mùa, ngày lễ, khuyến mãi, thời tiết/bão, dịch bệnh, giá, đối thủ hết hàng...
2. Vì không biết trước được. Mô hình chỉ được dùng thông tin có sẵn tại lúc dự báo.
3. Dùng thông tin tương lai để dự báo quá khứ, khiến kết quả đẹp giả tạo. Ví dụ: phân loại ABC tính trên cả giai đoạn test.
</details>

---

## Bài 3. Phân tích khám phá: nhìn dữ liệu trước khi chạy mô hình

**Kiến thức logistics**
- **Chu kỳ tuần:** thứ Bảy bán 1,16 lần mức trung bình, Chủ nhật chỉ 0,53 lần.
- **Mùa vụ:** đồ chơi mùa Thu 3,75 lần (Trung thu), kem mùa Hạ 1,96 lần.
- **Ma trận ABC × XYZ:** A = giá trị cao, X = ổn định. Nhóm A-Z (6 SKU) vừa đắt vừa khó đoán, là nơi cần tập trung nhất.
- **Khuyến mãi** làm bán tăng trung vị 60% (khi so trong cùng tháng).

**Kỹ năng dữ liệu**
- Đọc biểu đồ chuỗi thời gian, tách xu hướng và mùa vụ.
- **Nhiễu chéo (confounding):** so khuyến mãi với mọi ngày khác thì 11 SKU trông như "khuyến mãi làm giảm bán", vì hàng thời vụ được khuyến mãi lúc trái mùa. So trong cùng tháng thì hết hiện tượng này. Bài học: so sánh phải "cùng điều kiện".

**Liên hệ điều vận:** chu kỳ tuần nói thẳng ngày nào cần nhiều xe. Chủ nhật chỉ cần khoảng một nửa số xe so với ngày thường. Mùa vụ cho biết tháng nào cần thuê thêm xe hoặc tăng ca.

**Câu hỏi tự kiểm tra**
1. Nhóm A-X và A-Z, nhóm nào nên ưu tiên giữ tồn an toàn cao hơn? Vì sao?
2. Nếu ngày thường cần 10 chuyến, Chủ nhật cần khoảng bao nhiêu?
3. Vì sao không thể kết luận "khuyến mãi làm giảm bán" từ phép so sánh ban đầu?

<details><summary>Gợi ý</summary>

1. A-Z: giá trị cao mà nhu cầu biến động mạnh, sai một lần là thiệt nhiều. Nhưng tồn an toàn cũng tốn tiền, nên cần dự báo tốt để không giữ thừa.
2. Khoảng 5 chuyến (0,53 lần).
3. Vì hai nhóm ngày khác nhau cả về mùa, không chỉ khác ở khuyến mãi.
</details>

---

## Bài 4. Đánh giá dự báo: chấm điểm công bằng

**Kiến thức logistics**
- **Tầm dự báo (horizon):** dự báo trước 28 ngày, vì lead time dài nhất là 15 ngày cộng thêm thời gian xử lý đơn. Dự báo chỉ có ích nếu đủ xa để kịp đặt hàng và xếp xe.
- **Bão chỉ biết trước 3–5 ngày.** Nên mô hình dự báo 28 ngày không được "biết" bão. Ngoài đời, khi có cảnh báo bão, người điều vận phải điều chỉnh tay.

**Kỹ năng dữ liệu**
- **Chia theo thời gian, kiểm thử cuốn chiếu (backtest):** đứng ở ngày 30/9/2025 dự báo 28 ngày tới, rồi lùi mốc, lặp 13 lần. Không xáo trộn ngẫu nhiên như các bài toán khác.
- **WMAPE** = tổng sai số / tổng nhu cầu thật. Dùng thay MAPE vì MAPE "nổ" khi nhu cầu gần 0.
- **Bias:** dự báo thừa hay thiếu. Thiếu thì hết hàng, thừa thì tồn kho và xe chạy rỗng.
- **Mô hình mốc:** Seasonal Naive (lặp lại tuần trước) sai 77%; nhóm ổn định X sai 48%, nhóm mùa vụ Z sai 164%. Mô hình AI phải thắng con số này mới có giá trị.

**Liên hệ điều vận:** dự báo thừa 11% (Bias −11%) nghĩa là đặt xe thừa khoảng 1/10, tốn tiền. Dự báo thiếu thì thiếu xe, giao trễ.

**Câu hỏi tự kiểm tra**
1. Vì sao không chia dữ liệu ngẫu nhiên như các bài toán khác?
2. Thực tế bán 100, 0, 50; dự báo 80, 10, 60. Tính WMAPE.
3. Dự báo thiếu và dự báo thừa, cái nào nguy hiểm hơn cho kho? Cho điều vận?

<details><summary>Gợi ý</summary>

1. Vì ngoài đời không bao giờ có dữ liệu tương lai để học. Chia ngẫu nhiên khiến mô hình "nhìn trộm" tương lai.
2. Sai số tuyệt đối: 20 + 10 + 10 = 40; tổng thực tế 150; WMAPE = 40/150 ≈ 27%.
3. Tùy mặt hàng. Thiếu thì mất doanh thu và khách; thừa thì tốn tồn kho, tốn xe. Hàng giá trị cao, dễ hỏng thì sợ thừa; hàng thiết yếu (mì, nước khi bão) thì sợ thiếu.
</details>

---

## Bài 5. Mô hình mốc: ETS, ARIMA, Croston

**Kiến thức logistics**
- **Mô hình mốc (baseline)** là cách dự báo đơn giản mà người lập kế hoạch có thể làm bằng Excel. Mô hình AI chỉ có giá trị khi thắng được mốc này. Nhà tuyển dụng thường hỏi: "AI tốt hơn cách cũ bao nhiêu?"
- **Hàng bán rời rạc** (nhiều ngày không bán): phụ tùng, thiết bị theo mùa. Croston tách làm hai câu hỏi: "bao lâu bán một lần" và "mỗi lần bán bao nhiêu".

**5 cách dự báo đơn giản, hiểu bằng lời**
| Mô hình | Ý tưởng | Giống việc gì ngoài đời |
|---|---|---|
| Seasonal Naive | Tuần sau giống hệt tuần này | "Thứ Hai tuần trước xuất 50 thùng thì thứ Hai này cũng 50" |
| Trung bình trượt 28 ngày | Lấy trung bình 4 tuần gần nhất | Cách nhiều kho tính "bình quân ngày" để đặt hàng |
| ETS | Trung bình nhưng ngày gần đây quan trọng hơn, có tính xu hướng và chu kỳ tuần | Người lập kế hoạch "nhớ" số gần đây rõ hơn số cũ |
| ARIMA | Dự báo dựa trên mối liên hệ giữa hôm nay và các ngày trước đó | Phức tạp, khó giải thích bằng lời |
| Croston / TSB | Dự báo riêng tần suất bán và lượng bán | Hàng phụ tùng, hàng ít người mua |

**Kết quả (tập test) và bài học**
- **Đơn giản nhất lại thắng:** trung bình 28 ngày sai 64%, tốt hơn Seasonal Naive (77%) 17%. Chép nguyên một tuần là chép cả "nhiễu" của tuần đó; lấy trung bình thì nhiễu triệt tiêu bớt.
- **Phức tạp chưa chắc đáng:** ARIMA chạy chậm gấp khoảng 20 lần nhưng trên nhóm A chỉ ngang Croston (49,3% so với 49,2%). Trong công việc, mô hình chậm, khó giải thích mà không tốt hơn thì không nên dùng.
- **ETS dự báo thừa 17%:** sau đỉnh Tết, nó tưởng xu hướng tăng còn tiếp tục. Thừa 17% nghĩa là đặt dư hàng, đặt dư xe.
- **Chọn mô hình theo tên gọi là sai:** Croston "dành cho hàng rời rạc" nhưng không thắng ở nhóm rời rạc. 9 SKU đó thực ra là hàng **thời vụ** (máy sưởi chỉ bán mùa đông), không phải hàng rời rạc ngẫu nhiên. Phải nhìn dữ liệu (Bài 3) trước khi chọn công cụ.
- **Điểm yếu chung:** hàng mùa vụ (nhóm Z) mô hình tốt nhất vẫn sai 127%, vì không mô hình nào biết sắp tới Tết. Bước sau (Prophet, LightGBM) đưa lịch lễ vào để sửa chỗ này.

**Kỹ năng dữ liệu:** so sánh **công bằng**: ARIMA chỉ chạy 31 SKU nhóm A thì chỉ được so với các mô hình khác **trên đúng 31 SKU đó** (cột WMAPE_A), không so với sai số của cả 121 SKU.

**Liên hệ điều vận:** khi lên kế hoạch xe theo dự báo, một dự báo thừa có hệ thống (như ETS) làm thuê thừa xe, xe chạy không đầy. Một dự báo "đi ngang" (như trung bình 28 ngày) an toàn ngày thường nhưng sẽ **thiếu xe trước Tết**, vì nó không biết Tết sắp đến. Người điều vận phải tự cộng thêm. Đó là lý do cần mô hình biết lịch.

**Câu hỏi tự kiểm tra**
1. Vì sao không chọn ARIMA dù nó "xịn" hơn trung bình trượt?
2. Một kho dùng trung bình 28 ngày để đặt xe. Tuần trước Tết sẽ xảy ra chuyện gì?
3. Muốn biết AI có đáng dùng không, phải so với mô hình nào: Seasonal Naive hay trung bình 28 ngày?

<details><summary>Gợi ý</summary>

1. Vì không tốt hơn (ngang Croston trên nhóm A), lại chậm gấp khoảng 20 lần và khó giải thích. Nguyên tắc: hai mô hình ngang nhau thì chọn cái đơn giản.
2. Thiếu xe và thiếu hàng. Trung bình 28 ngày chỉ nhìn quá khứ, không biết nhu cầu sắp tăng mạnh (h01: tổng xuất trước Tết lên gần gấp 3 ngày thường).
3. So với mô hình mốc **tốt nhất** (trung bình 28 ngày, 0,640). Thắng mô hình yếu nhất thì chưa chứng minh được gì.
</details>

---

## Bài 6. Prophet: mô hình biết lịch

**Kiến thức logistics**
- Nhu cầu hàng tiêu dùng Việt Nam bị chi phối mạnh bởi **lịch**: Tết, Trung thu theo âm lịch (đổi ngày mỗi năm), các ngày lễ, sale 11.11, khuyến mãi. Người lập kế hoạch giỏi luôn có **lịch sự kiện** trên bàn.
- Phân biệt hai loại sự kiện:
  - **Biết trước:** lịch lễ, lịch sale, lịch khuyến mãi, lịch thi đấu bóng đá. Đưa được vào dự báo.
  - **Không biết trước** (hoặc chỉ biết trước vài ngày): bão, nắng nóng, dịch bệnh, tin đồn tăng giá. Không đưa vào dự báo 28 ngày; khi có cảnh báo thì người điều vận tự điều chỉnh.

**Prophet hiểu bằng lời:** Prophet tách nhu cầu thành các phần cộng lại:
nhu cầu = **xu hướng** + **mùa vụ năm** + **chu kỳ tuần** + **hiệu ứng ngày lễ** + **hiệu ứng khuyến mãi** + nhiễu.
Mình đưa cho nó lịch lễ (ví dụ Tết bắt đầu tăng từ 28 ngày trước), nó tự học mỗi SKU tăng bao nhiêu vào dịp đó.

**Kết quả và bài học**
- Prophet sai **45%**, so với 64% của trung bình trượt (mô hình mốc tốt nhất): giảm 29%. So với Seasonal Naive: giảm 41%. Đạt tiêu chí "giảm ít nhất 20%".
- **Thắng ở đâu:** hàng mùa vụ (nhóm Z) sai 127% → 64%, giảm một nửa. Mốc Tết 2026: 45% so với 148%.
- **Không thắng ở đâu:** tháng 5–6 (không có lễ lớn) thì ngang mô hình mốc. Nghĩa là: **AI có giá trị nhất ở những lúc có sự kiện**, còn lúc bình thường thì cách đơn giản cũng đủ.
- **Cảnh báo trung thực:** dữ liệu mô phỏng được tạo bằng **đúng** lịch lễ mà Prophet dùng, giống như học sinh được biết trước đề cương sát đề thi. Ngoài đời phải tự đoán "Tết bắt đầu tăng từ mấy tuần trước", nên kết quả thật sẽ kém hơn. Nói được điều này khi bảo vệ là điểm cộng, không phải điểm trừ.

**Kỹ năng dữ liệu**
- **Chọn tham số trên validation, chấm trên test:** thử 2 kiểu mùa vụ (cộng và nhân), chọn kiểu tốt hơn **trên validation** (cộng: 0,434 so với nhân: 0,535), rồi mới chạy test. Không được nhìn kết quả test để chọn, vì như thế là "gian lận" ngầm.
- **Kiểm tra từng mốc, không chỉ con số trung bình:** Prophet thắng 11/13 mốc, nên kết quả ổn định chứ không phải nhờ may ở 1–2 mốc.
- Kỹ thuật máy tính: chạy song song bị giới hạn bởi **RAM** (máy 7,6 GB chỉ chạy được 4 tiến trình Prophet cùng lúc); máy ngủ giữa chừng thì chương trình treo.

**Liên hệ điều vận:** dự báo theo tuần của Prophet chỉ sai 26%. Đủ tốt để **lên kế hoạch thuê xe theo tuần** trước mùa cao điểm: tuần trước Tết, dự báo cho biết cần tăng khoảng bao nhiêu chuyến, để đặt thuê xe ngoài sớm (giá rẻ hơn, chắc có xe hơn). Mô hình mốc (trung bình 28 ngày) sẽ không báo trước được đỉnh này.

**Câu hỏi tự kiểm tra**
1. Vì sao không đưa bão vào Prophet, dù bão làm nhu cầu mì gói tăng mạnh?
2. Prophet chỉ ngang mô hình mốc trong tháng 5–6. Điều đó có làm Prophet "kém" không?
3. Nếu hội đồng hỏi "Có chắc AI giảm sai số 41% ở kho thật không?", bạn trả lời thế nào?

<details><summary>Gợi ý</summary>

1. Vì dự báo cho 28 ngày tới, mà bão chỉ được cảnh báo trước 3–5 ngày. Đưa vào là "nhìn trộm tương lai", kết quả đẹp giả tạo. Khi có cảnh báo bão, người lập kế hoạch điều chỉnh tay.
2. Không. Lúc không có sự kiện, nhu cầu ổn định, cách đơn giản đã đủ tốt; Prophet không làm tệ hơn. Giá trị của nó nằm ở mùa cao điểm, nơi sai lầm tốn kém nhất.
3. Không chắc con số 41%: dữ liệu là mô phỏng, và mô hình được dùng đúng lịch lễ mà dữ liệu được tạo ra. Điều chắc chắn hơn là **xu hướng**: mô hình biết lịch lễ cải thiện mạnh ở hàng mùa vụ. Muốn có con số thật phải chạy thử trên dữ liệu kho thật, quy trình đã sẵn sàng cho việc đó.
</details>
