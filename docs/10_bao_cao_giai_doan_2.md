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

Trạng thái: 1–8 ✅ · 9 ⏳ · 8 ⏳ · 9 ⏳ · 10 ⏳ · 11 ⏳ · 12 ⏳.

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
| h06 | Ma trận ABC × XYZ (tập train) | A-X 22, A-Y 3, A-Z 6, B-X 18, B-Y 6, B-Z 17, C-X 31, C-Y 1, C-Z 17 |
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
- Phân loại ABC/XYZ trong `sku_master` tính trên cả 36 tháng (gồm giai đoạn test) → là nhìn trước tương lai. Tính lại trên tập train: 8 SKU đổi nhóm ABC, 3 SKU đổi nhóm XYZ. Mô hình dùng bản `*_train`.
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
| ARIMA (tự chọn) | Tự hồi quy + trung bình trượt, chu kỳ tuần | Chỉ 31 SKU nhóm A (chậm ~3 giây/SKU/mốc, gấp ~20 lần ETS) |
| Croston SBA | Tách "bao lâu bán 1 lần" và "mỗi lần bán bao nhiêu" | Thiết kế cho hàng bán rời rạc |
| TSB | Như Croston nhưng cập nhật xác suất bán mỗi ngày | alpha = 0,2 |

**Kết quả tập test (13 mốc, 10/2025–9/2026):**
| Mô hình | WMAPE | WMAPE tuần | Bias % | WMAPE A | WMAPE X | WMAPE Y | WMAPE Z | WMAPE lumpy | FVA so SN7 |
|---|---|---|---|---|---|---|---|---|---|
| **TB trượt 28** | **0,640** | **0,511** | −0,8% | 0,503 | 0,408 | 0,653 | **1,272** | **1,860** | **+17,2%** |
| Croston SBA | 0,651 | 0,516 | +0,4% | **0,492** | **0,395** | 0,589 | 1,365 | 2,184 | +15,8% |
| TSB | 0,686 | 0,549 | −6,5% | 0,504 | 0,410 | 0,555 | 1,477 | 2,476 | +11,2% |
| ETS | 0,721 | 0,614 | −16,7% | 0,531 | 0,428 | **0,527** | 1,574 | 2,291 | +6,8% |
| Naive | 0,739 | 0,634 | −9,1% | 0,541 | 0,491 | 0,639 | 1,442 | 2,408 | +4,4% |
| Seasonal Naive 7 | 0,773 | 0,598 | −11,0% | 0,559 | 0,475 | 0,597 | 1,636 | 2,691 | 0 |
| ARIMA (chỉ nhóm A) | — | — | — | 0,493 | — | — | — | — | +11,8% (trên A) |

Validation (6 mốc, 4–9/2025, giai đoạn "êm"): TB trượt 28 0,426 · Croston 0,415 · TSB 0,425 · ETS 0,450 · ARIMA (A) 0,386 · Seasonal Naive 0,498. Thứ hạng giữa validation và test khác nhau → kết luận dựa trên test.

**Nhận xét:**
1. **Mô hình mốc mạnh nhất là trung bình trượt 28 ngày** (WMAPE 0,640, giảm 17,2% so với Seasonal Naive). Đây là con số mô hình AI thực sự phải thắng, không chỉ Seasonal Naive.
2. **Seasonal Naive kém nhất** dù dữ liệu có chu kỳ tuần rõ: chép nguyên 1 tuần thì chép cả nhiễu của tuần đó. Làm mượt (trung bình 28 ngày) ổn định hơn.
3. **ARIMA không đáng công:** trên nhóm A chỉ ngang Croston (0,493 so với 0,492) nhưng chậm gấp ~20 lần. Không mở rộng ARIMA cho 121 SKU.
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
| **Prophet** | **0,454** | **0,257** | −4,9% | **0,391** | **0,383** | **0,486** | **0,638** | **0,725** | **+41,3%** |
| TB trượt 28 (mốc tốt nhất) | 0,640 | 0,511 | −0,8% | 0,503 | 0,408 | 0,653 | 1,272 | 1,860 | +17,2% |
| Seasonal Naive 7 | 0,773 | 0,598 | −11,0% | 0,559 | 0,475 | 0,597 | 1,636 | 2,691 | 0 |

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
- Hàm mất mát chọn trên validation: **tweedie** WMAPE 0,351 tốt hơn l2 0,420. Tham số: 600 cây, learning rate 0,05, 63 lá. Rất nhanh: ~3 giây/mốc (Prophet ~67 giây).

