# Lộ trình thực hiện đồ án (từ sau khi làm sạch dữ liệu)

Lập ngày 10/10/2026. Khung theo luồng 8 bước của Báo cáo GĐ1 (`docs/08`).

**Lịch chính thức của trường:**
| Mốc | Ngày |
|---|---|
| Sinh viên thực hiện đồ án (12 tuần) | 14/09/2026 – 06/12/2026 |
| **Nộp báo cáo đồ án** | **09/12/2026** |
| Phân công phản biện | 10/12/2026 |
| Chấm phản biện (3 tuần) | 11/12/2026 – 26/12/2026 |
| Thành lập hội đồng chấm | 27/12/2026 – 29/12/2026 |
| **Bảo vệ đồ án** | **30/12/2026 – 31/12/2026** |

Ngày 10/10/2026 là ngày thứ 27 của 12 tuần. Giai đoạn 1 (đề cương, Chương 2) và Bước 1 (dữ liệu, làm sạch) đã xong.
Còn **8 tuần làm việc (12/10 – 06/12)** + 2 ngày hoàn thiện (07–08/12) trước khi nộp.
Nguyên tắc nén lịch: **viết đồ án song song với chạy mô hình** (không dồn cuối); **LSTM bỏ** trừ khi vượt tiến độ; slide và tập bảo vệ làm từ sau khi nộp đến trước ngày bảo vệ (11–29/12).

Cách dùng: đánh dấu `[x]` khi xong một việc; xong giai đoạn nào thì cập nhật mục 3, 4, 6 của `docs/01`.

---

## 1. Bảng tổng quan

| GĐ | Tên (thuật ngữ logistics) | Bước GĐ1 | Chương | Thời gian | Sản phẩm chính | Trạng thái |
|---|---|---|---|---|---|---|
| 0 | Data Preparation: đối soát, làm sạch | 1 | 3, 4 | trước 10/10 | `data/clean/`, `reports/bao_cao_lam_sach.md` | ✅ Xong |
| A | Phân tích khám phá + tạo đặc trưng (Demand Drivers) | 2 | 4 | T1: 12–18/10 | `src/eda.py`, `src/dac_trung.py`, `reports/eda/` | ✅ Xong 10/10 (sớm hơn lịch) |
| B | Khung đánh giá: chia dữ liệu, backtest, chỉ số | 5 (chuẩn bị) | 4 | T2: 19–21/10 | `src/danh_gia.py` | ✅ Xong 10/10 (sớm hơn lịch) |
| C | Mô hình mốc (Baseline Forecast) | 3 | 4 | T2–T3: 22/10–28/10 | `src/mo_hinh_baseline.py` | ✅ Xong 23/10 |
| D | Mô hình AI: Prophet, LightGBM/XGBoost | 4 | 4 | T3–T4: 29/10–08/11 | `src/mo_hinh_prophet.py`, `src/mo_hinh_lightgbm.py` || ✅ Xong 24/10 (sớm 2 tuần) |
| E | Đo độ chính xác, chọn mô hình (Forecast Accuracy, FVA) | 5 | 4 | T5: 09–11/11 | Sheet `Bang_so_sanh` đã điền || ✅ Xong 24/10 (2 vòng) |
| F | Thiết lập chính sách tồn kho + mô phỏng (Inventory Policy, What-if) | 6 | 4, 5 | T5–T6: 12–22/11 | `src/ton_kho.py` (gồm mô phỏng), bảng trước–sau || ✅ Xong 24/10 (sớm ~4 tuần) |
| G | Dashboard (bản gọn) | 7 | 4 | T7: 23–26/11 | `app/dashboard.py` (Streamlit) | ✅ Xong 23/10 (sớm ~5 tuần) |
| H1 | Viết Chương 1–3 (song song, buổi tối / cuối tuần) | — | 1–3 | T1–T5 | Bản nháp Chương 1, 2 (rà lại), 3 | |
| H2 | Viết Chương 4–5, ráp đồ án, gửi GVHD xem | 8 | 4, 5 | T7–T8: 27/11–06/12 | Bản đồ án hoàn chỉnh | |
| H3 | Sửa cuối, định dạng, in | — | — | 07–08/12 | File nộp | |
| H4 | **Nộp** | — | — | **09/12** | | |
| H5 | Slide, tập bảo vệ, chuẩn bị câu hỏi phản biện | 8 | — | 11–29/12 | Slide 15–20 trang | |
| H6 | **Bảo vệ** | — | — | **30–31/12** | | |

