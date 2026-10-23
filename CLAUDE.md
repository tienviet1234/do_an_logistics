# Ngữ cảnh dự án cho AI (đọc file này trước)

Đồ án tốt nghiệp ngành Logistics: **"Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho"**, hướng thực tập kho.
Ngôn ngữ làm việc: **tiếng Việt**; code, tên biến bằng tiếng Anh hoặc tiếng Việt không dấu theo file hiện có.
Người dùng là sinh viên, **chưa đi làm**, mục tiêu là học để trở thành thực tập sinh điều vận; chưa quen sâu với lập trình và thuật ngữ: giải thích ngắn, dễ hiểu, thuật ngữ lần đầu thì kèm nghĩa. Dự án vừa là đồ án vừa là công cụ học: khi làm xong một bước, nói rõ bước đó dạy được kiến thức logistics/điều vận gì. Không có dữ liệu từ nơi làm việc.
**Cách học đã chốt:** học cả kiến thức điều vận/kho lẫn kỹ năng dữ liệu; AI làm phần việc, xong mỗi bước thì cùng xem lại → thêm 1 bài vào `docs/11_ghi_chu_hoc.md` (kiến thức logistics, kỹ năng dữ liệu, câu hỏi tự kiểm tra / phỏng vấn kèm gợi ý trả lời). Mỗi bài ngắn, dùng ví dụ từ chính dữ liệu dự án.

## Tóm tắt nhanh (đủ cho đa số câu hỏi, không cần mở thêm file)
- Dữ liệu **mô phỏng**: 121 SKU × 1.096 ngày (01/10/2023–30/09/2026) = 132.616 dòng, seed `20261009`.
- Chuỗi bài toán: dự báo cầu (d) → EOQ, SS, ROP → backtest so sánh mô hình → mô phỏng chính sách tồn kho (Fill Rate, Stockout, DOH).
- **Lịch:** thực hiện 14/09–06/12/2026, **nộp 09/12/2026**, phản biện 11–26/12, hội đồng 27–29/12, **bảo vệ 30–31/12/2026**. Lịch theo tuần: `docs/09` mục 1b.
- Đã xong: sinh dữ liệu, làm sạch (`src/lam_sach.py`), đặc trưng (`src/dac_trung.py` → `data/features/`, chạy lại nếu chưa có). EDA (`src/eda.py` → `reports/eda/`), khung đánh giá (`src/danh_gia.py`: mọi mô hình dùng `backtest()` + `save_results()`). Mô hình mốc (`src/mo_hinh_baseline.py`, xong 23/10; tốt nhất TB trượt 28 ngày WMAPE test 0,640, so sánh: `python src/tong_hop_ket_qua.py`). Chương 1 nháp (`do_an/`). Prophet (`src/mo_hinh_prophet.py`, xong 24/10; test WMAPE 0,454, tốt nhất hiện tại). LightGBM (`src/mo_hinh_lightgbm.py`, xong 24/10; test WMAPE 0,400 tốt nhất theo ngày nhưng Bias +11,6%, thiếu hàng mùa vụ). GĐ E xong 24/10 (`src/chon_mo_hinh.py --vong 2`): mô hình dùng tiếp là **kết hợp theo nhóm** (w LightGBM X 0,9 · Y 1,0 · Z 0,6), dự báo `reports/du_bao/ket_hop_theo_nhom_v2_test.csv`, test WMAPE 0,376, Bias +6,2%. Validation dùng để chọn là `validation2` (cùng mùa với test). Luồng hệ thống + CSDL (nhiệm vụ GVHD) xong 24/10: `python src/nap_database.py` rồi `python src/tao_trang_luong.py`. **Bước tiếp theo:** GĐ F tồn kho, **đọc từ CSDL** (`dm_sku`, `v_du_bao_chon`), ghi kết quả vào CSDL (xem `docs/09`). Máy 7,6 GB RAM: chạy song song tối đa 4 tiến trình.
- Cột bản sạch `data/clean/giao_dich_sach.csv`: `date, ma_sku, qty_in, qty_out, ton_cuoi_ngay, la_ngay_nghi, het_hang, co_sua`.
- Cột `sku_master.csv`: `ma_sku, ten_sku, nhom_hang, don_vi, gia_von, nhu_cau_tb_ngay, xu_huong_nam, lead_time_tb, cv_nhu_cau, loai_mua_vu, lead_time_std, chi_phi_dat_hang, ty_le_chi_phi_luu_kho, moq, nha_cung_cap, gia_ban, ton_kho_ban_dau, gia_tri_xuat_36t, phan_loai_ABC, cv_theo_thang, phan_loai_XYZ`.

## Đọc file nào khi nào (chỉ mở khi cần, không đọc hết)
| Cần gì | Mở file |
|---|---|
| Tình hình, việc tiếp theo, giả định, điểm chưa nhất quán | `docs/01_tinh_hinh_du_an.md` |
| Lộ trình chi tiết, việc đang ở giai đoạn nào, quyết định đã chốt | `docs/09_lo_trinh.md` |
| Báo cáo sống GĐ2 (kết quả, số liệu, nhật ký; nguồn để viết đồ án) | `docs/10_bao_cao_giai_doan_2.md` |
| Các chương đồ án (bản nháp để nộp) | `do_an/chuong_*.md`; chuyển Word: `python src/md_sang_docx.py do_an/chuong_1_mo_dau.md` |
| Công thức EOQ/SS/ROP, ABC/XYZ, MAE/WMAPE/MASE/Bias | `docs/02_thuat_ngu_cot_loi.md` |
| Ý nghĩa cột, 14 lý do tăng đột biến | `docs/03_du_lieu_mo_ta_va_su_kien.md` (2 bảng đầu) |
| Lịch sale sàn TMĐT | `docs/04_lich_sale_tmdt.md` |
| Thuật toán ở bước nào, bảng so sánh mô hình | `docs/06_thuat_toan_va_danh_gia.md` |
| Nguyên nhân chi phí (xăng, cảng, cước) | `docs/07_ly_do_chi_phi.md` |
| Thuật ngữ ngoài bảng cốt lõi (~120 thuật ngữ, điều vận, KPI) | `docs/02b_tu_dien_day_du.md` (tìm bằng grep, đừng đọc hết) |
| Cơ sở dữ liệu (SQLite `data/kho_hang.db`), thiết kế bảng, truy vấn mẫu | `database/schema.sql`, `database/truy_van_mau.sql`; kết nối: `src/csdl.py` (`ket_noi`, `doc`) |
| Trang trình bày luồng hệ thống (offline) | `trinh_bay/luong_he_thong.html`, sinh bởi `src/tao_trang_luong.py` |
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
- Sau khi xong một bước: cập nhật mục 3, 4, 6 trong `docs/01_tinh_hinh_du_an.md` **và ghi vào `docs/10_bao_cao_giai_doan_2.md`** (điền đúng mục của bước, thêm 1 dòng vào mục 14 Nhật ký, đổi ⏳ thành ✅). Số liệu lấy từ file kết quả, không ghi theo trí nhớ.
