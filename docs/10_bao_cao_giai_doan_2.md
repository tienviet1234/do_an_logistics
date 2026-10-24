# Báo cáo Giai đoạn 2: Xây dựng dữ liệu và mô hình (báo cáo sống)

Đề tài: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho. Giai đoạn 2 = từ sau khi chốt đề cương và cơ sở lý thuyết (GĐ1) đến lúc nộp báo cáo (09/12/2026).

**Cách dùng file này.** Làm xong bước nào thì ghi vào đúng mục của bước đó, giữ nguyên bố cục; cuối giai đoạn chỉ cần ghép vào các chương đồ án (xem mục 0). Quy tắc ghi:
- Mỗi con số phải lấy từ file kết quả (nêu rõ file), không ghi theo trí nhớ.
- Luôn ghi rõ đâu là giả định, đâu là số liệu thật. Dữ liệu hiện tại là **mô phỏng**.
- Phần chưa làm đánh dấu ⏳; làm xong đổi thành ✅ và điền kết quả.

Cập nhật lần cuối: 24/10/2026.

---

## 0. Bản đồ chuyển thành chương đồ án

| Mục trong báo cáo này | Chương đồ án | Ghi chú |
|---|---|---|
| 1. Mục tiêu và phạm vi | Chương 1 | Rút gọn |
| 2. Dữ liệu | Chương 3 (nếu có dữ liệu thật) hoặc đầu Chương 4 | Nêu rõ là dữ liệu mô phỏng |
| 3. Tiền xử lý | Chương 4, mục 4.1 | |
| 4. Phân tích khám phá | Chương 4, mục 4.2 | Dùng hình `reports/eda/` |
| 5. Đặc trưng | Chương 4, mục 4.3 | |
| 6. Khung đánh giá | Chương 4, mục 4.4 | |
| 7. Mô hình mốc, 8. Mô hình AI, 9. So sánh | Chương 4, mục 4.5–4.7 | Phần trọng tâm |
| 10. Chính sách tồn kho, 11. Mô phỏng | Chương 4, mục 4.8–4.9, Chương 5 | Bảng trước–sau |
| 12. Dashboard | Chương 4, mục 4.10 | |
| 13. Hạn chế, 14. Nhật ký | Chương 5 (hạn chế), phụ lục | |

Trạng thái: 1–12 ✅.

---

## 1. Mục tiêu và phạm vi ✅

- **Mục tiêu:** dự báo nhu cầu theo ngày từng SKU, từ đó tính tham số tồn kho (EOQ, Safety Stock, Reorder Point) và đánh giá lợi ích so với cách đặt hàng hiện có bằng mô phỏng.
- **Chuỗi bài toán:** dự báo nhu cầu (d) → tham số tồn kho → so sánh chính sách bằng mô phỏng (Fill Rate, Stockout, DOH, chi phí).
- **Phạm vi:** 121 SKU hàng tiêu dùng, theo ngày, tầm dự báo 28 ngày (lớn hơn lead time dài nhất của dữ liệu là 15 ngày).
- **Lý do dùng dữ liệu mô phỏng:** chưa có dữ liệu xuất nhập tồn thật từ đơn vị thực tập. Dữ liệu được thiết kế để có đủ các hiện tượng khó của kho thật (mùa vụ, ngày lễ, bão, hết hàng, dữ liệu lỗi), và quy trình được viết để thay được dữ liệu thật (giữ nguyên tên cột).
- **Việc còn treo (mục 13):** xin ý kiến giảng viên về việc dùng dữ liệu mô phỏng; xin dữ liệu thật (hạn chót nhận: 08/11/2026).

## 2. Dữ liệu ✅

Nguồn: `src/sinh_du_lieu.py` (hạt giống cố định `20261009`, chạy lại ra đúng bộ dữ liệu).

| Thuộc tính | Giá trị |
|---|---|
| Số SKU | 121 |
| Giai đoạn | 01/10/2023 – 30/09/2026 (1.096 ngày) |
| Số dòng | 132.616 (bản sạch); 132.814 (bản thô, gồm 198 dòng trùng) |
| Cột bản thô | `date, ma_sku, qty_in, qty_out, ton_cuoi_ngay` |
| Chu kỳ bao phủ | 3 mùa Tết (10/02/2024, 29/01/2025, 17/02/2026), 3 mùa Trung thu, 3 chu kỳ 4 mùa |

**Hiện tượng được đưa vào dữ liệu:**
- 4 mùa (miền Bắc: Xuân T2–4, Hạ T5–7, Thu T8–10, Đông T11–1); chu kỳ tuần; xu hướng năm theo SKU.
- 11 dịp lễ có cửa sổ trước–sau (Tết −28 ngày, Trung thu −25, Noel −20...); hàng chỉ bán dịp lễ (mứt Tết, bánh trung thu) gần như không bán ngoài mùa.
- Bão lũ 3 pha (mua tích trữ 3 ngày trước, cứu trợ 10 ngày sau, giao hàng chậm); nắng nóng, rét đậm, cúm, sốt xuất huyết, tin đồn tăng giá, thể thao, đơn B2B đột biến, nhà cung cấp giao chậm.
- Kho đóng cửa (Tết, lễ), hết hàng, sale 11.11, 12.12, Black Friday, khuyến mãi theo SKU (1.338 đợt).
- Chính sách đặt hàng mô phỏng (s,Q) dựa trên dự báo có độ lệch của người lập kế hoạch; cầu theo phân phối nhị thức âm.

**Phân biệt thật / giả định:**
- Số liệu thật (kiểm chứng nguồn): ngày bão Yagi (07/09/2024); danh sách bão 2025 (Wipha đến Koto, lấy từ Wikipedia); lịch thi đấu Euro 2024, AFF Cup 2024, World Cup 2026.
- Giả định (mô phỏng): mức độ mạnh của bão, mọi hệ số tác động, các cú sốc khác, mức tác động chi phí.
- Nguồn bên thứ ba, chưa kiểm chứng chính thức: lịch sale sàn TMĐT (bài viết của một nhà bán lẻ). Trong dữ liệu chỉ 11.11, 12.12 và Black Friday có hiệu ứng.

**Tài liệu tham chiếu:** `docs/03`, `docs/04`, `docs/05`, `data/reference/`.

### 2.1. Loại kho và giá mặt hàng theo thị trường ✅ (24/10)

**Loại kho dữ liệu đại diện:** kho tổng (trung tâm phân phối) của chuỗi siêu thị / bách hóa, giao hàng cho các cửa hàng của chuỗi. Khớp nhất với dữ liệu: 17 nhóm hàng lẫn lộn, đơn vị tính theo thùng, Chủ nhật bán 0,53 ngày thường, khuyến mãi theo mã, đơn B2B (so sánh với nhà phân phối B2B và kho TMĐT: `docs/09` mục 4).

**Vì sao cập nhật giá:** kiểm tra dữ liệu cho thấy một số giá mô phỏng lệch xa giá thật (ví dụ sữa tươi Vinamilk 1L thùng 12: giá bán 214 nghìn, giá bán lẻ thật khoảng 467 nghìn).

**Cách làm** (`src/cap_nhat_gia.py`, nguồn từng mã: `data/reference/gia_thi_truong.csv`, báo cáo `reports/cap_nhat_gia.md`):
- Tra giá bán lẻ hiện tại (Bách Hóa Xanh, Pharmacity, Long Châu, Lazada, trang hãng, Bộ Công Thương), ngày tra 24/10/2026; ưu tiên giá niêm yết thường, không lấy giá khuyến mãi tạm thời; nhiều nguồn thì lấy trung bình.
- **37 mã đổi giá** (trung vị ×1,20; thấp nhất muối i-ốt ×0,52, cao nhất sữa Vinamilk 1L ×2,18). **84 mã giữ giá cũ**: 65 mã hàng chung chung không có nhãn hiệu / quy cách chuẩn, còn lại không tìm được giá Việt Nam hoặc giá cũ đã nằm trong khoảng tra được.
- Giá bán = giá bán lẻ (cửa hàng hết hàng thì mất đúng khoản bán lẻ đó). **Giá vốn = giá bán ÷ (1 + biên lãi cũ của mã): giả định**, vì giá nhập không công khai.
- Giá trị xuất 36 tháng và ABC tính lại đúng cách của bộ sinh dữ liệu (script tự kiểm tra: tính bằng giá cũ ra đúng cột cũ). Tổng giá trị xuất +11,5%; 11 mã đổi nhóm ABC (36 tháng); nhóm A theo tập train còn 28 mã (trước 31).
- **Không sinh lại dữ liệu gốc** (nhu cầu, giao dịch giữ nguyên). Hạn chế: "hiện trạng" trong dữ liệu đặt hàng theo EOQ tính bằng giá cũ.
- Chạy lại từ bước đặc trưng: mô hình không dùng giá (Naive, TB trượt, ETS, Croston, TSB, Prophet) chỉ chấm lại theo nhóm mới (`src/cham_lai.py`, WMAPE tổng không đổi); LightGBM, ARIMA, chọn mô hình, CSDL, tồn kho, thử độ nhạy chạy lại.

**Ảnh hưởng (trước → sau):** mô hình được chọn và trọng số **không đổi** (kết hợp theo nhóm, X 0,9 · Y 1,0 · Z 0,6), WMAPE test 0,376 → 0,375; AI + hiệu chỉnh: Fill Rate 95,36% → 95,34%, chi phí liên quan 5,98 → 6,54 tỷ (giá vốn cao hơn), so với dự báo mốc −30,9% → −29,8%, tồn kho so với hiện trạng +36% → +28%. **Các kết luận chính không đổi.** Các mục dưới đây đã cập nhật theo giá mới; nhật ký (mục 14) giữ số liệu tại thời điểm làm từng bước.

## 3. Tiền xử lý ✅

Script: `src/lam_sach.py` → `data/clean/giao_dich_sach.csv`, báo cáo `reports/bao_cao_lam_sach.md`.

**Lỗi cài sẵn trong bản thô (để kiểm thử quy trình):**

| Lỗi | Số lượng | Cách xử lý |
|---|---|---|
| Dòng trùng hoàn toàn | 198 | Loại bỏ |
| `qty_out` bị thiếu | 530 | Suy ra từ đẳng thức kho |
| `qty_out` nhập sai gấp 10 hoặc 100 lần | 157 | Suy ra từ đẳng thức kho |

