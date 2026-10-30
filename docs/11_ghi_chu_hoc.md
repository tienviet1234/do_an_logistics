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

**Kỹ năng dữ liệu:** so sánh **công bằng**: ARIMA chỉ chạy các SKU nhóm A (28 mã theo giá thị trường, 31 với giá mô phỏng cũ) thì chỉ được so với các mô hình khác **trên đúng các SKU đó** (cột WMAPE_A), không so với sai số của cả 121 SKU.

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

---

## Bài 7. LightGBM: chính xác hơn chưa chắc tốt hơn

**Kiến thức logistics**
- **Sai số và độ lệch (Bias) là hai chuyện khác nhau.** Sai số cho biết trung bình đoán lệch bao nhiêu; Bias cho biết lệch **về phía nào**. Một mô hình sai ít nhưng luôn đoán thiếu sẽ làm kho **hết hàng lặp đi lặp lại**.
- **Chi phí sai lệch không đối xứng:** trước Tết, thiếu hàng là mất doanh thu mùa cao điểm và mất khách; thừa một ít thì sau Tết vẫn bán dần được (trừ hàng chỉ bán dịp Tết). Vì vậy với hàng mùa vụ, **thà thừa nhẹ còn hơn thiếu**.

**LightGBM hiểu bằng lời:** thay vì mỗi SKU một mô hình (như Prophet), LightGBM học **một mô hình chung cho cả 121 SKU** bằng cách xây hàng trăm "cây quyết định" nhỏ, mỗi cây sửa lỗi của các cây trước. Ví dụ một nhánh: "nếu là hàng loại Tết **và** còn dưới 20 ngày đến Tết **và** tuần trước bán nhiều → dự báo cao". Ưu điểm: các SKU giống nhau học hỏi lẫn nhau; chạy rất nhanh (3 giây/mốc so với 67 giây của Prophet).

**Kết quả và bài học**
- Theo ngày, LightGBM **tốt nhất**: sai 40% (Prophet 45%, trung bình trượt 64%), thắng Prophet 12/13 mốc. Hàng ổn định (nhóm X) chỉ sai 31%.
- Nhưng **đoán thiếu 11,7%**, dồn vào hàng mùa vụ: nhóm Z thiếu 40%, đúng các mốc **trước Tết và trước Trung thu**, lúc kho cần hàng nhất.
- Nguyên nhân: mô hình dựa nhiều vào "số bán cùng ngày năm ngoái" (lag_364), nhưng **Tết âm lịch lệch vài tuần mỗi năm**, nên cùng ngày năm ngoái có khi là trước Tết, có khi là sau Tết. Lại mới học được 2 mùa Tết.
- **Bài học:** đừng chọn mô hình chỉ theo một con số. Phải xem cả Bias, xem theo nhóm hàng và theo thời điểm.
- **Độ quan trọng đặc trưng** cho biết mô hình "dựa vào gì": mã SKU (36%, mỗi mặt hàng có mức bán riêng), số bán gần đây, số bán năm trước, loại mùa vụ, số ngày đến Tết. Khuyến mãi chỉ hạng 13 vì chỉ chiếm 8% số ngày, dù mỗi lần khuyến mãi làm bán tăng 60%. "Quan trọng" ở đây là **tổng đóng góp**, không phải **độ mạnh mỗi lần**.

**Kỹ năng dữ liệu**
- **Dự báo nhiều ngày tới mà không nhìn trộm:** chỉ dùng số bán cách ít nhất 28 ngày (lag ≥ 28). Muốn dự báo ngày thứ 28 thì không được dùng số bán hôm qua, vì lúc dự báo chưa có số đó.
- **Hàm mất mát (tweedie)** phù hợp dữ liệu nhiều số 0 và số đếm; chọn trên validation (0,351 so với 0,420 của hàm thường).

**Liên hệ điều vận:** nếu dùng LightGBM để lên kế hoạch xe, tuần trước Tết sẽ **thiếu xe khoảng 40% cho hàng mùa vụ**, đúng lúc thuê xe ngoài khó và đắt nhất. Người điều vận cần biết mô hình của mình "lệch về phía nào, lúc nào" để tự cộng thêm dự phòng.

