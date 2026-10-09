# Lịch sale sàn thương mại điện tử


## Sheet: Tham_so_sale

| Tham số dùng cho Lich_sale_TMDT |  |  |  |  |
|---|---|---|---|---|
| Năm cần tạo lịch | 2026 | Ô vàng: đổi năm thì cột Ngày đầy đủ trong Lich_sale_TMDT tự đổi. |  |  |
| Mức | Ý nghĩa | lower_window (ngày trước sale) | upper_window (ngày sau sale) | Ghi chú |
| 1 | Sale lớn: 11.11, 12.12, 9.9, 6.6, Black Friday | -3 | 3 | Giá trị gợi ý của người lập bảng, chưa hiệu chỉnh bằng dữ liệu thật. Sửa ở ô vàng. |
| 2 | Sale ngày đôi còn lại | -1 | 2 | Giá trị gợi ý của người lập bảng, chưa hiệu chỉnh bằng dữ liệu thật. Sửa ở ô vàng. |
| 3 | Nhịp lặp đầu, giữa, cuối tháng và cuối tuần | 0 | 1 | Giá trị gợi ý của người lập bảng, chưa hiệu chỉnh bằng dữ liệu thật. Sửa ở ô vàng. |
| Quy ước màu: chữ xanh, nền vàng là ô nhập hoặc giả định; chữ đen là công thức hoặc nội dung cố định. |  |  |  |  |

## Sheet: Lich_sale_TMDT

| Lịch sale của các sàn thương mại điện tử tại Việt Nam |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|
| Tổng hợp từ bài viết của bên bán lẻ (không phải lịch chính thức của sàn). Cột ds, lower_window, upper_window dùng được cho Prophet holidays. |  |  |  |  |  |  |  |  |
| Tháng | Ngày | Ngày đầy đủ (theo năm ở Tham_so_sale) | Tên thường gặp | Hàng thường tăng | Mức (1–3) | lower_window | upper_window | Tên holiday gợi ý |
| 1 | 1 | 2026-01-01 00:00:00 | Sale đầu năm | Hàng gia dụng, voucher toàn sàn | 2 | -1 | 2 | sale_1_1 |
| 2 | 2 | 2026-02-02 00:00:00 | Flash sale đầu tháng | Chăm sóc cá nhân, phụ kiện công nghệ | 2 | -1 | 2 | sale_2_2 |
| 3 | 3 | 2026-03-03 00:00:00 | Sale chào xuân | Thời trang, mỹ phẩm, đồ gia dụng | 2 | -1 | 2 | sale_3_3 |
| 4 | 4 | 2026-04-04 00:00:00 | Sale mùa hè | Quạt, điều hòa, đồ du lịch | 2 | -1 | 2 | sale_4_4 |
| 5 | 5 | 2026-05-05 00:00:00 | Sale giữa năm, ngày hội thương hiệu | Hàng thương hiệu, livestream | 2 | -1 | 2 | sale_5_5 |
| 6 | 6 | 2026-06-06 00:00:00 | Mid-year Sale | Điện tử, đồ gia dụng | 1 | -3 | 3 | sale_6_6 |
| 7 | 7 | 2026-07-07 00:00:00 | Sale mùa du lịch | Vali, balo, chăm sóc cá nhân | 2 | -1 | 2 | sale_7_7 |
| 8 | 8 | 2026-08-08 00:00:00 | Siêu sale livestream | Hàng bán qua KOL, KOC | 2 | -1 | 2 | sale_8_8 |
| 9 | 9 | 2026-09-09 00:00:00 | Siêu sale toàn sàn | Điện tử, mỹ phẩm, đồ gia dụng; mở đầu mùa cao điểm cuối năm | 1 | -3 | 3 | sale_9_9 |
| 10 | 10 | 2026-10-10 00:00:00 | Đại tiệc deal sốc | Công nghệ, mỹ phẩm, thời trang | 2 | -1 | 2 | sale_10_10 |
| 11 | 11 | 2026-11-11 00:00:00 | Ngày hội mua sắm lớn nhất năm | Hầu hết ngành hàng | 1 | -3 | 3 | sale_11_11 |
| 12 | 12 | 2026-12-12 00:00:00 | Sale cuối năm | Hàng tồn, quà cuối năm | 1 | -3 | 3 | sale_12_12 |
| 11 | Thứ Sáu thứ 4 | 2026-11-27 00:00:00 | Black Friday | Điện tử, thời trang, gia dụng; thứ Sáu ngay sau Lễ Tạ ơn (thứ Năm thứ 4 của tháng 11) | 1 | -3 | 3 | black_friday |
| Trước Tết | 2–3 tuần | Chưa có ngày cố định | Sale Tết Nguyên đán | Quà tặng, thực phẩm, đồ trang trí | 1 | Dùng cửa sổ của Tết | Dùng cửa sổ của Tết | sale_tet |
| Ghi chú |  |  |  |  |  |  |  |  |
| Cột Mức (ô vàng) là phân hạng gợi ý của người lập bảng: 1 là sale lớn, 2 là sale ngày đôi thường. Bạn có thể sửa. |  |  |  |  |  |  |  |  |
| Black Friday được tính bằng công thức (thứ Sáu thứ 4 của tháng 11). "Online Friday" của Bộ Công Thương chưa đối chiếu được nguồn nên chưa đưa vào. |  |  |  |  |  |  |  |  |

