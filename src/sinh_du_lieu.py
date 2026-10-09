"""Du lieu dau vao v2: ~100 SKU, 36 thang, mua vu 4 mua + cac ngay le (Viet Nam).
Chay: python gen2.py <thu_muc_ra>
"""
import sys, os
import numpy as np, pandas as pd

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261009)
START, END = pd.Timestamp("2023-10-01"), pd.Timestamp("2026-09-30")
dates = pd.date_range(START, END, freq="D"); T = len(dates)
doy = np.array([d.dayofyear for d in dates])
dow_idx = np.array([d.weekday() for d in dates])
D = lambda s: pd.Timestamp(s)

# ---------------- Su kien / ngay le ----------------
EVENTS = {  # ten: (danh_sach_ngay, so_ngay_truoc, dinh_truoc_ngay_le, do_rong, ghi_chu)
 "tet": ([D("2024-02-10"), D("2025-01-29"), D("2026-02-17")], 28, 6, 10, "Tết Nguyên đán (mùng 1, âm lịch)"),
 "trung_thu": ([D("2024-09-17"), D("2025-10-06"), D("2026-09-25")], 25, 7, 8, "Tết Trung thu (rằm tháng 8)"),
 "valentine": ([D(f"{y}-02-14") for y in (2024, 2025, 2026)], 10, 2, 4, "Valentine 14/2"),
 "quoc_te_phu_nu": ([D(f"{y}-03-08") for y in (2024, 2025, 2026)], 10, 2, 4, "Quốc tế Phụ nữ 8/3"),
 "thieu_nhi": ([D(f"{y}-06-01") for y in (2024, 2025, 2026)], 10, 2, 4, "Quốc tế Thiếu nhi 1/6"),
 "le_30_4_2_9": ([D(f"{y}-04-30") for y in (2024, 2025, 2026)] + [D(f"{y}-09-02") for y in (2024, 2025, 2026)],
                 7, 2, 3, "Lễ 30/4 và 2/9 (đi chơi, tiệc tụ họp)"),
 "khai_giang": ([D(f"{y}-09-05") for y in (2024, 2025, 2026)], 22, 8, 7, "Khai giảng năm học 5/9"),
 "phu_nu_vn": ([D(f"{y}-10-20") for y in (2023, 2024, 2025)], 8, 1, 3, "Phụ nữ Việt Nam 20/10"),
 "halloween": ([D(f"{y}-10-31") for y in (2023, 2024, 2025)], 12, 3, 4, "Halloween 31/10"),
 "nha_giao": ([D(f"{y}-11-20") for y in (2023, 2024, 2025)], 8, 1, 3, "Ngày Nhà giáo 20/11"),
 "noel": ([D(f"{y}-12-24") for y in (2023, 2024, 2025)], 20, 3, 7, "Giáng sinh 24/12"),
}
EV_BUMP = {}
for name, (ds, pre, peak, sig, _) in EVENTS.items():
    b = np.zeros(T)
    for d0 in ds:
        i0 = (d0 - START).days
        for k in range(-pre, 1):
            j = i0 + k
            if 0 <= j < T: b[j] = max(b[j], np.exp(-((k + peak) / sig) ** 2))
    EV_BUMP[name] = b
tet_post = np.zeros(T)
for d0 in EVENTS["tet"][0]:
    i0 = (d0 - START).days
    for k in range(1, 15):
        j = i0 + k
        if 0 <= j < T: tet_post[j] = np.exp(-k / 8.0)


# ---------------- Cu soc nhu cau (khong lap theo lich) ----------------
def wbump(st, en, ramp=2, tail=3):
    b = np.zeros(T); i0 = (D(st) - START).days; i1 = (D(en) - START).days
    for j in range(max(0, i0 - ramp), min(T, i1 + tail + 1)):
        if j < i0: b[j] = (j - (i0 - ramp) + 1) / (ramp + 1)
        elif j <= i1: b[j] = 1.0
        else: b[j] = max(0.0, 1 - (j - i1) / (tail + 1))
    return b
# Ngay do bo/cao diem lu theo cac nguon cong khai; MUC DO anh huong len kho la gia dinh (0-1).
STORMS = [
 ("Bão số 3 Yagi", "2024-09-07", 1.0, "Thực tế (ngày); mức độ giả định", "Đổ bộ Hải Phòng–Quảng Ninh, lũ miền Bắc 8–12/9/2024, đường sắt và giao thông gián đoạn"),
 ("Bão số 3 Wipha", "2025-07-22", 0.5, "Thực tế (ngày); mức độ giả định", "Đổ bộ Hưng Yên–Ninh Bình, mưa lớn Bắc Bộ và Bắc Trung Bộ"),
 ("Bão số 5 Kajiki", "2025-08-25", 0.6, "Thực tế (cuối tháng 8); mức độ giả định", "Đổ bộ Nghệ An–Hà Tĩnh–Quảng Trị, Hà Nội ngập sâu ngày 26/8"),
 ("Bão số 9 Ragasa", "2025-09-25", 0.3, "Thực tế (ngày); mức độ giả định", "Ảnh hưởng gián tiếp, mưa diện rộng"),
 ("Bão số 10 Bualoi", "2025-09-29", 0.7, "Thực tế (ngày); mức độ giả định", "Bắc Trung Bộ"),
 ("Bão số 11 Matmo", "2025-10-06", 0.8, "Thực tế (ngày); mức độ giả định", "Mưa lũ Thái Nguyên, Bắc Ninh, Cao Bằng, Lạng Sơn"),
 ("Bão số 12 và lũ miền Trung", "2025-10-23", 0.6, "Thực tế (ngày); mức độ giả định", "Lũ Huế, Đà Nẵng cuối tháng 10/2025"),
 ("Bão số 13 Kalmaegi", "2025-11-06", 0.7, "Thực tế (ngày); mức độ giả định", "Lũ Gia Lai, Đắk Lắk, Khánh Hòa"),
 ("Bão số 15 Koto", "2025-12-03", 0.3, "Thực tế (ngày); mức độ giả định", "Lũ Khánh Hòa, Lâm Đồng đầu tháng 12/2025"),
]
STORM_CLOSE = ["2024-09-07", "2024-09-08"]
f_pre = {-3: .4, -2: .8, -1: 1.0, 0: .3}
storm_pre = np.zeros(T); storm_post = np.zeros(T); storm_dip = np.zeros(T)
lt_extra = np.zeros(T); storm_level = np.zeros(T)
for (nm, ld, I, _, _) in STORMS:
    i0 = (D(ld) - START).days
    for k, w in f_pre.items():
        if 0 <= i0 + k < T: storm_pre[i0 + k] += I * w
    for k in range(1, 15):
        if 0 <= i0 + k < T: storm_post[i0 + k] += I * (k / 3) * np.exp(1 - k / 3)
    for k in range(-1, 8):
        if 0 <= i0 + k < T: storm_dip[i0 + k] = max(storm_dip[i0 + k], I)
    for k in range(-1, 11):
        if 0 <= i0 + k < T: lt_extra[i0 + k] = max(lt_extra[i0 + k], round(3 * I))
    for k in range(-3, 15):
        if 0 <= i0 + k < T: storm_level[i0 + k] = max(storm_level[i0 + k], I)
storm_pre = np.minimum(storm_pre, 1.5); storm_post = np.minimum(storm_post, 1.5)
EV_BUMP["bao_tru"] = storm_pre; EV_BUMP["bao_cuu_tro"] = storm_post