**Nguyên lý sửa lỗi:** xuất = tồn đầu + nhập − tồn cuối. Chỉ sửa dòng lệch với đẳng thức này. Đột biến thật (bão, sale) vẫn khớp với tồn kho nên **không** bị coi là lỗi. Cách này khác khuyến nghị nội suy / IQR trong báo cáo GĐ1, vì IQR dễ xóa nhầm đỉnh nhu cầu thật (xem `docs/08`).

**Kết quả:**
- Đã sửa 687 dòng; đối chiếu với bản đáp án: **0 dòng còn sai**; đủ 132.616 dòng; tồn không âm; không xuất hàng ngày kho đóng cửa.
- Nhật ký lỗi ghi 689 lỗi nhưng chỉ có 687 ô bị lỗi: 2 ô (SKU026 ngày 07/11/2024, SKU035 ngày 24/07/2025) bị ghi cả hai loại lỗi.
- **Cờ hết hàng** (`het_hang`, tồn cuối ngày = 0): 4.225 dòng (3,19%). Đối chiếu đáp án: bắt đủ 4.050/4.050 ngày hết hàng thật, thêm 175 ngày tồn về 0 nhưng vẫn đủ hàng cho khách (cờ thừa, an toàn vì chỉ loại bớt dữ liệu).
- Ngày hết hàng có lượng xuất thấp hơn nhu cầu thật → không coi là nhu cầu (demand censoring).

**Điều kiện áp dụng:** cách sửa dựa vào cột tồn cuối ngày đáng tin. Với dữ liệu thật phải kiểm chéo thêm với chứng từ.

## 4. Phân tích khám phá ✅

Script: `src/eda.py` → 8 hình `reports/eda/h01–h08.png`, nhận xét `reports/bao_cao_eda.md`.

| Hình | Nội dung | Phát hiện (số liệu từ file) |
|---|---|---|
| h01 | Tổng xuất kho theo ngày | Đỉnh lớn nhất trước Tết; đỉnh phụ tháng 9–10 (Trung thu, khai giảng, bão Yagi) |
| h02 | 6 SKU đại diện | Ổn định (X), mùa vụ (bánh trung thu, mứt Tết), tăng khi bão (mì gói), rời rạc: mỗi kiểu có hình dạng nhu cầu riêng |
| h03 | Chu kỳ tuần | Thứ Bảy 1,16 lần mức TB; Chủ nhật 0,53 lần → chu kỳ 7 ngày bắt buộc |
| h04 | Chỉ số mùa theo nhóm hàng | Đồ chơi mùa Thu 3,75 lần; trang trí mùa Đông 2,47 lần; kem mùa Hạ 1,96 lần |
| h05 | Phân rã chuỗi (chu kỳ 52 tuần) | Xu hướng gần như **đi ngang** (7.103–7.815 đơn vị/ngày); mùa vụ năm mạnh; phần dư lớn ở tuần Tết vì Tết âm lịch đổi ngày mỗi năm → cần biến ngày lễ |
| h06 | Ma trận ABC × XYZ (tập train, giá thị trường 24/10) | A-X 20, A-Y 3, A-Z 5, B-X 19, B-Y 6, B-Z 15, C-X 32, C-Y 1, C-Z 20 (với giá mô phỏng cũ: A-X 22, A-Z 6, B-X 18, B-Z 17, C-X 31, C-Z 17) |
| h07 | Phân loại Syntetos–Boylan | 58 smooth, 54 erratic, 9 lumpy |
| h08 | Tác động khuyến mãi | So trong cùng tháng: trung vị tăng 60%; 4 SKU có hệ số dưới 1 |

**Bài học phương pháp:** cách tính h08 đầu tiên (so ngày khuyến mãi với mọi ngày không khuyến mãi) làm 11 SKU trông như "khuyến mãi làm giảm bán", do khuyến mãi trái mùa so với ngày cao điểm. Đổi sang so trong cùng tháng loại được ảnh hưởng mùa vụ. Nên viết điều này vào đồ án như ví dụ về nhiễu chéo (confounding).

**Hàm ý cho mô hình:** cần biến thứ trong tuần, biến ngày lễ (có cửa sổ), biến khuyến mãi; nhóm Z và hàng mùa vụ là nơi mô hình có biến sự kiện kỳ vọng thắng mô hình mốc.

## 5. Đặc trưng ✅

Script: `src/dac_trung.py` → `data/features/dac_trung.csv` (132.616 dòng × 64 cột), `phan_loai_sku.csv`, báo cáo `reports/bao_cao_dac_trung.md`.

| Nhóm | Cột chính | Nguồn |
|---|---|---|
| Lịch | thứ, cuối tuần, tháng, tuần/ngày trong năm, mùa, đầu/cuối tháng | Lịch |
| Ngày lễ và sự kiện | 17 cờ `sk_*` có cửa sổ trước–sau; `so_ngay_den_tet`, `so_ngay_sau_tet` | `lich_su_kien_prophet.csv` |
| Bão | `bao_lu_muc_do`, `bao_truoc`, `bao_sau` (cửa sổ −3…+14 ngày) | `su_kien_dot_bien.csv` |
| Sale và khuyến mãi | `ngay_sale`, `cua_so_sale` (11.11, 12.12, Black Friday), `khuyen_mai` | Lịch sale, `lich_khuyen_mai.csv` |
| Trễ và trượt | `lag_1/7/14/28/35/364`, `tb_truot_7/28`, `dlc_truot_28`, `tb_truot_28_tre28` | Quá khứ của chính SKU |
| SKU | nhóm hàng, loại mùa vụ, `abc_train`, `xyz_train`, `loai_nhu_cau` | `sku_master`, tập train |
| Mục tiêu | `y` (= `qty_out`), `y_cau` (bỏ ngày hết hàng và ngày kho đóng cửa) | |

**Kiểm chứng:** cờ dựng lại từ lịch tham chiếu khớp bản đáp án 100% (thứ, mùa, khuyến mãi, Tết, bão); các cột trễ chỉ dùng dữ liệu quá khứ (kiểm tra ví dụ: lag_1 ngày 15/03/2025 bằng số bán ngày 14/03/2025).

**Quyết định ghi lại:**
- Phân loại ABC/XYZ trong `sku_master` tính trên cả 36 tháng (gồm giai đoạn test) → là nhìn trước tương lai. Tính lại trên tập train: 2 SKU đổi nhóm ABC (với giá mô phỏng cũ là 8), 3 SKU đổi nhóm XYZ. Mô hình dùng bản `*_train`.
- Đơn B2B đột biến (91 dòng) không biết trước → chỉ dùng để loại khỏi huấn luyện và chấm điểm, không làm biến dự báo.
- `y_cau` bỏ trống 8.706 dòng (hết hàng hoặc kho đóng cửa).
- **Lưu ý cho mô hình tầm 28 ngày:** lag nhỏ hơn 28 không có tại thời điểm dự báo; dùng lag ≥ 28 hoặc dự báo đệ quy.

## 6. Khung đánh giá ✅

Script: `src/danh_gia.py` → `reports/ket_qua_mo_hinh.csv`, dự báo chi tiết `reports/du_bao/`.

**Thiết kế:**
- Chia **theo thời gian**, không xáo trộn. Train: 01/10/2023–30/09/2025 (24 tháng, đủ 2 mùa Tết). Validation (dò tham số): 6 mốc, 31/03/2025–18/08/2025. Test (chấm điểm cuối): 13 mốc, 30/09/2025–01/09/2026.
- Backtest cuốn chiếu: mỗi 28 ngày đặt 1 mốc, dự báo 28 ngày tiếp theo.
- Chỉ chấm trên nhu cầu tin được (`y_cham` = `y_cau` bỏ ngày đơn B2B đột biến).
- Mô hình chỉ được biết trước các cột biết được ở tương lai: lịch, ngày lễ, sale, khuyến mãi, nghỉ kho, thông tin SKU. **Bão không biết trước** (ngoài đời chỉ có cảnh báo 3–5 ngày).
- Chỉ số: MAE, RMSE, WMAPE, WMAPE theo tuần, MASE, Bias %. WMAPE được chọn thay MAPE vì MAPE hỏng khi nhu cầu ngày gần 0. MASE dùng mẫu số là Seasonal Naive chu kỳ 7 một bước trên train, nên dự báo 28 ngày thường có MASE > 1. Bias % dương = dự báo thiếu (dễ hết hàng).

**Kiểm chứng:** mọi ngày dự báo đều sau ngày mốc; `ngay_thu` chạy từ 1 đến 28.

## 7. Mô hình mốc ✅ (xong 23/10, kế hoạch 22–28/10)

Script: `src/mo_hinh_baseline.py` (thư viện `statsforecast`), tổng hợp `src/tong_hop_ket_qua.py` → `reports/bang_so_sanh_test.md`. Mỗi mô hình học trên 365 ngày gần nhất trước mốc; ngày hết hàng / kho đóng cửa trong lịch sử được nội suy; ngày kho đóng cửa trong tương lai dự báo 0.

**Mô hình đã chạy:**
| Mô hình | Ý tưởng | Ghi chú |
|---|---|---|
| Naive | Lấy số bán ngày gần nhất | Từ GĐ B |
| Seasonal Naive 7 | Lặp lại tuần gần nhất | Từ GĐ B, **mốc so sánh chính** |
| Trung bình trượt 28 ngày | TB 28 ngày gần nhất, dự báo phẳng | |
| ETS (tự chọn) | Làm mượt mũ, chu kỳ tuần | |
| ARIMA (tự chọn) | Tự hồi quy + trung bình trượt, chu kỳ tuần | Chỉ 28 SKU nhóm A (31 với giá mô phỏng cũ; chậm ~3 giây/SKU/mốc, gấp ~20 lần ETS) |
| Croston SBA | Tách "bao lâu bán 1 lần" và "mỗi lần bán bao nhiêu" | Thiết kế cho hàng bán rời rạc |
| TSB | Như Croston nhưng cập nhật xác suất bán mỗi ngày | alpha = 0,2 |