**Song song suốt lộ trình:** làm việc với giảng viên hướng dẫn (mục 3).

---

## 1b. Lịch theo tuần (dán lên chỗ dễ thấy)

| Tuần | Ngày | Việc kỹ thuật (ban ngày) | Việc viết / liên hệ (song song) | Mốc kiểm tra cuối tuần |
|---|---|---|---|---|
| T1 | 12–18/10 | GĐ A: EDA + `dac_trung.py` | Hỏi GVHD về dữ liệu mô phỏng; xin dữ liệu đơn vị thực tập; hỏi ngày bảo vệ | Có file đặc trưng + 6–8 hình EDA |
| T2 | 19–25/10 | GĐ B (3 ngày) → bắt đầu GĐ C | Viết Chương 1 (mở đầu) ✅ nháp 23/10 (`do_an/chuong_1_mo_dau.md`) | Có WMAPE của Naive, Seasonal Naive |
| T3 | 26/10–01/11 | Xong GĐ C → bắt đầu Prophet | Rà Chương 2 theo bảng "điểm khác" ở `docs/08` | Bảng chỉ số đủ mô hình mốc |
| T4 | 02–08/11 | GĐ D: Prophet + LightGBM | Viết Chương 3 (mô tả bài toán và dữ liệu) | Có chỉ số Prophet, LightGBM |
| T5 | 09–15/11 | GĐ E (3 ngày) → bắt đầu GĐ F | **Gửi GVHD bảng so sánh mô hình** | Đã chọn mô hình theo nhóm SKU |
| T6 | 16–22/11 | GĐ F: SS/ROP/EOQ + mô phỏng | Viết Chương 4 phần dữ liệu, mô hình | **Có bảng trước–sau** |
| T7 | 23–29/11 | GĐ G: dashboard bản gọn (3–4 ngày) | Viết Chương 4 phần tồn kho + Chương 5; **gửi GVHD bảng trước–sau** | Dashboard chạy được |
| T8 | 30/11–06/12 | Không làm thêm mô hình mới | Ráp đồ án, gửi GVHD bản đầy đủ, sửa theo góp ý | Bản đồ án hoàn chỉnh |
| — | 07–08/12 | | Định dạng, mục lục, tài liệu tham khảo, in | |
| — | **09/12** | | **Nộp báo cáo** | |
| — | 11–26/12 | Học Power BI 5 buổi (`docs/12_power_bi.md`), làm hồ sơ xin thực tập | Slide, tập nói; trả lời nhận xét của phản biện (nếu có) | |
| — | 27–29/12 | | Tập bảo vệ hoàn chỉnh (bấm giờ), chạy thử demo trên máy sẽ dùng | |
| — | **30–31/12** | | **Bảo vệ** | |

**Nếu trễ:** cuối T4 chưa xong Prophet + LightGBM → chỉ giữ 1 mô hình AI (LightGBM), dời phần còn lại vào "hướng phát triển". Cuối T6 chưa có bảng trước–sau → bỏ dashboard, dùng biểu đồ tĩnh.

## 1d. Nhiệm vụ giảng viên giao thêm

| Nhiệm vụ | Giao | Sản phẩm | Trạng thái |
|---|---|---|---|
| Xây dựng luồng cho hệ thống (nghiệp vụ + dữ liệu), trình bày trực tiếp trên máy trước hội đồng | Tuần 24/10 | `trinh_bay/luong_he_thong.html` (`python src/tao_trang_luong.py`) | ✅ 24/10 |
| Hoàn thiện đẩy dữ liệu qua database | Tuần 24/10 | `data/kho_hang.db` (SQLite), `database/schema.sql`, `src/nap_database.py` | ✅ 24/10 |

Từ GĐ F trở đi: các bước **đọc trực tiếp từ CSDL** (bảng `dm_sku`, khung nhìn `v_du_bao_chon`) và ghi kết quả tồn kho ngược vào CSDL; sau mỗi lần nạp lại thì chạy lại `tao_trang_luong.py`.

## 1c. Tiêu chí thành công (đề xuất 23/10, các ngưỡng số cần giảng viên duyệt)