**Câu hỏi tự kiểm tra**
1. Mô hình A sai 40% nhưng luôn đoán thiếu; mô hình B sai 45% nhưng không lệch về phía nào. Kho bán hàng Tết nên dùng mô hình nào? Vì sao?
2. Vì sao "số bán cùng ngày năm ngoái" dự báo tốt cho Noel (25/12) nhưng kém cho Tết?
3. Khuyến mãi làm bán tăng 60% mà chỉ xếp hạng 13 về độ quan trọng. Có mâu thuẫn không?

<details><summary>Gợi ý</summary>

1. Với hàng Tết, B an toàn hơn vì A đoán thiếu đúng lúc cao điểm, dẫn tới hết hàng. Tốt nhất là kết hợp: dùng A cho hàng ổn định, B (hoặc trung bình A và B) cho hàng mùa vụ, và quyết định trên tập validation.
2. Noel luôn là 25/12 dương lịch; Tết theo âm lịch nên ngày dương lịch đổi mỗi năm (10/02/2024, 29/01/2025, 17/02/2026).
3. Không mâu thuẫn. Độ quan trọng đo tổng đóng góp trên mọi dòng dữ liệu; khuyến mãi tác động mạnh nhưng hiếm (8% số ngày).
</details>

---

## Bài 8. Chọn mô hình: "đề luyện" phải giống "đề thi"

**Kiến thức logistics:** khi một kho chọn phần mềm hay phương pháp dự báo, họ thường chạy thử vài tháng. Nếu chỉ chạy thử vào **mùa thấp điểm**, phương pháp nào trông cũng ổn; đến Tết mới lộ vấn đề. Muốn đánh giá đúng, phải thử **qua ít nhất một mùa cao điểm**.

**Chuyện đã xảy ra trong dự án**
- **Vòng 1:** dùng tập validation tháng 4–9/2025 (không có Tết) để chọn. Luật chọn ra **LightGBM**, vì trong giai đoạn êm nó chính xác nhất. Trên test, LightGBM thiếu hàng 40% ở nhóm mùa vụ, dồn vào trước Tết và Trung thu. Lựa chọn **sai**.
- Không được nhìn test rồi đổi lựa chọn, vì như vậy là xem đề thi rồi mới chọn cách làm bài.
- **Vòng 2:** chỉ sửa đúng một chỗ: tập validation mới **cùng mùa với test nhưng sớm một năm** (có Tết 2025). Giữ nguyên mô hình và luật chọn, và **ghi luật vào báo cáo trước khi chạy**.
- Kết quả: vòng 2 thấy ngay LightGBM thiếu hàng (+13%, sát mức +12% trên test) và chọn **kết hợp theo nhóm**: hàng ổn định dùng gần hết LightGBM, hàng mùa vụ lấy 40% từ Prophet. Trên test, đây là phương án tốt nhất: sai 37,6%, theo tuần chỉ 23,5%.

**Kỹ năng dữ liệu**
- **Kết hợp mô hình (ensemble):** trung bình có trọng số của nhiều mô hình thường tốt hơn từng mô hình, vì lỗi của chúng bù trừ nhau. Ở đây LightGBM đoán thiếu, Prophet đoán thừa nhẹ.
- **Trọng số theo nhóm hàng:** mỗi nhóm dùng tỷ lệ khác nhau, dò trên validation.
- **Ghi trước luật chơi:** viết luật chọn ra giấy (vào báo cáo) **trước khi** có kết quả. Đây là cách các nhà khoa học tránh tự lừa mình.

**Liên hệ điều vận:** tương tự khi đánh giá một nhà xe hay đối tác vận tải: chạy thử vào tháng thấp điểm thì ai cũng đúng giờ; phải xem họ làm thế nào trong **tuần trước Tết** mới biết có đáng tin không.

**Câu hỏi tự kiểm tra**
1. Vì sao vòng 1 chọn sai dù luật chọn hoàn toàn hợp lý?
2. Sau khi thấy kết quả test vòng 1, nếu đổi luôn sang "trung bình hai mô hình" thì có gì sai?
3. Mô hình được chọn vẫn thiếu hàng 6,3%, vượt ngưỡng ±5%. Có nên chỉnh trọng số cho tới khi Bias trên test dưới 5% không?

<details><summary>Gợi ý</summary>

