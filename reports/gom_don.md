# Gom đơn theo nhà cung cấp

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
