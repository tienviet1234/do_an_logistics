# TiDE, N-HiTS, TFT

Luật ghi trước: docs/10 mục 9.9. Quyết định chỉ dựa trên validation2. Mô hình đang dùng: ket_hop_v4.

| Mô hình | Validation2 WMAPE | Validation2 Bias | Test WMAPE | Test Bias |
|---|---:|---:|---:|---:|
| ket_hop_v4 | 0.358 | +5.5% | 0.356 | +3.0% |
| tide | 0.465 | +18.7% | 0.477 | +17.8% |
| nhits | 0.478 | +0.5% | 0.429 | +11.4% |
| tft | 0.412 | +16.9% | 0.425 | +17.1% |
| ket_hop_nf | 0.352 | +7.3% | 0.354 | +5.0% |

Quyết định: **ket_hop_v4** (trọng số ghép theo nhóm {'X': 0.5, 'Y': 0.3, 'Z': 0.0}, ghép với tft).
