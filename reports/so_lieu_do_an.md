# Sổ số liệu đồ án

Tạo tự động lúc 10/11/2026 22:07 bằng `python src/so_lieu_do_an.py`: mọi số đọc từ CSDL và tệp kết quả, không ghi tay. Khi viết đồ án lấy số ở đây.

**Lưu ý chung:** các số ở mục 1–9 là kết quả trên **dữ liệu mô phỏng**, không phải số liệu kho thật. Dữ liệu đổi thì số đổi, và mô hình được chọn có thể đổi.

## 1. Dữ liệu (nguồn: CSDL)

| Hạng mục | Giá trị |
|---|---|
| Số mã / nhóm hàng / nhà cung cấp | 121 / 17 / 14 |
| Thời gian | 2023-10-01 – 2026-09-30 (1.096 ngày) |
| Dòng thô / sạch / đã sửa | 132.814 / 132.616 / 687 |
| Tỉ lệ ngày-mã hết hàng | 3,2% |

Ma trận ABC × XYZ (số mã):

| ABC \ XYZ | X | Y | Z |
|---|---|---|---|
| A | 20 | 3 | 5 |
| B | 19 | 6 | 15 |
| C | 32 | 1 | 20 |

Đặc điểm thêm:

| Đặc điểm | Giá trị |
|---|---|
| Ngày kho nghỉ (cả kho) | 38 ngày |
| Xuất kho mỗi ngày mở cửa (toàn kho): trung bình / trung vị | 7.435 / 6.864 |
| Xuất kho mỗi mã mỗi ngày: trung vị; tỉ lệ ngày-mã bằng 0 | 28,0; 6,8% |
| Khuyến mãi: số đợt / số mã có / độ dài trung bình | 1.338 / 121 / 7,9 ngày |
| Phân loại nhu cầu (Syntetos–Boylan) | smooth (đều) 58, erratic (thất thường) 54, lumpy (rời rạc + thất thường) 9 |

Chu kỳ tuần (xuất trung bình theo thứ ÷ trung bình mọi ngày mở cửa):

| Thứ Hai | Thứ Ba | Thứ Tư | Thứ Năm | Thứ Sáu | Thứ Bảy | Chủ nhật |
|---|---|---|---|---|---|---|
| 1,02 | 1,05 | 1,04 | 1,07 | 1,15 | 1,16 | 0,53 |

## 2. Dự báo trên tập kiểm tra (nguồn: `reports/ket_qua_mo_hinh.csv`)

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---|---|---|---|---|---|
| RNN | 0,349 | 0,209 | +7,2% | 0,301 | 0,367 | 0,474 |
| Ghép v4 + LSTM (không đạt luật) | 0,351 | 0,201 | +4,8% | 0,307 | 0,370 | 0,469 |
| Ghép v4 + mô hình mới | 0,354 | 0,205 | +5,0% | 0,308 | 0,370 | 0,477 |
| LSTM | 0,355 | 0,210 | +5,2% | 0,314 | 0,383 | 0,459 |
| Kết hợp v4, cập nhật tuần (đang dùng) | 0,356 | 0,203 | +3,0% | 0,310 | 0,378 | 0,477 |
| Kết hợp v3, cập nhật 28 ngày | 0,368 | 0,226 | +3,9% | 0,319 | 0,392 | 0,496 |
| LightGBM theo tầm | 0,375 | 0,242 | +6,7% | 0,320 | 0,392 | 0,523 |
| Kết hợp theo nhóm v2 | 0,375 | 0,234 | +6,3% | 0,311 | 0,391 | 0,546 |
| LightGBM | 0,399 | 0,269 | +11,7% | 0,312 | 0,391 | 0,638 |
| TFT gọn | 0,425 | 0,302 | +17,1% | 0,322 | 0,409 | 0,710 |
| N-HiTS | 0,429 | 0,321 | +11,4% | 0,367 | 0,420 | 0,601 |
| Prophet | 0,454 | 0,257 | −4,9% | 0,383 | 0,486 | 0,638 |
| TiDE | 0,477 | 0,357 | +17,8% | 0,373 | 0,446 | 0,767 |
| TB trượt 28 ngày, cập nhật tuần | 0,584 | 0,443 | −0,2% | 0,391 | 0,558 | 1,116 |
| TB trượt 28 ngày | 0,640 | 0,511 | −0,8% | 0,408 | 0,653 | 1,272 |
| Croston SBA | 0,651 | 0,516 | +0,4% | 0,395 | 0,589 | 1,365 |
| TSB | 0,686 | 0,549 | −6,5% | 0,410 | 0,555 | 1,477 |
| ETS | 0,721 | 0,614 | −16,7% | 0,428 | 0,527 | 1,574 |
| Naive | 0,739 | 0,634 | −9,1% | 0,491 | 0,639 | 1,442 |
| Seasonal Naive | 0,773 | 0,598 | −11,0% | 0,475 | 0,597 | 1,636 |

## 3. Dự báo trên validation2 (dùng để chọn mô hình)

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---|---|---|---|---|---|
| Ghép v4 + LSTM (không đạt luật) | 0,351 | 0,208 | +7,7% | 0,299 | 0,352 | 0,503 |
| Ghép v4 + mô hình mới | 0,352 | 0,207 | +7,3% | 0,299 | 0,354 | 0,505 |
| Kết hợp v4, cập nhật tuần (đang dùng) | 0,358 | 0,213 | +5,5% | 0,307 | 0,359 | 0,505 |
| Kết hợp v3, cập nhật 28 ngày | 0,379 | 0,243 | +7,1% | 0,312 | 0,392 | 0,573 |
| LSTM | 0,384 | 0,239 | +7,5% | 0,305 | 0,370 | 0,620 |
| LightGBM theo tầm | 0,385 | 0,251 | +10,2% | 0,312 | 0,392 | 0,597 |
| Kết hợp theo nhóm v2 | 0,388 | 0,252 | +7,9% | 0,313 | 0,388 | 0,607 |
| RNN | 0,395 | 0,253 | +5,6% | 0,307 | 0,373 | 0,657 |
| TFT gọn | 0,412 | 0,289 | +16,9% | 0,309 | 0,391 | 0,716 |
| TiDE | 0,465 | 0,344 | +18,7% | 0,373 | 0,416 | 0,744 |
| N-HiTS | 0,478 | 0,376 | +0,5% | 0,433 | 0,461 | 0,615 |
| Prophet additive | 0,488 | 0,304 | −1,4% | 0,399 | 0,567 | 0,727 |
| TB trượt 28 ngày, cập nhật tuần | 0,566 | 0,425 | −1,1% | 0,383 | 0,498 | 1,120 |
| TB trượt 28 ngày | 0,631 | 0,499 | −5,0% | 0,397 | 0,563 | 1,332 |

## 4. Sàn sai số và khoảng dự báo (nguồn: `reports/nang_cap_du_bao_v4_trang_thai.json`)

Sàn sai số theo ngày: 0,286 (X 0,268, Y 0,310, Z 0,341).

| Mức | Theo ngày: đúng | Tổng lead time: đúng |
|---|---|---|
| 80% | 80,9% | 81,3% |
| 95% | 96,0% | 95,5% |

Sai số trên tổng lead time (test): 0,214.

## 5. Bảng rủi ro (nguồn: `reports/rui_ro_du_bao.md`)


Dữ liệu 2023-10-01 – 2025-09-30 (2.0 năm; KHÔNG dùng giai đoạn test). Dữ liệu mô phỏng.
Tác động = số bán trung bình trong đợt / mức nền (TB 28 ngày trước đợt, cùng mã); 1,00 = không đổi; chỉ tính mã có mức nền ≥ 1 đơn vị/ngày; nhóm hàng cần ≥ 3 đợt-mã. Đơn B2B tính trên số xuất thực (kể cả đơn lớn). Khuyến mãi: số đợt trên mỗi mã mỗi năm; đơn B2B: số đơn của cả kho mỗi năm.
Rủi ro không biết trước (bão, thời tiết, dịch, tin đồn): BỎ các ngày trùng cửa sổ Tết / Trung thu / Noel / Halloween khi tính tác động, vì không tách được (VD bão Yagi 04–17/09/2024 nằm trọn trong mùa Trung thu: đồ chơi tăng do Trung thu, không do bão). Cột % ngày trùng cho biết bao nhiêu phần bị bỏ.

| Rủi ro                                  | Nhận diện                                      |   Đợt / năm |   Ngày / đợt |   % ngày trùng Tết/Trung thu/Noel/Halloween |   Số mã |   Tác động (trung vị) |    p10 |    p90 | Nhóm chịu tác động mạnh nhất               | Biết trước                     | Hệ thống xử lý                                          |
|:----------------------------------------|:-----------------------------------------------|------------:|-------------:|--------------------------------------------:|--------:|----------------------:|-------:|-------:|:-------------------------------------------|:-------------------------------|:--------------------------------------------------------|
| Bão lũ                                  | cửa sổ 3 ngày trước – 10 ngày sau ngày bão vào |         2   |         14   |                                          45 |     117 |                  1.08 |   0.74 |   1.84 | Thực phẩm khô ×1.45, Y tế & sức khỏe ×1.35 | 3–5 ngày (bản tin bão)         | B2: cảnh báo bão ngắn hạn; tồn kho an toàn              |
| Nắng nóng                               | cờ sự kiện của mã                              |         1.5 |          9.7 |                                           0 |     118 |                  1.09 |   0.79 |   1.98 | Kem & đông lạnh ×2.71, Đồ uống ×1.56       | 7–10 ngày (dự báo thời tiết)   | tồn kho an toàn; theo dõi                               |
| Rét đậm                                 | cờ sự kiện của mã                              |         1.5 |        nan   |                                         100 |       0 |                nan    | nan    | nan    | không tách được (trùng sự kiện lớn)        | 7–10 ngày                      | tồn kho an toàn; theo dõi                               |
| Dịch cúm                                | cờ sự kiện của mã                              |         1   |          8.7 |                                          69 |     118 |                  0.97 |   0.56 |   1.43 | Y tế & sức khỏe ×1.40, Phụ kiện ×1.14      | vài ngày (tin y tế)            | tồn kho an toàn                                         |
| Sốt xuất huyết                          | cờ sự kiện của mã                              |         1   |         27   |                                          37 |     118 |                  0.94 |   0.55 |   1.3  | Văn phòng phẩm ×1.03, Hóa phẩm ×1.01       | vài ngày                       | tồn kho an toàn                                         |
| Tin đồn tăng giá                        | cờ sự kiện của mã                              |         1   |          7   |                                           0 |     118 |                  0.97 |   0.6  |   1.56 | Phụ kiện ×1.27, Thực phẩm khô ×1.10        | không biết trước               | tồn kho an toàn; khoảng dự báo                          |
| Giải thể thao lớn                       | cờ sự kiện của mã                              |         1   |         30   |                                         nan |     117 |                  1.06 |   0.81 |   2.18 | Phụ kiện ×1.75, Mỹ phẩm ×1.39              | hàng tháng (lịch thi đấu)      | đặc trưng biết trước của mô hình                        |
| Tết Nguyên đán                          | cờ sự kiện của mã                              |         1   |         36   |                                         nan |     119 |                  1.06 |   0.77 |   1.6  | Quà tặng ×1.53, Gia vị ×1.18               | cả năm (âm lịch)               | đặc trưng biết trước + âm lịch (vòng 3)                 |
| Khuyến mãi của mã                       | lịch khuyến mãi                                |         3.8 |          7.9 |                                         nan |     120 |                  1.5  |   0.91 |   2.35 | Phụ kiện ×1.70, Sữa ×1.64                  | theo lịch bộ phận bán hàng gửi | đặc trưng biết trước                                    |
| Đơn B2B đột biến                        | đơn lớn 1–2 ngày                               |        17   |          1.5 |                                         nan |      23 |                  6.23 |   2.63 |  10.61 | Sữa ×10.52, Thực phẩm khô ×9.19            | không biết trước               | không chấm vào dự báo; xử lý bằng đơn riêng             |
| Đứt gãy cung ứng (nhà cung cấp chậm)    | bảng sự kiện đột biến                          |         1   |         15   |                                         nan |      18 |                nan    | nan    | nan    | lead time +9–10 ngày                       | vài ngày (nhà cung cấp báo)    | thử độ nhạy lead time; cập nhật lead time vào công thức |
| Hết hàng (số bán thấp hơn nhu cầu thật) | cột hết hàng                                   |       nan   |        nan   |                                         nan |     114 |                nan    | nan    | nan    | 3.0% ngày-mã; X 3.4%, Y 3.8%, Z 1.9%       | —                              | bỏ khỏi huấn luyện và chấm điểm (không coi là nhu cầu)  |


## 6. Tồn kho theo chính sách và mức phục vụ (nguồn: CSDL, `v_so_sanh_chinh_sach`)

