# So sanh chinh sach ton kho (GD F, buoc 2: test)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, quy tac luong dat **eoq** (chon tren validation2), muc phuc vu chinh 95%. Du lieu mo phong.
Hien trang: nguoi lap ke hoach trong du lieu biet truoc nhu cau ky vong (lech +-10%) -> doi thu manh hon thuc te.

## Toan kho (95%)

| ma_chinh_sach          |   fill_rate_pt |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   so_lan_nhap |   chi_phi_dat_trieu |   chi_phi_luu_trieu |   tong_chi_phi_trieu |   doanh_thu_mat_trieu |   loi_nhuan_mat_trieu |   chi_phi_lien_quan_trieu |
|:-----------------------|---------------:|--------------------:|-------------------:|--------------:|--------------------:|--------------------:|---------------------:|----------------------:|----------------------:|--------------------------:|
| hien_trang             |          93.57 |                1564 |            11993.6 |          1910 |               320.8 |              2446   |               2766.8 |               22016.2 |                3693.3 |                    6460.1 |
| cong_thuc_du_bao_ai_hc |          95.91 |                 752 |            16377.3 |          3035 |               504.3 |              3217.4 |               3721.7 |               18652.2 |                2951   |                    6672.7 |
| cong_thuc_du_bao_ai    |          94.29 |                 880 |            13982.9 |          3081 |               511.2 |              2759.7 |               3270.9 |               22049.1 |                3551.9 |                    6822.8 |
| cong_thuc_du_bao_moc   |          88.83 |                1050 |            15808.5 |          3085 |               511.9 |              3192.5 |               3704.3 |               34163.8 |                5603.6 |                    9307.9 |

## Theo nhom XYZ (95%)

| xyz_train   | ma_chinh_sach          |   fill_rate_pt |   ton_tb_trieu |   loi_nhuan_mat_trieu |
|:------------|:-----------------------|---------------:|---------------:|----------------------:|
| X           | cong_thuc_du_bao_ai    |           95.2 |         3652.9 |                2536.6 |
| X           | cong_thuc_du_bao_ai_hc |           95.3 |         3705.5 |                2501.9 |
| X           | cong_thuc_du_bao_moc   |           95.3 |         4199.1 |                2553.4 |
| X           | hien_trang             |           93.8 |         5180.2 |                2749.6 |
| Y           | cong_thuc_du_bao_ai    |           97.4 |          512.5 |                 155.3 |
| Y           | cong_thuc_du_bao_ai_hc |           97.9 |          536.4 |                 142.6 |
| Y           | cong_thuc_du_bao_moc   |           95.7 |          706.2 |                 245.3 |
| Y           | hien_trang             |           97.9 |          473   |                 138.6 |
| Z           | cong_thuc_du_bao_ai    |           91   |         9817.5 |                 859.9 |
| Z           | cong_thuc_du_bao_ai_hc |           97.1 |        12135.5 |                 306.5 |
| Z           | cong_thuc_du_bao_moc   |           69.5 |        10903.2 |                2804.9 |
| Z           | hien_trang             |           91.9 |         6340.5 |                 805   |

## Do nhay theo muc phuc vu

| ma_chinh_sach          |   muc_phuc_vu |   fill_rate_pt |   ton_tb_trieu_vnd |   chi_phi_lien_quan_trieu |
|:-----------------------|--------------:|---------------:|-------------------:|--------------------------:|
| cong_thuc_du_bao_ai_hc |          0.9  |          94.72 |            15192.6 |                    7093.3 |
| cong_thuc_du_bao_ai    |          0.9  |          93.12 |            13036.3 |                    7404.2 |
| cong_thuc_du_bao_moc   |          0.9  |          87.54 |            14274.9 |                    9760.8 |
| cong_thuc_du_bao_ai_hc |          0.95 |          95.91 |            16377.3 |                    6672.7 |
| cong_thuc_du_bao_ai    |          0.95 |          94.29 |            13982.9 |                    6822.8 |
| cong_thuc_du_bao_moc   |          0.95 |          88.83 |            15808.5 |                    9307.9 |
| cong_thuc_du_bao_ai    |          0.99 |          95.93 |            15800.4 |                    6120.4 |
| cong_thuc_du_bao_ai_hc |          0.99 |          97.02 |            18704.9 |                    6286.8 |
| cong_thuc_du_bao_moc   |          0.99 |          91.09 |            18851.8 |                    8711.4 |
