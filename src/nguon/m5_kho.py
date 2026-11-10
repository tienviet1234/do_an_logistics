"""Dung bo du lieu kho day du tu so ban that M5. Luat ghi TRUOC khi chay: docs/10 muc 10.13.
So ban giu nguyen, luon ghi ro nguon. Doc tu ket qua cua src/nguon/m5.py (du_lieu_nguon/m5), gia M5 goc (data/m5) va Dominick's da gop; ghi vao thu muc rieng.
Chay tai thu muc goc: python src/nguon/m5_kho.py du_lieu_nguon/m5 data/m5 du_lieu_nguon/dominicks/theo_tuan.csv.gz du_lieu_nguon/m5_kho
Roi chay trong thu muc do: python ../../src/nap_database.py; python ../../src/ton_kho.py
"""
import json
import os
import shutil
import sys

import numpy as np
import pandas as pd

TI_GIA = 25000                                  # d/USD, gia dinh de cung don vi voi he thong; KHONG phai gia Viet Nam
CHI_PHI_DAT = 165000.0
HE_THONG_MOC = "tb_truot_28_tuan"               # ten du bao moc he thong dung
MO_HINH_NAP = {"ket_hop_dl": "ket_hop_dl", "tb_truot": HE_THONG_MOC}
CHU_KY, PHU_NGAY, LEAD, CUA_SO = 7, 14, 7, 28   # quy tac kinh nghiem: moi 7 ngay dat du (14 + 7) ngay ban
NGUONG_GIA, TUAN_TRUOC, TOI_THIEU_TUAN = 0.95, 8, 3
NGANH_THUC_PHAM = {"ber", "bjc", "cer", "che", "coo", "cra", "cso", "fec", "frd", "fre", "frj", "oat", "sdr", "sna", "tna"}
NGANH_GIA_DUNG = {"bat", "did", "fsf", "lnd", "ptw", "soa", "tti"}
NHOM_DOMINICKS = {"FOODS": NGANH_THUC_PHAM, "HOUSEHOLD": NGANH_GIA_DUNG}
NGUON = {"ten": "số bán thật M5 (Walmart), dựng thành kho tổng", "la_mo_phong": False, "mo_hinh_chon": "ket_hop_dl", "thu_muc_du_bao": "../m5", "lich_goc": "../../data/m5", "mo_ta_ai": "Công thức + dự báo AI: kết hợp LightGBM + Prophet + RNN theo nhóm",
         "ghi_chu": "Số bán và giá bán là dữ liệu thật M5 (Walmart, Mỹ, 2011–2016), cộng 10 cửa hàng thành một kho tổng; tiền quy đổi 25.000 đ/USD. Biên lãi đo từ Dominick's; lead time, chi phí, tồn kho là giả định.",
         "mo_ta": "<b>Số bán thật M5 (Walmart, Mỹ, 2011–2016)</b>, cộng 10 cửa hàng thành một kho tổng. Mã hàng do M5 ẩn tên; đây không phải số của một kho Việt Nam.",
         "that": "số bán theo ngày, giá bán theo tuần, sự kiện; khuyến mãi suy từ giá; biên lãi đo từ Dominick's (Kilts Center, Chicago Booth).",
         "gia_dinh": "tỉ giá, lead time, chi phí đặt và lưu kho, nhà cung cấp, tồn kho",
         "note_ht": "\\* Hiện trạng: **quy tắc kinh nghiệm giả định** (mỗi 7 ngày đặt đủ 21 ngày bán theo trung bình 28 ngày trước), vì M5 không có số tồn kho."}


def ton_theo_quy_tac(D, dong, chu_ky=CHU_KY, phu=PHU_NGAY, lead=LEAD, cua_so=CUA_SO):
    """Ton kho 1 ma theo quy tac kinh nghiem. Quyet dinh ngay t chi dung so ban truoc t (khong nhin truoc). Ngay nghi khong nhan, khong ban, khong dat."""
    D = np.asarray(D, dtype=float)
    n = len(D)
    if len(dong) != n:
        raise ValueError("D va dong khong cung do dai")
    nhap, xuat, ton = np.zeros(n), np.zeros(n), np.zeros(n)
    dang_ve = []
    con = 0.0
    for t in range(n):
        if dong[t]:
            ton[t] = con
            continue
        ve = sum(q for a, q in dang_ve if a <= t)
        dang_ve = [(a, q) for a, q in dang_ve if a > t]
        con += ve
        nhap[t] = ve
        xuat[t] = min(D[t], con)
        con -= xuat[t]
        ton[t] = con
        if t % chu_ky == 0:
            tb = D[max(0, t - cua_so):t].mean() if t > 0 else 0.0
            can = np.ceil(tb * (phu + lead) - con - sum(q for _, q in dang_ve))
            if can > 0:
                dang_ve.append((t + lead, float(can)))
    return nhap, xuat, ton