**Kết quả tập test:**
| Mô hình | WMAPE | WMAPE tuần | Bias % | WMAPE A | WMAPE X | WMAPE Y | WMAPE Z | WMAPE lumpy | FVA so SN7 |
|---|---|---|---|---|---|---|---|---|---|
| **LightGBM** | **0,400** | 0,270 | **+11,6%** | **0,338** | **0,312** | **0,392** | 0,643 | 0,823 | **+48,3%** |
| Prophet | 0,454 | **0,257** | −4,9% | 0,391 | 0,383 | 0,486 | **0,638** | **0,725** | +41,3% |
| TB trượt 28 | 0,640 | 0,511 | −0,8% | 0,503 | 0,408 | 0,653 | 1,272 | 1,860 | +17,2% |

- Theo mốc: LightGBM thắng Prophet ở **12/13 mốc** (thua mốc 01/09/2026: 0,57 so với 0,52).
- **Bias theo nhóm:** X +2,3% · Y −2,3% · **Z +40,8%**. Dự báo thiếu dồn vào các mốc trước cao điểm: 30/09/2025 (+26%), 20/01/2026 (+38%, trước Tết), 01/09/2026 (+30%, trước Trung thu).

**Độ quan trọng đặc trưng** (tỷ trọng gain, trung bình 13 mốc test; `reports/lightgbm_quan_trong.csv`): mã SKU 35,6% · TB 7 ngày tính đến t−28 10,9% · số bán cùng ngày năm trước (lag_364) 7,7% · loại mùa vụ 7,3% · TB 28 ngày đến t−28 5,7% · **số ngày đến Tết 5,5%** · lag_28 4,2% · cờ Trung thu 3,2% · ... · khuyến mãi 1,2% (hạng 13).

**Nhận xét:**
1. LightGBM chính xác nhất theo ngày (giảm 48% so với Seasonal Naive, 37% so với TB trượt 28), đặc biệt ở hàng ổn định (X: 0,312) và chạy nhanh hơn Prophet khoảng 20 lần.
2. Nhưng **dự báo thiếu hàng mùa vụ trước cao điểm** (Z +40,8%), vượt ngưỡng Bias ±5% của tiêu chí thành công. Nguyên nhân có thể: mô hình dựa nhiều vào số bán cùng ngày năm trước (lag_364) trong khi Tết âm lịch lệch vài tuần mỗi năm, và dữ liệu học mới có 2 mùa Tết. Với kho, thiếu hàng trước Tết là sai lầm đắt nhất.
3. Theo tuần, Prophet vẫn nhỉnh hơn (0,257 so với 0,270) nhờ không bị lệch có hệ thống.
4. Hai mô hình mạnh ở hai nhóm khác nhau (LightGBM: X/Y; Prophet: Z ít lệch hơn) → hướng xử lý ở GĐ E: **chọn mô hình theo nhóm SKU** hoặc **kết hợp** (lấy trung bình hai dự báo), quyết định **trên tập validation**, không nhìn tập test.
5. Khuyến mãi chỉ xếp hạng 13 dù EDA cho thấy tăng 60%: khuyến mãi chỉ chiếm ~8% số ngày, nên tổng "đóng góp" nhỏ dù tác động mỗi lần lớn. Độ quan trọng kiểu gain đo tổng đóng góp, không đo độ lớn tác động.

### 8.3. LSTM

