"""Tru hang cho phien livestream: newsvendor hai buoc. Luat ghi TRUOC khi chay: docs/10 muc 10.8. Chi doc CSDL, khong ghi CSDL.
Du lieu khong co phien live nao: moi tham so trong GiaDinh la GIA DINH, tru muc nen va he so deal (do tu du lieu).
Buoc 1, truoc phien: chon Q. Newsvendor: Q = phan vi Cu / (Cu + Co) cua nhu cau phien.
Buoc 2, trong phien: tu gio thu 3 uoc luong toc do tu so da ban (khong nhin truoc), thieu thi dat bo sung tu nguon nhanh.
Chay: python src/tru_hang_live.py   (tai thu muc goc) -> reports/tru_hang_live.md, reports/tru_hang_live_trang_thai.json
"""
import json
import os
import sys
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SO_PHIEN = 10_000
SO_PHIEN_DO_NHAY = 2_000
HAT_THIET_KE, HAT_CHAM = 20261103, 20261104
LUOI_PHAN_VI = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 0.995]
TU_GIO = 3                                      # gio dau tien duoc dat bo sung; cua so tinh toc do
NGUONG_DAT = 0.05                               # chi dat khi thieu >= 5% trung binh nhu cau phien
CUA_SO_NEN, TOI_THIEU_NEN = 28, 7
TOI_THIEU_MAU_DEAL = 30
NGUONG_PHU = 5.0                                # luat 10.8: lech phan vi deal khong qua 5 diem phan tram
MUC_PHU = [0.5, 0.75, 0.9]
HANG_THUA = {"ve_kho": "Về kho thường", "tra_ncc": "Trả nhà cung cấp", "xa_hang": "Phải xả"}
PHUONG_AN = {"ngay_thuong": "Theo ngày thường", "trung_binh": "Theo trung bình", "newsvendor": "Newsvendor",
             "hai_buoc_giu_q": "Hai bước lần 1, giữ Q", "hai_buoc": "Hai bước lần 1, chọn lại Q",
             "hai_buoc_2_giu_q": "Hai bước lần 2, giữ Q", "hai_buoc_2": "Hai bước lần 2, chọn lại Q"}
SO_NHOM = 20                                    # luat lan 2: moi gio chia mau thiet ke thanh 20 nhom theo toc do
PHU_PHI_THU = [0.0, 0.02, 0.05]
TAI_TRO_SAU_DOI_CHIEU = 0.45                    # docs/10 muc 10.10: lam tron tu 43,4% do tren Dominick's
TEP_HE_SO_THAT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "dominicks_he_so_deal.json")   # khong theo thu muc cua nguon du lieu
STATE = "reports/tru_hang_live_trang_thai.json"
REPORT = "reports/tru_hang_live.md"


@dataclass(frozen=True)
class GiaDinh:
    quy_mo: float = 1.0                         # phien ban bang may ngay ban thuong
    so_gio: int = 24
    p_xu_huong: float = 0.2
    no_thap: float = 3.0
    no_cao: float = 10.0
    giam_gia: float = 0.15
    tai_tro: float = 0.7                        # phan giam gia do nhan hang chiu
    phi_san: float = 0.08
    huy_don: float = 0.15
    gio_ve: int = 6
    phu_phi_nhanh: float = 0.05                 # theo gia von
    tran_nhanh: float = 3.0                     # toi da bao nhieu ngay ban thuong
    ngay_xa_kho: int = 30                       # hang thua ve kho thuong: so ngay ban het
    tra_ncc: float = 0.10                       # theo gia von
    xa_hang: float = 0.40                       # theo gia von
    co_gian: float = 0.0                        # so ban doi theo muc giam so voi giam_goc; 0 = khong doi (muc 10.8)
    giam_goc: float = 0.15

    def __post_init__(self):
        if self.so_gio < TU_GIO + 1:
            raise ValueError(f"phien phai dai hon {TU_GIO} gio")
        if not (self.quy_mo > 0 and 0 <= self.p_xu_huong <= 1 and 1 <= self.no_thap <= self.no_cao):
            raise ValueError("quy_mo > 0, p_xu_huong trong [0, 1], 1 <= no_thap <= no_cao")
        if not all(0 <= x < 1 for x in (self.giam_gia, self.phi_san, self.huy_don)) or not 0 <= self.tai_tro <= 1:
            raise ValueError("giam_gia, phi_san, huy_don trong [0, 1); tai_tro trong [0, 1]")
        if self.gio_ve < 1 or self.phu_phi_nhanh < 0 or self.tran_nhanh < 0:
            raise ValueError("gio_ve >= 1, phu_phi_nhanh va tran_nhanh khong am")
        if self.co_gian < 0 or not 0 <= self.giam_goc < 1:
            raise ValueError("co_gian khong am, giam_goc trong [0, 1)")


