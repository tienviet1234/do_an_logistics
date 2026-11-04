"""Bo chuyen doi M5 (Walmart) ve cung cau truc he thong dang dung, cho vong kiem chung (docs/10 muc 9.8). So ban GIU NGUYEN.
Chay tai thu muc goc:  python src/nguon/m5.py data/m5 du_lieu_nguon/m5
Ghi vao thu muc lam viec rieng (du lieu mo phong cua de tai khong bi dong toi):
  data/clean/giao_dich_sach.csv, data/reference/{sku_master, lich_su_kien_prophet, lich_ngay_nghi_kho, lich_khuyen_mai, su_kien_dot_bien, nguon_du_lieu}.
Lam sach (ghi trong luat): cong 10 cua hang thanh kho tong; ngay truoc khi ma len ke khong cham diem (het_hang = 1, KHONG danh dau ngay nghi vi ngay
nghi la thong tin biet truoc, se lo ngay len ke); ngay toan chuoi gan nhu dong cua (tong < 20% trung vi) la ngay nghi.
Giả định, chua dung de cham: gia von, lead time, chi phi (khong co trong M5). Khong co: khuyen mai, ton kho, het hang, nha cung cap.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

SO_MA_MAU, HAT_GIONG_MAU = 121, 20261103
NGUONG_DONG_CUA = 0.2
CUA_SO_SU_KIEN = (-3, 1)
TEN_CHUNG = {"Christmas": "noel", "Halloween": "halloween", "ValentinesDay": "valentine", "SuperBowl": "the_thao", "NBAFinalsStart": "the_thao",
             "NBAFinalsEnd": "the_thao", "Mother's day": "phu_nu_vn", "LaborDay": "le_30_4_2_9"}   # dung lai dac trung "so ngay den su kien" da co


def chon_mau(danh_muc, n=SO_MA_MAU, hat_giong=HAT_GIONG_MAU):
    """Chon ngau nhien phan tang theo phong ban, ti le theo so ma (phan du lon nhat), khong xem so ban. danh_muc: item_id, dept_id."""
    d = danh_muc.drop_duplicates("item_id").sort_values("item_id")
    if n >= len(d):
        return list(d.item_id)
    dem = d.dept_id.value_counts().sort_index()
    q = dem * n / len(d)
    so = np.floor(q).astype(int)
    so[(q - so).sort_values(ascending=False, kind="mergesort").index[:n - so.sum()]] += 1
    rng = np.random.default_rng(hat_giong)
    ra = []
    for pb, k in so.items():
        ma = d[d.dept_id == pb].item_id.values
        ra += list(rng.choice(ma, size=int(k), replace=False))
    return sorted(ra)


def ngay_dong_cua(tong_ngay, nguong=NGUONG_DONG_CUA):
    """tong_ngay: Series so ban toan chuoi theo ngay. Ngay rat thap so voi trung vi coi la dong cua."""
    return tong_ngay[tong_ngay < tong_ngay.median() * nguong].index


def bang_giao_dich(ban, dong_cua):
    """ban: bang (ngay x ma) da cong cua hang. Tra ve dang dai theo cau truc data/clean/giao_dich_sach.csv."""
    if (ban.values < 0).any():
        raise ValueError("So ban am")
    co_ban = ban.values > 0
    if not co_ban.any(axis=0).all():
        raise ValueError("Co ma khong ban ngay nao")
    len_ke = co_ban.argmax(axis=0)
    truoc = np.arange(len(ban))[:, None] < len_ke[None, :]
    d = pd.DataFrame({
        "date": np.repeat(ban.index.values, ban.shape[1]), "ma_sku": np.tile(ban.columns.values, len(ban)), "qty_in": 0.0,
        "qty_out": ban.values.ravel().astype(float), "ton_cuoi_ngay": 0, "la_ngay_nghi": 0, "het_hang": truoc.ravel().astype(int), "co_sua": 0,
        "truoc_len_ke": truoc.ravel().astype(int)})
    d.loc[d.date.isin(pd.DatetimeIndex(dong_cua)), "la_ngay_nghi"] = 1
    return d.sort_values(["date", "ma_sku"]).reset_index(drop=True)


def lich_su_kien(cal, cua_so=CUA_SO_SU_KIEN):
    """Su kien + ngay tem phieu SNAP (bang nao) cua M5, theo cau truc lich_su_kien_prophet.csv. Day la thong tin biet truoc."""
    dong = []
    for a, b in [("event_name_1", "event_type_1"), ("event_name_2", "event_type_2")]:
        for r in cal[cal[a].notna()].itertuples():
            ten = getattr(r, a)
            dong.append((TEN_CHUNG.get(ten, "m5_" + "".join(c for c in ten.lower() if c.isalnum())), r.date, cua_so[0], cua_so[1], f"{ten} ({getattr(r, b)})"))
    for bang in ["CA", "TX", "WI"]:
        for d in cal.loc[cal[f"snap_{bang}"] == 1, "date"]:
            dong.append((f"snap_{bang.lower()}", d, 0, 0, f"Tem phieu thuc pham bang {bang}"))
    return pd.DataFrame(dong, columns=["holiday", "ds", "lower_window", "upper_window", "ghi_chu"]).sort_values(["ds", "holiday"]).reset_index(drop=True)


def danh_muc_ma(ma_dm, gia):
    """Danh muc ma hang. gia_ban: gia ban trung binh cua ma (co dinh theo ma, nhu du lieu mo phong). Cac cot khac la gia dinh de chay duoc he thong."""
    d = ma_dm.drop_duplicates("item_id").set_index("item_id")
    g = gia.reindex(d.index)
    if g.isna().any():
        raise ValueError(f"Thieu gia: {list(g[g.isna()].index[:3])}")
    return pd.DataFrame({
        "ma_sku": d.index, "ten_sku": d.index, "nhom_hang": d.dept_id.values, "don_vi": "đơn vị", "gia_von": (g.values * 0.75).round(4), "nhu_cau_tb_ngay": 0.0,
        "xu_huong_nam": 0.0, "lead_time_tb": 7, "cv_nhu_cau": 0.0, "loai_mua_vu": d.cat_id.values, "lead_time_std": 1.5, "chi_phi_dat_hang": 20.0,
        "ty_le_chi_phi_luu_kho": 0.2, "moq": 1, "nha_cung_cap": "GIA_DINH", "gia_ban": g.values.round(4), "ton_kho_ban_dau": 0, "gia_tri_xuat_36t": 0.0,
        "phan_loai_ABC": "B", "cv_theo_thang": 0.0, "phan_loai_XYZ": "Y"})


NGUON = {"ten": "dữ liệu thật M5 (Walmart)", "la_mo_phong": False,
         "ghi_chu": "Số bán là dữ liệu thật M5 (Walmart, 2011–2016) đã cộng thành kho tổng; lead time, giá vốn, chi phí là giả định.",
         "mo_ta": "<b>Dữ liệu thật M5 (Walmart)</b>, dùng để kiểm chứng quy trình. Mã hàng được ẩn tên, thị trường Mỹ, không có khuyến mãi, tồn kho và cờ hết hàng.",
         "that": "số bán theo ngày, giá bán theo tuần, sự kiện, ngày tem phiếu SNAP.", "gia_dinh": "lead time, giá vốn, chi phí đặt hàng và lưu kho"}


def chuyen_doi(nguon, ra):
    cal = pd.read_csv(f"{nguon}/calendar.csv", parse_dates=["date"])
    hdr = pd.read_csv(f"{nguon}/sales_train_evaluation.csv", nrows=0).columns
    cot_ngay = [c for c in hdr if c.startswith("d_")]
    ban = pd.read_csv(f"{nguon}/sales_train_evaluation.csv", dtype={c: "int32" for c in cot_ngay}, usecols=["item_id", "dept_id", "cat_id"] + cot_ngay)
    ngay = pd.DatetimeIndex(cal.date[:len(cot_ngay)])
    assert (np.diff(ngay.values) == np.timedelta64(1, "D")).all(), "lich M5 khong lien tuc"
    dm = ban[["item_id", "dept_id", "cat_id"]].drop_duplicates("item_id")
    gop = ban.groupby("item_id")[cot_ngay].sum().T
    gop.index = ngay
    dong = ngay_dong_cua(gop.sum(axis=1))
    mau = chon_mau(dm)
    gop = gop[mau]
    gia = pd.read_csv(f"{nguon}/sell_prices.csv").groupby("item_id").sell_price.mean()
    for t in ["data/clean", "data/reference", "reports", "database"]:
        os.makedirs(f"{ra}/{t}", exist_ok=True)
    g = bang_giao_dich(gop, dong)
    g.assign(date=g.date.dt.strftime("%Y-%m-%d")).to_csv(f"{ra}/data/clean/giao_dich_sach.csv", index=False, encoding="utf-8-sig")
    danh_muc_ma(dm[dm.item_id.isin(mau)], gia).to_csv(f"{ra}/data/reference/sku_master.csv", index=False, encoding="utf-8-sig")
    ls = lich_su_kien(cal[cal.date <= ngay[-1]])
    ls.assign(ds=ls.ds.dt.strftime("%Y-%m-%d")).to_csv(f"{ra}/data/reference/lich_su_kien_prophet.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"date": pd.DatetimeIndex(dong).strftime("%Y-%m-%d"), "ten_ngay_nghi": "Đóng cửa (suy từ số bán)"}).to_csv(f"{ra}/data/reference/lich_ngay_nghi_kho.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=["ma_sku", "tu_ngay", "den_ngay", "so_ngay"]).to_csv(f"{ra}/data/reference/lich_khuyen_mai.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=["nhom_ly_do", "su_kien", "tu_ngay", "den_ngay", "muc_do_0_1", "nguon_du_lieu", "tac_dong_chinh", "ghi_chu_hoac_sku"]).to_csv(f"{ra}/data/reference/su_kien_dot_bien.csv", index=False, encoding="utf-8-sig")
    json.dump(NGUON, open(f"{ra}/data/reference/nguon_du_lieu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tl = g[g.het_hang == 1].shape[0] / len(g)
    print(f"{len(mau)} ma x {len(ngay)} ngay = {len(g):,} dong | {ngay[0].date()} .. {ngay[-1].date()} | dong cua: {list(pd.DatetimeIndex(dong).strftime('%Y-%m-%d'))} | truoc len ke: {tl:.1%} | phong ban: {dm[dm.item_id.isin(mau)].dept_id.value_counts().to_dict()}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chuyen_doi(sys.argv[1], sys.argv[2])
