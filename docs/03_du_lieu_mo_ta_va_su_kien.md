# Mô tả bộ dữ liệu, lý do tăng đột biến, lịch nghỉ, lịch sự kiện


## Sheet: Huong_dan

| DỮ LIỆU ĐẦU VÀO TỔNG HỢP — Dự báo nhu cầu & tối ưu tồn kho (4 mùa, ngày lễ, bão lũ, cú sốc, lịch sale sàn TMĐT) |  |
|---|---|
| LƯU Ý: đây là DỮ LIỆU MÔ PHỎNG (Python, seed cố định) để xây dựng và kiểm thử quy trình khi chưa có số liệu thật từ đơn vị thực tập. Khi có file export từ WMS/ERP, giữ nguyên tên cột để thay vào. |  |
| Phạm vi | 121 SKU × 1.096 ngày (01/10/2023 – 30/09/2026) = 132.616 dòng. Có 3 mùa Tết (10/02/2024, 29/01/2025, 17/02/2026), 3 mùa Trung thu (2024, 2025, 2026) và 3 chu kỳ đủ 4 mùa. |
| Quy ước 4 mùa (miền Bắc) | Xuân: tháng 2–4 · Hạ: tháng 5–7 · Thu: tháng 8–10 · Đông: tháng 11–1. Cột `mua` trong Giao_dich. |
| SHEET | NỘI DUNG |
| SKU_master | 121 SKU + tham số EOQ/SS/ROP (giá vốn, lead time, chi phí đặt hàng, tỷ lệ lưu kho, MOQ), phân loại ABC, XYZ và nhãn `loai_mua_vu` (Quanh năm / Mùa hè / Mùa đông / Mùa mưa / Chỉ dịp Tết / Trung thu / Quà tặng / Khai giảng / Halloween / Noel). |
| Giao_dich_SACH | Nhập–xuất–tồn theo ngày, không lỗi. Dùng để chạy mô hình. |
| Lich_su_kien | Ngày lễ theo ĐÚNG ĐỊNH DẠNG Prophet holidays: holiday, ds, lower_window, upper_window. lower_window âm = số ngày trước lễ mà nhu cầu bắt đầu tăng (Tết −28, Trung thu −25, Noel −20…). |
| Ngay_nghi_kho | Ngày kho đóng cửa (Tết 7 ngày, 30/4, 1/5, 2/9, 1/1, Giỗ Tổ). Khi đó qty_in = qty_out = 0. |
| Mua_x_SKU | Chỉ số mùa: bán TB/ngày trong từng mùa ÷ TB cả năm (1,0 = bình thường; 3,0 = gấp 3). Cột `ban_it_ngoai_mua` = Có nếu có mùa bán dưới 30% mức TB. Có kèm tồn cuối kỳ và số ngày tồn kho (DOH) để thấy hàng tồn không bán được. |
| NgayLe_x_SKU | Hệ số tăng ở 10–28 ngày trước từng ngày lễ so với TB cả năm của SKU. Ví dụ 4,0 nghĩa là bán gấp 4 lần bình thường; dưới 1,0 nghĩa là ngày lễ đó không giúp bán thêm (thậm chí giảm). |
| NgayLe_x_Nhom | Như trên nhưng gộp theo nhóm hàng để đọc nhanh. |
| Su_kien_dot_bien | Nhật ký MỌI cú sốc đã đưa vào: bão lũ (ngày thực tế, mức độ giả định), nắng nóng, rét đậm, tin đồn tăng giá, dịch bệnh, thể thao, đơn B2B lớn, nhà cung cấp giao chậm. Cột nguon_du_lieu cho biết cái nào là mốc thực tế, cái nào là mô phỏng. |
| Bao_lu_x_SKU | Nhu cầu thực ÷ nhu cầu kỳ vọng theo mùa vụ/lịch trong 3 ngày trước bão và 10 ngày sau bão (các bão mức ≥0,5). Cột nhom_nhu_yeu_pham nhận diện hàng tăng mạnh hoặc giảm khi bão lũ. |
| Ly_do_tang_dot_bien | Bảng tra: 14 nhóm lý do nhu cầu tăng đột ngột, hàng bị ảnh hưởng, dấu hiệu nhận biết, cách đưa vào mô hình. |
| Nhat_ky_loi | Đáp án lỗi cố ý chèn vào file THO (CSV riêng): thiếu qty_out, nhập sai ×10/×100, dòng trùng. |
| LỊCH SALE SÀN TMĐT (gộp từ file riêng) |  |
| Lich_sale_TMDT | 12 sale ngày đôi (1.1 đến 12.12), Black Friday, sale Tết: ngày đầy đủ theo năm ở Tham_so_sale, mức 1–3 và lower/upper_window gợi ý cho Prophet. Là LỊCH THAM KHẢO từ bài viết bên bán lẻ, không phải lịch chính thức của sàn. |
| Tham_so_sale | Ô vàng: năm cần tạo lịch và cửa sổ trước/sau sale theo từng mức (giá trị gợi ý, chưa hiệu chỉnh bằng dữ liệu). |
| Nhip_sale_TMDT | Nhịp sale lặp trong tháng: đầu, giữa, cuối tháng, cuối tuần, flash sale hằng ngày. |
| Tac_dong_sale_len_kho | Ý nghĩa của sale với kho và cách đưa vào mô hình. |
| Nguon_sale_TMDT | Nguồn và các chỗ chưa kiểm chứng. |
| LƯU Ý QUAN TRỌNG | Dữ liệu mô phỏng chỉ áp dụng hiệu ứng sale cho 11.11, 12.12 và Black Friday; các ngày sale còn lại chỉ là lịch tham khảo để làm biến holidays khi có dữ liệu thật. |
| TỪ ĐIỂN — Giao_dich_SACH |  |
| date | Ngày |
| ma_sku | Mã SKU (khóa nối SKU_master) |
| thu | Thứ (2 = Thứ Hai … 8 = Chủ Nhật) |
| mua | Xuân / Hạ / Thu / Đông |
| qty_in | Nhập kho trong ngày |
| qty_out | Xuất kho trong ngày — biến mục tiêu y |
| ton_cuoi_ngay | Tồn cuối ngày = tồn cuối ngày trước + qty_in − qty_out |
| bao_lu_muc_do | 0 nếu không có bão; 0,3–1,0 trong khoảng 3 ngày trước đến 14 ngày sau mỗi cơn bão (mức độ giả định). Dùng làm biến ngoại sinh, nhưng nhớ ngoài đời chỉ biết trước 3–5 ngày. |
| het_hang | 1 nếu hết hàng, xuất ít hơn nhu cầu thật (qty_out bị chặn bởi tồn kho) |
| khuyen_mai | 1 nếu SKU đang khuyến mãi |
| la_ngay_nghi | 1 nếu kho đóng cửa |
| trong_tuan_tet | 1 nếu thuộc kỳ nghỉ Tết |
| TỪ ĐIỂN — SKU_master |  |
| gia_von / gia_ban | VNĐ / đơn vị |
| nhu_cau_tb_ngay | Nhu cầu TB/ngày cả năm (tham số sinh dữ liệu) |
| lead_time_tb / lead_time_std | Thời gian giao hàng của NCC (ngày): TB và độ lệch chuẩn |
| chi_phi_dat_hang | S — VNĐ mỗi lần đặt |
| ty_le_chi_phi_luu_kho | h — %/năm trên giá vốn, H = h × gia_von |
| moq | Số lượng đặt tối thiểu |
| phan_loai_ABC | A ≤75% giá trị xuất tích lũy, B đến 92%, C còn lại |
| cv_theo_thang / phan_loai_XYZ | CV của tổng xuất theo tháng; X ≤0,5 · Y ≤1,0 · Z >1,0 (hàng mùa vụ thường là Z) |
| ĐẶC TÍNH ĐÃ MÔ PHỎNG | BÃO LŨ 3 pha: mua tích trữ 3 ngày trước bão (mì gói, nước, pin, nến, đèn pin, đồ hộp), cứu trợ 10 ngày sau (nước, mì, thuốc khử khuẩn, bạt, găng tay, chăn), giao hàng chậm và kho đóng cửa khi bão Yagi (7–8/9/2024); hàng quà tặng, trang trí, kem giảm. · Xu hướng năm · chu kỳ tuần (T7 cao, CN thấp) · mùa hè (kem, quạt, kem chống nắng) · mùa mưa (áo mưa, dù, nhang muỗi) · mùa đông (chăn, máy sưởi, lẩu, trà gừng) · đỉnh trước lễ rồi tụt sau lễ (Tết, Trung thu, 14/2, 8/3, 1/6, 30/4–2/9, khai giảng, 20/10, Halloween, 20/11, Noel) · nhóm hàng CHỈ bán dịp lễ (mứt Tết, bánh trung thu, cây thông Noel…) gần như không bán ngoài mùa · khuyến mãi theo SKU · 11.11, 12.12, Black Friday · chính sách đặt hàng theo dự báo có lệch nên có lúc hết hàng (~1,8% ngày) và có hàng tồn dư không bán được sau mùa. |

