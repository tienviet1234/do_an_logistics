# Bang so sanh mo hinh (tap test)

WMAPE: thap hon = tot hon. FVA: muc giam sai so so voi Seasonal Naive 7 (duong = tot hon).
Mo hinh chi chay mot nhom SKU (vd ARIMA chi nhom A) chi co cot cua nhom do; so sanh qua WMAPE_A.
Du lieu mo phong, khong phai so lieu kho that.

| Mo hinh | So SKU | WMAPE | WMAPE_tuan | Bias_pct | WMAPE_A | WMAPE_X | WMAPE_Y | WMAPE_Z | WMAPE_erratic | WMAPE_lumpy | WMAPE_smooth | FVA_vs_SN7 | FVA_A_vs_SN7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tb_truot_28 | 121 | 0,640 | 0,511 | -0,008 | 0,503 | 0,408 | 0,653 | 1,272 | 1,010 | 1,860 | 0,398 | 0,172 | 0,101 |
| croston_sba | 121 | 0,651 | 0,516 | 0,004 | 0,492 | 0,395 | 0,589 | 1,365 | 1,051 | 2,184 | 0,383 | 0,158 | 0,120 |
| tsb | 121 | 0,686 | 0,549 | -0,065 | 0,504 | 0,410 | 0,555 | 1,477 | 1,116 | 2,476 | 0,394 | 0,112 | 0,099 |
| ets | 121 | 0,721 | 0,614 | -0,167 | 0,531 | 0,428 | 0,527 | 1,574 | 1,203 | 2,291 | 0,406 | 0,068 | 0,050 |
| naive | 121 | 0,739 | 0,634 | -0,091 | 0,541 | 0,491 | 0,639 | 1,442 | 1,128 | 2,408 | 0,473 | 0,044 | 0,032 |
| seasonal_naive_7 | 121 | 0,773 | 0,598 | -0,110 | 0,559 | 0,475 | 0,597 | 1,636 | 1,243 | 2,691 | 0,455 | 0,000 | 0,000 |
| arima | 31 | — | — | — | 0,493 | — | — | — | — | — | — | — | 0,118 |