OTHER = [  # (khoa, ten, tu, den, nguon, ghi_chu)
 ("nang_nong", "Nắng nóng diện rộng", "2024-05-01", "2024-05-10", "Mô phỏng", "Đợt nóng điển hình, nước giải khát, kem, quạt tăng"),
 ("nang_nong", "Nắng nóng diện rộng", "2024-06-18", "2024-06-27", "Mô phỏng", ""),
 ("nang_nong", "Nắng nóng diện rộng", "2025-05-20", "2025-05-28", "Mô phỏng", ""),
 ("nang_nong", "Nắng nóng diện rộng", "2026-06-20", "2026-06-30", "Mô phỏng", ""),
 ("ret_dam", "Rét đậm, rét hại", "2024-01-21", "2024-01-28", "Mô phỏng", "Chăn, máy sưởi, miếng dán, đồ lẩu tăng"),
 ("ret_dam", "Rét đậm, rét hại", "2024-12-14", "2024-12-21", "Mô phỏng", ""),
 ("ret_dam", "Rét đậm, rét hại", "2025-01-08", "2025-01-15", "Mô phỏng", ""),
 ("ret_dam", "Rét đậm, rét hại", "2025-12-18", "2025-12-27", "Mô phỏng", ""),
 ("ret_dam", "Rét đậm, rét hại", "2026-01-10", "2026-01-17", "Mô phỏng", ""),
 ("tin_don_gia", "Tin đồn tăng giá, tích trữ", "2024-05-13", "2024-05-19", "Mô phỏng", "Người mua mua trước vì sợ tăng giá, sau đó nhu cầu tụt (kéo nhu cầu về trước)"),
 ("tin_don_gia", "Tin đồn tăng giá, tích trữ", "2025-03-10", "2025-03-16", "Mô phỏng", ""),
 ("tin_don_gia", "Tin đồn tăng giá, tích trữ", "2025-11-17", "2025-11-23", "Mô phỏng", ""),
 ("dich_cum", "Đợt cúm, bệnh hô hấp", "2023-12-04", "2024-01-14", "Mô phỏng", "Khẩu trang, nước rửa tay, dầu gió tăng"),
 ("dich_cum", "Đợt cúm, bệnh hô hấp", "2024-12-02", "2025-01-12", "Mô phỏng", ""),
 ("dich_cum", "Đợt cúm, bệnh hô hấp", "2025-11-24", "2026-01-04", "Mô phỏng", ""),
 ("sot_xuat_huyet", "Cao điểm sốt xuất huyết", "2024-08-05", "2024-10-13", "Mô phỏng", "Bình xịt, nhang muỗi, ORS tăng"),
 ("sot_xuat_huyet", "Cao điểm sốt xuất huyết", "2025-08-04", "2025-10-12", "Mô phỏng", ""),
]
SPORTS = [("Euro 2024", "2024-06-14", "2024-07-14"), ("AFF Cup 2024", "2024-12-08", "2025-01-05"), ("World Cup 2026", "2026-06-11", "2026-07-19")]
for k in {o[0] for o in OTHER}:
    b = np.zeros(T)
    for (kk, nm, st, en, _, _) in OTHER:
        if kk != k: continue
        w = wbump(st, en, ramp=1 if k in ("dich_cum", "sot_xuat_huyet") else 2, tail=4 if k in ("dich_cum", "sot_xuat_huyet") else 3)
        if k == "tin_don_gia":
            w = wbump(st, en, ramp=1, tail=1) - 0.3 * wbump((D(en) + pd.Timedelta(days=3)).strftime("%Y-%m-%d"), (D(en) + pd.Timedelta(days=12)).strftime("%Y-%m-%d"), 0, 0)
        b = b + w if k == "tin_don_gia" else np.maximum(b, w)
    EV_BUMP[k] = b
EV_BUMP["the_thao"] = np.maximum.reduce([wbump(a, b, 1, 1) for _, a, b in SPORTS])
SHOCK_KEYS = {"bao_tru", "bao_cuu_tro", "nang_nong", "ret_dam", "tin_don_gia", "dich_cum", "sot_xuat_huyet"}
SUPPLIER_OUT = [("NCC03", "2024-05-20", "2024-06-03", 10), ("NCC07", "2025-02-24", "2025-03-10", 9), ("NCC11", "2025-11-03", "2025-11-17", 8)]
sup_extra = {}
for ncc, st, en, add in SUPPLIER_OUT:
    a_ = sup_extra.setdefault(ncc, np.zeros(T)); i0 = (D(st) - START).days; i1 = (D(en) - START).days
    a_[max(0, i0):min(T, i1 + 1)] = add
DIP_GROUPS = {"Quà tặng", "Trang trí", "Đồ chơi", "Kem & đông lạnh"}

# ngay nghi kho
nghi = []
for d0 in EVENTS["tet"][0]:
    for k in range(-1, 6): nghi.append((d0 + pd.Timedelta(days=k), "Nghỉ Tết Nguyên đán"))
for y in (2023, 2024, 2025, 2026):
    for md, nm in (("01-01", "Tết Dương lịch"), ("04-30", "Giải phóng miền Nam"), ("05-01", "Quốc tế Lao động"), ("09-02", "Quốc khánh")):
        nghi.append((D(f"{y}-{md}"), nm))
for s in ("2024-04-18", "2025-04-07", "2026-04-26"): nghi.append((D(s), "Giỗ Tổ Hùng Vương"))
for s in STORM_CLOSE: nghi.append((D(s), "Đóng cửa do bão Yagi"))
cal_nghi = pd.DataFrame(nghi, columns=["date", "ten_ngay_nghi"]).drop_duplicates("date")
cal_nghi = cal_nghi[(cal_nghi.date >= START) & (cal_nghi.date <= END)].sort_values("date").reset_index(drop=True)
closed = set(cal_nghi.date)
tet_nghi = set(cal_nghi.loc[cal_nghi.ten_ngay_nghi == "Nghỉ Tết Nguyên đán", "date"])

# bang holidays dinh dang Prophet
hol = []
for name, (ds, pre, peak, sig, note) in EVENTS.items():
    for d0 in ds:
        if START <= d0 <= END or START <= d0 + pd.Timedelta(days=-pre) <= END:
            hol.append((name, d0, -pre, 7 if name == "tet" else 1, note))
lich_su_kien = pd.DataFrame(hol, columns=["holiday", "ds", "lower_window", "upper_window", "ghi_chu"]).sort_values("ds")
_ext = []
for (nm, ld, I, ng, gc) in STORMS: _ext.append(("bao_" + nm.split()[-1].lower() + "_" + ld[:4], D(ld), -3, 14, f"{nm} ({ng})"))
for (kk, nm, st, en, ng, gc) in OTHER: _ext.append((kk, D(st), 0, (D(en) - D(st)).days, f"{nm} ({ng})"))
for nm, a, b in SPORTS: _ext.append(("the_thao", D(a), 0, (D(b) - D(a)).days, nm + " (lịch thi đấu chính thức)"))
lich_su_kien = pd.concat([lich_su_kien, pd.DataFrame(_ext, columns=lich_su_kien.columns)]).sort_values("ds").reset_index(drop=True)

# su kien kinh doanh toan he thong (nhe)
event_mult = np.ones(T)
for i, d in enumerate(dates):
    if (d.month, d.day) == (11, 11): event_mult[i] = 1.30
    if (d.month, d.day) == (12, 12): event_mult[i] = 1.20
    if d.month == 11 and d.weekday() == 4 and 22 <= d.day <= 28: event_mult[i] = 1.35  # Black Friday

# ---------------- Mua ----------------
def circ(center, sigma):
    dd = np.minimum(np.abs(doy - center), 365 - np.abs(doy - center))
    return np.exp(-(dd / sigma) ** 2)
def season(kind):
    if kind == "flat": return np.ones(T)
    if kind == "summer": return 1 + 0.35 * np.sin(2 * np.pi * (doy - 80) / 365)
    if kind == "winter": return 1 - 0.28 * np.sin(2 * np.pi * (doy - 80) / 365)
    if kind == "hot": return 0.12 + circ(176, 55)       # dinh cuoi thang 6
    if kind == "rainy": return 0.10 + circ(212, 45)     # dinh thang 7-8
    if kind == "cold": return 0.10 + circ(10, 50)       # dinh thang 12 - thang 1
    raise ValueError(kind)
def mua_of(d):  # mien Bac
    m = d.month
    return "Xuân" if m in (2, 3, 4) else "Hạ" if m in (5, 6, 7) else "Thu" if m in (8, 9, 10) else "Đông"