| Chính sách | Mức phục vụ | Fill Rate | Ngày-mã thiếu | Tồn TB (tr đ) | Số lần nhập | CP đặt + lưu | LN mất | CP liên quan |
|---|---|---|---|---|---|---|---|---|
| cong_thuc_du_bao_ai | 90% | 94,13% | 1.027 | 8.222,9 | 3.437 | 2.225,2 | 3.785,8 | 6.011,0 |
| cong_thuc_du_bao_ai_hc | 90% | 95,09% | 964 | 10.606,2 | 3.171 | 2.654,3 | 3.339,9 | 5.994,2 |
| cong_thuc_du_bao_moc | 90% | 90,24% | 1.141 | 17.850,1 | 3.545 | 4.196,7 | 5.162,5 | 9.359,2 |
| hien_trang | 90% | 93,57% | 1.564 | 11.993,6 | 1.910 | 2.766,8 | 3.693,3 | 6.460,1 |
| cong_thuc_du_bao_ai | 95% | 95,33% | 793 | 9.208,7 | 3.467 | 2.427,4 | 2.902,2 | 5.329,6 |
| cong_thuc_du_bao_ai_hc | 95% | 95,82% | 735 | 11.906,0 | 3.192 | 2.915,7 | 2.912,4 | 5.828,1 |
| cong_thuc_du_bao_moc | 95% | 91,69% | 916 | 19.669,7 | 3.575 | 4.567,0 | 4.444,0 | 9.011,0 |
| hien_trang | 95% | 93,57% | 1.564 | 11.993,6 | 1.910 | 2.766,8 | 3.693,3 | 6.460,1 |
| cong_thuc_du_bao_ai | 99% | 96,30% | 536 | 11.206,3 | 3.530 | 2.840,3 | 2.184,4 | 5.024,7 |
| cong_thuc_du_bao_ai_hc | 99% | 97,12% | 500 | 14.312,7 | 3.249 | 3.409,7 | 1.966,5 | 5.376,2 |
| cong_thuc_du_bao_moc | 99% | 93,90% | 607 | 23.089,0 | 3.645 | 5.270,7 | 3.207,0 | 8.477,7 |
| hien_trang | 99% | 93,57% | 1.564 | 11.993,6 | 1.910 | 2.766,8 | 3.693,3 | 6.460,1 |

Theo nhóm XYZ, mức phục vụ 95%:

| Nhóm | Chính sách | Fill Rate | Tồn TB (tr đ) | LN mất (tr đ) |
|---|---|---|---|---|
| X | cong_thuc_du_bao_ai | 95,6% | 3.581,6 | 2.287,3 |
| X | cong_thuc_du_bao_ai_hc | 95,6% | 3.663,3 | 2.381,8 |
| X | cong_thuc_du_bao_moc | 95,6% | 4.151,9 | 2.509,9 |
| X | hien_trang | 93,8% | 5.180,2 | 2.749,6 |
| Y | cong_thuc_du_bao_ai | 98,4% | 488,9 | 134,1 |
| Y | cong_thuc_du_bao_ai_hc | 97,6% | 512,4 | 140,4 |
| Y | cong_thuc_du_bao_moc | 96,9% | 679,6 | 132,8 |
| Y | hien_trang | 97,9% | 473,0 | 138,6 |
| Z | cong_thuc_du_bao_ai | 93,9% | 5.138,3 | 480,8 |
| Z | cong_thuc_du_bao_ai_hc | 96,1% | 7.730,3 | 390,3 |
| Z | cong_thuc_du_bao_moc | 79,8% | 14.838,2 | 1.801,4 |
| Z | hien_trang | 91,9% | 6.340,5 | 805,0 |

## 7. Thử độ nhạy (nguồn: CSDL, `v_do_nhay`; chi tiết `reports/do_nhay.md`)

| Kịch bản (AI + hiệu chỉnh) | Fill Rate | CP liên quan (tr đ) |
|---|---|---|
| Gốc | 95,82% | 5.828,1 |
| Tắc cảng +3 ngày (TB 13 đợt) | 95,33% | 6.168,8 |
| Tắc cảng +5 ngày (TB 13 đợt) | 94,84% | 6.510,2 |
| Tắc cảng +7 ngày (TB 13 đợt) | 94,30% | 6.859,2 |
| chi_phi_dat_120 | 95,92% | 5.821,2 |
| chi_phi_luu_115 | 95,91% | 6.076,2 |
| lead_time_2 | 90,76% | 9.250,4 |
| lead_time_2_cap_nhat | 95,39% | 6.044,2 |

## 8. Logistics bổ sung

### 8.1. Chỉ số kho (nguồn: `reports/chi_so_kho.md`)


Mô phỏng 364 ngày của tập kiểm tra, mức phục vụ 95%. Dữ liệu mô phỏng, không phải số liệu kho thật.

Tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng để ra quyết định); bỏ 28 ngày cuối kỳ.

## Theo chính sách

| ma_chinh_sach          |   vong_quay_lan_nam |   so_ngay_ton |   ton_tb_trieu |   ton_du_tb_trieu |   ti_le_du_pt |
|:-----------------------|--------------------:|--------------:|---------------:|------------------:|--------------:|
| cong_thuc_du_bao_ai    |                31.3 |          11.7 |         9208.7 |            4096.9 |          44.6 |
| cong_thuc_du_bao_ai_hc |                24.2 |          15.1 |        11906   |            6367.8 |          54.2 |
| cong_thuc_du_bao_moc   |                14.2 |          25.7 |        19669.7 |           13629.4 |          69.6 |
| hien_trang             |                23.8 |          15.4 |        11993.6 |            5175.3 |          43.2 |

## Số ngày tồn kho theo nhóm XYZ

| ma_chinh_sach          |   X |    Y |     Z |
|:-----------------------|----:|-----:|------:|
| cong_thuc_du_bao_ai    | 5.7 | 10.9 |  45.2 |
| cong_thuc_du_bao_ai_hc | 5.8 | 11.5 |  67.1 |
| cong_thuc_du_bao_moc   | 6.6 | 15.2 | 155.4 |
| hien_trang             | 8.3 | 10.6 |  57.9 |

## 10 mã tồn dư lớn nhất (AI + hiệu chỉnh)

| ma_sku   | ten                             | xyz   |   du_trieu |
|:---------|:--------------------------------|:------|-----------:|
| SKU089   | Cây thông Noel 1m2              | Z     |     1038.1 |
| SKU059   | Hộp quà Tết cao cấp             | Z     |     1023.4 |
| SKU058   | Mứt Tết hộp 500g                | Z     |      563.7 |
| SKU060   | Hạt điều rang muối hộp 500g     | Z     |      483.6 |
| SKU068   | Bánh trung thu lẻ nhân thập cẩm | Z     |      377.4 |
| SKU061   | Rượu vang Đà Lạt chai           | Z     |      364.6 |
| SKU088   | Kẹo Halloween túi 300g          | Z     |      302.6 |
| SKU091   | Bánh quy bơ hộp Noel            | Z     |      298.7 |
| SKU063   | Hoa mai/đào giả trang trí       | Z     |      222.1 |
| SKU082   | Cặp sách học sinh               | Z     |      217.3 |

### 8.2. Gom đơn (nguồn: `reports/gom_don.md`)


Luật ghi trước: docs/10 mục 10.6. Chính sách AI + hiệu chỉnh, mức phục vụ 95%, quy tắc lượng đặt lai. Dữ liệu mô phỏng; tỉ lệ chi phí chung của phiếu là **giả định**. Chi phí đặt ở đây tính theo dòng đặt nên hơi khác `ket_qua_ton_kho` (tính theo số ngày nhận hàng).

## Validation2: chọn k (tỉ lệ 0,5)

| Phương án | Dòng đặt | Số phiếu | Fill Rate | Tồn TB (tr đ) | CP đặt riêng | CP đặt gom | CP liên quan riêng | CP liên quan gom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Chỉ gom cùng ngày | 3.291 | 2.415 | 96,83% | 10.040,6 | 546,0 | 481,4 | 4.072,9 | 4.008,3 |
| k = 1 | 3.358 | 1.826 | 97,02% | 10.317,8 | 556,8 | 443,2 | 3.998,2 | 3.884,6 |
| k = 2 | 3.420 | 1.507 | 97,34% | 10.546,7 | 567,6 | 423,5 | 4.094,0 | 3.949,9 |
| k = 3 | 3.515 | 1.344 | 97,28% | 10.754,1 | 582,6 | 417,8 | 4.060,8 | 3.896,0 |
| k = 5 | 3.689 | 1.142 | 97,28% | 11.331,2 | 612,6 | 417,0 | 4.242,7 | 4.047,2 |

Theo luật: **đặt kèm k = 1**.

## Test (chỉ báo cáo)

| Phương án | Dòng đặt | Số phiếu | Fill Rate | Tồn TB (tr đ) | CP đặt riêng | CP đặt gom | CP liên quan riêng | CP liên quan gom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Chỉ gom cùng ngày, tỉ lệ 0,3 | 3.285 | 2.404 | 95,82% | 11.906,0 | 544,5 | 505,8 | 5.842,8 | 5.804,1 |
| Chỉ gom cùng ngày, tỉ lệ 0,5 | 3.285 | 2.404 | 95,82% | 11.906,0 | 544,5 | 480,0 | 5.842,8 | 5.778,3 |
| Chỉ gom cùng ngày, tỉ lệ 0,7 | 3.285 | 2.404 | 95,82% | 11.906,0 | 544,5 | 454,2 | 5.842,8 | 5.752,5 |
| Đặt kèm k = 1, tỉ lệ 0,3 | 3.345 | 1.783 | 96,16% | 12.204,8 | 554,0 | 484,6 | 5.681,8 | 5.612,3 |
| Đặt kèm k = 1, tỉ lệ 0,5 | 3.345 | 1.783 | 96,16% | 12.204,8 | 554,0 | 438,2 | 5.681,8 | 5.566,0 |
| Đặt kèm k = 1, tỉ lệ 0,7 | 3.345 | 1.783 | 96,16% | 12.204,8 | 554,0 | 391,9 | 5.681,8 | 5.519,7 |

## Lợi ích đến từ đâu (test, tỉ lệ 0,5)

- Mức 1, chỉ gom cùng ngày: giảm **64,5 triệu đ** chi phí liên quan, không đổi tồn kho, không đổi Fill Rate.
- Mức 2 so với mức 1: giảm **212,3 triệu đ**, gồm đặt hàng 41,8, lưu kho -62,9, lợi nhuận mất 233,4.
- Đặt kèm làm hàng được đặt sớm hơn, nên có tác dụng như **tăng thêm dự phòng**; phần giảm lợi nhuận mất đến từ đó, không phải từ việc chia sẻ chi phí phiếu.

### 8.3. Chấm điểm nhà cung cấp (nguồn: `reports/cham_diem_ncc.md`)


Luật ghi trước: docs/10 mục 10.7. Dữ liệu mô phỏng: lead time được sinh theo quy tắc, nên bảng này **minh họa phương pháp**, không đánh giá một nhà cung cấp thật. Mô phỏng luôn giao đủ hàng nên chỉ đo đúng hạn, chưa đo đủ hàng (OTIF).

## Test: 3285 đơn, đúng hạn 77,6%

| Nhà cung cấp | Số đơn | Đúng hạn | Trễ TB (ngày) | Trễ lớn nhất | Trễ ≥ 3 ngày | Lệch chuẩn | Điểm | Xếp loại |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| NCC09 | 368 | 82,9% | 0,69 | 4 | 8,7% | 1,64 | 76,6 | Trung bình |
| NCC14 | 224 | 81,7% | 0,73 | 6 | 7,1% | 1,64 | 75,9 | Trung bình |
| NCC02 | 362 | 82,9% | 0,67 | 7 | 7,7% | 1,74 | 75,8 | Trung bình |
| NCC12 | 129 | 78,3% | 0,79 | 4 | 10,1% | 1,53 | 74,8 | Trung bình |
| NCC10 | 175 | 81,7% | 0,71 | 6 | 5,7% | 1,89 | 73,9 | Trung bình |
| NCC01 | 324 | 78,4% | 0,81 | 7 | 10,2% | 1,86 | 72,2 | Trung bình |
| NCC03 | 280 | 77,5% | 0,78 | 6 | 9,3% | 1,80 | 72,1 | Trung bình |
| NCC13 | 243 | 77,0% | 0,93 | 8 | 12,3% | 1,93 | 70,7 | Trung bình |
| NCC05 | 172 | 76,7% | 0,87 | 7 | 11,0% | 1,94 | 70,5 | Trung bình |
| NCC11 | 224 | 78,1% | 1,13 | 11 | 12,9% | 2,52 | 66,7 | Cần theo dõi |
| NCC08 | 189 | 72,5% | 0,98 | 8 | 15,3% | 2,24 | 65,6 | Cần theo dõi |
| NCC07 | 169 | 72,8% | 1,05 | 8 | 16,6% | 2,31 | 65,2 | Cần theo dõi |
| NCC06 | 208 | 66,8% | 1,09 | 7 | 14,9% | 1,92 | 64,7 | Cần theo dõi |
| NCC04 | 218 | 70,2% | 1,17 | 8 | 18,8% | 2,26 | 64,1 | Cần theo dõi |

Thứ hạng khi đổi trọng số đúng hạn từ 0,6 sang 0,8: tương quan hạng 0,99.

## Cảnh báo giao chậm

| Tập | Đợt giao chậm thật | Phát hiện | Ngày chờ từ đầu đợt | Ngày có cảnh báo | Báo nhầm |
|---|---:|---:|---|---:|---:|
| validation2 | 1 | 1 | [21] | 49 | 6 |
| test | 1 | 1 | [18] | 121 | 0 |

### 8.4. Trữ hàng cho phiên livestream (nguồn: `reports/tru_hang_live.md`; dữ liệu không có phiên live thật, phần lớn tham số là giả định)


