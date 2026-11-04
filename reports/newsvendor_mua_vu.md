# Newsvendor cho hàng chỉ bán dịp lễ

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
