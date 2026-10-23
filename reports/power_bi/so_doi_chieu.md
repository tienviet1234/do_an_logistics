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
| Hiện trạng* | 93,57% | 1.564 | 11.133,7 | 5.924,0 |
| Công thức + dự báo mốc | 88,75% | 1.051 | 14.890,1 | 8.650,1 |
| Công thức + dự báo AI | 93,15% | 933 | 12.673,9 | 6.359,3 |
| AI + hiệu chỉnh lệch (đề xuất) | 95,36% | 758 | 15.133,4 | 5.979,9 |

## 3. Du bao (buoi 3 va 5)

- WMAPE du bao AI (ket_hop_theo_nhom_v2), ca 121 SKU, tap test: **0,376** (du bao moc TB truot 28 ngay: 0,640). Chi tinh dong co `thuc_te`.
- Rieng SKU001: WMAPE AI 0,332, tong thuc te 81.434, tong du bao AI cung ngay 83.392.

## 4. Canh bao ngay 09/02/2026, chinh sach AI + hieu chinh lech (buoi 5)

| Trang thai | So SKU |
|---|---:|
| Hết hàng | 1 |
| Đặt hàng hôm nay | 5 |
| Dưới ROP, hàng đang về | 44 |
| Đủ hàng | 71 |
