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

- **Mô hình được chọn: kết hợp theo nhóm XYZ** (dự báo chi tiết: `reports/du_bao/ket_hop_theo_nhom_v2_test.csv`). Đây là mô hình dùng cho GĐ F đến 30/10; từ 31/10 thay bằng `ket_hop_v3` (mục 9.4).
- Validation vòng 2 **đại diện tốt hơn**: lộ ra đúng điểm yếu của LightGBM (Bias validation +12,9%, sát mức +11,7% trên test), trong khi vòng 1 chỉ thấy +4,8%. Thứ hạng trên validation vòng 2 khớp với thứ hạng trên test (kết hợp theo nhóm tốt nhất ở cả hai).
- Trọng số hợp lý về nghiệp vụ: hàng ổn định (X, Y) dựa gần hết vào LightGBM; hàng mùa vụ (Z) lấy 40% từ Prophet để giảm thiếu hàng trước cao điểm.
- Trên test: WMAPE **0,375**, WMAPE tuần **0,234**: tốt nhất trong mọi mô hình đã thử; giảm **51%** so với Seasonal Naive (0,773) và **41%** so với mô hình mốc tốt nhất (TB trượt 28: 0,640).
- **Còn hạn chế:** Bias +6,3%, vẫn dự báo thiếu nhẹ, **vượt ngưỡng ±5%** của tiêu chí thành công; nhóm Z còn thiếu 20,3%. Cần xử lý ở GĐ F (ví dụ hiệu chỉnh độ lệch **ước lượng trên validation vòng 2**, hoặc để tồn kho an toàn bù), không chỉnh bằng cách nhìn test.

**Bài học phương pháp (đưa vào Chương 4):** tập validation phải **cùng đặc điểm** với giai đoạn sẽ áp dụng mô hình (ở đây: có mùa cao điểm). Validation "êm" chọn nhầm mô hình chính xác trung bình nhưng thiếu hàng đúng lúc cao điểm.

### 9.4. Vòng 3: nâng cấp dự báo (luật ghi ngày 30/10, TRƯỚC khi chạy)

**Vì sao:** chẩn đoán (validation 2 / test, chỉ đọc kết quả có sẵn) cho thấy (1) dự báo 1–7 ngày tới không chính xác hơn 15–28 ngày tới (kết hợp: 0,368 so với 0,409 trên validation 2) vì LightGBM chỉ dùng số bán từ 28 ngày trước trở về, trong khi 58% mã có lead time ≤ 7 ngày; (2) nhóm Z dự báo thiếu có hệ thống (Bias +27% validation 2), 3 mốc tệ nhất đều ngay trước Tết / Trung thu; (3) nhóm X chủ yếu là nhiễu ngẫu nhiên. Tham khảo phương pháp thắng cuộc thi M5 (LightGBM chung nhiều chuỗi, kết hợp nhiều mô hình theo tầm dự báo).

**Cải tiến thử, lần lượt, mỗi bước chồng lên bước trước nếu được giữ** (script `src/nang_cap_du_bao.py`, giữ nguyên cấu hình tweedie của vòng 1):
1. **A – Dự báo theo tầm:** 3 mô hình LightGBM cho ngày thứ 1–7, 8–14, 15–28 sau mốc; mỗi mô hình dùng số bán gần nhất được phép (tầm h ngày dùng giá trị trễ ≥ h: trễ 7/14/28 và trung bình trượt tính đến thời điểm đó).
2. **B – Đặc trưng theo lịch sự kiện (biết trước):** số ngày đến / sau Trung thu, Noel, Halloween, khai giảng, Valentine, 8/3, 20/10, 20/11, 1/6, lễ 30/4–2/9, sự kiện thể thao (đã có cho Tết); **số bán cùng ngày âm lịch năm trước** (dịch theo khoảng cách giữa 2 Tết / 2 Trung thu gần nhất), vì Tết và Trung thu lệch vài tuần mỗi năm theo dương lịch.
3. **F – Dò tham số** LightGBM (số lá, tốc độ học, số cây, độ cong tweedie, số mẫu tối thiểu mỗi lá): 8 cấu hình chọn trước, ngẫu nhiên có hạt giống cố định.
4. Ghép lại với Prophet theo nhóm XYZ, dò trọng số trên validation 2 (như vòng 2).

**Luật giữ / bỏ (giống luật chọn mô hình vòng 1–2):** mỗi bước chỉ giữ nếu **WMAPE validation 2 giảm ít nhất 0,005** và **|Bias| validation 2 không tăng quá 1 điểm %**. Mô hình ghép cuối chỉ thay mô hình đang dùng (kết hợp theo nhóm v2, WMAPE validation 2 = 0,388) nếu đạt cùng luật. **Tập test chạy một lần** cho cấu hình cuối, chỉ để báo cáo, giữ kết quả dù tốt hay xấu. Báo thêm (không dùng để chọn) **WMAPE trên tổng lead time** của từng mã, chỉ số gắn với quyết định đặt hàng.

**Lưu ý trung thực:** dữ liệu mô phỏng dùng đúng lịch sự kiện này để tạo nhu cầu, nên mức cải thiện của B ngoài đời nhiều khả năng thấp hơn (giống lưu ý với Prophet, mục 8.1).

**Kết quả vòng 3 (chạy 30–31/10, `reports/nang_cap_du_bao.md`):**

| Bước (validation 2) | WMAPE | Bias | WMAPE nhóm Z | WMAPE trên lead time | Theo luật |
|---|---|---|---|---|---|
| Gốc (tái lập LightGBM cũ, khớp 0,4028) | 0,403 | +12,9% | 0,666 | 0,272 | — |
| A – dự báo theo tầm | 0,392 | +11,8% | 0,627 | 0,208 | ✅ giữ |
| B – thêm lịch sự kiện + số bán cùng ngày âm lịch | 0,385 | +10,2% | 0,597 | 0,208 | ✅ giữ |
| F – dò 8 cấu hình tham số (tốt nhất F6) | 0,384 | +9,8% | 0,600 | 0,199 | ❌ bỏ (chỉ giảm 0,0016) |
| Ghép với Prophet (w LightGBM X 0,9 · Y 1,0 · Z 0,7) | **0,379** | +7,1% | 0,573 | 0,216 | ✅ thay mô hình v2 (0,388) |

Kiểm tra rò rỉ: đặc trưng âm lịch và trễ 7 ngày không lấy giá trị nào từ ngày chưa qua; giá trị khớp đúng số bán cùng ngày âm lịch năm trước.

**Test (chạy một lần, chỉ báo cáo):** mô hình mới `ket_hop_v3` WMAPE **0,368** (v2: 0,376), WMAPE tuần **0,226** (0,234), **Bias +3,9%** (+6,3%) → **lần đầu đạt tiêu chí ±5%**; nhóm Z 0,496 (0,546); WMAPE trên lead time 0,233 (0,240); nhóm X kém đi nhẹ 0,319 (0,311). Giảm 52% so với Seasonal Naive.

**Nhận xét:** độ chính xác tăng nhờ **cách dùng dữ liệu đúng nghiệp vụ** (dùng số bán gần nhất cho dự báo ngắn hạn, so theo âm lịch), không nhờ chỉnh tham số. Lợi ích dự báo ngắn hạn trên test (−7% WMAPE lead time của LightGBM) nhỏ hơn nhiều so với validation 2 (−23%). Từ 31/10 mô hình dùng cho tồn kho là `ket_hop_v3` (`nap_database.MO_HINH_DUOC_CHON`); kết quả tồn kho mục 10–12 đã chạy lại theo mô hình này.

### 9.5. Vòng 4: rủi ro, tự hiệu chỉnh, cập nhật hằng tuần, khoảng dự báo (luật ghi ngày 31/10, TRƯỚC khi chạy)

**Lý do (chẩn đoán `ket_hop_v3` trên validation2, chỉ đọc):** WMAPE 0,379. **Sàn sai số** (sai số còn lại nếu biết đúng nhu cầu kỳ vọng từng ngày; nhu cầu mô phỏng là nhị thức âm, phương sai (cv·μ)² + μ, cv là tham số bộ sinh, chỉ dùng để đối chiếu) ≈ **0,285** (X 0,267 · Y 0,310 · Z 0,342), nên phần còn cải thiện được ≈ 0,094, chủ yếu ở nhóm Z (0,573 so với sàn 0,342). Nguồn sai số: cửa sổ bão 17% sai số, dự báo thiếu 20%; cửa sổ Tết 12%, thiếu 19%; nhóm Z thiếu 25%; ngày thứ 15–28 của mỗi đợt chiếm 58% sai số (WMAPE 0,408 so với 0,349 ở ngày 1–7). Theo tuần WMAPE 0,242, theo tháng × nhóm XYZ 0,100.

**Luật chung:** chọn và báo cáo trên **validation2** (13 mốc 30/09/2024–01/09/2025). **Test giữ kín** (người dùng quyết định 31/10): không chạy, không chấm, không mô phỏng tồn kho trên test; số tồn kho trên test ở mục 10–12 giữ theo `ket_hop_v3`. Vì chọn và báo cáo cùng một tập, mọi bước học từ sai số chỉ dùng **dữ liệu đã có thực tế tại mốc dự báo** (ngày ≤ mốc) — mốc k chỉ học từ các mốc trước. Ngưỡng giữ như vòng 3: WMAPE giảm ≥ 0,005 và |Bias| không tăng quá 0,01, so trên cùng các dòng chấm. Các bước làm theo thứ tự B1 → B2 → B3 → B4; mỗi bước so với phiên bản đang giữ.

- **B1 – Tự hiệu chỉnh lệch từ sai số đã qua:** hệ số r = Σ thực tế / Σ dự báo trên các dòng đã có thực tế tại mốc, theo nhóm XYZ × tầm (ngày 1–7, 8–14, 15–28); co về 1: r* = 1 + (r − 1)·n / (n + 500), n = số dòng; kẹp [0,8; 1,25]; mốc đầu không hiệu chỉnh. Dự báo mới = dự báo × r*.
- **B2 – Cảnh báo bão ngắn hạn:** giả định cảnh báo phát **4 ngày trước** ngày bão vào (ngoài đời 3–5 ngày), kèm cấp độ bão m (cột `muc_do_0_1`). Áp cho ngày [vào − 3, vào − 1] (trước bão) và [vào, vào + 10] (sau bão). Hệ số theo nhóm hàng × giai đoạn: u = 1 + β·m, β = (Σ thực tế / Σ mức nền − 1) / m tính trên **các trận bão đã kết thúc trước ngày cảnh báo** (trận đầu của validation2 chỉ học từ Yagi 09/2024); mức nền = trung bình số bán cùng mã 28 ngày trước cửa sổ; kẹp u trong [0,7; 3]. Báo cáo thêm WMAPE riêng cửa sổ bão. **Bổ sung luật (31/10, trước khi chạy B2):** khi lập bảng rủi ro (B5) thấy cửa sổ bão Yagi (04–17/09/2024) nằm trọn trong cửa sổ Trung thu (cờ sự kiện áp cho cả lịch), nên tác động bão không tách được khỏi Trung thu. Vì vậy, khi ước lượng β: bỏ các ngày nằm trong cửa sổ sự kiện biết trước (Tết, Trung thu, Noel, Halloween), vì mô hình đã có đặc trưng cho các sự kiện này, tính thêm là tính trùng; bỏ mã có mức nền < 1 đơn vị/ngày. Hệ quả: Yagi không dùng được, trận đầu của validation2 không hiệu chỉnh (u = 1). Lý do dựa trên lịch biết trước, không dựa trên kết quả validation2.
- **B3 – Cập nhật dự báo mỗi tuần:** chạy lại `lgb_v3_AB` và `prophet_addi` với mốc cách nhau **7 ngày** (thay vì 28) trên validation2, ghép cùng trọng số v3; mỗi ngày dùng dự báo của mốc mới nhất trước nó; áp lại B1/B2 nếu được giữ (học online theo mốc tuần). So với phiên bản 28 ngày đang giữ trên cùng các ngày. Báo cáo thêm mô phỏng tồn kho **validation2** (AI + hiệu chỉnh, EOQ, 95%, giữ nguyên hệ số hiệu chỉnh và σ của v3): Fill Rate, chi phí liên quan.
- **B4 – Khoảng dự báo 80% / 95%:** trên phiên bản cuối, theo nhóm XYZ × tầm, lấy phân vị của tỉ số thực tế / dự báo (dự báo ≥ 1; dự báo < 1 thì phân vị của thực tế) trên dòng đã có thực tế tại mốc; khoảng = [dự báo × q_thấp, dự báo × q_cao] (80%: q10–q90; 95%: q2,5–q97,5). Làm cho cả **tổng nhu cầu trong lead time** của từng mã ở mỗi mốc (theo nhóm XYZ). Đạt nếu tỉ lệ thực tế rơi vào khoảng lệch không quá ±3 điểm so với danh nghĩa, tính từ mốc thứ 3. Không chỉnh lại nếu không đạt; báo cáo đúng con số.
- **B5 – Bảng rủi ro định lượng:** từ dữ liệu đến 30/09/2025 (không dùng giai đoạn test): mỗi loại rủi ro (bão, nắng nóng, rét đậm, dịch cúm, sốt xuất huyết, tin đồn giá, thể thao, đơn B2B, đứt gãy cung ứng, Tết, hết hàng) — số lần / năm, số ngày, nhóm hàng chịu tác động, tác động lên nhu cầu (trung vị, p10–p90 của thực tế / mức nền), biết trước bao lâu, hệ thống xử lý bằng cách nào. Chỉ mô tả, không chọn mô hình.

Script: `src/nang_cap_du_bao_v4.py` (`--buoc rui_ro | B1 | B2 | B3 | B4 | bao_cao`); báo cáo `reports/nang_cap_du_bao_v4.md`, `reports/rui_ro_du_bao.md`.

**Kết quả vòng 4 (chạy 31/10, validation2; test vẫn kín):**

| Bước | WMAPE | Bias | Theo luật |
|---|---|---|---|
| Đang giữ `ket_hop_v3` (mỗi 28 ngày) | 0,379 | +7,1% | |
| B1 – tự hiệu chỉnh lệch | 0,383 | +3,5% | ❌ bỏ: lệch giảm một nửa nhưng WMAPE tăng |
| B2 – cảnh báo bão 4 ngày trước | 0,384 | +5,8% | ❌ bỏ: cửa sổ bão WMAPE 0,450 → 0,483 |
| **B3 – cập nhật dự báo mỗi tuần** | **0,358** | +5,5% | ✅ giữ (giảm 0,021) |
| Sàn sai số (đối chiếu) | ≈ 0,286 | | |

Gộp theo tuần (lịch): v3 0,242 → **0,208**; theo tháng × nhóm XYZ: 0,100 → **0,076**.

- **Tồn kho validation2** (AI + hiệu chỉnh, EOQ, 95%, giữ hệ số hiệu chỉnh và σ của v3): cập nhật mỗi tuần cho Fill Rate **96,44%** (v3: 94,83%), tồn kho TB **10.743** triệu đ (14.675, **−27%**), chi phí liên quan **4.305** triệu đ (5.517, **−22%**). Kiểm tra: LightGBM và Prophet chạy mốc tuần tái lập đúng dự báo cũ ở 13 mốc trùng lịch 28 ngày (lệch ≤ 5·10⁻¹³); khung mô phỏng tái lập đúng 94,83% / 5.516,8 của v3.
- **B4 khoảng dự báo** (học online, đánh giá từ mốc 25/11/2024): theo ngày, thực tế nằm trong khoảng 80% là **79,7%**, khoảng 95% là **95,7%** (độ rộng trung vị khoảng 80% ≈ ±52% dự báo); tổng nhu cầu trong lead time: **77,4%** / **93,5%** (độ rộng ≈ ±27%) → **đạt** (lệch ≤ 3 điểm). Ví dụ SKU009 mốc 20/01/2025: 7/7 ngày thực tế nằm trong khoảng 80%; tổng 3 ngày chờ hàng dự báo 1.127 (khoảng 80%: 872–1.454), thực tế 781 → nằm ngoài khoảng 80%, trong khoảng 95%.
- **B5 bảng rủi ro** (`reports/rui_ro_du_bao.md`, dữ liệu đến 30/09/2025): nắng nóng làm kem / đông lạnh ×2,7, đồ uống ×1,6; bão (bỏ ngày trùng Trung thu) thực phẩm khô ×1,45, y tế ×1,35; khuyến mãi trung vị ×1,5 (3,8 đợt / mã / năm); đơn B2B ×6 (17 đơn / năm); rét đậm trùng 100% Tết / Noel → không tách được.
- **B2 chạy 2 lần:** lần đầu có lỗi code (giai đoạn "trước bão" không được học); sửa rồi chạy lại, kết luận như nhau.

