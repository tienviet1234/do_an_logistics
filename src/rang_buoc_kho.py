"""Han su dung va suc chua kho. Luat ghi TRUOC khi chay: docs/10 muc 10.11. Chi doc CSDL, khong ghi CSDL, khong doi chinh sach chinh.
Du lieu khong co han su dung, the tich, dien tich kho: cac bang duoi day la GIA DINH theo loai hang.
Tat het rang buoc thi mo_phong_kho phai trung gom_don.mo_phong (co test, doi chieu ca CSDL).
Chay: python src/rang_buoc_kho.py   (tai thu muc goc) -> reports/rang_buoc_kho.md, reports/rang_buoc_kho_trang_thai.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gom_don import R_COVER, TI_LE_CHINH, so_luong, tong_ket  # noqa: E402

# han su dung (ngay), gia dinh. Tu khoa uu tien hon nhom; None = khong xet
HAN_TU_KHOA = [("rượu vang", None), ("sữa chua", 30), ("bánh trung thu", 60), ("đá lạnh", 90), ("sữa tươi", 180), ("sữa học đường", 180), ("sữa hạt", 180), ("sữa đặc", 365), ("sữa bột", 540),
               ("mứt", 180), ("snack", 180), ("hạt dưa", 180), ("xúc xích", 180), ("mì ", 180), ("hạt điều", 270), ("bánh gạo", 270), ("cháo", 270), ("bia ", 270), ("trà xanh", 270), ("nước cam", 270),
               ("pepsi", 270), ("cá viên", 270), ("cá hộp", 1095), ("thịt hộp", 1095), ("đường", 730), ("cà phê", 730), ("muối", 730), ("dầu ăn", 540), ("trà ", 540)]
HAN_NHOM = {"Sữa": 180, "Bánh kẹo": 365, "Thực phẩm khô": 365, "Đồ uống": 365, "Gia vị": 540, "Kem & đông lạnh": 365}
# the tich 1 don vi (lit), gia dinh
THE_TICH_TU_KHOA = [("cây thông", 120.0), ("máy sưởi", 90.0), ("quạt cây", 70.0), ("chăn", 40.0), ("gấu bông", 30.0), ("giấy vệ sinh", 25.0), ("cặp sách", 20.0), ("tã quần", 20.0), ("đèn lồng", 10.0), ("bạt", 10.0),
                    ("pepsi", 12.0), ("gạo", 6.0), ("nước khoáng", 6.0), ("bột giặt", 4.0), ("nước xả", 4.0), ("nước rửa chén", 4.0), ("mì ly", 30.0), ("sạc dự phòng", 0.3), ("bóng đèn", 0.5),
                    ("bật lửa", 0.05), ("son", 0.05), ("bút bi", 1.0), ("bao lì xì", 0.1), ("thiệp", 0.05)]
THE_TICH_DON_VI = {"thùng": 25.0, "lốc": 6.0, "túi": 4.0, "can": 6.0, "chai": 1.5, "hộp": 2.0, "gói": 1.0, "lon": 0.6, "tuýp": 0.2, "cái": 5.0, "bộ": 4.0, "đôi": 3.0, "cuộn": 2.0, "xấp": 0.5, "cuốn": 1.0, "ream": 3.0,
                   "vỉ": 0.1, "tấm": 0.05, "thỏi": 0.05, "cành": 15.0, "con": 20.0}
THE_TICH_MAC_DINH = 2.0
VUNG_LANH_NHOM, VUNG_LANH_TU_KHOA = "Kem & đông lạnh", "sữa chua"
VUNG = ["Kho thường", "Kho lạnh"]
TI_LE_DUNG = 1 / 3                              # quy tac 1/3
GIA_THUE = 10.0                                 # d/lit/ngay, khoang 300.000 d/m3/thang
MUC_SUC_CHUA = [1.0, 0.9, 0.8]
GIAM_CP, GIAM_FILL = 0.005, 0.2                 # luat 10.11
STATE = "reports/rang_buoc_kho_trang_thai.json"
REPORT = "reports/rang_buoc_kho.md"


# ------------------------------------------------------------------ gia dinh theo ma
def han_cua_ma(ten, nhom):
    t = ten.lower()
    for k, v in HAN_TU_KHOA:
        if k in t:
            if nhom in HAN_NHOM:                                    # tu khoa chi ap cho nhom thuc pham ("trà" trong hop qua bieu khong tinh)
                return v
            break
    return HAN_NHOM.get(nhom)


def the_tich_cua_ma(ten, don_vi):
    t = ten.lower()
    for k, v in THE_TICH_TU_KHOA:
        if k in t:
            return v
    return THE_TICH_DON_VI.get(don_vi, THE_TICH_MAC_DINH)


def vung_cua_ma(ten, nhom):
    return 1 if nhom == VUNG_LANH_NHOM or VUNG_LANH_TU_KHOA in ten.lower() else 0


def so_ngay_duoc_giao(han, he_so=1.0):
    """So ngay kho duoc giao tu luc hang ve (quy tac 1/3); it nhat 1. Khong xet han: None."""
    return None if han is None else max(1, int(round(han * he_so * TI_LE_DUNG)))


# ------------------------------------------------------------------ lo hang (FIFO)
def bo_het_han(lo, t):
    """lo: danh sach [ngay het duoc giao, so luong], lo ve truoc dung truoc. Bo cac lo den han (ngay het <= t), tra ve so luong bo."""
    bo = sum(q for h, q in lo if h <= t)
    lo[:] = [x for x in lo if x[0] > t]
    return bo


def ban_fifo(lo, sl):
    """Xuat sl tu lo ve som nhat. Goi sau khi da kiem tra du hang."""
    con = sl
    while con > 1e-12 and lo:
        lay = min(lo[0][1], con)
        lo[0][1] -= lay
        con -= lay
        if lo[0][1] <= 1e-12:
            lo.pop(0)


def uoc_luong_luc_ve(ip, d, L, the_tich):
    """The tich du kien luc hang ve = (hang hien co + dang ve - nhu cau trong thoi gian cho) x the tich."""
    return np.maximum(ip - d * L, 0) * the_tich


def cat_theo_cho(don, the_tich, cho_trong, moq):
    """Giam don cho vua cho trong; duoi MOQ thi khong dat."""
    du = cho_trong / the_tich if the_tich > 0 else don
    if don <= du:
        return don
    q = float(np.floor(max(du, 0.0)))
    return q if q >= moq and q > 0 else 0.0


# ------------------------------------------------------------------ mo phong
def trang_thai_mua(ds_mua, t, L, da_dat):
    """Hom nay voi 1 ma co ke hoach mua: (co duoc dat theo quy tac thuong, luong can dat theo mua hoac None).
    ds_mua: [{t_dat, t_dau, t_cuoi, q, bo_sung}]. Ngay nghi khong goi ham nay nen don den ngay mo cua dau tien tu t_dat. da_dat: chi so cac mua da dat, duoc cap nhat."""
    for k, m in enumerate(ds_mua):
        if m["t_dat"] <= t <= m["t_cuoi"]:
            q = None
            if k not in da_dat:
                da_dat.add(k)
                q = m["q"]
            return (bool(m.get("bo_sung")) and t >= m["t_dau"] and t + L <= m["t_cuoi"]), q
    return True, None


def mo_phong_kho(inp, F, sig, z, buoc, ngay_giao=None, tran_han=False, the_tich=None, vung=None, suc_chua=None, horizon=28, ke_hoach=None):
    """Mo phong ca kho theo tung ngay. ngay_giao: so ngay duoc giao tung ma (None = khong xet han). tran_han: tran luong dat theo han.
    suc_chua: [kho thuong, kho lanh] lit, co thi cat don (phuong an B). ke_hoach: {chi so ma: cac mua} newsvendor mua vu (newsvendor_mua_vu.py).
    Khong rang buoc nao: trung gom_don.mo_phong."""
    sku, D, closed, LT = inp["sku"], inp["dem"], inp["closed"], inp["LT"]
    S_ma, n = len(sku), D.shape[1]
    if ngay_giao is not None and len(ngay_giao) != S_ma:
        raise ValueError("ngay_giao khong dung so ma")
    if suc_chua is not None and (the_tich is None or vung is None):
        raise ValueError("cat don can the_tich va vung")
    ncc = sku.ma_ncc.values
    S, H, moq = sku.chi_phi_dat_hang.values.astype(float), (sku.ty_le_chi_phi_luu_kho * sku.gia_von).values.astype(float), sku.moq.values.astype(float)
    L = np.maximum(1, np.round(sku.lead_time_tb.values).astype(int))
    lt_std = sku.lead_time_std.values.astype(float)
    quy_tac = np.where(sku.xyz_train.values == "Z", "dat_den_muc", "eoq")
    onhand = np.array(inp["init"], dtype=float)
    pipe = [list(p) for p in inp["pipe0"]]
    co_han = [ngay_giao is not None and ngay_giao[i] is not None for i in range(S_ma)]
    lo = [[[max(1, ngay_giao[i] // 2), onhand[i]]] if co_han[i] and onhand[i] > 0 else [] for i in range(S_ma)]   # ton dau ky: da dung nua khoang
    ra = {c: np.zeros((S_ma, n)) for c in ["nhap", "xuat", "ton", "dat", "huy"]}
    nhom = {c: np.flatnonzero(ncc == c) for c in np.unique(ncc)}
    so_lan_cat = 0
    da_dat_mua = {i: set() for i in (ke_hoach or {})}
    for t in range(n):
        if closed[t]:
            ra["ton"][:, t] = onhand
            continue
        state = {}
        for i in range(S_ma):
            if co_han[i]:
                bo = bo_het_han(lo[i], t)
                onhand[i] -= bo
                ra["huy"][i, t] = bo
            rec = sum(q for a, q in pipe[i] if a <= t)
            pipe[i] = [(a, q) for a, q in pipe[i] if a > t]
            onhand[i] += rec
            ra["nhap"][i, t] = rec
            if co_han[i] and rec > 0:
                lo[i].append([t + ngay_giao[i], rec])
            sold = min(D[i, t], onhand[i])
            onhand[i] -= sold
            ra["xuat"][i, t] = sold
            if co_han[i]:
                ban_fifo(lo[i], sold)
            km = min((t + 1) // buoc, F.shape[1] - 1)
            f, st = F[i, km], t + 1 - buoc * km
            fw = lambda m, c=f, b=st: (c[b:b + m] if b < horizon else c[-1:]).mean() * m
            ltd = fw(L[i])
            ss = z * np.sqrt(sig[i] ** 2 + (ltd / L[i]) ** 2 * lt_std[i] ** 2)
            dbar = f.mean()
            state[i] = dict(rop=ltd + ss, ss=ss, ip=onhand[i] + sum(q for _, q in pipe[i]), eoq=np.sqrt(2 * dbar * 365 * S[i] / H[i]) if dbar > 0 else 0.0,
                            fw_lr=fw(L[i] + R_COVER), d=ltd / L[i], dbar=dbar)
        if suc_chua is None:
            thu_tu = [i for ma_nhom in nhom.values() for i in ma_nhom if state[i]["ip"] <= state[i]["rop"]]
        else:
            can = [i for i in range(S_ma) if state[i]["ip"] <= state[i]["rop"]]
            thu_tu = sorted(can, key=lambda i: state[i]["ip"] / state[i]["d"] if state[i]["d"] > 0 else np.inf)     # it ngay ton nhat dat truoc
            du_kien = [0.0, 0.0]
            for i in range(S_ma):
                du_kien[vung[i]] += float(uoc_luong_luc_ve(state[i]["ip"], state[i]["d"], L[i], the_tich[i]))
        if ke_hoach:
            dat_mua, chan = {}, set()
            for i, ds_mua in ke_hoach.items():
                duoc_dat, q_m = trang_thai_mua(ds_mua, t, int(L[i]), da_dat_mua[i])
                if not duoc_dat:
                    chan.add(i)
                if q_m is not None:
                    dat_mua[i] = q_m
            thu_tu = [i for i in thu_tu if i not in chan and i not in dat_mua]
            for i, q_m in dat_mua.items():
                can = q_m - state[i]["ip"]
                if can > 0:                                       # da du hang hien co + dang ve thi khong dat
                    order = float(max(moq[i], np.ceil(can)))
                    pipe[i].append((t + LT[i, t], order))
                    ra["dat"][i, t] = order
        for i in thu_tu:
            x = state[i]
            order = so_luong(quy_tac[i], x["ip"], x["rop"], x["eoq"], moq[i], x["fw_lr"], x["ss"])
            if tran_han and co_han[i]:
                order = min(order, float(np.ceil(max(moq[i], x["dbar"] * ngay_giao[i]))))
            if suc_chua is not None:
                moi = cat_theo_cho(order, the_tich[i], suc_chua[vung[i]] - du_kien[vung[i]], moq[i])
                so_lan_cat += moi < order
                order = moi
                du_kien[vung[i]] += order * the_tich[i]
            if order <= 0:
                continue
            pipe[i].append((t + LT[i, t], order))
            ra["dat"][i, t] = order
        ra["ton"][:, t] = onhand
    ra["so_lan_cat"] = so_lan_cat
    return ra


# ------------------------------------------------------------------ chi tieu
def the_tich_vung(ton, the_tich, vung):
    """Mang (2, ngay): lit dang chua theo vung."""
    tt = ton * np.asarray(the_tich)[:, None]
    v = np.asarray(vung)
    return np.vstack([tt[v == k].sum(axis=0) for k in (0, 1)])


def vuot_suc_chua(tt_vung, suc_chua):
    """Lit-ngay vuot, so ngay co vuot, ti le dinh / suc chua theo vung."""
    cap = np.asarray(suc_chua, dtype=float)[:, None]
    vuot = np.maximum(tt_vung - cap, 0)
    return dict(lit_ngay=float(vuot.sum()), so_ngay=int((vuot.sum(axis=0) > 0).sum()), theo_vung=[float(v) for v in vuot.sum(axis=1)], dinh_pt=[float(100 * d / c) if c > 0 else 0.0 for d, c in zip(tt_vung.max(axis=1), cap[:, 0])])


def chi_tieu_han(inp, ra, chon=None, ti_le_mat=1.0):
    """tong_ket + hang loai; chon: chi so cac ma can tinh (mac dinh toan kho). cp_tong = dat hang (da gom) + luu kho + loi nhuan mat + hang loai."""
    if chon is None:
        chon = np.arange(len(inp["sku"]))
    sub = dict(sku=inp["sku"].iloc[chon], dem=inp["dem"][chon], closed=inp["closed"])
    ra_sub = {c: ra[c][chon] for c in ("nhap", "xuat", "ton", "dat")}
    t = tong_ket(sub, ra_sub, TI_LE_CHINH)
    huy_sl = ra["huy"][chon].sum(axis=1)
    gia_tri = float((huy_sl * sub["sku"].gia_von.values).sum())
    return dict(t, huy_sl=float(huy_sl.sum()), huy_gia_tri=gia_tri, huy_pt_nhap=float(100 * huy_sl.sum() / max(ra["nhap"][chon].sum(), 1.0)), cp_tong=t["cp_gom"] + gia_tri * ti_le_mat)


def giu_phuong_an(moi, goc, khoa="cp_tong"):
    """Luat 10.11: chi phi giam it nhat 0,5% va Fill Rate khong giam qua 0,2 diem."""
    return moi[khoa] <= goc[khoa] * (1 - GIAM_CP) and goc["fill_rate"] - moi["fill_rate"] <= GIAM_FILL


def chi_tieu_chua(inp, ra, the_tich, vung, suc_chua, gia_thue=GIA_THUE):
    """tong_ket + tien thue ngoai phan vuot. cp_chua = dat hang (da gom) + luu kho + loi nhuan mat + thue ngoai."""
    t = tong_ket(inp, {c: ra[c] for c in ("nhap", "xuat", "ton", "dat")}, TI_LE_CHINH)
    v = vuot_suc_chua(the_tich_vung(ra["ton"], the_tich, vung), suc_chua)
    return dict(t, **v, thue=v["lit_ngay"] * gia_thue, cp_chua=t["cp_gom"] + v["lit_ngay"] * gia_thue, so_lan_cat=int(ra.get("so_lan_cat", 0)))


def ton_vuot_nhu_cau(ton, D, the_tich, so_ngay=60):
    """Lit-ngay moi ma cua phan ton vuot nhu cau that so_ngay ke tiep, va tong lit-ngay. Bo so_ngay cuoi: cua so bi cat o cuoi du lieu se thoi cao."""
    n = D.shape[1] - so_ngay
    if n <= 0:
        raise ValueError("du lieu ngan hon cua so")
    cong = np.concatenate([np.zeros((D.shape[0], 1)), D.cumsum(axis=1)], axis=1)
    sau = cong[:, 1 + so_ngay:1 + so_ngay + n] - cong[:, 1:1 + n]
    tt = np.asarray(the_tich)[:, None]
    return (np.maximum(ton[:, :n] - sau, 0) * tt).sum(axis=1), (ton[:, :n] * tt).sum(axis=1)


def chan_doan(inp, ra, ra_han, the_tich, vung, suc_chua, so_top=3):
    """Them SAU khi thay ket qua: vi sao the tich vuot va hang loai den tu dau. Tinh tu du lieu, khong ghi cung ma nao."""
    sku = inp["sku"]
    ht = np.nan_to_num(inp["obs"]["ton_cuoi_ngay"])
    tt = np.asarray(the_tich, dtype=float)
    chenh = (ra["ton"] - ht).mean(axis=1) * tt
    top = np.argsort(-chenh)[:so_top]
    bo_top = tt.copy()
    bo_top[top[0]] = 0.0
    vuot, tong = ton_vuot_nhu_cau(ra["ton"], inp["dem"], tt)
    z = sku.xyz_train.values == "Z"
    dip = sku.loai_mua_vu.str.startswith("Chỉ dịp").values
    gia_tri = ra_han["huy"].sum(axis=1) * sku.gia_von.values
    return dict(top=[dict(ma=sku.ma_sku.iloc[i], ten=sku.ten_sku.iloc[i], lit_tb=float(ra["ton"][i].mean() * tt[i]), lit_tb_ht=float(ht[i].mean() * tt[i]), nhap=float(ra["nhap"][i].sum()), nhu_cau=float(inp["dem"][i].sum()),
                         ton_cuoi=float(ra["ton"][i, -1]), nhap_ht=float(inp["obs"]["qty_in"][i].sum())) for i in top],
                bo_ma_lon_nhat=vuot_suc_chua(the_tich_vung(ra["ton"], bo_top, vung), suc_chua), vuot_pt=float(100 * vuot.sum() / max(tong.sum(), 1.0)), vuot_z_pt=float(100 * vuot[z].sum() / max(vuot.sum(), 1.0)),
                loai_dip_le_pt=float(100 * gia_tri[dip].sum() / max(gia_tri.sum(), 1.0)), so_ma_loai=int((gia_tri > 0).sum()), so_ma_dip_le=int(dip.sum()))


def gia_dinh_ma(sku):
    return (np.array([han_cua_ma(r.ten_sku, r.nhom_hang) for r in sku.itertuples()], dtype=object), np.array([the_tich_cua_ma(r.ten_sku, r.don_vi) for r in sku.itertuples()]),
            np.array([vung_cua_ma(r.ten_sku, r.nhom_hang) for r in sku.itertuples()]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from gom_don import chuan_bi
    inp_v, F_v, sig_v, z_v, b_v = chuan_bi("validation2")
    inp_t, F_t, sig_t, z_t, b_t = chuan_bi("test")
    sku = inp_v["sku"]
    han, the_tich, vung = gia_dinh_ma(sku)
    chon = np.array([i for i, h in enumerate(han) if h is not None])
    ket = dict(so_ma=int(len(sku)), so_ma_han=int(len(chon)), so_ma_lanh=int((vung == 1).sum()))

    def chay_han(tap, he_so, tran):
        inp, F, sig, z, b = (inp_v, F_v, sig_v, z_v, b_v) if tap == "validation2" else (inp_t, F_t, sig_t, z_t, b_t)
        ng = [so_ngay_duoc_giao(h, he_so) for h in han]
        ra = mo_phong_kho(inp, F, sig, z, b, ng, tran)
        return ra, chi_tieu_han(inp, ra, chon)

    v_goc = chay_han("validation2", 1.0, False)[1]
    v_tran = chay_han("validation2", 1.0, True)[1]
    ket["han"] = dict(validation2=dict(khong_tran=v_goc, co_tran=v_tran), dung_tran=bool(giu_phuong_an(v_tran, v_goc)))
    print("han validation2 xong", ket["han"]["dung_tran"], round(v_goc["huy_gia_tri"] / 1e6, 1), round(v_tran["huy_gia_tri"] / 1e6, 1), flush=True)
    ra_t, t_goc = chay_han("test", 1.0, False)
    ra_tt, t_tran = chay_han("test", 1.0, True)
    ket["han"]["test"] = dict(khong_tran=t_goc, co_tran=t_tran, khong_tran_mat_50=chi_tieu_han(inp_t, ra_t, chon, 0.5), co_tran_mat_50=chi_tieu_han(inp_t, ra_tt, chon, 0.5))
    khong_han = chi_tieu_han(inp_t, dict(mo_phong_kho(inp_t, F_t, sig_t, z_t, b_t)), chon)
    ket["han"]["test"]["khong_xet_han"] = khong_han
    ket["han"]["do_nhay"] = {str(h): dict(khong_tran=chay_han("test", h, False)[1], co_tran=chay_han("test", h, True)[1]) for h in (0.5, 2.0)}
    print("han test xong", flush=True)
    gv = sku.gia_von.values
    theo_ma = pd.DataFrame({"ma": sku.ma_sku, "ten": sku.ten_sku, "han": han, "ngay_giao": [so_ngay_duoc_giao(h) for h in han], "moq": sku.moq, "nhu_cau_ngay": inp_t["dem"].mean(axis=1),
                            "huy": ra_t["huy"].sum(axis=1), "huy_tran": ra_tt["huy"].sum(axis=1), "gia_tri": ra_t["huy"].sum(axis=1) * gv, "gia_tri_tran": ra_tt["huy"].sum(axis=1) * gv})
    theo_ma = theo_ma[theo_ma.han.notna()]
    moq_lon = theo_ma[theo_ma.moq > theo_ma.nhu_cau_ngay * theo_ma.ngay_giao]
    ket["han"]["moq_lon"] = moq_lon.ma.tolist()
    top = theo_ma.sort_values("gia_tri", ascending=False).head(10)
    ket["han"]["top"] = top.to_dict("records")
    ket["han"]["ty_trong_top"] = float(100 * top.gia_tri.sum() / max(theo_ma.gia_tri.sum(), 1.0))

    # suc chua: moc = dinh hang thuc ton trong du lieu tren validation2
    dinh = the_tich_vung(np.nan_to_num(inp_v["obs"]["ton_cuoi_ngay"]), the_tich, vung).max(axis=1)
    ket["chua"] = dict(dinh_lit=[float(x) for x in dinh], hien_trang_test=vuot_suc_chua(the_tich_vung(np.nan_to_num(inp_t["obs"]["ton_cuoi_ngay"]), the_tich, vung), dinh), muc={})
    ra_a_v, ra_a_t = mo_phong_kho(inp_v, F_v, sig_v, z_v, b_v), mo_phong_kho(inp_t, F_t, sig_t, z_t, b_t)
    for m in MUC_SUC_CHUA:
        cap = dinh * m
        a_v = chi_tieu_chua(inp_v, ra_a_v, the_tich, vung, cap)
        b_v_ = chi_tieu_chua(inp_v, mo_phong_kho(inp_v, F_v, sig_v, z_v, b_v, the_tich=the_tich, vung=vung, suc_chua=cap), the_tich, vung, cap)
        a_t = chi_tieu_chua(inp_t, ra_a_t, the_tich, vung, cap)
        b_t_ = chi_tieu_chua(inp_t, mo_phong_kho(inp_t, F_t, sig_t, z_t, b_t, the_tich=the_tich, vung=vung, suc_chua=cap), the_tich, vung, cap)
        ket["chua"]["muc"][str(m)] = dict(validation2=dict(A=a_v, B=b_v_), test=dict(A=a_t, B=b_t_), dung_B=bool(giu_phuong_an(b_v_, a_v, "cp_chua")),
                                          thue_do_nhay={str(g): dict(A=float(a_t["cp_gom"] + a_t["lit_ngay"] * GIA_THUE * g), B=float(b_t_["cp_gom"] + b_t_["lit_ngay"] * GIA_THUE * g)) for g in (0.5, 2.0)})
        print("suc chua", m, ket["chua"]["muc"][str(m)]["dung_B"], flush=True)
    ket["chan_doan"] = dict(validation2=chan_doan(inp_v, ra_a_v, chay_han("validation2", 1.0, False)[0], the_tich, vung, dinh), test=chan_doan(inp_t, ra_a_t, ra_t, the_tich, vung, dinh))
    ket_json = json.loads(pd.Series([ket]).to_json(orient="records"))[0]
    json.dump(ket_json, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    tr = lambda v: so(v / 1e6)
    h = ket["han"]
    dong_h = lambda ten, r: f"| {ten} | {so(r['fill_rate'], 2)}% | {tr(r['ton_tb'])} | {so(r['huy_sl'], 0)} | {tr(r['huy_gia_tri'])} | {so(r['huy_pt_nhap'], 2)}% | {tr(r['cp_tong'])} |"
    dau_h = "| Phương án | Fill Rate | Tồn TB (tr đ) | Hàng loại | Giá trị loại (tr đ) | % hàng nhập | Tổng chi phí (tr đ) |\n|---|---:|---:|---:|---:|---:|---:|\n"
    L = ["# Hạn sử dụng và sức chứa kho", "", f"Luật ghi trước: docs/10 mục 10.11. **Hạn sử dụng, thể tích, sức chứa là giả định**, đơn hàng và nhu cầu là mô phỏng. Chính sách AI + hiệu chỉnh, mức phục vụ 95%. Xét riêng từng ràng buộc.", "",
         f"## 1. Hạn sử dụng ({ket['so_ma_han']}/{ket['so_ma']} mã)", "", "Số tính trên các mã có hạn.", "", "### Validation2: chọn trần lượng đặt", "", dau_h + "\n".join([dong_h("Không trần", h["validation2"]["khong_tran"]), dong_h("Có trần theo hạn", h["validation2"]["co_tran"])]), "",
         f"Theo luật (chi phí giảm ≥ {so(100 * GIAM_CP)}%, Fill Rate giảm ≤ {so(GIAM_FILL)} điểm): **{'dùng trần' if h['dung_tran'] else 'không dùng trần'}**.", "", "### Test (chỉ báo cáo)", "",
         dau_h + "\n".join([dong_h("Không xét hạn (như hiện nay, chưa tính hàng loại)", h["test"]["khong_xet_han"]), dong_h("Có hạn, không trần", h["test"]["khong_tran"]), dong_h("Có hạn, có trần", h["test"]["co_tran"]),
                            dong_h("Có hạn, không trần, xả được 50%", h["test"]["khong_tran_mat_50"]), dong_h("Có hạn, có trần, xả được 50%", h["test"]["co_tran_mat_50"]),
                            dong_h("Thời hạn ×0,5, không trần", h["do_nhay"]["0.5"]["khong_tran"]), dong_h("Thời hạn ×0,5, có trần", h["do_nhay"]["0.5"]["co_tran"]), dong_h("Thời hạn ×2, không trần", h["do_nhay"]["2.0"]["khong_tran"]), dong_h("Thời hạn ×2, có trần", h["do_nhay"]["2.0"]["co_tran"])]), "",
         f"10 mã loại nhiều nhất chiếm {so(h['ty_trong_top'], 0)}% giá trị loại (test, không trần):", "", "| Mã | Tên | Hạn (ngày) | Ngày được giao | MOQ | Nhu cầu/ngày | Loại, không trần (tr đ) | Loại, có trần (tr đ) |\n|---|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {r['ma']} | {r['ten']} | {r['han']} | {r['ngay_giao']} | {so(r['moq'], 0)} | {so(r['nhu_cau_ngay'])} | {tr(r['gia_tri'])} | {tr(r['gia_tri_tran'])} |" for r in h["top"]]
    L += ["", f"Mã có MOQ lớn hơn lượng bán được trong thời gian được giao (trần không giúp được): {', '.join(h['moq_lon']) or 'không có'}.", "", "## 2. Sức chứa", "", f"Mốc 100% = đỉnh thực tồn trên validation2: {VUNG[0]} {so(dinh[0] / 1000)} m³, {VUNG[1]} {so(dinh[1] / 1000)} m³. {ket['so_ma_lanh']} mã ở kho lạnh. Hiện trạng trên test đạt đỉnh {so(ket['chua']['hien_trang_test']['dinh_pt'][0], 0)}% / {so(ket['chua']['hien_trang_test']['dinh_pt'][1], 0)}% mốc này, vượt {ket['chua']['hien_trang_test']['so_ngay']} ngày.", "",
          "| Sức chứa | Tập | Phương án | Fill Rate | Tồn TB (tr đ) | Đỉnh thường / lạnh | Ngày vượt | Thuê ngoài (tr đ) | Lần cắt đơn | Tổng chi phí (tr đ) |\n|---:|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for m, d in ket["chua"]["muc"].items():
        for tap in ("validation2", "test"):
            for pa in ("A", "B"):
                r = d[tap][pa]
                L.append(f"| {so(100 * float(m), 0)}% | {tap} | {'A, thuê ngoài' if pa == 'A' else 'B, cắt đơn'} | {so(r['fill_rate'], 2)}% | {tr(r['ton_tb'])} | {so(r['dinh_pt'][0], 0)}% / {so(r['dinh_pt'][1], 0)}% | {r['so_ngay']} | {tr(r['thue'])} | {so(r['so_lan_cat'], 0)} | {tr(r['cp_chua'])} |")
    L += ["", "Theo luật trên validation2: " + "; ".join(f"sức chứa {so(100 * float(m), 0)}%: **{'B, cắt đơn' if d['dung_B'] else 'A, thuê ngoài'}**" for m, d in ket["chua"]["muc"].items()) + ".", "", "Độ nhạy giá thuê trên test, tổng chi phí (triệu đ):", "", "| Sức chứa | Giá ×0,5: A | Giá ×0,5: B | Giá ×2: A | Giá ×2: B |\n|---:|---:|---:|---:|---:|"]
    L += [f"| {so(100 * float(m), 0)}% | {tr(d['thue_do_nhay']['0.5']['A'])} | {tr(d['thue_do_nhay']['0.5']['B'])} | {tr(d['thue_do_nhay']['2.0']['A'])} | {tr(d['thue_do_nhay']['2.0']['B'])} |" for m, d in ket["chua"]["muc"].items()]
    cd = ket["chan_doan"]
    L += ["", "## 3. Chẩn đoán (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)", "", "| | Validation2 | Test |\n|---|---:|---:|",
          f"| Phần tồn vượt nhu cầu thật 60 ngày kế tiếp, % thể tích | {so(cd['validation2']['vuot_pt'])}% | {so(cd['test']['vuot_pt'])}% |", f"| Trong phần vượt đó, nhóm Z chiếm | {so(cd['validation2']['vuot_z_pt'])}% | {so(cd['test']['vuot_z_pt'])}% |",
          f"| Giá trị hàng loại đến từ {cd['test']['so_ma_dip_le']} mã chỉ bán dịp lễ | {so(cd['validation2']['loai_dip_le_pt'])}% | {so(cd['test']['loai_dip_le_pt'])}% |", f"| Số mã có hàng loại | {cd['validation2']['so_ma_loai']} | {cd['test']['so_ma_loai']} |",
          f"| Đỉnh thể tích thường / lạnh nếu bỏ mã lệch nhất, so với mốc 100% | {so(cd['validation2']['bo_ma_lon_nhat']['dinh_pt'][0], 0)}% / {so(cd['validation2']['bo_ma_lon_nhat']['dinh_pt'][1], 0)}% | {so(cd['test']['bo_ma_lon_nhat']['dinh_pt'][0], 0)}% / {so(cd['test']['bo_ma_lon_nhat']['dinh_pt'][1], 0)}% |",
          f"| Số ngày vượt nếu bỏ mã lệch nhất | {cd['validation2']['bo_ma_lon_nhat']['so_ngay']} | {cd['test']['bo_ma_lon_nhat']['so_ngay']} |", "",
          "Các mã làm thể tích lệch xa hiện trạng nhất trên test:", "", "| Mã | Tên | Thể tích TB (m³) | Hiện trạng (m³) | Chính sách nhập | Hiện trạng nhập | Nhu cầu | Tồn cuối kỳ |\n|---|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {r['ma']} | {r['ten']} | {so(r['lit_tb'] / 1000)} | {so(r['lit_tb_ht'] / 1000)} | {so(r['nhap'], 0)} | {so(r['nhap_ht'], 0)} | {so(r['nhu_cau'], 0)} | {so(r['ton_cuoi'], 0)} |" for r in cd["test"]["top"]]
    L += [""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