# ------------------------------------------------------------------ tien
def lai_don_vi(gia_ban, gia_von, gd):
    """Lai 1 don vi ban duoc trong phien (co the am)."""
    if gia_ban <= 0 or gia_von <= 0:
        raise ValueError("gia_ban, gia_von phai duong")
    sau_giam = gia_ban * (1 - gd.giam_gia)
    return float(sau_giam + gia_ban * gd.giam_gia * gd.tai_tro - gia_von - sau_giam * gd.phi_san)


def chi_phi_thua(gia_von, ti_le_luu, hang_thua, gd):
    """Thiet hai khi thua 1 don vi."""
    if hang_thua == "ve_kho":
        return float(gia_von * ti_le_luu * gd.ngay_xa_kho / 365)
    if hang_thua == "tra_ncc":
        return float(gia_von * gd.tra_ncc)
    if hang_thua == "xa_hang":
        return float(gia_von * gd.xa_hang)
    raise ValueError(f"hang_thua khong hop le: {hang_thua}")


def ti_le_toi_han(cu, co):
    """Cu / (Cu + Co). Ban lo (Cu <= 0): 0, khong tru. Thua khong mat gi (Co = 0): 1."""
    if cu <= 0:
        return 0.0
    return float(cu / (cu + max(co, 0.0)))


def q_newsvendor(mau, cu, co):
    """Phan vi toi han cua mau nhu cau. Ban lo thi khong tru."""
    tl = ti_le_toi_han(cu, co)
    return float(np.ceil(np.quantile(mau, tl))) if tl > 0 else 0.0


def he_so_gia(gd):
    """So ban doi bao nhieu lan vi muc giam khac muc goc: ((1 - giam) / (1 - goc)) ^ (-co gian). co_gian = 0: bang 1."""
    return float(((1 - gd.giam_gia) / (1 - gd.giam_goc)) ** (-gd.co_gian))


def doc_he_so_that(tep=TEP_HE_SO_THAT):
    """He so deal that theo dai giam gia (src/phan_tich_dominicks.py --buoc sau_doi_chieu tao). Chua co tep thi None."""
    if not os.path.exists(tep):
        return None
    return json.load(open(tep, encoding="utf-8"))


def dai_theo_giam(he_so, giam):
    """Dai giam gia chua muc giam. Duoi dai thap nhat dung dai thap nhat; tren dai cao nhat dung dai cao nhat."""
    ds = he_so["dai"]
    for d in ds:
        if d["tu"] <= giam < d["den"]:
            return d
    return ds[0] if giam < ds[0]["tu"] else ds[-1]


def mau_theo_giam(he_so, giam):
    return np.asarray(dai_theo_giam(he_so, giam)["phan_vi"], dtype=float)


# ------------------------------------------------------------------ nhu cau theo gio
def sinh_nhu_cau(nen, he_so_deal, gd, n, hat):
    """Mang (n, so_gio): so don moi gio (da tru huy). Dau phien ban deu; len xu huong thi tu gio T0 toc do tang de tong = nhu cau x he so no."""
    if nen <= 0:
        raise ValueError("muc nen phai duong")
    he_so_deal = np.asarray(he_so_deal, dtype=float)
    if not len(he_so_deal):
        raise ValueError("thieu he so deal")
    g = np.random.default_rng(hat)
    H = gd.so_gio
    mu = nen * gd.quy_mo * g.choice(he_so_deal, n) * (1 - gd.huy_don) * he_so_gia(gd)
    no = g.random(n) < gd.p_xu_huong
    B = np.exp(g.uniform(np.log(gd.no_thap), np.log(gd.no_cao), n))
    t0 = g.integers(2, max(3, int(H * 0.75) + 1), n)
    sau_no = no[:, None] & (np.arange(H) >= t0[:, None])
    toc = np.where(sau_no, ((mu * B - mu / H * t0) / (H - t0))[:, None], (mu / H)[:, None])
    return g.poisson(toc).astype(float)


def bang_muc_dat(D, gio_ve, ti_le, so_nhom=SO_NHOM):
    """Luat lan 2: moi gio, chia mau thiet ke theo toc do 3 gio gan nhat; moi nhom luu phan vi ti_le cua nhu cau SAU khi hang ve.
    Tra ve {so gio da qua: (bien nhom, muc dat theo nhom)}. Chi dung mau thiet ke."""
    H = D.shape[1]
    bang = {}
    for da_qua in range(TU_GIO, H - gio_ve):
        toc = D[:, da_qua - TU_GIO:da_qua].mean(axis=1)
        sau = D[:, da_qua + gio_ve:].sum(axis=1)
        bien = np.unique(np.quantile(toc, np.linspace(0, 1, so_nhom + 1)[1:-1]))
        nhom = np.searchsorted(bien, toc, side="right")
        muc, truoc = np.zeros(len(bien) + 1), 0.0
        for k in range(len(muc)):
            trong = sau[nhom == k]
            truoc = float(np.quantile(trong, ti_le)) if len(trong) else truoc     # nhom rong (nhieu toc do trung nhau): lay nhom lien truoc
            muc[k] = truoc
        bang[da_qua] = (bien, muc)
    return bang