## Sheet: Ly_do_tang_dot_bien

| nhom_ly_do | loai | hang_bi_anh_huong | dau_hieu_nhan_biet | cach_dua_vao_mo_hinh | noi_xem_trong_file |
|---|---|---|---|---|---|
| 1. Bão, lũ, ngập | Thiên tai | Mì gói, nước suối/khoáng, gạo, đồ hộp, lương khô, pin, nến, đèn pin, bật lửa, áo mưa; sau bão: khử khuẩn, bạt, găng tay, chăn, thuốc, ORS | Có cảnh báo của khí tượng thủy văn 3–5 ngày trước; ngay sau bão đơn cứu trợ tăng; giao hàng chậm | Biến ngoại sinh (mức độ bão), cửa sổ −3…+14 ngày; chặn lead time dài; không dùng ngày bão để huấn luyện mùa vụ thường | Bảng Lich_su_kien, cột bao_lu_muc_do |
| 2. Rét đậm, rét hại | Thời tiết | Chăn, máy sưởi, miếng dán nhiệt, đồ lẩu, trà gừng, khăn len | Dự báo nhiệt độ dưới 13°C kéo dài 3 ngày | Biến nhiệt độ hoặc cờ rét đậm; dùng Prophet extra_regressor | Su_kien_dot_bien: ret_dam |
| 3. Nắng nóng kỷ lục | Thời tiết | Nước suối, đá, kem, quạt, nước giải khát, kem chống nắng | Nhiệt độ trên 37°C, đỉnh hè | Biến nhiệt độ; xem như mùa vụ cộng thêm | Su_kien_dot_bien: nang_nong |
| 4. Tin đồn tăng giá, khan hàng, tích trữ | Tâm lý thị trường | Dầu ăn, đường, gạo, muối, bột giặt | Tin từ mạng xã hội, thông báo tăng giá của nhà cung cấp; sau đó nhu cầu tụt vì đã mua trước | Cờ sự kiện + biến "sau sự kiện" (dip); đừng tin chuỗi sau đó là xu hướng | Su_kien_dot_bien: tin_don_gia |
| 5. Dịch bệnh theo mùa | Y tế | Khẩu trang, nước rửa tay, dầu gió, ORS, trà gừng, bình xịt muỗi (sốt xuất huyết) | Báo cáo của ngành y tế, cao điểm cúm tháng 11–1, sốt xuất huyết tháng 8–10 | Cờ sự kiện dài nhiều tuần; nhóm hàng y tế nên gắn mùa dịch | Su_kien_dot_bien: dich_cum, sot_xuat_huyet |
| 6. Khuyến mãi lớn, sale đôi ngày (6.6, 9.9, 11.11, 12.12, Black Friday) | Thương mại | Hầu hết hàng tiêu dùng, nhất là đồ uống, mỹ phẩm, điện gia dụng | Lịch sale của sàn và chuỗi bán lẻ, thông báo của khách hàng lớn | Biến holidays có upper_window ngắn; sau sale thường có dip | Cột khuyen_mai; sự kiện trong code |
| 7. Sự kiện thể thao (Euro, World Cup, AFF Cup, SEA Games) | Sự kiện | Bia, snack, nước ngọt, hạt dưa, đồ nhắm | Lịch thi đấu, nhất là các trận Việt Nam | Cờ cửa sổ theo giải; có thể thêm cờ ngày có trận của Việt Nam | Su_kien_dot_bien: Thể thao |
| 8. Đơn B2B đột biến (tiệc cưới, tất niên, khai trương điểm bán, đơn dự án) | Khách hàng | Đồ uống thùng, mì, bánh kẹo, sữa, văn phòng phẩm | Đơn lớn bất thường của một khách, một đến hai ngày | Phát hiện ngoại lai (IQR/z-score) rồi quyết định giữ hay loại; không gán nhầm là mùa vụ | Su_kien_dot_bien: Đơn B2B đột biến |
| 9. Đứt gãy cung ứng, nhà cung cấp giao chậm, tắc cảng | Chuỗi cung ứng | Mọi SKU của nhà cung cấp đó | Thông báo trễ hàng, lead time thực tế vượt kế hoạch | Theo dõi lead time thực tế; tăng Safety Stock; hiệu ứng roi da khi hàng về dồn dập | Su_kien_dot_bien: Đứt gãy cung ứng |
| 10. Đối thủ hoặc kênh khác hết hàng | Cạnh tranh | Hàng đang thiếu ở nơi khác | Khách bất ngờ chuyển đơn sang kho của bạn | Chưa mô phỏng; nên hỏi bộ phận bán hàng | — |
| 11. Chính sách thuế, giá, an toàn thực phẩm | Chính sách | Hàng chịu thuế VAT, xăng dầu, thực phẩm | Quyết định giảm hoặc tăng thuế, giá trần, thu hồi sản phẩm | Cờ sự kiện + ngày hiệu lực; mua trước ngày tăng giá, sụt sau đó | Chưa mô phỏng |
| 12. Thưởng Tết, lương tháng 13, mùa cưới | Thu nhập | Quà tặng, đồ uống, bánh kẹo, điện máy | Tháng 1–2 (thưởng Tết); tháng 10–12 và 3–4 (cưới) | Đã nằm trong mùa vụ năm; thêm biến mùa cưới nếu có dữ liệu | Chủ yếu qua Tết |
| 13. Mở thêm điểm bán, chương trình trưng bày, đổi bao bì | Nội bộ công ty | SKU của chương trình | Thông báo của bộ phận bán hàng | Biến chương trình; dịch chuyển mức (level shift) | Chưa mô phỏng |
| 14. Lỗi dữ liệu, ghi nhận trễ, nhập sai | Chất lượng dữ liệu | Mọi SKU | Giá trị gấp 10 hoặc 100 lần, dòng trùng, ngày nhập bù | Làm sạch ở bước 1; đối chiếu nhật ký lỗi | File THO và Nhat_ky_loi |