**Nhận xét:** (1) với sai số theo ngày, dự báo **hơi thấp hơn trung bình lại tối ưu** (con số làm WMAPE nhỏ nhất là trung vị, thấp hơn trung bình khi nhu cầu lệch phải), nên sửa lệch ở khâu dự báo (B1) làm WMAPE tệ đi; lệch nên xử lý ở khâu tồn kho (hệ số hiệu chỉnh) như hệ thống đang làm. (2) Rủi ro hiếm (bão) không sửa được bằng hệ số cố định khi chỉ có 1–2 trận để học; xử lý bằng khoảng dự báo và tồn kho an toàn. (3) Cải thiện lớn nhất đến từ **quy trình** (dùng số liệu mới nhất mỗi tuần), không từ mô hình phức tạp hơn. **Chưa đưa vào tồn kho trên test / CSDL / dashboard** vì test đang giữ kín; khi mở test thì chạy một lần theo luật.

### 9.6. Mở test và đưa "cập nhật mỗi tuần" vào hệ thống (luật ghi ngày 31/10, TRƯỚC khi chạy test)

Người dùng quyết định mở test (31/10). Test **chạy một lần, chỉ báo cáo**; sau khi xem test không chỉnh mô hình, khoảng dự báo hay quy tắc đặt hàng.

- **Mô hình `ket_hop_v4`:** `lgb_v3_AB` (cấu hình vòng 3) và Prophet additive (như v3 trên test) chạy với mốc cách nhau 7 ngày trên test (49 mốc, 30/09/2025–01/09/2026), ghép theo trọng số v3 (X 0,9 · Y 1,0 · Z 0,7). Không hiệu chỉnh lệch, không cảnh báo bão (B1, B2 đã bỏ). Chấm điểm trên **bản mới nhất cho mỗi ngày** (cách dùng thật); báo cáo kèm `ket_hop_v3` (mỗi 28 ngày) trên cùng các dòng.
- **Dự báo mốc cũng cập nhật mỗi tuần** (`tb_truot_28_tuan`, cùng hàm `tb_truot_28`, mốc 7 ngày, validation2 và test) để so sánh AI – mốc không lẫn lợi ích của việc cập nhật thường xuyên; chấm theo bản mới nhất.
- **Khoảng dự báo 80 / 95%:** cách B4, học online qua các mốc validation2 rồi test (mốc k chỉ học từ dòng đã có thực tế tại mốc); báo cáo tỉ lệ phủ trên test theo ngày (bản mới nhất) và tổng lead time.
- **Hệ thống:** chọn `ket_hop_v4` (`nap_database.MO_HINH_DUOC_CHON`); bảng `du_bao` lưu đủ mọi mốc tuần (thêm cột khoảng `thap_80, cao_80, thap_95, cao_95`); khung nhìn `v_du_bao_chon` và mọi nơi hiển thị / tổng hợp lấy **bản mới nhất mỗi ngày**. Tồn kho (`ton_kho.py`): khoảng cách mốc lấy từ dữ liệu dự báo; chính sách dự báo mốc dùng `tb_truot_28_tuan`; hệ số hiệu chỉnh và σ tính lại từ dự báo tuần trên validation2 (cùng công thức); chọn quy tắc lượng đặt trên validation2 như cũ rồi chạy test. Thử độ nhạy, biểu đồ, Power BI, dashboard chạy lại theo mô hình mới. Các kết quả 28 ngày (`ket_hop_v3`) giữ trong báo cáo để so sánh.

**Kết quả test (chạy 01/11, một lần):**

| Test | `ket_hop_v4` (cập nhật mỗi tuần) | `ket_hop_v3` (mỗi 28 ngày) |
|---|---|---|
| WMAPE theo ngày | **0,356** | 0,368 |
| Bias | +3,0% | +3,9% |
| WMAPE theo tuần | 0,203 | 0,226 |
| Nhóm Z | 0,477 | 0,496 |
| Tổng nhu cầu trong lead time | 0,214 | 0,233 |
| Dự báo mốc TB trượt 28 ngày | 0,584 (cập nhật tuần) | 0,640 (mỗi 28 ngày) |

Khoảng dự báo trên test: theo ngày, thực tế nằm trong khoảng 80% là **80,9%**, khoảng 95% là **96,0%**; tổng nhu cầu trong lead time **81,3% / 95,5%** — khớp mức danh nghĩa. Kiểm tra: LightGBM, Prophet, TB trượt chạy mốc tuần tái lập đúng dự báo 28 ngày ở 13 mốc trùng (lệch ≤ 10⁻¹²). Kết quả tồn kho trên test: mục 10.4 và 11.

### 9.7. Vòng 5: mô hình học sâu LSTM và RNN (luật ghi ngày 02/11, TRƯỚC khi chạy)

Yêu cầu: thêm mô hình học sâu vào so sánh. **Lưu ý trung thực:** test đã mở ngày 01/11 nên không còn "chưa ai xem"; vì vậy mọi quyết định giữ / bỏ ở vòng này **chỉ dựa trên validation2**, test chỉ để báo cáo.

**Cấu hình (cố định trước khi chạy, không dò thêm):** một mô hình chung cho 121 mã, mã hóa – giải mã: bộ mã hóa đọc 56 ngày gần nhất (nhu cầu tin được, cờ thiếu dữ liệu, lịch), bộ giải mã cho ra 28 ngày tới từ thông tin biết trước (lịch, lễ, sale, khuyến mãi, giá, cùng ngày năm trước và cùng ngày âm lịch năm trước). 2 lớp, 64 đơn vị ẩn, dropout 0,1, học nhúng mã hàng + nhóm hàng; chuẩn hóa theo trung bình từng mã (tính đến mốc). Adam lr 0,001, batch 512, cắt gradient 1. Mỗi mốc đầu học 30 lượt, các mốc sau học tiếp 4 lượt từ trọng số cũ (lr 0,0005); mỗi lượt lấy ngẫu nhiên 40.000 mẫu. Trung bình 3 hạt giống. RNN và LSTM chỉ khác loại ô. Thông tin giống LightGBM: bão, nắng nóng, rét, dịch, tin đồn không đưa vào; ngày hết hàng, ngày nghỉ, đơn B2B không tính vào hàm mất mát; ngày nghỉ dự báo 0. Chạy GPU nên kết quả có thể lệch rất nhỏ nếu chạy lại; file dự báo được lưu làm căn cứ.

**Khác biệt cần ghi rõ:** LightGBM học lại từ đầu ở mỗi mốc, LSTM / RNN học tiếp 4 lượt.

**Luật (ghi trước):**
1. **Hàm mất mát:** LSTM với Tweedie (p = 1,2) và L1, validation2 mốc 28 ngày (13 mốc); chọn WMAPE thấp hơn, chênh dưới 0,005 thì giữ Tweedie (như LightGBM). RNN dùng hàm đã chọn.
2. **Cập nhật mỗi tuần:** LSTM và RNN chạy validation2 mốc 7 ngày, chấm trên bản mới nhất mỗi ngày (như `ket_hop_v4`).
3. **Ghép:** mô hình học sâu tốt hơn (WMAPE validation2) ghép với `ket_hop_v4`: dự báo = w × học sâu + (1 − w) × `ket_hop_v4`, w theo nhóm XYZ, dò 0; 0,1; …; 1 trên validation2 → `ket_hop_v5`.
4. **Thay mô hình đang dùng** chỉ khi một ứng viên (LSTM, RNN, `ket_hop_v5`) làm WMAPE validation2 giảm **≥ 0,005** so với `ket_hop_v4` (0,358) **và** |Bias| không tăng quá 1 điểm. Nhiều ứng viên đạt thì lấy WMAPE thấp nhất. Không đạt thì **hệ thống giữ nguyên `ket_hop_v4`**.
5. **Test:** LSTM, RNN và `ket_hop_v5` (trọng số giữ nguyên từ validation2) chạy một lần, chỉ báo cáo, xem xong không chỉnh gì.

**Kết quả (chạy 02/11):**

| Mô hình | Validation2 WMAPE | Validation2 Bias | Test WMAPE | Test Bias |
|---|---|---|---|---|
| `ket_hop_v4` (đang dùng) | 0,358 | +5,5% | 0,356 | +3,0% |
| LSTM | 0,384 | +7,5% | 0,355 | +5,2% |
| RNN | 0,395 | +5,6% | 0,349 | +7,2% |
| `ket_hop_v5` (v4 + LSTM, w X 0,6 · Y 0,4 · Z 0,1) | 0,351 | +7,7% | 0,351 | +4,8% |

- **Luật 1:** Tweedie 0,445, L1 0,415 → chọn L1 (giảm ≥ 0,005).
- **Luật 4, quyết định theo validation2: giữ `ket_hop_v4`.** LSTM, RNN có WMAPE cao hơn; `ket_hop_v5` giảm WMAPE 0,0065 (đạt) nhưng |Bias| tăng 2,2 điểm (vượt mức 1 điểm).
- **Ghi nhận trung thực:** trên test cả 3 ứng viên có WMAPE **thấp hơn** `ket_hop_v4`, đổi lại Bias cao hơn (dự báo thiếu nhiều hơn). Theo luật không đổi quyết định vì test đã mở và chênh lệch nhỏ. Validation2 bắt đầu khi mới có 1 năm dữ liệu, test có từ 2 năm trở lên; có thể học sâu cần nhiều dữ liệu hơn, nhưng **chưa kiểm chứng** nguyên nhân này. Khi có dữ liệu mới phải chạy lại vòng so sánh, không mặc định mô hình nào thắng.
- **Kiểm tra:** đổi toàn bộ nhu cầu sau mốc thành số rác, mọi đầu vào của mô hình không đổi (không nhìn trước). Báo cáo: `reports/mo_hinh_dl.md`.

### 9.8. Kiểm chứng trên dữ liệu thật M5 (luật ghi ngày 03/11, TRƯỚC khi chạy)

Mục đích: xem **quy trình** hoạt động thế nào trên nhu cầu thật và hệ thống có chịu được dữ liệu khác không. Không dùng để đổi mô hình của bộ dữ liệu mô phỏng; kết quả báo cáo riêng.

**Dữ liệu và làm sạch (cố định trước khi xem kết quả, `src/nguon/m5.py`, có test):** số bán giữ nguyên, cộng 10 cửa hàng thành kho tổng. Mẫu 121 mã, ngẫu nhiên phân tầng theo phòng ban, hạt giống 20261103, không xem số bán. Ngày trước khi mã lên kệ không chấm điểm. Ngày tổng toàn chuỗi dưới 20% trung vị là ngày đóng cửa. Sự kiện lấy từ lịch M5, cửa sổ −3…+1 ngày; ngày tem phiếu SNAP là thông tin biết trước. Giá bán lấy trung bình theo mã. Không có khuyến mãi, tồn kho, cờ hết hàng: ngày hết hàng thật **không tách được**, nên sai số và nhu cầu ở các ngày đó bị hiểu thấp.

**Mô hình (giữ nguyên cấu hình đã có, không dò thêm):** trung bình trượt 28 ngày, lặp tuần trước, Prophet additive, LightGBM theo tầm (`lgb_v3_AB`), LSTM, RNN (cấu hình mục 9.7, hàm L1). Tất cả cập nhật mỗi 7 ngày, chấm trên bản mới nhất mỗi ngày. Chia tập theo thời gian, tự suy từ ngày cuối dữ liệu: validation2 và test mỗi tập 1 năm.

**Luật:**
1. Trọng số ghép LightGBM – Prophet (`ket_hop`) và ghép thêm học sâu (`ket_hop_dl`) dò trên **validation2 của M5**, như mục 9.2 và 9.7.
2. Mô hình tốt nhất của M5 chọn trên validation2: WMAPE thấp nhất, chênh dưới 0,005 thì lấy phương án đơn giản hơn. Test chạy một lần, chỉ báo cáo.
3. **Câu hỏi kiểm chứng ghi trước:** (a) mô hình chọn có thấp hơn trung bình trượt trên test không; (b) thứ hạng các mô hình có giống dữ liệu mô phỏng không; (c) mức giảm sai số so với trung bình trượt lớn đến đâu so với mức 39% trên dữ liệu mô phỏng. Báo cáo cả khi kết quả bất lợi.
4. Hệ thống gãy ở đâu thì ghi lại và sửa có test, kiểm tra kết quả trên dữ liệu mô phỏng không đổi.
5. Phần tồn kho trên M5 là bán thực nghiệm vì lead time, giá vốn, chi phí đều giả định; làm sau, luật ghi riêng.

**Kết quả (chạy xong 04/11, xem `du_lieu_nguon/m5/reports/kiem_chung.md`):** mô hình chọn trên validation2 là `ket_hop_dl` (LightGBM + Prophet + RNN). Trên test: WMAPE 0,307, Bias +3,1%; trung bình trượt 0,356; LightGBM 0,314; RNN 0,311; LSTM 0,317; Prophet 0,389; lặp tuần 0,420.

**Trả lời 3 câu hỏi ghi trước:**
- **(a) Có thấp hơn trung bình trượt không: có**, giảm 13,8%.
- **(b) Thứ hạng có giống mô phỏng không: giống một phần.** Trên cả 2 bộ, mô hình ghép và học sâu đứng đầu, sát nhau, Prophet kém LightGBM. **Khác:** trên M5 trung bình trượt (0,356) **tốt hơn Prophet** (0,389), trong khi trên mô phỏng trung bình trượt (0,584) kém xa Prophet (0,454). Mức 0,89 của Prophet lúc thử 2 mốc không lặp lại khi chạy đủ.
- **(c) Mức giảm so với trung bình trượt: 13,8% trên số thật, so với 39% trên mô phỏng**, chỉ bằng khoảng một phần ba. **Đây là số quan trọng nhất:** dữ liệu mô phỏng có quy luật rõ, sinh từ chính các yếu tố mô hình được biết trước, nên làm AI trông tốt hơn nhiều so với trên số bán thật. Con số 39% không được trình bày như hiệu quả dự kiến khi dùng thật.

**Lưu ý:** nhóm Z trên M5 có WMAPE quanh 1 ở mọi mô hình (không dự báo được), nhưng chỉ chiếm khoảng 2% số mã. M5 không có tên hàng, khuyến mãi, cờ hết hàng, nên chưa dùng được đặc trưng khuyến mãi và số bán không phân biệt được nhu cầu với hết hàng. Phần TiDE, N-HiTS, TFT ở mục 9.9.

### 9.9. TiDE, N-HiTS, TFT (luật ghi ngày 03/11, TRƯỚC khi xem sai số)

Tra cứu nghiên cứu: trên dữ liệu bán lẻ cửa hàng, mô hình cây thường thắng mạng nơ-ron (M5; so sánh 2025), nên không kỳ vọng vượt trội; TiDE và N-HiTS nhanh, dùng được thông tin biết trước; TFT dễ giải thích. Chạy bằng NeuralForecast 1.7.5, môi trường riêng `.venv_nf`, `src/mo_hinh_nf.py`, trên **cả dữ liệu mô phỏng và M5**.

