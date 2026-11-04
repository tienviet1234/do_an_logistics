# Trữ hàng cho phiên livestream

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