**Bản gốc, trước khi đối chiếu số thật. Bảng theo mức giảm ở cuối giữ nguyên nhu cầu nên có thể gây hiểu sai; xem đính chính ở docs/10 mục 10.9 và bản sau đối chiếu `reports/tru_hang_live_sau_doi_chieu.md`.** Luật ghi trước: docs/10 mục 10.8. **Không có dữ liệu livestream thật**: mọi tham số trừ mức nền và hệ số deal là giả định. Mỗi mã 1 phiên, 118/121 mã có mức nền > 0.

Giả định mặc định: phiên 24 giờ, p = 20%, bùng nổ [3; 10] lần, giảm 15%, nhãn hàng tài trợ 70%, phí sàn 8%, hủy 15%. Lãi 1 đơn vị (trung vị) 5,7% giá bán; 9 mã bán lỗ theo giả định này.

## Phần đo được: hệ số deal

Đo trước test: 2.170 ngày khuyến mãi ngoài sự kiện, trung vị ×1,47, p10–p90 ×0,57–×3,00.

Kiểm tra trên 1.008 ngày khuyến mãi của test: phân vị 50% phủ 47,5%, phân vị 75% phủ 76,2%, phân vị 90% phủ 92,0%. Theo luật (lệch ≤ 5 điểm): **đạt**. Phép kiểm này không nói gì về bùng nổ, và dữ liệu là mô phỏng nên cùng một quy luật sinh ra cả hai giai đoạn.

## So sánh trên chính phân phối giả định (không phải bằng chứng)

Newsvendor tối ưu theo phân phối này nên thắng là tất yếu; bảng chỉ cho thấy độ lớn. Tổng toàn kho, mỗi mã 1 phiên.

### Hàng thừa: Về kho thường

| Phương án | Vốn trữ (tr đ) | Lãi kỳ vọng (tr đ) | Mất bán (tr đ) | Thừa (tr đ) | Bổ sung (tr đ) | Hết hàng (% phiên) |
|---|---:|---:|---:|---:|---:|---:|
| Theo ngày thường | 624,4 | 30,8 | 1.469,4 | 77,4 | 0,0 | 66,3% |
| Theo trung bình | 1.750,7 | 45,9 | 929,1 | 751,0 | 0,0 | 22,9% |
| Newsvendor | 1.890,6 | 52,1 | 1.006,7 | 970,0 | 0,0 | 25,7% |
| Hai bước lần 1, giữ Q | 1.890,6 | 47,4 | 711,1 | 1.018,3 | 299,5 | 15,8% |
| Hai bước lần 1, chọn lại Q | 1.622,5 | 50,7 | 1.019,3 | 880,5 | 162,3 | 28,5% |
| Hai bước lần 2, giữ Q | 1.890,6 | 51,9 | 905,6 | 1.033,5 | 145,1 | 23,0% |
| Hai bước lần 2, chọn lại Q | 1.858,0 | 51,7 | 910,8 | 1.008,0 | 148,1 | 22,8% |

Trần tham chiếu, nếu biết trước nhu cầu từng phiên: **104,6 triệu đ**. Tỉ lệ hết hàng tính trên 109 mã còn lãi; mã bán lỗ thì newsvendor không trữ.

### Hàng thừa: Trả nhà cung cấp

| Phương án | Vốn trữ (tr đ) | Lãi kỳ vọng (tr đ) | Mất bán (tr đ) | Thừa (tr đ) | Bổ sung (tr đ) | Hết hàng (% phiên) |
|---|---:|---:|---:|---:|---:|---:|
| Theo ngày thường | 624,4 | 24,4 | 1.469,4 | 77,4 | 0,0 | 66,3% |
| Theo trung bình | 1.750,7 | -16,4 | 929,1 | 751,0 | 0,0 | 22,9% |
| Newsvendor | 644,9 | 29,2 | 1.481,5 | 117,3 | 0,0 | 59,7% |
| Hai bước lần 1, giữ Q | 644,9 | 14,9 | 952,8 | 222,6 | 550,3 | 31,1% |
| Hai bước lần 1, chọn lại Q | 413,4 | 28,1 | 1.506,5 | 139,5 | 219,4 | 57,1% |
| Hai bước lần 2, giữ Q | 644,9 | 32,7 | 1.266,6 | 155,3 | 210,7 | 44,6% |
| Hai bước lần 2, chọn lại Q | 624,2 | 32,9 | 1.271,1 | 145,4 | 217,9 | 44,5% |

Trần tham chiếu, nếu biết trước nhu cầu từng phiên: **104,6 triệu đ**. Tỉ lệ hết hàng tính trên 109 mã còn lãi; mã bán lỗ thì newsvendor không trữ.

### Hàng thừa: Phải xả

| Phương án | Vốn trữ (tr đ) | Lãi kỳ vọng (tr đ) | Mất bán (tr đ) | Thừa (tr đ) | Bổ sung (tr đ) | Hết hàng (% phiên) |
|---|---:|---:|---:|---:|---:|---:|
| Theo ngày thường | 624,4 | 1,1 | 1.469,4 | 77,4 | 0,0 | 66,3% |
| Theo trung bình | 1.750,7 | -241,7 | 929,1 | 751,0 | 0,0 | 22,9% |
| Newsvendor | 306,4 | 14,5 | 1.777,4 | 24,8 | 0,0 | 83,1% |
| Hai bước lần 1, giữ Q | 306,4 | -23,4 | 1.129,7 | 123,9 | 639,8 | 54,3% |
| Hai bước lần 1, chọn lại Q | 69,3 | 9,0 | 1.813,7 | 27,1 | 201,7 | 91,2% |
| Hai bước lần 2, giữ Q | 306,4 | 17,4 | 1.478,1 | 47,8 | 263,2 | 67,8% |
| Hai bước lần 2, chọn lại Q | 244,5 | 18,5 | 1.519,1 | 34,6 | 278,9 | 79,1% |

Trần tham chiếu, nếu biết trước nhu cầu từng phiên: **104,6 triệu đ**. Tỉ lệ hết hàng tính trên 109 mã còn lãi; mã bán lỗ thì newsvendor không trữ.

## Bằng chứng 1: thực tế khác giả định

Q tính với p = 20%, bùng nổ [3; 10]. Bảng ghi lãi kỳ vọng (triệu đ) khi thực tế khác đi. **Chênh** = newsvendor − phương án tốt hơn trong 2 phương án so sánh.

### Hàng thừa: Về kho thường

| Thực tế | Theo ngày thường | Theo trung bình | Newsvendor | Chênh |
|---|---:|---:|---:|---:|
| p = 5% | 30,2 | 36,3 | 35,5 | -0,9 |
| p = 10% | 30,5 | 39,9 | 41,7 | 1,8 |
| p = 20% (như giả định) | 31,0 | 46,0 | 52,1 | 6,1 |
| p = 40% | 31,9 | 59,2 | 75,5 | 16,4 |
| bùng nổ [2; 5] | 31,0 | 44,0 | 45,6 | 1,6 |
| bùng nổ [5; 20] | 31,0 | 46,6 | 55,7 | 9,1 |

Theo luật: **không bền, thua khi p = 5%**.

### Hàng thừa: Trả nhà cung cấp

| Thực tế | Theo ngày thường | Theo trung bình | Newsvendor | Chênh |
|---|---:|---:|---:|---:|
| p = 5% | 23,2 | -40,4 | 25,8 | 2,6 |
| p = 10% | 23,9 | -32,9 | 27,3 | 3,4 |
| p = 20% (như giả định) | 24,9 | -20,1 | 29,7 | 4,8 |
| p = 40% | 26,8 | 7,4 | 34,4 | 7,7 |
| bùng nổ [2; 5] | 24,8 | -24,4 | 29,3 | 4,5 |
| bùng nổ [5; 20] | 24,9 | -18,9 | 29,7 | 4,8 |

Theo luật: **bền**.

### Hàng thừa: Phải xả

| Thực tế | Theo ngày thường | Theo trung bình | Newsvendor | Chênh |
|---|---:|---:|---:|---:|
| p = 5% | -2,2 | -318,2 | 13,7 | 15,9 |
| p = 10% | -0,2 | -296,4 | 14,3 | 14,6 |
| p = 20% (như giả định) | 2,7 | -259,5 | 15,1 | 12,5 |
| p = 40% | 8,1 | -180,0 | 16,6 | 8,5 |
| bùng nổ [2; 5] | 2,4 | -271,9 | 15,1 | 12,7 |
| bùng nổ [5; 20] | 2,7 | -256,0 | 15,2 | 12,5 |

Theo luật: **bền**.

## Giá trị theo dõi theo giờ

= lãi hai bước (chọn lại Q) − lãi newsvendor, tổng toàn kho, triệu đ. Là mức chi tối đa cho việc theo dõi, chưa trừ chi phí cài đặt. Lần 1 là quy tắc ghi trước; lần 2 sửa sau khi đã thấy lần 1 (docs/10 mục 10.8).

| Hàng về sau | Về kho thường: lần 1 | Về kho thường: lần 2 | Trả nhà cung cấp: lần 1 | Trả nhà cung cấp: lần 2 | Phải xả: lần 1 | Phải xả: lần 2 |
|---|---:|---:|---:|---:|---:|---:|
| 2 giờ | -0,7 | -0,7 | 0,3 | 5,8 | -6,2 | 7,1 |
| 6 giờ | -1,6 | -0,9 | -1,3 | 3,5 | -6,1 | 3,4 |
| 12 giờ | -2,0 | -0,9 | -2,2 | 1,3 | -3,8 | 2,4 |
| 24 giờ | -0,3 | -0,3 | -0,1 | -0,1 | -0,2 | -0,2 |

### Theo phụ phí nguồn nhanh (hàng về sau 6 giờ)

| Phụ phí | Về kho thường: lần 1 | Về kho thường: lần 2 | Trả nhà cung cấp: lần 1 | Trả nhà cung cấp: lần 2 | Phải xả: lần 1 | Phải xả: lần 2 |
|---|---:|---:|---:|---:|---:|---:|
| 0% giá vốn | 11,4 | 7,2 | 16,5 | 17,8 | 7,8 | 18,3 |
| 2% giá vốn | 5,2 | 0,4 | 6,0 | 8,9 | 1,6 | 10,0 |
| 5% giá vốn | -1,6 | -0,9 | -1,3 | 3,5 | -6,1 | 3,4 |

## Mức giảm giá và tài trợ (hàng thừa về kho thường)

| Giảm · tài trợ | Vốn trữ newsvendor (tr đ) | Lãi newsvendor (tr đ) | Lãi theo ngày thường (tr đ) |
|---|---:|---:|---:|
| 10% · tài trợ 70% | 2.295,7 | 65,1 | 38,3 |
| 15% · tài trợ 70% | 1.950,8 | 52,1 | 31,0 |
| 30% · tài trợ 70% | 973,3 | 25,0 | 9,4 |
| 15% · tài trợ 0% | 26,8 | 0,1 | -37,9 |
| 15% · tài trợ 100% | 3.261,3 | 111,0 | 60,6 |

### 8.5. Đối chiếu giả định với dữ liệu thật Dominick's (nguồn: `reports/dominicks.md`; siêu thị Mỹ 1989–1997)


Luật ghi trước: docs/10 mục 10.9. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business. Chuỗi siêu thị Mỹ, 09/1989–05/1997, số bán theo tuần; 27 ngành, 16.995 mã, 1.997.279 dòng mã-tuần sau khi gộp toàn chuỗi. Không phải Việt Nam, không phải livestream.

## 1. Hệ số deal

| | Số tuần | Trung bình | p10 | p50 | p90 | Từ ×3 | Từ ×5 | Từ ×10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dominick's (thật, theo tuần) | 225.883 | 3,28 | 0,94 | 1,63 | 5,71 | 23,1% | 11,9% | 4,7% |
| Mô phỏng (theo ngày) | 2.170 | 1,67 | 0,57 | 1,47 | 3,00 | 10,1% | 1,4% | 0,0% |

Theo luật (trung vị lệch quá 25%): **không lệch**. Luật chỉ so trung vị, nhưng lượng trữ phụ thuộc đuôi trên: p90 thật ×5,71 so với ×3,00 của mô phỏng, tuần đạt từ ×5 là 11,9% so với 1,4%, nên **đuôi trên của mô phỏng quá mỏng**, dù số thật theo tuần vốn đã ít dao động hơn theo ngày. Vài ngành kéo đuôi lên rõ (bảng dưới).