**Cấu hình (cố định, chỉ đo thời gian trước khi chốt, không xem sai số):** đọc 56 ngày, dự báo 28 ngày, hàm MAE, nhu cầu chia theo trung bình từng mã, 1 hạt giống, batch 32, cùng thông tin như LSTM (không nhìn trước, có test). **Học lại từ đầu mỗi 28 ngày, cập nhật đầu vào mỗi 7 ngày**, chấm trên bản mới nhất mỗi ngày.
- TiDE: 128 ẩn, 2 lớp mã hóa, 2 lớp giải mã, 1.000 bước. N-HiTS: 3 khối 256 × 256, 1.000 bước.
- **TFT cấu hình gọn:** 32 ẩn, cửa sổ 64, 500 bước, chỉ 8 cờ lịch và 6 giá trị trễ năm trước. Cấu hình 64 ẩn với đủ 69 biến không xong 100 bước trong 7 phút trên RTX 3050 4 GB, nên **TFT bị giới hạn bởi máy và không phản ánh hết năng lực của nó**.

**Khác biệt phải nêu:** LightGBM học lại mỗi mốc, LSTM học tiếp 4 lượt, 3 hạt giống; ba mô hình này học lại mỗi 28 ngày, 1 hạt giống.

**Luật (ghi trước):**
1. So với mô hình đang dùng của từng bộ dữ liệu (mô phỏng: `ket_hop_v4`; M5: mô hình chọn ở mục 9.8).
2. Mô hình tốt nhất trong ba ghép với mô hình đang dùng, w theo nhóm XYZ, dò trên validation2 → `ket_hop_nf`.
3. **Chỉ thay mô hình khi** WMAPE validation2 giảm ≥ 0,005 **và** |Bias| không tăng quá 1 điểm. Không đạt thì giữ nguyên.
4. Test chạy một lần, chỉ báo cáo, không đổi quyết định.

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
| Mô hình | `mo_hinh` (31, cờ `duoc_chon`, `pham_vi`), `ket_qua_mo_hinh` (49), `du_bao` (1.776.656) | |
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
| Công thức + dự báo AI | 94,29% | 880 | 13.982,9 | 3.081 | 3.270,9 | 22.049,1 |
| AI + hiệu chỉnh lệch | 95,91% | 752 | 16.377,3 | 3.035 | 3.721,7 | 18.652,2 |

**Phát hiện (khi xem kết quả test vòng 1):** ở nhóm Z, chính sách AI giữ tồn 12,1 tỷ so với 6,3 tỷ của hiện trạng; 5 SKU **chỉ bán dịp lễ** (cây thông Noel, bánh quy Noel, đồ hóa trang và kẹo Halloween, dây đèn LED) chiếm 5,2/5,8 tỷ chênh lệch. Ví dụ cây thông Noel: AI đáp ứng 81% nhưng tồn TB gấp ~15 lần hiện trạng (số theo mô hình v3). Cơ chế: gần lễ dự báo tăng vọt → ROP vọt → công thức đặt nhiều lần EOQ → hàng về sau khi mùa đã qua → vừa thiếu trong mùa, vừa tồn đến cuối năm. **EOQ giả định nhu cầu đều**, không hợp với hàng thời vụ (hạn chế kinh điển, cần viết vào Chương 2 và Chương 4).

### 10.2. Vòng 2: chọn quy tắc lượng đặt trên validation (luật viết ngày 24/10, TRƯỚC khi chạy)

Vì phát hiện trên đến từ tập test, việc sửa **không được chọn trên test**. Luật:
- Ứng viên quy tắc lượng đặt: (1) **EOQ** như vòng 1; (2) **đặt đến mức**: lượng đặt = dự báo trong (L + 7) ngày + SS − (tồn + hàng đang về), tối thiểu MOQ; (3) **lai**: EOQ cho nhóm X/Y, đặt đến mức cho nhóm Z.
- Mô phỏng trên **giai đoạn validation2** (01/10/2024–29/09/2025, có Noel 2024, Tết 2025, Halloween, Trung thu), mức phục vụ 95%, cùng thiết kế như trên, với 2 chính sách AI (có / không hiệu chỉnh lệch). σ_LTD và hệ số hiệu chỉnh đều lấy từ validation2 (trong mẫu, như nhau cho mọi ứng viên).
- **Tiêu chí:** chi phí liên quan thấp nhất = chi phí đặt hàng + chi phí lưu kho + **lợi nhuận mất** (đơn vị thiếu × (giá bán − giá vốn)). Chọn cặp (quy tắc lượng đặt, chính sách AI) có chi phí liên quan thấp nhất.
- Quy tắc lượng đặt được chọn áp dụng **cho mọi chính sách theo công thức** (cả dự báo mốc), rồi chạy một lần trên test để báo cáo. Kết quả vòng 1 giữ nguyên trong báo cáo.

**Kết quả bước chọn trên validation2** (`reports/ton_kho_chon_quy_tac.md`, mức phục vụ 95%):
| Quy tắc | Chính sách | Fill Rate | Tồn TB (tỷ đ) | Đặt + lưu (tỷ đ) | Lợi nhuận mất (tỷ đ) | Chi phí liên quan (tỷ đ) |
|---|---|---|---|---|---|---|
| **EOQ** ✅ | **AI + hiệu chỉnh** | 94,83% | 14,68 | 3,46 | 2,06 | **5,52** |
| Lai | AI + hiệu chỉnh | 95,53% | 16,08 | 3,79 | 1,78 | 5,57 |
| Lai | AI | 93,59% | 13,24 | 3,25 | 2,55 | 5,80 |
| EOQ | AI | 93,00% | 12,61 | 3,06 | 2,81 | 5,87 |
| Đặt đến mức | AI + hiệu chỉnh | 95,07% | 16,50 | 4,07 | 1,88 | 5,96 |
| Đặt đến mức | AI | 93,24% | 13,56 | 3,52 | 2,54 | 6,05 |

→ Theo luật, **giữ EOQ** và chọn **AI + hiệu chỉnh lệch**. Quy tắc "đặt đến mức"/"lai" giảm thiếu hàng nhưng tăng tồn kho nhiều hơn phần lợi nhuận cứu được. Vấn đề hàng chỉ bán dịp lễ (mục 10.1) **chưa giải quyết được bằng quy tắc lượng đặt đơn giản** → ghi vào hạn chế và hướng phát triển (chính sách riêng cho hàng thời vụ: đặt một lần trước mùa kiểu "người bán báo" (newsvendor), dừng đặt khi hàng về sau mùa).


### 10.3. Vòng 3: tồn kho an toàn theo phân phối sai số thực (luật ghi ngày 31/10, TRƯỚC khi chạy)

**Vì sao:** công thức hiện tại SS = z·√(σ_LTD² + d²·σ_LT²) giả định sai số dự báo trong lead time **phân phối chuẩn, đối xứng**. Nhưng mô hình dự báo thiếu có hệ thống (Bias dương) và nhóm mùa vụ lệch về một phía (thiếu nhiều trước cao điểm), nên z·σ dễ đặt dự phòng sai chỗ: thừa ở hàng ổn định, thiếu ở hàng mùa vụ. Tài liệu dự báo phân vị / hiệu chỉnh conformal đề xuất lấy thẳng **phân vị thực nghiệm** của sai số thay cho giả định chuẩn.

**Ứng viên** (đều dùng sai số trên **validation2**, như σ_LTD hiện tại; không nhìn test):
- **C0 (hiện tại):** SS = z·√(σ_LTD² + d²·σ_LT²).
- **C1 – phân vị thực nghiệm theo mã:** thay z·σ_LTD bằng phân vị mức phục vụ (90 / 95 / 99%) của **tổng sai số dự báo trong L ngày** (thực tế − dự báo, đã hiệu chỉnh lệch nếu chính sách có hiệu chỉnh), đo trên mọi cửa sổ L ngày của validation2: SS = √(max(q, 0)² + (z·d·σ_LT)²). Mã có dưới 20 cửa sổ thì dùng phân vị của sai số đã chuẩn hóa theo nhóm XYZ.
- **C2 – như C1 nhưng phân vị theo nhóm XYZ** (gộp sai số chuẩn hóa theo nhu cầu bình quân), ít nhiễu hơn cho mã có ít dữ liệu.

**Luật chọn (giống GĐ F vòng 2, mục 10.2):** mô phỏng trên validation2 (01/10/2024–29/09/2025), mức phục vụ 95%, quy tắc lượng đặt EOQ, chính sách AI + hiệu chỉnh; chọn ứng viên có **chi phí liên quan thấp nhất** (đặt hàng + lưu kho + lợi nhuận mất). Chỉ thay C0 nếu chi phí liên quan giảm **ít nhất 1%** và Fill Rate không giảm quá 0,5 điểm. Sau đó chạy test một lần, áp dụng cho mọi chính sách theo công thức. **Lưu ý:** σ_LTD / phân vị đo trên chính validation2 rồi mô phỏng trên validation2 là "trong mẫu", như nhau cho mọi ứng viên (giống mục 10.2); kết luận cuối dựa trên test.

### 10.4. Vòng 4: chọn lại quy tắc lượng đặt với dự báo cập nhật mỗi tuần (01/11, theo luật mục 10.2 và 9.6)

Cùng luật mục 10.2 (mô phỏng validation2, 95%, chi phí liên quan thấp nhất), dự báo `ket_hop_v4` cập nhật mỗi tuần (`reports/ton_kho_chon_quy_tac.md`):

| Quy tắc | Chính sách | Fill Rate | Tồn TB (tỷ đ) | Đặt + lưu (tỷ đ) | Lợi nhuận mất (tỷ đ) | Chi phí liên quan (tỷ đ) |
|---|---|---|---|---|---|---|
| **Lai** ✅ | **AI + hiệu chỉnh** | 96,83% | 10,04 | 2,56 | 1,49 | **4,05** |
| EOQ | AI + hiệu chỉnh | 96,34% | 10,64 | 2,64 | 1,73 | 4,36 |
| Đặt đến mức | AI + hiệu chỉnh | 96,31% | 10,40 | 2,84 | 1,61 | 4,45 |
| Lai | AI | 95,29% | 9,19 | 2,44 | 2,10 | 4,54 |
| EOQ | AI | 94,83% | 9,60 | 2,45 | 2,27 | 4,72 |
| Đặt đến mức | AI | 94,57% | 9,55 | 2,72 | 2,26 | 4,98 |

→ Với dự báo mới hơn, quy tắc **lai** (EOQ cho X/Y, **đặt đến mức** cho nhóm Z) thắng EOQ (vòng 2 với dự báo 28 ngày thì ngược lại): khi dự báo được cập nhật mỗi tuần, lượng "đặt đủ đến lần đặt sau" của hàng mùa vụ không còn dựa trên dự báo cũ nên không đặt quá tay. Áp dụng cho mọi chính sách theo công thức rồi chạy test một lần (mục 11). Hàm "Thử nếu…" của dashboard (`csdl.de_xuat_ngay`) bổ sung quy tắc đặt đến mức; tái lập đúng 127.776 / 127.776 dòng ROP và lượng đặt của mô phỏng tuần.

### 10.5. Chỉ số kho (02/11)

`src/chi_so_kho.py` (hàm thuần, test `tests/test_chi_so_kho.py`), báo cáo `reports/chi_so_kho.md`, hiển thị ở màn Kịch bản & kết quả. Vòng quay = giá vốn hàng xuất quy ra 1 năm ÷ tồn kho bình quân; số ngày tồn kho = tồn kho bình quân ÷ giá vốn xuất 1 ngày; tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng ra quyết định; bỏ 28 ngày cuối kỳ).

**Ghi nhận trung thực:** chính sách đề xuất có vòng quay và số ngày tồn tương đương hiện trạng, nhưng tồn dư cao hơn (xem báo cáo); phần lớn tồn dư nằm ở hàng theo dịp thuộc nhóm Z, vì mô phỏng không có giảm giá thanh lý hay trả hàng. Dữ liệu mô phỏng.

### 10.6. Gom đơn theo nhà cung cấp (luật ghi ngày 03/11, TRƯỚC khi chạy)

Hiện mô phỏng coi mỗi mã đặt riêng, chi phí đặt S tính riêng từng dòng. Thực tế các mã cùng nhà cung cấp đi chung một phiếu nên phần chi phí chung (lập phiếu, xử lý, giao nhận) được chia sẻ. `src/gom_don.py`, có test, chỉ đọc CSDL, **mô phỏng đang dùng và các số đã báo cáo không đổi**.

**Giả định (dữ liệu không có):** chi phí 1 phiếu = t × S lớn nhất trong phiếu + (1 − t) × tổng S các dòng, nên phiếu 1 dòng đúng bằng S cũ. **t = 0,5 là giả định**, báo cáo cả t = 0,3 và 0,7. Mỗi mã vẫn về theo lead time riêng. Không xét gom đủ xe, không xét chiết khấu số lượng.

- **Mức 1, gom cùng ngày:** quyết định đặt hàng giữ nguyên; tồn kho, Fill Rate không đổi, chỉ giảm chi phí đặt.
- **Mức 2, đặt kèm:** khi 1 mã của nhà cung cấp phải đặt, mã khác cùng nhà cung cấp đặt kèm nếu trong kho + đang về ≤ ROP + k ngày nhu cầu dự báo; k thử 1, 2, 3, 5. Khi k = 0 mô phỏng phải **trùng từng dòng** với `mo_phong_ngay` (có test).

**Luật:**
1. Chính sách AI + hiệu chỉnh lệch, mức phục vụ 95%, quy tắc lai. Chọn k trên validation2 với t = 0,5.
2. **Chỉ dùng đặt kèm** nếu so với mức 1, chi phí liên quan giảm ≥ 0,5% **và** Fill Rate không giảm quá 0,2 điểm; nhiều k đạt thì lấy chi phí thấp nhất. Không đạt thì chỉ gom cùng ngày.
3. Test chạy một lần, chỉ báo cáo.

**Kết quả (chạy 03/11):** xem `reports/gom_don.md`. Theo luật, chọn **đặt kèm k = 1** (validation2: chi phí liên quan giảm 3,1% so với chỉ gom cùng ngày, Fill Rate tăng). Trên test, t = 0,5: gom cùng ngày giảm số phiếu 3.285 → 2.404 dòng/phiếu, chi phí liên quan 5.842,8 → 5.778,3 triệu đ (−1,1%), tồn kho và Fill Rate không đổi; đặt kèm k = 1 còn 1.783 phiếu, chi phí liên quan 5.566,0 triệu đ (−4,7%), Fill Rate 96,16%, tồn kho 12.204,8 triệu đ (+2,5%).

**Ghi nhận trung thực:** phần lớn lợi ích của đặt kèm đến từ giảm lợi nhuận mất (hàng được đặt sớm hơn, có tác dụng như tăng dự phòng), không phải từ chia sẻ chi phí phiếu; mức tiết kiệm chi phí đặt phụ thuộc giả định t. Chưa xét gom đủ xe; mỗi mã vẫn về theo lead time riêng dù cùng nhà cung cấp (lead time trong dữ liệu mô phỏng khác nhau tới 3–15 ngày trong cùng một nhà cung cấp, chưa sát thực tế). **Chính sách trong hệ thống chưa đổi**; dashboard chỉ hiện mức 1.

### 10.7. Chấm điểm nhà cung cấp và cảnh báo giao chậm (luật ghi ngày 03/11, TRƯỚC khi chạy)

`src/cham_diem_ncc.py`, có test, chỉ đọc CSDL, không đổi mô phỏng. Dữ liệu lead time là **mô phỏng** nên chỉ minh họa phương pháp, không đánh giá nhà cung cấp thật. Mô phỏng luôn giao đủ hàng nên chỉ đo đúng hạn, **chưa đo đủ hàng (OTIF)**.