1. Vì dữ liệu dùng để chọn (mùa êm) khác dữ liệu dùng mô hình thật (có Tết). Luật đúng nhưng "đề luyện" sai.
2. Đó là chọn theo đề thi: kết quả test không còn khách quan, hội đồng sẽ không tin con số.
3. Không. Mọi điều chỉnh phải ước lượng trên validation (ví dụ validation vòng 2 cho thấy thiếu 8,1%), rồi mới kiểm tra trên test. Chỉnh theo test là gian lận ngầm.
</details>

---

## Bài 9. Luồng hệ thống và cơ sở dữ liệu

**Kiến thức logistics**
- **Luồng nghiệp vụ** trả lời "ai làm gì, theo thứ tự nào": kho ghi nhận → bán hàng gửi lịch → hệ thống dự báo, tính điểm đặt hàng → người lập kế hoạch duyệt → mua hàng đặt, điều vận lên xe. Hệ thống không thay con người; nó **đề xuất**, con người **quyết định**.
- **Luồng dữ liệu** trả lời "dữ liệu đi qua những bước nào": thô → sạch → đặc trưng → mô hình → dự báo → tồn kho → dashboard.
- Trong doanh nghiệp, dữ liệu kho nằm trong **WMS/ERP**, bản chất là một cơ sở dữ liệu. Dự án của bạn làm một bản thu nhỏ của điều đó.

**Kỹ năng dữ liệu**
- **Bảng danh mục và bảng giao dịch:** danh mục (`dm_sku`) ít thay đổi; giao dịch (`giao_dich_sach`) thêm mỗi ngày. Giao dịch chỉ lưu `ma_sku`, muốn biết tên hàng thì **nối (JOIN)** sang danh mục, không chép tên vào từng dòng.
- **Khóa chính:** mỗi (ngày, SKU) chỉ một dòng, nên không thể trùng.
- **Khóa ngoại:** mã hàng trong giao dịch phải có trong danh mục. Thử ghi `SKU999` thì bị từ chối.
- **Ràng buộc CHECK:** lượng xuất không được âm, dự báo không được cho ngày trước mốc.
- **Vùng tạm (staging):** `giao_dich_tho` nhận nguyên văn file kho, kể cả lỗi; chỉ dữ liệu đã làm sạch mới vào `giao_dich_sach`. Nhờ vậy luôn truy ngược được "dòng này ban đầu ra sao" (`nhat_ky_sua_loi`).
- **Đối soát bằng SQL:** đẳng thức kho (tồn cuối = tồn đầu + nhập − xuất) kiểm tra được bằng một câu lệnh; kết quả 0 dòng lệch.

**Liên hệ điều vận:** người điều vận hằng ngày tra cứu dữ liệu: đơn nào cần giao, hàng nào sắp về, xe nào trống. Biết đọc cơ sở dữ liệu và viết vài câu SQL đơn giản (SELECT, WHERE, JOIN, GROUP BY) là lợi thế lớn khi xin thực tập, vì phần lớn ứng viên chỉ biết Excel.

**Câu hỏi tự kiểm tra**
1. Vì sao không lưu tên hàng vào từng dòng giao dịch mà phải nối sang bảng danh mục?
2. Nếu file kho mới có mã hàng chưa có trong danh mục, cơ sở dữ liệu sẽ làm gì? Đó là tốt hay xấu?
3. Hội đồng hỏi: "Database để làm gì, sao không để file CSV?" Bạn trả lời thế nào?

<details><summary>Gợi ý</summary>

1. Để tên hàng chỉ nằm một chỗ: đổi tên thì sửa một dòng ở danh mục, không phải sửa 132.616 dòng giao dịch, và không bao giờ có hai tên khác nhau cho cùng một mã.
2. Từ chối ghi (vi phạm khóa ngoại). Đó là điều tốt: buộc phải thêm mã hàng vào danh mục trước (kèm giá, lead time, MOQ), tránh dữ liệu "mồ côi" làm sai báo cáo.
3. Database **chặn dữ liệu sai ngay khi ghi** (khóa chính, khóa ngoại, ràng buộc), cho nhiều người và nhiều chương trình dùng chung một nguồn, truy vấn nhanh bằng SQL, và ghi nhật ký mỗi lần nạp. File CSV không làm được những điều này; ai cũng có thể sửa tay làm sai lệch.
</details>

---

