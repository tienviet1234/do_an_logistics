# Bieu do ket qua (Chuong 4)

Dữ liệu mô phỏng, không phải số liệu kho thật. Hinh luu o `reports/ket_qua/`.

- `k01_xep_hang_mo_hinh.png`: AI được chọn sai 36,8%, mô hình mốc tốt nhất (TB trượt 28) 64,0%, Seasonal Naive 77,3%.
- `k02_du_bao_vs_thuc_te_tet.png`: TB trượt 28 ngày dự báo phẳng, không thấy đỉnh trước Tết/Trung thu; AI bám được đỉnh. Ngày thiếu dữ liệu tin được (kho đóng cửa dịp Tết) để trống.
- `k03_sai_so_theo_nhom.png`: Lợi ích lớn nhất của AI ở nhóm mùa vụ Z (TB trượt 127% → AI 55%); nhóm ổn định X chênh ít hơn.
- `k04_ton_kho_theo_thoi_gian.png`: Tồn kho theo thời gian của 4 chính sách; các đỉnh trước Tết là hàng chuẩn bị cho mùa cao điểm.
- `k05_truoc_sau.png`: Chi phí liên quan = đặt hàng + lưu kho + lợi nhuận mất do thiếu hàng. Cùng công thức, AI giảm 28% so với dự báo mốc.
- `k06_rang_cua_sku001.png`: Mỗi khi tồn + hàng đang về chạm ROP thì đặt hàng; ROP tăng trước Tết theo dự báo. Minh họa thực tế cho lý thuyết EOQ/ROP ở Chương 2.
- `k07_do_nhay_lead_time.png`: Tắc cảng tạm thời chỉ làm Fill Rate giảm 0,5–1,5 điểm và AI + hiệu chỉnh vẫn rẻ nhất ở mọi đợt; lead time dài ra lâu dài mà không cập nhật công thức thì giảm 5 điểm, cập nhật thì gần như hồi phục.