| Mặt | Tiêu chí đạt | Đo bằng | Trạng thái |
|---|---|---|---|
| **1. Được chấp nhận** | Giảng viên đồng ý dùng M5 cho dự báo và dữ liệu mô phỏng cho nghiệp vụ (quyết định 05/11, mục 3) | Câu trả lời của giảng viên | ⏳ **Chưa hỏi, rủi ro lớn nhất** |
| | Nộp đủ 5 chương đúng mẫu trường trước 09/12 | Lịch tuần mục 1b | ⏳ |
| **2. Dự báo** | Mô hình chọn được giảm WMAPE ít nhất **20%** so với Seasonal Naive trên tập test | `reports/bang_so_sanh_test.md`, cột FVA | ✅ v4 cập nhật mỗi tuần, WMAPE 0,356 (01/11; v3 0,368) |
| | Nhóm Z (mùa vụ) giảm rõ rệt (mốc hiện tại: WMAPE 1,64) | Cột WMAPE_Z | ✅ Prophet 0,638 (24/10) |
| | Bias trong khoảng **±5%** (không thừa, thiếu có hệ thống) | Cột Bias_pct | ✅ Mô hình v4 +3,0% (01/11; v3 +3,9%, v2 +6,3%) |
| **3. Tồn kho** (trọng tâm đề tài) | Chính sách dùng dự báo AI đạt Fill Rate ≥ **95%** với tồn kho bình quân **không cao hơn** hiện trạng | Bảng trước–sau GĐ F | ✅ Fill Rate 95,82%; tồn kho −0,7% so với hiện trạng (biết trước nhu cầu); nhóm X −29% (dự báo cập nhật mỗi tuần, 01/11; v3: +37%) |
| | Giảm số ngày hết hàng và tổng chi phí đặt hàng + lưu kho so với hiện trạng | Bảng trước–sau GĐ F | ✅ Ngày thiếu −53%; chi phí liên quan −9,8% so với hiện trạng, −35% so với dự báo mốc (01/11) |
| **4. Tin cậy và học được** | Chạy lại toàn bộ từ đầu bằng các lệnh trong README, ra đúng kết quả | Chạy thử trên máy sạch | ✅ 12/11: chạy lại 114 bước trên bản sạch (11 giờ máy), 226 tệp giống hệt; 8 tệp khác không lệch số nào (bảng cũ thiếu dòng NF, báo cáo tạo bằng code cũ, nhật ký chạy) |
| | Không rò rỉ dữ liệu: chia theo thời gian, chỉ dùng thông tin biết trước | Kiểm tra trong `danh_gia.py` | ✅ |
| | Tự giải thích được từng bước và trả lời câu hỏi phản biện | `docs/11` câu hỏi tự kiểm tra | 🔄 Bài 1–4 |

**Lưu ý trung thực:** nếu mô hình AI **không** thắng mô hình mốc ở một nhóm nào đó, đó vẫn là kết quả hợp lệ và đáng viết, miễn phân tích được vì sao. Không chỉnh dữ liệu hay cách chấm để AI "thắng".

## 2. Chi tiết từng giai đoạn

### GĐ A. Phân tích khám phá (EDA) + tạo đặc trưng (T1: 12–18/10)
**Mục tiêu:** hiểu dữ liệu bằng hình, rồi biến lịch lễ/bão/sale/khuyến mãi thành cột số cho mô hình.

Phân tích khám phá (`src/eda.py`, hình lưu `reports/eda/`):
- [x] Biểu đồ tổng xuất theo ngày toàn kho; đánh dấu Tết, bão Yagi, 11.11.
- [x] Biểu đồ 6 SKU đại diện: 2 nhóm X ổn định, 2 nhóm Z mùa vụ (bánh trung thu, mứt Tết), 1 hàng bão (mì gói), 1 hàng bán thưa.
- [x] Tách xu hướng / mùa vụ / nhiễu (`seasonal_decompose`, chu kỳ 7 và 365, **không dùng 30**).
- [x] Bảng ma trận ABC × XYZ (tập train, giá thị trường 24/10: A-X 20, A-Z 5, B-Z 15, C-Z 20...).
- [x] Phân loại hàng bán thưa theo ADI–CV² (Syntetos–Boylan): smooth / erratic / intermittent / lumpy. Hiện có 9 SKU có trên 30% ngày bán 0.