## Bài 10. Từ dự báo đến quyết định đặt hàng: SS, ROP, EOQ và mô phỏng

**Kiến thức logistics**
- **Điểm đặt hàng (ROP)** = nhu cầu dự báo trong thời gian chờ hàng + **tồn kho an toàn (SS)**. Mỗi ngày: nếu "tồn hiện có + hàng đang về" ≤ ROP thì đặt.
- **Tồn kho an toàn** bù cho hai thứ không chắc: dự báo sai và hàng về trễ. SS = z × √(σ² + d² × σ_LT²). Dự báo càng chính xác (σ nhỏ) thì SS càng nhỏ: đây là chỗ AI tiết kiệm tiền.
- **EOQ** cân bằng chi phí đặt hàng (đặt nhiều lần thì tốn) và chi phí lưu kho (đặt nhiều một lúc thì tốn). Giả định **nhu cầu đều quanh năm**, nên **không hợp với hàng thời vụ**.
- **Fill Rate** (tỷ lệ đáp ứng) = phần nhu cầu được phục vụ ngay từ kho.
- **Chi phí liên quan** = đặt hàng + lưu kho + **lợi nhuận mất do thiếu hàng**. Chỉ nhìn chi phí lưu kho thì luôn thấy "giữ ít hàng là tốt", nhưng thiếu hàng cũng là chi phí.

**Kết quả (12 tháng mô phỏng, mức phục vụ 95%)**
- Cùng công thức, chỉ đổi dự báo: AI (có hiệu chỉnh lệch) đáp ứng **95,9%** so với 88,8% của dự báo mốc; lợi nhuận mất giảm gần một nửa (−47%); tồn kho tăng nhẹ (+4%). **Chi phí liên quan giảm 28%.**
- Với hàng ổn định (nhóm X), AI thắng cả "hiện trạng" (người lập kế hoạch biết trước nhu cầu): đáp ứng cao hơn mà tồn **ít hơn 28%**.
- Với 5 mặt hàng **chỉ bán dịp lễ** (cây thông Noel, đồ Halloween...), EOQ thất bại: hàng về sau mùa, vừa thiếu trong mùa vừa tồn đến cuối năm. Thử hai cách đặt khác trên validation nhưng không tốt hơn, nên đây là **hạn chế** và **hướng phát triển** (hàng thời vụ nên đặt một lần trước mùa).

**Kỹ năng dữ liệu**
- **Mô phỏng (simulation):** chạy lại 12 tháng, từng ngày, cho từng chính sách, với **cùng nhu cầu, cùng thời gian giao hàng**. Chỉ như vậy mới so sánh công bằng.
- **Nhu cầu thật (đáp án)** chỉ dùng để chấm, không cho mô hình biết.
- **Hiệu chỉnh lệch:** dự báo thiếu có hệ thống 8% thì nhân dự báo với hệ số ước lượng **trên validation**.
- **Đối thủ quá mạnh:** "hiện trạng" trong dữ liệu biết trước nhu cầu. Thua nó ở tồn kho không có nghĩa là AI kém. Phải nói rõ điều này khi trình bày.

**Liên hệ điều vận:** EOQ nhỏ nghĩa là **nhập hàng nhiều lần hơn** (3.035 lần so với 1.910 lần của hiện trạng). Với kho, đó là thêm chuyến xe nhập, thêm lượt nhận hàng, xếp dỡ. Chi phí đặt hàng S trong công thức phải phản ánh đúng chi phí một chuyến xe nhận hàng. Đây là chỗ người điều vận góp ý được cho người lập kế hoạch.

**Câu hỏi tự kiểm tra**
1. Vì sao dự báo chính xác hơn lại giúp giảm tồn kho an toàn?
2. Vì sao EOQ không hợp với cây thông Noel?
3. Hội đồng hỏi: "Chính sách AI tồn kho nhiều hơn hiện trạng 37%, vậy AI có tốt không?" Bạn trả lời thế nào?

<details><summary>Gợi ý</summary>

