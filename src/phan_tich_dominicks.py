"""Doi chieu gia dinh voi du lieu that Dominick's (Kilts Center, Chicago Booth). Luat ghi TRUOC khi tinh: docs/10 muc 10.9. Chi doc; khong doi gia dinh, mo phong, dashboard.
Buoc 1: gop tung cua hang thanh toan chuoi theo ma va tuan -> du_lieu_nguon/dominicks/theo_tuan.csv.gz (tep goc 13 GB, doc theo khoi).
Buoc 2: he so deal, phu theo thoi gian, muc tai tro, bien lai, do sau giam gia, mua truoc roi giam, thu newsvendor.
Buoc 3 (docs/10 muc 10.10): he so theo dai giam gia -> reports/dominicks_he_so_deal.json (dashboard doc), kiem tra -> reports/tru_hang_live_sau_doi_chieu.md
Chay: python src/phan_tich_dominicks.py --buoc gop | tinh | sau_doi_chieu   (tai thu muc goc) -> reports/dominicks.md, reports/dominicks_trang_thai.json
"""
import json
import os
import sys
from dataclasses import replace

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GOC = "data/dominicks"
GOP = "du_lieu_nguon/dominicks/theo_tuan.csv.gz"
STATE = "reports/dominicks_trang_thai.json"
REPORT = "reports/dominicks.md"
BO_NGANH = {"cig"}                              # thuoc la: bi dieu tiet, khong co trong danh muc
LAI_MIN, LAI_MAX = -50.0, 80.0
NGUONG_CO, NGUONG_GIA = 0.5, 0.95               # >= 50% cua hang co co, hoac don gia <= 95% gia 8 tuan truoc
TUAN_TRUOC, TOI_THIEU_TUAN = 8, 3
NEN_TOI_THIEU, CUA_HANG_TOI_THIEU = 20, 10
GIAM_TOI_THIEU = 0.05
PHAN_DO = 2 / 3                                 # 2/3 dau de do, 1/3 sau de kiem
LECH_TRUNG_VI = 0.25                            # luat 10.9
TAI_TRO_THAP, TAI_TRO_CAO, TAI_TRO_GIA_DINH = 0.5, 0.9, 0.7
SAU_KM_NGUONG = 0.9
DAI_GIAM = [(0.05, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.50), (0.50, 0.90)]
# 62 tuan le trong bang tuan cua tai lieu Dominick's (muc "Week's Decode Table")
TUAN_SU_KIEN = {7, 11, 15, 16, 23, 28, 37, 51, 59, 63, 67, 68, 75, 81, 89, 103, 112, 116, 119, 120, 128, 133, 141, 156, 164, 168, 172, 173, 180, 185, 194, 208,
                216, 220, 224, 225, 232, 238, 246, 260, 268, 272, 276, 277, 284, 289, 298, 312, 320, 324, 328, 329, 336, 341, 350, 364, 372, 377, 380, 381, 389, 393}


# ------------------------------------------------------------------ buoc 1: gop toan chuoi
def gop_khoi(d):
    """1 khoi dong cua tep goc -> tong theo ma va tuan. Don gia = PRICE / QTY; bo OK = 0, gia hoac so ban bang 0, lai ngoai khoang."""
    d = d[(d.OK == 1) & (d.PRICE > 0) & (d.MOVE > 0) & (d.QTY > 0) & d.PROFIT.between(LAI_MIN, LAI_MAX)]
    doanh_thu = d.PRICE / d.QTY * d.MOVE
    x = pd.DataFrame({"UPC": d.UPC.values, "WEEK": d.WEEK.values, "move": d.MOVE.values, "doanh_thu": doanh_thu.values, "gia_von": (doanh_thu * (1 - d.PROFIT / 100)).values,
                      "so_cua_hang": 1, "so_co": d.SALE.notna().astype(int).values})
    return x.groupby(["UPC", "WEEK"], as_index=False).sum(), d[["WEEK", "STORE"]].drop_duplicates()


def gop_nganh(cac_khoi, cac_cua_hang):
    """Noi cac khoi cua 1 nganh; them n_ch = so cua hang co ban nganh do trong tuan."""
    g = pd.concat(cac_khoi).groupby(["UPC", "WEEK"], as_index=False).sum()
    n = pd.concat(cac_cua_hang).drop_duplicates().groupby("WEEK").STORE.nunique()
    return g.assign(n_ch=g.WEEK.map(n))