def chay_phien(D, q1, bo_sung=False, gio_ve=6, tran=0.0, nguong=0.0, bang_dat=None):
    """Ban tung gio. q1: so hoac mang theo phien. Tra ve dict mang theo phien: ban, thua, thieu, q2, het (co luc het hang).
    Quyet dinh o cuoi gio h chi dung so DA BAN den gio h; so ban bi chan khi het hang nen giu toc do cao nhat da thay.
    bang_dat (bang_muc_dat): quy tac lan 2, can = muc dat theo nhom toc do; khong co thi quy tac lan 1, can = toc do x so gio con lai."""
    n, H = D.shape
    ton = np.full(n, float(q1)) if np.isscalar(q1) else np.asarray(q1, dtype=float).copy()
    den = np.zeros((n, H + gio_ve + 2))
    ban_gio = np.zeros((n, H))
    dat_gio = np.zeros((n, H))
    q2 = np.zeros(n)
    toc = np.zeros(n)
    het = np.zeros(n, dtype=bool)
    thieu = np.zeros(n)
    for h in range(H):
        ton += den[:, h]
        ban = np.minimum(D[:, h], ton)
        ton -= ban
        ban_gio[:, h] = ban
        cut = D[:, h] > ban
        het |= cut
        thieu += D[:, h] - ban
        if not bo_sung:
            continue
        da_qua = h + 1
        if da_qua < TU_GIO:
            continue
        chan = ton <= 0                                           # bo het hang: thay moi giam gia, khong tin so ban
        moi = ban_gio[:, da_qua - TU_GIO:da_qua].mean(axis=1)
        toc = np.where(chan, np.maximum(toc, moi), moi)
        ve_luc = da_qua + gio_ve                                  # hang dat cuoi gio h, co mat dau gio ve_luc
        if ve_luc >= H:
            continue
        con = ton.copy()                                          # di tung gio den luc hang ve: hang chua ve thi chua ban duoc
        for j in range(da_qua, ve_luc):
            con = np.maximum(con + den[:, j] - toc, 0)
        if bang_dat is None:
            muc_can = toc * (H - ve_luc)
        else:
            bien, muc = bang_dat[da_qua]
            muc_can = muc[np.searchsorted(bien, toc, side="right")]
        can = muc_can - (con + den[:, ve_luc:].sum(axis=1))
        dat = np.minimum(np.where(can >= max(nguong, 1e-9), np.ceil(can), 0), tran - q2)
        dat = np.maximum(dat, 0)
        den[:, ve_luc] += dat
        dat_gio[:, h] = dat
        q2 += dat
    return dict(ban=ban_gio.sum(axis=1), thua=ton, thieu=thieu, q2=q2, het=het, ban_gio=ban_gio, dat_gio=dat_gio)


def lai_phien(r, cu, co, phu_phi):
    """Lai tung phien = ban x lai don vi - thua x Co - bo sung x phu phi."""
    return r["ban"] * cu - r["thua"] * co - r["q2"] * phu_phi


def chi_tieu(r, D, q1, cu, co, phu_phi):
    lai = lai_phien(r, cu, co, phu_phi)
    tong = D.sum()
    return dict(q=float(q1), lai=float(lai.mean()), lai_p10=float(np.quantile(lai, 0.1)), p_het=float(100 * r["het"].mean()), thieu=float(r["thieu"].mean()),
                thua=float(r["thua"].mean()), fill=float(100 * r["ban"].sum() / tong) if tong else 100.0, q2=float(r["q2"].mean()), p_bo_sung=float(100 * (r["q2"] > 0).mean()))


def chon_q_hai_buoc(D, cu, co, phu_phi, gio_ve, tran, nguong, bang_dat=None):
    """Q dau tien cua phuong an hai buoc: chon tren luoi phan vi cua mau thiet ke."""
    tong = D.sum(axis=1)
    tot, q_tot = -np.inf, 0.0
    for pv in LUOI_PHAN_VI:
        q = float(np.ceil(np.quantile(tong, pv)))
        lai = lai_phien(chay_phien(D, q, True, gio_ve, tran, nguong, bang_dat), cu, co, phu_phi).mean()
        if lai > tot:
            tot, q_tot = lai, q
    return q_tot