- **Đơn:** các đơn của chính sách AI + hiệu chỉnh, mức phục vụ 95%. Trễ = lead time thực tế − lead time hẹn (trung bình làm tròn). Đúng hạn: trễ ≤ 1 ngày.
- **Điểm (0–100):** 60% tỉ lệ đúng hạn + 40% độ ổn định (lệch chuẩn của trễ từ 5 ngày trở lên: 0 điểm). Trọng số là **giả định**; báo cáo tương quan hạng khi đổi sang 80/20. Xếp loại: Tốt ≥ 85, Trung bình ≥ 70, còn lại Cần theo dõi.
- **Cảnh báo:** trung bình trễ của 8 đơn **đã về** gần nhất của nhà cung cấp ≥ 2 ngày. Không nhìn trước vì chỉ dùng đơn đã về.
- **Chấm cảnh báo bằng sự kiện đã cài trong dữ liệu:** đợt nhà cung cấp giao chậm (`su_kien_dot_bien`). Phát hiện đúng nếu có cảnh báo từ đầu đợt đến 20 ngày sau đợt. Báo nhầm: cảnh báo ngoài mọi đợt giao chậm và đợt bão (bão cũng làm hàng về chậm thật).

**Luật:** ngưỡng trên cố định, không dò. Báo cáo cả validation2 và test, kể cả khi bất lợi. Chỉ có 1 đợt trong mỗi tập, nên **không đủ để kết luận về độ nhạy của cảnh báo**, chỉ để minh họa.

**Kết quả (chạy 03/11):** xem `reports/cham_diem_ncc.md`. Trên test: 3.285 đơn, đúng hạn 77,6%; điểm từ 76,6 (NCC09) đến 64,1 (NCC04); không nhà cung cấp nào đạt loại Tốt; đổi trọng số sang 80/20 thứ hạng gần như không đổi (tương quan hạng 0,99).

**Cảnh báo:** phát hiện đúng đợt giao chậm cài trong dữ liệu ở cả 2 tập, nhưng **chậm**: 18 ngày sau khi đợt NCC11 bắt đầu (test), 21 ngày với NCC07 (validation2), trong khi mỗi đợt chỉ kéo dài khoảng 15 ngày; lý do là cảnh báo chỉ dùng đơn đã về. Trên test có 121 ngày có cảnh báo, không báo nhầm theo định nghĩa, nhưng cửa sổ xét rộng và năm test có nhiều bão nên số 0 không nói lên nhiều; validation2 có 6 báo nhầm. **Kết luận:** dùng để nhận ra nhà cung cấp đang xấu đi, không đủ để phản ứng sớm với một đợt ngắn. Chênh lệch điểm giữa các nhà cung cấp còn do lead time sinh ngẫu nhiên và độ dao động khác nhau của từng mã; chỉ minh họa phương pháp.

### 10.8. Trữ hàng cho phiên livestream: newsvendor hai bước (luật ghi ngày 03/11, TRƯỚC khi chạy)

`src/tru_hang_live.py`, có test, chỉ đọc CSDL, không đổi mô phỏng tồn kho. **Dữ liệu không có phiên livestream nào**, nên phần lớn tham số dưới đây là **giả định** và kết quả chỉ cho thấy phương pháp và độ lớn tương đối, không phải lợi nhuận thật. Giả định bối cảnh: chuỗi có bán online và giao từ chính kho này; Q là hàng đặt thêm và để riêng cho phiên, không lấy vào tồn của siêu thị.

**Nhu cầu một phiên** (đơn đã trừ hủy) = mức nền × quy mô × hệ số deal × (1 − tỉ lệ hủy) × (hệ số bùng nổ nếu lên xu hướng).

| Tham số | Giá trị mặc định | Nguồn |
|---|---|---|
| Mức nền | trung vị nhu cầu ngày thường trong 28 ngày trước đó (bỏ ngày khuyến mãi, ngày nghỉ) | Đo. **Không** dùng dự báo AI vì dự báo ngày có khuyến mãi đã chứa phần tăng, nhân hệ số deal sẽ tính trùng. Mã có mức nền 0 không tính được |
| Hệ số deal | rút ngẫu nhiên từ tỉ số nhu cầu ngày khuyến mãi / mức nền, trước khi vào tập test, ngoài cửa sổ sự kiện | Đo, nhưng trên dữ liệu mô phỏng; khuyến mãi siêu thị không phải deal livestream |
| Quy mô phiên | 1 ngày bán thường | Giả định |
| Thời lượng phiên | 24 giờ | Giả định |
| Xác suất lên xu hướng p | 20% | Giả định |
| Hệ số bùng nổ | phân phối log-đều trong [3; 10] lần | Giả định; cỡ tham chiếu đơn đột biến trong dữ liệu (×4,1–×9,8) |
| Giờ bắt đầu lên xu hướng | đều từ giờ 2 đến 75% thời lượng | Giả định; đúng mô tả "đầu phiên ít người xem" |
| Mức giảm giá / nhãn hàng tài trợ | 15% / 70% phần giảm | Giả định |
| Phí sàn | 8% giá bán sau giảm | Giả định |
| Tỉ lệ hủy đơn | 15% | Giả định |
| Bổ sung nhanh | về sau 6 giờ, phụ phí 5% giá vốn, tối đa 3 ngày bán thường | Giả định |

**Tiền:** lãi 1 đơn vị bán được `m` = giá sau giảm + phần nhãn hàng tài trợ − giá vốn − phí sàn. Thiếu 1 đơn vị: `Cu = m`. Thừa 1 đơn vị, 3 trường hợp: **về kho thường** `Co` = giá vốn × tỉ lệ lưu kho × 30/365; **trả nhà cung cấp** `Co` = 10% giá vốn; **phải xả** `Co` = 40% giá vốn. `m ≤ 0` thì không trữ. Chưa tính uy tín mất khi hết hàng giữa phiên nên `Cu` có thể thấp hơn thực tế.

**Phương án so sánh, cùng một mẫu nhu cầu:**
1. Theo ngày thường, bỏ qua phiên live: Q = mức nền × quy mô.
2. Theo trung bình: Q = trung bình nhu cầu phiên.
3. Newsvendor: Q = phân vị `Cu / (Cu + Co)` của nhu cầu phiên.
4. Hai bước, giữ nguyên Q của phương án 3, bổ sung theo tín hiệu từng giờ.
5. Hai bước, Q đầu chọn lại trên lưới phân vị để lãi kỳ vọng cao nhất.

**Quy tắc bổ sung, không nhìn trước:** từ giờ thứ 3, ước lượng tốc độ = trung bình 3 giờ gần nhất; giờ nào hết hàng thì số bán bị chặn nên giữ tốc độ cao nhất đã thấy. Đặt phần thiếu = tốc độ × số giờ còn lại sau khi hàng về − hàng còn lại lúc hàng về, nếu thiếu ≥ 5% trung bình nhu cầu phiên và hàng về trước khi hết phiên. Ngưỡng cố định, không dò.

**Cách đánh giá:** Q tính trên một mẫu 10.000 phiên, chấm trên mẫu 10.000 phiên độc lập, cho mọi mã có mức nền > 0, mỗi mã 1 phiên. Mức nền lấy theo trung vị 365 ngày cuối.

**Luật kết luận, ghi trước:**
- **Không dùng** việc newsvendor thắng trên chính phân phối giả định làm bằng chứng: lời giải tối ưu theo phân phối đó nên thắng là tất yếu. Bảng này chỉ cho thấy độ lớn.
- **Bằng chứng 1, sai giả định:** Q tính với p = 20% và bùng nổ [3; 10], chấm khi thực tế p là 5%, 10%, 40%, hoặc bùng nổ [2; 5], [5; 20]. Newsvendor được gọi là **bền** ở một trường hợp hàng thừa nếu lãi không thấp hơn phương án 1 và 2 ở **mọi** kịch bản; có kịch bản thua thì báo đúng kịch bản đó.
- **Bằng chứng 2, phần đo được:** dùng hệ số deal đo trước test, nhân mức nền trượt, xem phân vị 50%, 75%, 90% có phủ đúng nhu cầu thật các ngày khuyến mãi trong test không. **Đạt** nếu lệch không quá 5 điểm phần trăm ở cả 3 mức. Phần này không kiểm chứng được bùng nổ.
- **Giá trị theo dõi theo giờ** = lãi phương án 5 − lãi phương án 3, báo theo thời gian hàng về 2, 6, 12, 24 giờ. Đây là **mức chi tối đa** đáng bỏ cho việc theo dõi mỗi phiên, chưa trừ chi phí cài đặt.
- Giả định không sửa sau khi xem kết quả. Muốn đổi thì ghi lý do và báo cả kết quả cũ.

**Kết quả lần 1 (chạy 03/11, giữ nguyên, không xóa):**
- **Hệ số deal (bằng chứng 2): đạt.** Trên 1.008 ngày khuyến mãi của test, phân vị 50%, 75%, 90% phủ 47,5%, 76,2%, 92,0%. Dữ liệu mô phỏng nên cùng một quy luật sinh ra cả hai giai đoạn; phép kiểm này yếu.
- **Sai giả định (bằng chứng 1):** hàng thừa trả nhà cung cấp và phải xả: **bền**. Hàng thừa về kho thường: **không bền**, thua 0,9 triệu đ (khoảng 2,5%) khi p thật là 5%.
- **Giá trị theo dõi theo giờ: ÂM ở gần như mọi ô** (−6,2 đến +0,3 triệu đ toàn kho). Quy tắc bổ sung ghi trước **thua cả việc không làm gì**. Không thể kết luận "theo dõi không có giá trị" từ đây, vì có thêm thông tin thì ít nhất cũng bằng được không làm gì: số âm cho thấy **quy tắc yếu**, không phải thông tin vô ích. Hai lỗi của quy tắc: (1) không xét tiền, đặt cả khi lãi sau phụ phí gần bằng 0 hoặc âm; (2) tin thẳng tốc độ 3 giờ, nên phiên chỉ dao động ngẫu nhiên cũng đặt thêm.

**Luật lần 2 (ghi ngày 03/11, SAU khi đã thấy kết quả lần 1, TRƯỚC khi chạy lần 2). Vì đã thấy kết quả nên đây không còn là kiểm định ghi trước hoàn toàn; báo cả 2 lần.** Mọi giả định giữ nguyên, chỉ đổi quy tắc bổ sung:
- **Xét tiền:** lãi sau phụ phí `m' = m − phụ phí`. `m' ≤ 0` thì không bao giờ bổ sung.
- **Lượng cần:** dùng lại đúng logic newsvendor cho phần còn lại của phiên. Mức đặt đến = phân vị `m' / (m' + Co)` của nhu cầu sau khi hàng về, **với điều kiện** tốc độ 3 giờ gần nhất. Điều kiện này tra từ bảng dựng trên **mẫu thiết kế** (mỗi giờ chia 20 nhóm theo tốc độ), không nhìn vào phiên đang chấm. Nhờ đó tự biết phiên chỉ dao động thì phần lớn trở lại bình thường. Không thêm tham số dò: số nhóm cố định 20.
- Ngưỡng 5%, trần nguồn nhanh, thời gian hàng về: như lần 1.
- **Thêm trần tham chiếu:** lãi nếu biết trước nhu cầu từng phiên (trữ đúng bằng nhu cầu). Khoảng cách từ newsvendor đến trần là giá trị tối đa của mọi thông tin, không riêng theo dõi theo giờ.
- **Thêm độ nhạy phụ phí:** 0%, 2%, 5% giá vốn (hàng về sau 6 giờ).
- **Kết luận:** giá trị theo dõi = lãi hai bước lần 2 (chọn lại Q) − lãi newsvendor. Số dương mới được gọi là có giá trị. **Không sửa quy tắc lần thứ 3 để số đẹp hơn**: kết quả lần 2 thế nào báo thế ấy.

**Kết quả lần 2 (chạy 03/11, xem `reports/tru_hang_live.md`). Các hàng của lần 1 chạy lại khớp đến từng đồng.**

| Giá trị theo dõi, triệu đ toàn kho, hàng về sau 6 giờ | Về kho thường | Trả nhà cung cấp | Phải xả |
|---|---:|---:|---:|
| Quy tắc lần 1 (ghi trước) | −1,6 | −1,3 | −6,1 |
| Quy tắc lần 2 (sửa sau khi thấy lần 1) | −0,9 | +3,5 | +3,4 |

- **Theo dõi theo giờ chỉ có giá trị khi hàng thừa tốn kém.** Hàng thừa về kho thường gần như không mất gì, nên trữ thêm từ đầu là đủ; bổ sung phải trả phụ phí nên không thêm được gì, ở mọi thời gian hàng về. Trả nhà cung cấp và phải xả: có giá trị khi hàng về trong 12 giờ, gần bằng 0 khi về sau 24 giờ. Phụ phí là yếu tố lớn: về kho thường, phụ phí 0% thì giá trị +7,2 triệu đ, 2% còn +0,4, 5% thành −0,9.
- Với hàng thừa về kho thường, quy tắc lần 2 vẫn **âm nhẹ** dù về lý thuyết không làm gì cũng được bằng 0: quy tắc vẫn còn đặt thừa một ít. Theo luật không sửa lần 3.
- **Các số đáng nói nhất không đến từ thuật toán mà từ điều kiện kinh doanh:**
  - Cùng giảm 15%, lãi toàn kho theo mức nhãn hàng tài trợ: 0% → 0,1 triệu đ; 70% → 52,1; 100% → 111,0. Biên gộp chỉ 10–23% nên 9/118 mã bán lỗ ngay ở mặc định.
  - Cách xử lý hàng thừa đổi vốn nên trữ gấp 6 lần: về kho 1.890,6 triệu đ, trả nhà cung cấp 644,9, phải xả 306,4.
  - Trữ theo trung bình là phương án **nguy hiểm** khi hàng thừa tốn kém: lỗ 241,7 triệu đ khi phải xả, vì vài phiên bùng nổ kéo trung bình lên cao hơn hẳn đa số phiên.
- Khoảng cách đến trần: biết trước nhu cầu từng phiên thì lãi 104,6 triệu đ, newsvendor đạt 52,1 ở trường hợp tốt nhất. Phần lớn khoảng này là bất định không thể mua lại bằng theo dõi với giả định hiện tại.

**Giới hạn phải nói rõ:** không có phiên live thật nên mọi số tiền chỉ để so sánh tương đối. Hệ số deal đo từ khuyến mãi siêu thị trong dữ liệu mô phỏng. Quy tắc lần 2 được viết sau khi thấy lần 1 nên kết quả dương của nó nhẹ cân hơn một kiểm định ghi trước. Chưa tính uy tín khi hết hàng, đơn hoàn trả, phần phiên live lấy bớt khách của cửa hàng, và tồn của siêu thị không bị ảnh hưởng vì Q là hàng đặt thêm.

**Trên dashboard (màn Mặt hàng):** nhập mức giảm, tài trợ, khả năng lên xu hướng, quy mô, cách xử lý hàng thừa, thời gian hàng về; hệ thống trả lời nên trữ bao nhiêu và vì sao, kèm đường lãi theo lượng trữ và "Phát lại một phiên" theo giờ. Bán lỗ thì báo không nên trữ và mức tài trợ tối thiểu để hòa vốn.

### 10.9. Đối chiếu giả định với dữ liệu thật Dominick's (luật ghi ngày 04/11, TRƯỚC khi tính)

`src/phan_tich_dominicks.py`, có test, chỉ đọc. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business; chuỗi siêu thị Dominick's Finer Foods, Chicago, khoảng 100 cửa hàng, 09/1989–05/1997, số bán theo tuần. **Đây là số bán thật có giá và lãi gộp, nhưng là siêu thị Mỹ 30 năm trước, không phải Việt Nam và không phải livestream.** Dùng để kiểm tra giả định, không dùng để huấn luyện mô hình của hệ thống. Bỏ ngành thuốc lá (bị điều tiết, không có trong danh mục 121 mã).