| Ngành | Số tuần | p10 | p50 | p90 | Từ ×3 |
|---|---:|---:|---:|---:|---:|
| che | 14.118 | 0,90 | 1,30 | 3,25 | 11,6% |
| fec | 6.025 | 0,91 | 1,33 | 2,72 | 8,2% |
| cra | 6.212 | 0,96 | 1,33 | 2,98 | 9,9% |
| soa | 3.611 | 0,88 | 1,34 | 2,59 | 7,5% |
| bjc | 9.676 | 0,93 | 1,38 | 3,57 | 14,0% |
| sna | 8.518 | 0,96 | 1,38 | 3,03 | 10,2% |
| tna | 5.096 | 0,95 | 1,38 | 3,10 | 10,4% |
| cso | 8.140 | 0,88 | 1,39 | 3,26 | 11,8% |
| oat | 1.199 | 0,87 | 1,39 | 5,14 | 18,8% |
| bat | 907 | 0,91 | 1,40 | 2,45 | 4,9% |
| ana | 4.719 | 0,93 | 1,46 | 3,51 | 13,6% |
| cer | 4.908 | 0,91 | 1,50 | 8,01 | 24,9% |
| fsf | 3.840 | 0,81 | 1,51 | 4,72 | 19,2% |
| ptw | 2.104 | 0,92 | 1,55 | 5,54 | 23,5% |
| coo | 16.016 | 0,99 | 1,55 | 4,13 | 16,7% |
| frj | 6.071 | 0,96 | 1,58 | 5,96 | 22,0% |
| gro | 12.468 | 0,90 | 1,59 | 3,83 | 16,5% |
| frd | 4.877 | 0,90 | 1,60 | 5,30 | 25,7% |
| sha | 14.988 | 0,91 | 1,64 | 4,41 | 19,3% |
| lnd | 6.277 | 0,78 | 1,64 | 8,43 | 27,1% |
| tbr | 5.702 | 0,95 | 1,65 | 3,36 | 13,5% |
| did | 3.810 | 0,83 | 1,68 | 5,77 | 24,3% |
| tti | 2.523 | 0,92 | 1,74 | 10,19 | 31,5% |
| tpa | 7.893 | 0,95 | 1,86 | 5,27 | 25,1% |
| fre | 18.941 | 0,98 | 2,16 | 9,97 | 38,6% |
| sdr | 38.135 | 1,03 | 2,34 | 10,91 | 39,9% |
| ber | 9.109 | 1,18 | 2,44 | 4,84 | 34,2% |

## 2. Phép đo có dùng được cho thời kỳ sau không

Đo trên 2/3 đầu (144.593 tuần), kiểm trên 1/3 sau (81.290 tuần): phân vị 50% phủ 44,3%, phân vị 75% phủ 70,8%, phân vị 90% phủ 87,0%. Theo luật: **không đạt**. Đo riêng từng ngành: 4/27 ngành đạt.

## 3. Nhà sản xuất tài trợ bao nhiêu

Gộp 251.438 tuần giảm ≥ 5%: nhà sản xuất gánh **43,4%** phần giảm. Giả định hiện tại 70%. Theo luật (khoảng 50–90%): **giả định lệch**. Giá vốn là giá bình quân tồn kho nên chỉ là ước lượng.

| Ngành | Tài trợ |
|---|---:|
| tbr | 8,7% |
| ber | 10,6% |
| frj | 10,8% |
| sha | 13,2% |
| fec | 13,6% |
| bat | 14,0% |
| gro | 14,2% |
| che | 17,4% |
| frd | 18,8% |
| ana | 21,7% |
| fre | 23,6% |
| tpa | 23,9% |
| soa | 24,5% |
| tna | 24,7% |
| fsf | 26,9% |
| ptw | 27,8% |
| bjc | 30,5% |
| sna | 33,4% |
| lnd | 36,2% |
| cso | 38,1% |
| coo | 41,0% |
| cra | 42,1% |
| did | 42,1% |
| tti | 43,5% |
| sdr | 58,6% |
| oat | 59,9% |
| cer | 70,6% |

## 4. Biên lãi gộp

Tuần thường 26,0%, tuần khuyến mãi 14,5%. Theo mã (tuần thường): p10 18,1%, trung vị 30,4%, p90 42,7%. Danh mục mô phỏng: 10–23%. 17,9% số mã-tuần là khuyến mãi; trong đó 82,8% có cờ, phần còn lại chỉ nhận ra nhờ giá.

## 5. Giảm sâu hơn thì bán thêm bao nhiêu

| Mức giảm | Số tuần | Trung vị hệ số deal |
|---|---:|---:|
| 5–10% | 52.044 | 1,34 |
| 10–20% | 64.057 | 1,78 |
| 20–30% | 35.575 | 2,41 |
| 30–50% | 25.203 | 4,44 |
| 50–90% | 3.585 | 14,03 |

Độ co giãn theo giá: **3,00** (giá giảm 1% thì số bán tăng khoảng ngần ấy %). Chỉ là tương quan: khuyến mãi thường đi kèm trưng bày, tờ rơi. Mô phỏng hiện chưa có quan hệ này.

## 6. Mua trước rồi giảm

99.799 tuần ngay sau khuyến mãi: trung vị ×1,01 so với mức nền. Theo luật (dưới 0,9): **không rõ hiện tượng**.

## 7. Thử newsvendor bằng hệ số thật

Giá, mức nền, chi phí của các mã trong đồ án giữ nguyên; bùng nổ vẫn là giả định. Chấm trên hệ số thật của 1/3 sau. Lãi kỳ vọng, triệu đ toàn kho.

### Hàng thừa: Về kho thường

| Bùng nổ thực tế | Q theo hệ số | Theo ngày thường | Theo trung bình | Newsvendor | Chênh so với phương án tốt hơn |
|---|---|---:|---:|---:|---:|
| p = 20% | mô phỏng | 34,5 | 59,7 | 74,2 | 14,5 |
| p = 20% | thật, 2/3 đầu | 34,5 | 66,3 | 80,1 | 13,8 |
| p = 0% | mô phỏng | 34,0 | 48,9 | 54,0 | 5,1 |
| p = 0% | thật, 2/3 đầu | 34,0 | 44,2 | 48,5 | 4,3 |

Theo luật: **bền**.

### Hàng thừa: Trả nhà cung cấp

| Bùng nổ thực tế | Q theo hệ số | Theo ngày thường | Theo trung bình | Newsvendor | Chênh so với phương án tốt hơn |
|---|---|---:|---:|---:|---:|
| p = 20% | mô phỏng | 32,2 | 8,5 | 38,7 | 6,5 |
| p = 20% | thật, 2/3 đầu | 32,2 | -47,7 | 39,9 | 7,8 |
| p = 0% | mô phỏng | 31,1 | -14,1 | 35,1 | 4,0 |
| p = 0% | thật, 2/3 đầu | 31,1 | -94,0 | 34,0 | 3,0 |

Theo luật: **bền**.

### Hàng thừa: Phải xả

| Bùng nổ thực tế | Q theo hệ số | Theo ngày thường | Theo trung bình | Newsvendor | Chênh so với phương án tốt hơn |
|---|---|---:|---:|---:|---:|
| p = 20% | mô phỏng | 23,7 | -177,0 | 24,0 | 0,3 |
| p = 20% | thật, 2/3 đầu | 23,7 | -460,3 | 27,2 | 3,5 |
| p = 0% | mô phỏng | 20,5 | -242,1 | 23,2 | 2,7 |
| p = 0% | thật, 2/3 đầu | 20,5 | -594,0 | 25,1 | 4,6 |

Theo luật: **bền**.

## 8. Thử thêm: mức tài trợ thật và độ co giãn (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)

Bảng so sánh mức giảm ở `reports/tru_hang_live.md` giữ nguyên nhu cầu khi đổi mức giảm nên có thể gây hiểu sai. Ở đây số bán đổi theo độ co giãn 3,00, lấy mức giảm 15% làm gốc; độ co giãn này chỉ là tương quan, có thể thổi cao. Hàng thừa về kho thường, lãi newsvendor toàn kho, triệu đ.

| Giảm | Nhãn hàng tài trợ | Số mã còn lãi | Lãi, nhu cầu không đổi | Lãi, có co giãn | Vốn trữ, có co giãn |
|---|---:|---:|---:|---:|---:|
| 10% | 70,0% | 117/118 | 65,1 | 54,9 | 1.937,2 |
| 10% | 43,4% | 94/118 | 36,6 | 30,8 | 1.181,9 |
| 15% | 70,0% | 109/118 | 52,1 | 52,1 | 1.950,8 |
| 15% | 43,4% | 73/118 | 20,9 | 20,9 | 857,8 |
| 30% | 70,0% | 77/118 | 25,0 | 44,8 | 1.737,4 |
| 30% | 43,4% | 3/118 | 0,0 | 0,0 | 2,9 |

### 8.6. Trữ hàng livestream, bản sau đối chiếu (nguồn: `reports/tru_hang_live_sau_doi_chieu.md`)


Luật: docs/10 mục 10.10, viết sau khi đã thấy kết quả 10.8 và 10.9. Hệ số deal theo đúng dải giảm giá, số thật siêu thị Mỹ 1989–1997 theo tuần; tài trợ mặc định 45%. Bùng nổ, phí sàn, hủy đơn vẫn là giả định; biên lãi 121 mã vẫn là mô phỏng. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business.

## 1. Phép đo theo dải có giữ được cho thời kỳ sau không

| Dải giảm | Số tuần | Trung vị | Trung bình | Phủ 50% | Phủ 75% | Phủ 90% | Theo luật | Ngành đạt |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| 5–10% | 52.044 | ×1,34 | ×1,79 | 50,5% | 75,9% | 90,8% | Đạt | 6/27 |
| 10–20% | 64.057 | ×1,78 | ×2,89 | 45,8% | 71,2% | 87,1% | Đạt | 8/27 |
| 20–30% | 35.575 | ×2,41 | ×3,81 | 55,2% | 78,1% | 90,0% | Không đạt | 3/26 |
| 30–50% | 25.203 | ×4,44 | ×7,37 | 52,0% | 75,5% | 90,4% | Đạt | 4/24 |
| 50–90% | 3.585 | ×14,03 | ×19,72 | 60,9% | 75,6% | 85,8% | Không đạt | 2/7 |

So với cách gộp mọi mức giảm ở mục 10.9: không đạt, 4/27 ngành đạt.

## 2. Newsvendor trên số thật

Q tính trên 2/3 đầu của đúng dải, chấm trên 1/3 sau; tài trợ 45%. Lãi kỳ vọng, triệu đ toàn kho. Mức giảm 30% rơi vào dải 30–50% nên hệ số có thể cao hơn thực tế.

| Giảm | Hàng thừa | Bùng nổ thực tế | Mã còn lãi | Theo ngày thường | Theo trung bình | Newsvendor | Vốn trữ newsvendor |
|---:|---|---:|---:|---:|---:|---:|---:|
| 10% | Về kho thường | 20% | 96/118 | 24,9 | 42,1 | 57,4 | 2.220,6 |
| 10% | Về kho thường | 0% | 96/118 | 24,6 | 26,6 | 33,4 | 2.220,6 |
| 10% | Trả nhà cung cấp | 20% | 96/118 | 23,1 | -51,2 | 31,8 | 681,9 |
| 10% | Trả nhà cung cấp | 0% | 96/118 | 22,2 | -88,3 | 27,8 | 681,9 |
| 10% | Phải xả | 20% | 96/118 | 16,5 | -388,8 | 21,7 | 403,0 |
| 10% | Phải xả | 0% | 96/118 | 13,9 | -504,4 | 19,9 | 403,0 |
| 15% | Về kho thường | 20% | 74/118 | 8,0 | 1,1 | 33,0 | 1.387,2 |
| 15% | Về kho thường | 0% | 74/118 | 7,8 | -7,0 | 20,1 | 1.387,2 |
| 15% | Trả nhà cung cấp | 20% | 74/118 | 6,2 | -92,2 | 18,9 | 415,9 |
| 15% | Trả nhà cung cấp | 0% | 74/118 | 5,5 | -121,9 | 16,8 | 415,9 |
| 15% | Phải xả | 20% | 74/118 | -0,4 | -429,8 | 12,9 | 269,6 |
| 15% | Phải xả | 0% | 74/118 | -2,9 | -538,0 | 11,8 | 269,6 |
| 30% | Về kho thường | 20% | 6/118 | -43,3 | -350,1 | 0,1 | 52,3 |
| 30% | Về kho thường | 0% | 6/118 | -43,2 | -305,5 | 0,1 | 52,3 |
| 30% | Trả nhà cung cấp | 20% | 6/118 | -44,1 | -728,1 | 0,1 | 23,3 |
| 30% | Trả nhà cung cấp | 0% | 6/118 | -44,2 | -753,1 | 0,0 | 23,3 |
| 30% | Phải xả | 20% | 6/118 | -47,0 | -2.095,9 | 0,0 | 10,0 |
| 30% | Phải xả | 0% | 6/118 | -47,5 | -2.372,9 | 0,0 | 10,0 |

Theo luật: **bền**.

## 3. Trước và sau đối chiếu, mặc định (giảm 15%)

Trước: hệ số mô phỏng, tài trợ 70%. Sau: hệ số thật dải 10–20%, tài trợ 45%. Cùng phiên giả lập theo giả định, chưa tách 2/3 và 1/3. Lãi kỳ vọng, triệu đ toàn kho.

| Hàng thừa | Vốn trước | Lãi trước | Mã còn lãi trước | Vốn sau | Lãi sau | Mã còn lãi sau | Giá trị theo dõi theo giờ (sau) | Trần nếu biết trước (sau) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Về kho thường | 1.950,8 | 52,1 | 109/118 | 1.412,7 | 31,0 | 74/118 | 0,5 | 75,7 |
| Trả nhà cung cấp | 656,1 | 29,7 | 109/118 | 417,6 | 18,3 | 74/118 | 1,5 | 75,7 |
| Phải xả | 309,2 | 15,1 | 109/118 | 269,6 | 12,7 | 74/118 | 0,6 | 75,7 |

Giá trị theo dõi = lãi hai bước theo quy tắc lần 2 (chọn lại Q) − lãi newsvendor, hàng về sau 6 giờ. Biên lãi mô phỏng thấp hơn số thật nên mức lãi ở đây thiên về bi quan.

### 8.7. Hạn sử dụng và sức chứa (nguồn: `reports/rang_buoc_kho.md`; hạn, thể tích, sức chứa là giả định)


