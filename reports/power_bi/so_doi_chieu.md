# So doi chieu cho Power BI

Sinh tu dong boi `python src/xuat_power_bi.py`, tinh tu chinh cac file CSV vua xuat va da doi chieu voi CSDL (lech thi script dung lai bao loi). Dung trang Power BI xong, so tren trang phai ra dung cac so duoi day. Du lieu mo phong.

## 1. So dong moi file (buoi 1: nap du lieu)

| File | So dong | So cot |
|---|---:|---:|
| `dim_sku.csv` | 121 | 12 |
| `dim_chinh_sach.csv` | 4 | 5 |
| `dim_ngay.csv` | 364 | 9 |
| `fact_du_bao.csv` | 44.044 | 6 |
| `fact_ton_kho_ngay.csv` | 176.176 | 12 |
| `fact_ket_qua_sku.csv` | 1.452 | 16 |

## 2. Truoc – sau, muc phuc vu 95% (buoi 2)

Bang `fact_ket_qua_sku` co 3 muc phuc vu: **phai loc `muc_phuc_vu` = 0.95**, neu khong chi phi bi cong gap 3 (Fill Rate van dung vi la ty le).

| Chinh sach | Fill Rate | Ngay-SKU thieu | Ton kho binh quan (trieu d) | Chi phi lien quan (trieu d) |
|---|---:|---:|---:|---:|
| Hiện trạng* | 93,57% | 1.564 | 11.993,6 | 6.460,1 |
| Công thức + dự báo mốc | 88,83% | 1.050 | 15.808,5 | 9.307,9 |
| Công thức + dự báo AI | 93,16% | 916 | 13.049,1 | 7.079,7 |
| AI + hiệu chỉnh lệch (đề xuất) | 95,34% | 785 | 15.341,0 | 6.538,7 |

## 3. Du bao (buoi 3 va 5)

- WMAPE du bao AI (ket_hop_theo_nhom_v2), ca 121 SKU, tap test: **0,375** (du bao moc TB truot 28 ngay: 0,640). Chi tinh dong co `thuc_te`.
- Rieng SKU001: WMAPE AI 0,332, tong thuc te 81.434, tong du bao AI cung ngay 83.065.

## 4. Canh bao ngay 09/02/2026, chinh sach AI + hieu chinh lech (buoi 5)

| Trang thai | So SKU |
|---|---:|
| Hết hàng | 0 |
| Đặt hàng hôm nay | 11 |
| Dưới ROP, hàng đang về | 43 |
| Đủ hàng | 67 |