Tạo đặc trưng (`src/dac_trung.py` → `data/features/dac_trung.csv`):
- [x] Lịch: thứ, tháng, tuần trong năm, mùa (Xuân/Hạ/Thu/Đông), cuối tuần, đầu/giữa/cuối tháng.
- [x] Sự kiện từ `data/reference/`: cờ lễ có cửa sổ trước–sau, số ngày đến Tết, cờ bão + mức độ (cửa sổ −3…+14), cờ sale 11.11/12.12/Black Friday, cờ khuyến mãi (`lich_khuyen_mai.csv`), cờ sự kiện đột biến.
- [x] Giá trị trễ: lag_1, lag_7, lag_14, lag_28, lag_364; trung bình trượt 7/28 ngày (chỉ dùng dữ liệu **quá khứ**, `shift(1)` trước khi tính).
- [x] Đặc trưng SKU: nhóm hàng, ABC, XYZ, loai_mua_vu, giá.
- [x] Xử lý ngày hết hàng: gắn cờ, đặt `y` = rỗng khi huấn luyện (không coi là cầu thật).
- [x] Kiểm tra: đối chiếu cờ dựng lại với answer_key (chỉ để kiểm tra), khớp ≥ 99%. → **Kết quả 10/10: thu, mua, khuyen_mai, trong_tuan_tet, bao_lu_muc_do khớp 100%; lag không nhìn tương lai.**
- Ghi chú: phân loại ABC/XYZ trong `sku_master` tính trên cả 36 tháng (có cả giai đoạn test) → mô hình dùng `abc_train`, `xyz_train` tính trên tập train (2 SKU đổi nhóm ABC theo giá thị trường, 8 với giá mô phỏng cũ; 3 SKU đổi XYZ). Đơn B2B đột biến (`don_b2b`) không biết trước → chỉ dùng để loại khỏi huấn luyện, không làm biến dự báo.
- Phân loại nhu cầu (ADI/CV²): 58 smooth, 54 erratic, 9 lumpy → 9 SKU lumpy thử thêm Croston/TSB.
- EDA (`reports/bao_cao_eda.md`, 8 hình `reports/eda/h01–h08`): xu hướng tổng gần như **đi ngang**; mùa vụ năm mạnh (Tết, Trung thu, Noel); Chủ nhật chỉ bằng 0,53 mức TB → chu kỳ 7 ngày bắt buộc; khuyến mãi làm bán tăng trung vị 60% (so cùng tháng); Tết âm lịch đổi ngày mỗi năm nên chu kỳ 52 tuần không đủ, cần biến ngày lễ.

**Xong khi:** file đặc trưng có đủ 132.616 dòng, không có cột nào nhìn thấy tương lai, có 6–8 hình EDA dùng được cho Chương 4.

### GĐ B. Khung đánh giá (T2: 19–21/10)
**Mục tiêu:** mọi mô hình được chấm trên **cùng** một đề thi.

- [x] Chốt cách chia (đề xuất, cần duyệt):
  - Train: 01/10/2023 – 30/09/2025 (24 tháng, đủ 2 mùa Tết).
  - Validation (dò tham số): các mốc trong 04/2025 – 09/2025.
  - Test (chấm điểm cuối): backtest cuốn chiếu 10/2025 – 09/2026, mỗi 4 tuần đặt 1 mốc, dự báo 28 ngày (12–13 lần). Năm test có Tết 2026, Trung thu 2026, 7 cơn bão năm 2025.
- [x] Tầm dự báo: 28 ngày (lớn hơn lead time dài nhất 15 ngày + chu kỳ kiểm hàng).
- [x] Viết hàm chỉ số: MAE, RMSE, WMAPE, MASE (so Seasonal Naive 7), Bias = mean(A − F).
- [x] Bỏ ngày kho đóng cửa và ngày hết hàng khỏi phần chấm điểm.
- [x] Hàm xuất kết quả theo SKU, theo nhóm ABC/XYZ, theo toàn kho.

**Xong khi:** chạy thử với mô hình Naive ra được bảng chỉ số đầy đủ. → **Đạt 10/10.**