Luật ghi trước: docs/10 mục 10.11. **Hạn sử dụng, thể tích, sức chứa là giả định**, đơn hàng và nhu cầu là mô phỏng. Chính sách AI + hiệu chỉnh, mức phục vụ 95%. Xét riêng từng ràng buộc.

## 1. Hạn sử dụng (50/121 mã)

Số tính trên các mã có hạn.

### Validation2: chọn trần lượng đặt

| Phương án | Fill Rate | Tồn TB (tr đ) | Hàng loại | Giá trị loại (tr đ) | % hàng nhập | Tổng chi phí (tr đ) |
|---|---:|---:|---:|---:|---:|---:|
| Không trần | 96,52% | 3.721,7 | 101.054 | 6.443,6 | 6,32% | 8.464,0 |
| Có trần theo hạn | 96,70% | 3.710,7 | 80.832 | 5.996,6 | 5,11% | 8.089,5 |

Theo luật (chi phí giảm ≥ 0,5%, Fill Rate giảm ≤ 0,2 điểm): **dùng trần**.

### Test (chỉ báo cáo)

| Phương án | Fill Rate | Tồn TB (tr đ) | Hàng loại | Giá trị loại (tr đ) | % hàng nhập | Tổng chi phí (tr đ) |
|---|---:|---:|---:|---:|---:|---:|
| Không xét hạn (như hiện nay, chưa tính hàng loại) | 95,02% | 5.286,7 | 0 | 0,0 | 0,00% | 3.622,6 |
| Có hạn, không trần | 95,08% | 3.955,2 | 108.033 | 6.233,3 | 6,19% | 9.601,9 |
| Có hạn, có trần | 95,17% | 3.997,0 | 91.436 | 5.950,1 | 5,29% | 9.312,7 |
| Có hạn, không trần, xả được 50% | 95,08% | 3.955,2 | 108.033 | 6.233,3 | 6,19% | 6.485,3 |
| Có hạn, có trần, xả được 50% | 95,17% | 3.997,0 | 91.436 | 5.950,1 | 5,29% | 6.337,7 |
| Thời hạn ×0,5, không trần | 94,16% | 3.657,7 | 204.271 | 10.046,7 | 11,33% | 13.549,1 |
| Thời hạn ×0,5, có trần | 94,93% | 3.625,3 | 127.674 | 8.690,7 | 7,29% | 12.061,3 |
| Thời hạn ×2, không trần | 95,36% | 4.457,4 | 64.006 | 4.083,0 | 3,76% | 7.513,2 |
| Thời hạn ×2, có trần | 95,38% | 4.464,4 | 62.730 | 4.044,0 | 3,69% | 7.445,2 |

10 mã loại nhiều nhất chiếm 100% giá trị loại (test, không trần):

| Mã | Tên | Hạn (ngày) | Ngày được giao | MOQ | Nhu cầu/ngày | Loại, không trần (tr đ) | Loại, có trần (tr đ) |
|---|---|---:|---:|---:|---:|---:|---:|
| SKU067 | Bánh trung thu Kinh Đô hộp 4 bánh | 60 | 20.0 | 30 | 80,5 | 1.545,1 | 1.470,9 |
| SKU058 | Mứt Tết hộp 500g | 180 | 60.0 | 40 | 55,3 | 1.260,8 | 1.437,5 |
| SKU068 | Bánh trung thu lẻ nhân thập cẩm | 60 | 20.0 | 95 | 213,3 | 1.049,0 | 1.035,0 |
| SKU060 | Hạt điều rang muối hộp 500g | 270 | 90.0 | 25 | 34,4 | 963,9 | 963,1 |
| SKU091 | Bánh quy bơ hộp Noel | 365 | 122.0 | 15 | 24,5 | 554,6 | 554,8 |
| SKU012 | Sữa chua Vinamilk lốc 4 hộp | 30 | 10.0 | 40 | 68,3 | 449,1 | 86,5 |
| SKU088 | Kẹo Halloween túi 300g | 365 | 122.0 | 30 | 42,0 | 389,0 | 389,0 |
| SKU040 | Đá lạnh túi 5kg | 90 | 30.0 | 70 | 129,4 | 21,6 | 13,2 |
| SKU100 | Xúc xích tiệt trùng gói 10 cây | 180 | 60.0 | 45 | 79,6 | 0,0 | 0,0 |
| SKU109 | Cá hộp 150g | 1095 | 365.0 | 40 | 89,5 | 0,0 | 0,0 |

Mã có MOQ lớn hơn lượng bán được trong thời gian được giao (trần không giúp được): không có.

## 2. Sức chứa

Mốc 100% = đỉnh thực tồn trên validation2: Kho thường 1.254,8 m³, Kho lạnh 80,3 m³. 5 mã ở kho lạnh. Hiện trạng trên test đạt đỉnh 115% / 80% mốc này, vượt 17 ngày.

| Sức chứa | Tập | Phương án | Fill Rate | Tồn TB (tr đ) | Đỉnh thường / lạnh | Ngày vượt | Thuê ngoài (tr đ) | Lần cắt đơn | Tổng chi phí (tr đ) |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 100% | validation2 | A, thuê ngoài | 96,83% | 10.040,6 | 93% / 95% | 0 | 0,0 | 0 | 4.008,3 |
| 100% | validation2 | B, cắt đơn | 96,83% | 10.040,6 | 93% / 95% | 0 | 0,0 | 0 | 4.008,3 |
| 100% | test | A, thuê ngoài | 95,82% | 11.906,0 | 134% / 102% | 277 | 468,6 | 0 | 6.246,9 |
| 100% | test | B, cắt đơn | 92,80% | 10.330,4 | 115% / 98% | 197 | 102,4 | 8.604 | 7.611,0 |
| 90% | validation2 | A, thuê ngoài | 96,83% | 10.040,6 | 103% / 105% | 5 | 0,4 | 0 | 4.008,7 |
| 90% | validation2 | B, cắt đơn | 96,80% | 10.040,6 | 103% / 108% | 5 | 0,5 | 4 | 4.016,8 |
| 90% | test | A, thuê ngoài | 95,82% | 11.906,0 | 149% / 113% | 280 | 816,8 | 0 | 6.595,1 |
| 90% | test | B, cắt đơn | 76,56% | 10.225,7 | 115% / 97% | 223 | 103,8 | 14.423 | 19.050,5 |
| 80% | validation2 | A, thuê ngoài | 96,83% | 10.040,6 | 116% / 118% | 18 | 6,0 | 0 | 4.014,3 |
| 80% | validation2 | B, cắt đơn | 96,74% | 10.216,5 | 112% / 118% | 48 | 11,5 | 69 | 4.158,3 |
| 80% | test | A, thuê ngoài | 95,82% | 11.906,0 | 168% / 127% | 282 | 1.169,5 | 0 | 6.947,8 |
| 80% | test | B, cắt đơn | 75,21% | 9.483,7 | 117% / 131% | 217 | 107,8 | 14.897 | 19.495,0 |

Theo luật trên validation2: sức chứa 100%: **A, thuê ngoài**; sức chứa 90%: **A, thuê ngoài**; sức chứa 80%: **A, thuê ngoài**.

Độ nhạy giá thuê trên test, tổng chi phí (triệu đ):

| Sức chứa | Giá ×0,5: A | Giá ×0,5: B | Giá ×2: A | Giá ×2: B |
|---:|---:|---:|---:|---:|
| 100% | 6.012,6 | 7.559,8 | 6.715,5 | 7.713,4 |
| 90% | 6.186,7 | 18.998,6 | 7.411,9 | 19.154,3 |
| 80% | 6.363,0 | 19.441,1 | 8.117,3 | 19.602,9 |

## 3. Chẩn đoán (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)

| | Validation2 | Test |
|---|---:|---:|
| Phần tồn vượt nhu cầu thật 60 ngày kế tiếp, % thể tích | 44,0% | 62,5% |
| Trong phần vượt đó, nhóm Z chiếm | 100,0% | 99,6% |
| Giá trị hàng loại đến từ 18 mã chỉ bán dịp lễ | 92,6% | 92,4% |
| Số mã có hàng loại | 8 | 8 |
| Đỉnh thể tích thường / lạnh nếu bỏ mã lệch nhất, so với mốc 100% | 65% / 95% | 84% / 102% |
| Số ngày vượt nếu bỏ mã lệch nhất | 0 | 1 |

Các mã làm thể tích lệch xa hiện trạng nhất trên test:

| Mã | Tên | Thể tích TB (m³) | Hiện trạng (m³) | Chính sách nhập | Hiện trạng nhập | Nhu cầu | Tồn cuối kỳ |
|---|---|---:|---:|---:|---:|---:|---:|
| SKU089 | Cây thông Noel 1m2 | 502,7 | 92,1 | 9.670 | 5.075 | 4.999 | 5.193 |
| SKU048 | Máy sưởi dầu 11 thanh | 17,5 | 5,1 | 1.832 | 1.655 | 2.036 | 94 |
| SKU046 | Chăn lông cừu 1m8 | 10,7 | 6,1 | 4.269 | 4.073 | 5.290 | 98 |

### 8.8. Newsvendor cho hàng chỉ bán dịp lễ (nguồn: `reports/newsvendor_mua_vu.md`)


Luật ghi trước: docs/10 mục 10.12. Dữ liệu mô phỏng; hạn sử dụng và chi phí hàng dư là giả định. 18 mã, 36 cặp mùa liên tiếp; r trung vị 0,99, p10–p90 0,81–1,20.

## validation2

13 mùa theo newsvendor; 5 mùa giữ quy tắc thường vì ngày đặt trước đầu kỳ, mùa ra ngoài kỳ, hoặc thiếu mùa trước.

### Môi trường có hạn sử dụng (dùng để chọn trên validation2)

| Phương án | CP toàn kho (tr đ) | Fill toàn kho | Fill hàng dịp lễ | Tồn TB dịp lễ (tr đ) | Hàng loại (tr đ) | Tồn sau mùa (tr đ) | Đỉnh thể tích |
|---|---:|---:|---:|---:|---:|---:|---:|
| Quy tắc hiện tại | 10.270,2 | 96,32% | 84,98% | 3.107,7 | 6.443,6 | – | 88% |
| Newsvendor, một lần | 9.640,1 | 95,99% | 81,83% | 3.049,8 | 5.715,4 | 529,7 | 114% |
| Newsvendor + bổ sung | 10.207,5 | 96,72% | 88,82% | 3.709,8 | 6.334,7 | 2.931,9 | 115% |
| Một lần, xả được 50% | 9.606,1 | 96,09% | 82,84% | 3.068,3 | 5.715,4 | 529,7 | 114% |
| Bổ sung, xả được 50% | 10.120,9 | 96,74% | 89,05% | 3.708,4 | 6.259,7 | 2.856,8 | 115% |
| Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test) | 9.640,1 | 95,99% | 81,83% | 3.049,8 | 5.715,4 | 529,7 | 114% |

### Môi trường không hạn (thiên vị trữ dư)

| Phương án | CP toàn kho (tr đ) | Fill toàn kho | Fill hàng dịp lễ | Tồn TB dịp lễ (tr đ) | Hàng loại (tr đ) | Tồn sau mùa (tr đ) | Đỉnh thể tích |
|---|---:|---:|---:|---:|---:|---:|---:|
| Quy tắc hiện tại | 4.008,3 | 96,83% | 88,32% | 4.544,4 | 0,0 | – | 93% |
| Newsvendor, một lần | 4.018,5 | 96,60% | 86,12% | 4.202,3 | 0,0 | 529,7 | 119% |
| Newsvendor + bổ sung | 4.030,9 | 97,26% | 92,45% | 5.082,5 | 0,0 | 2.920,4 | 119% |
| Một lần, xả được 50% | 3.984,6 | 96,70% | 87,14% | 4.221,3 | 0,0 | 529,7 | 119% |
| Bổ sung, xả được 50% | 4.014,6 | 97,29% | 92,68% | 5.057,6 | 0,0 | 2.856,8 | 119% |
| Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test) | 4.018,5 | 96,60% | 86,12% | 4.202,3 | 0,0 | 529,7 | 119% |

## test

17 mùa theo newsvendor; 5 mùa giữ quy tắc thường vì ngày đặt trước đầu kỳ, mùa ra ngoài kỳ, hoặc thiếu mùa trước.

### Môi trường có hạn sử dụng (dùng để chọn trên validation2)

| Phương án | CP toàn kho (tr đ) | Fill toàn kho | Fill hàng dịp lễ | Tồn TB dịp lễ (tr đ) | Hàng loại (tr đ) | Tồn sau mùa (tr đ) | Đỉnh thể tích |
|---|---:|---:|---:|---:|---:|---:|---:|
| Quy tắc hiện tại | 11.756,9 | 95,85% | 96,63% | 5.090,6 | 6.233,3 | – | 126% |
| Newsvendor, một lần | 13.441,9 | 93,89% | 81,03% | 3.030,2 | 7.280,1 | 778,5 | 100% |
| Newsvendor + bổ sung | 14.921,3 | 95,54% | 94,17% | 5.599,5 | 8.807,4 | 8.843,9 | 142% |
| Một lần, xả được 50% | 13.757,8 | 93,95% | 81,50% | 3.072,5 | 7.607,2 | 856,8 | 100% |
| Bổ sung, xả được 50% | 14.980,7 | 95,77% | 95,95% | 5.631,7 | 9.148,4 | 7.917,8 | 143% |
| Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test) | 9.668,1 | 95,30% | 92,23% | 2.899,4 | 4.506,0 | 778,5 | 100% |