1. SS tỷ lệ với độ lệch chuẩn của sai số dự báo (σ). Sai ít thì cần ít hàng dự phòng hơn mà vẫn giữ được cùng mức phục vụ.
2. EOQ giả định nhu cầu đều. Cây thông chỉ bán khoảng 3 tuần; đặt theo EOQ khi dự báo vọt lên thì hàng về sau Noel, tồn đến năm sau.
3. "Hiện trạng" trong dữ liệu mô phỏng biết trước nhu cầu kỳ vọng, ngoài đời không có. So với cách làm thực tế (công thức + dự báo đơn giản), AI giảm 28% chi phí liên quan và đáp ứng thêm 7,1 điểm. Ngay cả với đối thủ biết trước, AI đáp ứng tốt hơn, số ngày thiếu hàng ít hơn một nửa, tổng chi phí chỉ cao hơn 3,3%; với hàng ổn định AI còn tồn ít hơn 28%. Phần tồn cao đến từ 5 mặt hàng chỉ bán dịp lễ, đã chỉ rõ nguyên nhân và hướng khắc phục.
</details>


## Bài 11. Dashboard: người lập kế hoạch nhìn gì mỗi sáng

**Kiến thức logistics**
- **Quản lý theo ngoại lệ (management by exception):** kho 121 SKU không ai xem hết từng mã mỗi ngày. Màn hình cảnh báo chỉ đưa ra những mã **cần làm gì đó**: hết hàng, cần đặt hôm nay, tồn thấp nhưng hàng đang về. Ngày 09/02/2026 (trước Tết): 44 mã cần chú ý, 77 mã không cần nhìn.
- **Tồn thực khác vị thế tồn kho.** Tồn thực = hàng đang nằm trong kho. **Vị thế tồn kho** (inventory position) = tồn thực + hàng đang về (đã đặt, chưa nhận). Quy tắc ROP so **vị thế** với ROP, không so tồn thực. Ví dụ: hạt điều SKU060 ngày 09/02 tồn 897, ROP 6.960, nhưng đang về 7.279 → 897 + 7.279 > 6.960 nên **không đặt thêm**. Nếu so tồn thực, người lập kế hoạch sẽ đặt trùng, tồn dư sau Tết.
- **Số ngày đủ bán (days of cover)** = tồn / nhu cầu bình quân 1 ngày. Đem so với **lead time**: sữa tươi Vinamilk SKU009 ngày 09/02 chỉ đủ bán 1,3 ngày mà lead time 3 ngày; đủ bán ít hơn lead time thì gần như chắc chắn sẽ thiếu trước khi hàng về, phải gọi nhà cung cấp giao gấp.
- **Biểu đồ "răng cưa"**: tồn giảm dần theo bán, chạm ROP thì đặt, hàng về thì vọt lên. Răng cưa chạm đáy (tồn = 0) là ngày hết hàng.

**Kỹ năng dữ liệu**
- **Dashboard chỉ đọc, không tính lại:** mọi số lấy từ CSDL mà các bước trước đã ghi, nên dashboard luôn khớp báo cáo. Muốn đổi số thì chạy lại `ton_kho.py`, không sửa trong dashboard.
- **Tính lại đại lượng không lưu bằng phép bảo toàn:** hàng đang về không có trong CSDL, nhưng hàng đang về = đầu kỳ + tổng đã đặt − tổng đã nhận. Kiểm tra lại: không ngày nào âm, và không SKU nào "dưới ROP mà không đặt" khi vị thế ≤ ROP.
- **Giả lập "hôm nay":** chọn một ngày trong năm test để xem hệ thống lúc đó sẽ cảnh báo gì. Đây là **phát lại mô phỏng**, phải nói rõ khi trình bày.
- **Mỗi chỉ số một biểu đồ:** Fill Rate (%) và chi phí (triệu đồng) khác đơn vị, không vẽ chung một trục.

**Liên hệ điều vận:** danh sách "đặt hàng hôm nay" là đầu vào của điều vận: bao nhiêu đơn, của nhà cung cấp nào, khi nào hàng về → bao nhiêu chuyến xe nhận hàng, xếp lịch dock (cửa nhận hàng) ra sao. Cột "hàng đang về" cho biết sắp tới kho phải nhận bao nhiêu.

**Câu hỏi tự kiểm tra**
1. Một SKU tồn thực dưới ROP. Có phải lúc nào cũng phải đặt thêm không?
2. Vì sao dashboard nên đọc kết quả từ CSDL thay vì tự tính lại dự báo và tồn kho?
3. Hội đồng hỏi: "Dashboard này có dùng ngay ở kho thật được không?" Bạn trả lời thế nào?