mua_arr = np.array([mua_of(d) for d in dates])

# ---------------- Danh muc SKU ----------------
# 30 ma hang quanh nam / mua nhe (tu ban v1): (ten, nhom, dv, gia_von, d, kind, tet, trend, LT, cv, extra_events)
tetmap = {"none": 0, "summer": 0, "winter": 0, "tet_nhe": .3, "tet": .65, "summer_tet": .45, "summer_tet_strong": .9, "tet_strong": 1.6}
v1 = [
 ("Mì gói Hảo Hảo thùng 30 gói", "Thực phẩm khô", "thùng", 105000, 220, "tet_nhe", .04, 5, .30),
 ("Mì ly Modern 24 ly", "Thực phẩm khô", "thùng", 168000, 70, "none", .02, 6, .35),
 ("Gạo ST25 túi 5kg", "Thực phẩm khô", "túi", 112000, 140, "tet", .03, 7, .28),
 ("Dầu ăn Simply chai 1L", "Thực phẩm khô", "chai", 52000, 260, "tet", 0, 4, .30),
 ("Đường tinh luyện 1kg", "Thực phẩm khô", "gói", 24500, 180, "tet", 0, 4, .30),
 ("Nước mắm Nam Ngư chai 750ml", "Gia vị", "chai", 38000, 150, "tet", .02, 5, .27),
 ("Nước tương Maggi chai 700ml", "Gia vị", "chai", 29000, 85, "tet_nhe", .01, 5, .30),
 ("Hạt nêm Knorr 900g", "Gia vị", "gói", 66000, 95, "tet_nhe", .02, 5, .30),
 ("Sữa tươi Vinamilk 1L thùng 12", "Sữa", "thùng", 186000, 160, "tet_nhe", .05, 3, .25),
 ("Sữa đặc Ông Thọ lon 380g", "Sữa", "lon", 24500, 210, "tet_nhe", 0, 5, .30),
 ("Sữa bột Dielac Alpha 900g", "Sữa", "lon", 290000, 28, "none", .03, 8, .38),
 ("Sữa chua Vinamilk lốc 4 hộp", "Sữa", "lốc", 25500, 240, "summer", .03, 2, .32),
 ("Nước suối Aquafina 500ml thùng 24", "Đồ uống", "thùng", 78000, 190, "summer", .04, 3, .33),
 ("Coca-Cola lon 330ml thùng 24", "Đồ uống", "thùng", 192000, 130, "summer_tet", .03, 3, .33),
 ("Trà xanh 0 độ chai 455ml thùng 24", "Đồ uống", "thùng", 144000, 95, "summer", .05, 3, .34),
 ("Bia Tiger lon 330ml thùng 24", "Đồ uống", "thùng", 396000, 110, "summer_tet_strong", .02, 4, .35),
 ("Nước ngọt Pepsi chai 1.5L lốc 6", "Đồ uống", "lốc", 82000, 100, "summer_tet", .01, 3, .33),
 ("Cà phê G7 3in1 hộp 21 gói", "Đồ uống", "hộp", 54000, 120, "winter", .03, 6, .30),
 ("Trà Lipton hộp 25 túi", "Đồ uống", "hộp", 33000, 75, "winter", .01, 6, .32),
 ("Bột giặt OMO 3kg", "Hóa phẩm", "túi", 148000, 110, "tet_nhe", .01, 6, .28),
 ("Nước xả vải Comfort 3.2L", "Hóa phẩm", "túi", 128000, 65, "tet_nhe", .02, 6, .30),
 ("Nước rửa chén Sunlight 3.6kg", "Hóa phẩm", "chai", 69000, 90, "tet_nhe", .01, 5, .28),
 ("Dầu gội Clear 630g", "Chăm sóc cá nhân", "chai", 148000, 60, "none", 0, 7, .33),
 ("Kem đánh răng P/S 230g", "Chăm sóc cá nhân", "tuýp", 30500, 130, "none", 0, 6, .26),
 ("Giấy vệ sinh Pulppy lốc 10 cuộn", "Hóa phẩm", "lốc", 56000, 150, "tet_nhe", .02, 5, .27),
 ("Khăn giấy Tempo hộp 3 lớp", "Hóa phẩm", "hộp", 21500, 125, "tet", 0, 5, .30),
 ("Bánh quy Cosy hộp thiếc 750g", "Bánh kẹo", "hộp", 85000, 40, "tet_strong", 0, 8, .45),
 ("Kẹo Alpenliebe gói 336g", "Bánh kẹo", "gói", 38000, 60, "tet_strong", 0, 8, .40),
 ("Snack Poca khoai tây thùng 24", "Bánh kẹo", "thùng", 210000, 22, "summer", .04, 7, .38),
 ("Hạt dưa Chacheer túi 500g", "Bánh kẹo", "túi", 62000, 25, "tet_strong", 0, 9, .50),
]
SPEC = []  # (ten,nhom,dv,gia_von,d,season_kind,events,trend,LT,cv,nhan_mua)
for (ten, nhom, dv, gv, d, k, tr, lt, cv) in v1:
    skind = "summer" if k.startswith("summer") else ("winter" if k == "winter" else "flat")
    ev = {"tet": tetmap[k]}
    if "Bia" in ten or "Coca" in ten or "Pepsi" in ten or "Snack" in ten: ev["le_30_4_2_9"] = 0.5
    if "Bánh quy" in ten or "Kẹo" in ten: ev.update({"trung_thu": 0.4, "noel": 0.6})
    d2 = max(8, round(d * (gv / 80000) ** 0.9 * 0.8))
    lab = ("Mùa hè" if skind == "summer" else "Mùa đông" if skind == "winter" else
           "Quanh năm, đỉnh Tết" if tetmap[k] >= .6 else "Quanh năm")
    SPEC.append((ten, nhom, dv, gv, d2, skind, ev, tr, lt, cv, lab))