### Môi trường không hạn (thiên vị trữ dư)

| Phương án | CP toàn kho (tr đ) | Fill toàn kho | Fill hàng dịp lễ | Tồn TB dịp lễ (tr đ) | Hàng loại (tr đ) | Tồn sau mùa (tr đ) | Đỉnh thể tích |
|---|---:|---:|---:|---:|---:|---:|---:|
| Quy tắc hiện tại | 5.778,3 | 95,82% | 94,93% | 6.422,2 | 0,0 | – | 134% |
| Newsvendor, một lần | 5.343,2 | 95,34% | 91,16% | 3.571,7 | 0,0 | 856,2 | 106% |
| Newsvendor + bổ sung | 5.621,3 | 96,43% | 99,79% | 6.725,7 | 0,0 | 6.405,7 | 144% |
| Một lần, xả được 50% | 5.279,9 | 95,48% | 92,27% | 3.658,7 | 0,0 | 1.019,7 | 106% |
| Bổ sung, xả được 50% | 5.641,7 | 96,43% | 99,79% | 6.821,1 | 0,0 | 6.523,4 | 145% |
| Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test) | 5.242,1 | 95,33% | 91,04% | 3.417,5 | 0,0 | 856,2 | 106% |

## Theo luật

Trên validation2, môi trường có hạn: **Newsvendor, một lần**. Phương án bỏ mã hạn ngắn được thêm sau khi thấy test nên không dự chọn, chỉ để tham khảo.

## Mã chiếm chỗ nhất trên test: Cây thông Noel 1m2

| Phương án | Nhập | Tồn cuối kỳ |
|---|---:|---:|
| Quy tắc hiện tại | 9.670 | 5.193 |
| Newsvendor, một lần | 4.935 | 481 |
| Newsvendor + bổ sung | 9.670 | 5.199 |
| Một lần, xả được 50% | 4.935 | 481 |
| Bổ sung, xả được 50% | 9.670 | 5.199 |
| Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test) | 4.935 | 481 |

Nhu cầu cả kỳ: 4.999.

## Chẩn đoán theo từng dịp (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)

Quy tắc hiện tại so với newsvendor một lần. Chi phí gồm đặt hàng, lưu kho, lợi nhuận mất, hàng loại; triệu đ.

| Tập | Môi trường | Dịp | CP hiện tại | CP newsvendor | Fill hiện tại | Fill newsvendor | Loại hiện tại | Loại newsvendor |
|---|---|---|---:|---:|---:|---:|---:|---:|
| validation2 | Có hạn | halloween | 477,0 | 206,4 | 73,8% | 82,4% | 320,5 | 86,1 |
| validation2 | Có hạn | noel | 707,1 | 500,9 | 93,8% | 82,1% | 519,2 | 263,4 |
| validation2 | Có hạn | tet | 2.044,6 | 1.889,8 | 92,7% | 88,1% | 1.591,7 | 1.353,7 |
| validation2 | Có hạn | trung_thu | 3.904,6 | 3.904,6 | 66,2% | 66,2% | 3.537,4 | 3.537,4 |
| validation2 | Không hạn | halloween | 175,8 | 120,2 | 73,9% | 82,4% | 0,0 | 0,0 |
| validation2 | Không hạn | noel | 204,3 | 225,9 | 93,9% | 84,3% | 0,0 | 0,0 |
| validation2 | Không hạn | tet | 496,4 | 540,5 | 92,2% | 88,8% | 0,0 | 0,0 |
| validation2 | Không hạn | trung_thu | 488,8 | 488,8 | 82,6% | 82,6% | 0,0 | 0,0 |
| test | Có hạn | halloween | 494,1 | 155,6 | 81,8% | 94,6% | 389,0 | 102,2 |
| test | Có hạn | noel | 825,9 | 391,5 | 99,9% | 87,0% | 554,6 | 252,7 |
| test | Có hạn | tet | 2.814,1 | 1.468,5 | 99,7% | 94,6% | 2.224,7 | 1.086,2 |
| test | Có hạn | trung_thu | 2.855,5 | 6.659,6 | 95,6% | 63,7% | 2.594,2 | 5.368,3 |
| test | Không hạn | halloween | 132,2 | 53,2 | 81,9% | 94,6% | 0,0 | 0,0 |
| test | Không hạn | noel | 289,9 | 128,3 | 100,0% | 89,1% | 0,0 | 0,0 |
| test | Không hạn | tet | 710,7 | 386,7 | 99,7% | 95,4% | 0,0 | 0,0 |
| test | Không hạn | trung_thu | 372,1 | 503,7 | 91,4% | 86,9% | 0,0 | 0,0 |

Mã có thời gian từ ngày đặt đến hết mùa dài hơn số ngày được giao (một lần đặt không phục vụ hết mùa): validation2: không có; test: SKU067, SKU068.

### 8.9. Độ nhạy theo chi phí đặt (nguồn: `reports/do_nhay_chi_phi_dat.md`)


Luật ghi trước: docs/10 mục 10.13. Dữ liệu mô phỏng. Tập test, mức phục vụ 95%, quy tắc lượng đặt **lai** (giữ nguyên), EOQ tính lại theo S. Quy tắc kinh nghiệm / hiện trạng giữ nguyên đơn, chỉ tính lại chi phí. Đây là phân tích độ nhạy, không đổi giả định chính.

| S so với gốc | EOQ (ngày bán, trung vị) | Lợi ích AI so với dự báo mốc | Fill AI + HC | Fill dự báo mốc | Ngày-mã thiếu AI + HC | Ngày-mã thiếu dự báo mốc | Tồn AI + HC (tr đ) | Tồn dự báo mốc (tr đ) | CP liên quan AI + HC (tr đ) | CP liên quan dự báo mốc (tr đ) | CP liên quan hiện trạng (tr đ) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| × 0,10 | 4,8 | +37,1% | 95,12% | 90,95% | 1.013 | 1.161 | 10.484,4 | 18.203,5 | 5.408,4 | 8.597,8 | 6.171,3 |
| × 0,25 | 7,6 | +37,2% | 95,34% | 91,15% | 948 | 1.073 | 10.844,7 | 18.594,4 | 5.454,4 | 8.687,0 | 6.219,4 |
| × 0,50 | 10,8 | +36,5% | 95,50% | 91,45% | 862 | 972 | 11.296,3 | 19.026,6 | 5.562,1 | 8.754,2 | 6.299,6 |
| × 1,00 | 15,3 | +35,3% | 95,82% | 91,69% | 735 | 916 | 11.906,0 | 19.669,7 | 5.828,1 | 9.011,0 | 6.460,1 |
| × 2,00 | 21,6 | +34,9% | 96,15% | 91,90% | 660 | 842 | 12.760,8 | 20.558,8 | 6.066,3 | 9.321,4 | 6.780,9 |

**Theo luật:** lợi ích AI ở S × 0,1 cao hơn ở S × 1 1,8 điểm %, ngưỡng 5,0 điểm → **không phụ thuộc rõ**.

### 8.10. Cảnh báo dự báo lệch, mô phỏng (nguồn: `reports/canh_bao_lech.md`; M5: `du_lieu_nguon/m5_kho/reports/canh_bao_lech.md`)


Luật ghi trước: docs/10 mục 10.14. Dữ liệu mô phỏng. Mô hình ket_hop_v4, dự báo gốc. TS = tổng sai số / MAD trên 28 ngày đến hết ngày lập phiếu (ít nhất 14 ngày có thực tế). Lệch = (thực tế − dự báo) / dự báo của 28 ngày kế tiếp.

## Validation2: chọn ngưỡng

| Ngưỡng \|TS\| | Cặp (mã, mốc) | Cảnh báo | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \|lệch\| có cảnh báo | Trung vị \|lệch\| không cảnh báo | Gấp | Mã bị cảnh báo quá nửa số mốc | Đạt luật |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 5.657 | 4.102 | 72,5% | 51,5% | 12,4% | 10,2% | 1,22 | 120 | ❌ |
| 4 | 5.657 | 3.685 | 65,1% | 51,8% | 12,6% | 10,3% | 1,23 | 112 | ❌ |
| 5 | 5.657 | 3.274 | 57,9% | 52,0% | 13,2% | 9,9% | 1,33 | 83 | ❌ |
| 6 | 5.657 | 2.855 | 50,5% | 52,9% | 13,8% | 10,0% | 1,38 | 59 | ❌ |

Theo luật: **không ngưỡng nào đạt, cảnh báo chưa đủ tin cậy**.

M5:


Luật ghi trước: docs/10 mục 10.14. Nguồn: số bán thật M5 (Walmart), dựng thành kho tổng. Mô hình ket_hop_dl, dự báo gốc. TS = tổng sai số / MAD trên 28 ngày đến hết ngày lập phiếu (ít nhất 14 ngày có thực tế). Lệch = (thực tế − dự báo) / dự báo của 28 ngày kế tiếp.

## Validation2: chọn ngưỡng

| Ngưỡng \|TS\| | Cặp (mã, mốc) | Cảnh báo | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \|lệch\| có cảnh báo | Trung vị \|lệch\| không cảnh báo | Gấp | Mã bị cảnh báo quá nửa số mốc | Đạt luật |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 5.628 | 4.324 | 76,8% | 61,5% | 15,9% | 13,3% | 1,19 | 119 | ❌ |
| 4 | 5.628 | 3.874 | 68,8% | 62,5% | 16,3% | 13,2% | 1,23 | 108 | ❌ |
| 5 | 5.628 | 3.478 | 61,8% | 63,2% | 16,5% | 13,3% | 1,24 | 92 | ❌ |
| 6 | 5.628 | 3.081 | 54,7% | 64,4% | 17,3% | 13,3% | 1,30 | 73 | ❌ |

Theo luật: **không ngưỡng nào đạt, cảnh báo chưa đủ tin cậy**.

### 8.11. Cảnh báo dự báo lệch, vòng 2 (nguồn: `reports/canh_bao_lech_v2.md`; M5: `du_lieu_nguon/m5_kho/reports/canh_bao_lech_v2.md`)


Luật ghi trước: docs/10 mục 10.14 (vòng 2). Dữ liệu mô phỏng. Mô hình ket_hop_v4, dự báo gốc. TS = tổng sai số 4 tuần / MAD theo tuần của 13 tuần; sai số = số bán − dự báo.

## Phần 1: lệch kéo dài, validation2

| Ngưỡng \|TS\| | Cặp (mã, mốc) | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \|lệch\| có / không cảnh báo | Gấp | Đạt (a, b, c) |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 4.961 | 25,3% | 50,3% | 15,1% / 11,2% | 1,35 | ❌ |
| 4 | 4.961 | 13,9% | 50,2% | 17,9% / 11,4% | 1,57 | ❌ |
| 5 | 4.961 | 8,2% | 49,5% | 21,8% / 11,5% | 1,90 | ❌ |
| 6 | 4.961 | 4,8% | 49,2% | 34,2% / 11,5% | 2,97 | ❌ |

Theo luật: **không ngưỡng nào đạt**.

## Phần 2: thay đổi đột ngột, validation2

166 cặp (mã, đợt) có hệ số tác động ≥ 0,5 trong các đợt dài ≥ 7 ngày (cả kỳ dữ liệu); 0 đợt ngắn hơn bị loại. Bão và đơn B2B nằm ngoài phạm vi.