**Mức xem xét:** cộng toàn chuỗi theo mã và tuần, vì kho tổng nhìn nhu cầu gộp, không nhìn từng cửa hàng. Số bán chia cho số cửa hàng có bán ngành đó trong tuần, để cửa hàng mở thêm không bị tính thành tăng nhu cầu. Bỏ dòng tài liệu đánh dấu đáng ngờ (`OK = 0`), giá hoặc số bán bằng 0, lãi gộp ngoài khoảng −50% đến 80%. Đơn giá = giá / số món trong gói (theo tài liệu).

**Nhận ra tuần khuyến mãi:** tài liệu nói cờ khuyến mãi không đầy đủ (có cờ là có, không có cờ vẫn có thể có). Vì vậy một tuần là khuyến mãi nếu ít nhất 50% cửa hàng có cờ, **hoặc** đơn giá ≤ 95% trung vị đơn giá 8 tuần trước.

**Mức nền, không nhìn trước:** trung vị số bán các tuần không khuyến mãi trong 8 tuần trước, cần ít nhất 3 tuần; đơn giá thường và giá vốn thường tính cùng cách. Cỡ mẫu: mức nền toàn chuỗi ≥ 20 đơn vị/tuần, có ít nhất 10 cửa hàng bán. Hệ số deal lấy ngoài 62 tuần lễ tài liệu liệt kê, để so cùng điều kiện với mô phỏng.

**Câu hỏi và luật kết luận:**
1. **Hệ số deal:** so phân vị 10, 50, 90 và tỉ lệ tuần đạt ×3, ×5, ×10 với mô phỏng (trung vị ×1,47). Trung vị thật lệch quá 25% so với mô phỏng thì ghi là **giả định lệch**.
2. **Phép đo có dùng được cho thời kỳ sau không:** từng ngành lấy 2/3 đầu thời gian để đo, 1/3 sau để kiểm, như mục 10.8: phân vị 50, 75, 90 phải phủ đúng, lệch không quá 5 điểm phần trăm ở cả 3 mức (tính gộp), đồng thời báo số ngành đạt. Đây là phép kiểm **trên số thật**, khác với phép kiểm trên mô phỏng ở 10.8.
3. **Mức tài trợ:** khi giá giảm, nhà sản xuất gánh bao nhiêu = (giá vốn thường − giá vốn tuần đó) / (đơn giá thường − đơn giá tuần đó), tính gộp theo số lượng, chỉ các tuần giảm ≥ 5%. Ngoài khoảng 50–90% thì ghi giả định 70% là **lệch**. Giới hạn: tài liệu nói giá vốn là giá bình quân tồn kho, phản ánh chậm giá mua thật, nên đây chỉ là ước lượng.
4. **Biên lãi gộp thật** so với 10–23% trong danh mục mô phỏng, tách tuần thường và tuần khuyến mãi.
5. **Quan hệ độ sâu giảm giá và số bán:** trung vị hệ số deal theo dải giảm giá, và độ co giãn từ hồi quy log(hệ số) theo log(1 − mức giảm). Mô phỏng hiện không có quan hệ này: hệ số deal không phụ thuộc mức giảm trên màn hình.
6. **Mua trước rồi giảm:** tuần ngay sau khuyến mãi so với mức nền. Trung vị dưới 0,9 thì ghi là có hiện tượng này, và nhu cầu ngay sau phiên live cần được tính đến.
7. **Thử newsvendor bằng hệ số thật:** giá, mức nền, chi phí của 121 mã giữ nguyên. Lượng trữ tính theo (a) hệ số mô phỏng, (b) hệ số thật của 2/3 đầu; chấm trên hệ số thật của 1/3 sau, với p = 20% và p = 0 (không phiên nào bùng nổ). Newsvendor gọi là **bền** như 10.8 nếu lãi không thấp hơn 2 phương án so sánh ở mọi trường hợp. Lãi (a) thấp hơn (b) bao nhiêu chính là cái giá của việc dùng hệ số mô phỏng.

**Giới hạn của cả mục:** bùng nổ của phiên live vẫn là giả định, dữ liệu này không kiểm được. **Kết quả chỉ để báo cáo: không tự đổi giả định mặc định, mô phỏng hay dashboard.** Đổi gì phải hỏi người làm đồ án trước.

**Kết quả (chạy 04/11, xem `reports/dominicks.md`):** 27 ngành, 16.995 mã, 225.883 tuần khuyến mãi ngoài tuần lễ.

| Câu hỏi | Số thật | Giả định trong đồ án | Theo luật |
|---|---|---|---|
| Hệ số deal, trung vị | ×1,63 | ×1,47 | Không lệch |
| Hệ số deal, p90 | ×5,71 | ×3,00 | Luật không xét đuôi, nhưng **đuôi của mô phỏng quá mỏng**: từ ×5 là 11,9% so với 1,4% |
| Đo trên 2/3 đầu, kiểm trên 1/3 sau | phủ 44,3 / 70,8 / 87,0% (mục tiêu 50 / 75 / 90) | Trên mô phỏng đạt: 47,5 / 76,2 / 92,0% | **Không đạt** (lệch 5,7 điểm ở mức 50%); 4/27 ngành đạt khi đo riêng |
| Nhà sản xuất tài trợ | 43,4% (theo ngành 8,7–70,6%) | 70% | **Giả định lệch** |
| Biên lãi gộp theo mã, tuần thường | trung vị 30,4% (p10 18,1%, p90 42,7%) | 10–23% | Không có ngưỡng; mô phỏng thấp hơn |
| Biên lãi gộp, tuần khuyến mãi | 14,5% (tuần thường 26,0%) | Không mô hình hóa | |
| Độ co giãn theo giá | 3,00 | **Không có**: đổi mức giảm không đổi nhu cầu | Thiếu sót của phần livestream |
| Tuần ngay sau khuyến mãi | trung vị ×1,01 | Từng nói có "mua trước rồi giảm" | **Không rõ hiện tượng** ở mức toàn chuỗi |

**Điều rút ra:**
- **Phép đo của đồ án yếu hơn trên số thật.** Phép kiểm trên mô phỏng đạt vì cùng một quy luật sinh ra cả hai giai đoạn; trên số thật, nhu cầu giai đoạn sau cao hơn, chỉ 4/27 ngành giữ được. Hệ số deal phải đo lại định kỳ, không thể đo một lần rồi dùng mãi.
- **Newsvendor vẫn bền:** dùng hệ số thật để chấm, cả 12 trường hợp đều không thua 2 phương án so sánh, kể cả khi Q tính bằng hệ số mô phỏng. Cái giá của việc dùng hệ số mô phỏng khi p = 20%: lãi thấp hơn 1,3 đến 5,9 triệu đ. Khi không có phiên bùng nổ (p = 0), Q theo hệ số mô phỏng lại lãi cao hơn ở 2 trong 3 trường hợp, vì Q theo hệ số thật cộng thêm giả định bùng nổ thì trữ dư. Trữ theo trung bình tệ hơn nhiều với đuôi dày thật: lỗ tới 594 triệu đ khi hàng thừa phải xả.
- **Lãi phụ thuộc mức tài trợ nhiều nhất** (mục 8 của báo cáo, thêm sau khi thấy kết quả, không thuộc luật). Giảm 15%: tài trợ 70% lãi 52,1 triệu đ, 109/118 mã có lãi; tài trợ 43,4% lãi 20,9, còn 73/118 mã. Giảm 30%, tài trợ 43,4%: chỉ 3/118 mã có lãi. Tổ hợp này dùng tài trợ thật với biên lãi mô phỏng thấp hơn thật và phí sàn 8% nên là kịch bản bi quan.
- **Đính chính báo cáo livestream:** bảng theo mức giảm trong `reports/tru_hang_live.md` giữ nguyên nhu cầu nên làm lãi tụt mạnh khi giảm sâu (65,1 / 52,1 / 25,0 triệu đ). Tính cả co giãn thì phẳng hơn nhiều (54,9 / 52,1 / 44,8). Độ co giãn 3,00 chỉ là tương quan, vì khuyến mãi siêu thị đi kèm trưng bày, tờ rơi.

**Giới hạn:** siêu thị Mỹ 1990, không phải Việt Nam và không phải livestream; số theo tuần được dùng cho phiên 1 ngày; giá vốn là giá bình quân tồn kho nên mức tài trợ chỉ là ước lượng; bùng nổ vẫn là giả định. **Chưa đổi gì trong giả định mặc định, mô phỏng, dashboard:** các việc này chờ người làm đồ án quyết định.

### 10.10. Trữ hàng livestream, bản sau đối chiếu với Dominick's (luật ghi ngày 04/11, TRƯỚC khi chạy)

Người làm đồ án đồng ý sửa theo số thật. **Luật này viết sau khi đã thấy kết quả mục 10.8 và 10.9, nên không phải kiểm định ghi trước hoàn toàn.** Kết quả cũ của 10.8 giữ nguyên, `reports/tru_hang_live.md` không chạy lại.

**Thay đổi so với 10.8:**
- **Hệ số deal lấy theo đúng dải giảm giá:** 5–10%, 10–20%, 20–30%, 30–50%, 50–90%, từ số thật Dominick's. Trung vị lần lượt ×1,34, ×1,78, ×2,41, ×4,44, ×14,03. Lý do: mẫu gộp lẫn tuần giảm 50–90% vào mọi phiên, nhân thêm độ co giãn thì tính trùng. Mức giảm dưới 5% dùng dải thấp nhất vì không có dải riêng cho "không giảm".
- **Nhãn hàng tài trợ mặc định 45%,** làm tròn từ 43,4% đo được; vẫn đổi được trên màn hình.
- **Nếu chọn nguồn hệ số của hệ thống (mô phỏng):** số bán nhân thêm `((1 − giảm) / (1 − 15%))^(−3,00)`. Nguồn này không có dải theo mức giảm nên cần độ co giãn; nguồn thật thì không nhân thêm.
- **Giữ nguyên, chưa sửa:** biên lãi của 121 mã (10–23%, thấp hơn số thật), xác suất và hệ số bùng nổ, phí sàn, tỉ lệ hủy, chi phí hàng thừa, quy tắc bổ sung lần 2. Việc hiệu chuẩn biên lãi trong dữ liệu mô phỏng là quyết định riêng.

**Kiểm tra trên số thật, không dò tham số:**
1. **Phép đo theo dải có giữ được cho thời kỳ sau không:** đo trên 2/3 đầu từng ngành, kiểm trên 1/3 sau, từng dải. **Đạt** nếu lệch không quá 5 điểm phần trăm ở cả 3 mức 50%, 75%, 90%. Báo cả so với cách gộp ở 10.9 (không đạt) để biết chia dải có giúp không. Thêm kiểm tra theo ngành và dải (đủ 30 tuần mỗi phần).
2. **Newsvendor:** với mức giảm 10%, 15%, 30%, tài trợ 45%, 3 cách xử lý hàng thừa, p = 20% và p = 0: Q tính trên 2/3 đầu của đúng dải, chấm trên 1/3 sau. **Bền** nếu lãi không thấp hơn 2 phương án so sánh ở mọi trường hợp; thua ở đâu báo đúng ở đó.
3. **Giá trị theo dõi theo giờ** với giả định mới, hàng về sau 6 giờ, cùng quy tắc lần 2, mức giảm 15%. Mã có lãi sau phụ phí ≤ 0 thì không bổ sung, nên giá trị có thể gần 0.
4. **So lãi trước và sau đối chiếu** ở mặc định, kèm số mã còn lãi. Báo rõ khi lãi giảm.

**Không sửa thêm để số đẹp hơn:** kết quả thế nào báo thế ấy. Giới hạn của 10.9 vẫn áp dụng: siêu thị Mỹ 1989–1997, số theo tuần dùng cho phiên 1 ngày, bùng nổ vẫn là giả định.

**Kết quả (chạy 04/11, xem `reports/tru_hang_live_sau_doi_chieu.md`):**
- **Chia theo dải giúp phép đo tốt hơn nhưng chưa đủ.** Gộp mọi mức giảm thì không đạt; theo dải thì đạt 3/5 dải (5–10%, 10–20%, 30–50%), không đạt ở 20–30% và 50–90%. Đo riêng từng ngành vẫn yếu: nhiều nhất 8/27 ngành đạt. Hệ số vẫn phải đo lại định kỳ, và nên đo theo ngành khi có đủ số liệu.
- **Newsvendor bền ở cả 18 trường hợp.** Riêng giảm 30% với tài trợ 45% thì lãi xấp xỉ 0 (chỉ 6/118 mã còn lãi, newsvendor gần như không trữ), trong khi 2 phương án so sánh lỗ 43 đến 2.373 triệu đ. Tức là newsvendor bền ở đây vì nó từ chối trữ, không phải vì phiên đó đáng làm.
- **Lãi mặc định giảm rõ khi dùng số thật** (giảm 15%, toàn kho): về kho thường 52,1 còn 31,0 triệu đ; trả nhà cung cấp 29,7 còn 18,3; phải xả 15,1 còn 12,7; số mã còn lãi 109 còn 74 trên 118. Phần lớn do tài trợ 45% thay vì 70%. Biên lãi mô phỏng thấp hơn số thật nên các số này thiên về bi quan.
- **Giá trị theo dõi theo giờ nhỏ:** +0,5 / +1,5 / +0,6 triệu đ toàn kho (hàng về sau 6 giờ). Kết luận "chỉ đáng làm khi hàng thừa tốn kém" ở 10.8 **không còn rõ**: lãi sau phụ phí còn quá mỏng nên giá trị nhỏ ở cả 3 trường hợp. Đây là mức chi tối đa, chưa trừ chi phí cài đặt.

**Trên dashboard:** tài trợ mặc định 45%; thêm ô chọn nguồn hệ số (số thật theo dải giảm giá, hoặc dữ liệu của hệ thống kèm độ co giãn). `reports/dominicks_he_so_deal.json` là tệp nhỏ dashboard đọc, không cần 13 GB gốc. **Điểm cần biết khi trình bày:** dải đổi đột ngột ở các mốc (giảm 25% dùng trung vị ×2,41, giảm 30% dùng ×4,44), nên kết quả nhảy bậc khi kéo qua mốc.

### 10.11. Hạn sử dụng và sức chứa kho (luật ghi ngày 04/11, TRƯỚC khi chạy)

`src/rang_buoc_kho.py`, có test, chỉ đọc CSDL, không đổi chính sách chính. Khi tắt hết ràng buộc, bộ mô phỏng này phải **trùng từng mã từng ngày** với chính sách AI + hiệu chỉnh trong CSDL. **Dữ liệu không có hạn sử dụng, thể tích hay diện tích kho**, nên các bảng dưới đây là **giả định** theo loại hàng, không phải số trên bao bì hay số của kho thật; kết quả chỉ cho thấy phương pháp và độ lớn tương đối. Dữ liệu đơn hàng và nhu cầu là mô phỏng.

**Hạn sử dụng:**
- **Mã được xét:** thực phẩm, đồ uống, sữa, gia vị, bánh kẹo, kem và đông lạnh, theo bảng giả định trong mã nguồn (từ 30 ngày với sữa chua đến 3 năm với đồ hộp). Hàng khác và rượu vang không xét.
- **Quy tắc 1/3 (giả định):** kho chỉ được giao hàng trong 1/3 thời hạn kể từ lúc hàng về; quá mốc đó siêu thị không nhận, hàng bị loại. Tồn đầu kỳ coi như đã dùng hết nửa khoảng này. Xuất theo lô về trước (FIFO).
- **Chi phí:** loại 1 đơn vị mất 100% giá vốn; thử thêm 50% (bán xả được một nửa).
- **Phương án thử:** trần lượng đặt theo hạn: mỗi lần không đặt quá `max(MOQ, nhu cầu dự báo mỗi ngày × số ngày được giao)`. Mã MOQ lớn hơn lượng bán được trong thời hạn thì trần không giúp được, báo riêng.
- **Luật chọn, chỉ trên validation2:** dùng trần nếu trên các mã có hạn, tổng chi phí (đặt hàng + lưu kho + lợi nhuận mất + hàng loại) giảm ít nhất 0,5% **và** Fill Rate không giảm quá 0,2 điểm. Test chỉ báo cáo. Thử độ nhạy thời hạn ×0,5 và ×2.