def chay_gop():
    os.makedirs(os.path.dirname(GOP), exist_ok=True)
    ra = []
    for f in sorted(os.listdir(GOC)):
        nganh = f[1:-4]
        if not (f.startswith("w") and f.endswith(".csv")) or nganh in BO_NGANH:
            continue
        khoi, ch = [], []
        for d in pd.read_csv(os.path.join(GOC, f), usecols=["STORE", "UPC", "WEEK", "MOVE", "QTY", "PRICE", "SALE", "PROFIT", "OK"], dtype={"SALE": "category"}, chunksize=500_000):      # may it RAM: khoi nho
            a, b = gop_khoi(d)
            khoi.append(a)
            ch.append(b)
        g = gop_nganh(khoi, ch).assign(nganh=nganh)
        ra.append(g)
        print(nganh, len(g), flush=True)
    t = pd.concat(ra)
    t.to_csv(GOP, index=False, compression="gzip")
    print("xong", len(t), "dong", t.nganh.nunique(), "nganh", flush=True)


# ------------------------------------------------------------------ buoc 2: chi so tung ma
def _truot(s):
    return s.shift(1).rolling(TUAN_TRUOC, min_periods=TOI_THIEU_TUAN).median()


def chi_so_ma(g):
    """1 ma cua 1 nganh, cac tuan lien tiep (tuan khong ban = NaN). Moi moc 'thuong' chi dung TUAN TRUOC, khong nhin truoc."""
    g = g.set_index("WEEK").sort_index()
    g = g.reindex(range(int(g.index.min()), int(g.index.max()) + 1))
    p, c = g.doanh_thu / g.move, g.gia_von / g.move
    km = (g.so_co / g.so_cua_hang >= NGUONG_CO) | (p <= NGUONG_GIA * _truot(p))
    tt = ~km & g.move.notna()                                      # tuan thuong that (khong tinh tuan khong ban)
    chuan = g.move / g.n_ch
    r = pd.DataFrame({"move": g.move, "chuan": chuan, "km": km & g.move.notna(), "co": g.so_co / g.so_cua_hang >= NGUONG_CO, "so_cua_hang": g.so_cua_hang, "p": p, "c": c,
                      "nen": _truot(chuan.where(tt)), "nen_tong": _truot(g.move.where(tt)), "p_thuong": _truot(p.where(tt)), "c_thuong": _truot(c.where(tt))})
    r["sau_km"] = tt & km.shift(1, fill_value=False) & g.move.notna()
    return r[r.move.notna()].reset_index()


def bang_chi_so(t):
    ra = [chi_so_ma(g).assign(nganh=n, UPC=u) for (n, u), g in t.groupby(["nganh", "UPC"], sort=False) if len(g) > TOI_THIEU_TUAN]
    return pd.concat(ra, ignore_index=True)


def loc_du_mau(b):
    """Tuan du dieu kien: co muc nen, du ban, du cua hang."""
    return b[(b.nen > 0) & (b.nen_tong >= NEN_TOI_THIEU) & (b.so_cua_hang >= CUA_HANG_TOI_THIEU)]


def mau_deal(b):
    """He so deal: tuan khuyen mai ngoai tuan le, so voi muc nen."""
    x = loc_du_mau(b)
    x = x[x.km & ~x.WEEK.isin(TUAN_SU_KIEN)]
    return x.assign(ti_so=x.chuan / x.nen, giam=1 - x.p / x.p_thuong)


def tach_thoi_gian(x, tuan_nganh):
    """2/3 dau moi nganh de do, 1/3 sau de kiem. tuan_nganh: {nganh: (tuan dau, tuan cuoi)}."""
    moc = x.nganh.map({n: a + PHAN_DO * (z - a) for n, (a, z) in tuan_nganh.items()})
    return x[x.WEEK <= moc], x[x.WEEK > moc]


def tom_tat_he_so(s):
    s = np.asarray(s, dtype=float)
    return dict(n=int(len(s)), tb=float(s.mean()), p10=float(np.quantile(s, 0.1)), p50=float(np.quantile(s, 0.5)), p90=float(np.quantile(s, 0.9)),
                tu_3=float(100 * (s >= 3).mean()), tu_5=float(100 * (s >= 5).mean()), tu_10=float(100 * (s >= 10).mean()))