def cac_phuong_an(nen, he_so_deal, gia_ban, gia_von, ti_le_luu, hang_thua, gd, n=SO_PHIEN, gd_thuc=None, hat_tk=HAT_THIET_KE, hat_cham=HAT_CHAM, hai_buoc=True, he_so_deal_thuc=None):
    """Q tinh tren mau thiet ke theo gd va he_so_deal; cham tren mau doc lap theo gd_thuc va he_so_deal_thuc (mac dinh = gd, he_so_deal). Tien luon theo gd.
    hai_buoc=False: chi 3 phuong an tru mot lan (bang sai gia dinh, muc giam gia khong can 2 buoc, chay nhanh hon)."""
    gd_thuc = gd_thuc or gd
    cu, co = lai_don_vi(gia_ban, gia_von, gd), chi_phi_thua(gia_von, ti_le_luu, hang_thua, gd)
    phu_phi = gia_von * gd.phu_phi_nhanh
    tk = sinh_nhu_cau(nen, he_so_deal, gd, n, hat_tk)
    tong = tk.sum(axis=1)
    tran = nen * gd.quy_mo * gd.tran_nhanh
    nguong = NGUONG_DAT * tong.mean()
    qs = dict(ngay_thuong=float(np.ceil(nen * gd.quy_mo)), trung_binh=float(np.ceil(tong.mean())), newsvendor=q_newsvendor(tong, cu, co))
    bang_dat, co_lan_2 = None, False
    if hai_buoc:
        qs["hai_buoc_giu_q"] = qs["newsvendor"]
        qs["hai_buoc"] = chon_q_hai_buoc(tk, cu, co, phu_phi, gd.gio_ve, tran, nguong) if cu > 0 else 0.0
        qs["hai_buoc_2_giu_q"] = qs["newsvendor"]
        lai_sau_phu_phi = cu - phu_phi
        co_lan_2 = lai_sau_phu_phi > 0                                                     # luat lan 2: lai sau phu phi <= 0 thi khong bo sung
        bang_dat = bang_muc_dat(tk, gd.gio_ve, ti_le_toi_han(lai_sau_phu_phi, co)) if co_lan_2 else None
        qs["hai_buoc_2"] = (chon_q_hai_buoc(tk, cu, co, phu_phi, gd.gio_ve, tran, nguong, bang_dat) if co_lan_2 else qs["newsvendor"])
    D = sinh_nhu_cau(nen, he_so_deal if he_so_deal_thuc is None else he_so_deal_thuc, gd_thuc, n, hat_cham)
    ra = {}
    for ten, q in qs.items():
        if ten.startswith("hai_buoc_2"):
            r = chay_phien(D, q, co_lan_2, gd.gio_ve, tran, nguong, bang_dat)
        else:
            r = chay_phien(D, q, ten.startswith("hai_buoc") and cu > 0, gd.gio_ve, tran, nguong)
        ra[ten] = chi_tieu(r, D, q, cu, co, phu_phi)
    return dict(cu=cu, co=co, ti_le=ti_le_toi_han(cu, co), tb_nhu_cau=float(D.sum(axis=1).mean()), lai_biet_truoc=float(max(cu, 0.0) * D.sum(axis=1).mean()), phuong_an=ra)


# ------------------------------------------------------------------ do tu du lieu
def nen_truot(nhu_cau, bo_ngay, cua_so=CUA_SO_NEN, toi_thieu=TOI_THIEU_NEN):
    """Muc nen moi ngay = trung vi cac ngay khong bi loai trong cua_so ngay TRUOC do (khong tinh chinh ngay do)."""
    return nhu_cau.where(~bo_ngay).shift(1).rolling(cua_so, min_periods=toi_thieu).median()


def nap_nhu_cau(doc=None):
    """Chuoi nhu cau + mat na khuyen mai, nghi, su kien theo tung ma; lich rong (nguon khong co khuyen mai) thi mat na rong.
    doc: ham doc SQL (dashboard truyen ham cua minh de doc dung CSDL cua nguon dang chon)."""
    if doc is None:
        from csdl import doc
    d = doc("SELECT ngay, ma_sku, nhu_cau FROM nhu_cau_that")
    d["ngay"] = pd.to_datetime(d.ngay)
    bang = d.pivot(index="ngay", columns="ma_sku", values="nhu_cau").sort_index().asfreq("D")
    km = pd.DataFrame(False, index=bang.index, columns=bang.columns)
    for r in doc("SELECT ma_sku, tu_ngay, den_ngay FROM lich_khuyen_mai").itertuples():
        if r.ma_sku in km.columns:
            km.loc[r.tu_ngay:r.den_ngay, r.ma_sku] = True
    nghi = bang.index.isin(pd.to_datetime(doc("SELECT ngay FROM lich_ngay_nghi").ngay))
    su_kien = pd.Series(False, index=bang.index)
    for r in doc("SELECT ngay, cua_so_truoc, cua_so_sau FROM lich_su_kien").itertuples():
        g = pd.Timestamp(r.ngay)
        su_kien.loc[g + pd.Timedelta(days=int(r.cua_so_truoc)):g + pd.Timedelta(days=int(r.cua_so_sau))] = True
    return bang, km, nghi, su_kien.values


