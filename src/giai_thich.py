"""Giai thich vi sao mo hinh ra con so: gom dong gop tung cot cua LightGBM thanh nhom yeu to de doc; thanh phan cua Prophet.
LightGBM dung ham Tweedie (log): du bao = exp(muc nen + tong dong gop) -> moi nhom la mot HE SO NHAN (x 1,3 = tang 30%).
Chi dung cho mo hinh da hoc (nang_cap_du_bao.make_model(...).du_doan_lai(..., dong_gop=True)); khong doi du bao.
"""
import numpy as np
import pandas as pd

NHOM = [  # (ten nhom, ham nhan cot) theo thu tu hien thi
    ("Mức bán gần đây", lambda c: c.startswith(("tb7_tre", "tb28_tre", "dlc28_tre")) or (c.startswith("lag_") and c not in ("lag_364", "lag_am"))),
    ("Cùng kỳ năm trước", lambda c: c in ("lag_364", "lag_am", "tb7_am")),
    ("Thứ trong tuần", lambda c: c in ("thu", "cuoi_tuan")),
    ("Thời điểm trong tháng, năm", lambda c: c in ("ngay_trong_thang", "thang", "tuan_trong_nam", "ngay_trong_nam", "dau_thang", "cuoi_thang", "mua")),
    ("Tết", lambda c: c in ("so_ngay_den_tet", "so_ngay_sau_tet", "trong_tuan_tet") or c in ("den_tet", "sau_tet")),
    ("Lễ, sự kiện biết trước", lambda c: c.startswith(("sk_", "den_", "sau_"))),
    ("Sale sàn thương mại điện tử", lambda c: c in ("ngay_sale", "cua_so_sale")),
    ("Khuyến mãi", lambda c: c == "khuyen_mai"),
    ("Đặc điểm mã hàng", lambda c: c in ("ma_sku", "nhom_hang", "loai_mua_vu", "abc_train", "xyz_train", "loai_nhu_cau", "gia_ban", "lead_time_tb")),
]
TEN_NHOM = [t for t, _ in NHOM]


def nhom_cua(cot):
    for ten, ok in NHOM:
        if ok(cot):
            return ten
    raise ValueError(f"Cot chua xep nhom: {cot}")


def gom_nhom(dg):
    """dg: bang du_doan_lai(dong_gop=True), cot dong gop 'dg_<cot>' (co the trong o cac tam khac nhau -> 0).
    Tra ve bang moi dong (date, ma_sku): muc_nen (log), cac nhom (log), du_bao_tho (exp tong)."""
    nhom = {}
    for c in dg.columns:
        if c.startswith("dg_") and c != "dg_goc":
            nhom.setdefault(nhom_cua(c[3:]), []).append(c)
    ra = dg[["date", "ma_sku", "la_ngay_nghi", "du_bao"]].copy()
    ra["muc_nen"] = dg["dg_goc"].values
    for ten in TEN_NHOM:
        ra[ten] = dg[nhom[ten]].fillna(0).sum(axis=1).values if ten in nhom else 0.0
    ra["du_bao_tho"] = np.exp(ra[["muc_nen"] + TEN_NHOM].sum(axis=1))
    return ra


def he_so(dong):
    """Mot dong cua gom_nhom -> (muc nen theo don vi, [(nhom, he so nhan)]) xep theo do anh huong giam dan."""
    ds = [(t, float(np.exp(dong[t]))) for t in TEN_NHOM]
    return float(np.exp(dong["muc_nen"])), sorted(ds, key=lambda x: -abs(np.log(x[1])))


def thanh_phan_prophet(fc, co_khuyen_mai):
    """fc: Prophet.predict (che do cong). Tra ve cac thanh phan theo don vi: xu huong, mua trong tuan, mua trong nam, ngay le, khuyen mai."""
    ra = pd.DataFrame({"date": pd.to_datetime(fc.ds).values, "Xu hướng": fc.trend.values,
                       "Mùa trong tuần": fc.weekly.values, "Mùa trong năm": fc.yearly.values,
                       "Ngày lễ, sự kiện": fc.holidays.values if "holidays" in fc else 0.0,
                       "Khuyến mãi": fc.khuyen_mai.values if co_khuyen_mai and "khuyen_mai" in fc else 0.0})
    ra["Tổng (Prophet)"] = fc.yhat.values
    return ra