def tuan_khuyen_mai(gia):
    """gia: chuoi gia trung binh theo tuan. Tuan khuyen mai: gia <= 95% trung vi 8 tuan truoc (toi thieu 3 tuan), khong nhin truoc."""
    return gia <= NGUONG_GIA * gia.shift(1).rolling(TUAN_TRUOC, min_periods=TOI_THIEU_TUAN).median()


def cac_dot_lien_tiep(ngay_dau_tuan):
    """Gop cac tuan khuyen mai lien tiep thanh dot. Tra ve danh sach (tu ngay, den ngay, so ngay)."""
    ds = sorted(pd.to_datetime(list(ngay_dau_tuan)))
    ra = []
    for d in ds:
        if ra and d == ra[-1][1] + pd.Timedelta(days=1):
            ra[-1][1] = d + pd.Timedelta(days=6)
        else:
            ra.append([d, d + pd.Timedelta(days=6)])
    return [(a, b, int((b - a).days) + 1) for a, b in ra]


def lich_khuyen_mai(gia_tuan, cuoi):
    """gia_tuan: ma_sku, ngay_dau_tuan, gia. Tra ve bang lich_khuyen_mai, cat o ngay cuoi cua du lieu."""
    dong = []
    for ma, g in gia_tuan.sort_values("ngay_dau_tuan").groupby("ma_sku"):
        s = g.set_index("ngay_dau_tuan").gia
        for a, b, _ in cac_dot_lien_tiep(s.index[tuan_khuyen_mai(s).values]):
            if a <= cuoi:
                b = min(b, cuoi)
                dong.append(dict(ma_sku=ma, tu_ngay=a.strftime("%Y-%m-%d"), den_ngay=b.strftime("%Y-%m-%d"), so_ngay=int((b - a).days) + 1))
    return pd.DataFrame(dong, columns=["ma_sku", "tu_ngay", "den_ngay", "so_ngay"])


def bien_lai_nhom(gop):
    """Bien lai gop that cua Dominick's: tu dong theo nganh va tuan (nganh, doanh_thu, gia_von). Tra ve {nhom M5: bien}; nhom khac dung bien toan bo."""
    bien = lambda g: float(1 - g.gia_von.sum() / g.doanh_thu.sum())
    ra = {k: bien(gop[gop.nganh.isin(v)]) for k, v in NHOM_DOMINICKS.items()}
    ra["KHAC"] = bien(gop)
    return ra


def danh_muc(sku, gia_usd, bien, phan_loai):
    """Danh muc ma hang cho he thong. Khong doi ma, khong dat ten hang gia. Thieu gia hoac nhom la thi bao loi."""
    g = sku.ma_sku.map(gia_usd)
    if g.isna().any():
        raise ValueError(f"Thieu gia: {list(sku.ma_sku[g.isna()][:3])}")
    bl = sku.loai_mua_vu.map(lambda c: bien.get(c, bien["KHAC"]))
    pl = phan_loai.set_index("ma_sku")
    gia_ban = g.values * TI_GIA
    return sku.assign(gia_ban=gia_ban.round(0), gia_von=(gia_ban * (1 - bl.values)).round(0), chi_phi_dat_hang=CHI_PHI_DAT, nha_cung_cap="NCC_" + sku.nhom_hang,
                      phan_loai_ABC=sku.ma_sku.map(pl.abc_train).values, phan_loai_XYZ=sku.ma_sku.map(pl.xyz_train).values)


def giao_dich(g):
    """g: giao_dich_sach cua src/nguon/m5.py (qty_out la so ban that). Tra ve (bang sach co ton theo quy tac kinh nghiem, nhu cau that)."""
    ra = []
    for ma, x in g.sort_values("date").groupby("ma_sku"):
        nhap, xuat, ton = ton_theo_quy_tac(x.qty_out.values, x.la_ngay_nghi.values == 1)
        ra.append(x.assign(qty_in=nhap, qty_out=xuat, ton_cuoi_ngay=ton, het_hang=((x.truoc_len_ke.values == 1) | (x.qty_out.values - xuat > 0.5)).astype(int)))
    sach = pd.concat(ra).sort_values(["date", "ma_sku"])[["date", "ma_sku", "qty_in", "qty_out", "ton_cuoi_ngay", "la_ngay_nghi", "het_hang", "co_sua"]]
    return sach, pd.DataFrame({"date": g.date, "ma_sku": g.ma_sku, "nhu_cau_that": g.qty_out})


