# Độ nhạy theo chi phí đặt hàng

Luật ghi trước: docs/10 mục 10.13. Dữ liệu mô phỏng. Tập test, mức phục vụ 95%, quy tắc lượng đặt **lai** (giữ nguyên), EOQ tính lại theo S. Quy tắc kinh nghiệm / hiện trạng giữ nguyên đơn, chỉ tính lại chi phí. Đây là phân tích độ nhạy, không đổi giả định chính.

| S so với gốc | EOQ (ngày bán, trung vị) | Lợi ích AI so với dự báo mốc | Fill AI + HC | Fill dự báo mốc | Ngày-mã thiếu AI + HC | Ngày-mã thiếu dự báo mốc | Tồn AI + HC (tr đ) | Tồn dự báo mốc (tr đ) | CP liên quan AI + HC (tr đ) | CP liên quan dự báo mốc (tr đ) | CP liên quan hiện trạng (tr đ) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| × 0,10 | 4,8 | +37,1% | 95,12% | 90,95% | 1.013 | 1.161 | 10.484,4 | 18.203,5 | 5.408,4 | 8.597,8 | 6.171,3 |
| × 0,25 | 7,6 | +37,2% | 95,34% | 91,15% | 948 | 1.073 | 10.844,7 | 18.594,4 | 5.454,4 | 8.687,0 | 6.219,4 |
| × 0,50 | 10,8 | +36,5% | 95,50% | 91,45% | 862 | 972 | 11.296,3 | 19.026,6 | 5.562,1 | 8.754,2 | 6.299,6 |
| × 1,00 | 15,3 | +35,3% | 95,82% | 91,69% | 735 | 916 | 11.906,0 | 19.669,7 | 5.828,1 | 9.011,0 | 6.460,1 |
| × 2,00 | 21,6 | +34,9% | 96,15% | 91,90% | 660 | 842 | 12.760,8 | 20.558,8 | 6.066,3 | 9.321,4 | 6.780,9 |

**Theo luật:** lợi ích AI ở S × 0,1 cao hơn ở S × 1 1,8 điểm %, ngưỡng 5,0 điểm → **không phụ thuộc rõ**.
