# Chon mo hinh (GD E) - vong 2
Tap dung de chon: validation2.

Trong so LightGBM do tren validation: toan kho w = 0.8; theo nhom {'X': 0.9, 'Y': 1.0, 'Z': 0.6}.
Luat: WMAPE validation thap nhat, chenh duoi 0.005 thi chon phuong an don gian hon. **Duoc chon: ket_hop_theo_nhom**.
Cac cot test chi de bao cao, KHONG dung de chon. Bias duong = du bao thieu. Du lieu mo phong.

| ung_vien | trong_so_LightGBM | val_WMAPE | val_Bias | test_WMAPE | test_WMAPE_tuan | test_Bias | test_WMAPE_Z | test_Bias_Z | duoc_chon |
|---|---|---|---|---|---|---|---|---|---|
| prophet | 0.0 | 0,488 | -0,014 | 0,454 | 0,257 | -0,049 | 0,638 | -0,097 |  |
| lightgbm | 1.0 | 0,403 | 0,129 | 0,399 | 0,269 | 0,117 | 0,638 | 0,402 |  |
| trung_binh | 0.5 | 0,408 | 0,058 | 0,388 | 0,235 | 0,034 | 0,544 | 0,153 |  |
| ket_hop_toan_kho | 0.8 | 0,394 | 0,100 | 0,383 | 0,250 | 0,084 | 0,574 | 0,302 |  |
| ket_hop_theo_nhom | {'X': 0.9, 'Y': 1.0, 'Z': 0.6} | 0,388 | 0,079 | 0,375 | 0,234 | 0,063 | 0,546 | 0,203 | ✅ |