def ti_so_deal(bang, km, nghi, su_kien, tu=None, den=None):
    """Bang ngay khuyen mai ngoai su kien: ma, ngay, nhu cau, muc nen, ti so. Nen khong tinh ngay khuyen mai, ngay nghi."""
    bo = km.values | nghi[:, None]
    nen = nen_truot(bang, pd.DataFrame(bo, index=bang.index, columns=bang.columns))
    chon = km.values & ~nghi[:, None] & ~su_kien[:, None] & (nen.values > 0) & bang.notna().values
    i, j = np.nonzero(chon)
    r = pd.DataFrame({"ma": bang.columns[j], "ngay": bang.index[i], "nhu_cau": bang.values[i, j], "nen": nen.values[i, j]})
    r = r[r.ngay >= pd.Timestamp(tu)] if tu is not None else r
    r = r[r.ngay <= pd.Timestamp(den)] if den is not None else r
    return r.assign(ti_so=r.nhu_cau / r.nen)


def do_phu(mau_deal, kiem, muc=MUC_PHU):
    """Ti le (%) ngay kiem tra co nhu cau <= nen x phan vi muc cua he so deal."""
    if not len(kiem):
        return {}
    return {str(m): float(100 * (kiem.nhu_cau <= kiem.nen * np.quantile(mau_deal, m)).mean()) for m in muc}


def muc_nen_gan_nhat(bang, km, nghi, ngay=None, cua_so=CUA_SO_NEN):
    """Muc nen tung ma tinh den ngay (khong tinh ngay do). Dung cho man hinh."""
    moc = pd.Timestamp(ngay) if ngay is not None else bang.index[-1] + pd.Timedelta(days=1)
    tr = (bang.index < moc) & (bang.index >= moc - pd.Timedelta(days=cua_so))
    return bang[tr].where(~(km.values[tr] | nghi[tr][:, None])).median()


def bang_thong_so_ma():
    from csdl import doc
    return doc("SELECT s.ma_sku, s.ten_sku, s.don_vi, s.gia_ban, s.gia_von, s.ty_le_chi_phi_luu_kho, p.xyz_train FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku) ORDER BY ma_sku")


def mau_deal_truoc(moc_cuoi=None, doc=None):
    """He so deal do truoc tap test. Tra ve (mau, bang kiem tren test, nhu cau, khuyen mai, nghi); nguon khong co khuyen mai thi mau rong."""
    from kiem_tra_du_lieu import moc_thoi_gian
    bang, km, nghi, su_kien = nap_nhu_cau(doc)
    moc = moc_thoi_gian(moc_cuoi if moc_cuoi is not None else bang.index[-1])
    return (ti_so_deal(bang, km, nghi, su_kien, den=moc["TRAIN_END"]).ti_so.values,
            ti_so_deal(bang, km, nghi, su_kien, tu=moc["TRAIN_END"] + pd.Timedelta(days=1)), bang, km, nghi)


# ------------------------------------------------------------------ ca kho
# ------------------------------------------------------------------ cho man hinh
def tai_tro_hoa_von(gia_ban, gia_von, gd):
    """Nhan hang phai tai tro bao nhieu phan muc giam de 1 don vi khong lo (0..1). Khong giam gia ma van lo, hoac tai tro het van lo: None."""
    if lai_don_vi(gia_ban, gia_von, replace(gd, tai_tro=0)) >= 0:
        return 0.0
    if gd.giam_gia <= 0:
        return None
    f = (gia_von + gia_ban * (1 - gd.giam_gia) * (gd.phi_san - 1)) / (gia_ban * gd.giam_gia)
    return float(f) if f <= 1 else None


def duong_lai(nen, he_so_deal, cu, co, gd, n=SO_PHIEN_DO_NHAY, so_diem=40, hat=HAT_CHAM, q_max=None):
    """Lai ky vong 1 phien theo Q (tru mot lan, khong bo sung), cham tren mau doc lap. Tra ve DataFrame q, lai.
    q_max: Q lon nhat can ve; mac dinh phan vi 99,5% (duoi day thi vung ra quyet dinh bi ep lai nen man hinh truyen vao)."""
    tong = sinh_nhu_cau(nen, he_so_deal, gd, n, hat).sum(axis=1)
    ds_q = np.linspace(0, float(np.quantile(tong, 0.995)) if q_max is None else float(q_max), so_diem)
    ban = np.minimum(tong[None, :], ds_q[:, None])
    return pd.DataFrame({"q": ds_q, "lai": (ban * cu - (ds_q[:, None] - ban) * co).mean(axis=1)})