**Sức chứa:**
- **Thể tích từng đơn vị:** giả định theo đơn vị tính và loại hàng. Hai vùng riêng: **kho lạnh** (kem, đông lạnh, sữa chua) và **kho thường**.
- **Sức chứa giả định:** mỗi vùng bằng đỉnh thể tích hàng thực tồn trong dữ liệu trên validation2 (kho vừa đủ cho hoạt động năm trước), thử thêm 90% và 80%, vì không biết kho thật lớn bao nhiêu.
- **Phương án A, thuê kho ngoài:** không đổi quyết định đặt hàng; phần vượt tính 10 đ/lít/ngày (khoảng 300.000 đ/m³/tháng, giả định), thử thêm ×0,5 và ×2.
- **Phương án B, cắt đơn:** trước khi đặt, ước lượng thể tích lúc hàng về = hàng hiện có + đang về − nhu cầu dự báo trong thời gian chờ. Mã ít ngày tồn nhất được đặt trước; không đủ chỗ thì giảm lượng đặt, dưới MOQ thì không đặt. Phần vẫn vượt tính tiền thuê như A.
- **Luật chọn, chỉ trên validation2, từng mức sức chứa:** dùng B nếu tổng chi phí (đặt hàng + lưu kho + lợi nhuận mất + thuê ngoài) thấp hơn A ít nhất 0,5% **và** Fill Rate không giảm quá 0,2 điểm; còn lại dùng A. Test chỉ báo cáo.

**Giới hạn:** hạn sử dụng và sức chứa được xét riêng, chưa gộp; chưa xét cửa nhận hàng, số chuyến xe, xếp chồng và chiều cao kệ. Hàng loại không được bù từ nhà cung cấp. Không tự đưa kết quả vào chính sách chính: đổi gì phải hỏi người làm đồ án trước.

**Kết quả (chạy 04/11, xem `reports/rang_buoc_kho.md`). Các số tiền phụ thuộc nặng vào giả định:**

| | Validation2 | Test |
|---|---:|---:|
| Hàng loại, không trần (triệu đ, 50 mã có hạn) | 6.443,6 | 6.233,3 |
| Hàng loại, có trần | 5.996,6 | 5.950,1 |
| Tổng chi phí 50 mã, không trần | 8.464,0 | 9.601,9 |
| Tổng chi phí 50 mã, có trần | 8.089,5 | 9.312,7 |
| Fill Rate 50 mã, không trần / có trần | 96,52% / 96,70% | 95,08% / 95,17% |
| Đỉnh thể tích kho thường so với mốc 100% (không cắt đơn) | 93% | 134% |
| Số ngày vượt mốc 100% (không cắt đơn) | 0 | 277 |
| Fill Rate toàn kho nếu cắt đơn, mức 100% / 90% / 80% | 96,83 / 96,80 / 96,74% | 92,80 / 76,56 / 75,21% |

**Theo luật:** dùng trần lượng đặt theo hạn (validation2 giảm 4,4% chi phí, Fill Rate không giảm). Ở cả 3 mức sức chứa, **dùng A, thuê ngoài, không cắt đơn**. Test đồng ý với cả hai lựa chọn.

**Điều rút ra:**
- **Hàng loại tập trung ở hàng chỉ bán dịp lễ:** 8 mã có hàng loại; 18 mã chỉ bán dịp lễ chiếm 92,4% giá trị. Hàng bán quanh năm gần như không bị loại, trừ sữa chua. Trần lượng đặt có tác dụng rõ với sữa chua (449,1 còn 86,5 triệu đ) nhưng gần như không giúp hàng dịp lễ, có mã còn tệ hơn (Mứt Tết 1.260,8 thành 1.437,5). **Con số 6,2 tỷ là mức trần bi quan:** coi hàng thừa sau mùa mất trắng, không trả được nhà cung cấp, không xả được; xả được một nửa thì tổng chi phí còn 6.485,3 triệu đ. Mô phỏng cũng không có quy tắc ngừng đặt khi hết mùa, nên có mã bị đặt thêm rồi lại loại.
- **Vấn đề sức chứa gần như chỉ do một mã (chẩn đoán thêm sau khi thấy kết quả).** Chính sách đề xuất đặt 9.670 cây thông Noel trên test trong khi nhu cầu 4.999, hiện trạng nhập 5.075; cuối kỳ dư 5.193 cây. Dự báo khi vào mùa cao hơn thực tế khoảng 50%. Bỏ riêng mã này, đỉnh thể tích từ 134% còn 84%, ngày vượt từ 277 còn 1. Mức ảnh hưởng còn phụ thuộc giả định 120 lít/cây. **Đây là điểm yếu có sẵn trong kết quả chính, không phải do phần sức chứa tạo ra:** số liệu khớp `mo_phong_ngay` trong CSDL.
- **Cắt đơn có thể rất nguy hiểm:** ở test, 62,5% thể tích là hàng vượt nhu cầu thật 60 ngày tới, 99,6% trong đó là nhóm Z. Tồn chết chiếm chỗ nên quy tắc cắt đơn chặn cả hàng bán chạy, Fill Rate tụt còn 76%. Muốn xử lý chỗ chứa phải xả tồn chết, không phải cắt đơn mới.
- **Cả 2 ràng buộc cùng chỉ về một điểm: chính sách cho hàng chỉ bán dịp lễ.** Quy tắc đặt lặp lại đặt quá tay ở mùa cao điểm; đây chính là việc newsvendor mùa vụ nhắm tới. Phép thử đó dùng được nhu cầu đã có trong dữ liệu (dù mô phỏng), không cần giả định phiên live.

**Chưa đổi chính sách chính.** Trần lượng đặt theo hạn và thuê ngoài chỉ là kết quả phân tích, chờ người làm đồ án quyết định.

**Quyết định của người làm đồ án (04/11):** chuỗi có bán online và giao từ chính kho, nhưng chủ yếu là phân phối cho siêu thị; mọi mặt hàng đều bán online được. Khối livestream giữ sẵn để sau dùng, không phải hoạt động chính. Trần lượng đặt theo hạn (mục 10.11) **chưa đưa vào chính sách chính**.

### 10.12. Newsvendor cho hàng chỉ bán dịp lễ (luật ghi ngày 04/11, TRƯỚC khi chạy)

Người làm đồ án yêu cầu làm (04/11), sau khi mục 10.11 chỉ ra hàng dịp lễ gây phần lớn hàng loại và tồn chết. `src/newsvendor_mua_vu.py`, có test, chỉ đọc CSDL. Khác với livestream, phép thử này dùng **nhu cầu đã có trong dữ liệu**, nhưng dữ liệu vẫn là mô phỏng. **Không tự đưa vào chính sách chính.**

**Phạm vi:** các mã "Chỉ dịp ..." (18 mã), mỗi mã gắn với 1 sự kiện trong `lich_su_kien` (Tết, Trung thu, Halloween, Noel). Mùa = cửa sổ của sự kiện trong lịch, biết trước. Hàng khác giữ nguyên quy tắc hiện tại. Nguồn dữ liệu không có nhãn mùa hoặc lịch thì không áp dụng.

**Lượng đặt cho một mùa:** `Q = tổng nhu cầu mùa trước × phân vị Cu/(Cu + Co) của r`, trong đó `r` = tổng mùa này / tổng mùa trước của cùng mã, gộp mọi mã.
- `Cu` = giá bán − giá vốn. `Co`: hàng có hạn theo bảng giả định mục 10.11 thì mất 100% giá vốn; hàng không hạn giữ sang năm, mất giá vốn × tỉ lệ lưu kho × 1 năm.
- **Vì sao không dùng dự báo AI để tính Q:** lúc phải đặt (trước mùa một khoảng lead time) dự báo chỉ nhìn được 28 ngày nên không phủ hết mùa. Dự báo AI vẫn dùng ở phương án bổ sung trong mùa.
- **Không nhìn trước:** trên test, `r` chỉ lấy từ các mùa đã kết thúc trước ngày đặt. Trên validation2 chưa có cặp mùa nào trước đó, nên dùng `r` của các mã khác cùng năm (bỏ chính mã đó); **cách này có nhìn ngang trong cùng năm nên validation2 thuận lợi hơn thực tế**.

**Cách đặt:** ngày đặt = đầu mùa − lead time − 2 × độ lệch lead time (làm tròn lên). Đặt `max(Q − hàng hiện có − hàng đang về, 0)`, tối thiểu MOQ. Từ ngày đặt đến hết mùa tắt quy tắc đặt thường. Ngoài mùa giữ quy tắc thường. Mùa có ngày đặt trước đầu kỳ, hoặc kết thúc sau cuối kỳ, thì giữ quy tắc thường vì không chấm công bằng được.

**Hai phương án:**
1. **Một lần:** chỉ đặt 1 lần cho cả mùa.
2. **Một lần + bổ sung:** thêm quy tắc đặt thường (có dự báo AI) trong mùa, nếu hàng về kịp trước khi hết mùa.

**Chấm trong 2 môi trường:** có hạn sử dụng (lô hàng, quy tắc 1/3, loại mất 100% như 10.11) và không hạn (giống chính sách chính, hàng dư chỉ tốn lưu kho). Môi trường không hạn **thiên vị việc trữ dư** vì hàng dư gần như không mất gì và mô phỏng dừng ở cuối kỳ.

**Luật chọn, chỉ trên validation2, môi trường có hạn:** dùng phương án có tổng chi phí toàn kho thấp nhất, nếu chi phí thấp hơn quy tắc hiện tại ít nhất 0,5%, **và** Fill Rate toàn kho không giảm quá 0,5 điểm **và** không dưới 95%. Ngưỡng 0,5 điểm rộng hơn 0,2 điểm của các mục trước vì newsvendor cố ý đổi mức phục vụ lấy chi phí theo tỉ số Cu/Co; ghi rõ lý do này trước khi chạy. Không phương án nào đạt thì **giữ quy tắc hiện tại**. Test chỉ báo cáo.

**Báo cáo thêm:** môi trường không hạn, kể cả khi bất lợi; Fill Rate riêng hàng dịp lễ; giá trị tồn ngay sau mùa; cây thông Noel; đỉnh thể tích; độ nhạy `Co` khi xả được 50%. Giả định không sửa sau khi xem kết quả.

**Kết quả (chạy 04/11, xem `reports/newsvendor_mua_vu.md`):**

| Toàn kho, chính sách AI + hiệu chỉnh | Quy tắc hiện tại | Newsvendor, một lần (theo luật) | Bỏ mã hạn ngắn (thêm sau khi thấy test) |
|---|---:|---:|---:|
| Validation2, có hạn: chi phí (tr đ) · Fill Rate | 10.270,2 · 96,32% | 9.640,1 · 95,99% | 9.640,1 · 95,99% |
| Test, có hạn: chi phí · Fill Rate | 11.756,9 · 95,85% | **13.441,9 · 93,89%** | 9.668,1 · 95,30% |
| Test, không hạn: chi phí · Fill Rate | 5.778,3 · 95,82% | 5.343,2 · 95,34% | 5.242,1 · 95,33% |
| Test, không hạn: Fill Rate hàng dịp lễ · tồn TB hàng dịp lễ (tr đ) | 94,93% · 6.422,2 | 91,16% · 3.571,7 | 91,04% · 3.417,5 |
| Test, không hạn: đỉnh thể tích kho thường | 134% | 106% | 106% |

**Theo luật:** validation2 chọn "một lần" (chi phí giảm 6,1%, Fill Rate giảm 0,33 điểm). **Test không xác nhận trong môi trường có hạn:** chi phí tăng 14,3%, Fill Rate 93,89%, dưới 95%. Vì vậy **không đưa phương án này vào chính sách chính.** Phương án "bổ sung trong mùa" đặt lại gần như quy tắc cũ (cây thông vẫn 9.670) nên không giải quyết được đặt quá tay.

**Vì sao validation2 không báo trước:** hai mã bánh trung thu chỉ được giao 20 ngày theo giả định, trong khi từ ngày đặt đến hết mùa dài hơn, nên hàng hết hạn giữa mùa và không được đặt lại. Trên test chi phí nhóm Trung thu tăng từ 2.855,5 lên 6.659,6 triệu đ. Validation2 không có mùa Trung thu nào được chấm vì mùa 2025 kết thúc sau cuối kỳ, nên phép chọn **không thấy được** rủi ro này. Đây là điểm yếu của cách chia dữ liệu, không chỉ của phương án.

**Điều rút ra:**
- **Đặt một lần có ích ở các dịp còn lại (chẩn đoán sau khi thấy kết quả):** test, có hạn: Halloween 494,1 còn 155,6 triệu đ, Noel 825,9 còn 391,5, Tết 2.814,1 còn 1.468,5. Đổi lại Fill Rate Noel giảm từ 99,9% xuống 87,0%, Tết từ 99,7% xuống 94,6%; Halloween tăng từ 81,8% lên 94,6%.
- **Đặt quá tay được giải quyết:** cây thông nhập 4.935 so với nhu cầu 4.999, cuối kỳ dư 481 thay vì 5.193. Đỉnh thể tích từ 134% còn 106%.
- **Phương án bỏ mã hạn ngắn trông tốt nhưng chưa được kiểm chứng độc lập:** các mã bị bỏ được nhận ra bằng phép kiểm logic (mùa dài hơn số ngày được giao), không dò theo kết quả, nhưng phương án được **thêm sau khi đã thấy test**, và trên test Fill Rate giảm 0,55 điểm, nhích quá ngưỡng 0,5. Dữ liệu không còn năm nào chưa xem để kiểm lại. **Chỉ trình bày như đề xuất cải tiến**, không như kết quả đã kiểm định.
- Hàng hạn ngắn có mùa dài cần giao nhiều đợt, chưa làm.

**Giới hạn:** mỗi mã chỉ có 1–2 mùa trước để làm gốc; `r` trên validation2 nhìn ngang trong cùng năm; dữ liệu mô phỏng nên mùa này giống mùa trước hơn thực tế (`r` p10–p90 là 0,81–1,20), có thể làm lợi cho cách dựa vào mùa trước; hạn và chi phí hàng dư là giả định. Q dùng lịch sử mùa trước, không dùng dự báo AI, vì dự báo chỉ nhìn được 28 ngày.

## 11. Mô phỏng và bảng trước–sau ✅ (24/10)

**Từ 01/11 (vòng 4):** dự báo `ket_hop_v4` cập nhật mỗi tuần, dự báo mốc TB trượt 28 ngày cũng cập nhật mỗi tuần, quy tắc lượng đặt **lai** (chọn trên validation2, mục 10.4), 12 tháng test, 121 SKU, mức phục vụ 95% (`reports/ton_kho_so_sanh.md`, CSDL `v_so_sanh_chinh_sach`). Chi phí liên quan = chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do thiếu hàng.

| KPI | Hiện trạng ⚠️ | Công thức + dự báo mốc | Công thức + dự báo AI | **AI + hiệu chỉnh lệch** | *v3 (28 ngày, EOQ)* |
|---|---|---|---|---|---|
| Fill Rate | 93,57% | 91,69% | 95,33% | **95,82%** | *95,91%* |
| Số ngày-SKU thiếu hàng | 1.564 | 916 | 793 | **735** | *752* |
| Tồn kho TB (triệu đ) | 11.993,6 | 19.669,7 | **9.208,7** | 11.906,0 | *16.377,3* |
| Số lần nhập hàng | **1.910** | 3.575 | 3.467 | 3.192 | *3.035* |
| Chi phí đặt + lưu (triệu đ) | 2.766,8 | 4.567,0 | **2.427,4** | 2.915,7 | *3.721,7* |
| Lợi nhuận mất (triệu đ) | 3.693,3 | 4.444,0 | **2.902,2** | 2.912,4 | *2.951,0* |
| **Chi phí liên quan (triệu đ)** | 6.460,1 | 9.011,0 | **5.329,6** | 5.828,1 | *6.672,7* |

