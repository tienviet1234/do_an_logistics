# Hướng dẫn Power BI cho người mới (dùng dữ liệu đồ án)

Lập 23/10/2026. **Kế hoạch học: sau khi nộp đồ án (11–26/12/2026)**, không làm trước 09/12. Dashboard dùng khi bảo vệ vẫn là Streamlit (`app/dashboard.py`).
Mục tiêu: tự dựng 4 trang báo cáo Power BI giống các phần dự báo, cảnh báo, trước – sau, tham số của dashboard (bản 5 khu 24/10; bản 31/10 gộp lại thành 4 màn), qua đó học kỹ năng hay gặp trong tin tuyển thực tập kho / kế hoạch / điều vận.

**Chuẩn bị dữ liệu (AI đã làm sẵn):** `python src/xuat_power_bi.py` → 6 file CSV trong `reports/power_bi/` + `so_doi_chieu.md` (các con số đúng để tự kiểm tra). Chạy lại lệnh này mỗi khi chạy lại `ton_kho.py`.

Mỗi buổi khoảng 2–3 tiếng. Cuối mỗi buổi so số trên trang của bạn với `reports/power_bi/so_doi_chieu.md`; **khớp mới sang buổi sau**.

---

## Các file dữ liệu

| File | Loại | Một dòng là | Cột chính |
|---|---|---|---|
| `dim_sku` | Danh mục | 1 mặt hàng | `ma_sku`, `ten_sku`, `nhom_hang`, `abc`, `xyz`, `lead_time_tb`, `moq` |
| `dim_chinh_sach` | Danh mục | 1 chính sách đặt hàng | `ma_chinh_sach`, `ten_chinh_sach`, `thu_tu`, `de_xuat` |
| `dim_ngay` | Danh mục | 1 ngày trong 12 tháng test | `ngay`, `thang_nam`, `dau_tuan`, `ten_thu`, `kho_nghi` |
| `fact_du_bao` | Sự kiện | 1 SKU × 1 ngày | `thuc_te` (trống = ngày không chấm), `du_bao_ai`, `du_bao_moc` |
| `fact_ton_kho_ngay` | Sự kiện | 1 chính sách × 1 SKU × 1 ngày (mô phỏng, mức phục vụ 95%) | `nhu_cau`, `xuat`, `thieu`, `ton_cuoi`, `rop`, `dang_ve`, `dat_hang`, `trang_thai` |
| `fact_ket_qua_sku` | Sự kiện | 1 chính sách × 1 mức phục vụ × 1 SKU (tổng 12 tháng) | `nhu_cau`, `da_dap_ung`, `so_ngay_thieu`, `gia_tri_ton_tb`, chi phí, `ss_tb`, `rop_tb`, `eoq_tb` |

**Bảng danh mục (dimension)** mô tả "ai, cái gì, khi nào"; **bảng sự kiện (fact)** chứa các con số. Nối danh mục vào sự kiện qua mã chung gọi là **mô hình hình sao** (star schema), cùng ý tưởng với khóa ngoại trong CSDL `data/kho_hang.db` (`dm_sku` ↔ `giao_dich_sach`).

---

## Buổi 1. Cài đặt, nạp dữ liệu, nối bảng

1. Cài **Power BI Desktop** từ Microsoft Store (miễn phí), mở lên, đóng màn hình chào.
2. **Home → Get data → Text/CSV** → chọn `reports/power_bi/dim_sku.csv` → bảng xem trước hiện tiếng Việt đúng → **Load**. Lặp lại cho 5 file còn lại.
3. Bấm biểu tượng **Table view** (ô lưới, cột bên trái). Chọn từng bảng, xem số dòng ở góc dưới bên trái, so với mục 1 của `so_doi_chieu.md`.
4. Kiểm tra kiểu dữ liệu: cột `ngay` của `dim_ngay`, `fact_du_bao`, `fact_ton_kho_ngay` phải là **Date** (chọn cột → **Column tools → Data type → Date**). Các cột số lượng phải là số (biểu tượng Σ trong danh sách cột).
5. Bấm **Model view** (biểu tượng 3 ô nối nhau). Power BI có thể tự nối một số bảng. Cần đủ 7 đường nối, mỗi đường **1 → \*** (một – nhiều):
   - `dim_sku[ma_sku]` → `fact_du_bao`, `fact_ton_kho_ngay`, `fact_ket_qua_sku`
   - `dim_ngay[ngay]` → `fact_du_bao`, `fact_ton_kho_ngay`
   - `dim_chinh_sach[ma_chinh_sach]` → `fact_ton_kho_ngay`, `fact_ket_qua_sku`

   Thiếu đường nào thì kéo cột ở bảng danh mục thả vào cột cùng tên ở bảng sự kiện. Thấy đường nối **giữa 2 bảng fact** thì xóa (chuột phải → Delete).
6. Lưu file: `reports/power_bi/do_an_ton_kho.pbix`.

**Học được:** mô hình hình sao; vì sao mỗi mã SKU chỉ có 1 dòng trong bảng danh mục (để nối không bị nhân đôi số).