Kết quả và quy ước đã chốt trong code:
- Validation: 6 mốc (31/03/2025 … 18/08/2025); Test: 13 mốc (30/09/2025 … 01/09/2026); mỗi mốc dự báo 28 ngày.
- Chấm điểm trên `y_cham` = nhu cầu tin được: bỏ ngày kho đóng cửa, ngày hết hàng, ngày đơn B2B đột biến.
- Cột được nhìn thấy ở tương lai (`KNOWN_AHEAD`): lịch, lễ/sự kiện, sale, khuyến mãi, nghỉ kho, thông tin SKU. **Bão không được biết trước** (ngoài đời chỉ biết 3–5 ngày) → mô hình chỉ thấy bão trong quá khứ.
- Chỉ số: MAE, RMSE, WMAPE, WMAPE theo tuần, MASE (mẫu số = Seasonal Naive 7 ngày một bước trên train, nên dự báo 28 ngày thường có MASE > 1), Bias % (dương = dự báo thiếu).
- Mốc so sánh (test): Naive WMAPE 0,739; **Seasonal Naive 7 WMAPE 0,773**, WMAPE tuần 0,598. Theo nhóm: X 0,48 · Y 0,60 · Z 1,64. Mốc xấu nhất là mốc 17/02/2026 (ngày Tết, WMAPE 2,17): lặp lại tuần cao điểm trước Tết cho giai đoạn sau Tết.
- Kết quả: `reports/ket_qua_mo_hinh.csv` (1 dòng / mô hình / tập), dự báo chi tiết `reports/du_bao/`.

### GĐ C. Mô hình mốc (22–28/10)
- [x] Naive, Seasonal Naive (7 ngày), Trung bình trượt 28 ngày.
- [x] ETS / Holt-Winters.
- [x] SARIMA cho nhóm A (28 SKU theo giá thị trường 24/10; 31 với giá mô phỏng cũ); dùng auto_arima hoặc statsforecast cho nhanh.
- [x] Croston / TSB cho nhóm hàng bán thưa (từ GĐ A).
- [x] Ghi kết quả vào `reports/ket_qua_mo_hinh.csv`. → **Mốc tốt nhất: TB trượt 28 ngày, WMAPE 0,640** (giảm 17,2% so với Seasonal Naive). Chi tiết: `docs/10` mục 7.

**Xong khi:** có WMAPE mốc của Seasonal Naive. Đây là con số mọi mô hình AI phải thắng.

### GĐ D. Mô hình AI (29/10–08/11)
- [x] **Prophet** từng SKU: holidays = `lich_su_kien_prophet.csv` + sale; thêm biến khuyến mãi, bão (extra regressor). Dò cửa sổ lễ trên validation. → **Xong 24/10: test WMAPE 0,454** (additive; −29% so với TB trượt 28). Bão không dùng (không biết trước).
- [x] **LightGBM hoặc XGBoost**: một mô hình chung cho cả 121 SKU, dùng file đặc trưng; dự báo nhiều bước bằng lag ≥ 28 (hoặc dự báo đệ quy). → **Xong 24/10: test WMAPE 0,399** (tốt nhất theo ngày; 0,400 với giá cũ) nhưng Bias +11,7% (thiếu hàng mùa vụ trước cao điểm).
- [x] Phân tích độ quan trọng đặc trưng (feature importance): biến nào quyết định nhu cầu (để viết Chương 4). → `reports/lightgbm_quan_trong.csv`
- [ ] ~~LSTM~~: bỏ do lịch 12 tuần; chỉ làm nếu xong GĐ F trước 22/11. Trong đồ án ghi vào "hướng phát triển".

**Xong khi:** mỗi mô hình có đủ chỉ số trên cùng tập test như GĐ C.

### GĐ E. Chọn mô hình (09–11/11)
- [ ] Điền `Bang_so_sanh` trong `reports/Mo_hinh_va_danh_gia.xlsx`.
- [ ] So sánh theo nhóm ABC × XYZ: có thể mỗi nhóm thắng một mô hình khác nhau.
- [ ] Tính FVA: mô hình AI giảm WMAPE bao nhiêu % so với Seasonal Naive.
- [ ] Vẽ dự báo chồng thực tế quanh Tết 2026 và 1 cơn bão: mô hình có bắt được đỉnh không.
- [ ] Quy tắc chọn: sai số thấp nhất; nếu chênh dưới ~2 điểm WMAPE thì chọn mô hình đơn giản hơn.

