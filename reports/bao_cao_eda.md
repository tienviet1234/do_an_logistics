# Bao cao phan tich kham pha (EDA)

Dữ liệu mô phỏng, không phải số liệu kho thật. Hinh luu o `reports/eda/`.

## Hinh
- `h01_tong_xuat_theo_ngay.png`: tổng xuất theo ngày (bỏ ngày kho đóng cửa): đỉnh lớn nhất trước Tết, đỉnh phụ tháng 9–10 (Trung thu, khai giảng, bão), Chủ nhật tụt rõ.
- `h02_sku_dai_dien.png`: 6 SKU đại diện cho các kiểu nhu cầu: ổn định, mùa vụ dịp lễ, tăng khi bão, rời rạc.
- `h03_chu_ky_tuan.png`: thứ Bảy cao nhất (1,16), Chủ nhật thấp nhất (0,53) → cần biến thứ trong tuần / chu kỳ 7 ngày.
- `h04_chi_so_mua.png`: nhóm hàng xếp theo độ chênh giữa các mùa; cam = bán nhiều hơn TB, xanh = bán ít hơn.
- `h05_phan_ra_mua_vu.png`: xu hướng gần như đi ngang (dao động 7.103–7.815 đơn vị/ngày, các chỗ lõm do bão và Tết lệch ngày); mùa vụ năm rõ: đỉnh trước Tết, Trung thu, Noel; phần dư lớn ở các tuần Tết (Tết âm lịch đổi ngày mỗi năm) → cần biến ngày lễ, không chỉ chu kỳ 52 tuần.
- `h06_ma_tran_abc_xyz.png`: A-X 20 SKU (dễ dự báo, giá trị cao), A-Z 5 SKU (giá trị cao nhưng khó dự báo: ưu tiên mô hình AI).
- `h07_adi_cv2.png`: phần lớn SKU bán hằng ngày (ADI < 1,32); nhóm lumpy cần Croston/TSB.
- `h08_tac_dong_khuyen_mai.png`: so trong cùng tháng: trung vị khuyến mãi làm bán tăng 60% (4 SKU dưới 1,0); biến khuyến mãi cần có trong mô hình.

## Thong ke mo ta
- `thong_ke_mo_ta.csv`: TB, do lech chuan, min, max, ty le ngay ban 0 cua tung SKU (ngay kho mo cua).
- TB xuat/ngay moi SKU: tu 4.1 den 372.9; ty le ngay ban 0 cao nhat: 60.9%