def S(ten, nhom, dv, gv, d, kind, ev, lt, cv, lab, tr=0.0): SPEC.append((ten, nhom, dv, gv, d, kind, ev, tr, lt, cv, lab))
EO = "event_only"
# --- MUA HE (nong): ban manh T5-T8, gan nhu khong ban T11-T2
S("Kem Wall's hộp 1L", "Kem & đông lạnh", "hộp", 62000, 90, "hot", {"thieu_nhi": .5}, 3, .35, "Mùa hè")
S("Kem ốc quế Celano thùng 24", "Kem & đông lạnh", "thùng", 168000, 40, "hot", {"thieu_nhi": .6}, 3, .38, "Mùa hè")
S("Nước tăng lực Redbull thùng 24", "Đồ uống", "thùng", 276000, 55, "hot", {"tet": .5, "le_30_4_2_9": .4}, 4, .33, "Mùa hè")
S("Nước dừa đóng hộp lốc 6", "Đồ uống", "lốc", 54000, 70, "hot", {}, 4, .36, "Mùa hè")
S("Quạt cây Senko", "Điện gia dụng", "cái", 420000, 14, "hot", {}, 12, .45, "Mùa hè")
S("Quạt mini cầm tay", "Điện gia dụng", "cái", 55000, 38, "hot", {"thieu_nhi": .6}, 10, .5, "Mùa hè")
S("Kem chống nắng Nivea 50ml", "Mỹ phẩm", "tuýp", 95000, 26, "hot", {}, 9, .38, "Mùa hè")
S("Bình xịt côn trùng Raid 600ml", "Hóa phẩm", "chai", 58000, 45, "hot", {}, 6, .33, "Mùa hè")
S("Sữa tắm mát lạnh 650g", "Chăm sóc cá nhân", "chai", 88000, 32, "hot", {}, 7, .34, "Mùa hè")
S("Đá lạnh túi 5kg", "Kem & đông lạnh", "túi", 12000, 120, "hot", {"tet": .6, "le_30_4_2_9": .5}, 1, .4, "Mùa hè")
# --- MUA MUA (ha-thu)
S("Áo mưa bộ Rando", "Phụ kiện", "bộ", 38000, 28, "rainy", {}, 8, .45, "Mùa mưa (hè-thu)")
S("Dù gấp tự động", "Phụ kiện", "cái", 70000, 14, "rainy", {}, 9, .45, "Mùa mưa (hè-thu)")
S("Ủng đi mưa nhựa", "Phụ kiện", "đôi", 52000, 10, "rainy", {}, 10, .5, "Mùa mưa (hè-thu)")
S("Nhang muỗi Jumbo hộp", "Hóa phẩm", "hộp", 24000, 60, "rainy", {}, 5, .33, "Mùa mưa (hè-thu)")
S("Thuốc diệt gián/kiến gói", "Hóa phẩm", "gói", 31000, 30, "rainy", {}, 6, .35, "Mùa mưa (hè-thu)")
# --- MUA DONG (lanh)
S("Chăn lông cừu 1m8", "Gia dụng", "cái", 280000, 11, "cold", {"tet": .5}, 14, .45, "Mùa đông")
S("Khăn len quàng cổ", "Phụ kiện", "cái", 65000, 24, "cold", {"noel": .6}, 12, .45, "Mùa đông")
S("Máy sưởi dầu 11 thanh", "Điện gia dụng", "cái", 1100000, 4, "cold", {}, 15, .55, "Mùa đông")
S("Miếng dán giữ nhiệt hộp 10", "Y tế & sức khỏe", "hộp", 40000, 34, "cold", {}, 8, .4, "Mùa đông")
S("Bình giữ nhiệt Lock&Lock", "Gia dụng", "cái", 220000, 13, "cold", {"tet": .4, "nha_giao": .8}, 10, .4, "Mùa đông")
S("Gia vị lẩu Thái gói", "Gia vị", "gói", 18000, 85, "cold", {"tet": .6, "noel": .3}, 5, .32, "Mùa đông")
S("Cá viên đông lạnh 500g", "Kem & đông lạnh", "gói", 48000, 65, "cold", {"tet": .8}, 3, .35, "Mùa đông")
S("Trà gừng hòa tan hộp", "Đồ uống", "hộp", 36000, 58, "cold", {"tet": .3}, 6, .33, "Mùa đông")
S("Sữa hạt óc chó lốc 4", "Sữa", "lốc", 52000, 48, "cold", {"tet": .4}, 4, .33, "Mùa đông")
S("Dầu gió xanh chai 24ml", "Y tế & sức khỏe", "chai", 26000, 60, "cold", {}, 6, .3, "Mùa đông")
S("Kem dưỡng thể Vaseline 350ml", "Mỹ phẩm", "chai", 85000, 30, "cold", {"noel": .5}, 8, .35, "Mùa đông")
S("Son dưỡng môi chống nứt", "Mỹ phẩm", "thỏi", 42000, 38, "cold", {"valentine": .7}, 8, .35, "Mùa đông")
# --- CHI DIP TET
S("Mứt Tết hộp 500g", "Bánh kẹo", "hộp", 78000, 70, EO, {"tet": 1.0}, 10, .42, "Chỉ dịp Tết")
S("Hộp quà Tết cao cấp", "Quà tặng", "hộp", 450000, 18, EO, {"tet": 1.0}, 14, .45, "Chỉ dịp Tết")
S("Hạt điều rang muối hộp 500g", "Bánh kẹo", "hộp", 98000, 45, EO, {"tet": 1.0}, 8, .4, "Chỉ dịp Tết")
S("Rượu vang Đà Lạt chai", "Đồ uống", "chai", 135000, 30, EO, {"tet": 1.0, "noel": .35}, 9, .42, "Chỉ dịp Tết")
S("Bao lì xì xấp 10", "Văn phòng phẩm", "xấp", 6000, 160, EO, {"tet": 1.0}, 7, .45, "Chỉ dịp Tết")
S("Hoa mai/đào giả trang trí", "Trang trí", "cành", 90000, 22, EO, {"tet": 1.0}, 14, .5, "Chỉ dịp Tết")
S("Lịch Tết treo tường", "Văn phòng phẩm", "cuốn", 28000, 55, EO, {"tet": 1.0}, 14, .5, "Chỉ dịp Tết")
S("Câu đối, tranh Tết", "Trang trí", "bộ", 45000, 20, EO, {"tet": 1.0}, 12, .5, "Chỉ dịp Tết")
S("Hương trầm hộp", "Gia dụng", "hộp", 20000, 40, "flat", {"tet": 0.9}, 6, .35, "Quanh năm, đỉnh Tết")
# --- TRUNG THU
S("Bánh trung thu Kinh Đô hộp 4 bánh", "Bánh kẹo", "hộp", 150000, 55, EO, {"trung_thu": 1.0}, 12, .42, "Chỉ dịp Trung thu")
S("Bánh trung thu lẻ nhân thập cẩm", "Bánh kẹo", "cái", 28000, 160, EO, {"trung_thu": 1.0}, 10, .42, "Chỉ dịp Trung thu")
S("Đèn lồng Trung thu", "Đồ chơi", "cái", 35000, 48, EO, {"trung_thu": 1.0}, 15, .5, "Chỉ dịp Trung thu")
S("Mặt nạ, đồ chơi Trung thu", "Đồ chơi", "bộ", 24000, 52, EO, {"trung_thu": 1.0}, 14, .5, "Chỉ dịp Trung thu")
S("Trà thượng hạng hộp quà biếu", "Quà tặng", "hộp", 180000, 18, "flat", {"trung_thu": 2.5, "tet": 1.2, "nha_giao": .8}, 9, .4, "Quà tặng")
# --- QUA TANG: 14/2, 8/3, 20/10, 20/11, Noel
GIFT = {"valentine": 3.5, "quoc_te_phu_nu": 3.0, "phu_nu_vn": 3.0, "nha_giao": 1.2, "noel": 1.8, "tet": .5}
S("Socola Ferrero hộp 16 viên", "Bánh kẹo", "hộp", 175000, 26, "flat", dict(GIFT), 8, .4, "Quà tặng")
S("Gấu bông 40cm", "Quà tặng", "con", 85000, 22, "flat", {**GIFT, "thieu_nhi": 1.2}, 12, .5, "Quà tặng")
S("Set mỹ phẩm quà tặng", "Mỹ phẩm", "hộp", 320000, 14, "flat", {**GIFT, "valentine": 2.0}, 10, .45, "Quà tặng")
S("Nước hoa 50ml", "Mỹ phẩm", "chai", 380000, 12, "flat", {**GIFT, "nha_giao": .5}, 10, .45, "Quà tặng")
S("Hoa hồng sáp hộp", "Quà tặng", "hộp", 120000, 12, EO, {"valentine": 1.0, "quoc_te_phu_nu": .9, "phu_nu_vn": .9, "nha_giao": .5}, 8, .5, "Quà tặng")
S("Giấy gói quà, hộp quà rỗng", "Văn phòng phẩm", "xấp", 18000, 60, "flat", {"valentine": 2.0, "quoc_te_phu_nu": 2.0, "phu_nu_vn": 2.0, "nha_giao": 2.0, "noel": 3.0, "tet": 1.0}, 6, .4, "Quà tặng")
S("Thiệp chúc mừng", "Văn phòng phẩm", "tấm", 8000, 90, "flat", {"valentine": 2.5, "quoc_te_phu_nu": 2.0, "phu_nu_vn": 2.0, "nha_giao": 3.5, "noel": 2.5}, 6, .45, "Quà tặng")
S("Bút ký quà tặng hộp", "Văn phòng phẩm", "hộp", 150000, 8, "flat", {"nha_giao": 4.0, "khai_giang": 1.0, "tet": 1.0}, 10, .5, "Quà tặng")
# --- KHAI GIANG
S("Vở học sinh lốc 10 quyển", "Văn phòng phẩm", "lốc", 68000, 70, "flat", {"khai_giang": 4.0}, 7, .38, "Khai giảng (T8–T9)")
S("Bút bi Thiên Long hộp 20", "Văn phòng phẩm", "hộp", 62000, 55, "flat", {"khai_giang": 2.5, "nha_giao": .5}, 6, .35, "Khai giảng (T8–T9)")
S("Cặp sách học sinh", "Văn phòng phẩm", "cái", 240000, 12, EO, {"khai_giang": 1.0}, 14, .5, "Khai giảng (T8–T9)")
S("Hộp bút, bộ dụng cụ học tập", "Văn phòng phẩm", "bộ", 75000, 30, "flat", {"khai_giang": 3.5}, 8, .4, "Khai giảng (T8–T9)")
S("Bình nước học sinh 600ml", "Gia dụng", "cái", 85000, 20, "flat", {"khai_giang": 3.0}, 10, .4, "Khai giảng (T8–T9)")
S("Sữa học đường hộp 180ml thùng 48", "Sữa", "thùng", 255000, 32, "flat", {"khai_giang": 1.5, "tet": .3}, 4, .3, "Khai giảng (T8–T9)")
S("Bao tập, nhãn vở lốc", "Văn phòng phẩm", "lốc", 15000, 80, EO, {"khai_giang": 1.0}, 6, .45, "Khai giảng (T8–T9)")
# --- HALLOWEEN / NOEL
S("Mặt nạ, đồ hóa trang Halloween", "Trang trí", "bộ", 30000, 40, EO, {"halloween": 1.0}, 15, .55, "Chỉ dịp Halloween")
S("Kẹo Halloween túi 300g", "Bánh kẹo", "túi", 45000, 55, EO, {"halloween": 1.0}, 9, .45, "Chỉ dịp Halloween")
S("Cây thông Noel 1m2", "Trang trí", "cái", 260000, 14, EO, {"noel": 1.0}, 15, .5, "Chỉ dịp Noel")
S("Dây đèn LED nhấp nháy", "Trang trí", "cuộn", 75000, 30, EO, {"noel": 1.0, "tet": .35}, 12, .5, "Chỉ dịp Noel")
S("Bánh quy bơ hộp Noel", "Bánh kẹo", "hộp", 120000, 25, EO, {"noel": 1.0}, 9, .45, "Chỉ dịp Noel")
S("Mũ, vớ ông già Noel", "Trang trí", "cái", 22000, 40, EO, {"noel": 1.0}, 14, .55, "Chỉ dịp Noel")
# --- QUANH NAM bo sung
S("Khẩu trang y tế hộp 50", "Y tế & sức khỏe", "hộp", 28000, 85, "cold", {}, 6, .34, "Quanh năm, tăng mùa đông")
S("Nước rửa tay Lifebuoy 500ml", "Chăm sóc cá nhân", "chai", 52000, 60, "flat", {}, 6, .28, "Quanh năm")
S("Bàn chải đánh răng P/S lốc 3", "Chăm sóc cá nhân", "lốc", 42000, 45, "flat", {}, 6, .28, "Quanh năm")
S("Băng vệ sinh Diana lốc 8 gói", "Chăm sóc cá nhân", "lốc", 70000, 40, "flat", {}, 6, .27, "Quanh năm")
S("Tã quần Bobby gói 40 miếng", "Chăm sóc cá nhân", "gói", 165000, 26, "flat", {}, 7, .3, "Quanh năm")
S("Bột ngọt Ajinomoto 1kg", "Gia vị", "gói", 52000, 70, "flat", {"tet": .4}, 5, .28, "Quanh năm")
S("Muối i-ốt 500g", "Gia vị", "gói", 6500, 130, "flat", {}, 5, .25, "Quanh năm")
S("Xúc xích tiệt trùng gói 10 cây", "Thực phẩm khô", "gói", 38000, 75, "flat", {"thieu_nhi": .4, "tet": .5}, 4, .3, "Quanh năm")
S("Pin AA Panasonic vỉ 4", "Điện gia dụng", "vỉ", 36000, 70, "flat", {"tet": .3}, 8, .3, "Quanh năm")
S("Bóng đèn LED 9W", "Điện gia dụng", "cái", 32000, 55, "flat", {}, 8, .3, "Quanh năm")
S("Túi rác cuộn lớn", "Hóa phẩm", "cuộn", 22000, 90, "flat", {"tet": .5}, 5, .27, "Quanh năm")
S("Giấy A4 Double A ream", "Văn phòng phẩm", "ream", 88000, 50, "flat", {"khai_giang": .5}, 7, .3, "Quanh năm")
S("Bánh gạo Ichi gói 150g", "Bánh kẹo", "gói", 15000, 100, "flat", {"tet": .5}, 6, .3, "Quanh năm")
S("Nước cam ép Twister lốc 6", "Đồ uống", "lốc", 60000, 62, "summer", {"tet": .3}, 4, .3, "Mùa hè")
S("Cháo ăn liền gói", "Thực phẩm khô", "gói", 8500, 140, "winter", {}, 5, .3, "Mùa đông")
S("Hộp cơm điện tử giữ nhiệt", "Gia dụng", "cái", 320000, 8, "cold", {"nha_giao": .4}, 14, .5, "Mùa đông")


