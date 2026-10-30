# Tình hình hiện tại của dự án

Cập nhật: 10/10/2026.

## 1. Mục tiêu và bối cảnh
- Đề tài: ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho, hướng thực tập kho.
- Giảng viên hướng dẫn yêu cầu **xây dựng dữ liệu đầu vào** cho bài toán. Báo cáo giai đoạn 1 ("Kiến thức cần chuẩn bị") nằm ở `docs/Bao_cao_Giai_doan_1_Kien_thuc_can_chuan_bi.docx`, bản md: `docs/08_bao_cao_giai_doan_1.md` (có tóm tắt và bảng điểm khác với cách dự án đang làm).
- **Chưa có dữ liệu thật** từ đơn vị thực tập. Vì vậy dữ liệu được mô phỏng bằng Python để xây dựng và kiểm thử quy trình. Khi có file xuất từ WMS/ERP, giữ nguyên tên cột để thay vào.
- Lịch trường: thực hiện 14/09–06/12/2026 (12 tuần), nộp 09/12/2026, chấm phản biện 11–26/12/2026, thành lập hội đồng 27–29/12, bảo vệ 30–31/12/2026.
- Chuỗi bài toán: dự báo nhu cầu (d) → tham số tồn kho (EOQ, SS, ROP) → so sánh mô hình bằng backtest.

## 2. Dữ liệu hiện có
- **121 SKU × 1.096 ngày** (01/10/2023 đến 30/09/2026) = 132.616 dòng. Đủ 3 mùa Tết (10/02/2024, 29/01/2025, 17/02/2026), 3 mùa Trung thu, 3 chu kỳ đủ 4 mùa.
- 4 mùa (miền Bắc): Xuân T2–4, Hạ T5–7, Thu T8–10, Đông T11–1.
- Có hàng bán được và không bán được theo mùa (nhãn `loai_mua_vu` trong sku_master), ngày lễ có hệ số tăng riêng từng SKU, bão lũ 3 pha, đột biến (nắng nóng, rét đậm, cúm, tin đồn tăng giá, thể thao, đơn B2B, nhà cung cấp giao chậm), kho đóng cửa (Tết, lễ), hết hàng (~3,2% số ngày), sale 11.11, 12.12, Black Friday.
- Cơ chế đặt hàng mô phỏng: chính sách (s,Q) dựa trên dự báo của người lập kế hoạch có độ lệch; cầu theo phân phối nhị thức âm.
- Cố định hạt giống `20261009`, chạy lại `src/sinh_du_lieu.py` sẽ ra đúng bộ dữ liệu.

### File dữ liệu
| Thư mục | File | Nội dung |
|---|---|---|
| data/raw | giao_dich_nhap_xuat_ton_THO.csv | Bản có lỗi cài sẵn: date, ma_sku, qty_in, qty_out, ton_cuoi_ngay |
| data/clean | giao_dich_sach.csv | Sau làm sạch: thêm la_ngay_nghi, het_hang, co_sua |
| data/reference | sku_master.csv | 121 SKU + tham số EOQ/SS/ROP, ABC, XYZ |
| data/reference | lich_su_kien_prophet.csv | Lịch lễ đúng định dạng Prophet (holiday, ds, lower_window, upper_window) |
| data/reference | lich_ngay_nghi_kho.csv | Ngày kho đóng cửa |
| data/reference | su_kien_dot_bien.csv | Nhật ký bão và mọi cú sốc đã đưa vào |
| data/reference | lich_khuyen_mai.csv | Đợt khuyến mãi theo SKU: ma_sku, tu_ngay, den_ngay, so_ngay |
| data/reference | tong_hop_*.csv | Chỉ số mùa, ngày lễ, bão lũ theo SKU |
| data/answer_key | ...SACH.csv, nhat_ky_loi_co_chu_dich.csv | Đáp án để kiểm tra |

**Lưu ý quan trọng:** bản sạch trong `data/clean` chưa có các cột `mua`, `khuyen_mai`, `bao_lu_muc_do`, `trong_tuan_tet` (chỉ có trong bản đáp án). Khi làm đặc trưng phải tái tạo từ lịch trong `data/reference` (`khuyen_mai` lấy từ `lich_khuyen_mai.csv`), không lấy từ answer_key.

