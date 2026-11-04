"""Khong phu thuoc vao 1 bo du lieu cu the: moc thoi gian tu suy tu ngay cuoi cua du lieu, kiem tra dau vao truoc khi chay.
Ham thuan, co test: tests/test_kiem_tra_du_lieu.py. Du lieu moi sai cau truc phai bao loi ngay, khong chay tiep ra so sai.
Chay rieng: python src/kiem_tra_du_lieu.py   (kiem tra data/clean/giao_dich_sach.csv cua thu muc hien tai)
"""
import json
import os
import sys

import pandas as pd

NGAY_TEST = 365                  # 1 nam cuoi: kiem tra
NGAY_VALIDATION2 = 365           # 1 nam truoc do: chon mo hinh (cung mua voi tap kiem tra)
NGAY_VALIDATION = 183            # vong 1: nua nam truoc tap kiem tra
SO_NGAY_TOI_THIEU = 2 * 365      # it nhat 1 nam validation + 1 nam kiem tra
COT_SACH = ["date", "ma_sku", "qty_in", "qty_out", "ton_cuoi_ngay", "la_ngay_nghi", "het_hang"]


NGUON_MAC_DINH = {
    "ten": "dữ liệu mô phỏng", "ghi_chu": "Dữ liệu mô phỏng, không phải số liệu kho thật.", "la_mo_phong": True,
    "mo_ta": ("<b>Đây là dữ liệu mô phỏng</b> (máy sinh ra theo quy tắc), vì chưa có dữ liệu từ kho thật. Tên hàng là sản phẩm phổ biến "
              "trên thị trường nhưng <b>mọi con số không phải của hãng hay của kho nào</b>. Mục tiêu là xây <b>quy trình</b> dự báo và đặt hàng "
              "rồi so sánh các cách làm trên cùng dữ liệu; các con số là kết quả trên bộ dữ liệu này, dữ liệu khác sẽ cho số khác."),
    "that": "ngày các cơn bão (Yagi 07/09/2024, các bão năm 2025), lễ Tết, Trung thu, lịch sale 11.11 / 12.12 / Black Friday; giá bán lẻ 37 mã tra ngày 24/10/2026.",
    "gia_dinh": "lượng bán từng ngày, mức tăng do lễ, bão, khuyến mãi; giá vốn, chi phí đặt hàng, lưu kho; thời gian giao hàng; lỗi cài sẵn trong dữ liệu thô",
}


def nguon_du_lieu(goc="."):
    """Mo ta nguon du lieu dang chay (data/reference/nguon_du_lieu.json); khong co tep -> du lieu mo phong cua de tai."""
    f = os.path.join(goc, "data", "reference", "nguon_du_lieu.json")
    if not os.path.exists(f):
        return dict(NGUON_MAC_DINH)
    with open(f, encoding="utf-8") as t:
        return {**NGUON_MAC_DINH, **json.load(t)}


class LoiDuLieu(ValueError):
    """Du lieu dau vao khong dung duoc."""


def moc_thoi_gian(ngay_cuoi):
    """Cac moc chia tap theo thoi gian, suy tu ngay cuoi cua du lieu."""
    cuoi = pd.Timestamp(ngay_cuoi).normalize()
    het_hoc = cuoi - pd.Timedelta(days=NGAY_TEST)
    return dict(DATA_END=cuoi, TRAIN_END=het_hoc, VAL2_START=het_hoc - pd.Timedelta(days=NGAY_VALIDATION2),
                VAL_START=het_hoc - pd.Timedelta(days=NGAY_VALIDATION))


def ngay_cuoi_cua(path):
    """Ngay cuoi trong 1 tep du lieu co cot date."""
    return pd.to_datetime(pd.read_csv(path, encoding="utf-8-sig", usecols=["date"]).date).max()