## Sheet: Ngay_nghi_kho

| date | ten_ngay_nghi |
|---|---|
| 2024-01-01 00:00:00 | Tết Dương lịch |
| 2024-02-09 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-10 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-11 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-12 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-13 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-14 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-02-15 00:00:00 | Nghỉ Tết Nguyên đán |
| 2024-04-18 00:00:00 | Giỗ Tổ Hùng Vương |
| 2024-04-30 00:00:00 | Giải phóng miền Nam |
| 2024-05-01 00:00:00 | Quốc tế Lao động |
| 2024-09-02 00:00:00 | Quốc khánh |
| 2024-09-07 00:00:00 | Đóng cửa do bão Yagi |
| 2024-09-08 00:00:00 | Đóng cửa do bão Yagi |
| 2025-01-01 00:00:00 | Tết Dương lịch |
| 2025-01-28 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-01-29 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-01-30 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-01-31 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-02-01 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-02-02 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-02-03 00:00:00 | Nghỉ Tết Nguyên đán |
| 2025-04-07 00:00:00 | Giỗ Tổ Hùng Vương |
| 2025-04-30 00:00:00 | Giải phóng miền Nam |
| 2025-05-01 00:00:00 | Quốc tế Lao động |
| 2025-09-02 00:00:00 | Quốc khánh |
| 2026-01-01 00:00:00 | Tết Dương lịch |
| 2026-02-16 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-17 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-18 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-19 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-20 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-21 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-02-22 00:00:00 | Nghỉ Tết Nguyên đán |
| 2026-04-26 00:00:00 | Giỗ Tổ Hùng Vương |
| 2026-04-30 00:00:00 | Giải phóng miền Nam |
| 2026-05-01 00:00:00 | Quốc tế Lao động |
| 2026-09-02 00:00:00 | Quốc khánh |

