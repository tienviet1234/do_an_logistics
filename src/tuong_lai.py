"""Dung 28 ngay TUONG LAI (sau ngay cuoi du lieu) voi cac cot biet truoc, de mo hinh du bao ngay chua co thuc te.
Lich biet truoc duoc mo rong theo dung quy tac cua lich hien co:
- su kien / ngay nghi roi vao cung ngay duong lich o it nhat 2 nam: lap lai nam sau (xet tung ngay-thang rieng);
- su kien theo am lich (Tet, Trung thu, Gio To): lay tu bang AM_LICH (ngay duong lich da cong bo);
- su kien khong biet truoc (bao, nang nong, dich benh, tin don) va lich thi dau the thao: KHONG tu suy ra (tuong lai = 0).
Khuyen mai tuong lai chi co neu lich khuyen mai gui truoc co; khong co thi = 0.
Ham thuan, co test (tests/test_tuong_lai.py): dung cho mot khoang NGAY DA QUA phai ra dung cac cot cua data/features/dac_trung.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lich_dac_trung import lich_theo_ngay  # noqa: E402

HORIZON = 28
# Ngay duong lich cua su kien am lich (theo lich am Viet Nam da cong bo). Het bang thi bao loi, khong tu doan.
AM_LICH = {
    "tet": ["2027-02-06", "2028-01-26"],
    "trung_thu": ["2027-09-15", "2028-10-03"],
    "Giỗ Tổ Hùng Vương": ["2027-04-16", "2028-04-04"],
}
TEN_NGHI_TET = "Nghỉ Tết Nguyên đán"
COT_TINH = ["nhom_hang", "loai_mua_vu", "gia_ban", "lead_time_tb", "nha_cung_cap", "abc_train", "xyz_train", "loai_nhu_cau"]


class ThieuLichAmLich(ValueError):
    pass


def _lan_tiep(ten, cuoi, den, am_lich, co_dinh, cua_so_truoc=0):
    """Cac lan xay ra sau `cuoi` ma cua so (bat dau cua_so_truoc ngay truoc) cham toi `den`."""
    if ten in am_lich:
        cac = [pd.Timestamp(x) for x in am_lich[ten] if pd.Timestamp(x) > cuoi]
        moc = cac[-1] if cac else cuoi                  # lan xa nhat da biet; lan ke tiep cach it nhat ~330 ngay (nam am lich)
        if moc + pd.Timedelta(days=330 + cua_so_truoc) <= den:
            raise ThieuLichAmLich(f"Bang AM_LICH cua '{ten}' khong du toi {den.date()} (lan cuoi da biet {moc.date()})")
        return cac
    if co_dinh:
        return [pd.Timestamp(y, cuoi.month, cuoi.day) for y in range(cuoi.year + 1, den.year + 2)]
    return []


def mo_rong_lich(lich, den, am_lich=AM_LICH):
    """lich: lich_su_kien_prophet (holiday, ds, lower_window, upper_window, ...). Them cac lan xay ra tiep theo co cua so
    cham toi `den`. Tra ve (lich moi, danh sach su kien khong tu suy ra duoc)."""
    den = pd.Timestamp(den)
    them, bo = [], []
    for ten, g in lich.groupby("holiday", sort=True):
        if ten.startswith("bao_"):
            continue
        g = g.sort_values("ds")
        if ten in am_lich:
            nhom = [g]
        else:                                           # moi ngay-thang lap lai o >= 2 nam la 1 chuoi rieng (VD le 30/4 va 2/9 chung 1 ten)
            md = g.ds.dt.strftime("%m-%d")
            nhom = [x for _, x in g.groupby(md) if x.ds.dt.year.nunique() >= 2]
            if not nhom:
                bo.append(ten)
                continue
        for x in nhom:
            cuoi = x.iloc[-1]
            for d in _lan_tiep(ten, cuoi.ds, den, am_lich, ten not in am_lich, int(cuoi.lower_window)):
                if d + pd.Timedelta(days=int(cuoi.lower_window)) <= den:
                    them.append({**cuoi.to_dict(), "ds": d})
    moi = pd.concat([lich, pd.DataFrame(them, columns=lich.columns)], ignore_index=True) if them else lich.copy()
    return moi.sort_values(["ds", "holiday"]).reset_index(drop=True), sorted(bo)


def mo_rong_nghi(nghi, lich_mr, den, am_lich=AM_LICH):
    """nghi: (date, ten_ngay_nghi). Ngay nghi co dinh (cung ngay moi nam) lap lai; nghi Tet theo do lech so voi mung 1 Tet;
    ngay nghi am lich lay tu AM_LICH; ngay nghi khac (VD dong cua vi bao) khong tu suy ra."""
    den = pd.Timestamp(den)
    cuoi_du_lieu = nghi.date.max()
    them = []
    tet = sorted(lich_mr.loc[lich_mr.holiday == "tet", "ds"])
    for ten, g in nghi.groupby("ten_ngay_nghi"):
        if ten == TEN_NGHI_TET:
            if not tet:
                continue
            lech = sorted({int((d - max(t for t in tet if t <= d + pd.Timedelta(days=20))).days) for d in g.date})
            for t in tet:
                for k in lech:
                    d = t + pd.Timedelta(days=k)
                    if d > cuoi_du_lieu and d <= den:
                        them.append((d, ten))
            continue
        if ten in am_lich:
            nhom = [g]
        else:
            nhom = [x for _, x in g.groupby(g.date.dt.strftime("%m-%d")) if x.date.dt.year.nunique() >= 2]
        for x in nhom:
            for d in _lan_tiep(ten, x.date.max(), den, am_lich, ten not in am_lich):
                if d <= den:
                    them.append((d, ten))
    moi = pd.concat([nghi, pd.DataFrame(them, columns=["date", "ten_ngay_nghi"])], ignore_index=True) if them else nghi.copy()
    return moi.drop_duplicates().sort_values("date").reset_index(drop=True)


def khuyen_mai_theo_ngay(km, dates, skus):
    """Lich khuyen mai gui truoc -> (date, ma_sku, khuyen_mai) cho cac ngay `dates`; khong co lich = 0 (giong dac_trung.py)."""
    rows = [(dd, r.ma_sku) for r in km.itertuples() for dd in pd.date_range(r.tu_ngay, r.den_ngay)]
    s = pd.DataFrame(rows, columns=["date", "ma_sku"]).astype({"date": "datetime64[ns]"}).drop_duplicates().assign(khuyen_mai=1)
    k = pd.MultiIndex.from_product([dates, skus], names=["date", "ma_sku"]).to_frame(index=False)
    k = k.merge(s, on=["date", "ma_sku"], how="left")
    k["khuyen_mai"] = k.khuyen_mai.fillna(0).astype(int)
    return k


def khung_tuong_lai(df, tu_ngay, lich, nghi, shock, km, so_ngay=HORIZON, mo_rong=True):
    """Cac cot biet truoc (df.attrs['known_ahead']) cho so_ngay ngay sau tu_ngay, moi SKU co trong df.
    Cot tinh cua ma (gia, nhom, ABC/XYZ...) lay o dong cuoi cung cua ma den tu_ngay. Tra ve (khung, ghi_chu)."""
    o = pd.Timestamp(tu_ngay)
    dates = pd.date_range(o + pd.Timedelta(days=1), periods=so_ngay)
    den = dates[-1]
    bo = []
    if mo_rong:
        lich, bo = mo_rong_lich(lich, den)
        nghi = mo_rong_nghi(nghi, lich, den)
    cal = lich_theo_ngay(pd.DatetimeIndex(dates), lich, nghi, shock[shock.tu_ngay <= o])     # bao sau ngay lap: chua biet
    skus = sorted(df.ma_sku.unique())
    k = khuyen_mai_theo_ngay(km[km.tu_ngay <= den], pd.DatetimeIndex(dates), skus)
    tinh = df[df.date <= o].sort_values("date").groupby("ma_sku")[COT_TINH].last().reset_index()
    f = k.merge(cal, on="date", how="left").merge(tinh, on="ma_sku", how="left")
    f["la_ngay_nghi"] = f.date.isin(set(nghi.date)).astype(int)
    known = df.attrs["known_ahead"]
    thieu = [c for c in known if c not in f.columns]
    if thieu:
        raise ValueError(f"Khung tuong lai thieu cot: {thieu}")
    ghi = dict(tu=str(dates[0].date()), den=str(den.date()), su_kien_khong_tu_suy_ra=bo,
               khuyen_mai_co_lich=int(f.khuyen_mai.sum()), ngay_nghi=[str(d.date()) for d in sorted(set(f.date[f.la_ngay_nghi == 1]))])
    return f[known].sort_values(["ma_sku", "date"]).reset_index(drop=True), ghi


def doc_tham_chieu(ref="data/reference"):
    """Doc 4 bang tham chieu nhu dac_trung.py."""
    lich = pd.read_csv(f"{ref}/lich_su_kien_prophet.csv", encoding="utf-8-sig", parse_dates=["ds"])
    nghi = pd.read_csv(f"{ref}/lich_ngay_nghi_kho.csv", encoding="utf-8-sig", parse_dates=["date"])
    shock = pd.read_csv(f"{ref}/su_kien_dot_bien.csv", encoding="utf-8-sig", parse_dates=["tu_ngay", "den_ngay"])
    km = pd.read_csv(f"{ref}/lich_khuyen_mai.csv", encoding="utf-8-sig", parse_dates=["tu_ngay", "den_ngay"])
    return lich, nghi, shock, km