Bỏ khỏi kế hoạch; ghi vào hướng phát triển (lý do: mỗi SKU chỉ ~1.096 điểm, khó giải thích, hiếm khi hơn Prophet/XGBoost; xem `docs/06`).

## 9. So sánh và chọn mô hình ⏳ (kế hoạch 09–11/11)

- Bảng so sánh toàn bộ mô hình trên cùng tập test (điền từ `reports/ket_qua_mo_hinh.csv`): ⏳
- So sánh theo nhóm ABC × XYZ và loại nhu cầu; FVA so với Seasonal Naive: ⏳
- Biểu đồ dự báo chồng thực tế quanh Tết 2026 và một cơn bão: ⏳
- Quy tắc chọn: sai số thấp nhất; nếu chênh dưới khoảng 2 điểm WMAPE thì chọn mô hình đơn giản hơn. Mô hình được chọn: ⏳

## 10. Chính sách tồn kho ⏳ (kế hoạch 12–22/11)

- Công thức (xem `docs/02`): EOQ = √(2DS/H); SS = z·σd·√LT (khi LT dao động: SS = z·√(LT·σd² + d²·σLT²)); ROP = d·LT + SS.
- σd lấy từ độ lệch chuẩn **sai số dự báo**, không phải độ lệch chuẩn nhu cầu thô.
- Ba mức phục vụ thử: 90%, 95%, 99%. Làm tròn theo MOQ.
- Bảng SS, ROP, EOQ theo SKU: ⏳

## 11. Mô phỏng và bảng trước–sau ⏳

Ba chính sách so sánh trên 12 tháng test: (1) hiện trạng; (2) công thức + dự báo mốc; (3) công thức + dự báo AI.

| KPI | Hiện trạng | Dự báo mốc | Dự báo AI |
|---|---|---|---|
| Fill Rate | ⏳ | ⏳ | ⏳ |
| Số ngày hết hàng | ⏳ | ⏳ | ⏳ |
| Tồn kho bình quân | ⏳ | ⏳ | ⏳ |
| DOH | ⏳ | ⏳ | ⏳ |
| Chi phí đặt hàng + lưu kho | ⏳ | ⏳ | ⏳ |
| Hàng tồn dư sau mùa | ⏳ | ⏳ | ⏳ |

Thử độ nhạy (lead time +3–7 ngày; chi phí đặt hàng +20%; xem `docs/07`): ⏳

## 12. Dashboard ⏳ (kế hoạch 23–26/11)

Streamlit, tối đa 4 khu: dự báo vs thực tế theo SKU; cảnh báo SKU dưới ROP; KPI trước–sau; bảng SS/ROP/EOQ. ⏳

## 13. Hạn chế và việc còn treo

**Hạn chế đã biết:**
- **Lợi thế "biết đề" của dữ liệu mô phỏng:** mô hình dùng đúng lịch lễ và lịch khuyến mãi mà bộ sinh dữ liệu đã dùng; trên dữ liệu thật, cửa sổ lễ phải tự ước lượng nên mức cải thiện (Prophet −41% so với Seasonal Naive) nhiều khả năng thấp hơn.
- Toàn bộ kết quả trên **dữ liệu mô phỏng**; mức tác động của bão, ngày lễ, khuyến mãi là giả định của người lập dữ liệu, nên độ chính xác tuyệt đối không phản ánh kho thật. Giá trị của đồ án nằm ở quy trình và ở việc so sánh tương đối giữa các mô hình.
- Mô hình dự báo biết lịch lễ và khuyến mãi chính xác; ngoài đời lịch khuyến mãi có thể đến muộn hoặc thay đổi.
- Hiệu ứng sale chỉ mô phỏng cho 11.11, 12.12, Black Friday; các sale khác chưa có.
- Chưa mô phỏng: tăng giá xăng, tắc cảng, ngày lương, rằm/mùng 1, SKU mới và ngừng bán (xem `docs/01` mục 6).
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