**Kết quả tập test (13 mốc, 10/2025–9/2026):**
| Mô hình | WMAPE | WMAPE tuần | Bias % | WMAPE A | WMAPE X | WMAPE Y | WMAPE Z | WMAPE lumpy | FVA so SN7 |
|---|---|---|---|---|---|---|---|---|---|
| **TB trượt 28** | **0,640** | **0,511** | −0,8% | 0,495 | 0,408 | 0,653 | **1,272** | **1,860** | **+17,2%** |
| Croston SBA | 0,651 | 0,516 | +0,4% | **0,484** | **0,395** | 0,589 | 1,365 | 2,184 | +15,8% |
| TSB | 0,686 | 0,549 | −6,5% | 0,496 | 0,410 | 0,555 | 1,477 | 2,476 | +11,2% |
| ETS | 0,721 | 0,614 | −16,7% | 0,525 | 0,428 | **0,527** | 1,574 | 2,291 | +6,8% |
| Naive | 0,739 | 0,634 | −9,1% | 0,535 | 0,491 | 0,639 | 1,442 | 2,408 | +4,4% |
| Seasonal Naive 7 | 0,773 | 0,598 | −11,0% | 0,550 | 0,475 | 0,597 | 1,636 | 2,691 | 0 |
| ARIMA (chỉ nhóm A) | — | — | — | 0,493 | — | — | — | — | +10,5% (trên A) |

Validation (6 mốc, 4–9/2025, giai đoạn "êm"): TB trượt 28 0,426 · Croston 0,415 · TSB 0,425 · ETS 0,450 · ARIMA (A) 0,382 · Seasonal Naive 0,498. Thứ hạng giữa validation và test khác nhau → kết luận dựa trên test.

**Nhận xét:**
1. **Mô hình mốc mạnh nhất là trung bình trượt 28 ngày** (WMAPE 0,640, giảm 17,2% so với Seasonal Naive). Đây là con số mô hình AI thực sự phải thắng, không chỉ Seasonal Naive.
2. **Seasonal Naive kém nhất** dù dữ liệu có chu kỳ tuần rõ: chép nguyên 1 tuần thì chép cả nhiễu của tuần đó. Làm mượt (trung bình 28 ngày) ổn định hơn.
3. **ARIMA không đáng công:** trên nhóm A còn kém Croston (0,493 so với 0,484) mà chậm gấp ~20 lần. Không mở rộng ARIMA cho 121 SKU.
4. **ETS dự báo thừa có hệ thống** (Bias −16,7%): sau các đỉnh mùa vụ, ETS kéo xu hướng đi quá xa.
5. **Croston/TSB không thắng ở nhóm "lumpy"** (TB trượt 1,860 so với Croston 2,184). Lý do: 9 SKU lumpy trong dữ liệu là hàng **thời vụ** (máy sưởi...), không phải hàng bán rời rạc ngẫu nhiên; khuôn mùa vụ mới là yếu tố chính, điều Croston không mô tả được.
6. **Nhóm Z (mùa vụ) là điểm yếu chung:** mô hình mốc tốt nhất vẫn sai 127%, vì không mô hình nào biết sắp tới Tết, Trung thu. Đây là khoảng trống GĐ D (Prophet, LightGBM có biến ngày lễ) cần lấp.

**Đối chiếu tiêu chí thành công (`docs/09` mục 1c):** ngưỡng "giảm ≥ 20% so với Seasonal Naive" tương đương WMAPE ≤ 0,618. Mô hình mốc tốt nhất đạt 0,640 (chưa tới) → mô hình AI cần thắng **cả** 0,618 lẫn 0,640.

## 8. Mô hình AI ✅ (xong 24/10; kế hoạch 29/10–08/11)

### 8.1. Prophet ✅

Script: `src/mo_hinh_prophet.py`. Mỗi SKU một mô hình, học trên toàn bộ lịch sử đến mốc.
- **Holidays (biết trước):** 12 loại sự kiện có lịch trong `lich_su_kien_prophet.csv` (Tết, Trung thu, Noel, các ngày lễ, khai giảng, thể thao) + sale 11.11, 12.12, Black Friday (cửa sổ −1…+1 ngày).
- **Biến thêm (regressor):** `khuyen_mai` theo lịch khuyến mãi.
- **Không dùng:** bão lũ, nắng nóng, rét đậm, dịch bệnh, tin đồn giá (không biết trước 28 ngày). Quyết định ngày 23/10: loại 5 cờ này khỏi danh sách "biết trước" của khung đánh giá (`UNFORESEEABLE` trong `src/danh_gia.py`).
- **Mùa vụ:** năm + tuần; kiểu mùa vụ chọn trên validation: cộng (additive) WMAPE 0,434 tốt hơn nhân (multiplicative) 0,535 → dùng **additive**.
- Kỹ thuật: chạy song song 4 tiến trình (11 tiến trình làm hết RAM máy 7,6 GB); khoảng 67 giây/mốc.

**Kết quả tập test:**
| Mô hình | WMAPE | WMAPE tuần | Bias % | WMAPE A | WMAPE X | WMAPE Y | WMAPE Z | WMAPE lumpy | FVA so SN7 |
|---|---|---|---|---|---|---|---|---|---|
| **Prophet** | **0,454** | **0,257** | −4,9% | **0,387** | **0,383** | **0,486** | **0,638** | **0,725** | **+41,3%** |
| TB trượt 28 (mốc tốt nhất) | 0,640 | 0,511 | −0,8% | 0,495 | 0,408 | 0,653 | 1,272 | 1,860 | +17,2% |
| Seasonal Naive 7 | 0,773 | 0,598 | −11,0% | 0,550 | 0,475 | 0,597 | 1,636 | 2,691 | 0 |

**Theo từng mốc (WMAPE):** Prophet thắng TB trượt 28 ở **11/13 mốc**. Mốc Tết (17/02/2026): Prophet 0,45 · TB trượt 1,48 · Seasonal Naive 2,17. Hai mốc hòa/thua nhẹ là 12/05 và 09/06/2026 (giai đoạn không có lễ lớn: 0,39 so với 0,39; 0,46 so với 0,44).

**Nhận xét:**
1. Prophet giảm sai số **29%** so với mô hình mốc tốt nhất (0,454 so với 0,640) và **41%** so với Seasonal Naive.
2. Lợi thế đến từ **lịch lễ**: nhóm Z (mùa vụ) giảm từ 1,272 xuống 0,638 (giảm một nửa); nhóm X (ổn định) chỉ cải thiện nhẹ (0,408 → 0,383). Ở giai đoạn không có lễ, Prophet ngang mô hình mốc. Điều này khớp với validation (tháng 4–9, ít lễ): Prophet 0,434 ngang TB trượt 0,426.
3. Sai số theo tuần chỉ còn 0,257: cộng theo tuần, sai số ngày triệt tiêu bớt; đây là mức thời gian dùng cho quyết định đặt hàng.
4. Bias −4,9%: dự báo thừa nhẹ, nằm trong ngưỡng ±5%.

**Lưu ý trung thực (phải ghi vào phần hạn chế):** lịch lễ Prophet dùng (`lich_su_kien_prophet.csv`) chính là lịch mà bộ sinh dữ liệu mô phỏng dùng để tạo hiệu ứng lễ, và lịch khuyến mãi khớp tuyệt đối với dữ liệu. Ngoài đời, cửa sổ lễ (bắt đầu tăng từ bao nhiêu ngày trước) phải tự ước lượng và lịch khuyến mãi có thể thay đổi, nên mức cải thiện trên dữ liệu thật **nhiều khả năng thấp hơn**. Kết luận an toàn: "mô hình có biến lịch lễ cải thiện mạnh nhất ở hàng mùa vụ", không phải "giảm đúng 41%".

### 8.2. LightGBM ✅ (24/10)

Script: `src/mo_hinh_lightgbm.py`. **Một mô hình chung cho cả 121 SKU** (global model), học lại tại mỗi mốc.
- **Đặc trưng (43):** mã SKU và thông tin SKU (nhóm hàng, loại mùa vụ, ABC/XYZ, giá, lead time); lịch (thứ, tháng, ngày trong năm, số ngày đến/sau Tết...); 12 cờ sự kiện biết trước; sale; khuyến mãi; **giá trị trễ chỉ từ 28 ngày trở về trước** (lag 28/35/42/49/364, trung bình và độ lệch chuẩn 7 và 28 ngày tính đến t−28), để dự báo cả 28 ngày tới từ một mốc mà không cần dự báo đệ quy. Giá trị trễ tính lại bên trong từng mốc từ dữ liệu quá khứ (đã kiểm tra: lag_28 của ngày xa nhất bằng đúng số bán ngày mốc).
- Không dùng bão / thời tiết / dịch bệnh (không biết trước).
- Hàm mất mát chọn trên validation: **tweedie** WMAPE 0,353 tốt hơn l2 0,425. Tham số: 600 cây, learning rate 0,05, 63 lá. Rất nhanh: ~3 giây/mốc (Prophet ~67 giây).

**Kết quả tập test:**
| Mô hình | WMAPE | WMAPE tuần | Bias % | WMAPE A | WMAPE X | WMAPE Y | WMAPE Z | WMAPE lumpy | FVA so SN7 |
|---|---|---|---|---|---|---|---|---|---|
| **LightGBM** | **0,399** | 0,269 | **+11,7%** | **0,335** | **0,312** | **0,391** | 0,638 | 0,837 | **+48,4%** |
| Prophet | 0,454 | **0,257** | −4,9% | 0,387 | 0,383 | 0,486 | 0,638 | **0,725** | +41,3% |
| TB trượt 28 | 0,640 | 0,511 | −0,8% | 0,495 | 0,408 | 0,653 | 1,272 | 1,860 | +17,2% |

- Theo mốc: LightGBM thắng Prophet ở **12/13 mốc** (thua mốc 01/09/2026: 0,57 so với 0,52).
- **Bias theo nhóm:** X +2,6% · Y −1,5% · **Z +40,2%**. Dự báo thiếu dồn vào các mốc trước cao điểm: 30/09/2025 (+25%), 20/01/2026 (+38%, trước Tết), 01/09/2026 (+30%, trước Trung thu).

**Độ quan trọng đặc trưng** (tỷ trọng gain, trung bình 13 mốc test; `reports/lightgbm_quan_trong.csv`): mã SKU 35,5% · TB 7 ngày tính đến t−28 10,8% · số bán cùng ngày năm trước (lag_364) 7,7% · loại mùa vụ 7,3% · TB 28 ngày đến t−28 5,8% · **số ngày đến Tết 5,5%** · lag_28 4,1% · cờ Trung thu 3,2% · ... · khuyến mãi 1,2% (hạng 13) · giá bán 1,1% (hạng 14).

