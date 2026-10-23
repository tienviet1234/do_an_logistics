# So sanh chinh sach ton kho (GD F, buoc 2: test)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, quy tac luong dat **eoq** (chon tren validation2), muc phuc vu chinh 95%. Du lieu mo phong.
Hien trang: nguoi lap ke hoach trong du lieu biet truoc nhu cau ky vong (lech +-10%) -> doi thu manh hon thuc te.

## Toan kho (95%)

| ma_chinh_sach          |   fill_rate_pt |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   so_lan_nhap |   chi_phi_dat_trieu |   chi_phi_luu_trieu |   tong_chi_phi_trieu |   doanh_thu_mat_trieu |   loi_nhuan_mat_trieu |   chi_phi_lien_quan_trieu |
|:-----------------------|---------------:|--------------------:|-------------------:|--------------:|--------------------:|--------------------:|---------------------:|----------------------:|----------------------:|--------------------------:|
| hien_trang             |          93.57 |                1564 |            11133.7 |          1910 |               320.8 |              2275.6 |               2596.4 |               19452.7 |                3327.6 |                    5924   |
| cong_thuc_du_bao_ai_hc |          95.36 |                 758 |            15133.4 |          2924 |               487.8 |              3012.7 |               3500.4 |               14502.6 |                2479.4 |                    5979.9 |
| cong_thuc_du_bao_ai    |          93.15 |                 933 |            12673.9 |          2968 |               495   |              2533.3 |               3028.3 |               19361.7 |                3331   |                    6359.3 |
| cong_thuc_du_bao_moc   |          88.75 |                1051 |            14890.1 |          2979 |               495.9 |              3006   |               3501.9 |               30952.9 |                5148.1 |                    8650.1 |

## Theo nhom XYZ (95%)

| xyz_train   | ma_chinh_sach          |   fill_rate_pt |   ton_tb_trieu |   loi_nhuan_mat_trieu |
|:------------|:-----------------------|---------------:|---------------:|----------------------:|
| X           | cong_thuc_du_bao_ai    |           95.3 |         3379.6 |                1921   |
| X           | cong_thuc_du_bao_ai_hc |           95.6 |         3459.6 |                1746.7 |
| X           | cong_thuc_du_bao_moc   |           95.2 |         3923   |                2300.4 |
| X           | hien_trang             |           93.8 |         4542.9 |                2481.4 |
| Y           | cong_thuc_du_bao_ai    |           98.8 |          515.2 |                 126.6 |
| Y           | cong_thuc_du_bao_ai_hc |           98.2 |          548.5 |                 137.4 |
| Y           | cong_thuc_du_bao_moc   |           95.4 |          711.6 |                 265.8 |
| Y           | hien_trang             |           97.9 |          492.2 |                 140.3 |
| Z           | cong_thuc_du_bao_ai    |           85.9 |         8779.2 |                1283.4 |
| Z           | cong_thuc_du_bao_ai_hc |           94   |        11125.3 |                 595.4 |
| Z           | cong_thuc_du_bao_moc   |           69.6 |        10255.5 |                2582   |
| Z           | hien_trang             |           91.9 |         6098.6 |                 705.9 |

## Do nhay theo muc phuc vu

| ma_chinh_sach          |   muc_phuc_vu |   fill_rate_pt |   ton_tb_trieu_vnd |   chi_phi_lien_quan_trieu |
|:-----------------------|--------------:|---------------:|-------------------:|--------------------------:|
| cong_thuc_du_bao_ai_hc |          0.9  |          94.24 |            13849.8 |                    6534.7 |
| cong_thuc_du_bao_ai    |          0.9  |          92.4  |            11696.1 |                    6815.3 |
| cong_thuc_du_bao_moc   |          0.9  |          87.54 |            13388.7 |                    8934.1 |
| cong_thuc_du_bao_ai_hc |          0.95 |          95.36 |            15133.4 |                    5979.9 |
| cong_thuc_du_bao_ai    |          0.95 |          93.15 |            12673.9 |                    6359.3 |
| cong_thuc_du_bao_moc   |          0.95 |          88.75 |            14890.1 |                    8650.1 |
| cong_thuc_du_bao_ai_hc |          0.99 |          96.82 |            17084.5 |                    5548.8 |
| cong_thuc_du_bao_ai    |          0.99 |          94.98 |            14230.9 |                    5662.3 |
| cong_thuc_du_bao_moc   |          0.99 |          90.99 |            17643.6 |                    7917.1 |