**So sánh chính (cùng công thức, cùng cập nhật mỗi tuần, chỉ khác dự báo): AI + hiệu chỉnh so với dự báo mốc:** Fill Rate +4,1 điểm (91,69% → 95,82%); ngày-SKU thiếu −20%; tồn kho −39,5%; chi phí đặt + lưu −36%; lợi nhuận mất −35%; **chi phí liên quan −35,3%** (9,01 → 5,83 tỷ đ).

**So với hiện trạng** (đối thủ biết trước nhu cầu kỳ vọng): Fill Rate +2,3 điểm, ngày-SKU thiếu −53%, lợi nhuận mất −21%, **tồn kho −0,7%** (lần đầu không cao hơn hiện trạng), số lần nhập +67%; **chi phí liên quan −9,8%** (6,46 → 5,83 tỷ đ).

**So với v3 (cập nhật 28 ngày):** cùng chính sách AI + hiệu chỉnh, tồn kho −27% (16,38 → 11,91 tỷ), chi phí liên quan −12,7% (6,67 → 5,83 tỷ), Fill Rate gần như giữ (95,91% → 95,82%). Cải thiện đến từ **quy trình** (dùng số liệu mới mỗi tuần) và quy tắc đặt đến mức cho hàng mùa vụ, không từ mô hình phức tạp hơn.

**Ghi nhận trung thực:** trên test, chính sách **AI không hiệu chỉnh lệch** còn rẻ hơn (5,33 tỷ, tồn kho −23% so với hiện trạng) nhưng Fill Rate thấp hơn (95,33%); trên validation2 (tập chọn) AI + hiệu chỉnh rẻ hơn (4,05 so với 4,54 tỷ), nên theo luật vẫn giữ AI + hiệu chỉnh — không đổi lựa chọn vì kết quả test.

*Bảng v3 (28 ngày, EOQ — kết quả trước 01/11, giữ để so sánh):* Hiện trạng 93,57% / 11.993,6 / 6.460,1; dự báo mốc 88,83% / 15.808,5 / 9.307,9; AI 94,29% / 13.982,9 / 6.822,8; AI + hiệu chỉnh 95,91% / 16.377,3 / 6.672,7 (Fill Rate / tồn TB / chi phí liên quan, triệu đ).

**Dự báo chính xác hơn chưa chắc rẻ hơn (v3 so với v2, cùng công thức):** Fill Rate 95,34% → 95,91%, ngày-SKU thiếu 785 → 752, nhưng tồn kho +6,8% và chi phí liên quan +2,0% (6,54 → 6,67 tỷ). Mô hình v3 bớt dự báo thiếu ở nhóm Z (Fill Rate Z 94,4% → 97,1%), nhưng với hàng chỉ bán dịp lễ công thức EOQ đặt quá tay nên tồn nhóm Z tăng thêm ~1 tỷ. Trên validation2, v3 lại cho chi phí thấp hơn (5,52 so với 5,55 tỷ). Không quay lại v2 dựa trên kết quả test (sẽ là chọn theo đề thi). Kết luận: nút thắt đã chuyển từ **dự báo** sang **quy tắc đặt hàng cho hàng thời vụ** (mục 10.3, hướng phát triển newsvendor).

**Theo nhóm (95%, vòng 4):**
| Nhóm | Chính sách | Fill Rate | Tồn TB (triệu đ) | Lợi nhuận mất (triệu đ) |
|---|---|---|---|---|
| X (ổn định) | AI + hiệu chỉnh | **95,6%** | 3.663,3 | 2.381,8 |
| X | Hiện trạng | 93,8% | 5.180,2 | 2.749,6 |
| X | Dự báo mốc | 95,6% | 4.151,9 | 2.509,9 |
| Y | AI + hiệu chỉnh | 97,6% | 512,4 | 140,4 |
| Y | Hiện trạng | 97,9% | 473,0 | 138,6 |
| Z (mùa vụ) | AI + hiệu chỉnh | **96,1%** | 7.730,3 | **390,3** |
| Z | Hiện trạng | 91,9% | **6.340,5** | 805,0 |
| Z | Dự báo mốc | 79,8% | 14.838,2 | 1.801,4 |

- **Hàng ổn định (X):** chính sách AI thắng **cả hiện trạng** dù hiện trạng biết trước nhu cầu: đáp ứng cao hơn (95,6% so với 93,8%) mà tồn kho **thấp hơn 29%**.
- **Hàng mùa vụ (Z):** AI đáp ứng 96,1% (hiện trạng 91,9%) với tồn 7,7 tỷ so với 6,3 tỷ (+22%); bản v3 (EOQ) tồn tới 12,1 tỷ. Quy tắc đặt đến mức cho nhóm Z đã giải phần lớn vấn đề hàng chỉ bán dịp lễ (mục 10.1).
- **Độ nhạy mức phục vụ:** chi phí liên quan của AI + hiệu chỉnh: 90% → 5,99 tỷ; 95% → 5,83; 99% → 5,38. Chi phí thiếu hàng (lợi nhuận mất) lớn so với chi phí lưu kho nên mức phục vụ cao hơn có lợi hơn. Chưa đổi mức chính (95% đã chốt trước); nếu muốn đổi phải chọn lại trên validation.

**Đối chiếu tiêu chí thành công (mục 1c `docs/09`, vòng 4):** Fill Rate ≥ 95% ✅ (95,82%); "tồn kho không cao hơn hiện trạng" ✅ (−0,7%; nhóm X −29%); giảm thiếu hàng ✅ (−53%); tổng chi phí liên quan thấp hơn hiện trạng ✅ (−9,8%, dù hiện trạng biết trước nhu cầu) và thấp hơn dự báo mốc −35% ✅.

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
| Gốc | 95,82% | | 5.828,1 tr đ | |
| Tắc cảng +3 ngày (TB 13 đợt) | 95,33% | −0,49 điểm | 6.168,8 | +5,8% |
| Tắc cảng +5 ngày | 94,84% | −0,98 | 6.510,2 | +11,7% |
| Tắc cảng +7 ngày | 94,30% | −1,52 | 6.859,2 | +17,7% |
| Tắc cảng +7 ngày, đợt xấu nhất (hàng dự kiến về từ 21/01/2026, trước Tết) | 93,32% | −2,50 | 7.184,4 | +23,3% |
| Lead time +2 ngày, **không** cập nhật công thức | 90,76% | **−5,06** | 9.250,4 | **+58,7%** |
| Lead time +2 ngày, **có** cập nhật | 95,39% | −0,43 | 6.044,2 | +3,7% |
| Chi phí đặt hàng +20% | 95,92% | +0,10 | 5.821,2 | −0,1% |
| Chi phí lưu kho +15% | 95,91% | +0,09 | 6.076,2 | +4,3% |

(Vòng 4: dự báo cập nhật mỗi tuần, quy tắc lai. Bảng v3 (28 ngày, EOQ) trước 01/11: gốc 95,91% / 6.672,7; tắc cảng +7 ngày 94,37% / 7.694,3; lead time +2 không cập nhật 90,80% / 10.117,4.)

**Nhận xét:**
- **Tắc cảng tạm thời:** Fill Rate chỉ giảm 0,5–1,5 điểm (trung bình). **Chính sách dùng dự báo AI luôn có chi phí liên quan thấp nhất ở cả 39 lần thử (13 đợt × 3 mức trễ)**: 38 lần là AI không hiệu chỉnh, 1 lần AI + hiệu chỉnh (đúng như bảng gốc, AI không hiệu chỉnh rẻ hơn trên test). Chi phí của AI + hiệu chỉnh tăng nhiều hơn về % (+17,7% so với +9,6% của dự báo mốc khi trễ 7 ngày) vì gốc thấp hơn và tồn sát hơn; tính bằng tiền, AI tăng 1.031 tr đ, dự báo mốc tăng 869 tr đ, AI vẫn rẻ hơn mốc khoảng 3,0 tỷ đ.
- **Đợt nguy hiểm nhất là trước Tết** (hàng dự kiến về 21/01–10/02/2026): đúng lúc tồn kho đang được đẩy lên cho cao điểm. Nếu ngoài đời cuối năm cũng là mùa cảng đông (giả định, cần kiểm chứng với đơn vị thực tập) thì nên đặt sớm hơn hoặc tăng tồn an toàn trước Tết.
- **Lead time dài ra lâu dài nguy hiểm hơn tắc cảng tạm thời** nếu không ai cập nhật tham số: Fill Rate −5,1 điểm, chi phí +59%. Cập nhật lead time vào công thức thì gần như hồi phục (−0,4 điểm). Bài học: **công thức chỉ tốt khi tham số được cập nhật**; cần theo dõi lead time thực tế từng nhà cung cấp hằng tháng.
- **Chi phí tăng:** Fill Rate gần như không đổi. AI + hiệu chỉnh vẫn rẻ hơn hiện trạng ở mọi kịch bản chi phí: gốc −9,8%; S +20% → −10,8%; H +15% → −11,0%. (Bản v3 giữ tồn nhiều hơn hiện trạng 37% nên khi H +15% chênh lệch xấu đi thành +6,7%; vòng 4 tồn ngang hiện trạng nên không còn điểm yếu này.)

## 12. Dashboard ✅ (xong 23/10, kế hoạch 23–26/11)

**Chạy:** `streamlit run app/dashboard.py` tại thư mục gốc dự án (cần chạy trước `python src/nap_database.py` và `python src/ton_kho.py`). Trình duyệt tự mở `http://localhost:8501`, không cần mạng.

**Nguyên tắc:** dashboard **chỉ đọc** CSDL `data/kho_hang.db` (mở SQLite ở chế độ read-only), không tính lại mô hình hay tồn kho; mọi số lấy từ bảng/khung nhìn do các bước trước ghi, nên luôn khớp với báo cáo. Màu giống hình `reports/ket_qua/` (thực tế đen, AI xanh dương, dự báo mốc cam, hiện trạng xám). Mọi trang ghi "dữ liệu mô phỏng".

**Bản 31/10 (giao diện mới, 4 màn, cơ chế kiểu Power BI; người dùng chọn hướng "phiếu vận đơn"):** người dùng chính là người lập kế hoạch kho, hệ thống chỉ ra kết quả khi người dùng thao tác. Giao diện dựng như **bộ phiếu kế hoạch đặt hàng nhiều liên**: khung và nhãn in một màu mực xanh, số liệu mực đen, trạng thái là con dấu (luôn có chữ + biểu tượng), việc cần làm tô dạ quang vàng, mỗi màn một màu liên giấy. Font Be Vietnam Pro lưu sẵn trong `app/static/fonts` (chạy không cần mạng). Hệ thiết kế ghi ở `DESIGN.md`.

**Cơ chế kiểu Power BI:** (1) **bộ lọc chung** ở đầu phiếu (ngày lập phiếu, chính sách, nhóm ABC, nhóm XYZ) áp cho mọi màn; (2) **lọc chéo**: bấm 1 ô trạng thái → lọc lịch cả năm và danh sách theo dõi; bấm 1 ngày trên lịch 12 tháng (màn Hôm nay) hoặc dải trạng thái từng ngày của mã (màn Mặt hàng) → đổi ngày lập phiếu; bấm 1 chính sách trên biểu đồ → tô đậm ở mọi biểu đồ và chọn làm chính sách chung; (3) **đi sâu**: bấm 1 dòng / "Xem mặt hàng" → mở màn Mặt hàng của mã đó. Số ở màn Kịch bản & kết quả **cộng lại theo bộ lọc nhóm** (không phải số toàn kho cố định).

| Màn | Nội dung | Đọc từ |
|---|---|---|
| Hôm nay | 4 ô trạng thái cuối ngày (bấm để lọc); **đơn cần duyệt**: mỗi dòng ghi lý do bằng số (trong kho + đang về ≤ ROP), chọn Duyệt / Sửa (đổi số lượng) / Bỏ qua → con dấu; "Duyệt các dòng còn lại"; **tải phiếu đặt hàng** CSV xếp theo nhà cung cấp, có ngày về dự kiến theo lead time TB; **so với bình thường** (ngày đang xem và trung bình năm, nút tới ngày nhiều việc nhất / nhiều hết hàng nhất); **lịch 12 tháng** (mỗi ô 1 ngày, bấm để đổi ngày, rê chuột xem số) kèm số mã hết hàng / phải đặt trung bình theo tháng; danh sách theo dõi | `mo_phong_ngay`, `du_bao`, `tham_so_ton_kho`, `giao_dich_sach`, `dm_sku` |
| Mặt hàng | Nhãn mã hàng (nhóm, ABC · XYZ, nhà cung cấp, lead time, trong kho, đang về); tồn kho 12 tháng + ROP + ngày đặt hàng, dải trạng thái từng ngày của mã (bấm để đổi ngày); dự báo so với thực tế (tuần / ngày, WMAPE, Bias); **"Thử nếu…"**: kéo mức phục vụ 90–99,5% và "hàng về chậm thêm" 0–7 ngày → SS, ROP, EOQ, lượng đặt hôm nay tính lại ngay; kết quả cả năm của mã theo 4 chính sách | như trên + `ket_qua_ton_kho` |
| Kịch bản & kết quả | Mức phục vụ 90/95/99%; bảng trước – sau; 4 chỉ số chính (bấm để chọn chính sách); theo nhóm XYZ: tồn kho đổi lấy mức đáp ứng; thử độ nhạy 7 kịch bản | `ket_qua_ton_kho`, `ket_qua_do_nhay`, `kich_ban_do_nhay` |
| Dữ liệu & phương pháp | Dữ liệu là gì, cái gì thật / giả định; hệ thống chạy thế nào (5 bước); 6 biểu đồ phân tích (như khu ① cũ); xếp hạng mô hình; công thức SS / ROP / EOQ | như khu ① cũ |

**"Thử nếu…" dùng đúng công thức mô phỏng:** hàm `csdl.de_xuat_ngay` (SS, ROP, EOQ, lượng đặt của 1 mã tại 1 ngày, cùng công thức `ton_kho.simulate`). Kiểm tra: ở 95% và không chậm, tái lập đúng **127.776 / 127.776** dòng (ROP và lượng đặt của 3 chính sách × 121 mã × 352 ngày mở cửa). Khi hàng về chậm k ngày: lead time L + k, sai số dự báo trong thời gian chờ giả định tăng theo √((L + k) / L) (giả định, không đo lại trên validation). "Thử nếu" chỉ tính lại cho ngày đang xem, không chạy lại mô phỏng cả năm.

**Bản 24/10 (5 khu, đã thay bằng bản 31/10):** người dùng duyệt tăng từ 4 lên 5. bản đầu chỉ có 1 biểu đồ mỗi khu, còn lại là bảng số và mã kỹ thuật, nên người xem không thấy "dữ liệu nói gì" và thấy số liệu "không thực". Đã thêm khu ① Tổng quan, mỗi biểu đồ kèm **Cách đọc** và **Phát hiện** (phát hiện tính trực tiếp từ dữ liệu, không ghi tay số); thêm ví dụ bằng lời cho bảng cảnh báo và bảng tham số; cột kỹ thuật giấu sau nút "Hiện thêm cột kỹ thuật"; đổi tên cột sang lời dễ hiểu.

