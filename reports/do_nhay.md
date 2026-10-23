# Thu do nhay chinh sach ton kho (GD F bo sung)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, muc phuc vu 95%, quy tac luong dat **eoq**. Kich ban theo `docs/07`. Du lieu mo phong. Kich ban goc trung khop ket qua GD F (da kiem tra trong script).
Hien trang* chi so duoc o kich ban chi phi (don lay tu du lieu, khong chay lai duoc khi lead time doi).

## 1. Kich ban goc

| ma_chinh_sach             |   fill_rate |   ngay_thieu |   ton_tb |    cplq |
|:--------------------------|------------:|-------------:|---------:|--------:|
| Du bao moc                |       88.75 |         1051 |  14890.1 | 8650.05 |
| AI                        |       93.15 |          933 |  12673.9 | 6359.33 |
| AI + hieu chinh (de xuat) |       95.36 |          758 |  15133.4 | 5979.88 |
| Hien trang*               |       93.57 |         1564 |  11133.7 | 5924.05 |

## 2. Tac cang 3 tuan (nguoi lap ke hoach khong biet truoc)

13 dot, moi dot bat dau cach nhau 4 tuan; bang ghi trung binh tren 13 dot va dot xau nhat. `doi_*`: so voi kich ban goc (Fill Rate: diem %, chi phi lien quan: %).

|   tre_them_ngay | chinh_sach                |   fill_rate_tb |   doi_fill_rate_tb_diem |   doi_fill_rate_xau_nhat_diem | dot_xau_nhat   |   doi_cp_lien_quan_tb_pt |   doi_cp_lien_quan_xau_nhat_pt |
|----------------:|:--------------------------|---------------:|------------------------:|------------------------------:|:---------------|-------------------------:|-------------------------------:|
|               3 | AI                        |          92.65 |                   -0.5  |                         -0.99 | 2026-06-10     |                     5    |                          13.57 |
|               3 | AI + hieu chinh (de xuat) |          94.87 |                   -0.49 |                         -1.11 | 2026-01-21     |                     5.09 |                          13.44 |
|               3 | Du bao moc                |          88.35 |                   -0.4  |                         -1.03 | 2026-06-10     |                     2.79 |                           8.89 |
|               5 | AI                        |          92.16 |                   -1    |                         -1.71 | 2026-06-10     |                     9.71 |                          22.13 |
|               5 | AI + hieu chinh (de xuat) |          94.37 |                   -0.98 |                         -2.03 | 2026-01-21     |                    10.38 |                          23.08 |
|               5 | Du bao moc                |          87.97 |                   -0.78 |                         -1.74 | 2026-06-10     |                     5.62 |                          15.23 |
|               7 | AI                        |          91.67 |                   -1.49 |                         -2.52 | 2026-01-21     |                    14.35 |                          29.37 |
|               7 | AI + hieu chinh (de xuat) |          93.87 |                   -1.49 |                         -3.17 | 2026-01-21     |                    15.22 |                          30.81 |
|               7 | Du bao moc                |          87.52 |                   -1.24 |                         -2.22 | 2026-06-10     |                     8.86 |                          18.67 |

So dot moi chinh sach co chi phi lien quan thap nhat (trong 3 chinh sach theo cong thuc):

- Tre them 3 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 5 ngay: AI + hieu chinh (de xuat) 13/13
- Tre them 7 ngay: AI + hieu chinh (de xuat) 13/13

Dot truoc Tet (hang du kien ve 2026-01-21 tro di, Tet 17/02/2026):

|   k | chinh_sach                |   fill_rate_pt |   d_fr |   so_ngay_sku_thieu |   chi_phi_lien_quan_trieu |   d_cp |
|----:|:--------------------------|---------------:|-------:|--------------------:|--------------------------:|-------:|
|   3 | AI                        |          92.58 |  -0.57 |                1035 |                    6692.8 |   5.24 |
|   3 | AI + hieu chinh (de xuat) |          94.25 |  -1.11 |                 869 |                    6439.5 |   7.69 |
|   3 | Du bao moc                |          88.3  |  -0.45 |                1137 |                    8987.1 |   3.9  |
|   5 | AI                        |          91.62 |  -1.53 |                1178 |                    7201.4 |  13.24 |
|   5 | AI + hieu chinh (de xuat) |          93.33 |  -2.03 |                 977 |                    6921   |  15.74 |
|   5 | Du bao moc                |          87.88 |  -0.87 |                1239 |                    9236   |   6.77 |
|   7 | AI                        |          90.63 |  -2.52 |                1352 |                    7689.2 |  20.91 |
|   7 | AI + hieu chinh (de xuat) |          92.19 |  -3.17 |                1126 |                    7501.6 |  25.45 |
|   7 | Du bao moc                |          87.22 |  -1.53 |                1369 |                    9605.7 |  11.05 |

## 3. Lead time dai them 2 ngay ca nam

| ma_kich_ban          | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:---------------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| lead_time_2          | AI                        |          87.61 |                -5.54 |                1948 |            11943   |           -5.77 |          2841 |                    9624.9 |                 51.35 |
| lead_time_2          | AI + hieu chinh (de xuat) |          90.1  |                -5.26 |                1701 |            14458.9 |           -4.46 |          2799 |                    9072.5 |                 51.72 |
| lead_time_2          | Du bao moc                |          84.49 |                -4.26 |                1975 |            13673.1 |           -8.17 |          2838 |                   11104   |                 28.37 |
| lead_time_2_cap_nhat | AI                        |          92.15 |                -1    |                1086 |            13676.7 |            7.91 |          2968 |                    6987.1 |                  9.87 |
| lead_time_2_cap_nhat | AI + hieu chinh (de xuat) |          94.6  |                -0.76 |                 888 |            16342.9 |            7.99 |          2912 |                    6554.7 |                  9.61 |
| lead_time_2_cap_nhat | Du bao moc                |          88.36 |                -0.39 |                1187 |            16530.5 |           11.02 |          2949 |                    9227.1 |                  6.67 |

## 4. Chi phi tang (co hien trang)

| ma_kich_ban     | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:----------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| chi_phi_dat_120 | AI                        |          93.65 |                 0.5  |                 936 |            12862.6 |            1.49 |          2744 |                    6213.2 |                 -2.3  |
| chi_phi_dat_120 | AI + hieu chinh (de xuat) |          95.12 |                -0.24 |                 791 |            15200.2 |            0.44 |          2684 |                    6074.4 |                  1.58 |
| chi_phi_dat_120 | Du bao moc                |          88.85 |                 0.1  |                1038 |            15191.9 |            2.03 |          2765 |                    8706.2 |                  0.65 |
| chi_phi_dat_120 | Hien trang*               |          93.57 |                 0    |                1564 |            11133.7 |            0    |          1910 |                    5988.2 |                  1.08 |
| chi_phi_luu_115 | AI                        |          93.32 |                 0.17 |                 912 |            12431.1 |           -1.92 |          3162 |                    6747.1 |                  6.1  |
| chi_phi_luu_115 | AI + hieu chinh (de xuat) |          95.28 |                -0.08 |                 823 |            14801.3 |           -2.19 |          3107 |                    6472.3 |                  8.23 |
| chi_phi_luu_115 | Du bao moc                |          88.61 |                -0.14 |                1134 |            14549.7 |           -2.29 |          3162 |                    9106.6 |                  5.28 |
| chi_phi_luu_115 | Hien trang*               |          93.57 |                 0    |                1564 |            11133.7 |            0    |          1910 |                    6265.4 |                  5.76 |