def phat_lai(nen, he_so_deal, q1, gia_ban, gia_von, ti_le_luu, hang_thua, gd, xu_huong, hat, n=SO_PHIEN_DO_NHAY):
    """1 phien theo tung gio, dat bo sung theo quy tac lan 2. Tra ve DataFrame moi gio; quyet dinh gio h chi dung so lieu den gio h (chay_phien).
    hang_co = hang da co mat tinh den cuoi gio do; dat = luong dat cuoi gio do."""
    cu, co = lai_don_vi(gia_ban, gia_von, gd), chi_phi_thua(gia_von, ti_le_luu, hang_thua, gd)
    lai_sau_phu_phi = cu - gia_von * gd.phu_phi_nhanh
    tk = sinh_nhu_cau(nen, he_so_deal, gd, n, HAT_THIET_KE)
    bang_dat = bang_muc_dat(tk, gd.gio_ve, ti_le_toi_han(lai_sau_phu_phi, co)) if lai_sau_phu_phi > 0 else None
    D = sinh_nhu_cau(nen, he_so_deal, replace(gd, p_xu_huong=1.0 if xu_huong else 0.0), 1, hat)
    r = chay_phien(D, q1, bang_dat is not None, gd.gio_ve, nen * gd.quy_mo * gd.tran_nhanh, NGUONG_DAT * tk.sum(axis=1).mean(), bang_dat)
    dat = r["dat_gio"][0]
    ve = np.concatenate([np.zeros(gd.gio_ve + 1), dat])[:gd.so_gio]            # dat cuoi gio h, co mat dau gio h + gio_ve + 1
    return pd.DataFrame({"gio": np.arange(1, gd.so_gio + 1), "nhu_cau": D[0], "ban": r["ban_gio"][0], "dat": dat, "nhu_cau_cd": D[0].cumsum(),
                         "ban_cd": r["ban_gio"][0].cumsum(), "hang_co": q1 + ve.cumsum()})


def ma_va_muc_nen(bang, km, nghi):
    """Cac ma co muc nen > 0 va muc nen = trung vi ngay thuong (bo khuyen mai, ngay nghi) cua 365 ngay cuoi."""
    nam = bang.iloc[-365:].where(~(km.iloc[-365:].values | nghi[-365:][:, None])).median()
    ds = bang_thong_so_ma()
    return ds[ds.ma_sku.map(nam).fillna(0) > 0].reset_index(drop=True), nam