def kiem_tra_giao_dich(df, ma_danh_muc=None, so_ngay_toi_thieu=SO_NGAY_TOI_THIEU):
    """Tra ve (loi, canh_bao). Loi: khong duoc chay tiep. Canh bao: chay duoc nhung phai doc."""
    thieu = [c for c in COT_SACH if c not in df.columns]
    if thieu:
        return [f"Thieu cot: {thieu}"], []
    if df.empty:
        return ["Du lieu rong"], []
    loi, cb = [], []
    ngay = pd.to_datetime(df.date, errors="coerce")
    if ngay.isna().any():
        loi.append(f"{int(ngay.isna().sum())} dong co ngay khong doc duoc")
        return loi, cb
    d = df.assign(date=ngay)
    trung = int(d.duplicated(["date", "ma_sku"]).sum())
    if trung:
        loi.append(f"{trung} dong trung (ngay, ma)")
    for c in ["qty_in", "qty_out"]:
        so = pd.to_numeric(d[c], errors="coerce")
        if (so < 0).any():
            loi.append(f"{int((so < 0).sum())} dong {c} am")
    if pd.to_numeric(d.qty_out, errors="coerce").isna().any():
        loi.append(f"{int(pd.to_numeric(d.qty_out, errors='coerce').isna().sum())} dong qty_out khong phai so hoac rong")
    cac_ngay = pd.date_range(d.date.min(), d.date.max())
    if len(cac_ngay) < so_ngay_toi_thieu:
        loi.append(f"Chi co {len(cac_ngay)} ngay, can it nhat {so_ngay_toi_thieu} ngay de chia tap")
    thieu_ngay = len(cac_ngay) - d.date.nunique()
    if thieu_ngay:
        cb.append(f"{thieu_ngay} ngay khong co dong nao")
    dem = d.groupby("ma_sku").date.count()
    khong_du = dem[dem < len(cac_ngay)]
    if len(khong_du):
        cb.append(f"{len(khong_du)}/{len(dem)} ma khong du moi ngay (ma moi hoac ngung ban): {list(khong_du.index[:5])}")
    if ma_danh_muc is not None:
        co, dm = set(d.ma_sku), set(ma_danh_muc)
        if co - dm:
            loi.append(f"{len(co - dm)} ma khong co trong danh muc: {sorted(co - dm)[:5]}")
        if dm - co:
            cb.append(f"{len(dm - co)} ma trong danh muc khong co giao dich: {sorted(dm - co)[:5]}")
    tl_0 = (pd.to_numeric(d.qty_out, errors="coerce").fillna(0) == 0).mean()
    if tl_0 > 0.5:
        cb.append(f"{tl_0:.0%} dong ban bang 0: nen xem lai cach xu ly hang ban thua")
    return loi, cb


def dam_bao_hop_le(df, ma_danh_muc=None, ten="du lieu"):
    """Bao loi neu du lieu khong dung duoc; in canh bao."""
    loi, cb = kiem_tra_giao_dich(df, ma_danh_muc)
    for x in cb:
        print(f"CANH BAO ({ten}): {x}", flush=True)
    if loi:
        raise LoiDuLieu(f"{ten} khong dung duoc:\n  - " + "\n  - ".join(loi))


def ngay_mac_dinh(ngay_mo_cua, cac_tet=(), truoc_tet=8):
    """Ngay mo san khi mo dashboard: truoc Tet gan nhat trong ky (nhieu viec de xem); khong co Tet thi lay ngay giua ky.
    ngay_mo_cua: danh sach ngay chuoi YYYY-MM-DD da sap xep."""
    if not len(ngay_mo_cua):
        raise LoiDuLieu("Khong co ngay mo cua nao")
    co = set(ngay_mo_cua)
    for t in sorted(cac_tet):
        d = (pd.Timestamp(t) - pd.Timedelta(days=truoc_tet)).strftime("%Y-%m-%d")
        if d in co:
            return d
    return ngay_mo_cua[len(ngay_mo_cua) // 2]


def cac_moc_o_giua(moc, su_kien_theo_loai, truoc=28):
    """Moc de ve bieu do truoc su kien: voi moi loai, lan GAN NHAT co moc trong vong `truoc` ngay truoc do. Tra ve [(moc, ten loai)]
    xep theo ngay. Khong loai nao hop le (VD du lieu khong co Tet) -> 2 moc o 1/3 va 2/3 ky, ten loai None."""
    moc = sorted(pd.Timestamp(x) for x in moc)
    if not moc:
        return []
    ra = []
    for ten, ngay in su_kien_theo_loai.items():
        for s in sorted((pd.Timestamp(x) for x in ngay), reverse=True):
            hop_le = [m for m in moc if s - pd.Timedelta(days=truoc) <= m < s]
            if hop_le:
                ra.append((hop_le[0], ten))
                break
    return sorted(ra, key=lambda x: x[0]) if ra else [(moc[len(moc) // 3], None), (moc[2 * len(moc) // 3], None)]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    du_lieu = pd.read_csv("data/clean/giao_dich_sach.csv", encoding="utf-8-sig")
    loi_, cb_ = kiem_tra_giao_dich(du_lieu)
    print(f"{len(du_lieu):,} dong, {du_lieu.ma_sku.nunique()} ma")
    print("LOI:", loi_ or "khong")
    print("CANH BAO:", cb_ or "khong")
    print({k: str(v.date()) for k, v in moc_thoi_gian(pd.to_datetime(du_lieu.date).max()).items()})
    sys.exit(1 if loi_ else 0)