**Nhận xét:**
1. LightGBM chính xác nhất theo ngày (giảm 48% so với Seasonal Naive, 38% so với TB trượt 28), đặc biệt ở hàng ổn định (X: 0,312) và chạy nhanh hơn Prophet khoảng 20 lần.
2. Nhưng **dự báo thiếu hàng mùa vụ trước cao điểm** (Z +40,2%), vượt ngưỡng Bias ±5% của tiêu chí thành công. Nguyên nhân có thể: mô hình dựa nhiều vào số bán cùng ngày năm trước (lag_364) trong khi Tết âm lịch lệch vài tuần mỗi năm, và dữ liệu học mới có 2 mùa Tết. Với kho, thiếu hàng trước Tết là sai lầm đắt nhất.
3. Theo tuần, Prophet vẫn nhỉnh hơn (0,257 so với 0,269) nhờ không bị lệch có hệ thống.
4. Hai mô hình mạnh ở hai nhóm khác nhau (LightGBM: X/Y; Prophet: Z ít lệch hơn) → hướng xử lý ở GĐ E: **chọn mô hình theo nhóm SKU** hoặc **kết hợp** (lấy trung bình hai dự báo), quyết định **trên tập validation**, không nhìn tập test.
5. Khuyến mãi chỉ xếp hạng 13 dù EDA cho thấy tăng 60%: khuyến mãi chỉ chiếm ~8% số ngày, nên tổng "đóng góp" nhỏ dù tác động mỗi lần lớn. Độ quan trọng kiểu gain đo tổng đóng góp, không đo độ lớn tác động.

### 8.3. LSTM

Bỏ khỏi kế hoạch; ghi vào hướng phát triển (lý do: mỗi SKU chỉ ~1.096 điểm, khó giải thích, hiếm khi hơn Prophet/XGBoost; xem `docs/06`).

## 9. So sánh và chọn mô hình 🔄 (bắt đầu 24/10; kế hoạch 09–11/11)

Script: `src/chon_mo_hinh.py`. Kết quả vòng 1: `reports/chon_mo_hinh.md`; vòng 2: `reports/chon_mo_hinh_vong2.md`.

**Ứng viên** (dự báo = w × LightGBM + (1 − w) × Prophet): Prophet (w = 0), LightGBM (w = 1), trung bình (w = 0,5), kết hợp toàn kho (w dò trên validation, lưới 0; 0,1; …; 1), kết hợp theo nhóm XYZ (mỗi nhóm một w dò trên validation).

**Luật chọn (viết trước khi xem test, giữ nguyên cả 2 vòng):** WMAPE trên validation thấp nhất; nếu chênh dưới 0,005 thì chọn phương án đơn giản hơn (thứ tự đơn giản: Prophet, LightGBM, trung bình, kết hợp toàn kho, kết hợp theo nhóm). Tập test chỉ dùng để báo cáo.

### 9.1. Vòng 1 (validation 6 mốc, 31/03–18/08/2025)

| Ứng viên | w LightGBM | Val WMAPE | Val Bias | Test WMAPE | Test WMAPE tuần | Test Bias | Test WMAPE Z | Test Bias Z |
|---|---|---|---|---|---|---|---|---|
| Prophet | 0 | 0,434 | −3,2% | 0,454 | 0,257 | −4,9% | 0,638 | −9,7% |
| **LightGBM** ✅ | 1 | **0,353** | +4,8% | 0,399 | 0,269 | +11,7% | 0,638 | +40,2% |
| Trung bình | 0,5 | 0,374 | +0,8% | **0,388** | **0,235** | **+3,4%** | **0,544** | +15,3% |
| Kết hợp toàn kho | 0,9 (dò được) | 0,353 | +4,0% | 0,389 | 0,258 | +10,1% | 0,601 | +35,2% |
| Kết hợp theo nhóm | X 0,9 · Y 0,7 · Z 1,0 | 0,351 | +4,2% | 0,399 | 0,268 | +11,3% | 0,638 | +40,2% |

- Luật chọn **LightGBM** (kết hợp theo nhóm chỉ thấp hơn 0,002 trên validation, dưới ngưỡng 0,005 → chọn phương án đơn giản hơn). Nhưng trên test, **trung bình hai mô hình tốt hơn ở mọi chỉ số** (WMAPE, WMAPE tuần, Bias, nhóm Z).
- **Nguyên nhân:** validation vòng 1 (tháng 4–9) **không có Tết hay cao điểm lớn**, nên không lộ ra điểm yếu của LightGBM (dự báo thiếu trước cao điểm). Tập dùng để chọn không đại diện cho tập dùng để chấm. Điểm này đã được ghi nhận từ khi chạy Prophet (mục 8.1: "validation là giai đoạn êm").
- **Không** đổi sang "trung bình" dựa trên kết quả test, vì như vậy là chọn theo đề thi (rò rỉ thông tin từ tập test).

### 9.2. Vòng 2 (validation 13 mốc, 30/09/2024–01/09/2025) ✅

**Thay đổi duy nhất so với vòng 1:** tập validation, nay gồm 13 mốc **cùng ngày với 13 mốc test nhưng sớm hơn một năm**, nên có Tết 2025, Trung thu 2024–2025 và các cơn bão. **Giữ nguyên:** cấu hình mô hình (Prophet additive, LightGBM tweedie, đã chọn ở vòng 1), lưới trọng số, luật chọn. Hạn chế: các mốc validation đầu chỉ có khoảng 12 tháng dữ liệu học (ít hơn tập test), ảnh hưởng cả hai mô hình. Phân loại ABC/XYZ tính trên toàn tập train (đến 30/09/2025), có phủ giai đoạn validation; ảnh hưởng nhỏ vì chỉ dùng để nhóm và làm đặc trưng tĩnh.

**Kết quả (chạy 24/10):**
| Ứng viên | w LightGBM | Val2 WMAPE | Val2 Bias | Test WMAPE | Test WMAPE tuần | Test Bias | Test WMAPE Z | Test Bias Z |
|---|---|---|---|---|---|---|---|---|
| Prophet | 0 | 0,488 | −1,4% | 0,454 | 0,257 | −4,9% | 0,638 | −9,7% |
| LightGBM | 1 | 0,403 | +12,9% | 0,399 | 0,269 | +11,7% | 0,638 | +40,2% |
| Trung bình | 0,5 | 0,408 | +5,8% | 0,388 | 0,235 | +3,4% | 0,544 | +15,3% |
| Kết hợp toàn kho | 0,8 (dò được) | 0,394 | +10,0% | 0,383 | 0,250 | +8,4% | 0,574 | +30,2% |
| **Kết hợp theo nhóm** ✅ | X 0,9 · Y 1,0 · **Z 0,6** | **0,388** | +7,9% | **0,375** | **0,234** | +6,3% | 0,546 | +20,3% |

- **Mô hình được chọn: kết hợp theo nhóm XYZ** (dự báo chi tiết: `reports/du_bao/ket_hop_theo_nhom_v2_test.csv`). Đây là mô hình dùng cho GĐ F.
- Validation vòng 2 **đại diện tốt hơn**: lộ ra đúng điểm yếu của LightGBM (Bias validation +12,9%, sát mức +11,7% trên test), trong khi vòng 1 chỉ thấy +4,8%. Thứ hạng trên validation vòng 2 khớp với thứ hạng trên test (kết hợp theo nhóm tốt nhất ở cả hai).
- Trọng số hợp lý về nghiệp vụ: hàng ổn định (X, Y) dựa gần hết vào LightGBM; hàng mùa vụ (Z) lấy 40% từ Prophet để giảm thiếu hàng trước cao điểm.
- Trên test: WMAPE **0,375**, WMAPE tuần **0,234**: tốt nhất trong mọi mô hình đã thử; giảm **51%** so với Seasonal Naive (0,773) và **41%** so với mô hình mốc tốt nhất (TB trượt 28: 0,640).
- **Còn hạn chế:** Bias +6,3%, vẫn dự báo thiếu nhẹ, **vượt ngưỡng ±5%** của tiêu chí thành công; nhóm Z còn thiếu 20,3%. Cần xử lý ở GĐ F (ví dụ hiệu chỉnh độ lệch **ước lượng trên validation vòng 2**, hoặc để tồn kho an toàn bù), không chỉnh bằng cách nhìn test.

**Bài học phương pháp (đưa vào Chương 4):** tập validation phải **cùng đặc điểm** với giai đoạn sẽ áp dụng mô hình (ở đây: có mùa cao điểm). Validation "êm" chọn nhầm mô hình chính xác trung bình nhưng thiếu hàng đúng lúc cao điểm.

### 9.3. Biểu đồ kết quả ✅ (24/10)
`src/bieu_do_ket_qua.py` (đọc từ CSDL) → `reports/ket_qua/`, chú thích ở `reports/bao_cao_bieu_do_ket_qua.md`. Màu cố định theo đối tượng ở mọi hình (thực tế đen, AI xanh dương, dự báo mốc cam, Prophet xanh ngọc, LightGBM vàng, hiện trạng xám).
- `k01` xếp hạng sai số các mô hình (tập test); `k02` dự báo so với thực tế, tổng toàn kho, mốc trước Tết và trước Trung thu 2026 (TB trượt dự báo phẳng, AI bám đỉnh nhưng vẫn thấp hơn đỉnh, khớp Bias dương); `k03` sai số theo nhóm XYZ; `k04` giá trị tồn kho theo ngày của 4 chính sách; `k05` trước–sau (Fill Rate, chi phí liên quan); `k06` mô hình răng cưa tồn kho – ROP – đặt hàng của SKU001 (minh họa lý thuyết Chương 2).
- Bảng tổng hợp mọi mô hình: `reports/bang_so_sanh_test.md` và khung nhìn `v_xep_hang_mo_hinh`.

## 9b. Luồng hệ thống và cơ sở dữ liệu ✅ (24/10; nhiệm vụ giảng viên giao, trình bày trước hội đồng)

**Trang trình bày:** `trinh_bay/luong_he_thong.html`, mở bằng trình duyệt, **không cần internet**, có 3 phần (mở thẳng bằng `#1`, `#2`, `#3`). Tạo tự động từ cơ sở dữ liệu bằng `src/tao_trang_luong.py`, nên số liệu trên trang luôn khớp dữ liệu.
1. **Luồng nghiệp vụ** (7 bước, ai làm gì): kho ghi nhận nhập–xuất–tồn → bán hàng gửi lịch khuyến mãi/lễ → hệ thống làm sạch, đối soát → dự báo 28 ngày → tính SS/ROP/EOQ → cảnh báo, đề xuất đơn → mua hàng đặt hàng, điều vận lên kế hoạch xe; vòng lặp hằng ngày. Hệ thống đảm nhận bước 3–6.
2. **Luồng dữ liệu** (nguồn + 9 bước, mỗi bước một chương trình chạy lại được, ghi rõ đọc/ghi bảng nào). Trình bày trung thực hiện trạng: bước 1–6 xử lý trên file, bước 7 đẩy toàn bộ vào CSDL; từ bước 8 (tồn kho, dashboard) đọc trực tiếp từ CSDL.
3. **Cơ sở dữ liệu**: các bảng theo nhóm, số dòng, cột, khóa chính / khóa ngoại.