def phu_theo_thoi_gian(x, tuan_nganh, muc=(0.5, 0.75, 0.9)):
    """Do phan vi he so deal tren phan dau, xem phu bao nhieu % o phan sau. Tra ve gop va tung nganh (phan vi do tren chinh nganh do)."""
    dau, sau = tach_thoi_gian(x, tuan_nganh)
    gop = {str(m): float(100 * (sau.ti_so <= np.quantile(dau.ti_so, m)).mean()) for m in muc}
    theo = {}
    for n, s in sau.groupby("nganh"):
        d = dau[dau.nganh == n]
        if len(d) >= 30 and len(s) >= 30:
            theo[n] = {str(m): float(100 * (s.ti_so <= np.quantile(d.ti_so, m)).mean()) for m in muc}
    return dict(so_dau=int(len(dau)), so_sau=int(len(sau)), gop=gop, theo_nganh=theo)


def dat_phu(phu, nguong=5.0):
    return all(abs(v - 100 * float(m)) <= nguong for m, v in phu.items())


def muc_tai_tro(b):
    """Nha san xuat ganh bao nhieu phan giam gia: tong (giam gia von x so luong) / tong (giam don gia x so luong), cac tuan giam >= 5%."""
    x = b[b.km & b.p_thuong.notna() & b.c_thuong.notna()]
    x = x[1 - x.p / x.p_thuong >= GIAM_TOI_THIEU]
    if not len(x):
        return None
    giam_gia_ban = ((x.p_thuong - x.p) * x.move).sum()
    return float(((x.c_thuong - x.c) * x.move).sum() / giam_gia_ban), int(len(x))


def bien_lai(b):
    """Bien lai gop theo doanh thu: tuan thuong, tuan khuyen mai; va phan bo theo ma (tuan thuong)."""
    def bien(x):
        return float(1 - (x.c * x.move).sum() / (x.p * x.move).sum())
    tt, km = b[~b.km], b[b.km]
    tong = tt.assign(dt=tt.p * tt.move, gv=tt.c * tt.move).groupby(["nganh", "UPC"])[["dt", "gv"]].sum()
    theo_ma = 1 - tong.gv / tong.dt
    return dict(thuong=bien(tt), km=bien(km), ma_p10=float(theo_ma.quantile(0.1)), ma_p50=float(theo_ma.quantile(0.5)), ma_p90=float(theo_ma.quantile(0.9)), ti_le_tuan_km=float(100 * b.km.mean()), co_trong_km=float(100 * b.co[b.km].mean()))


def theo_do_sau(x):
    """Trung vi he so deal theo dai giam gia; do co gian = he so hoi quy log(he so) theo log(1 - giam), doi dau."""
    dai = [dict(tu=a, den=z, n=int(((x.giam >= a) & (x.giam < z)).sum()), p50=float(x.ti_so[(x.giam >= a) & (x.giam < z)].median()) if ((x.giam >= a) & (x.giam < z)).any() else float("nan")) for a, z in DAI_GIAM]
    y = x[(x.giam >= DAI_GIAM[0][0]) & (x.giam < DAI_GIAM[-1][1]) & (x.ti_so > 0)]
    co_gian = float(-np.polyfit(np.log(1 - y.giam), np.log(y.ti_so), 1)[0]) if len(y) > 2 else float("nan")
    return dict(dai=dai, co_gian=co_gian)


def sau_khuyen_mai(b):
    x = loc_du_mau(b)
    x = x[x.sau_km & ~x.WEEK.isin(TUAN_SU_KIEN)]
    r = x.chuan / x.nen
    return dict(n=int(len(r)), p50=float(r.median()) if len(r) else float("nan"), tb=float(r.mean()) if len(r) else float("nan"))


def thu_newsvendor(ds, nen, mau_mp, mau_dau, mau_sau):
    """Luat 10.9 muc 7. Cham tren he so that phan sau; Q theo he so mo phong (a) hoac he so that phan dau (b)."""
    import tru_hang_live as L
    gd = L.GiaDinh()
    ra = {}
    for h in L.HANG_THUA:
        ra[h] = {}
        for p_thuc in (0.2, 0.0):
            thuc = replace(gd, p_xu_huong=p_thuc)
            ra[h][str(p_thuc)] = {ten: L.tong_ca_kho(ds, nen, m, h, gd, L.SO_PHIEN_DO_NHAY, thuc, hai_buoc=False, he_so_deal_thuc=mau_sau)["phuong_an"] for ten, m in [("mo_phong", mau_mp), ("that", mau_dau)]}
    return ra


def quy_mo_theo_gia(giam, co_gian, goc=0.15):
    """So ban doi bao nhieu lan khi muc giam khac muc goc, theo do co gian: ((1 - giam) / (1 - goc)) ^ (-co_gian)."""
    return float(((1 - giam) / (1 - goc)) ** (-co_gian))