## Buổi 2. Trang "Trước – sau"

1. Ở **Report view**, đổi tên trang (chuột phải tab dưới cùng) thành `Trước – sau`.
2. **Lọc mức phục vụ:** mở khung **Filters** → kéo `fact_ket_qua_sku[muc_phuc_vu]` vào **Filters on this page** → chỉ tích `0.95`.
   ⚠️ Bỏ bước này thì chi phí bị **cộng gấp 3** (bảng có 3 mức 90/95/99%). Đây là lỗi hay gặp nhất khi làm báo cáo: cộng trùng dữ liệu.
3. Tạo **measure** (phép tính dùng lại được): chọn bảng `fact_ket_qua_sku` → **Home → New measure**, gõ từng dòng, Enter:
   ```
   Fill Rate = DIVIDE ( SUM ( fact_ket_qua_sku[da_dap_ung] ), SUM ( fact_ket_qua_sku[nhu_cau] ) )
   Ngày-SKU thiếu = SUM ( fact_ket_qua_sku[so_ngay_thieu] )
   Tồn kho bình quân (tr đ) = SUM ( fact_ket_qua_sku[gia_tri_ton_tb] ) / 1000000
   Chi phí liên quan (tr đ) = ( SUM ( fact_ket_qua_sku[chi_phi_dat] ) + SUM ( fact_ket_qua_sku[chi_phi_luu] ) + SUM ( fact_ket_qua_sku[loi_nhuan_mat] ) ) / 1000000
   ```
   Chọn measure `Fill Rate` → **Measure tools → Format → Percentage**, 2 chữ số thập phân.
4. **Sắp xếp chính sách đúng thứ tự:** Table view → bảng `dim_chinh_sach` → chọn cột `ten_chinh_sach` → **Column tools → Sort by column → thu_tu**.
5. Thêm 4 biểu đồ **Clustered bar chart**: trục Y = `dim_chinh_sach[ten_chinh_sach]`, trục X = từng measure (mỗi measure một biểu đồ, không gộp chung vì khác đơn vị).
6. Thêm **Table**: `ten_chinh_sach` + 4 measure. So với mục 2 của `so_doi_chieu.md` (AI + hiệu chỉnh: 95,91%, 752, 16.377,3, 6.672,7).
7. Thêm **Slicer** `dim_sku[xyz]`: chọn X, Y, Z để xem nhóm nào AI thắng (so `reports/ton_kho_so_sanh.md`, bảng theo nhóm XYZ).

**Học được:** measure khác cột thường; Fill Rate phải là **tổng đáp ứng / tổng nhu cầu**, không phải trung bình Fill Rate từng SKU (SKU bán ít sẽ kéo lệch).

## Buổi 3. Trang "Dự báo theo SKU"

1. Trang mới `Dự báo`. Thêm **Slicer** `dim_sku[ten_sku]`; ở Format, bật **Single select**.
2. Measure trên bảng `fact_du_bao`:
   ```
   Thực tế = SUM ( fact_du_bao[thuc_te] )
   Dự báo AI = SUM ( fact_du_bao[du_bao_ai] )
   Dự báo mốc = SUM ( fact_du_bao[du_bao_moc] )
   WMAPE AI =
   VAR cham = FILTER ( fact_du_bao, NOT ISBLANK ( fact_du_bao[thuc_te] ) )
   RETURN DIVIDE ( SUMX ( cham, ABS ( fact_du_bao[thuc_te] - fact_du_bao[du_bao_ai] ) ), SUMX ( cham, fact_du_bao[thuc_te] ) )
   ```
3. **Line chart**: trục X = `dim_ngay[ngay]` (bấm mũi tên cạnh tên trường, chọn `ngay` thay vì *Date Hierarchy*), trục Y = 3 measure đầu.
4. **Card** = `WMAPE AI`, định dạng 3 chữ số thập phân. Chọn SKU001 → 0,332; bỏ chọn (cả kho) → 0,368 (mục 3 `so_doi_chieu.md`).
5. **Thử thách:** đổi trục X sang `dim_ngay[dau_tuan]` (theo tuần). Đường thực tế trông thấp hơn dự báo, vì tuần có ngày hết hàng/kho nghỉ thì thực tế trống mà dự báo vẫn cộng. Sửa bằng measure chỉ cộng dự báo ở ngày được chấm:
   ```
   Dự báo AI (ngày chấm) = SUMX ( FILTER ( fact_du_bao, NOT ISBLANK ( fact_du_bao[thuc_te] ) ), fact_du_bao[du_bao_ai] )
   ```
   SKU001: tổng thực tế 81.434, tổng dự báo AI ngày chấm 83.392.

**Học được:** WMAPE là sai số theo tổng (không phải trung bình phần trăm); so sánh công bằng phải so trên cùng ngày.

## Buổi 4. Trang "Diễn biến tồn kho"

