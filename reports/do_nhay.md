# Thu do nhay chinh sach ton kho (GD F bo sung)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, muc phuc vu 95%, quy tac luong dat **eoq**. Kich ban theo `docs/07`. Du lieu mo phong. Kich ban goc trung khop ket qua GD F (da kiem tra trong script).
Hien trang* chi so duoc o kich ban chi phi (don lay tu du lieu, khong chay lai duoc khi lead time doi).

## 1. Kich ban goc

| ma_chinh_sach             |   fill_rate |   ngay_thieu |   ton_tb |    cplq |
|:--------------------------|------------:|-------------:|---------:|--------:|
| Du bao moc                |       88.83 |         1050 |  15808.5 | 9307.91 |
| AI                        |       93.16 |          916 |  13049.1 | 7079.7  |
| AI + hieu chinh (de xuat) |       95.34 |          785 |  15341   | 6538.69 |
| Hien trang*               |       93.57 |         1564 |  11993.6 | 6460.06 |

## 2. Tac cang 3 tuan (nguoi lap ke hoach khong biet truoc)

13 dot, moi dot bat dau cach nhau 4 tuan; bang ghi trung binh tren 13 dot va dot xau nhat. `doi_*`: so voi kich ban goc (Fill Rate: diem %, chi phi lien quan: %).

|   tre_them_ngay | chinh_sach                |   fill_rate_tb |   doi_fill_rate_tb_diem |   doi_fill_rate_xau_nhat_diem | dot_xau_nhat   |   doi_cp_lien_quan_tb_pt |   doi_cp_lien_quan_xau_nhat_pt |
|----------------:|:--------------------------|---------------:|------------------------:|------------------------------:|:---------------|-------------------------:|-------------------------------:|
|               3 | AI                        |          92.62 |                   -0.54 |                         -0.96 | 2026-06-10     |                     5.44 |                          11.37 |
|               3 | AI + hieu chinh (de xuat) |          94.8  |                   -0.54 |                         -1.04 | 2026-06-10     |                     5.88 |                          14.81 |
|               3 | Du bao moc                |          88.4  |                   -0.44 |                         -1.11 | 2026-06-10     |                     3.28 |                           8.63 |
|               5 | AI                        |          92.1  |                   -1.06 |                         -1.66 | 2026-01-21     |                    10.33 |                          18.91 |
|               5 | AI + hieu chinh (de xuat) |          94.32 |                   -1.03 |                         -1.99 | 2026-01-21     |                    11.1  |                          22.92 |
|               5 | Du bao moc                |          88.01 |                   -0.82 |                         -1.86 | 2026-06-10     |                     6.37 |                          14.54 |
|               7 | AI                        |          91.62 |                   -1.54 |                         -2.76 | 2026-01-21     |                    14.54 |                          25.73 |
|               7 | AI + hieu chinh (de xuat) |          93.8  |                   -1.54 |                         -3.14 | 2026-01-21     |                    15.99 |                          31.74 |
|               7 | Du bao moc                |          87.59 |                   -1.24 |                         -2.23 | 2026-06-10     |                     9.3  |                          17.75 |

So dot moi chinh sach co chi phi lien quan thap nhat (trong 3 chinh sach theo cong thuc):

- Tre them 3 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 5 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 7 ngay: AI + hieu chinh (de xuat) 13/13

Dot truoc Tet (hang du kien ve 2026-01-21 tro di, Tet 17/02/2026):

|   k | chinh_sach                |   fill_rate_pt |   d_fr |   so_ngay_sku_thieu |   chi_phi_lien_quan_trieu |   d_cp |
|----:|:--------------------------|---------------:|-------:|--------------------:|--------------------------:|-------:|
|   3 | AI                        |          92.41 |  -0.75 |                1044 |                    7616   |   7.58 |
|   3 | AI + hieu chinh (de xuat) |          94.37 |  -0.97 |                 888 |                    6967   |   6.55 |
|   3 | Du bao moc                |          88.42 |  -0.41 |                1139 |                    9654.4 |   3.72 |
|   5 | AI                        |          91.5  |  -1.66 |                1206 |                    8135.8 |  14.92 |
|   5 | AI + hieu chinh (de xuat) |          93.35 |  -1.99 |                1016 |                    7565.4 |  15.7  |
|   5 | Du bao moc                |          87.91 |  -0.92 |                1258 |                   10061.5 |   8.1  |
|   7 | AI                        |          90.4  |  -2.76 |                1348 |                    8696.4 |  22.84 |
|   7 | AI + hieu chinh (de xuat) |          92.2  |  -3.14 |                1169 |                    8132.6 |  24.38 |
|   7 | Du bao moc                |          87.25 |  -1.58 |                1397 |                   10450.8 |  12.28 |

## 3. Lead time dai them 2 ngay ca nam

| ma_kich_ban          | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:---------------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| lead_time_2          | AI                        |          87.66 |                -5.5  |                1984 |            12105.8 |           -7.23 |          2947 |                   10667.2 |                 50.67 |
| lead_time_2          | AI + hieu chinh (de xuat) |          90.01 |                -5.33 |                1766 |            14407.3 |           -6.09 |          2887 |                   10196.3 |                 55.94 |
| lead_time_2          | Du bao moc                |          84.38 |                -4.45 |                1992 |            14526.4 |           -8.11 |          2942 |                   12141.5 |                 30.44 |
| lead_time_2_cap_nhat | AI                        |          92.08 |                -1.08 |                1092 |            14040.2 |            7.59 |          3074 |                    7642.3 |                  7.95 |
| lead_time_2_cap_nhat | AI + hieu chinh (de xuat) |          94.44 |                -0.9  |                 921 |            16897.1 |           10.14 |          3011 |                    7261.5 |                 11.05 |
| lead_time_2_cap_nhat | Du bao moc                |          88.3  |                -0.53 |                1207 |            17739.3 |           12.21 |          3055 |                   10174.4 |                  9.31 |

## 4. Chi phi tang (co hien trang)

| ma_kich_ban     | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:----------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| chi_phi_dat_120 | AI                        |          93.47 |                 0.31 |                 920 |            13224.7 |            1.35 |          2854 |                    7016.4 |                 -0.89 |
| chi_phi_dat_120 | AI + hieu chinh (de xuat) |          95.02 |                -0.32 |                 800 |            15466.8 |            0.82 |          2801 |                    6629.5 |                  1.39 |
| chi_phi_dat_120 | Du bao moc                |          88.97 |                 0.14 |                1028 |            16278.2 |            2.97 |          2863 |                    9363.3 |                  0.6  |
| chi_phi_dat_120 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6524.2 |                  0.99 |
| chi_phi_luu_115 | AI                        |          93.18 |                 0.02 |                 955 |            12937.2 |           -0.86 |          3286 |                    7393.1 |                  4.43 |
| chi_phi_luu_115 | AI + hieu chinh (de xuat) |          95.38 |                 0.04 |                 805 |            15169.4 |           -1.12 |          3212 |                    7014   |                  7.27 |
| chi_phi_luu_115 | Du bao moc                |          88.63 |                -0.2  |                1107 |            15514.6 |           -1.86 |          3269 |                    9901.9 |                  6.38 |
| chi_phi_luu_115 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6827   |                  5.68 |