def thu_tai_tro_co_gian(ds, nen, mau, co_gian, tai_tro_that):
    """Them SAU khi thay ket qua (ghi ro trong bao cao): lai newsvendor theo muc giam va tai tro, khong co gian va co gian theo so that."""
    import tru_hang_live as L
    ra = []
    for g in (0.10, 0.15, 0.30):
        for f in (TAI_TRO_GIA_DINH, tai_tro_that):
            d = dict(giam=g, tai_tro=f)
            for ten, e in (("khong", 0.0), ("co", co_gian)):
                gd = replace(L.GiaDinh(), giam_gia=g, tai_tro=f, quy_mo=quy_mo_theo_gia(g, e))
                kq = L.tong_ca_kho(ds, nen, mau, "ve_kho", gd, L.SO_PHIEN_DO_NHAY, hai_buoc=False)
                d[f"lai_{ten}"], d[f"von_{ten}"], d["so_ma_lai"] = kq["phuong_an"]["newsvendor"]["lai"], kq["phuong_an"]["newsvendor"]["q"], kq["so_ma_lai"]
            ra.append(d)
    return ra


# ------------------------------------------------------------------ buoc 3: ban sau doi chieu (muc 10.10)
def chia_dai(x):
    """{(tu, den): cac tuan khuyen mai co muc giam trong dai}."""
    return {(a, z): x[(x.giam >= a) & (x.giam < z)] for a, z in DAI_GIAM}


def he_so_gon(x, co_gian, tai_tro, so_diem=1000):
    """He so deal theo dai giam gia, luu luoi phan vi de dashboard rut mau (tep nho, khong can 13 GB goc)."""
    q = (np.arange(so_diem) + 0.5) / so_diem
    return dict(nguon="Dominick's, Kilts Center, Chicago Booth; sieu thi My 1989-1997, so ban theo tuan", co_gian=co_gian, tai_tro=tai_tro,
                dai=[dict(tu=a, den=z, n=int(len(s)), tb=float(s.ti_so.mean()), p50=float(s.ti_so.median()), phan_vi=[round(float(v), 3) for v in np.quantile(s.ti_so, q)]) for (a, z), s in chia_dai(x).items()])


def phu_theo_dai(x, tuan_nganh):
    """Do tren 2/3 dau, kiem tren 1/3 sau, rieng tung dai giam gia."""
    ra = {}
    for (a, z), s in chia_dai(x).items():
        p = phu_theo_thoi_gian(s, tuan_nganh)
        ra[f"{a}-{z}"] = dict(p, dat=dat_phu(p["gop"]), nganh_dat=sum(dat_phu(v) for v in p["theo_nganh"].values()), so_nganh=len(p["theo_nganh"]))
    return ra


def thu_sau_doi_chieu(ds, nen, dau, sau, tai_tro):
    """Muc 10.10 phan 2: Q tinh tren 2/3 dau cua dung dai, cham tren 1/3 sau. Tra ve bang va cac truong hop newsvendor thua."""
    import tru_hang_live as L
    bang, thua = [], []
    for g in (0.10, 0.15, 0.30):
        k = next((a, z) for a, z in DAI_GIAM if a <= g < z)
        m_dau, m_sau = chia_dai(dau)[k].ti_so.values, chia_dai(sau)[k].ti_so.values
        gd = replace(L.GiaDinh(), giam_gia=g, tai_tro=tai_tro)
        for h in L.HANG_THUA:
            for p_thuc in (0.2, 0.0):
                kq = L.tong_ca_kho(ds, nen, m_dau, h, gd, L.SO_PHIEN_DO_NHAY, replace(gd, p_xu_huong=p_thuc), hai_buoc=False, he_so_deal_thuc=m_sau)
                pa = kq["phuong_an"]
                bang.append(dict(giam=g, hang_thua=h, p=p_thuc, so_ma_lai=kq["so_ma_lai"], **{k_: pa[k_]["lai"] for k_ in ("ngay_thuong", "trung_binh", "newsvendor")}, von=pa["newsvendor"]["q"]))
                if pa["newsvendor"]["lai"] < max(pa["ngay_thuong"]["lai"], pa["trung_binh"]["lai"]):
                    thua.append(f"giảm {int(100 * g)}%, {L.HANG_THUA[h]}, p = {int(100 * p_thuc)}%")
    return bang, thua


