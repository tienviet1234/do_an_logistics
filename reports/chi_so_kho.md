# Chỉ số kho

Mô phỏng 364 ngày của tập kiểm tra, mức phục vụ 95%. Dữ liệu mô phỏng, không phải số liệu kho thật.

Tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng để ra quyết định); bỏ 28 ngày cuối kỳ.

## Theo chính sách

| ma_chinh_sach          |   vong_quay_lan_nam |   so_ngay_ton |   ton_tb_trieu |   ton_du_tb_trieu |   ti_le_du_pt |
|:-----------------------|--------------------:|--------------:|---------------:|------------------:|--------------:|
| cong_thuc_du_bao_ai    |                31.3 |          11.7 |         9208.7 |            4096.9 |          44.6 |
| cong_thuc_du_bao_ai_hc |                24.2 |          15.1 |        11906   |            6367.8 |          54.2 |
| cong_thuc_du_bao_moc   |                14.2 |          25.7 |        19669.7 |           13629.4 |          69.6 |
| hien_trang             |                23.8 |          15.4 |        11993.6 |            5175.3 |          43.2 |

## Số ngày tồn kho theo nhóm XYZ

| ma_chinh_sach          |   X |    Y |     Z |
|:-----------------------|----:|-----:|------:|
| cong_thuc_du_bao_ai    | 5.7 | 10.9 |  45.2 |
| cong_thuc_du_bao_ai_hc | 5.8 | 11.5 |  67.1 |
| cong_thuc_du_bao_moc   | 6.6 | 15.2 | 155.4 |
| hien_trang             | 8.3 | 10.6 |  57.9 |

## 10 mã tồn dư lớn nhất (AI + hiệu chỉnh)

| ma_sku   | ten                             | xyz   |   du_trieu |
|:---------|:--------------------------------|:------|-----------:|
| SKU089   | Cây thông Noel 1m2              | Z     |     1038.1 |
| SKU059   | Hộp quà Tết cao cấp             | Z     |     1023.4 |
| SKU058   | Mứt Tết hộp 500g                | Z     |      563.7 |
| SKU060   | Hạt điều rang muối hộp 500g     | Z     |      483.6 |
| SKU068   | Bánh trung thu lẻ nhân thập cẩm | Z     |      377.4 |
| SKU061   | Rượu vang Đà Lạt chai           | Z     |      364.6 |
| SKU088   | Kẹo Halloween túi 300g          | Z     |      302.6 |
| SKU091   | Bánh quy bơ hộp Noel            | Z     |      298.7 |
| SKU063   | Hoa mai/đào giả trang trí       | Z     |      222.1 |
| SKU082   | Cặp sách học sinh               | Z     |      217.3 |