# --- NHU YEU PHAM CHO BAO LU (ban it binh thuong, bung manh truoc va sau bao)
S("Cá hộp 150g", "Thực phẩm khô", "hộp", 24000, 70, "flat", {}, 6, .32, "Quanh năm, bùng nổ khi bão lũ")
S("Thịt hộp 340g", "Thực phẩm khô", "hộp", 46000, 38, "flat", {"tet": .4}, 6, .34, "Quanh năm, bùng nổ khi bão lũ")
S("Lương khô gói", "Thực phẩm khô", "gói", 18000, 45, "flat", {}, 6, .33, "Quanh năm, bùng nổ khi bão lũ")
S("Nến trắng gói 10 cây", "Gia dụng", "gói", 12000, 40, "flat", {"tet": .3}, 6, .35, "Quanh năm, bùng nổ khi bão lũ")
S("Đèn pin sạc LED", "Điện gia dụng", "cái", 95000, 10, "flat", {}, 10, .45, "Quanh năm, bùng nổ khi bão lũ")
S("Sạc dự phòng 10000mAh", "Điện gia dụng", "cái", 260000, 9, "flat", {"nha_giao": .3, "tet": .3}, 12, .4, "Quanh năm, bùng nổ khi bão lũ")
S("Nước khoáng can 5L", "Đồ uống", "can", 22000, 60, "summer", {}, 3, .32, "Quanh năm, bùng nổ khi bão lũ")
S("Viên khử khuẩn Cloramin B hộp", "Y tế & sức khỏe", "hộp", 45000, 15, "flat", {}, 8, .45, "Bùng nổ sau bão lũ")
S("Gói bù nước ORS hộp 20", "Y tế & sức khỏe", "hộp", 38000, 22, "flat", {}, 7, .4, "Quanh năm, bùng nổ khi bão lũ")
S("Bạt nilon che mưa cuộn", "Gia dụng", "cuộn", 110000, 9, "flat", {}, 9, .5, "Bùng nổ sau bão lũ")
S("Nước tẩy Javel 1L", "Hóa phẩm", "chai", 14000, 45, "flat", {"tet": .4}, 5, .3, "Quanh năm, bùng nổ khi bão lũ")
S("Găng tay cao su đôi", "Hóa phẩm", "đôi", 18000, 35, "flat", {}, 6, .38, "Bùng nổ sau bão lũ")
S("Bật lửa gas", "Gia dụng", "cái", 6000, 110, "flat", {"tet": .3}, 5, .3, "Quanh năm, bùng nổ khi bão lũ")

sku = pd.DataFrame(SPEC, columns=["ten_sku", "nhom_hang", "don_vi", "gia_von", "nhu_cau_tb_ngay", "skind", "events",
                                  "xu_huong_nam", "lead_time_tb", "cv_nhu_cau", "loai_mua_vu"])
