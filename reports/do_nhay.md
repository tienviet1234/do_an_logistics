# Thu do nhay chinh sach ton kho (GD F bo sung)

12 thang test (2025-10-01 .. 2026-09-29), 121 SKU, muc phuc vu 95%, quy tac luong dat **lai**. Kich ban theo `docs/07`. Du lieu mo phong. Kich ban goc trung khop ket qua GD F (da kiem tra trong script).
Hien trang* chi so duoc o kich ban chi phi (don lay tu du lieu, khong chay lai duoc khi lead time doi).

## 1. Kich ban goc

| ma_chinh_sach             |   fill_rate |   ngay_thieu |   ton_tb |    cplq |
|:--------------------------|------------:|-------------:|---------:|--------:|
| Du bao moc                |       91.69 |          916 | 19669.7  | 9011    |
| AI                        |       95.33 |          793 |  9208.73 | 5329.6  |
| AI + hieu chinh (de xuat) |       95.82 |          735 | 11906    | 5828.15 |
| Hien trang*               |       93.57 |         1564 | 11993.6  | 6460.06 |

## 2. Tac cang 3 tuan (nguoi lap ke hoach khong biet truoc)

13 dot, moi dot bat dau cach nhau 4 tuan; bang ghi trung binh tren 13 dot va dot xau nhat. `doi_*`: so voi kich ban goc (Fill Rate: diem %, chi phi lien quan: %).

|   tre_them_ngay | chinh_sach                |   fill_rate_tb |   doi_fill_rate_tb_diem |   doi_fill_rate_xau_nhat_diem | dot_xau_nhat   |   doi_cp_lien_quan_tb_pt |   doi_cp_lien_quan_xau_nhat_pt |
|----------------:|:--------------------------|---------------:|------------------------:|------------------------------:|:---------------|-------------------------:|-------------------------------:|
|               3 | AI                        |          94.76 |                   -0.57 |                         -1.1  | 2026-09-02     |                     7.72 |                          15.54 |
|               3 | AI + hieu chinh (de xuat) |          95.33 |                   -0.49 |                         -0.9  | 2026-09-02     |                     5.84 |                          12.68 |
|               3 | Du bao moc                |          91.25 |                   -0.43 |                         -1.09 | 2026-06-10     |                     3.12 |                           9.32 |
|               5 | AI                        |          94.28 |                   -1.05 |                         -1.82 | 2026-01-21     |                    14.11 |                          24.28 |
|               5 | AI + hieu chinh (de xuat) |          94.84 |                   -0.97 |                         -1.71 | 2026-09-02     |                    11.7  |                          19.77 |
|               5 | Du bao moc                |          90.83 |                   -0.86 |                         -1.87 | 2026-06-10     |                     6.37 |                          15.82 |
|               7 | AI                        |          93.69 |                   -1.64 |                         -2.98 | 2026-01-21     |                    21.32 |                          35.39 |
|               7 | AI + hieu chinh (de xuat) |          94.3  |                   -1.52 |                         -2.5  | 2026-01-21     |                    17.69 |                          29.57 |
|               7 | Du bao moc                |          90.39 |                   -1.29 |                         -2.46 | 2026-06-10     |                     9.64 |                          20.46 |

So dot moi chinh sach co chi phi lien quan thap nhat (trong 3 chinh sach theo cong thuc):

- Tre them 3 ngay: AI 13/13
- Tre them 5 ngay: AI 13/13
- Tre them 7 ngay: AI 12/13, AI + hieu chinh (de xuat) 1/13

Dot truoc Tet (hang du kien ve 2026-01-21 tro di, Tet 17/02/2026):