<details><summary>Gợi ý</summary>

1. Không. Xét vị thế tồn kho (tồn + hàng đang về). Nếu hàng đang về đủ đưa vị thế lên trên ROP thì chỉ theo dõi; đặt thêm là đặt trùng.
2. Một nguồn số duy nhất: báo cáo, biểu đồ và dashboard cùng đọc một chỗ nên không lệch nhau; dashboard mở nhanh và không thể vô tình làm hỏng kết quả (chỉ đọc).
3. Chưa dùng ngay được: đang chạy trên dữ liệu mô phỏng và phát lại một năm đã qua. Để dùng thật cần nạp dữ liệu nhập – xuất – tồn hằng ngày từ WMS/ERP vào cùng các bảng, chạy dự báo định kỳ (ví dụ mỗi tuần), thêm bước người lập kế hoạch duyệt đơn. Cấu trúc CSDL và các bước đã sẵn để thay nguồn dữ liệu.
</details>

## Bài 12. Thử độ nhạy: chính sách có chịu được cú sốc không

**Kiến thức logistics**
- **Thử độ nhạy (sensitivity analysis / stress test):** giữ nguyên mọi thứ, chỉ đổi **một** yếu tố (lead time, chi phí) rồi xem kết quả thay đổi bao nhiêu. Mục đích: biết chính sách **gãy ở đâu** trước khi gặp ngoài đời.
- **Cú sốc tạm thời khác thay đổi lâu dài.** Tắc cảng 3 tuần (hàng về trễ 7 ngày) chỉ làm Fill Rate giảm trung bình 1,5 điểm, vì tồn kho an toàn (SS) hấp thụ được một phần. Nhưng lead time dài thêm chỉ 2 ngày **cả năm** mà công thức vẫn dùng lead time cũ thì Fill Rate giảm 5,1 điểm, chi phí +52%: ví dụ SKU001 (lead time TB 5 ngày), ROP vẫn tính cho 5 ngày chờ trong khi thật ra phải chờ khoảng 7 ngày, nên lần nào cũng dễ thiếu.
- **Tham số phải được cập nhật.** Cập nhật lead time mới vào công thức thì chỉ còn giảm 1,1 điểm. Đây là việc của người điều vận / mua hàng: theo dõi **lead time thực tế** từng nhà cung cấp (ngày đặt → ngày nhận), báo cho người lập kế hoạch khi nó thay đổi.
- **Thời điểm nguy hiểm nhất là trước cao điểm.** Đợt tắc cảng trước Tết (hàng dự kiến về 21/01–10/02/2026) gây thiệt hại lớn nhất: Fill Rate −2,9 điểm, chi phí +24%.
- **Chi phí lưu kho tăng phạt chính sách giữ nhiều hàng.** Khi H +15% (giá điện, kho lạnh), khoảng cách chi phí giữa chính sách AI và hiện trạng giãn từ 3,3% lên 6,7%, vì AI giữ tồn nhiều hơn 37%.

**Kỹ năng dữ liệu**
- **Mỗi kịch bản chỉ đổi 1 yếu tố**, mọi thứ khác (nhu cầu, lead time ngẫu nhiên, dự báo) giống hệt; nếu không, không biết thay đổi do đâu.
- **Không chọn đợt có lợi:** chạy tắc cảng ở **13 thời điểm** khác nhau trong năm, báo cả trung bình lẫn đợt xấu nhất. Chọn đúng 1 đợt là có thể (cố ý hoặc vô tình) chọn đợt làm kết quả đẹp.
- **Kiểm tra kịch bản gốc trước:** chạy lại không đổi gì phải ra đúng kết quả cũ (script tự kiểm tra), để chắc chắn mọi chênh lệch là do cú sốc chứ không do lỗi code.
- **So sánh bằng cả % và tiền:** chi phí của AI tăng nhiều hơn về % (+15% so với +9% của dự báo mốc) nhưng tính bằng tiền thì gần bằng (+1.022 so với +865 triệu đ) và AI vẫn rẻ hơn khoảng 2,5 tỷ. Chỉ nhìn % dễ kết luận sai.