def tong_ca_kho(ds, nen, mau, hang_thua, gd, n, gd_thuc=None, hai_buoc=True, he_so_deal_thuc=None):
    """Cong lai moi ma, moi ma 1 phien. Tra ve lai, mat ban, thua, von theo phuong an. p_het chi tinh ma con lai
    (ma ban lo newsvendor khong tru nen het hang 100%, tinh vao thi lam sai y nghia ti le nay)."""
    tong = {}
    so, so_lai, biet_truoc = 0, 0, 0.0
    for r in ds.itertuples():
        kq = cac_phuong_an(nen[r.ma_sku], mau, r.gia_ban, r.gia_von, r.ty_le_chi_phi_luu_kho, hang_thua, gd, n, gd_thuc, hai_buoc=hai_buoc, he_so_deal_thuc=he_so_deal_thuc)
        so += 1
        so_lai += kq["cu"] > 0
        biet_truoc += kq["lai_biet_truoc"]
        for k, v in kq["phuong_an"].items():
            t = tong.setdefault(k, dict(lai=0.0, thieu=0.0, thua=0.0, q=0.0, q2=0.0, p_het=0.0))
            t["lai"] += v["lai"]
            t["thieu"] += v["thieu"] * r.gia_ban
            t["thua"] += v["thua"] * r.gia_von
            t["q"] += v["q"] * r.gia_von
            t["q2"] += v["q2"] * r.gia_von
            if kq["cu"] > 0:
                t["p_het"] += v["p_het"]
    for t in tong.values():
        t["p_het"] /= max(so_lai, 1)
    return dict(so_ma=so, so_ma_lai=so_lai, lai_biet_truoc=biet_truoc, phuong_an=tong)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    mau, kiem, bang, km, nghi = mau_deal_truoc()
    if len(mau) < TOI_THIEU_MAU_DEAL:
        raise SystemExit(f"Nguồn dữ liệu này chỉ có {len(mau)} ngày khuyến mãi đo được, không đủ để đo hệ số deal.")
    ds, nam = ma_va_muc_nen(bang, km, nghi)
    gd = GiaDinh()
    ket = dict(so_ma_ca_kho=int(len(bang.columns)), so_ma=int(len(ds)), mau_deal=dict(n=int(len(mau)), **{f"p{int(100 * q)}": float(np.quantile(mau, q)) for q in (0.1, 0.5, 0.9)}, tb=float(mau.mean())))
    ket["bien_mac_dinh"] = float(ds.apply(lambda r: lai_don_vi(r.gia_ban, r.gia_von, gd) / r.gia_ban, axis=1).median())
    ket["so_ma_ban_lo"] = int(ds.apply(lambda r: lai_don_vi(r.gia_ban, r.gia_von, gd) <= 0, axis=1).sum())
    ket["phu_deal"] = dict(so_ngay=int(len(kiem)), **do_phu(mau, kiem))
    ket["phu_dat"] = bool(ket["phu_deal"]) and all(abs(ket["phu_deal"][str(m)] - 100 * m) <= NGUONG_PHU for m in MUC_PHU)
    print("deal", ket["mau_deal"], "phu", ket["phu_deal"], flush=True)
    ket["chinh"] = {h: tong_ca_kho(ds, nam, mau, h, gd, SO_PHIEN) for h in HANG_THUA}
    print("xong bang chinh", flush=True)
    sai = {"p = 5%": dict(p_xu_huong=0.05), "p = 10%": dict(p_xu_huong=0.1), "p = 20% (như giả định)": {}, "p = 40%": dict(p_xu_huong=0.4),
           "bùng nổ [2; 5]": dict(no_thap=2.0, no_cao=5.0), "bùng nổ [5; 20]": dict(no_thap=5.0, no_cao=20.0)}
    ket["sai_gia_dinh"] = {h: {t: tong_ca_kho(ds, nam, mau, h, gd, SO_PHIEN_DO_NHAY, replace(gd, **d), hai_buoc=False)["phuong_an"] for t, d in sai.items()} for h in HANG_THUA}
    ket["ben"] = {h: {t: min(v["newsvendor"]["lai"] - v["ngay_thuong"]["lai"], v["newsvendor"]["lai"] - v["trung_binh"]["lai"]) for t, v in ket["sai_gia_dinh"][h].items()} for h in HANG_THUA}
    print("xong sai gia dinh", flush=True)
    ket["gio_ve"] = {str(t): {h: tong_ca_kho(ds, nam, mau, h, replace(gd, gio_ve=t), SO_PHIEN_DO_NHAY) for h in HANG_THUA} for t in (2, 6, 12, 24)}
    print("xong gio ve", flush=True)
    ket["phu_phi"] = {str(f): {h: tong_ca_kho(ds, nam, mau, h, replace(gd, phu_phi_nhanh=f), SO_PHIEN_DO_NHAY) for h in HANG_THUA} for f in PHU_PHI_THU}
    print("xong phu phi", flush=True)
    ket["giam_gia"] = {f"{int(100 * g)}% · tài trợ {int(100 * f)}%": tong_ca_kho(ds, nam, mau, "ve_kho", replace(gd, giam_gia=g, tai_tro=f), SO_PHIEN_DO_NHAY, hai_buoc=False)["phuong_an"]
                       for g, f in [(0.1, 0.7), (0.15, 0.7), (0.3, 0.7), (0.15, 0.0), (0.15, 1.0)]}
    json.dump(ket, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    so_ = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    tr = lambda v: so_(v / 1e6)
    dau = "| Phương án | Vốn trữ (tr đ) | Lãi kỳ vọng (tr đ) | Mất bán (tr đ) | Thừa (tr đ) | Bổ sung (tr đ) | Hết hàng (% phiên) |\n|---|---:|---:|---:|---:|---:|---:|\n"
    dong = lambda v: "\n".join(f"| {PHUONG_AN[k]} | {tr(t['q'])} | {tr(t['lai'])} | {tr(t['thieu'])} | {tr(t['thua'])} | {tr(t['q2'])} | {so_(t['p_het'])}% |" for k, t in v.items())
    L = ["# Trữ hàng cho phiên livestream", "", f"**Bản gốc, trước khi đối chiếu số thật. Bảng theo mức giảm ở cuối giữ nguyên nhu cầu nên có thể gây hiểu sai; xem đính chính ở docs/10 mục 10.9 và bản sau đối chiếu `reports/tru_hang_live_sau_doi_chieu.md`.** Luật ghi trước: docs/10 mục 10.8. **Không có dữ liệu livestream thật**: mọi tham số trừ mức nền và hệ số deal là giả định. Mỗi mã 1 phiên, {ket['so_ma']}/{ket['so_ma_ca_kho']} mã có mức nền > 0.", "",
         f"Giả định mặc định: phiên {gd.so_gio} giờ, p = {so_(100 * gd.p_xu_huong, 0)}%, bùng nổ [{so_(gd.no_thap, 0)}; {so_(gd.no_cao, 0)}] lần, giảm {so_(100 * gd.giam_gia, 0)}%, nhãn hàng tài trợ {so_(100 * gd.tai_tro, 0)}%, phí sàn {so_(100 * gd.phi_san, 0)}%, hủy {so_(100 * gd.huy_don, 0)}%. "
         f"Lãi 1 đơn vị (trung vị) {so_(100 * ket['bien_mac_dinh'])}% giá bán; {ket['so_ma_ban_lo']} mã bán lỗ theo giả định này.", "",
         "## Phần đo được: hệ số deal", "", f"Đo trước test: {so_(ket['mau_deal']['n'], 0)} ngày khuyến mãi ngoài sự kiện, trung vị ×{so_(ket['mau_deal']['p50'], 2)}, p10–p90 ×{so_(ket['mau_deal']['p10'], 2)}–×{so_(ket['mau_deal']['p90'], 2)}.", "",
         f"Kiểm tra trên {so_(ket['phu_deal'].get('so_ngay', 0), 0)} ngày khuyến mãi của test: " + ", ".join(f"phân vị {int(100 * m)}% phủ {so_(ket['phu_deal'][str(m)])}%" for m in MUC_PHU if str(m) in ket["phu_deal"])
         + f". Theo luật (lệch ≤ {so_(NGUONG_PHU, 0)} điểm): **{'đạt' if ket['phu_dat'] else 'không đạt'}**. Phép kiểm này không nói gì về bùng nổ, và dữ liệu là mô phỏng nên cùng một quy luật sinh ra cả hai giai đoạn.", "",
         "## So sánh trên chính phân phối giả định (không phải bằng chứng)", "", "Newsvendor tối ưu theo phân phối này nên thắng là tất yếu; bảng chỉ cho thấy độ lớn. Tổng toàn kho, mỗi mã 1 phiên.", ""]
    for h, t in HANG_THUA.items():
        c = ket["chinh"][h]
        L += [f"### Hàng thừa: {t}", "", dau + dong(c["phuong_an"]), "", f"Trần tham chiếu, nếu biết trước nhu cầu từng phiên: **{tr(c['lai_biet_truoc'])} triệu đ**. Tỉ lệ hết hàng tính trên {c['so_ma_lai']} mã còn lãi; mã bán lỗ thì newsvendor không trữ.", ""]
    L += ["## Bằng chứng 1: thực tế khác giả định", "", "Q tính với p = 20%, bùng nổ [3; 10]. Bảng ghi lãi kỳ vọng (triệu đ) khi thực tế khác đi. **Chênh** = newsvendor − phương án tốt hơn trong 2 phương án so sánh.", ""]
    for h, t in HANG_THUA.items():
        L += [f"### Hàng thừa: {t}", "", "| Thực tế | Theo ngày thường | Theo trung bình | Newsvendor | Chênh |\n|---|---:|---:|---:|---:|"]
        L += [f"| {k} | {tr(v['ngay_thuong']['lai'])} | {tr(v['trung_binh']['lai'])} | {tr(v['newsvendor']['lai'])} | {tr(ket['ben'][h][k])} |" for k, v in ket["sai_gia_dinh"][h].items()]
        thua = [k for k, v in ket["ben"][h].items() if v < 0]
        L += ["", f"Theo luật: **{'bền' if not thua else 'không bền, thua khi ' + '; '.join(thua)}**.", ""]
    gt = lambda d, k: tr(d[k]["lai"] - d["newsvendor"]["lai"])
    dau_gt = "| " + " | ".join(f"{t}: lần 1 | {t}: lần 2" for t in HANG_THUA.values()) + " |\n|---|" + "---:|" * (2 * len(HANG_THUA))
    L += ["## Giá trị theo dõi theo giờ", "", "= lãi hai bước (chọn lại Q) − lãi newsvendor, tổng toàn kho, triệu đ. Là mức chi tối đa cho việc theo dõi, chưa trừ chi phí cài đặt. Lần 1 là quy tắc ghi trước; lần 2 sửa sau khi đã thấy lần 1 (docs/10 mục 10.8).", "", "| Hàng về sau " + dau_gt]
    L += [f"| {t} giờ | " + " | ".join(f"{gt(v[h]['phuong_an'], 'hai_buoc')} | {gt(v[h]['phuong_an'], 'hai_buoc_2')}" for h in HANG_THUA) + " |" for t, v in ket["gio_ve"].items()]
    L += ["", "### Theo phụ phí nguồn nhanh (hàng về sau 6 giờ)", "", "| Phụ phí " + dau_gt]
    L += [f"| {so_(100 * float(f), 0)}% giá vốn | " + " | ".join(f"{gt(v[h]['phuong_an'], 'hai_buoc')} | {gt(v[h]['phuong_an'], 'hai_buoc_2')}" for h in HANG_THUA) + " |" for f, v in ket["phu_phi"].items()]
    L += ["", "## Mức giảm giá và tài trợ (hàng thừa về kho thường)", "", "| Giảm · tài trợ | Vốn trữ newsvendor (tr đ) | Lãi newsvendor (tr đ) | Lãi theo ngày thường (tr đ) |\n|---|---:|---:|---:|"]
    L += [f"| {k} | {tr(v['newsvendor']['q'])} | {tr(v['newsvendor']['lai'])} | {tr(v['ngay_thuong']['lai'])} |" for k, v in ket["giam_gia"].items()]
    L += [""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