|   k | chinh_sach                |   fill_rate_pt |   d_fr |   so_ngay_sku_thieu |   chi_phi_lien_quan_trieu |   d_cp |
|----:|:--------------------------|---------------:|-------:|--------------------:|--------------------------:|-------:|
|   3 | AI                        |          94.4  |  -0.93 |                 923 |                    5848.4 |   9.73 |
|   3 | AI + hieu chinh (de xuat) |          95.03 |  -0.79 |                 835 |                    6255.5 |   7.33 |
|   3 | Du bao moc                |          91.21 |  -0.48 |                 993 |                    9335   |   3.6  |
|   5 | AI                        |          93.51 |  -1.82 |                1062 |                    6600.3 |  23.84 |
|   5 | AI + hieu chinh (de xuat) |          94.33 |  -1.49 |                 947 |                    6716.4 |  15.24 |
|   5 | Du bao moc                |          90.48 |  -1.21 |                1129 |                    9722.8 |   7.9  |
|   7 | AI                        |          92.35 |  -2.98 |                1199 |                    7208.3 |  35.25 |
|   7 | AI + hieu chinh (de xuat) |          93.32 |  -2.5  |                1085 |                    7184.4 |  23.27 |
|   7 | Du bao moc                |          89.94 |  -1.75 |                1232 |                   10059.6 |  11.64 |

## 3. Lead time dai them 2 ngay ca nam

| ma_kich_ban          | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:---------------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| lead_time_2          | AI                        |          89.74 |                -5.59 |                1881 |             8308.4 |           -9.78 |          3314 |                    8953.1 |                 67.99 |
| lead_time_2          | AI + hieu chinh (de xuat) |          90.76 |                -5.06 |                1721 |            11161.7 |           -6.25 |          3050 |                    9250.4 |                 58.72 |
| lead_time_2          | Du bao moc                |          86.85 |                -4.84 |                1841 |            18292.7 |           -7    |          3441 |                   11727.2 |                 30.14 |
| lead_time_2_cap_nhat | AI                        |          94.39 |                -0.94 |                 986 |             9465.7 |            2.79 |          3449 |                    6056.1 |                 13.63 |
| lead_time_2_cap_nhat | AI + hieu chinh (de xuat) |          95.39 |                -0.43 |                 849 |            12342.1 |            3.66 |          3182 |                    6044.2 |                  3.71 |
| lead_time_2_cap_nhat | Du bao moc                |          90.89 |                -0.8  |                1025 |            21768.3 |           10.67 |          3543 |                    9727.7 |                  7.95 |

## 4. Chi phi tang (co hien trang)

| ma_kich_ban     | chinh_sach                |   fill_rate_pt |   doi_fill_rate_diem |   so_ngay_sku_thieu |   ton_tb_trieu_vnd |   doi_ton_tb_pt |   so_lan_nhap |   chi_phi_lien_quan_trieu |   doi_cp_lien_quan_pt |
|:----------------|:--------------------------|---------------:|---------------------:|--------------------:|-------------------:|----------------:|--------------:|--------------------------:|----------------------:|
| chi_phi_dat_120 | AI                        |          95.19 |                -0.14 |                 809 |             9433.2 |            2.44 |          3262 |                    5573.6 |                  4.58 |
| chi_phi_dat_120 | AI + hieu chinh (de xuat) |          95.92 |                 0.1  |                 735 |            12098.3 |            1.62 |          2990 |                    5821.2 |                 -0.12 |
| chi_phi_dat_120 | Du bao moc                |          91.73 |                 0.04 |                 910 |            19843.3 |            0.88 |          3397 |                    9065.6 |                  0.61 |
| chi_phi_dat_120 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6524.2 |                  0.99 |
| chi_phi_luu_115 | AI                        |          95.33 |                 0    |                 808 |             9050.8 |           -1.71 |          3641 |                    5600.5 |                  5.08 |
| chi_phi_luu_115 | AI + hieu chinh (de xuat) |          95.91 |                 0.09 |                 721 |            11745.1 |           -1.35 |          3372 |                    6076.2 |                  4.26 |
| chi_phi_luu_115 | Du bao moc                |          91.61 |                -0.08 |                 920 |            19503.1 |           -0.85 |          3731 |                    9640.9 |                  6.99 |
| chi_phi_luu_115 | Hien trang*               |          93.57 |                 0    |                1564 |            11993.6 |           -0    |          1910 |                    6827   |                  5.68 |