1. Trang mới `Tồn kho`. Slicer `dim_sku[ten_sku]` (single select) và slicer `dim_chinh_sach[ten_chinh_sach]` (single select, chọn "AI + hiệu chỉnh lệch").
2. Measure trên `fact_ton_kho_ngay`:
   ```
   Tồn cuối ngày = SUM ( fact_ton_kho_ngay[ton_cuoi] )
   ROP = SUM ( fact_ton_kho_ngay[rop] )
   Fill Rate ngày = DIVIDE ( SUM ( fact_ton_kho_ngay[xuat] ), SUM ( fact_ton_kho_ngay[nhu_cau] ) )
   ```
3. **Line chart**: trục X = `dim_ngay[ngay]`, trục Y = `Tồn cuối ngày`, `ROP`. Thấy hình **răng cưa**: tồn giảm theo bán, chạm ROP thì đặt, hàng về thì vọt lên. Răng chạm 0 là ngày hết hàng.
4. **Line chart** thứ hai: trục X = `dim_ngay[thang_nam]`, trục Y = `Fill Rate ngày`, Legend = `ten_chinh_sach`; bỏ chọn slicer chính sách và SKU. Tháng nào chính sách mốc tụt mạnh? Đáp án: 02/2026 (Tết) mốc chỉ 69,9% so với 95,7% của AI + hiệu chỉnh; 12/2025 (Noel) 81,1% và 09/2026 (Trung thu) 80,9% cũng tụt. Tháng 10/2025 mọi chính sách đều thấp (80–84%) vì đầu kỳ bắt đầu từ tồn kho có sẵn trong dữ liệu.
5. Kiểm tra: bỏ chọn SKU, chọn 1 chính sách → `Fill Rate ngày` cả năm phải bằng Fill Rate ở buổi 2 (95,91% với AI + hiệu chỉnh).

**Học được:** điểm đặt hàng (ROP) và chu kỳ tồn kho; tháng cao điểm là lúc dự báo kém bị lộ ra.

## Buổi 5. Trang "Cảnh báo tồn kho"

1. Trang mới `Cảnh báo`. Slicer `dim_ngay[ngay]`: ở Format → Slicer settings chọn kiểu **Single value** hoặc **Dropdown**, chọn 09/02/2026. Slicer chính sách: "AI + hiệu chỉnh lệch".
2. Measure:
   ```
   Số SKU = DISTINCTCOUNT ( fact_ton_kho_ngay[ma_sku] )
   Đặt hôm nay = SUM ( fact_ton_kho_ngay[dat_hang] )
   ```
3. **Matrix**: Rows = `fact_ton_kho_ngay[trang_thai]`, Values = `Số SKU`. Phải ra 1 / 5 / 44 / 71 (mục 4 `so_doi_chieu.md`).
4. **Table** chi tiết: `trang_thai`, `ma_sku`, `ten_sku`, `ton_cuoi`, `rop`, `dang_ve`, `dat_hang`, `lead_time_tb`; ở Filters của riêng bảng này, bỏ tích "Đủ hàng". Bấm tiêu đề cột để sắp xếp.
5. **Tô màu theo trạng thái** (Format → Cell elements → Background color → Rules): Hết hàng đỏ, Đặt hàng hôm nay cam, Dưới ROP vàng. Giữ chữ trạng thái, không chỉ dùng màu (người mù màu vẫn đọc được).

**Học được:** quản lý theo ngoại lệ; khác nhau giữa tồn thực và vị thế tồn kho (tồn + hàng đang về) — xem `docs/11` Bài 11.

---

## Lỗi hay gặp

| Hiện tượng | Nguyên nhân | Cách sửa |
|---|---|---|
| Chi phí gấp 3 lần `so_doi_chieu.md` | Chưa lọc `muc_phuc_vu` = 0.95 | Buổi 2, bước 2 |
| Số thập phân sai (95.36 thành 9536) | Máy đặt định dạng số kiểu Việt Nam (dấu phẩy thập phân) | **File → Options and settings → Options → Regional settings → Locale for import: English (United States)**, rồi **Home → Refresh** |
| Chữ tiếng Việt lỗi font | Đọc sai bảng mã | Khi nạp, chọn **File origin: 65001: Unicode (UTF-8)** |
| Biểu đồ theo ngày chỉ ra 4 điểm (Year/Quarter/Month/Day) | Power BI tự tạo *Date Hierarchy* | Bấm mũi tên cạnh trường ngày → chọn `ngay` |
| Slicer SKU không lọc biểu đồ | Thiếu đường nối trong Model view | Buổi 1, bước 5 |
| Chạy lại mô hình nhưng Power BI vẫn số cũ | CSV chưa xuất lại | `python src/xuat_power_bi.py` rồi **Home → Refresh** |

## Ghi vào CV (sau khi làm xong 5 buổi)

> Xây dựng báo cáo Power BI theo dõi dự báo nhu cầu và tồn kho cho 121 SKU (dữ liệu mô phỏng): mô hình dữ liệu hình sao 6 bảng, measure DAX cho Fill Rate, WMAPE, chi phí tồn kho; trang cảnh báo SKU cần đặt hàng theo ngày.

Ghi rõ "dữ liệu mô phỏng" khi phỏng vấn, giống quy tắc của đồ án.