## Sheet: Nhip_sale_TMDT

| Nhịp sale lặp lại trong tháng |  |  |  |
|---|---|---|---|
| Chu kỳ | Mô tả | Mức gợi ý | Nguồn |
| Đầu tháng | Sale với voucher toàn sàn | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |
| Giữa tháng | Flash sale giảm sâu theo khung giờ | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |
| Cuối tháng | Xả hàng và hoàn xu | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |
| Cuối tuần | Sale từ thứ Sáu đến Chủ nhật, nhóm hàng thường ngày, thời trang, phụ kiện | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |
| Flash sale hằng ngày | Khung giờ cố định (ví dụ 0h, 12h, 20h), số lượng giới hạn | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |
| Sale theo chủ đề | Tuần lễ công nghệ, làm đẹp, đồ gia dụng | 3 | Bài tổng hợp lịch sale Shopee (viettablet.com) |

## Sheet: Tac_dong_sale_len_kho

| Ý nghĩa của sale với kho và cách đưa vào mô hình dự báo |  |  |
|---|---|---|
| Yếu tố | Điều xảy ra | Cách đưa vào mô hình |
| Phân hạng | Sale lớn (11.11, 12.12, 9.9, 6.6, Black Friday) mạnh hơn sale ngày đôi thường và nhịp tháng | Gán mức 1, 2, 3 (xem Tham_so_sale); mỗi mức một cửa sổ |
| Cửa sổ trước sale | Đơn tăng từ 1 đến 3 ngày trước sale (đặt trước, gom voucher) | lower_window âm trong Prophet |
| Cửa sổ sau sale | Xử lý đơn và trả hàng kéo dài 2 đến 3 ngày sau | upper_window dương |
| Kéo nhu cầu về trước | Sau sale lớn thường có đoạn nhu cầu tụt vì khách đã mua trước | Thêm cờ "sau sale" hoặc biến dip |
| Trả hàng | Tỷ lệ trả hàng cao sau sale; qty_out ròng có thể thấp hơn doanh số bán | Tách đơn bán và đơn trả khi làm sạch dữ liệu |
| Theo ngành hàng | Điện tử, mỹ phẩm, thời trang tăng mạnh; thực phẩm khô tăng nhẹ | Hệ số riêng theo SKU hoặc nhóm hàng |
| Loại kho | Kho phân phối B2B (siêu thị, đại lý): ảnh hưởng nhẹ. Kho giao hàng cho người bán trên sàn (fulfillment): ảnh hưởng lớn | Xác nhận với đơn vị thực tập trước khi chọn mức độ ưu tiên |
| Chuẩn bị | Người bán nhập hàng trước sale 1 đến 2 tuần | Đẩy ROP và Safety Stock lên trước sale lớn |

## Sheet: Nguon_sale_TMDT

| Nguồn và lưu ý về lịch sale |
|---|
| Shopee: https://www.viettablet.com/cac-ngay-sale-lon-2026-cua-shopee |
| TikTok Shop: https://www.viettablet.com/cac-ngay-sale-lon-2026-tiktok-shop |
| Đây là bài viết của bên bán lẻ, không phải lịch chính thức của sàn; lịch, ngân sách voucher và nội dung từng sale có thể đổi mỗi năm, cần kiểm tra lại trên ứng dụng của sàn. |
| Lịch Lazada: bài tra được chỉ nói về Philippines, nên chưa đưa vào bảng. |
| Sinh nhật từng sàn (Shopee, Lazada, TikTok Shop) và Online Friday: chưa có nguồn xác nhận trong lần tra này. |
| Cột Mức, lower_window và upper_window là gợi ý của người lập bảng, chưa hiệu chỉnh bằng dữ liệu thật; dữ liệu mô phỏng hiện chỉ có 11.11, 12.12 và Black Friday. |