# Bieu do ket qua (Chuong 4)

Dữ liệu mô phỏng, không phải số liệu kho thật. Hinh luu o `reports/ket_qua/`.

- `k01_xep_hang_mo_hinh.png`: AI được chọn (cập nhật mỗi tuần) sai 35,6% (cùng mô hình cập nhật mỗi 28 ngày: 36,8%); mốc TB trượt 28 ngày cập nhật mỗi tuần 58,4% (mỗi 28 ngày: 64,0%); Seasonal Naive 77,3%. Hai mô hình cập nhật mỗi tuần chấm trên bản mới nhất cho mỗi ngày (cách dùng thật); các mô hình khác chấm trên mốc 28 ngày × 28 ngày.
- `k02_du_bao_vs_thuc_te_tet.png`: TB trượt 28 ngày dự báo phẳng, không thấy đỉnh trước Tết/Trung thu; AI bám được đỉnh. Ngày thiếu dữ liệu tin được (kho đóng cửa dịp Tết) để trống.
- `k03_sai_so_theo_nhom.png`: Lợi ích lớn nhất của AI ở nhóm mùa vụ Z (TB trượt 112% → AI 48%); nhóm ổn định X chênh ít hơn (39% → 31%).
- `k04_ton_kho_theo_thoi_gian.png`: Tồn kho theo thời gian của 4 chính sách; các đỉnh trước Tết là hàng chuẩn bị cho mùa cao điểm.
- `k05_truoc_sau.png`: Chi phí liên quan = đặt hàng + lưu kho + lợi nhuận mất do thiếu hàng. Cùng công thức, AI giảm 35% so với dự báo mốc.
- `k06_rang_cua_sku001.png`: Mỗi khi tồn + hàng đang về chạm ROP thì đặt hàng; ROP tăng trước Tết theo dự báo. Minh họa thực tế cho lý thuyết EOQ/ROP ở Chương 2.
- `k07_do_nhay_lead_time.png`: Tắc cảng tạm thời chỉ làm Fill Rate giảm 0,5–1,5 điểm và AI + hiệu chỉnh vẫn rẻ nhất ở mọi đợt; lead time dài ra lâu dài mà không cập nhật công thức thì giảm 5 điểm, cập nhật thì gần như hồi phục.
