# Ngữ cảnh dự án cho AI (đọc file này trước)

Đồ án tốt nghiệp ngành Logistics: **"Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho"**, hướng thực tập kho.
Ngôn ngữ làm việc: **tiếng Việt**; code, tên biến bằng tiếng Anh hoặc tiếng Việt không dấu theo file hiện có.
Người dùng là sinh viên, đang làm điều vận, chưa quen sâu với lập trình và thuật ngữ: giải thích ngắn, dễ hiểu, thuật ngữ lần đầu thì kèm nghĩa.

## Tóm tắt nhanh (đủ cho đa số câu hỏi, không cần mở thêm file)
- Dữ liệu **mô phỏng**: 121 SKU × 1.096 ngày (01/10/2023–30/09/2026) = 132.616 dòng, seed `20261009`.
- Chuỗi bài toán: dự báo cầu (d) → EOQ, SS, ROP → backtest so sánh mô hình → mô phỏng chính sách tồn kho (Fill Rate, Stockout, DOH).
- Đã xong: sinh dữ liệu, làm sạch (`src/lam_sach.py`). **Bước tiếp theo:** `src/dac_trung.py` (xem mục 6 file 01).
- Cột bản sạch `data/clean/giao_dich_sach.csv`: `date, ma_sku, qty_in, qty_out, ton_cuoi_ngay, la_ngay_nghi, het_hang, co_sua`.
- Cột `sku_master.csv`: `ma_sku, ten_sku, nhom_hang, don_vi, gia_von, nhu_cau_tb_ngay, xu_huong_nam, lead_time_tb, cv_nhu_cau, loai_mua_vu, lead_time_std, chi_phi_dat_hang, ty_le_chi_phi_luu_kho, moq, nha_cung_cap, gia_ban, ton_kho_ban_dau, gia_tri_xuat_36t, phan_loai_ABC, cv_theo_thang, phan_loai_XYZ`.

## Đọc file nào khi nào (chỉ mở khi cần, không đọc hết)
| Cần gì | Mở file |
|---|---|
| Tình hình, việc tiếp theo, giả định, điểm chưa nhất quán | `docs/01_tinh_hinh_du_an.md` |
| Công thức EOQ/SS/ROP, ABC/XYZ, MAE/WMAPE/MASE/Bias | `docs/02_thuat_ngu_cot_loi.md` |
| Ý nghĩa cột, 14 lý do tăng đột biến | `docs/03_du_lieu_mo_ta_va_su_kien.md` (2 bảng đầu) |
| Lịch sale sàn TMĐT | `docs/04_lich_sale_tmdt.md` |
| Thuật toán ở bước nào, bảng so sánh mô hình | `docs/06_thuat_toan_va_danh_gia.md` |
| Nguyên nhân chi phí (xăng, cảng, cước) | `docs/07_ly_do_chi_phi.md` |
| Thuật ngữ ngoài bảng cốt lõi (~120 thuật ngữ, điều vận, KPI) | `docs/02b_tu_dien_day_du.md` (tìm bằng grep, đừng đọc hết) |
| Khung 8 bước, lộ trình 79 ngày, chương đồ án | `docs/08_bao_cao_giai_doan_1.md` (chỉ đọc phần "Tóm tắt cho AI") |

**Tiết kiệm token:**
- Bảng ngày nghỉ, lịch lễ, nhật ký sự kiện trong docs 03 và 05 là **bản chép lại** của CSV trong `data/reference/`. Khi cần số liệu, đọc CSV (hoặc lọc bằng pandas), không đọc cả file md.
- `src/sinh_du_lieu.py` (~43 KB) chỉ mở khi cần sửa cách sinh dữ liệu; muốn biết cơ chế thì xem mục 2 file 01.
- Không mở file CSV lớn (`data/raw`, `data/clean`, `data/answer_key`) bằng Read; dùng pandas để in `head()`/thống kê.
- Không đọc file `.docx` trong `docs/`; đã có bản `.md` (02b, 08). Nếu file Word được sửa, chạy lại `python src/docx_sang_md.py <file.docx> <file.md>` (với 08 thì phải chép lại phần tóm tắt ở đầu).

## Quy tắc bắt buộc
- Dữ liệu là **mô phỏng**. Không trình bày kết quả như số liệu kho thật.
- `data/answer_key/` chỉ để kiểm tra script, **không** dùng làm đầu vào mô hình.
- Chia train/validation/test **theo thời gian**, không xáo trộn ngẫu nhiên.
- Ngày `het_hang = 1` có `qty_out` thấp hơn cầu thật, không coi là cầu.
- Đặc trưng lễ/bão/sale/mùa/khuyến mãi phải **tái tạo từ `data/reference/`** (khuyến mãi: `lich_khuyen_mai.csv`), không lấy từ answer_key.
- Mọi bước xử lý viết thành script trong `src/`, chạy lại được, ghi nhật ký thay đổi.
- Điều gì là giả định, điều gì kiểm chứng từ nguồn thật: luôn ghi rõ (xem mục 5 file 01).
- Sau khi xong một bước: cập nhật mục 3, 4, 6 trong `docs/01_tinh_hinh_du_an.md`.