| Ngưỡng | (mã, đợt) xét được | Phát hiện | Cặp không sự kiện | TS > ngưỡng ở cặp không sự kiện | \|TS\| > ngưỡng ở cặp không sự kiện | Gấp | Đạt (d, e, c') |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 56 | 42,9% | 4.644 | 8,9% | 23,9% | 4,81 | ❌ |
| 4 | 56 | 32,1% | 4.644 | 5,0% | 12,7% | 6,38 | ❌ |
| 5 | 56 | 21,4% | 4.644 | 3,4% | 7,2% | 6,38 | ❌ |
| 6 | 56 | 14,3% | 4.644 | 2,2% | 4,3% | 6,44 | ❌ |

Theo luật: **không ngưỡng nào đạt**.

M5:


Luật ghi trước: docs/10 mục 10.14 (vòng 2). Nguồn: số bán thật M5 (Walmart), dựng thành kho tổng. Mô hình ket_hop_dl, dự báo gốc. TS = tổng sai số 4 tuần / MAD theo tuần của 13 tuần; sai số = số bán − dự báo.

## Phần 1: lệch kéo dài, validation2

| Ngưỡng \|TS\| | Cặp (mã, mốc) | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \|lệch\| có / không cảnh báo | Gấp | Đạt (a, b, c) |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 4.961 | 29,2% | 70,5% | 17,7% / 14,3% | 1,23 | ❌ |
| 4 | 4.961 | 15,1% | 72,8% | 19,2% / 14,6% | 1,32 | ❌ |
| 5 | 4.961 | 6,2% | 72,5% | 20,9% / 14,9% | 1,41 | ❌ |
| 6 | 4.961 | 2,9% | 72,9% | 28,7% / 15,0% | 1,92 | ❌ |

Theo luật: **không ngưỡng nào đạt**.

### 8.12. Dự báo 28 ngày chưa xảy ra (nguồn: `reports/du_bao_tuong_lai.md`; M5: `du_lieu_nguon/m5/reports/du_bao_tuong_lai.md`)


Ngày lập: **2026-09-30** (ngày cuối của dữ liệu). Mô hình **ket_hop_v4**. Các ngày dưới đây **chưa xảy ra**, chưa có số thật để so.

- Lịch biết trước mở rộng theo quy tắc của lịch hiện có (`src/tuong_lai.py`). Sự kiện không tự suy ra (không biết trước hoặc không lặp theo ngày cố định): dich_cum, nang_nong, ret_dam, sot_xuat_huyet, the_thao, tin_don_gia.
- Khuyến mãi có lịch gửi trước trong 28 ngày: 0 dòng mã-ngày (chưa có lịch khuyến mãi: coi như không khuyến mãi).
- Ngày kho nghỉ: không.

| Ngày | Tổng dự báo toàn kho | Khoảng 80% |
|---|---:|---|
| 2026-10-01 | 5.615 | 2.755 – 8.970 |
| 2026-10-02 | 6.039 | 2.960 – 9.650 |
| 2026-10-03 | 6.155 | 3.007 – 9.840 |
| 2026-10-04 | 2.743 | 1.363 – 4.379 |
| 2026-10-05 | 5.409 | 2.664 – 8.633 |
| 2026-10-06 | 5.528 | 2.729 – 8.819 |
| 2026-10-07 | 5.490 | 2.699 – 8.762 |
| 2026-10-08 | 5.763 | 2.791 – 9.246 |
| 2026-10-09 | 6.247 | 3.013 – 10.030 |
| 2026-10-10 | 6.405 | 3.064 – 10.301 |
| 2026-10-11 | 2.926 | 1.422 – 4.700 |
| 2026-10-12 | 5.474 | 2.626 – 8.798 |
| 2026-10-13 | 5.687 | 2.742 – 9.131 |
| 2026-10-14 | 5.734 | 2.763 – 9.206 |
| 2026-10-15 | 6.116 | 2.878 – 9.842 |
| 2026-10-16 | 6.430 | 2.976 – 10.394 |
| 2026-10-17 | 6.175 | 2.850 – 9.986 |
| 2026-10-18 | 2.903 | 1.346 – 4.697 |
| 2026-10-19 | 5.498 | 2.493 – 8.932 |
| 2026-10-20 | 5.695 | 2.601 – 9.233 |
| 2026-10-21 | 5.926 | 2.666 – 9.645 |
| 2026-10-22 | 6.252 | 2.762 – 10.223 |
| 2026-10-23 | 6.933 | 2.945 – 11.447 |
| 2026-10-24 | 7.291 | 3.087 – 12.042 |
| 2026-10-25 | 3.881 | 1.463 – 6.587 |
| 2026-10-26 | 6.688 | 2.644 – 11.217 |
| 2026-10-27 | 7.397 | 2.840 – 12.486 |
| 2026-10-28 | 7.746 | 2.767 – 13.262 |

M5:


Ngày lập: **2016-05-22** (ngày cuối của dữ liệu). Mô hình **ket_hop_dl** (RNN ghép với LightGBM + Prophet). Các ngày dưới đây **chưa xảy ra**.

- Lịch biết trước lấy từ lịch gốc của nguồn: snap_ca 10, snap_tx 10, snap_wi 10, the_thao 2, m5_memorialday 1, m5_ramadanstarts 1, m5_fathersday 1.
- Nguồn không có lịch khuyến mãi gửi trước: coi như không khuyến mãi.

Khoảng 80% / 95% có cho **từng mã**; không cộng thành khoảng của tổng.

| Ngày | Thứ | Tổng dự báo toàn kho |
|---|---|---:|
| 2016-05-23 | Thứ Hai | 1.249 |
| 2016-05-24 | Thứ Ba | 1.131 |
| 2016-05-25 | Thứ Tư | 1.118 |
| 2016-05-26 | Thứ Năm | 1.114 |
| 2016-05-27 | Thứ Sáu | 1.290 |
| 2016-05-28 | Thứ Bảy | 1.474 |
| 2016-05-29 | Chủ nhật | 1.387 |
| 2016-05-30 | Thứ Hai | 1.248 |
| 2016-05-31 | Thứ Ba | 1.120 |
| 2016-06-01 | Thứ Tư | 1.286 |
| 2016-06-02 | Thứ Năm | 1.270 |
| 2016-06-03 | Thứ Sáu | 1.490 |
| 2016-06-04 | Thứ Bảy | 1.634 |
| 2016-06-05 | Chủ nhật | 1.739 |
| 2016-06-06 | Thứ Hai | 1.407 |
| 2016-06-07 | Thứ Ba | 1.246 |
| 2016-06-08 | Thứ Tư | 1.267 |
| 2016-06-09 | Thứ Năm | 1.337 |
| 2016-06-10 | Thứ Sáu | 1.366 |
| 2016-06-11 | Thứ Bảy | 1.663 |
| 2016-06-12 | Chủ nhật | 1.663 |
| 2016-06-13 | Thứ Hai | 1.312 |
| 2016-06-14 | Thứ Ba | 1.287 |
| 2016-06-15 | Thứ Tư | 1.304 |
| 2016-06-16 | Thứ Năm | 1.159 |
| 2016-06-17 | Thứ Sáu | 1.317 |
| 2016-06-18 | Thứ Bảy | 1.522 |
| 2016-06-19 | Chủ nhật | 1.407 |

## Kiểm tra độ hợp lý (tính tự động từ dữ liệu)

| So sánh, trung bình mỗi ngày | Số bán / dự báo |
|---|---:|
| Cùng kỳ 1 năm trước (2015-05-25 … 2015-06-21) | 1.255 |
| Cùng kỳ 2 năm trước (2014-05-26 … 2014-06-22) | 1.395 |
| 28 ngày gần nhất trước ngày lập | 1.456 |
| **Dự báo 28 ngày tới** | **1.350** |

## 9. Học sâu trên dữ liệu mô phỏng

### 9.1. LSTM, RNN (nguồn: `reports/mo_hinh_dl.md`)

Quyết định theo luật: giữ **ket_hop_v4**; học sâu tốt hơn trên validation2: lstm; trọng số ghép {'X': 0.6, 'Y': 0.4, 'Z': 0.1}.

### 9.2. TiDE, N-HiTS, TFT (nguồn: `reports/mo_hinh_nf.md`)


Luật ghi trước: docs/10 mục 9.9. Quyết định chỉ dựa trên validation2. Mô hình đang dùng: ket_hop_v4.

| Mô hình | Validation2 WMAPE | Validation2 Bias | Test WMAPE | Test Bias |
|---|---:|---:|---:|---:|
| ket_hop_v4 | 0.358 | +5.5% | 0.356 | +3.0% |
| tide | 0.465 | +18.7% | 0.477 | +17.8% |
| nhits | 0.478 | +0.5% | 0.429 | +11.4% |
| tft | 0.412 | +16.9% | 0.425 | +17.1% |
| ket_hop_nf | 0.352 | +7.3% | 0.354 | +5.0% |

Quyết định: **ket_hop_v4** (trọng số ghép theo nhóm {'X': 0.5, 'Y': 0.3, 'Z': 0.0}, ghép với tft).

## 10. Kiểm chứng trên dữ liệu thật M5 (số bán thật, không phải mô phỏng)

### 10.0. Dữ liệu bộ kho dựng từ M5 (nguồn: CSDL `du_lieu_nguon/m5_kho/data/kho_hang.db`; số bán thật, phần còn lại giả định)

| Hạng mục | Giá trị |
|---|---|
| Số mã / nhóm hàng / nhà cung cấp | 121 / 7 / 7 |
| Thời gian | 2011-01-29 – 2016-05-22 (1.941 ngày) |
| Số dòng (mã × ngày) | 234.861 |

Ma trận ABC × XYZ (số mã, phân loại trên tập huấn luyện):

| ABC \ XYZ | X | Y | Z |
|---|---|---|---|
| A | 27 | 14 | 0 |
| B | 26 | 8 | 0 |
| C | 31 | 14 | 1 |

| Đặc điểm | Giá trị |
|---|---|
| Ngày kho nghỉ (cả kho) | 5 ngày |
| Xuất kho mỗi ngày mở cửa (toàn kho): trung bình / trung vị | 1.146 / 1.124 |
| Xuất kho mỗi mã mỗi ngày: trung vị; tỉ lệ ngày-mã bằng 0 | 3,0; 30,1% |
| Khuyến mãi: số đợt / số mã có / độ dài trung bình | 157 / 67 / 14,7 ngày |
| Phân loại nhu cầu (Syntetos–Boylan) | smooth (đều) 92, intermittent (rời rạc) 17, erratic (thất thường) 7, lumpy (rời rạc + thất thường) 5 |

Chu kỳ tuần (xuất trung bình theo thứ ÷ trung bình mọi ngày mở cửa):

| Thứ Hai | Thứ Ba | Thứ Tư | Thứ Năm | Thứ Sáu | Thứ Bảy | Chủ nhật |
|---|---|---|---|---|---|---|
| 0,96 | 0,89 | 0,87 | 0,87 | 0,98 | 1,23 | 1,20 |

### 10.1. Các mô hình (nguồn: `du_lieu_nguon/m5/reports/kiem_chung.md`)


Luật ghi trước: docs/10 mục 9.8. Mô hình chọn trên validation2, test chạy một lần.

Mô hình chọn: **ket_hop_dl**; trọng số LightGBM trong ket_hop {'X': 0.9, 'Y': 1.0, 'Z': 0.9}; học sâu dùng để ghép: rnn, trọng số {'X': 0.5, 'Y': 0.3, 'Z': 0.5}.

Trên test, mô hình chọn giảm WMAPE 13.8% so với trung bình trượt.

## Validation2

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---:|---:|---:|---:|---:|---:|
| ket_hop_dl | 0.331 | 0.186 | +1.8% | 0.322 | 0.357 | 1.017 |
| ket_hop | 0.337 | 0.187 | +0.7% | 0.329 | 0.360 | 1.037 |
| lightgbm | 0.338 | 0.187 | +0.9% | 0.330 | 0.360 | 1.039 |
| rnn | 0.342 | 0.203 | +3.6% | 0.328 | 0.382 | 1.044 |
| lstm | 0.344 | 0.207 | +2.4% | 0.334 | 0.375 | 0.958 |
| tb_truot | 0.382 | 0.211 | +0.2% | 0.371 | 0.411 | 1.072 |
| prophet | 0.431 | 0.294 | -3.1% | 0.386 | 0.562 | 1.229 |
| lap_tuan | 0.450 | 0.225 | +0.2% | 0.445 | 0.460 | 1.239 |

## Test

| Mô hình | WMAPE ngày | WMAPE tuần | Bias | X | Y | Z |
|---|---:|---:|---:|---:|---:|---:|
| ket_hop_dl | 0.307 | 0.162 | +3.1% | 0.299 | 0.328 | 0.930 |
| rnn | 0.311 | 0.170 | +4.4% | 0.303 | 0.331 | 0.906 |
| ket_hop | 0.313 | 0.164 | +2.0% | 0.305 | 0.337 | 0.989 |
| lightgbm | 0.314 | 0.165 | +2.0% | 0.306 | 0.337 | 1.001 |
| lstm | 0.317 | 0.178 | +4.6% | 0.308 | 0.343 | 0.792 |
| tb_truot | 0.356 | 0.187 | +0.4% | 0.343 | 0.390 | 0.989 |
| prophet | 0.389 | 0.250 | +1.1% | 0.350 | 0.502 | 1.038 |
| lap_tuan | 0.420 | 0.200 | +0.5% | 0.410 | 0.446 | 1.173 |

### 10.2. TiDE, N-HiTS, TFT trên M5 (nguồn: `du_lieu_nguon/m5/reports/mo_hinh_nf.md`)


Luật ghi trước: docs/10 mục 9.9. Quyết định chỉ dựa trên validation2. Mô hình đang dùng: ket_hop_dl.

| Mô hình | Validation2 WMAPE | Validation2 Bias | Test WMAPE | Test Bias |
|---|---:|---:|---:|---:|
| ket_hop_dl | 0.331 | +1.8% | 0.307 | +3.1% |
| tide | 0.350 | +9.1% | 0.328 | +8.0% |
| nhits | 0.366 | +10.2% | 0.341 | +10.9% |
| tft | 0.351 | +6.1% | 0.325 | +5.5% |
| ket_hop_nf | 0.328 | +3.5% | 0.306 | +4.3% |

Quyết định: **ket_hop_dl** (trọng số ghép theo nhóm {'X': 0.2, 'Y': 0.4, 'Z': 0.0}, ghép với tide). Batch 14.

### 10.3. Tồn kho trên bộ dữ liệu dựng từ M5 (nguồn: `du_lieu_nguon/m5_kho/reports/ton_kho_so_sanh.md`; lead time, chi phí, tồn kho là giả định)


12 thang test (2015-05-24 .. 2016-05-21), 121 SKU, quy tac luong dat **eoq** (chon tren validation2), muc phuc vu chinh 95%. Nguon: số bán thật M5 (Walmart), dựng thành kho tổng.
Hien trang: Hiện trạng: **quy tắc kinh nghiệm giả định** (mỗi 7 ngày đặt đủ 21 ngày bán theo trung bình 28 ngày trước), vì M5 không có số tồn kho.

## Toan kho (95%)

| ma_chinh_sach          |   fill_rate_pt |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   so_lan_nhap |   chi_phi_dat_trieu |   chi_phi_luu_trieu |   tong_chi_phi_trieu |   doanh_thu_mat_trieu |   loi_nhuan_mat_trieu |   chi_phi_lien_quan_trieu |
|:-----------------------|---------------:|--------------------:|-------------------:|--------------:|--------------------:|--------------------:|---------------------:|----------------------:|----------------------:|--------------------------:|
| cong_thuc_du_bao_ai_hc |          99.71 |                 126 |             1623.3 |          1500 |               247.5 |               323.8 |                571.3 |                 113.1 |                  23.6 |                     594.9 |
| cong_thuc_du_bao_ai    |          99.64 |                 127 |             1584.4 |          1511 |               249.3 |               316   |                565.3 |                 150.1 |                  31.9 |                     597.2 |
| cong_thuc_du_bao_moc   |          99.67 |                 112 |             1658.6 |          1483 |               244.7 |               330.8 |                575.5 |                 139.8 |                  29.6 |                     605.1 |
| hien_trang             |          99.38 |                 303 |             1195   |          5830 |               962   |               238.3 |               1200.3 |                 214.2 |                  44.7 |                    1245   |

## Theo nhom XYZ (95%)

| xyz_train   | ma_chinh_sach          |   fill_rate_pt |   ton_tb_trieu |   loi_nhuan_mat_trieu |
|:------------|:-----------------------|---------------:|---------------:|----------------------:|
| X           | cong_thuc_du_bao_ai    |           99.6 |          993.6 |                  23.8 |
| X           | cong_thuc_du_bao_ai_hc |           99.6 |          987.4 |                  21   |
| X           | cong_thuc_du_bao_moc   |           99.7 |         1043.7 |                  15.1 |
| X           | hien_trang             |           99.5 |          690.9 |                  20.9 |
| Y           | cong_thuc_du_bao_ai    |           99.8 |          585.3 |                   8.1 |
| Y           | cong_thuc_du_bao_ai_hc |           99.9 |          629.3 |                   2.6 |
| Y           | cong_thuc_du_bao_moc   |           99.5 |          607   |                  14.4 |
| Y           | hien_trang             |           99.1 |          501.8 |                  23.4 |
| Z           | cong_thuc_du_bao_ai    |          100   |            5.5 |                   0   |
| Z           | cong_thuc_du_bao_ai_hc |          100   |            6.6 |                   0   |
| Z           | cong_thuc_du_bao_moc   |           98   |            7.9 |                   0.2 |
| Z           | hien_trang             |           95.6 |            2.2 |                   0.4 |

## Do nhay theo muc phuc vu

| ma_chinh_sach          |   muc_phuc_vu |   fill_rate_pt |   ton_tb_trieu_vnd |   chi_phi_lien_quan_trieu |
|:-----------------------|--------------:|---------------:|-------------------:|--------------------------:|
| cong_thuc_du_bao_ai_hc |          0.9  |          99.45 |             1544   |                     609   |
| cong_thuc_du_bao_ai    |          0.9  |          99.39 |             1503.8 |                     614.4 |
| cong_thuc_du_bao_moc   |          0.9  |          99.34 |             1575.5 |                     616.7 |
| cong_thuc_du_bao_ai_hc |          0.95 |          99.71 |             1623.3 |                     594.9 |
| cong_thuc_du_bao_ai    |          0.95 |          99.64 |             1584.4 |                     597.2 |
| cong_thuc_du_bao_moc   |          0.95 |          99.67 |             1658.6 |                     605.1 |
| cong_thuc_du_bao_ai    |          0.99 |          99.91 |             1726.4 |                     602.8 |
| cong_thuc_du_bao_ai_hc |          0.99 |          99.91 |             1773.6 |                     610.7 |
| cong_thuc_du_bao_moc   |          0.99 |          99.87 |             1823.6 |                     626.2 |

### 10.4. Chỉ số kho trên bộ M5 (nguồn: `du_lieu_nguon/m5_kho/reports/chi_so_kho.md`)


Mô phỏng 364 ngày của tập kiểm tra, mức phục vụ 95%. Nguồn: số bán thật M5 (Walmart), dựng thành kho tổng; tồn kho là kết quả mô phỏng chính sách, lead time và chi phí là giả định, không phải số liệu kho thật.

Tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng để ra quyết định); bỏ 28 ngày cuối kỳ.

