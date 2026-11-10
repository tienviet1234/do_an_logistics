# Cảnh báo dự báo bắt đầu lệch

Luật ghi trước: docs/10 mục 10.14. Dữ liệu mô phỏng. Mô hình ket_hop_v4, dự báo gốc. TS = tổng sai số / MAD trên 28 ngày đến hết ngày lập phiếu (ít nhất 14 ngày có thực tế). Lệch = (thực tế − dự báo) / dự báo của 28 ngày kế tiếp.

## Validation2: chọn ngưỡng

| Ngưỡng \|TS\| | Cặp (mã, mốc) | Cảnh báo | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \|lệch\| có cảnh báo | Trung vị \|lệch\| không cảnh báo | Gấp | Mã bị cảnh báo quá nửa số mốc | Đạt luật |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 5.657 | 4.102 | 72,5% | 51,5% | 12,4% | 10,2% | 1,22 | 120 | ❌ |
| 4 | 5.657 | 3.685 | 65,1% | 51,8% | 12,6% | 10,3% | 1,23 | 112 | ❌ |
| 5 | 5.657 | 3.274 | 57,9% | 52,0% | 13,2% | 9,9% | 1,33 | 83 | ❌ |
| 6 | 5.657 | 2.855 | 50,5% | 52,9% | 13,8% | 10,0% | 1,38 | 59 | ❌ |

Theo luật: **không ngưỡng nào đạt, cảnh báo chưa đủ tin cậy**.
