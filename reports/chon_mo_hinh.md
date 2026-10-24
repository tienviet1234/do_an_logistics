# Chon mo hinh (GD E)
Tap dung de chon: validation.

Trong so LightGBM do tren validation: toan kho w = 0.9; theo nhom {'X': 0.9, 'Y': 0.7, 'Z': 1.0}.
Luat: WMAPE validation thap nhat, chenh duoi 0.005 thi chon phuong an don gian hon. **Duoc chon: lightgbm**.
Cac cot test chi de bao cao, KHONG dung de chon. Bias duong = du bao thieu. Du lieu mo phong.

| ung_vien | trong_so_LightGBM | val_WMAPE | val_Bias | test_WMAPE | test_WMAPE_tuan | test_Bias | test_WMAPE_Z | test_Bias_Z | duoc_chon |
|---|---|---|---|---|---|---|---|---|---|
| prophet | 0.0 | 0,434 | -0,032 | 0,454 | 0,257 | -0,049 | 0,638 | -0,097 |  |
| lightgbm | 1.0 | 0,353 | 0,048 | 0,399 | 0,269 | 0,117 | 0,638 | 0,402 | ✅ |
| trung_binh | 0.5 | 0,374 | 0,008 | 0,388 | 0,235 | 0,034 | 0,544 | 0,153 |  |
| ket_hop_toan_kho | 0.9 | 0,353 | 0,040 | 0,389 | 0,258 | 0,101 | 0,601 | 0,352 |  |
| ket_hop_theo_nhom | {'X': 0.9, 'Y': 0.7, 'Z': 1.0} | 0,351 | 0,042 | 0,399 | 0,268 | 0,113 | 0,638 | 0,402 |  |