**Cơ sở dữ liệu:** SQLite, một file `data/kho_hang.db` (không cần máy chủ, chạy được khi bảo vệ không có mạng; viết bằng SQL chuẩn để chuyển sang MySQL / PostgreSQL / SQL Server nếu được yêu cầu). Thiết kế: `database/schema.sql`. Nạp: `src/nap_database.py` (xóa và tạo lại, nạp theo thứ tự khóa ngoại, ghi `nhat_ky_chay`).
| Nhóm | Bảng | Ghi chú |
|---|---|---|
| Danh mục | `dm_nha_cung_cap` (14), `dm_sku` (121), `phan_loai_sku` (121) | Chi phí đặt hàng, lưu kho, lead time, MOQ dùng cho GĐ F |
| Lịch và sự kiện | `lich_su_kien` (65, có cờ biết trước 28 ngày), `lich_ngay_nghi` (38), `lich_khuyen_mai` (1.338), `su_kien_dot_bien` (92) | |
| Giao dịch | `giao_dich_tho` (132.814, vùng tạm), `giao_dich_sach` (132.616, khóa chính ngày + SKU), `nhat_ky_sua_loi` (687) | Truy vết từ thô → sạch |
| Mô hình | `mo_hinh` (19, cờ `duoc_chon`, `pham_vi`), `ket_qua_mo_hinh` (35), `du_bao` (1.160.040) | |
| Hệ thống | `nhat_ky_chay` | Mỗi lần nạp: bảng, số dòng, trạng thái |
| Khung nhìn | `v_giao_dich`, `v_du_bao_chon`, `v_xep_hang_mo_hinh` | Dùng cho trình bày và dashboard |

**Kiểm tra toàn vẹn (tự chạy sau mỗi lần nạp, đều đạt 24/10):** 0 vi phạm khóa ngoại; integrity_check ok; số dòng và tổng lượng xuất (7.866.600) khớp file nguồn; 0 SKU lạ; **đẳng thức kho kiểm bằng SQL: 0 dòng lệch**; mô hình được chọn đúng.
**Ràng buộc chặn dữ liệu sai (đã thử):** mã hàng không có trong danh mục (khóa ngoại), lượng xuất âm (CHECK), trùng (ngày, SKU) (khóa chính), dự báo cho ngày trước mốc (CHECK).
**Trình diễn:** `database/truy_van_mau.sql` (8 truy vấn) hoặc `python src/xem_database.py`; xem bảng trực quan bằng phần mềm miễn phí DB Browser for SQLite.

## 10. Chính sách tồn kho ✅ (24/10; kế hoạch 12–22/11)

Script: `src/ton_kho.py`, **đọc toàn bộ đầu vào từ CSDL** (`dm_sku`, `phan_loai_sku`, `nhu_cau_that`, `giao_dich_sach`, `lich_ngay_nghi`, `su_kien_dot_bien`, `du_bao`) và ghi kết quả vào CSDL (`chinh_sach`, `tham_so_ton_kho`, `ket_qua_ton_kho`, `mo_phong_ngay`, khung nhìn `v_so_sanh_chinh_sach`). Báo cáo: `reports/ton_kho_so_sanh.md`.

**Thiết kế mô phỏng** (12 tháng test 01/10/2025–29/09/2026, 121 SKU). Mọi chính sách dùng **chung**: nhu cầu thật (kể cả ngày hết hàng; bảng `nhu_cau_that`, là **đáp án**, chỉ dùng để chấm, không đưa vào mô hình), thời gian giao hàng thực tế (bốc ngẫu nhiên một lần, hạt giống 20261023, cộng chậm do bão và nhà cung cấp theo `su_kien_dot_bien`), tồn kho và hàng đang về ban đầu, chi phí S, H, MOQ, mức phục vụ.
- Kiểm tra mỗi ngày kho mở cửa: nếu tồn hiện có + hàng đang về ≤ ROP thì đặt hàng. Mất bán khi hết hàng (không nợ đơn).
- ROP = dự báo nhu cầu trong lead time + SS; SS = z·√(σ_LTD² + d²·σ_LT²); σ_LTD = độ lệch chuẩn của **tổng sai số dự báo trong L ngày**, đo trên **validation2**.
- Chỉ dùng dự báo của mốc gần nhất đã qua (không nhìn trước).
- Chính sách: **hiện trạng** (đo từ dữ liệu); **công thức + dự báo mốc** (TB trượt 28); **công thức + dự báo AI** (kết hợp theo nhóm); **AI + hiệu chỉnh lệch** (hệ số theo nhóm XYZ ước lượng trên validation2).
- ⚠️ **Hiện trạng là đối thủ rất mạnh:** trong bộ sinh dữ liệu, người lập kế hoạch dùng đường nhu cầu kỳ vọng của tương lai (biết trước mùa vụ, lễ), chỉ lệch ±10%. Ngoài đời không ai biết trước như vậy. So sánh chính là **AI với dự báo mốc dùng cùng công thức**.

### 10.1. Vòng 1: lượng đặt = EOQ (đã chạy trên test 24/10)

Mức phục vụ 95%:
| Chính sách | Fill Rate | Ngày-SKU thiếu | Tồn TB (triệu đ) | Lần nhập | Chi phí đặt + lưu (triệu đ) | Doanh thu mất (triệu đ) |
|---|---|---|---|---|---|---|
| Hiện trạng | 93,57% | 1.564 | 11.993,6 | 1.910 | 2.766,8 | 22.016,2 |
| Công thức + dự báo mốc | 88,83% | 1.050 | 15.808,5 | 3.085 | 3.704,3 | 34.163,8 |
| Công thức + dự báo AI | 93,16% | 916 | 13.049,1 | 3.091 | 3.119,0 | 23.562,2 |
| AI + hiệu chỉnh lệch | 95,34% | 785 | 15.341,0 | 3.025 | 3.562,0 | 17.991,7 |

**Phát hiện (khi xem kết quả test vòng 1):** ở nhóm Z, chính sách AI giữ tồn 11,1 tỷ so với 6,3 tỷ của hiện trạng; 5 SKU **chỉ bán dịp lễ** (cây thông Noel, bánh quy Noel, đồ hóa trang và kẹo Halloween, dây đèn LED) chiếm 4,0/4,7 tỷ chênh lệch. Ví dụ cây thông Noel: AI đáp ứng 78% nhưng tồn TB gấp ~8,8 lần hiện trạng. Cơ chế: gần lễ dự báo tăng vọt → ROP vọt → công thức đặt nhiều lần EOQ → hàng về sau khi mùa đã qua → vừa thiếu trong mùa, vừa tồn đến cuối năm. **EOQ giả định nhu cầu đều**, không hợp với hàng thời vụ (hạn chế kinh điển, cần viết vào Chương 2 và Chương 4).

### 10.2. Vòng 2: chọn quy tắc lượng đặt trên validation (luật viết ngày 24/10, TRƯỚC khi chạy)

Vì phát hiện trên đến từ tập test, việc sửa **không được chọn trên test**. Luật:
- Ứng viên quy tắc lượng đặt: (1) **EOQ** như vòng 1; (2) **đặt đến mức**: lượng đặt = dự báo trong (L + 7) ngày + SS − (tồn + hàng đang về), tối thiểu MOQ; (3) **lai**: EOQ cho nhóm X/Y, đặt đến mức cho nhóm Z.
- Mô phỏng trên **giai đoạn validation2** (01/10/2024–29/09/2025, có Noel 2024, Tết 2025, Halloween, Trung thu), mức phục vụ 95%, cùng thiết kế như trên, với 2 chính sách AI (có / không hiệu chỉnh lệch). σ_LTD và hệ số hiệu chỉnh đều lấy từ validation2 (trong mẫu, như nhau cho mọi ứng viên).
- **Tiêu chí:** chi phí liên quan thấp nhất = chi phí đặt hàng + chi phí lưu kho + **lợi nhuận mất** (đơn vị thiếu × (giá bán − giá vốn)). Chọn cặp (quy tắc lượng đặt, chính sách AI) có chi phí liên quan thấp nhất.
- Quy tắc lượng đặt được chọn áp dụng **cho mọi chính sách theo công thức** (cả dự báo mốc), rồi chạy một lần trên test để báo cáo. Kết quả vòng 1 giữ nguyên trong báo cáo.

**Kết quả bước chọn trên validation2** (`reports/ton_kho_chon_quy_tac.md`, mức phục vụ 95%):
| Quy tắc | Chính sách | Fill Rate | Tồn TB (tỷ đ) | Đặt + lưu (tỷ đ) | Lợi nhuận mất (tỷ đ) | Chi phí liên quan (tỷ đ) |
|---|---|---|---|---|---|---|
| **EOQ** ✅ | **AI + hiệu chỉnh** | 95,40% | 15,02 | 3,55 | 2,00 | **5,55** |
| EOQ | AI | 93,39% | 12,83 | 3,11 | 2,75 | 5,86 |
| Lai | AI + hiệu chỉnh | 95,89% | 17,07 | 4,01 | 1,85 | 5,86 |
| Lai | AI | 94,15% | 13,78 | 3,38 | 2,61 | 5,99 |
| Đặt đến mức | AI | 93,82% | 14,21 | 3,67 | 2,52 | 6,19 |
| Đặt đến mức | AI + hiệu chỉnh | 95,50% | 17,53 | 4,30 | 1,90 | 6,20 |

→ Theo luật, **giữ EOQ** và chọn **AI + hiệu chỉnh lệch**. Quy tắc "đặt đến mức"/"lai" giảm thiếu hàng nhưng tăng tồn kho nhiều hơn phần lợi nhuận cứu được. Vấn đề hàng chỉ bán dịp lễ (mục 10.1) **chưa giải quyết được bằng quy tắc lượng đặt đơn giản** → ghi vào hạn chế và hướng phát triển (chính sách riêng cho hàng thời vụ: đặt một lần trước mùa kiểu "người bán báo" (newsvendor), dừng đặt khi hàng về sau mùa).


