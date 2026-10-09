# Bao cao lam sach du lieu

## 1. Cau truc
- So dong ban dau: 132,814; so SKU: 121; tu 2023-10-01 den 2026-09-30
- O trong theo cot: {'qty_out': 531}

## 2. Lam sach
- Dong co SKU khong co trong SKU_master: 0
- Dong trung hoan toan (loai bo): 198
- Con trung theo (ngay, SKU) sau khi loai: 0 (neu > 0 can xem tay)
- SKU thieu ngay trong chuoi: 0

## 3. Kiem tra logic kho (ton_cuoi = ton_dau + nhap - xuat)
- Dong co ton cuoi am: 0
- Dong co qty_out suy ra am (vo ly): 0
- Dong xuat hang vao ngay kho dong cua: 0

## 4. Loi nhap lieu hay dot bien that
- qty_out bi thieu (NaN): 530
- qty_out khac gia tri suy ra tu ton kho (nghi nhap sai): 157
  Cach xu ly: dot bien that (bao, sale) van khop voi ton kho nen KHONG bi coi la loi.
  Chi dong lech voi ton kho moi bi sua.
- Da sua: 687 dong (chi tiet o reports/dong_da_sua.csv)

## 5. Ngay het hang
- Ngay ton cuoi = 0: 4225 dong (3.19% tong so dong)
- Tren cac ngay nay, luong xuat THAP HON cau that vi khong du hang.
  Khi huan luyen mo hinh can loai ra hoac uoc luong lai (xem buoc dac trung).

=> Da ghi 132,616 dong vao data/clean/giao_dich_sach.csv

## 6. Doi chieu voi dap an (du lieu mo phong)
- So dong khop khoa (ngay, SKU) voi dap an: 132,616 / 132,616
- Dong qty_out con sai so voi dap an: 0
- Loi da cai san: {'thieu_qty_out': 530, 'dong_trung': 198, 'outlier_nhap_sai': 159}
- Loi dong_trung phat hien: 198 (cai san 198)
- Loi thieu/outlier da sua: 687 (cai san 689)