## Sheet: Lich_su_kien

| holiday | ds | lower_window | upper_window | ghi_chu |
|---|---|---|---|---|
| phu_nu_vn | 2023-10-20 00:00:00 | -8 | 1 | Phụ nữ Việt Nam 20/10 |
| halloween | 2023-10-31 00:00:00 | -12 | 1 | Halloween 31/10 |
| nha_giao | 2023-11-20 00:00:00 | -8 | 1 | Ngày Nhà giáo 20/11 |
| dich_cum | 2023-12-04 00:00:00 | 0 | 41 | Đợt cúm, bệnh hô hấp (Mô phỏng) |
| noel | 2023-12-24 00:00:00 | -20 | 1 | Giáng sinh 24/12 |
| ret_dam | 2024-01-21 00:00:00 | 0 | 7 | Rét đậm, rét hại (Mô phỏng) |
| tet | 2024-02-10 00:00:00 | -28 | 7 | Tết Nguyên đán (mùng 1, âm lịch) |
| valentine | 2024-02-14 00:00:00 | -10 | 1 | Valentine 14/2 |
| quoc_te_phu_nu | 2024-03-08 00:00:00 | -10 | 1 | Quốc tế Phụ nữ 8/3 |
| le_30_4_2_9 | 2024-04-30 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| nang_nong | 2024-05-01 00:00:00 | 0 | 9 | Nắng nóng diện rộng (Mô phỏng) |
| tin_don_gia | 2024-05-13 00:00:00 | 0 | 6 | Tin đồn tăng giá, tích trữ (Mô phỏng) |
| thieu_nhi | 2024-06-01 00:00:00 | -10 | 1 | Quốc tế Thiếu nhi 1/6 |
| the_thao | 2024-06-14 00:00:00 | 0 | 30 | Euro 2024 (lịch thi đấu chính thức) |
| nang_nong | 2024-06-18 00:00:00 | 0 | 9 | Nắng nóng diện rộng (Mô phỏng) |
| sot_xuat_huyet | 2024-08-05 00:00:00 | 0 | 69 | Cao điểm sốt xuất huyết (Mô phỏng) |
| le_30_4_2_9 | 2024-09-02 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| khai_giang | 2024-09-05 00:00:00 | -22 | 1 | Khai giảng năm học 5/9 |
| bao_yagi_2024 | 2024-09-07 00:00:00 | -3 | 14 | Bão số 3 Yagi (Thực tế (ngày); mức độ giả định) |
| trung_thu | 2024-09-17 00:00:00 | -25 | 1 | Tết Trung thu (rằm tháng 8) |
| phu_nu_vn | 2024-10-20 00:00:00 | -8 | 1 | Phụ nữ Việt Nam 20/10 |
| halloween | 2024-10-31 00:00:00 | -12 | 1 | Halloween 31/10 |
| nha_giao | 2024-11-20 00:00:00 | -8 | 1 | Ngày Nhà giáo 20/11 |
| dich_cum | 2024-12-02 00:00:00 | 0 | 41 | Đợt cúm, bệnh hô hấp (Mô phỏng) |
| the_thao | 2024-12-08 00:00:00 | 0 | 28 | AFF Cup 2024 (lịch thi đấu chính thức) |
| ret_dam | 2024-12-14 00:00:00 | 0 | 7 | Rét đậm, rét hại (Mô phỏng) |
| noel | 2024-12-24 00:00:00 | -20 | 1 | Giáng sinh 24/12 |
| ret_dam | 2025-01-08 00:00:00 | 0 | 7 | Rét đậm, rét hại (Mô phỏng) |
| tet | 2025-01-29 00:00:00 | -28 | 7 | Tết Nguyên đán (mùng 1, âm lịch) |
| valentine | 2025-02-14 00:00:00 | -10 | 1 | Valentine 14/2 |
| quoc_te_phu_nu | 2025-03-08 00:00:00 | -10 | 1 | Quốc tế Phụ nữ 8/3 |
| tin_don_gia | 2025-03-10 00:00:00 | 0 | 6 | Tin đồn tăng giá, tích trữ (Mô phỏng) |
| le_30_4_2_9 | 2025-04-30 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| nang_nong | 2025-05-20 00:00:00 | 0 | 8 | Nắng nóng diện rộng (Mô phỏng) |
| thieu_nhi | 2025-06-01 00:00:00 | -10 | 1 | Quốc tế Thiếu nhi 1/6 |
| bao_wipha_2025 | 2025-07-22 00:00:00 | -3 | 14 | Bão số 3 Wipha (Thực tế (ngày); mức độ giả định) |
| sot_xuat_huyet | 2025-08-04 00:00:00 | 0 | 69 | Cao điểm sốt xuất huyết (Mô phỏng) |
| bao_kajiki_2025 | 2025-08-25 00:00:00 | -3 | 14 | Bão số 5 Kajiki (Thực tế (cuối tháng 8); mức độ giả định) |
| le_30_4_2_9 | 2025-09-02 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| khai_giang | 2025-09-05 00:00:00 | -22 | 1 | Khai giảng năm học 5/9 |
| bao_ragasa_2025 | 2025-09-25 00:00:00 | -3 | 14 | Bão số 9 Ragasa (Thực tế (ngày); mức độ giả định) |
| bao_bualoi_2025 | 2025-09-29 00:00:00 | -3 | 14 | Bão số 10 Bualoi (Thực tế (ngày); mức độ giả định) |
| trung_thu | 2025-10-06 00:00:00 | -25 | 1 | Tết Trung thu (rằm tháng 8) |
| bao_matmo_2025 | 2025-10-06 00:00:00 | -3 | 14 | Bão số 11 Matmo (Thực tế (ngày); mức độ giả định) |
| phu_nu_vn | 2025-10-20 00:00:00 | -8 | 1 | Phụ nữ Việt Nam 20/10 |
| bao_trung_2025 | 2025-10-23 00:00:00 | -3 | 14 | Bão số 12 và lũ miền Trung (Thực tế (ngày); mức độ giả định) |
| halloween | 2025-10-31 00:00:00 | -12 | 1 | Halloween 31/10 |
| bao_kalmaegi_2025 | 2025-11-06 00:00:00 | -3 | 14 | Bão số 13 Kalmaegi (Thực tế (ngày); mức độ giả định) |
| tin_don_gia | 2025-11-17 00:00:00 | 0 | 6 | Tin đồn tăng giá, tích trữ (Mô phỏng) |
| nha_giao | 2025-11-20 00:00:00 | -8 | 1 | Ngày Nhà giáo 20/11 |
| dich_cum | 2025-11-24 00:00:00 | 0 | 41 | Đợt cúm, bệnh hô hấp (Mô phỏng) |
| bao_koto_2025 | 2025-12-03 00:00:00 | -3 | 14 | Bão số 15 Koto (Thực tế (ngày); mức độ giả định) |
| ret_dam | 2025-12-18 00:00:00 | 0 | 9 | Rét đậm, rét hại (Mô phỏng) |
| noel | 2025-12-24 00:00:00 | -20 | 1 | Giáng sinh 24/12 |
| ret_dam | 2026-01-10 00:00:00 | 0 | 7 | Rét đậm, rét hại (Mô phỏng) |
| valentine | 2026-02-14 00:00:00 | -10 | 1 | Valentine 14/2 |
| tet | 2026-02-17 00:00:00 | -28 | 7 | Tết Nguyên đán (mùng 1, âm lịch) |
| quoc_te_phu_nu | 2026-03-08 00:00:00 | -10 | 1 | Quốc tế Phụ nữ 8/3 |
| le_30_4_2_9 | 2026-04-30 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| thieu_nhi | 2026-06-01 00:00:00 | -10 | 1 | Quốc tế Thiếu nhi 1/6 |
| the_thao | 2026-06-11 00:00:00 | 0 | 38 | World Cup 2026 (lịch thi đấu chính thức) |
| nang_nong | 2026-06-20 00:00:00 | 0 | 10 | Nắng nóng diện rộng (Mô phỏng) |
| le_30_4_2_9 | 2026-09-02 00:00:00 | -7 | 1 | Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp) |
| khai_giang | 2026-09-05 00:00:00 | -22 | 1 | Khai giảng năm học 5/9 |
| trung_thu | 2026-09-25 00:00:00 | -25 | 1 | Tết Trung thu (rằm tháng 8) |