## 11. Mô phỏng và bảng trước–sau ✅ (24/10)

Quy tắc lượng đặt EOQ (chọn trên validation2), 12 tháng test, 121 SKU, mức phục vụ 95% (`reports/ton_kho_so_sanh.md`, CSDL `v_so_sanh_chinh_sach`). Chi phí liên quan = chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do thiếu hàng.

| KPI | Hiện trạng ⚠️ | Công thức + dự báo mốc | Công thức + dự báo AI | **AI + hiệu chỉnh lệch** |
|---|---|---|---|---|
| Fill Rate | 93,57% | 88,83% | 93,16% | **95,34%** |
| Số ngày-SKU thiếu hàng | 1.564 | 1.050 | 916 | **785** |
| Tồn kho TB (triệu đ) | **11.993,6** | 15.808,5 | 13.049,1 | 15.341,0 |
| Số lần nhập hàng | **1.910** | 3.085 | 3.091 | 3.025 |
| Chi phí đặt + lưu (triệu đ) | **2.766,8** | 3.704,3 | 3.119,0 | 3.562,0 |
| Lợi nhuận mất (triệu đ) | 3.693,3 | 5.603,6 | 3.960,7 | **2.976,7** |
| **Chi phí liên quan (triệu đ)** | **6.460,1** | 9.307,9 | 7.079,7 | 6.538,7 |

**So sánh chính (cùng công thức, chỉ khác dự báo): AI + hiệu chỉnh so với dự báo mốc:** Fill Rate +6,5 điểm (88,83% → 95,34%); ngày-SKU thiếu −25%; tồn kho −3,0%; chi phí đặt + lưu −3,8%; lợi nhuận mất −47%; **chi phí liên quan −29,8%** (9,31 → 6,54 tỷ đ).

**So với hiện trạng** (đối thủ biết trước nhu cầu kỳ vọng): Fill Rate +1,8 điểm, ngày-SKU thiếu −50%, lợi nhuận mất −19%, nhưng tồn kho +28% và số lần nhập +58% (EOQ đặt nhỏ, nhiều lần); chi phí liên quan gần bằng (+1,2%).

**Theo nhóm (95%):**
| Nhóm | Chính sách | Fill Rate | Tồn TB (triệu đ) | Lợi nhuận mất (triệu đ) |
|---|---|---|---|---|
| X (ổn định) | AI + hiệu chỉnh | **95,4%** | 3.714,9 | **2.244,2** |
| X | Hiện trạng | 93,8% | 5.180,2 | 2.749,6 |
| X | Dự báo mốc | 95,3% | 4.199,1 | 2.553,4 |
| Y | AI + hiệu chỉnh | 98,1% | 543,9 | 128,6 |
| Y | Hiện trạng | 97,9% | 473,0 | 138,6 |
| Z (mùa vụ) | AI + hiệu chỉnh | **94,4%** | 11.082,2 | **603,8** |
| Z | Hiện trạng | 91,9% | **6.340,5** | 805,0 |
| Z | Dự báo mốc | 69,5% | 10.903,2 | 2.804,9 |

- **Hàng ổn định (X):** chính sách AI thắng **cả hiện trạng** dù hiện trạng biết trước nhu cầu: đáp ứng cao hơn (95,4% so với 93,8%) mà tồn kho **thấp hơn 28%**.
- **Hàng mùa vụ (Z):** AI đáp ứng cao hơn nhưng tồn gần gấp đôi hiện trạng, do 5 SKU chỉ bán dịp lễ (mục 10.1).
- **Độ nhạy mức phục vụ:** chi phí liên quan của AI + hiệu chỉnh: 90% → 6,90 tỷ; 95% → 6,54; 99% → 6,18. Chi phí thiếu hàng (lợi nhuận mất) lớn so với chi phí lưu kho nên mức phục vụ cao hơn có lợi hơn. Chưa đổi mức chính (95% đã chốt trước); nếu muốn đổi phải chọn lại trên validation.

**Đối chiếu tiêu chí thành công (mục 1c `docs/09`):** Fill Rate ≥ 95% ✅ (95,34%); "tồn kho không cao hơn hiện trạng" ❌ (+28%, chủ yếu do hàng chỉ bán dịp lễ; nhóm X thì thấp hơn 28%); giảm thiếu hàng ✅; giảm tổng chi phí so với hiện trạng: gần bằng (+1,2%), so với dự báo mốc −30% ✅.

### 11.1. Thử độ nhạy: hàng về trễ và chi phí tăng ✅ (23/10)

**Chạy:** `python src/do_nhay.py` (~2 phút, sau `ton_kho.py`) → CSDL (`kich_ban_do_nhay`, `ket_qua_do_nhay`, khung nhìn `v_do_nhay`), `reports/do_nhay.md`, hình `reports/ket_qua/k07_do_nhay_lead_time.png`; dashboard khu ④ có phần "Thử độ nhạy".

**Cách làm:** dùng lại nguyên hàm mô phỏng của `ton_kho.py` (cùng nhu cầu thật, cùng lead time ngẫu nhiên, cùng dự báo), mỗi lần chỉ đổi **một** yếu tố, mức phục vụ 95%, quy tắc EOQ. Kịch bản lấy từ `docs/07`; mọi mức tác động là **giả định**. Kịch bản gốc (không đổi gì) được script kiểm tra trùng khớp kết quả GĐ F.

| Kịch bản | Cách mô phỏng | Người lập kế hoạch biết trước? |
|---|---|---|
| Tắc cảng +3 / +5 / +7 ngày | Hàng dự kiến về trong 3 tuần tắc cảng thì về trễ thêm k ngày. Chạy **13 đợt** (mỗi 4 tuần một đợt) để không chọn đợt có lợi; giả định mọi SKU bị ảnh hưởng | Không |
| Lead time +2 ngày cả năm (quy định tải trọng) | Mọi đơn về trễ thêm 2 ngày; chạy 2 lần: công thức không cập nhật / có cập nhật lead time (+2, σ tính lại trên validation) | Không / Có |
| Chi phí đặt hàng S +20% (cước tăng) | EOQ tự tính lại theo S mới | Có |
| Chi phí lưu kho H +15% (giá điện, kho lạnh) | EOQ tự tính lại theo H mới | Có |

Hiện trạng chỉ so được ở kịch bản chi phí: đơn hàng của nó lấy từ dữ liệu, không có quy tắc để chạy lại khi lead time đổi.

**Kết quả chính (AI + hiệu chỉnh, so với kịch bản gốc):**

| Kịch bản | Fill Rate | Đổi Fill Rate | Chi phí liên quan | Đổi chi phí |
|---|---|---|---|---|
| Gốc | 95,34% | | 6.538,7 tr đ | |
| Tắc cảng +3 ngày (TB 13 đợt) | 94,80% | −0,54 điểm | 6.923,3 | +5,9% |
| Tắc cảng +5 ngày | 94,32% | −1,02 | 7.264,6 | +11,1% |
| Tắc cảng +7 ngày | 93,80% | −1,54 | 7.584,3 | +16,0% |
| Tắc cảng +7 ngày, đợt xấu nhất (hàng dự kiến về từ 21/01/2026, trước Tết) | 92,20% | −3,14 | 8.132,6 | +24,4% |
| Lead time +2 ngày, **không** cập nhật công thức | 90,01% | **−5,33** | 10.196,3 | **+55,9%** |
| Lead time +2 ngày, **có** cập nhật | 94,44% | −0,90 | 7.261,5 | +11,1% |
| Chi phí đặt hàng +20% | 95,02% | −0,32 | 6.629,5 | +1,4% |
| Chi phí lưu kho +15% | 95,38% | +0,04 | 7.014,0 | +7,3% |

**Nhận xét:**
- **Tắc cảng tạm thời:** Fill Rate chỉ giảm 0,5–1,5 điểm (trung bình). **AI + hiệu chỉnh vẫn có chi phí liên quan thấp nhất trong 3 chính sách theo công thức ở cả 13/13 đợt, với cả 3 mức trễ.** Chi phí của AI tăng nhiều hơn về % (+16,0% so với +9,3% của dự báo mốc khi trễ 7 ngày) vì gốc thấp hơn và tồn sát hơn; tính bằng tiền, AI tăng 1.046 tr đ, dự báo mốc tăng 865 tr đ, AI vẫn rẻ hơn mốc khoảng 2,6 tỷ đ.
- **Đợt nguy hiểm nhất là trước Tết** (hàng dự kiến về 21/01–10/02/2026): đúng lúc tồn kho đang được đẩy lên cho cao điểm. Nếu ngoài đời cuối năm cũng là mùa cảng đông (giả định, cần kiểm chứng với đơn vị thực tập) thì nên đặt sớm hơn hoặc tăng tồn an toàn trước Tết.
- **Lead time dài ra lâu dài nguy hiểm hơn tắc cảng tạm thời** nếu không ai cập nhật tham số: Fill Rate −5,3 điểm, chi phí +56%. Cập nhật lead time vào công thức thì gần như hồi phục (−0,9 điểm). Bài học: **công thức chỉ tốt khi tham số được cập nhật**; cần theo dõi lead time thực tế từng nhà cung cấp hằng tháng.
- **Chi phí tăng:** Fill Rate gần như không đổi. Khoảng cách chi phí liên quan giữa AI + hiệu chỉnh và hiện trạng giãn ra: gốc +1,2%; S +20% → +1,6%; **H +15% → +2,7%**, vì chính sách AI giữ tồn nhiều hơn hiện trạng 28%. Kho lạnh / giá điện tăng thì càng cần giải quyết điểm yếu tồn kho nhóm Z (mục 10.1).

## 12. Dashboard ✅ (xong 23/10, kế hoạch 23–26/11)

**Chạy:** `streamlit run app/dashboard.py` tại thư mục gốc dự án (cần chạy trước `python src/nap_database.py` và `python src/ton_kho.py`). Trình duyệt tự mở `http://localhost:8501`, không cần mạng.

**Nguyên tắc:** dashboard **chỉ đọc** CSDL `data/kho_hang.db` (mở SQLite ở chế độ read-only), không tính lại mô hình hay tồn kho; mọi số lấy từ bảng/khung nhìn do các bước trước ghi, nên luôn khớp với báo cáo. Màu giống hình `reports/ket_qua/` (thực tế đen, AI xanh dương, dự báo mốc cam, hiện trạng xám). Mọi trang ghi "dữ liệu mô phỏng".