def ben_trong(kq):
    """Theo luat: newsvendor khong thap hon 2 phuong an so sanh o moi truong hop. Tra ve {hang thua: cac truong hop thua}."""
    return {h: [f"p = {p}, Q theo {t}" for p, d in v.items() for t, x in d.items() if x["newsvendor"]["lai"] < max(x["ngay_thuong"]["lai"], x["trung_binh"]["lai"])] for h, v in kq.items()}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    buoc = sys.argv[sys.argv.index("--buoc") + 1]
    if buoc == "gop":
        chay_gop()
        raise SystemExit
    import tru_hang_live as L
    t = pd.read_csv(GOP)
    b = bang_chi_so(t)
    tuan_nganh = {n: (int(g.WEEK.min()), int(g.WEEK.max())) for n, g in t.groupby("nganh")}
    x = mau_deal(b)
    print("so tuan km", len(x), flush=True)
    mau_mp, _, bang, km, nghi = L.mau_deal_truoc()
    if buoc == "sau_doi_chieu":
        so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
        tr = lambda v: so(v / 1e6)
        ttro = muc_tai_tro(b)[0]
        co_gian = theo_do_sau(x)["co_gian"]
        hs = he_so_gon(x, co_gian, ttro)
        json.dump(hs, open(L.TEP_HE_SO_THAT, "w", encoding="utf-8"), ensure_ascii=False)
        ds, nen = L.ma_va_muc_nen(bang, km, nghi)
        gd = replace(L.GiaDinh(), tai_tro=L.TAI_TRO_SAU_DOI_CHIEU)
        phu = phu_theo_dai(x, tuan_nganh)
        print("xong phu", flush=True)
        dau, sau = tach_thoi_gian(x, tuan_nganh)
        bang_nv, thua = thu_sau_doi_chieu(ds, nen, dau, sau, L.TAI_TRO_SAU_DOI_CHIEU)
        print("xong newsvendor", flush=True)
        mau_15 = L.mau_theo_giam(hs, gd.giam_gia)
        sau_dc = {h: L.tong_ca_kho(ds, nen, mau_15, h, gd, L.SO_PHIEN_DO_NHAY) for h in L.HANG_THUA}
        truoc = {h: L.tong_ca_kho(ds, nen, mau_mp, h, L.GiaDinh(), L.SO_PHIEN_DO_NHAY, hai_buoc=False) for h in L.HANG_THUA}
        ket = dict(tai_tro_do=ttro, co_gian=co_gian, phu=phu, newsvendor=bang_nv, thua=thua, sau=sau_dc, truoc=truoc, dai=[{k: d[k] for k in ("tu", "den", "n", "tb", "p50")} for d in hs["dai"]])
        json.dump(ket, open("reports/tru_hang_live_sau_doi_chieu_trang_thai.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        L_ = ["# Trữ hàng livestream, bản sau đối chiếu với Dominick's", "", "Luật: docs/10 mục 10.10, viết sau khi đã thấy kết quả 10.8 và 10.9. Hệ số deal theo đúng dải giảm giá, số thật siêu thị Mỹ 1989–1997 theo tuần; tài trợ mặc định 45%. Bùng nổ, phí sàn, hủy đơn vẫn là giả định; biên lãi 121 mã vẫn là mô phỏng. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business.", "",
              "## 1. Phép đo theo dải có giữ được cho thời kỳ sau không", "", "| Dải giảm | Số tuần | Trung vị | Trung bình | Phủ 50% | Phủ 75% | Phủ 90% | Theo luật | Ngành đạt |\n|---|---:|---:|---:|---:|---:|---:|---|---:|"]
        for d in hs["dai"]:
            r = phu[f"{d['tu']}-{d['den']}"]
            L_.append(f"| {so(100 * d['tu'], 0)}–{so(100 * d['den'], 0)}% | {so(d['n'], 0)} | ×{so(d['p50'], 2)} | ×{so(d['tb'], 2)} | " + " | ".join(f"{so(r['gop'][m])}%" for m in ("0.5", "0.75", "0.9")) + f" | {'Đạt' if r['dat'] else 'Không đạt'} | {r['nganh_dat']}/{r['so_nganh']} |")
        L_ += ["", f"So với cách gộp mọi mức giảm ở mục 10.9: không đạt, 4/27 ngành đạt.", "", "## 2. Newsvendor trên số thật", "", "Q tính trên 2/3 đầu của đúng dải, chấm trên 1/3 sau; tài trợ 45%. Lãi kỳ vọng, triệu đ toàn kho. Mức giảm 30% rơi vào dải 30–50% nên hệ số có thể cao hơn thực tế.", "",
               "| Giảm | Hàng thừa | Bùng nổ thực tế | Mã còn lãi | Theo ngày thường | Theo trung bình | Newsvendor | Vốn trữ newsvendor |\n|---:|---|---:|---:|---:|---:|---:|---:|"]
        L_ += [f"| {so(100 * r['giam'], 0)}% | {L.HANG_THUA[r['hang_thua']]} | {so(100 * r['p'], 0)}% | {r['so_ma_lai']}/{len(ds)} | {tr(r['ngay_thuong'])} | {tr(r['trung_binh'])} | {tr(r['newsvendor'])} | {tr(r['von'])} |" for r in bang_nv]
        L_ += ["", f"Theo luật: **{'bền' if not thua else 'không bền, thua khi: ' + '; '.join(thua)}**.", "", "## 3. Trước và sau đối chiếu, mặc định (giảm 15%)", "", "Trước: hệ số mô phỏng, tài trợ 70%. Sau: hệ số thật dải 10–20%, tài trợ 45%. Cùng phiên giả lập theo giả định, chưa tách 2/3 và 1/3. Lãi kỳ vọng, triệu đ toàn kho.", "",
               "| Hàng thừa | Vốn trước | Lãi trước | Mã còn lãi trước | Vốn sau | Lãi sau | Mã còn lãi sau | Giá trị theo dõi theo giờ (sau) | Trần nếu biết trước (sau) |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for h, t_ in L.HANG_THUA.items():
            a, c = truoc[h], sau_dc[h]
            L_.append(f"| {t_} | {tr(a['phuong_an']['newsvendor']['q'])} | {tr(a['phuong_an']['newsvendor']['lai'])} | {a['so_ma_lai']}/{a['so_ma']} | {tr(c['phuong_an']['newsvendor']['q'])} | {tr(c['phuong_an']['newsvendor']['lai'])} | {c['so_ma_lai']}/{c['so_ma']} | {tr(c['phuong_an']['hai_buoc_2']['lai'] - c['phuong_an']['newsvendor']['lai'])} | {tr(c['lai_biet_truoc'])} |")
        L_ += ["", "Giá trị theo dõi = lãi hai bước theo quy tắc lần 2 (chọn lại Q) − lãi newsvendor, hàng về sau 6 giờ. Biên lãi mô phỏng thấp hơn số thật nên mức lãi ở đây thiên về bi quan.", ""]
        open("reports/tru_hang_live_sau_doi_chieu.md", "w", encoding="utf-8").write("\n".join(L_))
        print("\n".join(L_))
        raise SystemExit
    ket = dict(so_nganh=int(t.nganh.nunique()), so_ma=int(t.groupby(["nganh", "UPC"]).ngroups), so_dong=int(len(t)), deal=tom_tat_he_so(x.ti_so), deal_mo_phong=tom_tat_he_so(mau_mp))
    ket["deal_lech"] = abs(ket["deal"]["p50"] / ket["deal_mo_phong"]["p50"] - 1) > LECH_TRUNG_VI
    ket["deal_nganh"] = {n: tom_tat_he_so(g.ti_so) for n, g in x.groupby("nganh")}
    ket["phu"] = phu_theo_thoi_gian(x, tuan_nganh)
    ket["phu_dat"] = dat_phu(ket["phu"]["gop"])
    ket["phu_nganh_dat"] = sum(dat_phu(v) for v in ket["phu"]["theo_nganh"].values())
    tt = muc_tai_tro(b)
    ket["tai_tro"] = dict(gop=tt[0], so_tuan=tt[1], theo_nganh={n: muc_tai_tro(g)[0] for n, g in b.groupby("nganh") if muc_tai_tro(g)})
    ket["tai_tro_lech"] = not TAI_TRO_THAP <= tt[0] <= TAI_TRO_CAO
    ket["bien"] = bien_lai(b)
    ket["do_sau"] = theo_do_sau(x[x.giam.notna()])
    ket["sau_km"] = sau_khuyen_mai(b)
    json.dump(ket, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("xong chi so", flush=True)
    dau, sau = tach_thoi_gian(x, tuan_nganh)
    ds, nen = L.ma_va_muc_nen(bang, km, nghi)
    ket["newsvendor"] = thu_newsvendor(ds, nen, mau_mp, dau.ti_so.values, sau.ti_so.values)
    ket["ben"] = ben_trong(ket["newsvendor"])
    ket["thu_them"] = thu_tai_tro_co_gian(ds, nen, mau_mp, ket["do_sau"]["co_gian"], tt[0])
    json.dump(ket, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    tr = lambda v: so(v / 1e6)
    d, m = ket["deal"], ket["deal_mo_phong"]
    L_ = ["# Đối chiếu giả định với dữ liệu thật Dominick's", "", f"Luật ghi trước: docs/10 mục 10.9. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business. Chuỗi siêu thị Mỹ, 09/1989–05/1997, số bán theo tuần; {ket['so_nganh']} ngành, {so(ket['so_ma'], 0)} mã, {so(ket['so_dong'], 0)} dòng mã-tuần sau khi gộp toàn chuỗi. Không phải Việt Nam, không phải livestream.", "",
          "## 1. Hệ số deal", "", "| | Số tuần | Trung bình | p10 | p50 | p90 | Từ ×3 | Từ ×5 | Từ ×10 |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    L_ += [f"| {t_} | {so(r['n'], 0)} | {so(r['tb'], 2)} | {so(r['p10'], 2)} | {so(r['p50'], 2)} | {so(r['p90'], 2)} | {so(r['tu_3'])}% | {so(r['tu_5'])}% | {so(r['tu_10'])}% |" for t_, r in [("Dominick's (thật, theo tuần)", d), ("Mô phỏng (theo ngày)", m)]]
    L_ += ["", f"Theo luật (trung vị lệch quá {so(100 * LECH_TRUNG_VI, 0)}%): **{'giả định lệch' if ket['deal_lech'] else 'không lệch'}**. Luật chỉ so trung vị, nhưng lượng trữ phụ thuộc đuôi trên: " + (f"p90 thật ×{so(d['p90'], 2)} so với ×{so(m['p90'], 2)} của mô phỏng, tuần đạt từ ×5 là {so(d['tu_5'])}% so với {so(m['tu_5'])}%, nên **đuôi trên của mô phỏng quá mỏng**, dù số thật theo tuần vốn đã ít dao động hơn theo ngày." if d["p90"] > 1.25 * m["p90"] else "đuôi trên không lệch nhiều.") + " Vài ngành kéo đuôi lên rõ (bảng dưới).", "",
           "| Ngành | Số tuần | p10 | p50 | p90 | Từ ×3 |\n|---|---:|---:|---:|---:|---:|"]
    L_ += [f"| {n} | {so(r['n'], 0)} | {so(r['p10'], 2)} | {so(r['p50'], 2)} | {so(r['p90'], 2)} | {so(r['tu_3'])}% |" for n, r in sorted(ket["deal_nganh"].items(), key=lambda a: a[1]["p50"])]
    ph = ket["phu"]
    L_ += ["", "## 2. Phép đo có dùng được cho thời kỳ sau không", "", f"Đo trên 2/3 đầu ({so(ph['so_dau'], 0)} tuần), kiểm trên 1/3 sau ({so(ph['so_sau'], 0)} tuần): " + ", ".join(f"phân vị {int(100 * float(k))}% phủ {so(v)}%" for k, v in ph["gop"].items())
           + f". Theo luật: **{'đạt' if ket['phu_dat'] else 'không đạt'}**. Đo riêng từng ngành: {ket['phu_nganh_dat']}/{len(ph['theo_nganh'])} ngành đạt.", "",
           "## 3. Nhà sản xuất tài trợ bao nhiêu", "", f"Gộp {so(ket['tai_tro']['so_tuan'], 0)} tuần giảm ≥ {so(100 * GIAM_TOI_THIEU, 0)}%: nhà sản xuất gánh **{so(100 * ket['tai_tro']['gop'])}%** phần giảm. Giả định hiện tại {so(100 * TAI_TRO_GIA_DINH, 0)}%. Theo luật (khoảng {so(100 * TAI_TRO_THAP, 0)}–{so(100 * TAI_TRO_CAO, 0)}%): **{'giả định lệch' if ket['tai_tro_lech'] else 'không lệch'}**. Giá vốn là giá bình quân tồn kho nên chỉ là ước lượng.", "",
           "| Ngành | Tài trợ |\n|---|---:|"]
    L_ += [f"| {n} | {so(100 * v)}% |" for n, v in sorted(ket["tai_tro"]["theo_nganh"].items(), key=lambda a: a[1])]
    bi = ket["bien"]
    L_ += ["", "## 4. Biên lãi gộp", "", f"Tuần thường {so(100 * bi['thuong'])}%, tuần khuyến mãi {so(100 * bi['km'])}%. Theo mã (tuần thường): p10 {so(100 * bi['ma_p10'])}%, trung vị {so(100 * bi['ma_p50'])}%, p90 {so(100 * bi['ma_p90'])}%. Danh mục mô phỏng: 10–23%. {so(bi['ti_le_tuan_km'])}% số mã-tuần là khuyến mãi; trong đó {so(bi['co_trong_km'])}% có cờ, phần còn lại chỉ nhận ra nhờ giá.", "",
           "## 5. Giảm sâu hơn thì bán thêm bao nhiêu", "", "| Mức giảm | Số tuần | Trung vị hệ số deal |\n|---|---:|---:|"]
    L_ += [f"| {so(100 * r['tu'], 0)}–{so(100 * r['den'], 0)}% | {so(r['n'], 0)} | {so(r['p50'], 2)} |" for r in ket["do_sau"]["dai"]]
    L_ += ["", f"Độ co giãn theo giá: **{so(ket['do_sau']['co_gian'], 2)}** (giá giảm 1% thì số bán tăng khoảng ngần ấy %). Chỉ là tương quan: khuyến mãi thường đi kèm trưng bày, tờ rơi. Mô phỏng hiện chưa có quan hệ này.", "",
           "## 6. Mua trước rồi giảm", "", f"{so(ket['sau_km']['n'], 0)} tuần ngay sau khuyến mãi: trung vị ×{so(ket['sau_km']['p50'], 2)} so với mức nền. Theo luật (dưới {so(SAU_KM_NGUONG, 1)}): **{'có hiện tượng' if ket['sau_km']['p50'] < SAU_KM_NGUONG else 'không rõ hiện tượng'}**.", "",
           "## 7. Thử newsvendor bằng hệ số thật", "", "Giá, mức nền, chi phí của các mã trong đồ án giữ nguyên; bùng nổ vẫn là giả định. Chấm trên hệ số thật của 1/3 sau. Lãi kỳ vọng, triệu đ toàn kho.", ""]
    for h, t_ in L.HANG_THUA.items():
        L_ += [f"### Hàng thừa: {t_}", "", "| Bùng nổ thực tế | Q theo hệ số | Theo ngày thường | Theo trung bình | Newsvendor | Chênh so với phương án tốt hơn |\n|---|---|---:|---:|---:|---:|"]
        for p_, dd in ket["newsvendor"][h].items():
            for ten, nhan in [("mo_phong", "mô phỏng"), ("that", "thật, 2/3 đầu")]:
                r = dd[ten]
                L_.append(f"| p = {so(100 * float(p_), 0)}% | {nhan} | {tr(r['ngay_thuong']['lai'])} | {tr(r['trung_binh']['lai'])} | {tr(r['newsvendor']['lai'])} | {tr(r['newsvendor']['lai'] - max(r['ngay_thuong']['lai'], r['trung_binh']['lai']))} |")
        thua = ket["ben"][h]
        L_ += ["", f"Theo luật: **{'bền' if not thua else 'không bền: ' + '; '.join(thua)}**.", ""]
    L_ += ["## 8. Thử thêm: mức tài trợ thật và độ co giãn (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)", "",
           f"Bảng so sánh mức giảm ở `reports/tru_hang_live.md` giữ nguyên nhu cầu khi đổi mức giảm nên có thể gây hiểu sai. Ở đây số bán đổi theo độ co giãn {so(ket['do_sau']['co_gian'], 2)}, lấy mức giảm 15% làm gốc; độ co giãn này chỉ là tương quan, có thể thổi cao. Hàng thừa về kho thường, lãi newsvendor toàn kho, triệu đ.", "",
           "| Giảm | Nhãn hàng tài trợ | Số mã còn lãi | Lãi, nhu cầu không đổi | Lãi, có co giãn | Vốn trữ, có co giãn |\n|---|---:|---:|---:|---:|---:|"]
    L_ += [f"| {so(100 * r['giam'], 0)}% | {so(100 * r['tai_tro'])}% | {r['so_ma_lai']}/{len(ds)} | {tr(r['lai_khong'])} | {tr(r['lai_co'])} | {tr(r['von_co'])} |" for r in ket["thu_them"]]
    L_ += [""]
    json.dump(ket, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(REPORT, "w", encoding="utf-8").write("\n".join(L_))
    print("\n".join(L_))
