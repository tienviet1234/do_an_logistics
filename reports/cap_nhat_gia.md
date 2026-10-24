# Cap nhat gia mat hang theo gia ban le thi truong

Tra ngay 2026-10-24, nguon tung ma: `data/reference/gia_thi_truong.csv`. Kho duoc coi la kho tong chuoi sieu thi / bach hoa (docs/09 muc 4).
gia_ban = gia ban le tra duoc; gia_von = gia_ban / (bien lai cu cua ma) la **gia dinh** (gia nhap khong cong khai). Du lieu nhu cau, giao dich van la mo phong.

- Ma doi gia: **37**; giu gia cu: 84 (84 ma: hang chung chung / khong tra duoc / gia cu nam trong khoang tra duoc).
- Gia moi / gia cu (ma doi gia): trung vi x1.20, thap nhat x0.52, cao nhat x2.18.
- Tong gia tri xuat 36 thang (gia von): 736 ty -> 821 ty (+11.5%).
- ABC (36 thang) truoc: {'A': 31, 'B': 41, 'C': 49} -> sau: {'A': 28, 'B': 40, 'C': 53}; 11 ma doi nhom.

## Ma doi gia

| ma_sku   | ten_sku                           |   gia_von_cu |   gia_ban_cu | phan_loai_ABC_cu   |   gia_von_moi |   gia_ban_moi | phan_loai_ABC_moi   |   ty_le |
|:---------|:----------------------------------|-------------:|-------------:|:-------------------|--------------:|--------------:|:--------------------|--------:|
| SKU099   | Muối i-ốt 500g                    |         6500 |         7500 | C                  |          3500 |          3900 | C                   |    0.52 |
| SKU117   | Gói bù nước ORS hộp 20            |        38000 |        45000 | C                  |         24500 |         29000 | C                   |    0.64 |
| SKU104   | Giấy A4 Double A ream             |        88000 |        99000 | B                  |         62000 |         70000 | B                   |    0.71 |
| SKU011   | Sữa bột Dielac Alpha 900g         |       290000 |       359500 | A                  |        218000 |        270500 | A                   |    0.75 |
| SKU012   | Sữa chua Vinamilk lốc 4 hộp       |        25500 |        31500 | C                  |         21000 |         26000 | C                   |    0.83 |
| SKU033   | Nước tăng lực Redbull thùng 24    |       276000 |       320000 | A                  |        234500 |        272000 | A                   |    0.85 |
| SKU016   | Bia Tiger lon 330ml thùng 24      |       396000 |       455000 | A                  |        341500 |        392500 | A                   |    0.86 |
| SKU095   | Bàn chải đánh răng P/S lốc 3      |        42000 |        48500 | B                  |         36500 |         42000 | C                   |    0.87 |
| SKU094   | Nước rửa tay Lifebuoy 500ml       |        52000 |        67000 | B                  |         47500 |         61000 | B                   |    0.91 |
| SKU001   | Mì gói Hảo Hảo thùng 30 gói       |       105000 |       132500 | A                  |         99000 |        125000 | A                   |    0.94 |
| SKU014   | Coca-Cola lon 330ml thùng 24      |       192000 |       244000 | A                  |        184000 |        234000 | A                   |    0.96 |
| SKU038   | Bình xịt côn trùng Raid 600ml     |        58000 |        65500 | B                  |         56000 |         63000 | B                   |    0.96 |
| SKU007   | Nước tương Maggi chai 700ml       |        29000 |        36000 | C                  |         28000 |         35000 | C                   |    0.97 |
| SKU035   | Quạt cây Senko                    |       420000 |       496000 | A                  |        422500 |        499000 | A                   |    1.01 |
| SKU005   | Đường tinh luyện 1kg              |        24500 |        31000 | C                  |         25500 |         32000 | C                   |    1.03 |
| SKU008   | Hạt nêm Knorr 900g                |        66000 |        82500 | A                  |         69000 |         86000 | B                   |    1.04 |
| SKU081   | Bút bi Thiên Long hộp 20          |        62000 |        75000 | B                  |         66000 |         80000 | B                   |    1.07 |
| SKU085   | Sữa học đường hộp 180ml thùng 48  |       255000 |       286000 | A                  |        303000 |        340000 | A                   |    1.19 |
| SKU006   | Nước mắm Nam Ngư chai 750ml       |        38000 |        43500 | B                  |         45500 |         52000 | B                   |    1.2  |
| SKU017   | Nước ngọt Pepsi chai 1.5L lốc 6   |        82000 |       103500 | A                  |        100000 |        126000 | A                   |    1.22 |
| SKU022   | Nước rửa chén Sunlight 3.6kg      |        69000 |        83000 | A                  |         86500 |        104000 | A                   |    1.25 |
| SKU023   | Dầu gội Clear 630g                |       148000 |       168500 | A                  |        184500 |        210000 | A                   |    1.25 |
| SKU067   | Bánh trung thu Kinh Đô hộp 4 bánh |       150000 |       193000 | A                  |        190500 |        245000 | A                   |    1.27 |
| SKU106   | Nước cam ép Twister lốc 6         |        60000 |        70500 | B                  |         76500 |         90000 | A                   |    1.28 |
| SKU025   | Giấy vệ sinh Pulppy lốc 10 cuộn   |        56000 |        70000 | A                  |         72500 |         90500 | A                   |    1.29 |
| SKU018   | Cà phê G7 3in1 hộp 21 gói         |        54000 |        61500 | B                  |         70500 |         80500 | B                   |    1.31 |
| SKU021   | Nước xả vải Comfort 3.2L          |       128000 |       158500 | A                  |        169000 |        209000 | A                   |    1.32 |
| SKU024   | Kem đánh răng P/S 230g            |        30500 |        35000 | C                  |         43500 |         50000 | C                   |    1.43 |
| SKU093   | Khẩu trang y tế hộp 50            |        28000 |        35000 | B                  |         40000 |         50000 | B                   |    1.43 |
| SKU101   | Pin AA Panasonic vỉ 4             |        36000 |        44500 | B                  |         52500 |         65000 | B                   |    1.46 |
| SKU072   | Socola Ferrero hộp 16 viên        |       175000 |       223500 | A                  |        258500 |        330000 | A                   |    1.48 |
| SKU050   | Bình giữ nhiệt Lock&Lock          |       220000 |       267000 | B                  |        329500 |        400000 | B                   |    1.5  |
| SKU056   | Kem dưỡng thể Vaseline 350ml      |        85000 |        95500 | B                  |        133500 |        150000 | B                   |    1.57 |
| SKU061   | Rượu vang Đà Lạt chai             |       135000 |       155500 | B                  |        230000 |        265000 | A                   |    1.7  |
| SKU003   | Gạo ST25 túi 5kg                  |       112000 |       133500 | A                  |        198000 |        236000 | A                   |    1.77 |
| SKU013   | Nước suối Aquafina 500ml thùng 24 |        78000 |        88000 | A                  |        149000 |        168000 | A                   |    1.91 |
| SKU009   | Sữa tươi Vinamilk 1L thùng 12     |       186000 |       214000 | A                  |        406500 |        467500 | A                   |    2.18 |

