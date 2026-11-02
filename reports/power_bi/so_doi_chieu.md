# So doi chieu cho Power BI

Sinh tu dong boi `python src/xuat_power_bi.py`, tinh tu chinh cac file CSV vua xuat va da doi chieu voi CSDL (lech thi script dung lai bao loi). Dung trang Power BI xong, so tren trang phai ra dung cac so duoi day. Du lieu mo phong.

## 1. So dong moi file (buoi 1: nap du lieu)

| File | So dong | So cot |
|---|---:|---:|
| `dim_sku.csv` | 121 | 12 |
| `dim_chinh_sach.csv` | 4 | 5 |
| `dim_ngay.csv` | 364 | 9 |
| `fact_du_bao.csv` | 44.044 | 8 |
| `fact_ton_kho_ngay.csv` | 176.176 | 12 |
| `fact_ket_qua_sku.csv` | 1.452 | 16 |

## 2. Truoc – sau, muc phuc vu 95% (buoi 2)

Bang `fact_ket_qua_sku` co 3 muc phuc vu: **phai loc `muc_phuc_vu` = 0.95**, neu khong chi phi bi cong gap 3 (Fill Rate van dung vi la ty le).

| Chinh sach | Fill Rate | Ngay-SKU thieu | Ton kho binh quan (trieu d) | Chi phi lien quan (trieu d) |
|---|---:|---:|---:|---:|
| Hiện trạng* | 93,57% | 1.564 | 11.993,6 | 6.460,1 |
| Công thức + dự báo mốc | 91,69% | 916 | 19.669,7 | 9.011,0 |
| Công thức + dự báo AI | 95,33% | 793 | 9.208,7 | 5.329,6 |
| AI + hiệu chỉnh lệch (đề xuất) | 95,82% | 735 | 11.906,0 | 5.828,1 |

## 3. Du bao (buoi 3 va 5)

- WMAPE du bao AI (ket_hop_v4), ca 121 SKU, tap test: **0,356** (du bao moc TB truot 28 ngay: 0,584). Chi tinh dong co `thuc_te`.
- Rieng SKU001: WMAPE AI 0,316, tong thuc te 81.434, tong du bao AI cung ngay 82.141.

## 4. Canh bao ngay 09/02/2026, chinh sach AI + hieu chinh lech (buoi 5)

| Trang thai | So SKU |
|---|---:|
| Hết hàng | 0 |
| Đặt hàng hôm nay | 8 |
| Dưới ROP, hàng đang về | 44 |
| Đủ hàng | 69 |