**Liên hệ điều vận:** người điều vận là người **nhìn thấy cú sốc đầu tiên**: xe về trễ, cảng ùn, cước tăng. Kết quả này cho thấy giá trị của việc báo sớm: cùng một lần trễ, nếu người lập kế hoạch biết và cập nhật thì thiệt hại giảm từ −5,1 xuống −1,1 điểm Fill Rate.

**Câu hỏi tự kiểm tra**
1. Vì sao lead time dài thêm 2 ngày cả năm lại nguy hiểm hơn tắc cảng 7 ngày trong 3 tuần?
2. Vì sao phải chạy tắc cảng ở 13 thời điểm mà không chọn một đợt?
3. Hội đồng hỏi: "Nếu tắc cảng thì chính sách AI có còn tốt không?" Bạn trả lời thế nào?

<details><summary>Gợi ý</summary>

1. Tắc cảng chỉ ảnh hưởng một số lô trong 3 tuần, tồn an toàn đủ đỡ phần lớn. Lead time dài ra cả năm làm **mọi** lô đều về trễ hơn mức công thức tính, nên lần nào cũng thiếu; nhưng cập nhật tham số thì gần như hết vấn đề.
2. Kết quả phụ thuộc thời điểm (trước Tết thiệt hại gấp đôi trung bình). Chạy nhiều đợt cho thấy bức tranh đầy đủ và tránh chọn đợt có lợi.
3. "Em đã thử tắc cảng 3 tuần với hàng về trễ 3, 5, 7 ngày, ở 13 thời điểm khác nhau. Fill Rate giảm trung bình 0,5–1,5 điểm, đợt xấu nhất (trước Tết, trễ 7 ngày) giảm 2,9 điểm. Ở cả 13 đợt, chính sách AI + hiệu chỉnh vẫn có chi phí thấp nhất trong các chính sách theo công thức. Điểm cần lưu ý là nếu lead time thay đổi lâu dài thì phải cập nhật vào công thức, nếu không Fill Rate giảm 5 điểm."
</details>

## Bài 13. Trình bày dữ liệu: mỗi biểu đồ trả lời một câu hỏi

**Vì sao làm lại dashboard:** bản đầu đúng số nhưng mỗi trang chỉ có 1 biểu đồ, còn lại là bảng dài và mã kỹ thuật (σ, hệ số hiệu chỉnh…). Người xem không biết dữ liệu nói gì, và thấy số liệu "không thực". Bài học: **đúng số chưa đủ, người xem phải hiểu được**.

**Kiến thức logistics (từ trang Tổng quan, số liệu mô phỏng)**
- **Mùa vụ theo nhóm hàng:** đồ chơi bán gấp ~10 lần vào tháng 9 (Trung thu), đồ trang trí gấp ~5 lần tháng 12 (Noel), quà tặng gấp ~3,5 lần tháng 2 (Tết). Hàng này phải **đặt trước mùa**, không chờ chạm ROP.
- **Thứ trong tuần:** Chủ nhật chỉ bán bằng ~0,53 ngày thường, thứ Bảy cao nhất. Người điều vận dùng điều này để xếp ca, lịch xe nhận/giao.
- **Khuyến mãi:** một nửa số đợt làm bán tăng từ ~58% trở lên. Kho phải nhận lịch khuyến mãi **trước** khi đặt hàng.
- **ABC × XYZ:** 20 mã A-X (17% số mã) chiếm ~67% giá trị xuất (theo giá thị trường 24/10). Áp dụng đặt hàng tự động cho nhóm này trước là ít rủi ro, nhiều lợi nhất.

**Kỹ năng trình bày dữ liệu**
- **Mỗi biểu đồ kèm 2 dòng:** "Cách đọc" (trục, màu nghĩa là gì) và "Phát hiện" (điều rút ra). Phát hiện **tính từ dữ liệu**, không gõ tay, để chạy lại vẫn đúng.
- **Kiểm tra phát hiện trước khi viết:** câu "ngày nhiều mã hết hàng nhất là mùa cao điểm" sai, vì ngày đó rơi vào tuần đầu mô phỏng (tồn kho ban đầu). Phải tách đầu kỳ ra rồi mới kết luận.
- **Giải thích bảng bằng ví dụ:** một câu như "còn 608 thùng + 851 đang về = 1.459, chưa vượt ROP 1.652 → đặt thêm 851" dễ hiểu hơn 10 cột số.
- **Nói rõ cái gì thật, cái gì giả định** ngay đầu trang; đừng để người xem tự đoán.
- **Màu có nghĩa:** xanh = ít hơn bình thường, đỏ = nhiều hơn; đỏ/cam/vàng dành riêng cho trạng thái cảnh báo, luôn kèm chữ.