**Bản 24/10 (5 khu, người dùng duyệt tăng từ 4 lên 5):** bản đầu chỉ có 1 biểu đồ mỗi khu, còn lại là bảng số và mã kỹ thuật, nên người xem không thấy "dữ liệu nói gì" và thấy số liệu "không thực". Đã thêm khu ① Tổng quan, mỗi biểu đồ kèm **Cách đọc** và **Phát hiện** (phát hiện tính trực tiếp từ dữ liệu, không ghi tay số); thêm ví dụ bằng lời cho bảng cảnh báo và bảng tham số; cột kỹ thuật giấu sau nút "Hiện thêm cột kỹ thuật"; đổi tên cột sang lời dễ hiểu.

| Khu | Nội dung | Đọc từ |
|---|---|---|
| ① Tổng quan dữ liệu | Dữ liệu là gì (121 SKU, 1.096 ngày, 132.616 dòng, 687 dòng lỗi đã sửa); **cái gì thật, cái gì giả định, vì sao vẫn dùng được**; 6 biểu đồ: giá trị xuất kho theo tuần 3 năm kèm Tết / Trung thu / bão Yagi / 11.11; bản đồ mùa vụ nhóm hàng × tháng; thứ trong tuần; khuyến mãi làm bán tăng bao nhiêu (1.332 đợt); ma trận ABC × XYZ; xếp hạng mô hình dự báo | `giao_dich_sach`, `giao_dich_tho`, `nhat_ky_sua_loi`, `lich_su_kien`, `lich_khuyen_mai`, `phan_loai_sku`, `v_xep_hang_mo_hinh` |
| ② Dự báo theo SKU | Chọn SKU (lọc theo nhóm XYZ) → đường thực tế, dự báo AI, dự báo mốc trong 12 tháng test, xem theo ngày hoặc tuần; WMAPE, Bias, số ngày được chấm của riêng SKU đó | `du_bao`, `mo_hinh`, `dm_sku`, `phan_loai_sku` |
| ③ Cảnh báo tồn kho | Chọn một ngày trong năm test làm "hôm nay" → số SKU hết hàng / cần đặt hôm nay / tồn dưới ROP nhưng hàng đang về / đủ hàng; biểu đồ số mặt hàng cần chú ý mỗi ngày cả năm; ví dụ bằng lời cho từng loại cảnh báo; bảng chi tiết (tồn, ROP, hàng đang về, lượng đặt, đủ bán bao nhiêu ngày); biểu đồ "răng cưa" tồn kho và ROP của 1 SKU, so với hiện trạng | `mo_phong_ngay`, `v_du_bao_chon`, `tham_so_ton_kho`, `giao_dich_sach` |
| ④ Trước – sau | Chọn mức phục vụ 90/95/99% → 4 chỉ số chính của chính sách đề xuất so với dự báo mốc và hiện trạng; 4 biểu đồ cột nhỏ (mỗi chỉ số một trục); bảng trước – sau toàn kho và theo nhóm XYZ; thử độ nhạy (mục 11.1) | `v_so_sanh_chinh_sach`, `ket_qua_ton_kho` |
| ⑤ Tham số SS / ROP / EOQ | Chọn chính sách, mức phục vụ, lọc ABC/XYZ, tìm theo tên → giải thích bằng lời cho 1 mặt hàng; biểu đồ tiền nằm trong hàng dự phòng theo nhóm và Fill Rate từng mặt hàng; bảng SS, ROP, EOQ bình quân, SS đủ bán bao nhiêu ngày, MOQ, lead time, σ sai số, hệ số hiệu chỉnh và kết quả mô phỏng từng SKU; tải CSV; công thức | `tham_so_ton_kho`, `ket_qua_ton_kho`, `dm_sku` |

**Hàng đang về** (khu ③) không lưu trong CSDL nên tính theo bảo toàn: hàng đang về đầu kỳ + tổng đã đặt − tổng đã nhận. Đã kiểm tra trên cả 3 chính sách theo công thức: không ngày nào âm; mọi SKU "tồn dưới ROP mà không đặt" đều có tồn + hàng đang về > ROP, đúng quy tắc đặt hàng của `ton_kho.py`.

**Kiểm tra:** chạy tự động bằng `streamlit.testing` (đổi SKU, nhóm, ngày, chính sách, mức phục vụ, bộ lọc: không lỗi); số ở khu ④ khớp `reports/ton_kho_so_sanh.md` (theo giá thị trường 24/10: Fill Rate 95,34%, 785 ngày-SKU thiếu, chi phí liên quan 6,54 tỷ đ, −29,8% so với dự báo mốc); chụp màn hình cả 5 khu trên Edge.

**Ví dụ để demo:** ngày 09/02/2026 (8 ngày trước Tết), chính sách đề xuất: 0 SKU hết hàng, 11 SKU cần đặt hôm nay, 43 SKU tồn dưới ROP nhưng hàng đang về, 67 SKU đủ hàng (số liệu theo giá thị trường 24/10; với giá mô phỏng cũ là 1 / 5 / 44 / 71).

**Giới hạn:** khu ③ là **phát lại** kết quả mô phỏng, không phải hệ thống chạy hằng ngày; chưa có nút duyệt đơn; dữ liệu theo ngày chỉ lưu cho mức phục vụ 95%.

## 13. Hạn chế và việc còn treo

**Hạn chế đã biết:**
- **Chính sách tồn kho:** "hiện trạng" trong dữ liệu mô phỏng là người lập kế hoạch biết trước nhu cầu kỳ vọng (lệch ±10%), mạnh hơn thực tế; EOQ không hợp với 5 SKU chỉ bán dịp lễ (tồn sau mùa); mô phỏng mất bán (không nợ đơn), nhận hàng vào ngày kho mở cửa, tồn và hàng đang về ban đầu lấy xấp xỉ từ dữ liệu.
- **Lợi thế "biết đề" của dữ liệu mô phỏng:** mô hình dùng đúng lịch lễ và lịch khuyến mãi mà bộ sinh dữ liệu đã dùng; trên dữ liệu thật, cửa sổ lễ phải tự ước lượng nên mức cải thiện (Prophet −41% so với Seasonal Naive) nhiều khả năng thấp hơn.
- Toàn bộ kết quả trên **dữ liệu mô phỏng**; mức tác động của bão, ngày lễ, khuyến mãi là giả định của người lập dữ liệu, nên độ chính xác tuyệt đối không phản ánh kho thật. Giá trị của đồ án nằm ở quy trình và ở việc so sánh tương đối giữa các mô hình.
- Mô hình dự báo biết lịch lễ và khuyến mãi chính xác; ngoài đời lịch khuyến mãi có thể đến muộn hoặc thay đổi.
- Hiệu ứng sale chỉ mô phỏng cho 11.11, 12.12, Black Friday; các sale khác chưa có.
- Dữ liệu chưa mô phỏng: tăng giá xăng, tắc cảng, ngày lương, rằm/mùng 1, SKU mới và ngừng bán (xem `docs/01` mục 6). Tắc cảng và chi phí tăng đã được **thử độ nhạy ở bước tồn kho** (mục 11.1), nhưng chưa có trong dữ liệu gốc.
- **Thử độ nhạy (mục 11.1):** mức trễ và mức tăng chi phí là giả định; giả định mọi SKU cùng bị tắc cảng (thực tế chỉ hàng nhập khẩu); chưa mô phỏng riêng hiện tượng "các lô trễ về dồn 1–2 ngày" của `docs/07`; hiện trạng không so được khi lead time đổi.

**Kho thật cần mà mô hình chưa có** (ghi vào Chương 5, phần hạn chế và hướng phát triển):
- **Hạn sử dụng:** có sữa, sữa chua, kem nhưng mô phỏng coi hàng giữ bao lâu cũng được; ngoài đời tồn nhiều thì hàng cận hạn, phải giảm giá hoặc hủy. Hướng phát triển: thêm hạn sử dụng theo SKU, xuất hàng theo FEFO (hết hạn trước xuất trước), tính chi phí hủy.
- **Giới hạn sức chứa:** diện tích kho, kho lạnh, số chuyến xe nhận hàng mỗi ngày (cửa nhận hàng), ngân sách mua hàng. Chính sách AI tồn nhiều hơn hiện trạng 28% có thể vượt sức chứa kho lạnh dịp Tết.
- **Điều kiện mua hàng:** giảm giá khi mua nhiều, gom đơn nhiều mã của cùng nhà cung cấp cho đủ xe/container; mô hình đặt từng SKU riêng lẻ.
- **Lịch đặt hàng cố định:** mô hình cho đặt bất kỳ ngày kho mở cửa; thực tế mỗi nhà cung cấp thường chỉ nhận đơn vài ngày cố định trong tuần (kiểm tra định kỳ, cần tồn an toàn lớn hơn).
- **Tần suất cập nhật dự báo:** 28 ngày làm mới một lần; kho thật thường làm mới mỗi tuần, bắt kịp thay đổi nhanh hơn.
- **Lệch tồn sổ sách và tồn thực:** mô hình tin số tồn luôn đúng; ngoài đời có hư hỏng, mất mát, nhập sai, cần kiểm kê định kỳ.
- **Hàng thay thế:** hết hàng một mã thì khách có thể mua mã cùng loại; mô hình tính là mất bán hoàn toàn (lợi nhuận mất có thể bị phóng đại). Khuyến mãi một mã cũng làm giảm bán mã cùng loại, mô hình chưa xét.
- **Khách chờ hàng (nợ đơn):** mô hình giả định hết hàng là mất bán; với khách B2B thường chờ giao sau.
- **Một kho duy nhất:** chưa xét nhiều kho, nhiều chi nhánh và chuyển hàng giữa các kho.
- **Mã hàng mới:** chưa có lịch sử thì không dự báo được (cần dự báo theo mã tương tự).
- Lịch nghỉ Tết trong dữ liệu là 7 ngày cố định.

**Việc đang treo:**
- [ ] Hỏi giảng viên: dùng dữ liệu mô phỏng cho Chương 4 có được không. (Ngày bảo vệ đã có: 30–31/12/2026.)
- [ ] Xin đơn vị thực tập file xuất–nhập–tồn theo ngày, ít nhất 12 tháng (hạn chót nhận: 08/11).
- [ ] Số liệu chưa thống nhất giữa các tài liệu (xem `docs/01`, mục "Điểm chưa nhất quán"): tỷ lệ hết hàng 1,8% trong Excel so với 3,05% đo được; cửa sổ bão.