## Ma doi nhom ABC (36 thang)

| ma_sku   | ten_sku                         |   gia_von_cu |     gia_ban_cu | phan_loai_ABC_cu   |   gia_von_moi |    gia_ban_moi | phan_loai_ABC_moi   |
|:---------|:--------------------------------|-------------:|---------------:|:-------------------|--------------:|---------------:|:--------------------|
| SKU008   | Hạt nêm Knorr 900g              |        66000 |  82500         | A                  |         69000 |  86000         | B                   |
| SKU048   | Máy sưởi dầu 11 thanh           |      1100000 |      1.361e+06 | A                  |       1100000 |      1.361e+06 | B                   |
| SKU061   | Rượu vang Đà Lạt chai           |       135000 | 155500         | B                  |        230000 | 265000         | A                   |
| SKU068   | Bánh trung thu lẻ nhân thập cẩm |        28000 |  36500         | A                  |         28000 |  36500         | B                   |
| SKU080   | Vở học sinh lốc 10 quyển        |        68000 |  87000         | A                  |         68000 |  87000         | B                   |
| SKU088   | Kẹo Halloween túi 300g          |        45000 |  54500         | B                  |         45000 |  54500         | C                   |
| SKU095   | Bàn chải đánh răng P/S lốc 3    |        42000 |  48500         | B                  |         36500 |  42000         | C                   |
| SKU097   | Tã quần Bobby gói 40 miếng      |       165000 | 197000         | A                  |        165000 | 197000         | B                   |
| SKU106   | Nước cam ép Twister lốc 6       |        60000 |  70500         | B                  |         76500 |  90000         | A                   |
| SKU109   | Cá hộp 150g                     |        24000 |  29500         | B                  |         24000 |  29500         | C                   |
| SKU110   | Thịt hộp 340g                   |        46000 |  55500         | B                  |         46000 |  55500         | C                   |

