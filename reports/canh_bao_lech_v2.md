# Cảnh báo dự báo lệch, vòng 2

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