## 14. Nhật ký thực hiện

| Ngày | Việc đã làm | File | Kết quả chính | Quyết định / lý do |
|---|---|---|---|---|
| 10/10 | Làm sạch dữ liệu | `src/lam_sach.py` | Sửa 687 dòng, loại 198 dòng trùng, 0 dòng sai so với đáp án | Dùng đẳng thức kho thay cho nội suy/IQR |
| 10/10 | Tạo lịch khuyến mãi theo SKU; sửa lỗi tràn số trên Windows | `src/sinh_du_lieu.py`, `data/reference/lich_khuyen_mai.csv` | 1.338 đợt; dựng lại khớp đáp án 132.616/132.616 dòng | Khuyến mãi phải có lịch tham chiếu để không dùng answer_key |
| 10/10 | Chuyển 2 file Word sang Markdown | `src/docx_sang_md.py`, `docs/02b`, `docs/08` | | Để AI và người đọc tra cứu nhanh |
| 10/10 | Tạo đặc trưng | `src/dac_trung.py` | 64 cột, cờ khớp đáp án 100%, 0 rò rỉ tương lai | ABC/XYZ tính trên train; B2B chỉ để loại |
| 10/10 | Phân tích khám phá | `src/eda.py` | 8 hình, xu hướng đi ngang, Chủ nhật 0,53 lần | Sửa cách tính khuyến mãi (so cùng tháng) |
| 10/10 | Khung đánh giá | `src/danh_gia.py` | Mốc Seasonal Naive test WMAPE 0,773 | Bão không biết trước; chia 24 tháng train / 12 tháng test |
| 10/10 | Lập lộ trình theo lịch trường | `docs/09_lo_trinh.md` | Nộp 09/12; 8 tuần làm việc | Bỏ LSTM; viết song song với chạy mô hình |
| 23/10 | Mô hình mốc (GĐ C) | `src/mo_hinh_baseline.py`, `src/tong_hop_ket_qua.py` | Mốc tốt nhất: TB trượt 28, WMAPE 0,640 (giảm 17,2% so SN7); nhóm Z vẫn sai 127% | ARIMA chỉ chạy nhóm A vì quá chậm; không mở rộng vì không hơn Croston |
| 23/10 | Bản nháp Chương 1 (Mở đầu) | `do_an/chuong_1_mo_dau.md` | Đủ 7 mục: lý do, mục tiêu, câu hỏi, phạm vi, phương pháp, ý nghĩa, bố cục | Tên đề tài theo báo cáo GĐ1, cần đối chiếu quyết định giao đề tài; Chương 3 đổi thành "Mô tả bài toán và dữ liệu" nếu không có dữ liệu thật |
| 24/10 | Prophet (GĐ D) | `src/mo_hinh_prophet.py` | Test WMAPE 0,454 (−29% so TB trượt 28, −41% so SN7); nhóm Z 1,272 → 0,638; thắng 11/13 mốc | Chọn additive trên validation; loại 5 sự kiện không biết trước khỏi khung đánh giá; 4 tiến trình vì RAM; chặn máy ngủ khi chạy |
| 24/10 | LightGBM (GĐ D) | `src/mo_hinh_lightgbm.py` | Test WMAPE 0,400 (tốt nhất theo ngày, thắng Prophet 12/13 mốc) nhưng Bias +11,6% (nhóm Z +40,8%, thiếu trước cao điểm) | Lag ≥ 28 để dự báo 28 ngày không đệ quy; tweedie chọn trên validation; GĐ E sẽ chọn/kết hợp theo nhóm trên validation |
| 24/10 | Chọn mô hình (GĐ E), 2 vòng | `src/chon_mo_hinh.py` | Vòng 1 chọn LightGBM (validation không có Tết); vòng 2 chọn **kết hợp theo nhóm** (X 0,9 · Y 1,0 · Z 0,6 LightGBM): test WMAPE 0,376, tuần 0,235, Bias +6,2% | Vòng 2 chỉ đổi tập validation (cùng mùa với test, sớm 1 năm); cấu hình mô hình và luật chọn giữ nguyên, ghi trước khi có kết quả |
| 24/10 | Luồng hệ thống + cơ sở dữ liệu (nhiệm vụ GVHD) | `database/schema.sql`, `src/nap_database.py`, `src/tao_trang_luong.py`, `trinh_bay/luong_he_thong.html` | SQLite 14 bảng + 3 khung nhìn, 1,39 triệu dòng; 7/7 kiểm tra toàn vẹn đạt; trang 3 phần chạy không cần mạng | SQLite vì GVHD không yêu cầu loại CSDL và cần chạy được khi bảo vệ; trang tự sinh từ CSDL để số liệu luôn khớp |
| 24/10 | Tồn kho + mô phỏng (GĐ F) | `src/ton_kho.py` (đọc/ghi CSDL) | AI + hiệu chỉnh (EOQ): Fill Rate 95,36%, chi phí liên quan −31% so với dự báo mốc, ≈ hiện trạng; nhóm X thắng cả hiện trạng; tồn nhóm Z cao | Lỗi EOQ với hàng chỉ bán dịp lễ phát hiện trên test → thử quy tắc khác, chọn trên validation2 theo luật ghi trước: vẫn EOQ |
| 23/10 | Dashboard (GĐ G) | `app/dashboard.py`, `.streamlit/config.toml` | 4 khu (dự báo theo SKU, cảnh báo tồn kho theo ngày, trước – sau, bảng SS/ROP/EOQ); số khớp `reports/ton_kho_so_sanh.md`; kiểm tra tự động không lỗi | Chỉ đọc CSDL, không tính lại gì, để số trên dashboard luôn khớp báo cáo; cảnh báo theo ngày là phát lại mô phỏng, ghi rõ trên trang |
| 23/10 | Chuẩn bị dữ liệu Power BI | `src/xuat_power_bi.py`, `docs/12_power_bi.md` | 6 CSV (3 danh mục + 3 sự kiện), Fill Rate, chi phí, WMAPE 0,376 tự đối chiếu với CSDL; hướng dẫn 5 buổi cho người mới | Streamlit vẫn là bản demo; Power BI học sau khi nộp (11–26/12) để làm kỹ năng xin thực tập; hàng đang về và trạng thái cảnh báo dùng chung hàm `csdl.py` với dashboard |
| 23/10 | Thử độ nhạy (GĐ F bổ sung) + bổ sung hạn chế | `src/do_nhay.py`, `reports/do_nhay.md`, k07 | Tắc cảng +3/+5/+7 ngày (13 đợt): Fill Rate AI + hiệu chỉnh −0,5/−1,0/−1,5 điểm, vẫn rẻ nhất 13/13 đợt; lead time +2 ngày không cập nhật: −5,3 điểm, chi phí +52%, cập nhật thì −0,8 điểm; H +15%: chênh chi phí với hiện trạng lên +3,3% | Chạy tắc cảng ở 13 thời điểm để không chọn đợt có lợi; mỗi kịch bản chỉ đổi 1 yếu tố; bổ sung 10 hạn chế "kho thật cần mà mô hình chưa có" vào mục 13 |
| 24/10 | Dashboard thêm khu Tổng quan + dễ đọc hơn | `app/dashboard.py` | 5 khu; 6 biểu đồ phân tích dữ liệu, mỗi biểu đồ có "cách đọc" + "phát hiện" tự tính (Chủ nhật bán 0,53; khuyến mãi trung vị +58%; 22 mã A-X = 65,5% giá trị; đồ chơi tháng 9 ×10,5); ví dụ bằng lời ở bảng cảnh báo và bảng tham số; nói rõ cái gì thật / giả định | Người dùng thấy dashboard chỉ có 1 biểu đồ, nhiều bảng số khó hiểu, "không thực"; đồng ý tăng từ 4 lên 5 khu |
| 24/10 | Loại kho + giá theo thị trường, chạy lại từ đặc trưng | `src/cap_nhat_gia.py`, `data/reference/gia_thi_truong.csv`, `src/cham_lai.py` | 37/121 mã đổi giá (trung vị ×1,20), 11 mã đổi nhóm ABC; mô hình chọn không đổi (test WMAPE 0,375); AI + hiệu chỉnh Fill Rate 95,34%, chi phí liên quan 6,54 tỷ, −29,8% so với dự báo mốc; tồn so với hiện trạng +28%; tắc cảng vẫn rẻ nhất 39/39 | Dữ liệu là kho tổng chuỗi bán lẻ (khớp nhất); giá bán = giá bán lẻ tra công khai, giá vốn giữ biên lãi cũ (giả định); không sinh lại dữ liệu gốc; **từ dòng này trở đi số liệu theo giá thị trường**, các dòng trước theo giá mô phỏng cũ |

*(Thêm dòng mới ở cuối bảng sau mỗi lần làm xong một việc.)*

## 15. Danh mục file kết quả

| File | Nội dung |
|---|---|
| `reports/bao_cao_lam_sach.md` | Báo cáo làm sạch chi tiết |
| `reports/bao_cao_dac_trung.md` | Báo cáo đặc trưng và đối chiếu đáp án |
| `reports/bao_cao_eda.md`, `reports/eda/` | Nhận xét và 8 hình khám phá |
| `reports/ket_qua_mo_hinh.csv` | Bảng điểm mọi mô hình (1 dòng / mô hình / tập) |
| `reports/du_bao/` | Dự báo chi tiết từng ngày (không lưu git, tạo lại được) |
| `docs/09_lo_trinh.md` | Lộ trình và lịch theo tuần |
| `app/dashboard.py` | Dashboard Streamlit 5 khu, chỉ đọc CSDL (`streamlit run app/dashboard.py`) |
| `reports/do_nhay.md`, `reports/ket_qua/k07_do_nhay_lead_time.png` | Thử độ nhạy: tắc cảng, lead time dài thêm, chi phí tăng (mục 11.1); tạo bằng `python src/do_nhay.py` |
| `data/reference/gia_thi_truong.csv`, `reports/cap_nhat_gia.md` | Giá bán lẻ tra cứu từng mã (nguồn, ngày) và bảng giá cũ – mới; bản giá mô phỏng gốc: `data/reference/sku_master_mo_phong.csv` |
| `reports/power_bi/` | 6 file CSV cho Power BI (mô hình hình sao) + `so_doi_chieu.md`; tạo bằng `python src/xuat_power_bi.py`; hướng dẫn `docs/12_power_bi.md` |