## 3. Đã làm
1. Đọc báo cáo giai đoạn 1, xây dựng bộ dữ liệu mô phỏng ban đầu (108 SKU) rồi mở rộng.
2. Từ điển thuật ngữ viết tắt logistics (~120 thuật ngữ, 5 nhóm, kèm nhóm thuật ngữ cho nhân viên điều vận). Bản đầy đủ: `docs/Từ điển thuật ngữ viết tắt ngành Logistics & Quản lý tồn kho.docx`, bản md: `docs/02b_tu_dien_day_du.md`.
3. Mở rộng dữ liệu lên 121 SKU: 4 mùa, ngày lễ, hàng bán được và không bán được theo mùa.
4. Thêm bão lũ (ngày bão thực tế), nhiều lý do tăng đột biến khác, nguyên nhân phi thời tiết, lịch sale sàn thương mại điện tử.
5. Gộp các bảng tính thành 2 file Excel (`reports/Du_lieu_dau_vao_tong_hop.xlsx`, `reports/Mo_hinh_va_danh_gia.xlsx`).
6. Lập bảng nguyên nhân về chi phí kèm bảng thử độ nhạy EOQ/SS/ROP (file 07).
7. Dựng thư mục dự án cho VS Code và script `src/lam_sach.py` (bước 1–5 tiền xử lý).
8. (10/10/2026) `sinh_du_lieu.py`: xuất thêm `lich_khuyen_mai.csv`; sửa lỗi tràn số cột `gia_tri_xuat_36t` khi chạy trên Windows (int 32-bit). Đã chạy lại và đối chiếu: mọi file cũ giống hệt nội dung. Lưu ý: bản thân script ghi tất cả file ra **một** thư mục (`python src/sinh_du_lieu.py <thu_muc>`), sau đó phải tự chia vào raw/reference/answer_key.
9. (10/10/2026) Chuyển 2 file .docx sang md bằng `src/docx_sang_md.py`.
10. (10/10/2026) `src/dac_trung.py` → `data/features/dac_trung.csv` (132.616 dòng × 64 cột, không lưu vào git, chạy lại script để có) và `data/features/phan_loai_sku.csv`. Báo cáo: `reports/bao_cao_dac_trung.md`. Cột chính: lịch, 17 cờ sự kiện `sk_*`, bão (mức độ, pha trước/sau), sale, khuyến mãi, lag 1/7/14/28/35/364, trung bình trượt, `y` (= qty_out), `y_cau` (bỏ ngày hết hàng và ngày kho đóng cửa), `abc_train`/`xyz_train`/`loai_nhu_cau`.
12. (10/10/2026) `src/danh_gia.py`: khung backtest chung (6 mốc validation, 13 mốc test, tầm 28 ngày), Naive và Seasonal Naive làm mốc; kết quả `reports/ket_qua_mo_hinh.csv`. Chi tiết quy ước: `docs/09` GĐ B.
11. (10/10/2026) `src/eda.py` → 8 hình `reports/eda/h01–h08.png` + `reports/bao_cao_eda.md` (kèm nhận xét từng hình).
13. (23/10/2026) GĐ G: dashboard `app/dashboard.py` (Streamlit, chỉ đọc CSDL), chạy `streamlit run app/dashboard.py`. Từ 24/10 có 5 khu: tổng quan dữ liệu (6 biểu đồ phân tích), dự báo theo SKU, cảnh báo tồn kho theo ngày, trước – sau, bảng SS/ROP/EOQ. Chi tiết `docs/10` mục 12.
14. (23/10/2026) Dữ liệu cho Power BI: `python src/xuat_power_bi.py` → `reports/power_bi/` (6 CSV + số đối chiếu). Hướng dẫn học 5 buổi: `docs/12_power_bi.md`, làm sau khi nộp.
15. (23/10/2026) Thử độ nhạy chính sách tồn kho `src/do_nhay.py` (tắc cảng +3/+5/+7 ngày ở 13 đợt, lead time +2 ngày cả năm, chi phí đặt +20%, lưu kho +15%) → CSDL, `reports/do_nhay.md`, hình k07. Bổ sung 10 hạn chế "kho thật cần mà mô hình chưa có" vào `docs/10` mục 13.
17. (31/10/2026) Nâng cấp dự báo vòng 3 (`src/nang_cap_du_bao.py`, luật ghi trước ở `docs/10` mục 9.4): dự báo theo tầm + lịch sự kiện / âm lịch giữ, dò tham số bỏ; mô hình dùng tiếp `ket_hop_v3`. Tồn kho: Fill Rate tăng nhưng tồn và chi phí liên quan tăng nhẹ (nút thắt là quy tắc đặt hàng cho hàng thời vụ). `ton_kho.py` đọc mô hình chọn từ CSDL.
16. (24/10/2026) Dữ liệu được coi là kho tổng chuỗi siêu thị / bách hóa; cập nhật giá theo giá bán lẻ thị trường (`src/cap_nhat_gia.py`, nguồn `data/reference/gia_thi_truong.csv`): 37/121 mã đổi giá, giá vốn giữ biên lãi cũ (giả định). Chạy lại từ bước đặc trưng (`src/cham_lai.py` chấm lại mô hình không dùng giá). Mô hình chọn không đổi; kết luận chính không đổi. Chi tiết `docs/10` mục 2.1.

