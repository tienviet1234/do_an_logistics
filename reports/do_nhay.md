# Thu do nhay chinh sach ton kho (GD F bo sung)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, muc phuc vu 95%, quy tac luong dat **eoq**. Kich ban theo `docs/07`. Du lieu mo phong. Kich ban goc trung khop ket qua GD F (da kiem tra trong script).
Hien trang* chi so duoc o kich ban chi phi (don lay tu du lieu, khong chay lai duoc khi lead time doi).

## 1. Kich ban goc

| ma_chinh_sach             |   fill_rate |   ngay_thieu |   ton_tb |    cplq |
|:--------------------------|------------:|-------------:|---------:|--------:|
| Du bao moc                |       88.83 |         1050 |  15808.5 | 9307.91 |
| AI                        |       94.29 |          880 |  13982.9 | 6822.76 |
| AI + hieu chinh (de xuat) |       95.91 |          752 |  16377.3 | 6672.73 |
| Hien trang*               |       93.57 |         1564 |  11993.6 | 6460.06 |

## 2. Tac cang 3 tuan (nguoi lap ke hoach khong biet truoc)

13 dot, moi dot bat dau cach nhau 4 tuan; bang ghi trung binh tren 13 dot va dot xau nhat. `doi_*`: so voi kich ban goc (Fill Rate: diem %, chi phi lien quan: %).

|   tre_them_ngay | chinh_sach                |   fill_rate_tb |   doi_fill_rate_tb_diem |   doi_fill_rate_xau_nhat_diem | dot_xau_nhat   |   doi_cp_lien_quan_tb_pt |   doi_cp_lien_quan_xau_nhat_pt |
|----------------:|:--------------------------|---------------:|------------------------:|------------------------------:|:---------------|-------------------------:|-------------------------------:|
|               3 | AI                        |          93.74 |                   -0.55 |                         -0.94 | 2026-09-02     |                     5.75 |                          11.68 |
|               3 | AI + hieu chinh (de xuat) |          95.4  |                   -0.5  |                         -0.92 | 2026-09-02     |                     5.41 |                          11.65 |
|               3 | Du bao moc                |          88.4  |                   -0.44 |                         -1.11 | 2026-06-10     |                     3.28 |                           8.63 |
|               5 | AI                        |          93.24 |                   -1.05 |                         -1.84 | 2026-01-21     |                    10.72 |                          18.87 |
|               5 | AI + hieu chinh (de xuat) |          94.9  |                   -1    |                         -1.61 | 2026-01-21     |                    10.2  |                          19.66 |
|               5 | Du bao moc                |          88.01 |                   -0.82 |                         -1.86 | 2026-06-10     |                     6.37 |                          14.54 |
|               7 | AI                        |          92.74 |                   -1.55 |                         -2.76 | 2026-01-21     |                    15.55 |                          28.28 |
|               7 | AI + hieu chinh (de xuat) |          94.37 |                   -1.53 |                         -2.88 | 2026-01-21     |                    15.31 |                          27.39 |
|               7 | Du bao moc                |          87.59 |                   -1.24 |                         -2.23 | 2026-06-10     |                     9.3  |                          17.75 |

So dot moi chinh sach co chi phi lien quan thap nhat (trong 3 chinh sach theo cong thuc):

- Tre them 3 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 5 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 7 ngay: AI + hieu chinh (de xuat) 13/13

Dot truoc Tet (hang du kien ve 2026-01-21 tro di, Tet 17/02/2026):

|   k | chinh_sach                |   fill_rate_pt |   d_fr |   so_ngay_sku_thieu |   chi_phi_lien_quan_trieu |   d_cp |
|----:|:--------------------------|---------------:|-------:|--------------------:|--------------------------:|-------:|
|   3 | AI                        |          93.5  |  -0.79 |                 985 |                    7188.7 |   5.36 |
|   3 | AI + hieu chinh (de xuat) |          95.16 |  -0.75 |                 862 |                    7089   |   6.24 |
|   3 | Du bao moc                |          88.42 |  -0.41 |                1139 |                    9654.4 |   3.72 |
|   5 | AI                        |          92.45 |  -1.84 |                1116 |                    7739.2 |  13.43 |
|   5 | AI + hieu chinh (de xuat) |          94.3  |  -1.61 |                 999 |                    7586.4 |  13.69 |
|   5 | Du bao moc                |          87.91 |  -0.92 |                1258 |                   10061.5 |   8.1  |
|   7 | AI                        |          91.53 |  -2.76 |                1283 |                    8280.5 |  21.37 |
|   7 | AI + hieu chinh (de xuat) |          93.03 |  -2.88 |                1141 |                    8260.1 |  23.79 |
|   7 | Du bao moc                |          87.25 |  -1.58 |                1397 |                   10450.8 |  12.28 |

## 3. Lead time dai them 2 ngay ca nam

| ma_kich_ban          | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:---------------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| lead_time_2          | AI                        |          89.11 |                -5.18 |                1909 |            12930.4 |           -7.53 |          2952 |                   10456.1 |                 53.25 |
| lead_time_2          | AI + hieu chinh (de xuat) |          90.8  |                -5.11 |                1717 |            15610.9 |           -4.68 |          2914 |                   10117.4 |                 51.62 |
| lead_time_2          | Du bao moc                |          84.38 |                -4.45 |                1992 |            14526.4 |           -8.11 |          2942 |                   12141.5 |                 30.44 |
| lead_time_2_cap_nhat | AI                        |          93.3  |                -0.99 |                1009 |            14819.9 |            5.99 |          3074 |                    7437.5 |                  9.01 |
| lead_time_2_cap_nhat | AI + hieu chinh (de xuat) |          94.83 |                -1.08 |                 870 |            18025.2 |           10.06 |          3000 |                    7297.5 |                  9.36 |
| lead_time_2_cap_nhat | Du bao moc                |          88.3  |                -0.53 |                1207 |            17739.3 |           12.21 |          3055 |                   10174.4 |                  9.31 |

## 4. Chi phi tang (co hien trang)

| ma_kich_ban     | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:----------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| chi_phi_dat_120 | AI                        |          93.98 |                -0.31 |                 873 |            14502.3 |            3.71 |          2847 |                    6891   |                  1    |
| chi_phi_dat_120 | AI + hieu chinh (de xuat) |          95.93 |                 0.02 |                 735 |            16649.6 |            1.66 |          2799 |                    6556.4 |                 -1.74 |
| chi_phi_dat_120 | Du bao moc                |          88.97 |                 0.14 |                1028 |            16278.2 |            2.97 |          2863 |                    9363.3 |                  0.6  |
| chi_phi_dat_120 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6524.2 |                  0.99 |
| chi_phi_luu_115 | AI                        |          94.19 |                -0.1  |                 890 |            13821.4 |           -1.16 |          3275 |                    7329.9 |                  7.43 |
| chi_phi_luu_115 | AI + hieu chinh (de xuat) |          95.63 |                -0.28 |                 793 |            16445   |            0.41 |          3211 |                    7283.6 |                  9.15 |
| chi_phi_luu_115 | Du bao moc                |          88.63 |                -0.2  |                1107 |            15514.6 |           -1.86 |          3269 |                    9901.9 |                  6.38 |
| chi_phi_luu_115 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6827   |                  5.68 |