| Khu | Nội dung | Đọc từ |
|---|---|---|
| ① Tổng quan dữ liệu | Dữ liệu là gì (121 SKU, 1.096 ngày, 132.616 dòng, 687 dòng lỗi đã sửa); **cái gì thật, cái gì giả định, vì sao vẫn dùng được**; 6 biểu đồ: giá trị xuất kho theo tuần 3 năm kèm Tết / Trung thu / bão Yagi / 11.11; bản đồ mùa vụ nhóm hàng × tháng; thứ trong tuần; khuyến mãi làm bán tăng bao nhiêu (1.332 đợt); ma trận ABC × XYZ; xếp hạng mô hình dự báo | `giao_dich_sach`, `giao_dich_tho`, `nhat_ky_sua_loi`, `lich_su_kien`, `lich_khuyen_mai`, `phan_loai_sku`, `v_xep_hang_mo_hinh` |
| ② Dự báo theo SKU | Chọn SKU (lọc theo nhóm XYZ) → đường thực tế, dự báo AI, dự báo mốc trong 12 tháng test, xem theo ngày hoặc tuần; WMAPE, Bias, số ngày được chấm của riêng SKU đó | `du_bao`, `mo_hinh`, `dm_sku`, `phan_loai_sku` |
| ③ Cảnh báo tồn kho | Chọn một ngày trong năm test làm "hôm nay" → số SKU hết hàng / cần đặt hôm nay / tồn dưới ROP nhưng hàng đang về / đủ hàng; biểu đồ số mặt hàng cần chú ý mỗi ngày cả năm; ví dụ bằng lời cho từng loại cảnh báo; bảng chi tiết (tồn, ROP, hàng đang về, lượng đặt, đủ bán bao nhiêu ngày); biểu đồ "răng cưa" tồn kho và ROP của 1 SKU, so với hiện trạng | `mo_phong_ngay`, `v_du_bao_chon`, `tham_so_ton_kho`, `giao_dich_sach` |
| ④ Trước – sau | Chọn mức phục vụ 90/95/99% → 4 chỉ số chính của chính sách đề xuất so với dự báo mốc và hiện trạng; 4 biểu đồ cột nhỏ (mỗi chỉ số một trục); bảng trước – sau toàn kho và theo nhóm XYZ; thử độ nhạy (mục 11.1) | `v_so_sanh_chinh_sach`, `ket_qua_ton_kho` |
| ⑤ Tham số SS / ROP / EOQ | Chọn chính sách, mức phục vụ, lọc ABC/XYZ, tìm theo tên → giải thích bằng lời cho 1 mặt hàng; biểu đồ tiền nằm trong hàng dự phòng theo nhóm và Fill Rate từng mặt hàng; bảng SS, ROP, EOQ bình quân, SS đủ bán bao nhiêu ngày, MOQ, lead time, σ sai số, hệ số hiệu chỉnh và kết quả mô phỏng từng SKU; tải CSV; công thức | `tham_so_ton_kho`, `ket_qua_ton_kho`, `dm_sku` |

**Hàng đang về** (khu ③) không lưu trong CSDL nên tính theo bảo toàn: hàng đang về đầu kỳ + tổng đã đặt − tổng đã nhận. Đã kiểm tra trên cả 3 chính sách theo công thức: không ngày nào âm; mọi SKU "tồn dưới ROP mà không đặt" đều có tồn + hàng đang về > ROP, đúng quy tắc đặt hàng của `ton_kho.py`.

**Sửa 02/11 (góp ý người dùng: cột xếp chồng 352 ngày khó đọc, người mới không biết nhìn vào đâu):** thay dải cả năm ở màn Hôm nay bằng bảng so với bình thường + lịch 12 tháng + 2 biểu đồ cột theo tháng có ghi số. Chỉ đổi cách hiển thị, không đổi số liệu; kiểm tra lại bằng chuột thật và 32 thao tác `streamlit.testing`. **Kiểm tra (bản 31/10):** bấm chuột thật trong Edge (13 bước: lọc trạng thái, duyệt, bấm dải cả năm, chuyển thẻ giữ ngày + bộ lọc, đi sâu, bấm dải trạng thái của mã, bấm chính sách, đổi mức phục vụ + kịch bản; chạy 3 lần liên tiếp, không lỗi JavaScript); `streamlit.testing` 32 thao tác trên 4 màn (lọc trạng thái, duyệt / sửa / bỏ qua / hoàn tác, ngày kho nghỉ, đổi chính sách, lọc nhóm, đi sâu sang Mặt hàng, "Thử nếu", mức phục vụ, 3 kịch bản, lọc nhóm ở Kết quả): không lỗi; chụp Edge 4 màn ở 1440 px và 390 px: không lỗi, font nạp đúng, không tràn ngang. **Kiểm tra (bản 24/10):** số ở khu ④ khớp `reports/ton_kho_so_sanh.md` (mô hình v3: Fill Rate 95,91%, 752 ngày-SKU thiếu, chi phí liên quan 6,67 tỷ đ, −28,3% so với dự báo mốc); chụp màn hình cả 5 khu trên Edge.

**Ví dụ để demo:** ngày 09/02/2026 (8 ngày trước Tết), chính sách đề xuất: 0 SKU hết hàng, 8 SKU cần đặt hôm nay, 44 SKU tồn dưới ROP nhưng hàng đang về, 69 SKU đủ hàng (mô hình v4 cập nhật mỗi tuần, 01/11; trước đó 0 / 6 / 38 / 77 với v3, 0 / 11 / 43 / 67 với v2, 1 / 5 / 44 / 71 với giá mô phỏng cũ).

**Giới hạn:** màn Hôm nay là **phát lại** kết quả mô phỏng, không phải hệ thống chạy hằng ngày; quyết định duyệt đơn chỉ giữ trong phiên (không ghi CSDL, đúng lựa chọn (a) của người dùng); chưa ước tính số chuyến xe vì dữ liệu chưa có thể tích / trọng lượng từng mã; dữ liệu theo ngày chỉ lưu cho mức phục vụ 95%.

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
- **Giới hạn sức chứa:** diện tích kho, kho lạnh, số chuyến xe nhận hàng mỗi ngày (cửa nhận hàng), ngân sách mua hàng. Chính sách AI (vòng 4) tồn ngang hiện trạng, nhưng nhóm Z vẫn cao hơn 22% trước mùa cao điểm, có thể vượt sức chứa kho lạnh dịp Tết.
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
| 31/10 | Nâng cấp dự báo vòng 3 + đưa vào tồn kho | `src/nang_cap_du_bao.py`, `reports/nang_cap_du_bao.md` | Luật ghi trước; A (theo tầm) và B (lịch sự kiện, âm lịch) giữ, F (tham số) bỏ; test WMAPE 0,368, Bias +3,9% (đạt ±5%), Z 0,496. Tồn kho: Fill Rate 95,91%, ngày thiếu 752, nhưng tồn +6,8% và chi phí liên quan +2,0% so với v2 (6,67 tỷ, −28,3% so với dự báo mốc) | Chọn theo validation2, không quay lại v2 vì kết quả test; nút thắt chuyển sang quy tắc đặt hàng cho hàng thời vụ; `ton_kho.py` đọc mô hình chọn từ CSDL |
| 31/10 | Làm lại giao diện: 4 màn, cơ chế kiểu Power BI | `app/dashboard.py`, `app/chung.py`, `app/trang/*.py`, `.streamlit/config.toml`, `DESIGN.md`, `csdl.de_xuat_ngay` | Bộ lọc chung, lọc chéo, đi sâu; duyệt / sửa / bỏ qua đơn + tải phiếu đặt hàng; "Thử nếu…" tái lập đúng 127.776/127.776 dòng mô phỏng ở 95%; 30 thao tác AppTest không lỗi | Người dùng chính là người lập kế hoạch (phải thao tác mới ra kết quả); giao diện "phiếu vận đơn" do người dùng chọn; duyệt đơn chỉ giữ trong phiên; không ước tính số xe khi chưa có dữ liệu thể tích |
| 31/10 | Vòng 4 dự báo: rủi ro, cập nhật hằng tuần, khoảng dự báo | `src/nang_cap_du_bao_v4.py`, `reports/nang_cap_du_bao_v4.md`, `reports/rui_ro_du_bao.md` | Sàn sai số ≈ 0,286; B1, B2 bỏ; cập nhật mỗi tuần WMAPE 0,379 → 0,358, tồn kho validation2 −27%, chi phí liên quan −22%, Fill Rate 96,4%; khoảng 80 / 95% phủ 79,7 / 95,7% (lead time 77,4 / 93,5%) | Test giữ kín theo người dùng; luật bổ sung trước B2 (bỏ ngày trùng sự kiện lớn khi ước lượng tác động bão); `danh_gia.folds` và `ton_kho.simulate` thêm tham số khoảng cách mốc, mặc định không đổi kết quả |
| 01/11 | Mở test + đưa cập nhật mỗi tuần vào hệ thống | `src/nang_cap_du_bao_v4.py --buoc test`, `ton_kho.py`, `nap_database.py`, `csdl.de_xuat_ngay`, dashboard, biểu đồ, Power BI | Test (một lần): WMAPE 0,356 (v3 0,368), Bias +3,0%, khoảng 80 / 95% phủ 80,9 / 96,0%. Quy tắc lai được chọn trên validation2; tồn kho test AI + hiệu chỉnh: Fill Rate 95,82%, tồn 11,91 tỷ (−0,7% so với hiện trạng), chi phí liên quan 5,83 tỷ (−9,8% so với hiện trạng, −35,3% so với dự báo mốc cập nhật tuần) | Người dùng mở test 31/10; dự báo mốc cũng cập nhật mỗi tuần cho công bằng; mọi nơi hiển thị lấy bản mới nhất mỗi ngày; AI không hiệu chỉnh rẻ hơn trên test nhưng giữ lựa chọn theo validation2 |
| 02/11 | Màn Hôm nay: thay dải cả năm bằng bảng so với bình thường + lịch 12 tháng + cột theo tháng (góp ý người dùng) | `app/trang/hom_nay.py`, `app/chung.py`, `csdl.chia_lop_mau` | Chỉ đổi hiển thị; chuột thật + 32 thao tác đạt; lỗi Vega ở màn Mặt hàng vẫn còn |  |
| 02/11 | Vòng 5: LSTM, RNN theo luật mục 9.7; giữ `ket_hop_v4` | `src/mo_hinh_dl.py`, `reports/mo_hinh_dl.md` | Nạp lại CSDL: bảng tồn kho, dự báo v4 trùng khớp từng dòng; đối chiếu số liệu khớp |  |
| 02/11 | Chỉ số kho (mục 10.5); sơ đồ luồng báo cáo | `src/chi_so_kho.py`, `src/tao_so_do_bao_cao.py` | 39 test pytest, 32 thao tác giao diện đạt |  |
| 02/11 | Sửa lỗi Vega "Unrecognized data set": nhúng dữ liệu vào đặc tả (`C.ve_bd`) | `app/chung.py`, `app/trang/*` | Bấm chuột thật 8 lần: 7 lần không lỗi JS, 1 lần trình duyệt không khởi động |  |
| 03/11 | Gom đơn theo nhà cung cấp (mục 10.6); gỡ ghi cứng theo dữ liệu; bộ chuyển đổi M5 | `src/gom_don.py`, `src/kiem_tra_du_lieu.py`, `src/nguon/m5.py` | k = 0 trùng từng dòng với `mo_phong_ngay`; đặc trưng, CSDL trùng khớp sau khi gỡ ghi cứng |  |
| 03/11 | Chấm điểm nhà cung cấp, cảnh báo giao chậm (mục 10.7); sổ số liệu đồ án | `src/cham_diem_ncc.py`, `src/so_lieu_do_an.py`, `reports/so_lieu_do_an.md` | Có test; cảnh báo phát hiện đúng nhưng chậm |  |
| 03/11 | Trữ hàng cho phiên livestream, newsvendor hai bước (mục 10.8); khối trên màn Mặt hàng | `src/tru_hang_live.py`, `reports/tru_hang_live.md`, `app/trang/mat_hang.py` | Có test; quy tắc bổ sung lần 1 thua cả không làm gì, phải sửa, báo cả 2 lần |  |
| 04/11 | Đối chiếu giả định với số bán thật Dominick's (mục 10.9) | `src/phan_tich_dominicks.py`, `reports/dominicks.md` | Có test; đuôi deal, mức tài trợ lệch, phép đo không đạt trên số thật; newsvendor vẫn bền; chưa đổi giả định |  |
| 04/11 | Khối livestream bản sau đối chiếu: hệ số theo dải giảm giá, tài trợ 45%, độ co giãn (mục 10.10) | `src/tru_hang_live.py`, `src/phan_tich_dominicks.py`, `app/trang/mat_hang.py`, `reports/tru_hang_live_sau_doi_chieu.md` | Có test; newsvendor bền 18/18; lãi mặc định giảm khoảng 40%; giá trị theo dõi nhỏ |  |
| 04/11 | Hạn sử dụng và sức chứa kho (mục 10.11) | `src/rang_buoc_kho.py`, `reports/rang_buoc_kho.md`, `app/trang/ket_qua.py` | Có test, khớp CSDL khi tắt ràng buộc; hàng dịp lễ chiếm 92% hàng loại; sức chứa vượt do 1 mã đặt quá tay |  |
| 04/11 | Newsvendor cho hàng chỉ bán dịp lễ (mục 10.12); khối livestream dùng được cho mọi mã | `src/newsvendor_mua_vu.py`, `reports/newsvendor_mua_vu.md`, `app/trang/ket_qua.py`, `app/trang/mat_hang.py` | Có test; validation2 chọn đặt một lần, test có hạn không xác nhận do hàng hạn ngắn; không đưa vào chính sách chính |  |

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
| `app/dashboard.py`, `app/chung.py`, `app/trang/` | Công cụ kế hoạch đặt hàng Streamlit 4 màn (Hôm nay, Mặt hàng, Kịch bản & kết quả, Dữ liệu & phương pháp), chỉ đọc CSDL (`streamlit run app/dashboard.py`); hệ thiết kế `DESIGN.md`; font `app/static/fonts/` |
| `src/nang_cap_du_bao_v4.py`, `reports/nang_cap_du_bao_v4.md`, `reports/rui_ro_du_bao.md` (+ `.csv`), `reports/du_bao/ket_hop_v4_*.csv`, `reports/du_bao/tb_truot_28_tuan_*.csv` (mọi mốc tuần, có cột khoảng; file trung gian ở `reports/du_bao/v4/`) | Vòng 4 (mục 9.5): bảng rủi ro định lượng, tự hiệu chỉnh, cảnh báo bão, cập nhật dự báo mỗi tuần, khoảng dự báo 80 / 95%; trạng thái `reports/nang_cap_du_bao_v4_trang_thai.json`; dự báo `reports/du_bao/ket_hop_v4_validation2.csv` (có cột khoảng) |
| `src/nang_cap_du_bao.py`, `reports/nang_cap_du_bao.md` | Nâng cấp dự báo vòng 3 (mục 9.4): dự báo theo tầm, lịch sự kiện / âm lịch, ghép với Prophet → `ket_hop_v3`; trạng thái từng bước ở `reports/nang_cap_du_bao_trang_thai.json` |
| `reports/do_nhay.md`, `reports/ket_qua/k07_do_nhay_lead_time.png` | Thử độ nhạy: tắc cảng, lead time dài thêm, chi phí tăng (mục 11.1); tạo bằng `python src/do_nhay.py` |
| `data/reference/gia_thi_truong.csv`, `reports/cap_nhat_gia.md` | Giá bán lẻ tra cứu từng mã (nguồn, ngày) và bảng giá cũ – mới; bản giá mô phỏng gốc: `data/reference/sku_master_mo_phong.csv` |
| `reports/power_bi/` | 6 file CSV cho Power BI (mô hình hình sao) + `so_doi_chieu.md`; tạo bằng `python src/xuat_power_bi.py`; hướng dẫn `docs/12_power_bi.md` |