## 4. Kết quả làm sạch (đã chạy)
- Loại 198 dòng trùng; sửa 687 dòng (530 thiếu `qty_out`, 157 nhập sai gấp 10 hoặc 100 lần).
- Cách sửa: dựa vào đẳng thức kho, xuất = tồn đầu + nhập − tồn cuối.
- Đối chiếu đáp án: 0 dòng còn sai. Đủ 132.616 dòng, tồn không âm, không xuất hàng ngày kho đóng cửa.
- Cờ hết hàng: 4.225 dòng (3,19%), đặt theo quy tắc tồn cuối ngày = 0. Đối chiếu đáp án: bắt đủ 4.050/4.050 ngày hết hàng thật, thêm 175 ngày tồn về 0 nhưng vẫn đủ hàng cho khách (cờ thừa, an toàn vì chỉ loại bớt dữ liệu).
- Nhật ký lỗi ghi 689 lỗi (thiếu + nhập sai) nhưng chỉ có 687 ô bị lỗi: 2 ô (SKU026 ngày 07/11/2024, SKU035 ngày 24/07/2025) bị ghi cả "nhập sai" lẫn "thiếu" (lỗi sau đè lỗi trước). Script đã sửa đủ 687/687 ô.
- Điều kiện của cách sửa này: cột tồn cuối ngày phải đáng tin. Với dữ liệu thật phải kiểm chéo thêm với chứng từ.

## 5. Điều đã kiểm chứng và điều là giả định
- **Kiểm chứng từ nguồn:** ngày bão Yagi (07/09/2024); danh sách bão 2025 từ bão số 3 Wipha (22/7) đến bão số 15 Koto (3/12), lấy từ Wikipedia.
- **Giả định (mô phỏng):** mức độ mạnh của bão, mọi hệ số tác động, các cú sốc khác, mọi mức tác động ở sheet chi phí.
- **Giả định về giá (24/10):** giá bán = giá bán lẻ tra công khai ngày 24/10/2026 (37 mã; nguồn từng mã trong `data/reference/gia_thi_truong.csv`), 84 mã giữ giá mô phỏng; giá vốn = giá bán ÷ (1 + biên lãi cũ), không phải giá nhập thật.
- **Giả định của thử độ nhạy (`src/do_nhay.py`):** mức trễ tắc cảng 3/5/7 ngày trong 3 tuần, lead time +2 ngày, chi phí đặt +20%, lưu kho +15% lấy theo `docs/07` (không phải số liệu thật); mọi SKU cùng bị tắc cảng.
- **Nguồn bên thứ ba, chưa kiểm chứng chính thức:** lịch sale sàn (bài viết của một nhà bán lẻ). Chỉ 11.11, 12.12 và Black Friday có hiệu ứng trong dữ liệu mô phỏng; các sale còn lại chỉ là lịch tham khảo.
- Black Friday là thứ Sáu thứ tư của tháng 11.
- Sheet `Huong_dan` trong file Excel từng ghi nhầm "108 SKU"; số đúng là **121**.