def chep_du_bao(nguon, ra):
    """Du bao du moi moc cua mo hinh da chon va du bao moc, doi ten moc theo he thong. Khong hoc lai."""
    os.makedirs(f"{ra}/reports/du_bao", exist_ok=True)
    for cu, moi in MO_HINH_NAP.items():
        for tap in ("validation2", "test", "tuong_lai"):
            f = f"{nguon}/reports/du_bao/day_du/{cu}_{tap}.csv"
            if tap == "tuong_lai" and not os.path.exists(f):            # du bao tuong lai (src/du_bao_tuong_lai_kc.py) chi co khi da chay
                continue
            d = pd.read_csv(f, encoding="utf-8-sig")
            d.assign(du_bao=d.du_bao.clip(lower=0)).to_csv(f"{ra}/reports/du_bao/{moi}_{tap}.csv", index=False, encoding="utf-8-sig")
    kq = pd.read_csv(f"{nguon}/reports/ket_qua_mo_hinh.csv", encoding="utf-8-sig")
    kq.assign(mo_hinh=kq.mo_hinh.replace({"tb_truot": HE_THONG_MOC})).to_csv(f"{ra}/reports/ket_qua_mo_hinh.csv", index=False, encoding="utf-8-sig")


def gia_theo_tuan(goc, ma, cal):
    """Gia trung binh toan chuoi theo ma va tuan M5; doc theo khoi vi tep goc lon. Tra ve (bang tuan, gia trung binh USD theo ma)."""
    tong = []
    for k in pd.read_csv(f"{goc}/sell_prices.csv", usecols=["item_id", "wm_yr_wk", "sell_price"], chunksize=1_000_000):
        k = k[k.item_id.isin(ma)]
        if len(k):
            tong.append(k.groupby(["item_id", "wm_yr_wk"]).sell_price.agg(["sum", "count"]))
    t = pd.concat(tong).groupby(level=[0, 1]).sum().reset_index()
    tuan = cal.groupby("wm_yr_wk").date.min()
    bang = pd.DataFrame({"ma_sku": t.item_id, "ngay_dau_tuan": t.wm_yr_wk.map(tuan), "gia": t["sum"] / t["count"]})
    return bang, t.groupby("item_id")["sum"].sum() / t.groupby("item_id")["count"].sum()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    nguon, goc, dom, ra = sys.argv[1:5]
    for t in ["data/clean", "data/reference", "data/raw", "data/answer_key", "data/features", "reports", "database"]:
        os.makedirs(f"{ra}/{t}", exist_ok=True)
    g = pd.read_csv(f"{nguon}/data/clean/giao_dich_sach.csv", encoding="utf-8-sig")
    sku = pd.read_csv(f"{nguon}/data/reference/sku_master.csv", encoding="utf-8-sig")
    pl = pd.read_csv(f"{nguon}/data/features/phan_loai_sku.csv", encoding="utf-8-sig")
    cal = pd.read_csv(f"{goc}/calendar.csv", usecols=["date", "wm_yr_wk"], parse_dates=["date"])
    bang, gia_usd = gia_theo_tuan(goc, set(sku.ma_sku), cal)
    bien = bien_lai_nhom(pd.read_csv(dom, usecols=["nganh", "doanh_thu", "gia_von"]))
    print("bien lai Dominick's:", {k: round(v, 3) for k, v in bien.items()}, flush=True)
    danh_muc(sku, gia_usd, bien, pl).to_csv(f"{ra}/data/reference/sku_master.csv", index=False, encoding="utf-8-sig")
    km = lich_khuyen_mai(bang, pd.Timestamp(g.date.max()))
    km.to_csv(f"{ra}/data/reference/lich_khuyen_mai.csv", index=False, encoding="utf-8-sig")
    sach, nct = giao_dich(g)
    sach.to_csv(f"{ra}/data/clean/giao_dich_sach.csv", index=False, encoding="utf-8-sig")
    nct.to_csv(f"{ra}/data/answer_key/nhu_cau_that.csv", index=False, encoding="utf-8-sig")
    sach[["date", "ma_sku", "qty_in", "qty_out", "ton_cuoi_ngay"]].to_csv(f"{ra}/data/raw/giao_dich_nhap_xuat_ton_THO.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=["date", "ma_sku", "qty_out_tho", "qty_out_da_sua", "loai_loi"]).to_csv(f"{ra}/reports/dong_da_sua.csv", index=False, encoding="utf-8-sig")
    for f in ["lich_su_kien_prophet.csv", "lich_ngay_nghi_kho.csv", "su_kien_dot_bien.csv"]:
        shutil.copy(f"{nguon}/data/reference/{f}", f"{ra}/data/reference/{f}")
    for f in ["phan_loai_sku.csv", "dac_trung.csv"]:                # dac trung: danh_gia.py can khi nap CSDL; khong hoc lai
        shutil.copy(f"{nguon}/data/features/{f}", f"{ra}/data/features/{f}")
    shutil.copy("database/schema.sql", f"{ra}/database/schema.sql")
    chep_du_bao(nguon, ra)
    json.dump(NGUON, open(f"{ra}/data/reference/nguon_du_lieu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    co = sach[sach.la_ngay_nghi == 0]
    print(f"{sku.ma_sku.nunique()} ma | {len(km)} dot khuyen mai | quy tac kinh nghiem: Fill Rate {100 * co.qty_out.sum() / nct.nhu_cau_that[sach.index].sum():.2f}% | so ban goc giu nguyen: {bool((nct.nhu_cau_that.values == g.qty_out.values).all())}", flush=True)
