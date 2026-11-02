# Nâng cấp dự báo vòng 4 (GĐ E): rủi ro, tự hiệu chỉnh, cập nhật hằng tuần, khoảng dự báo

Luật ghi trước khi chạy: `docs/10` mục 9.5 (kèm bổ sung trước B2). Chọn và báo cáo trên **validation2**; **test giữ kín** (không chạy, không chấm). Mọi bước học từ sai số chỉ dùng dữ liệu đã có thực tế tại mốc. Dữ liệu mô phỏng.

## Mức sai số tối thiểu (đối chiếu)

Nếu biết đúng nhu cầu kỳ vọng từng ngày, WMAPE theo ngày vẫn còn khoảng **0.286** (X 0.268 · Y 0.31 · Z 0.341) do nhu cầu ngẫu nhiên (nhị thức âm). Phiên bản cuối: **0.358**.

## Kết quả từng bước (validation2)

| Bước | WMAPE | Bias | So với phiên bản đang giữ | Theo luật |
|---|---|---|---|---|
| Đang giữ: `ket_hop_v3` | 0.3792 | 7.1% | | |
| B1 – tự hiệu chỉnh lệch từ sai số đã qua | 0.3831 | 3.5% | 0.3792 / 7.1% (41,263 dòng) | ❌ bỏ |
| B2 – cảnh báo bão 4 ngày trước | 0.3836 | 5.8% | 0.3792 / 7.1% (41,263 dòng) | ❌ bỏ |
| B3 – cập nhật dự báo mỗi tuần (bản mới nhất mỗi ngày) | 0.3578 | 5.5% | 0.3792 / 7.1% (41,263 dòng) | ✅ giữ |

Riêng cửa sổ bão (B2): WMAPE 0.450 → 0.483, Bias 24.3% → 14.2%. Hệ số học được theo nhóm hàng dao động rộng (xem `hoc` trong file trạng thái): 1–2 trận bão là quá ít để học hệ số ổn định.

**Tồn kho validation2** (AI + hiệu chỉnh, EOQ, 95%; giữ hệ số hiệu chỉnh và σ của v3):

| Dự báo | Fill Rate | Tồn TB (tr đ) | CP đặt + lưu | LN mất | CP liên quan |
|---|---|---|---|---|---|
| v3, mỗi 28 ngày | 94.83% | 14,675.1 | 3,457.3 | 2,059.5 | 5,516.8 |
| đang giữ, mỗi 28 ngày | 94.83% | 14,675.1 | 3,457.3 | 2,059.5 | 5,516.8 |
| cập nhật mỗi tuần | 96.44% | 10,742.9 | 2,656.4 | 1,648.9 | 4,305.3 |

## B4 – Khoảng dự báo (tính từ mốc 2024-11-25, chỉ học từ mốc trước)

| Mức | Theo ngày: tỉ lệ thực tế nằm trong khoảng | Độ rộng (trung vị, × dự báo) | Tổng lead time: tỉ lệ nằm trong khoảng | Độ rộng |
|---|---|---|---|---|
| 80% | 79.7% (X 79 · Y 81 · Z 81) | 1.04 | 77.4% | 0.53 |
| 95% | 95.7% (X 95 · Y 95 · Z 98) | 1.77 | 93.5% | 0.88 |

Theo luật (lệch ≤ ±3 điểm so với danh nghĩa): **đạt**.

## Ví dụ: con số dự báo kèm khoảng (validation2, sữa tươi Vinamilk SKU009, 7 ngày sau mốc 20/01/2025, trước Tết)

| Ngày | Dự báo | Khoảng 80% | Khoảng 95% | Thực tế | Trong khoảng 80% |
|---|---|---|---|---|---|
| 21/01 | 433 | 236–677 | 153–912 | 283 | ✓ |
| 22/01 | 398 | 217–623 | 141–839 | 235 | ✓ |
| 23/01 | 295 | 161–462 | 104–622 | 263 | ✓ |
| 24/01 | 355 | 193–555 | 125–748 | 423 | ✓ |
| 25/01 | 356 | 194–556 | 126–749 | 320 | ✓ |
| 26/01 | 184 | 100–287 | 65–387 | 138 | ✓ |
| 27/01 | 350 | 190–547 | 124–737 | 286 | ✓ |

Tổng nhu cầu trong thời gian chờ hàng (3 ngày): dự báo **1,127**, khoảng 80% 872–1,454, khoảng 95% 747–1,708; thực tế **781**.

## Test (mở 31/10 theo quyết định người dùng; chạy một lần, chỉ báo cáo — luật `docs/10` mục 9.6)

| Test | WMAPE | Bias | WMAPE tuần | Nhóm Z | Nhóm X | WMAPE lead time |
|---|---|---|---|---|---|---|
| `ket_hop_v4` (cập nhật mỗi tuần, bản mới nhất) | **0.3559** | 3.0% | 0.2033 | 0.4767 | 0.3095 | 0.2136 |
| `ket_hop_v3` (mỗi 28 ngày), cùng các dòng | 0.3683 | 3.9% | | | | 0.2331 |
| Mốc TB trượt 28 ngày, cập nhật mỗi tuần | 0.5838 | -0.2% | | | | |

Khoảng dự báo trên test (học online từ validation2 rồi các mốc test trước; tính từ mốc 2025-09-30):

| Mức | Theo ngày (bản mới nhất) | Độ rộng | Tổng lead time | Độ rộng |
|---|---|---|---|---|
| 80% | 80.9% | 1.06 | 81.3% | 0.55 |
| 95% | 96.0% | 1.82 | 95.5% | 0.97 |

## Bảng rủi ro

Xem `reports/rui_ro_du_bao.md` (định lượng từ dữ liệu đến 30/09/2025).

## Nhật ký

- ['B1', 'ket_hop_v3']
- ['B2', 'ket_hop_v3']
- ['B2', 'ket_hop_v3']
- ['B3', 'v4_B3']
- ['B4', 'v4_B3']
- ['test', 'v4_B3']

B2 chạy 2 lần: lần đầu có lỗi code (điều kiện "dữ liệu phủ hết cửa sổ" so với ngày kết thúc SAU bão nên giai đoạn "trước bão" không được học, hệ số = 1); lần 2 sau khi sửa. Kết luận như nhau: bỏ (WMAPE 0,3820 rồi 0,3836).