### Điểm chưa nhất quán giữa các tài liệu (cần sửa khi viết báo cáo)
- Tỷ lệ hết hàng: sheet `Huong_dan` (docs/03) ghi ~1,8%; số đo trên đáp án là **3,05%** (cờ bản sạch 3,19%).
- Cửa sổ bão: docs/03 ghi "3 ngày trước đến 14 ngày sau" (khớp `lower_window=-3, upper_window=14`), còn `Su_kien_dot_bien` ghi `den_ngay` = ngày bão + 10 và sheet `Bao_lu_x_SKU` đo 3 ngày trước, 10 ngày sau. Khi làm đặc trưng, thống nhất dùng −3…+14.
- ~~`khuyen_mai` không tái tạo được~~ → **Đã xử lý 10/10/2026:** thêm `data/reference/lich_khuyen_mai.csv` (1.338 đợt, 121 SKU, mỗi đợt 5–21 ngày). Dựng lại cờ từ lịch này khớp đáp án 132.616/132.616 dòng. Ngoài đời, lịch này tương ứng kế hoạch khuyến mãi bộ phận bán hàng gửi trước cho kho.
- Lịch nghỉ Tết trong dữ liệu là 7 ngày cố định (giả định), không đúng hoàn toàn lịch nghỉ chính thức từng năm.

## 6. Việc tiếp theo (đề xuất, chưa làm)
Lộ trình chi tiết từng giai đoạn, checklist và quyết định cần chốt: `docs/09_lo_trinh.md`.

1. ~~`src/dac_trung.py`, `src/eda.py`, `src/danh_gia.py`~~ (xong 10/10). GĐ C mô hình mốc xong 23/10 (`src/mo_hinh_baseline.py`; mốc tốt nhất TB trượt 28 ngày, WMAPE test 0,640). Prophet xong 24/10 (test WMAPE 0,454); LightGBM xong 24/10 (0,399, Bias +11,7%). GĐ E xong 24/10; vòng 3 (31/10) nâng cấp thành `ket_hop_v3` (test WMAPE 0,368, Bias +3,9%). GĐ F: Fill Rate 95,91%, chi phí liên quan −28,3% so với dự báo mốc (mô hình v3, giá thị trường). GĐ G dashboard xong 23/10 (`streamlit run app/dashboard.py`). Tiếp theo: viết Chương 2–5.
2. Chia train/validation/test theo thời gian; backtest cuốn chiếu.
3. Chạy baseline (Naive, Seasonal Naive, trung bình trượt, ETS), Prophet, XGBoost; hàng bán thưa dùng Croston/TSB; LSTM chỉ khi đủ dữ liệu.
4. Đo MAE, RMSE, WMAPE, MASE, Bias; so sánh theo nhóm ABC/XYZ; điền `Bang_so_sanh`.
5. Từ dự báo tính SS, ROP, EOQ (σd = độ lệch chuẩn sai số dự báo); mô phỏng chính sách tồn kho và so sánh KPI (Fill Rate, Stockout, DOH).
5b. ~~Dashboard và bảng so sánh "trước – sau"~~ (xong 23/10, Streamlit). Còn: chọn 2–3 màn hình dashboard đưa vào slide bảo vệ.
6. Chưa làm: đưa vào dữ liệu mô phỏng các sự kiện chi phí (tăng giá xăng, tắc cảng), nguyên nhân phi thời tiết (rằm, mùng 1, nghỉ lễ dài, ngày lương, SKU mới và ngừng bán), và hiệu ứng của toàn bộ 12 ngày sale.
7. Khi có dữ liệu thật: thay file raw, giữ tên cột, chạy lại `lam_sach.py`.