**Câu hỏi tự kiểm tra**
1. Hội đồng hỏi: "Số liệu này có thật không?" Bạn trả lời thế nào?
2. Vì sao "Phát hiện" phải tính từ dữ liệu thay vì gõ tay?

<details><summary>Gợi ý</summary>

1. "Dữ liệu mô phỏng, vì chưa có dữ liệu kho thật. Ngày bão, ngày lễ, lịch sale lấy từ nguồn thật; lượng bán, chi phí, lead time là giả định. Mục tiêu là xây quy trình và so sánh các cách đặt hàng trên cùng dữ liệu; có file xuất – nhập – tồn thật thì chạy lại toàn bộ."
2. Khi dữ liệu hoặc mô hình chạy lại, số thay đổi; câu gõ tay sẽ sai mà không ai biết. Tính tự động thì câu luôn khớp biểu đồ.
</details>

## Bài 14. Nâng cấp dự báo: chính xác hơn chưa chắc rẻ hơn

**Kiến thức logistics**
- **Dự báo ngắn hạn quan trọng nhất:** 58% mã có lead time ≤ 7 ngày, nên điểm đặt hàng phụ thuộc chính vào dự báo vài ngày tới. Mô hình cũ chỉ dùng số bán từ 28 ngày trước; mô hình mới dùng số bán tuần gần nhất cho các ngày gần.
- **So theo âm lịch:** Tết và Trung thu lệch vài tuần mỗi năm theo dương lịch. So "cùng ngày âm lịch năm trước" (như người lập kế hoạch Việt Nam vẫn làm) giúp mô hình bớt dự báo thiếu trước Tết: Bias từ +6,3% xuống +3,9%, lần đầu đạt tiêu chí ±5%.
- **Chính xác hơn chưa chắc rẻ hơn:** với dự báo mới, Fill Rate tăng (95,3% → 95,9%), ít ngày thiếu hơn, nhưng tồn kho và tổng chi phí tăng nhẹ (+2%), vì hàng chỉ bán dịp lễ vẫn bị công thức EOQ đặt quá tay. Khi dự báo đã tốt, **nút thắt chuyển sang quy tắc đặt hàng**.

**Kỹ năng dữ liệu**
- **Ghi luật trước khi chạy:** mỗi cải tiến chỉ giữ nếu sai số trên validation giảm ít nhất 0,005 và Bias không tệ hơn. Dò tham số (F) bị bỏ vì chỉ giảm 0,0016: cải thiện đến từ cách dùng dữ liệu, không từ chỉnh tham số.
- **Tái lập trước khi cải tiến:** code mới ở cấu hình gốc phải ra đúng kết quả cũ (0,4028) thì mọi khác biệt sau đó mới là do cải tiến.
- **Kiểm tra rò rỉ:** đặc trưng mới chỉ được lấy số bán của ngày đã qua tại thời điểm dự báo.
- **Không quay lại vì kết quả test:** trên validation, mô hình mới cũng rẻ hơn về tồn kho; trên test thì đắt hơn 2%. Quay lại mô hình cũ vì test là chọn theo đề thi.

**Câu hỏi tự kiểm tra**
1. Vì sao dự báo chính xác hơn mà chi phí tồn kho lại tăng?
2. Vì sao phải ghi luật giữ / bỏ trước khi chạy cải tiến?

<details><summary>Gợi ý</summary>

1. Mô hình mới bớt dự báo thiếu ở hàng mùa vụ, nên đặt nhiều hơn trước cao điểm. Với hàng chỉ bán dịp lễ, công thức EOQ (giả định nhu cầu đều) đặt nhiều lần, hàng về sau mùa thành tồn dư. Dự báo tốt mà quy tắc đặt hàng không hợp thì lợi ích bị mất ở khâu sau.
2. Nếu xem kết quả rồi mới đặt luật, rất dễ chọn cái "đẹp" một cách vô tình. Luật ghi trước giữ cho việc chọn công bằng và bảo vệ được trước hội đồng.
</details>