**Vòng 3 (30–31/10, `src/nang_cap_du_bao.py`, luật `docs/10` mục 9.4):** dự báo theo tầm + lịch sự kiện / âm lịch → test WMAPE 0,368, Bias +3,9%; mô hình dùng tiếp `ket_hop_v3`.

**Vòng 4 (31/10, `src/nang_cap_du_bao_v4.py`, luật `docs/10` mục 9.5, test giữ kín):** bảng rủi ro định lượng; cập nhật dự báo mỗi tuần (validation2 WMAPE 0,358, tồn kho −27%); khoảng dự báo 80 / 95% đạt; tự hiệu chỉnh và cảnh báo bão bị bỏ.

### GĐ F. Chính sách tồn kho + mô phỏng (12–22/11)
**Đây là phần "tối ưu tồn kho" trong tên đề tài; giám khảo nhìn vào đây đầu tiên.**

- [x] `src/ton_kho.py`: với mỗi SKU tính D, d, σ (độ lệch chuẩn **sai số dự báo** trong lead time), SS, ROP, EOQ; làm tròn theo MOQ.
- [x] Thử 3 mức phục vụ: 90%, 95%, 99%.
- [x] Mô phỏng (trong `src/ton_kho.py`, xong 24/10): chạy lại 12 tháng test theo từng chính sách (thêm chính sách thứ 4: AI + hiệu chỉnh lệch):
  1. **Hiện trạng**: chính sách đặt hàng đang có trong dữ liệu (người lập kế hoạch có độ lệch).
  2. **Seasonal Naive + công thức**: chính sách dựa trên dự báo mốc.
  3. **AI + công thức**: chính sách dựa trên mô hình thắng ở GĐ E.
- [ ] KPI mỗi chính sách: Fill Rate, số ngày hết hàng, tồn kho bình quân, DOH, vòng quay, chi phí đặt hàng + lưu kho, hàng tồn dư sau mùa.
- [x] Bảng **trước – sau** (sản phẩm quan trọng nhất của đồ án): `reports/ton_kho_so_sanh.md`, `docs/10` mục 10.2. Dòng KPI trên còn thiếu DOH, vòng quay, tồn dư sau mùa.
- [x] Thử độ nhạy: lead time +3–7 ngày (tắc cảng), chi phí đặt hàng +20% (cước tăng), dùng bảng ở `docs/07`. → **Xong 23/10** (`src/do_nhay.py`, thêm lead time +2 ngày cả năm và chi phí lưu kho +15%): tắc cảng chỉ làm Fill Rate giảm 0,5–1,5 điểm, AI + hiệu chỉnh vẫn rẻ nhất ở 13/13 đợt (cả trước và sau cập nhật giá); lead time dài ra mà không cập nhật công thức thì −5,3 điểm. Chi tiết `docs/10` mục 11.1.

**Xong khi:** có bảng trước–sau và 2–3 biểu đồ, ghi rõ "kết quả trên dữ liệu mô phỏng".

### GĐ G. Dashboard bản gọn (23–26/11)
- [x] Streamlit, tối đa 4 khu: chọn SKU → dự báo vs thực tế; cảnh báo SKU dưới ROP; KPI trước–sau; bảng SS/ROP/EOQ. → **24/10: tăng lên 5 khu** (người dùng duyệt): thêm khu ① Tổng quan dữ liệu (6 biểu đồ phân tích, nói rõ dữ liệu mô phỏng là gì).
- [x] Chạy được bằng 1 lệnh, dùng để demo khi bảo vệ: `streamlit run app/dashboard.py` (cần chạy trước `nap_database.py`, `ton_kho.py`).
- [x] Power BI: không thay Streamlit. Dữ liệu đã chuẩn bị 23/10 (`python src/xuat_power_bi.py` → `reports/power_bi/`); **học và dựng báo cáo sau khi nộp (11–26/12)** theo `docs/12_power_bi.md` (5 buổi, có số đối chiếu).

Kết quả 23/10: dashboard **chỉ đọc** CSDL (mở SQLite ở chế độ read-only). Khu ③ (cảnh báo tồn kho; số khu theo bản 5 khu từ 24/10) cho chọn một ngày trong năm test làm "hôm nay" và liệt kê SKU hết hàng / cần đặt hôm nay / tồn dưới ROP nhưng hàng đang về; đây là **phát lại mô phỏng** của GĐ F, không phải hệ thống chạy thật. Chi tiết: `docs/10` mục 12.