## Theo chính sách

| ma_chinh_sach          |   vong_quay_lan_nam |   so_ngay_ton |   ton_tb_trieu |   ton_du_tb_trieu |   ti_le_du_pt |
|:-----------------------|--------------------:|--------------:|---------------:|------------------:|--------------:|
| cong_thuc_du_bao_ai    |                22.1 |          16.5 |         1584.4 |             242   |          15.3 |
| cong_thuc_du_bao_ai_hc |                21.6 |          16.9 |         1623.3 |             252.4 |          15.5 |
| cong_thuc_du_bao_moc   |                21.1 |          17.3 |         1658.6 |             263.3 |          15.9 |
| hien_trang             |                29.3 |          12.5 |         1195   |             137.8 |          11.6 |

## Số ngày tồn kho theo nhóm XYZ

| ma_chinh_sach          |    X |    Y |    Z |
|:-----------------------|-----:|-----:|-----:|
| cong_thuc_du_bao_ai    | 16   | 17.3 | 40.9 |
| cong_thuc_du_bao_ai_hc | 15.9 | 18.6 | 49   |
| cong_thuc_du_bao_moc   | 16.8 | 18   | 60.3 |
| hien_trang             | 11.1 | 14.9 | 17.5 |

## 10 mã tồn dư lớn nhất (AI + hiệu chỉnh)

| ma_sku          | ten             | xyz   |   du_trieu |
|:----------------|:----------------|:------|-----------:|
| FOODS_3_134     | FOODS_3_134     | Y     |       45.6 |
| FOODS_3_370     | FOODS_3_370     | Y     |       35.9 |
| FOODS_3_797     | FOODS_3_797     | Y     |        7.9 |
| HOUSEHOLD_1_223 | HOUSEHOLD_1_223 | Y     |        6.6 |
| FOODS_3_216     | FOODS_3_216     | X     |        5.5 |
| HOUSEHOLD_2_282 | HOUSEHOLD_2_282 | Y     |        5.2 |
| FOODS_3_463     | FOODS_3_463     | Y     |        4.8 |
| FOODS_3_093     | FOODS_3_093     | Y     |        4.4 |
| HOUSEHOLD_2_466 | HOUSEHOLD_2_466 | Y     |        3.9 |
| FOODS_2_310     | FOODS_2_310     | X     |        3.7 |

### 10.5. Gom đơn trên bộ M5 (nguồn: `du_lieu_nguon/m5_kho/reports/gom_don.md`; nhà cung cấp và chi phí là giả định)


Luật ghi trước: docs/10 mục 10.6. Chính sách AI + hiệu chỉnh, mức phục vụ 95%, quy tắc lượng đặt eoq. Nguồn: số bán thật M5 (Walmart), dựng thành kho tổng; lead time, chi phí, nhà cung cấp là giả định; tỉ lệ chi phí chung của phiếu là **giả định**. Chi phí đặt ở đây tính theo dòng đặt nên hơi khác `ket_qua_ton_kho` (tính theo số ngày nhận hàng).

## Validation2: chọn k (tỉ lệ 0,5)

| Phương án | Dòng đặt | Số phiếu | Fill Rate | Tồn TB (tr đ) | CP đặt riêng | CP đặt gom | CP liên quan riêng | CP liên quan gom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Chỉ gom cùng ngày | 1.361 | 953 | 99,63% | 1.539,3 | 224,6 | 190,9 | 574,7 | 541,1 |
| k = 1 | 1.364 | 701 | 99,74% | 1.586,3 | 225,1 | 170,4 | 568,8 | 514,1 |
| k = 2 | 1.364 | 568 | 99,76% | 1.639,6 | 225,1 | 159,4 | 581,5 | 515,8 |
| k = 3 | 1.362 | 472 | 99,78% | 1.684,6 | 224,7 | 151,3 | 585,8 | 512,3 |
| k = 5 | 1.364 | 362 | 99,82% | 1.798,8 | 225,1 | 142,4 | 601,2 | 518,5 |

Theo luật: **đặt kèm k = 3**.

## Test (chỉ báo cáo)

| Phương án | Dòng đặt | Số phiếu | Fill Rate | Tồn TB (tr đ) | CP đặt riêng | CP đặt gom | CP liên quan riêng | CP liên quan gom |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Chỉ gom cùng ngày, tỉ lệ 0,3 | 1.418 | 1.008 | 99,71% | 1.623,3 | 234,0 | 213,7 | 581,4 | 561,1 |
| Chỉ gom cùng ngày, tỉ lệ 0,5 | 1.418 | 1.008 | 99,71% | 1.623,3 | 234,0 | 200,1 | 581,4 | 547,5 |
| Chỉ gom cùng ngày, tỉ lệ 0,7 | 1.418 | 1.008 | 99,71% | 1.623,3 | 234,0 | 186,6 | 581,4 | 534,0 |
| Đặt kèm k = 3, tỉ lệ 0,3 | 1.427 | 473 | 99,78% | 1.758,6 | 235,5 | 188,2 | 604,3 | 557,1 |
| Đặt kèm k = 3, tỉ lệ 0,5 | 1.427 | 473 | 99,78% | 1.758,6 | 235,5 | 156,8 | 604,3 | 525,6 |
| Đặt kèm k = 3, tỉ lệ 0,7 | 1.427 | 473 | 99,78% | 1.758,6 | 235,5 | 125,3 | 604,3 | 494,1 |

## Lợi ích đến từ đâu (test, tỉ lệ 0,5)

- Mức 1, chỉ gom cùng ngày: giảm **33,8 triệu đ** chi phí liên quan, không đổi tồn kho, không đổi Fill Rate.
- Mức 2 so với mức 1: giảm **22,0 triệu đ**, gồm đặt hàng 43,4, lưu kho -27,0, lợi nhuận mất 5,6.
- Phần lớn lợi ích đến từ **chia sẻ chi phí phiếu** (đặt hàng 43,4 triệu đ), nên phụ thuộc giả định tỉ lệ chi phí chung; đổi lại hàng được đặt sớm hơn nên tồn kho tăng (lưu kho thêm 27,0 triệu đ).

Chấm điểm nhà cung cấp, hạn sử dụng, sức chứa, newsvendor hàng dịp lễ không áp dụng cho M5 (docs/10 mục 10.13).

### 10.6. Độ nhạy theo chi phí đặt trên bộ M5 (nguồn: `du_lieu_nguon/m5_kho/reports/do_nhay_chi_phi_dat.md`)


Luật ghi trước: docs/10 mục 10.13. Nguồn: số bán thật M5 (Walmart), dựng thành kho tổng; chi phí, lead time là giả định. Tập test, mức phục vụ 95%, quy tắc lượng đặt **eoq** (giữ nguyên), EOQ tính lại theo S. Quy tắc kinh nghiệm / hiện trạng giữ nguyên đơn, chỉ tính lại chi phí. Đây là phân tích độ nhạy, không đổi giả định chính.

| S so với gốc | EOQ (ngày bán, trung vị) | Lợi ích AI so với dự báo mốc | Fill AI + HC | Fill dự báo mốc | Ngày-mã thiếu AI + HC | Ngày-mã thiếu dự báo mốc | Tồn AI + HC (tr đ) | Tồn dự báo mốc (tr đ) | CP liên quan AI + HC (tr đ) | CP liên quan dự báo mốc (tr đ) | CP liên quan hiện trạng (tr đ) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| × 0,10 | 11,6 | +6,4% | 99,41% | 99,30% | 315 | 265 | 863,1 | 901,4 | 299,8 | 320,3 | 379,2 |
| × 0,25 | 18,4 | +0,4% | 99,42% | 99,30% | 256 | 229 | 1.068,9 | 1.099,8 | 385,6 | 387,0 | 523,5 |
| × 0,50 | 26,0 | +2,6% | 99,63% | 99,45% | 149 | 159 | 1.287,7 | 1.319,5 | 462,7 | 475,2 | 764,0 |
| × 1,00 | 36,7 | +1,7% | 99,71% | 99,67% | 126 | 112 | 1.623,3 | 1.658,6 | 594,9 | 605,1 | 1.245,0 |
| × 2,00 | 51,9 | +0,1% | 99,78% | 99,73% | 103 | 84 | 2.082,9 | 2.122,1 | 807,2 | 808,1 | 2.206,9 |

**Theo luật:** lợi ích AI ở S × 0,1 cao hơn ở S × 1 4,7 điểm %, ngưỡng 5,0 điểm → **không phụ thuộc rõ**.

## 11. Nguồn dữ liệu công khai cần trích dẫn

- M5 Forecasting: bản sao Zenodo record 12636070, gốc từ Kaggle (Walmart, University of Nicosia). Zenodo ghi CC BY 4.0, người đăng là bên thứ ba: cần hỏi giảng viên.
- Dominick's Dataset: Kilts Center for Marketing, University of Chicago Booth School of Business. Chỉ dùng cho nghiên cứu học thuật, phải ghi nguồn.

## 12. Hình cho đồ án

- Kết quả: `reports/ket_qua/k01`–`k07`. Khám phá dữ liệu: `reports/eda/h01`–`h08`. Sơ đồ: `reports/so_do/`.

## 13. Luật và quyết định

Toàn bộ luật ghi trước, kết quả từng vòng và nhật ký: `docs/10_bao_cao_giai_doan_2.md` (mục 9.4–9.9, 10.2–10.7, mục 14).