sku.insert(0, "ma_sku", [f"SKU{i+1:03d}" for i in range(len(sku))])
sku["lead_time_std"] = np.round(sku.lead_time_tb * 0.2 + 0.4, 1)
sku["chi_phi_dat_hang"] = rng.choice([120000, 150000, 180000, 220000], len(sku)).astype(int)
sku["ty_le_chi_phi_luu_kho"] = np.round(rng.uniform(0.16, 0.24, len(sku)), 2)
sku["moq"] = np.maximum(6, (sku.nhu_cau_tb_ngay * 0.6 // 5 * 5)).astype(int)
sku["nha_cung_cap"] = [f"NCC{(i % 14) + 1:02d}" for i in range(len(sku))]
sku["gia_ban"] = np.round(sku.gia_von * rng.uniform(1.12, 1.30, len(sku)) / 500) * 500

# gan he so anh huong cu soc theo tu khoa ten SKU
STORM_AFF = {  # tu khoa: (mua tich tru truoc bao, cuu tro sau bao)
 "Mì gói": (2.5, 2.0), "Mì ly": (1.6, 1.2), "Gạo ST25": (1.2, 1.5), "Dầu ăn": (.6, .8), "Đường tinh": (.4, .5),
 "Nước suối": (2.2, 2.5), "Nước mắm": (.3, .5), "Muối i-ốt": (.5, .8), "Sữa đặc": (.8, .8), "Xúc xích": (.8, .5),
 "Pin AA": (3.0, 2.0), "Bóng đèn": (0, .8), "Cháo ăn liền": (1.5, 1.2), "Bánh gạo": (.6, .3), "Bánh quy Cosy": (.5, .3),
 "Túi rác": (0, .5), "Bột giặt": (.1, .8), "Giấy vệ sinh": (.3, .8), "Nước rửa tay": (.3, 1.0), "Khẩu trang": (.3, .8),
 "Áo mưa": (2.0, 1.5), "Dù gấp": (.8, .3), "Ủng đi mưa": (1.2, 1.5), "Chăn lông": (0, 1.2), "Dầu gió": (.3, .6),
 "Nhang muỗi": (0, .5), "Hạt nêm": (.3, .3),
 "Cá hộp": (3.0, 2.5), "Thịt hộp": (2.5, 2.0), "Lương khô": (3.5, 3.0), "Nến trắng": (6.0, 3.0), "Đèn pin sạc": (7.0, 3.0),
 "Sạc dự phòng": (4.0, 1.5), "Nước khoáng can": (2.5, 3.0), "Cloramin": (.5, 8.0), "Gói bù nước ORS": (.5, 5.0),
 "Bạt nilon": (2.0, 4.0), "Javel": (.3, 5.0), "Găng tay cao su": (.2, 4.0), "Bật lửa": (3.0, 1.5),
}
OTHER_AFF = {
 "nang_nong": {"Nước suối": 1.0, "Kem Wall": 1.3, "Kem ốc quế": 1.3, "Quạt": 1.6, "Đá lạnh": 1.3, "Bia": .5, "Coca": .4, "Pepsi": .4,
               "Trà xanh": .5, "Nước dừa": .6, "Redbull": .5, "Nước cam": .5, "Kem chống nắng": .6, "Sữa tắm": .5, "Nước khoáng can": 1.0},
 "ret_dam": {"Chăn lông": 1.6, "Máy sưởi": 2.2, "Miếng dán": 1.8, "Khăn len": 1.2, "Trà gừng": 1.0, "Gia vị lẩu": 1.0, "Cá viên": .8,
             "Cà phê": .4, "Dầu gió": .7, "Sữa hạt": .6, "Kem dưỡng thể": .6, "Son dưỡng": .6, "Bình giữ nhiệt": .8, "Cháo ăn liền": .4,
             "Khẩu trang": .3, "Hộp cơm điện": .5},
 "tin_don_gia": {"Dầu ăn": 2.0, "Đường tinh": 1.8, "Gạo ST25": 1.5, "Muối i-ốt": 1.2, "Nước mắm": .8, "Bột giặt": .8, "Mì gói": .6, "Sữa đặc": .5},
 "dich_cum": {"Khẩu trang": 2.0, "Nước rửa tay": 1.2, "Dầu gió": 1.2, "Gói bù nước ORS": .8, "Trà gừng": .5},
 "sot_xuat_huyet": {"Bình xịt côn trùng": 1.2, "Nhang muỗi": 1.0, "Thuốc diệt gián": .3, "Gói bù nước ORS": 1.2},
 "the_thao": {"Bia": .4, "Snack": .5, "Hạt dưa": .4, "Coca": .2, "Pepsi": .2, "Bánh gạo": .2, "Xúc xích": .2, "Redbull": .2},
}
_evs = []
for _, _r in sku.iterrows():
    e = dict(_r.events)
    for kw, (a, b) in STORM_AFF.items():
        if kw in _r.ten_sku:
            if a: e["bao_tru"] = a
            if b: e["bao_cuu_tro"] = b
    for key, tab in OTHER_AFF.items():
        for kw, A in tab.items():
            if kw in _r.ten_sku: e[key] = A
    _evs.append(e)
sku["events"] = _evs


# ---------------- Nhu cau ----------------
demand, promos, means = {}, {}, {}
for _, r in sku.iterrows():
    trend = 1 + r.xu_huong_nam * (np.arange(T) / 365)
    ev = np.zeros(T); evs = np.zeros(T)
    for e, A in r.events.items():
        if e in SHOCK_KEYS: evs += A * EV_BUMP[e]
        else: ev += A * EV_BUMP[e]
    if r.skind == EO:
        base_shape = 0.02 + 12.0 * ev
    else:
        base_shape = season(r.skind) * (1 + ev)
        if r.events.get("tet", 0) > 0: base_shape = base_shape * (1 - 0.35 * tet_post)
    mult = base_shape * np.array([1.05, 1.10, 1.08, 1.10, 1.18, 1.20, 0.55])[dow_idx] * trend * event_mult
    promo = np.zeros(T, dtype=int); pm = np.ones(T)
    for _ in range(int(4 * T / 365)):
        s0 = rng.integers(0, T - 12); L = rng.integers(5, 11)
        promo[s0:s0 + L] = 1; pm[s0:s0 + L] *= rng.uniform(1.3, 1.9); pm[s0 + L:s0 + L + 4] *= 0.85
    if r.skind == EO: pm = np.where(pm > 1.0, 1.0 + (pm - 1.0) * 0.3, pm)   # mua cao diem moi co KM that su, ngoai mua hau nhu khong
    mult = mult * pm
    mean_plan = r.nhu_cau_tb_ngay * mult / np.mean(mult)
    mean_plan = np.where(np.array([d in closed for d in dates]), 0, mean_plan)
    dip = 0.3 * storm_dip if r.nhom_hang in DIP_GROUPS else 0
    mean = np.where(mean_plan > 0, mean_plan * np.maximum(0.1, 1 + evs - dip), 0)
    cv = r.cv_nhu_cau
    var = (cv * np.maximum(mean, 0.05)) ** 2 + mean
    p = np.clip(mean / np.maximum(var, 1e-9), 1e-3, 0.999); n = np.maximum(mean * p / (1 - p), 0.3)
    d = rng.negative_binomial(n, p)
    d = np.where(mean <= 0, 0, d)
    demand[r.ma_sku] = d; promos[r.ma_sku] = promo; means[r.ma_sku] = mean_plan

closed_arr_pre = np.array([d in closed for d in dates])

# don B2B dot bien (tiec, khai truong, du an): 1-2 ngay, gap 4-10 lan muc TB
SHOCK_LOG = []
for (nm, ld, I, ng, gc) in STORMS:
    SHOCK_LOG.append(("Thiên tai", nm, ld, (D(ld) + pd.Timedelta(days=10)).strftime("%Y-%m-%d"), I, ng,
                      "Mua tích trữ 3 ngày trước bão, nhu yếu phẩm cứu trợ 10 ngày sau, giao hàng chậm, quà tặng/trang trí giảm", gc))
for (kk, nm, st, en, ng, gc) in OTHER:
    SHOCK_LOG.append((kk, nm, st, en, "", ng, "", gc))
for nm, a, b in SPORTS:
    SHOCK_LOG.append(("Thể thao", nm, a, b, "", "Thực tế (lịch thi đấu)", "Bia, snack, nước ngọt, đồ nhắm tăng", ""))
for ncc, st, en, add in SUPPLIER_OUT:
    SHOCK_LOG.append(("Đứt gãy cung ứng", f"Nhà cung cấp {ncc} giao chậm", st, en, "", "Mô phỏng", f"Lead time +{add} ngày cho SKU của {ncc}", ""))
b2b_pool = sku[(sku.nhu_cau_tb_ngay >= 40) & sku.nhom_hang.isin(["Đồ uống", "Thực phẩm khô", "Bánh kẹo", "Sữa", "Hóa phẩm", "Văn phòng phẩm", "Gia vị"])]
_open_days = [i for i in range(T) if not closed_arr_pre[i]]
for _ in range(60):
    r = b2b_pool.iloc[rng.integers(0, len(b2b_pool))]
    i = int(rng.choice(_open_days)); L = int(rng.integers(1, 3)); mul = float(rng.uniform(4, 10))
    for j in range(i, min(T, i + L)):
        if not closed_arr_pre[j]:
            demand[r.ma_sku][j] += int(max(1, means[r.ma_sku][j]) * mul)
    SHOCK_LOG.append(("Đơn B2B đột biến", f"Đơn lớn {r.ten_sku}", dates[i].strftime("%Y-%m-%d"), dates[min(T - 1, i + L - 1)].strftime("%Y-%m-%d"),
                      "", "Mô phỏng", f"Gấp khoảng {mul:.1f} lần mức TB (tiệc, khai trương điểm bán, đơn dự án)", r.ma_sku))
shock_log = pd.DataFrame(SHOCK_LOG, columns=["nhom_ly_do", "su_kien", "tu_ngay", "den_ngay", "muc_do_0_1", "nguon_du_lieu", "tac_dong_chinh", "ghi_chu_hoac_sku"])
shock_log = shock_log.sort_values("tu_ngay").reset_index(drop=True)

# ---------------- Mo phong kho ----------------
closed_arr = np.array([d in closed for d in dates])
def simulate(r):
    d = demand[r.ma_sku]; mean = means[r.ma_sku]; promo = promos[r.ma_sku]
    cs = np.concatenate([[0.0], np.cumsum(mean)])
    fwd = lambda t, h: cs[min(t + 1 + h, T)] - cs[min(t + 1, T)]
    LT = r.lead_time_tb
    fb = 1 + rng.normal(0, 0.10)                                     # lech du bao co he thong cua nguoi lap ke hoach
    eoq = np.sqrt(2 * r.nhu_cau_tb_ngay * 365 * r.chi_phi_dat_hang / (r.gia_von * r.ty_le_chi_phi_luu_kho))
    qmin = max(int(r.moq), int(round(eoq / 5) * 5))
    stock = int(fwd(0, int(LT) + 10) * fb * 1.1 + qmin * 0.5)
    pipeline = []; rows = []
    for t, day in enumerate(dates):
        is_closed = closed_arr[t]
        qin = 0
        if not is_closed:
            arr = [p for p in pipeline if p[0] <= t]; pipeline = [p for p in pipeline if p[0] > t]
            qin = sum(q for _, q in arr)
        begin = stock; stock += qin
        dem = 0 if is_closed else int(d[t]); qout = min(dem, stock); stock -= qout
        order_flag = 0; qo = 0
        if not is_closed:
            ip = stock + sum(q for _, q in pipeline)
            ltd = fwd(t, int(round(LT))) * fb
            avg = ltd / max(LT, 1)
            ss = 1.65 * r.cv_nhu_cau * avg * np.sqrt(max(LT, 1))
            rop = ltd + ss
            if ip <= rop:
                target = fwd(t, int(round(LT)) + 14) * fb + ss
                qo = int(max(qmin, round(target - ip)))
                lt = max(1, int(round(rng.normal(LT, r.lead_time_std))) + int(lt_extra[t]) + int(sup_extra.get(r.nha_cung_cap, np.zeros(T))[t]))
                pipeline.append((t + lt, qo)); order_flag = 1
        rows.append((day, r.ma_sku, begin, qin, qout, stock, int(dem > qout), int(promo[t]), order_flag, qo))
    return rows

all_rows = []
for _, r in sku.iterrows(): all_rows += simulate(r)
tx = pd.DataFrame(all_rows, columns=["date", "ma_sku", "ton_dau_ngay", "qty_in", "qty_out", "ton_cuoi_ngay", "het_hang",
                                     "khuyen_mai", "phat_sinh_don_dat", "so_luong_dat"])
tx["thu"] = tx.date.dt.dayofweek + 2
tx["mua"] = tx.date.map(mua_of)
tx["la_ngay_nghi"] = tx.date.isin(closed).astype(int)
tx["trong_tuan_tet"] = tx.date.isin(tet_nghi).astype(int)
tx["bao_lu_muc_do"] = storm_level[(tx.date - START).dt.days.values].round(1)

# ---------------- SKU master: ABC, XYZ ----------------
price = sku.set_index("ma_sku").gia_von
tx["gia_tri_xuat"] = tx.qty_out * tx.ma_sku.map(price)
val = tx.groupby("ma_sku").gia_tri_xuat.sum().sort_values(ascending=False)
cum = val.cumsum() / val.sum()
abc = pd.Series(np.where(cum <= 0.75, "A", np.where(cum <= 0.92, "B", "C")), index=val.index); abc.iloc[0] = "A"
tx["ym"] = tx.date.dt.to_period("M")
mon = tx.groupby(["ma_sku", "ym"]).qty_out.sum().unstack()
cvm = (mon.std(axis=1) / mon.mean(axis=1))
xyz = pd.Series(np.where(cvm <= 0.5, "X", np.where(cvm <= 1.0, "Y", "Z")), index=cvm.index)
first = tx[tx.date == START].set_index("ma_sku")["ton_dau_ngay"]
sku["ton_kho_ban_dau"] = sku.ma_sku.map(first)
sku["gia_tri_xuat_36t"] = sku.ma_sku.map(val).astype("int64")  # int64: tren Windows int mac dinh la 32-bit, tran so
sku["phan_loai_ABC"] = sku.ma_sku.map(abc)
sku["cv_theo_thang"] = sku.ma_sku.map(cvm).round(2)
sku["phan_loai_XYZ"] = sku.ma_sku.map(xyz)

# ---------------- Bang tong hop mua vu & ngay le (tinh tu du lieu) ----------------
op = tx[tx.la_ngay_nghi == 0]
avg_day = op.groupby("ma_sku").qty_out.mean()
mu = op.groupby(["ma_sku", "mua"]).qty_out.mean().unstack()[["Xuân", "Hạ", "Thu", "Đông"]]
mu_idx = mu.div(avg_day, axis=0).round(2)
mua_tbl = sku[["ma_sku", "ten_sku", "nhom_hang", "loai_mua_vu"]].copy()
mua_tbl["tb_xuat_ngay"] = mua_tbl.ma_sku.map(avg_day).round(1)
for m in mu_idx.columns: mua_tbl[f"chi_so_{m}"] = mua_tbl.ma_sku.map(mu_idx[m])
mua_tbl["mua_cao_diem"] = mu_idx.idxmax(axis=1).reindex(mua_tbl.ma_sku).values
mua_tbl["mua_thap_diem"] = mu_idx.idxmin(axis=1).reindex(mua_tbl.ma_sku).values
mua_tbl["ban_it_ngoai_mua"] = np.where(mu_idx.min(axis=1).reindex(mua_tbl.ma_sku).values < 0.3, "Có", "")
last = tx[tx.date == END].set_index("ma_sku").ton_cuoi_ngay
mua_tbl["ton_cuoi_ky"] = mua_tbl.ma_sku.map(last)
last90 = op[op.date > END - pd.Timedelta(days=90)].groupby("ma_sku").qty_out.mean()
mua_tbl["so_ngay_ton_kho_(DOH)"] = (mua_tbl.ton_cuoi_ky / mua_tbl.ma_sku.map(last90).replace(0, np.nan)).round(0)

ev_rows = []
for name, (ds, pre, peak, sig, note) in EVENTS.items():
    cols = {}
    for sk in sku.ma_sku:
        s = op[op.ma_sku == sk]
        vals = []
        for d0 in ds:
            w = s[(s.date >= d0 - pd.Timedelta(days=pre)) & (s.date <= d0)]
            if len(w) > 3 and (d0 - pd.Timedelta(days=pre)) >= START and d0 <= END:
                vals.append(w.qty_out.mean())
        cols[sk] = np.mean(vals) / avg_day[sk] if vals and avg_day[sk] > 0 else np.nan
    ev_rows.append(pd.Series(cols, name=name))
le = pd.DataFrame(ev_rows).T.round(2)
le.columns = [f"x_{c}" for c in le.columns]
le_tbl = sku[["ma_sku", "ten_sku", "nhom_hang", "loai_mua_vu"]].merge(le, left_on="ma_sku", right_index=True)
le_nhom = le_tbl.groupby("nhom_hang")[[c for c in le_tbl.columns if c.startswith("x_")]].mean().round(2).reset_index()


# bao lu x SKU: he so tang truoc va sau bao (cac bao muc do >= 0.5)
bl_rows = {}
for sk in sku.ma_sku:
    pre_v, post_v = [], []
    dd = demand[sk]; mm = means[sk]
    for (nm, ld, I, _, _) in STORMS:
        if I < 0.5: continue
        i0 = (D(ld) - START).days
        wa = [k for k in range(i0 - 3, i0 + 1) if 0 <= k < T and mm[k] > 0]
        wb = [k for k in range(i0 + 1, i0 + 11) if 0 <= k < T and mm[k] > 0]
        if wa: pre_v.append(dd[wa].sum() / mm[wa].sum())
        if wb: post_v.append(dd[wb].sum() / mm[wb].sum())
    bl_rows[sk] = (np.mean(pre_v) if pre_v else np.nan, np.mean(post_v) if post_v else np.nan)
bl = pd.DataFrame(bl_rows, index=["x_truoc_bao_3_ngay", "x_sau_bao_10_ngay"]).T.round(2)
bao_tbl = sku[["ma_sku", "ten_sku", "nhom_hang"]].merge(bl, left_on="ma_sku", right_index=True)
bao_tbl["nhom_nhu_yeu_pham"] = np.where((bao_tbl.x_truoc_bao_3_ngay >= 1.5) | (bao_tbl.x_sau_bao_10_ngay >= 1.5), "Tăng mạnh khi bão lũ",
                                   np.where((bao_tbl.x_truoc_bao_3_ngay < 0.9) & (bao_tbl.x_sau_bao_10_ngay < 0.9), "Giảm khi bão lũ", ""))

# ---------------- Ban tho co loi ----------------
raw_tx = tx[["date", "ma_sku", "qty_in", "qty_out", "ton_cuoi_ngay"]].copy()
raw_tx["qty_out"] = raw_tx["qty_out"].astype(float); raw_tx["qty_in"] = raw_tx["qty_in"].astype(float)
log = []; n = len(raw_tx)
mi = rng.choice(n, int(0.004 * n), replace=False)
for i in mi: log.append((raw_tx.iat[i, 0], raw_tx.iat[i, 1], "thieu_qty_out", raw_tx.iat[i, 3]))
raw_tx.iloc[mi, raw_tx.columns.get_loc("qty_out")] = np.nan
oi = rng.choice(n, int(0.0012 * n), replace=False)
for i in oi:
    log.append((raw_tx.iat[i, 0], raw_tx.iat[i, 1], "outlier_nhap_sai", raw_tx.iat[i, 3]))
    if not np.isnan(raw_tx.iat[i, 3]): raw_tx.iat[i, 3] = raw_tx.iat[i, 3] * rng.choice([10, 100]) + 1
di = rng.choice(n, int(0.0015 * n), replace=False)
dups = raw_tx.iloc[di]
for _, x in dups.iterrows(): log.append((x.date, x.ma_sku, "dong_trung", x.qty_out))
raw_tx = pd.concat([raw_tx, dups]).sort_values(["date", "ma_sku"], kind="stable").reset_index(drop=True)
dirty_log = pd.DataFrame(log, columns=["date", "ma_sku", "loai_loi", "gia_tri_goc_qty_out"]).sort_values(["date", "ma_sku"])

# ---------------- Xuat ----------------
tx_out = tx[["date", "ma_sku", "thu", "mua", "qty_in", "qty_out", "ton_cuoi_ngay", "het_hang", "khuyen_mai", "la_ngay_nghi", "trong_tuan_tet", "bao_lu_muc_do"]]
sku_out = sku.drop(columns=["skind", "events"])
sku_out.to_csv(f"{OUT}/sku_master.csv", index=False, encoding="utf-8-sig")
tx_out.to_csv(f"{OUT}/giao_dich_nhap_xuat_ton_SACH.csv", index=False, encoding="utf-8-sig")
raw_tx.to_csv(f"{OUT}/giao_dich_nhap_xuat_ton_THO.csv", index=False, encoding="utf-8-sig")
lich_su_kien.to_csv(f"{OUT}/lich_su_kien_prophet.csv", index=False, encoding="utf-8-sig")
cal_nghi.to_csv(f"{OUT}/lich_ngay_nghi_kho.csv", index=False, encoding="utf-8-sig")
mua_tbl.to_csv(f"{OUT}/tong_hop_mua_x_sku.csv", index=False, encoding="utf-8-sig")
bao_tbl.to_csv(f"{OUT}/tong_hop_bao_lu_x_sku.csv", index=False, encoding="utf-8-sig")
shock_log.to_csv(f"{OUT}/su_kien_dot_bien.csv", index=False, encoding="utf-8-sig")
le_tbl.to_csv(f"{OUT}/tong_hop_ngay_le_x_sku.csv", index=False, encoding="utf-8-sig")
dirty_log.to_csv(f"{OUT}/nhat_ky_loi_co_chu_dich.csv", index=False, encoding="utf-8-sig")
# Lich khuyen mai theo dot (bo phan ban hang gui truoc cho kho) -> dung lam dac trung, thay cho cot khuyen_mai trong answer_key
km = tx_out[["date", "ma_sku", "khuyen_mai"]].sort_values(["ma_sku", "date"]).reset_index(drop=True)
km["dot"] = (km.khuyen_mai != km.groupby("ma_sku").khuyen_mai.shift()).cumsum()
lich_km = (km[km.khuyen_mai == 1].groupby(["ma_sku", "dot"]).date.agg(tu_ngay="min", den_ngay="max")
           .reset_index().drop(columns="dot"))
lich_km["so_ngay"] = (pd.to_datetime(lich_km.den_ngay) - pd.to_datetime(lich_km.tu_ngay)).dt.days + 1
lich_km.to_csv(f"{OUT}/lich_khuyen_mai.csv", index=False, encoding="utf-8-sig")
pd.to_pickle(dict(tx=tx_out, sku=sku_out, raw=raw_tx, lich=lich_su_kien, nghi=cal_nghi, mua=mua_tbl, le=le_tbl, lenhom=le_nhom, bao=bao_tbl, shock=shock_log, log=dirty_log, EVENTS={k: v[4] for k, v in EVENTS.items()}), f"{OUT}/_all.pkl")
print(len(sku), len(tx_out), len(raw_tx)); print(sku.phan_loai_ABC.value_counts().to_dict(), sku.phan_loai_XYZ.value_counts().to_dict())