### GĐ H. Viết đồ án và bảo vệ (song song T1–T8, nộp 09/12, slide 11–29/12, bảo vệ 30–31/12)
- [x] Chương 1: Mở đầu (lý do, mục tiêu, phạm vi, phương pháp). → Nháp lần 1: `do_an/chuong_1_mo_dau.md` (còn chỗ [CẦN TRÍCH DẪN] phải tự tra nguồn).
- [ ] Chương 2: Cơ sở lý thuyết (đã có từ GĐ1, rà lại theo bảng "điểm khác" trong `docs/08`).
- [ ] Chương 3: Mô tả bài toán và dữ liệu (quyết định 05/11: chưa thực tập, chưa có dữ liệu thực tập nên **không viết thực trạng kho**). Dàn ý:
  - 3.1. Bối cảnh: kho tổng của chuỗi siêu thị nói chung (không gắn với đơn vị cụ thể), luồng từ nhà cung cấp qua kho đến siêu thị và đơn online; đặc điểm chung lấy từ tài liệu công khai, có trích dẫn.
  - 3.2. Phát biểu bài toán: đặt mã nào, khi nào, bao nhiêu; đầu vào, đầu ra, mục tiêu, ràng buộc (lead time, lượng đặt tối thiểu, sức chứa, hạn sử dụng), chỉ số đánh giá.
  - 3.3. Dữ liệu: M5 (số bán thật, Mỹ) và bộ mô phỏng (nghiệp vụ Việt Nam); bảng phân biệt phần nào thật, phần nào giả định.
  - 3.4. Đặc điểm dữ liệu: phân loại ABC/XYZ, mùa vụ, khuyến mãi của từng bộ.
  - 3.5. Tiền xử lý: làm sạch theo đẳng thức tồn kho, nhận diện hết hàng (mô phỏng); giữ nguyên số bán, suy khuyến mãi từ giá (M5).
  - 3.6. Giới hạn của dữ liệu: không có số liệu của một kho Việt Nam cụ thể.
- [ ] Chương 4: Xây dựng mô hình (dữ liệu → EDA → mô hình → so sánh → tồn kho → dashboard).
- [ ] Chương 5: Kết luận, đề xuất cho kho cùng loại, không gắn với đơn vị cụ thể (ví dụ: áp ROP tự động cho nhóm A trước, mở rộng B/C sau 3 tháng), hạn chế (không có dữ liệu của kho Việt Nam: M5 là số của Mỹ, phần còn lại là mô phỏng và giả định), hướng phát triển.
- [ ] Slide 15–20 trang, 2–3 biểu đồ chính, demo dashboard (làm trong 11–29/12, sau khi nộp).
- [ ] Chuẩn bị câu hỏi phản biện: vì sao dữ liệu mô phỏng, vì sao WMAPE không phải MAPE, vì sao không chia ngẫu nhiên, LSTM có hơn không...

---

## 3. Việc song song: giảng viên (phần đơn vị thực tập dừng từ 05/11)

| Khi nào | Việc | Ai |
|---|---|---|
| T1 (trước 18/10) | Hỏi giảng viên: dùng dữ liệu mô phỏng cho Chương 4 có được không; có cần dữ liệu thật không (ngày bảo vệ đã có: 30–31/12) | Bạn |
| T1 (trước 18/10) | Xin đơn vị thực tập: file xuất nhập tồn theo ngày (date, mã SKU, nhập, xuất, tồn cuối), danh mục SKU, lead time nhà cung cấp, lịch khuyến mãi. Tối thiểu 12 tháng, ưu tiên nhóm A | Bạn |
| Trong GĐ A–C | Hỏi kho: loại kho (B2B hay fulfillment cho sàn), chính sách đặt hàng hiện tại, mức phục vụ mục tiêu, chi phí đặt hàng và lưu kho ước tính | Bạn |
| Khi có dữ liệu thật | Thay file raw, giữ tên cột, chạy lại toàn bộ script. **Hạn chót nhận dữ liệu thật: 08/11** (sau đó không kịp chạy lại, chỉ dùng cho Chương 3) | AI hỗ trợ |
| Cuối GĐ E và F | Gửi giảng viên bảng so sánh mô hình và bảng trước–sau để xin góp ý | Bạn |

