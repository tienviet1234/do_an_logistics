# Chon mo hinh (GD E)

Trong so LightGBM do tren validation: toan kho w = 1.0; theo nhom {'X': 0.9, 'Y': 0.8, 'Z': 1.0}.
Luat: WMAPE validation thap nhat, chenh duoi 0.005 thi chon phuong an don gian hon. **Duoc chon: lightgbm**.
Cac cot test chi de bao cao, KHONG dung de chon. Bias duong = du bao thieu. Du lieu mo phong.

| ung_vien | trong_so_LightGBM | val_WMAPE | val_Bias | test_WMAPE | test_WMAPE_tuan | test_Bias | test_WMAPE_Z | test_Bias_Z | duoc_chon |
|---|---|---|---|---|---|---|---|---|---|
| prophet | 0.0 | 0,434 | -0,032 | 0,454 | 0,257 | -0,049 | 0,638 | -0,097 |  |
| lightgbm | 1.0 | 0,351 | 0,047 | 0,400 | 0,270 | 0,116 | 0,643 | 0,408 | ✅ |
| trung_binh | 0.5 | 0,373 | 0,007 | 0,388 | 0,236 | 0,034 | 0,545 | 0,156 |  |
| ket_hop_toan_kho | 1.0 | 0,351 | 0,047 | 0,400 | 0,270 | 0,116 | 0,643 | 0,408 |  |
| ket_hop_theo_nhom | {'X': 0.9, 'Y': 0.8, 'Z': 1.0} | 0,350 | 0,042 | 0,400 | 0,269 | 0,112 | 0,643 | 0,408 |  |
