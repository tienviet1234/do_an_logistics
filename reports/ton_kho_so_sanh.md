# So sanh chinh sach ton kho (GD F, buoc 2: test)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, quy tac luong dat **lai** (chon tren validation2), muc phuc vu chinh 95%. Du lieu mo phong.
Hien trang: nguoi lap ke hoach trong du lieu biet truoc nhu cau ky vong (lech +-10%) -> doi thu manh hon thuc te.

## Toan kho (95%)

| ma_chinh_sach          |   fill_rate_pt |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   so_lan_nhap |   chi_phi_dat_trieu |   chi_phi_luu_trieu |   tong_chi_phi_trieu |   doanh_thu_mat_trieu |   loi_nhuan_mat_trieu |   chi_phi_lien_quan_trieu |
|:-----------------------|---------------:|--------------------:|-------------------:|--------------:|--------------------:|--------------------:|---------------------:|----------------------:|----------------------:|--------------------------:|
| cong_thuc_du_bao_ai    |          95.33 |                 793 |             9208.7 |          3467 |               574.6 |              1852.8 |               2427.4 |               18037.5 |                2902.2 |                    5329.6 |
| cong_thuc_du_bao_ai_hc |          95.82 |                 735 |            11906   |          3192 |               529.9 |              2385.8 |               2915.7 |               18075.5 |                2912.4 |                    5828.1 |
| hien_trang             |          93.57 |                1564 |            11993.6 |          1910 |               320.8 |              2446   |               2766.8 |               22016.2 |                3693.3 |                    6460.1 |
| cong_thuc_du_bao_moc   |          91.69 |                 916 |            19669.7 |          3575 |               594.5 |              3972.4 |               4567   |               27827.4 |                4444   |                    9011   |

## Theo nhom XYZ (95%)

| xyz_train   | ma_chinh_sach          |   fill_rate_pt |   ton_tb_trieu |   loi_nhuan_mat_trieu |
|:------------|:-----------------------|---------------:|---------------:|----------------------:|
| X           | cong_thuc_du_bao_ai    |           95.6 |         3581.6 |                2287.3 |
| X           | cong_thuc_du_bao_ai_hc |           95.6 |         3663.3 |                2381.8 |
| X           | cong_thuc_du_bao_moc   |           95.6 |         4151.9 |                2509.9 |
| X           | hien_trang             |           93.8 |         5180.2 |                2749.6 |
| Y           | cong_thuc_du_bao_ai    |           98.4 |          488.9 |                 134.1 |
| Y           | cong_thuc_du_bao_ai_hc |           97.6 |          512.4 |                 140.4 |
| Y           | cong_thuc_du_bao_moc   |           96.9 |          679.6 |                 132.8 |
| Y           | hien_trang             |           97.9 |          473   |                 138.6 |
| Z           | cong_thuc_du_bao_ai    |           93.9 |         5138.3 |                 480.8 |
| Z           | cong_thuc_du_bao_ai_hc |           96.1 |         7730.3 |                 390.3 |
| Z           | cong_thuc_du_bao_moc   |           79.8 |        14838.2 |                1801.4 |
| Z           | hien_trang             |           91.9 |         6340.5 |                 805   |

## Do nhay theo muc phuc vu

| ma_chinh_sach          |   muc_phuc_vu |   fill_rate_pt |   ton_tb_trieu_vnd |   chi_phi_lien_quan_trieu |
|:-----------------------|--------------:|---------------:|-------------------:|--------------------------:|
| cong_thuc_du_bao_ai_hc |          0.9  |          95.09 |            10606.2 |                    5994.2 |
| cong_thuc_du_bao_ai    |          0.9  |          94.13 |             8222.9 |                    6011   |
| cong_thuc_du_bao_moc   |          0.9  |          90.24 |            17850.1 |                    9359.2 |
| cong_thuc_du_bao_ai    |          0.95 |          95.33 |             9208.7 |                    5329.6 |
| cong_thuc_du_bao_ai_hc |          0.95 |          95.82 |            11906   |                    5828.1 |
| cong_thuc_du_bao_moc   |          0.95 |          91.69 |            19669.7 |                    9011   |
| cong_thuc_du_bao_ai    |          0.99 |          96.3  |            11206.3 |                    5024.7 |
| cong_thuc_du_bao_ai_hc |          0.99 |          97.12 |            14312.7 |                    5376.2 |
| cong_thuc_du_bao_moc   |          0.99 |          93.9  |            23089   |                    8477.7 |