**Quyết định của người làm đồ án (05/11): không có dữ liệu từ đơn vị thực tập, dùng dữ liệu hiện có.** Số bán thật M5 làm kết quả chính cho phần dự báo; bộ mô phỏng minh họa nghiệp vụ kho Việt Nam mà M5 không có (Tết, bão, hàng mùa vụ, tên hàng, hạn sử dụng, làm sạch dữ liệu), ghi rõ là mô phỏng; phần tồn kho báo cả hai bộ, gồm cả việc lợi ích giảm từ 35,3% xuống 1,7%. Giảng viên chưa xác nhận cách này. Việc "xin dữ liệu đơn vị thực tập" và "hỏi kho" ở bảng trên dừng lại vì người làm đồ án chưa thực tập; quy trình vẫn thay được dữ liệu nếu sau này có. Chương 3 đổi thành mô tả bài toán; cần kiểm tra mẫu đồ án của trường có bắt buộc chương thực trạng không.

---

## 4. Quyết định cần chốt (ghi kết quả vào đây)

| Quyết định | Đề xuất | Đã chốt |
|---|---|---|
| Hạn nộp đồ án, ngày bảo vệ | | Nộp 09/12/2026; bảo vệ 30–31/12/2026 |
| Dự báo theo ngày hay theo tuần | Theo ngày, chấm điểm thêm tổng theo tầm lead time | |
| Cách chia train/validation/test | Như GĐ B | |
| Thư viện | statsforecast (baseline, Croston), prophet, lightgbm, streamlit | |
| Có làm LSTM không | Không (lịch 12 tuần) | Bỏ, trừ khi xong GĐ F trước 22/11 |
| Dashboard | Streamlit | Streamlit (23/10), chỉ đọc CSDL; 5 khu từ 24/10; **31/10 làm lại thành 4 màn** kiểu Power BI (bộ lọc chung, lọc chéo, đi sâu, duyệt đơn, "Thử nếu…"), giao diện "phiếu vận đơn" |
| Loại kho mà dữ liệu mô phỏng đại diện | Kho tổng chuỗi bán lẻ / nhà phân phối B2B / kho TMĐT | **Kho tổng (trung tâm phân phối) của chuỗi siêu thị / bách hóa** (24/10): khớp nhất với dữ liệu (17 nhóm hàng lẫn lộn, đơn vị thùng, Chủ nhật bán 0,53, khuyến mãi theo mã, đơn B2B). Nếu đơn vị thực tập là loại kho khác thì xem lại để Chương 3–4 nhất quán |
| Giá mặt hàng | Giữ giá mô phỏng cũ / cập nhật theo giá thị trường | **Cập nhật theo giá bán lẻ hiện tại** (24/10): giá bán = giá bán lẻ tra công khai (ghi nguồn, ngày); giá vốn = giá bán ÷ (1 + biên lãi cũ của mã) là giả định. Không sinh lại dữ liệu gốc; chạy lại từ bước đặc trưng (`data/reference/gia_thi_truong.csv`) |
| Phân hệ điều vận (số xe, xếp chuyến, cảnh báo cao điểm) | Ngoài kế hoạch chính | Chỉ làm nếu xong GĐ G trước hạn, hoặc làm sau khi nộp (11–26/12) để làm hồ sơ xin thực tập. Không được làm chậm GĐ C–F |

## 5. Rủi ro và cách xử lý
| Rủi ro | Cách xử lý |
|---|---|
| Không xin được dữ liệu thật (**đã xảy ra, 05/11**) | M5 cho dự báo, mô phỏng cho nghiệp vụ, nói rõ ở phần hạn chế; quy trình đã sẵn sàng thay dữ liệu |
| Prophet/LightGBM cài lỗi trên Windows | Dùng môi trường ảo (`.venv`), cài sớm ngay đầu GĐ C |
| Chạy 121 SKU × 13 mốc backtest quá lâu | Chạy nhóm A trước, các nhóm khác chạy sau hoặc giảm số mốc |
| Mô hình AI không thắng Seasonal Naive | Vẫn là kết quả hợp lệ; phân tích vì sao, nhóm nào AI có lợi |
| Trễ tiến độ | Xem dòng "Nếu trễ" ở mục 1b; ưu tiên GĐ F và Chương 4 hơn dashboard |
| Dồn viết vào cuối | Mỗi tuần viết ít nhất 1 phần (cột "Việc viết" mục 1b) |
