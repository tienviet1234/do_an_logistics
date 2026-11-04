# Chấm điểm nhà cung cấp

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
