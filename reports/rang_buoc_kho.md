# Hạn sử dụng và sức chứa kho

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
