"""Newsvendor cho hang chi ban dip le. Luat ghi TRUOC khi chay: docs/10 muc 10.12. Chi doc CSDL, khong ghi CSDL, khong doi chinh sach chinh.
Q = tong mua truoc x phan vi Cu/(Cu + Co) cua r; r = tong mua nay / tong mua truoc, gop moi ma. Dat 1 lan truoc mua, co the bo sung trong mua.
Chay: python src/newsvendor_mua_vu.py   (tai thu muc goc) -> reports/newsvendor_mua_vu.md, reports/newsvendor_mua_vu_trang_thai.json
"""
import json
import os
import sys
from math import ceil

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rang_buoc_kho import chi_tieu_han, gia_dinh_ma, mo_phong_kho, so_ngay_duoc_giao, the_tich_vung, vuot_suc_chua  # noqa: E402

SU_KIEN_THEO_MUA = {"Tết": "tet", "Trung thu": "trung_thu", "Halloween": "halloween", "Noel": "noel"}
TIEN_TO = "Chỉ dịp "
HE_SO_LECH_LT = 2                               # dat som them 2 x do lech lead time
GIAM_CP, GIAM_FILL, FILL_SAN = 0.005, 0.5, 95.0  # luat 10.12
MAT_HAN = 1.0                                   # hang co han du sau mua mat 100% gia von
STATE = "reports/newsvendor_mua_vu_trang_thai.json"
REPORT = "reports/newsvendor_mua_vu.md"


def su_kien_cua_ma(loai_mua_vu):
    """Ten su kien cua ma chi ban dip le; ma khac: None."""
    if not isinstance(loai_mua_vu, str) or not loai_mua_vu.startswith(TIEN_TO):
        return None
    return SU_KIEN_THEO_MUA.get(loai_mua_vu[len(TIEN_TO):])


def cac_mua(lich, ten_su_kien):
    """Cac mua cua 1 su kien tang dan theo thoi gian. lich: co cot ten_su_kien, ngay, cua_so_truoc, cua_so_sau."""
    g = lich[lich.ten_su_kien == ten_su_kien].sort_values("ngay")
    return [(pd.Timestamp(r.ngay) + pd.Timedelta(days=int(r.cua_so_truoc)), pd.Timestamp(r.ngay) + pd.Timedelta(days=int(r.cua_so_sau))) for r in g.itertuples()]


def tong_mua(chuoi, dau, cuoi):
    """Tong nhu cau trong mua; du lieu khong phu het mua thi None (khong coi la mua day du)."""
    if chuoi.empty or dau < chuoi.index.min() or cuoi > chuoi.index.max():
        return None
    return float(chuoi[dau:cuoi].sum())


def bang_cap_mua(chuoi_theo_ma, su_kien_theo_ma, lich):
    """Moi dong: ma, cuoi mua nay, tong mua truoc, tong mua nay. Chi cac cap mua lien tiep day du va mua truoc > 0."""
    dong = []
    for ma, sk in su_kien_theo_ma.items():
        mua = cac_mua(lich, sk)
        for (a0, b0), (a1, b1) in zip(mua, mua[1:]):
            t0, t1 = tong_mua(chuoi_theo_ma[ma], a0, b0), tong_mua(chuoi_theo_ma[ma], a1, b1)
            if t0 is not None and t1 is not None and t0 > 0:
                dong.append(dict(ma=ma, cuoi=b1, truoc=t0, nay=t1))
    return pd.DataFrame(dong, columns=["ma", "cuoi", "truoc", "nay"])


def mau_r(cap, ma, ngay_dat, cung_nam=None):
    """Mau r de tinh Q. Binh thuong: cac cap da ket thuc TRUOC ngay dat (khong nhin truoc).
    cung_nam = (tu, den): nhu validation2, chua co cap nao truoc do: lay cap ket thuc trong khoang, bo chinh ma do."""
    if cung_nam is not None:
        g = cap[(cap.cuoi >= cung_nam[0]) & (cap.cuoi <= cung_nam[1]) & (cap.ma != ma)]
    else:
        g = cap[cap.cuoi < ngay_dat]
    return (g.nay / g.truoc).values


def q_mua(tong_truoc, r, cu, co, moq):
    """Luong dat cho ca mua. Khong co mau r thi None; ban lo (Cu <= 0) thi 0."""
    if cu <= 0:
        return 0.0
    if not len(r):
        return None
    return float(max(moq, ceil(tong_truoc * float(np.quantile(r, cu / (cu + max(co, 0.0)))))))


def chi_phi_du(gia_von, ti_le_luu, han, ti_le_mat=MAT_HAN):
    """Thiet hai du 1 don vi sau mua: co han mat ti_le_mat gia von; khong han giu sang nam, ton 1 nam luu kho."""
    return float(gia_von * ti_le_mat) if han is not None else float(gia_von * ti_le_luu)


def ngay_dat_cua(dau_mua, lead_tb, lead_std):
    """Dau mua - lead time - 2 x do lech (lam tron len)."""
    return dau_mua - pd.Timedelta(days=int(round(lead_tb)) + ceil(HE_SO_LECH_LT * lead_std))


def lap_ke_hoach(inp, lich, cap, chuoi_theo_ma, han, cung_nam=None, ti_le_mat=MAT_HAN, bo_sung=False):
    """{chi so ma: [{t_dat, t_dau, t_cuoi, q, bo_sung}]} cho cac mua nam tron trong ky va dat duoc tu dau ky. Q chi dung nhu cau den ngay dat."""
    sku, ds = inp["sku"], pd.to_datetime(inp["ds"])
    ke_hoach, bo_qua = {}, []
    for i, r in enumerate(sku.itertuples()):
        sk = su_kien_cua_ma(r.loai_mua_vu)
        if sk is None:
            continue
        chuoi = chuoi_theo_ma[r.ma_sku]
        mua = cac_mua(lich, sk)
        for k, (dau, cuoi) in enumerate(mua):
            if cuoi < ds[0] or dau > ds[-1]:
                continue
            dat = ngay_dat_cua(dau, r.lead_time_tb, r.lead_time_std)
            if dat < ds[0] or cuoi > ds[-1] or k == 0:                    # k == 0: chua co mua truoc de lam goc
                bo_qua.append(dict(ma=r.ma_sku, dau=str(dau.date())))
                continue
            tong_truoc = tong_mua(chuoi[chuoi.index < dat], *mua[k - 1])
            q = None if tong_truoc is None else q_mua(tong_truoc, mau_r(cap, r.ma_sku, dat, cung_nam), r.gia_ban - r.gia_von, chi_phi_du(r.gia_von, r.ty_le_chi_phi_luu_kho, han[i], ti_le_mat), r.moq)
            if q is None:
                bo_qua.append(dict(ma=r.ma_sku, dau=str(dau.date())))
                continue
            ke_hoach.setdefault(i, []).append(dict(t_dat=int((dat - ds[0]).days), t_dau=int((dau - ds[0]).days), t_cuoi=int((cuoi - ds[0]).days), q=q, bo_sung=bo_sung))
    return ke_hoach, bo_qua


def ton_sau_mua(inp, ra, ke_hoach):
    """Gia tri ton cuoi moi mua, cong lai (dong). Hang du ngay sau khi mua ket thuc."""
    gv = inp["sku"].gia_von.values
    return float(sum(ra["ton"][i, min(m["t_cuoi"], ra["ton"].shape[1] - 1)] * gv[i] for i, ds in ke_hoach.items() for m in ds))


def mua_dai_hon_han(ke_hoach, ngay_giao):
    """Cac ma co thoi gian tu ngay dat den het mua dai hon so ngay duoc giao: mot lan dat khong the phuc vu het mua (hang het han giua mua)."""
    ra = set()
    for i, ds in ke_hoach.items():
        if ngay_giao[i] is not None and any(m["t_cuoi"] - m["t_dat"] > ngay_giao[i] for m in ds):
            ra.add(i)
    return ra


def chon_phuong_an(goc, cac_pa):
    """Luat 10.12: chi phi thap nhat trong cac phuong an dat: giam >= 0,5%, Fill Rate giam <= 0,5 diem va >= 95%. Khong dat: None."""
    dat = {k: v for k, v in cac_pa.items() if v["cp_tong"] <= goc["cp_tong"] * (1 - GIAM_CP) and goc["fill_rate"] - v["fill_rate"] <= GIAM_FILL and v["fill_rate"] >= FILL_SAN}
    return min(dat, key=lambda k: dat[k]["cp_tong"]) if dat else None


def danh_gia(inp, F, sig, z, b, ke_hoach, ngay_giao, the_tich, vung, dip, suc_chua, theo_sk=None):
    """Chay 2 moi truong voi 1 ke hoach. Tra ve chi tieu toan kho, rieng hang dip le, theo tung su kien, ton sau mua, dinh the tich."""
    ra = {}
    for ten, ng in (("co_han", ngay_giao), ("khong_han", None)):
        r = mo_phong_kho(inp, F, sig, z, b, ng, ke_hoach=ke_hoach)
        ra[ten] = dict(toan_kho=chi_tieu_han(inp, r), dip_le=chi_tieu_han(inp, r, dip), theo_su_kien={k: chi_tieu_han(inp, r, v) for k, v in (theo_sk or {}).items()}, ton_sau_mua=ton_sau_mua(inp, r, ke_hoach) if ke_hoach else None,
                       dinh_pt=vuot_suc_chua(the_tich_vung(r["ton"], the_tich, vung), suc_chua)["dinh_pt"], nhap=r["nhap"].sum(axis=1).tolist(), ton_cuoi=r["ton"][:, -1].tolist(), so_ngay_vuot=vuot_suc_chua(the_tich_vung(r["ton"], the_tich, vung), suc_chua)["so_ngay"])
    return ra


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from csdl import doc
    from gom_don import chuan_bi
    inp_v, F_v, sig_v, z_v, b_v = chuan_bi("validation2")
    inp_t, F_t, sig_t, z_t, b_t = chuan_bi("test")
    sku = inp_v["sku"]
    if "loai_mua_vu" not in sku.columns or not sku.loai_mua_vu.map(su_kien_cua_ma).notna().any():
        raise SystemExit("Nguồn dữ liệu này không có mã chỉ bán dịp lễ, không áp dụng.")
    lich = doc("SELECT ten_su_kien, ngay, cua_so_truoc, cua_so_sau FROM lich_su_kien")
    d = doc("SELECT ngay, ma_sku, nhu_cau FROM nhu_cau_that")
    d["ngay"] = pd.to_datetime(d.ngay)
    bang = d.pivot(index="ngay", columns="ma_sku", values="nhu_cau").sort_index().fillna(0)
    su_kien = {r.ma_sku: su_kien_cua_ma(r.loai_mua_vu) for r in sku.itertuples() if su_kien_cua_ma(r.loai_mua_vu)}
    chuoi = {m: bang[m] for m in su_kien}
    cap = bang_cap_mua(chuoi, su_kien, lich)
    han, the_tich, vung = gia_dinh_ma(sku)
    ng = [so_ngay_duoc_giao(h) for h in han]
    dip = np.array([i for i, r in enumerate(sku.itertuples()) if r.ma_sku in su_kien])
    theo_sk = {k: np.array([i for i, r in enumerate(sku.itertuples()) if su_kien.get(r.ma_sku) == k]) for k in sorted(set(su_kien.values()))}
    dinh = the_tich_vung(np.nan_to_num(inp_v["obs"]["ton_cuoi_ngay"]), the_tich, vung).max(axis=1)
    nam_v = (pd.Timestamp(inp_v["ds"][0]), pd.Timestamp(inp_v["ds"][-1]))
    ket = dict(so_ma=int(len(su_kien)), so_cap=int(len(cap)), r=dict(p10=float((cap.nay / cap.truoc).quantile(0.1)), p50=float((cap.nay / cap.truoc).median()), p90=float((cap.nay / cap.truoc).quantile(0.9))), tap={})
    for tap, inp, F, sig, z, b, cn in (("validation2", inp_v, F_v, sig_v, z_v, b_v, nam_v), ("test", inp_t, F_t, sig_t, z_t, b_t, None)):
        pa = {"goc": {}}
        kh1, bq = lap_ke_hoach(inp, lich, cap, chuoi, han, cn)
        kh2, _ = lap_ke_hoach(inp, lich, cap, chuoi, han, cn, bo_sung=True)
        kh50, _ = lap_ke_hoach(inp, lich, cap, chuoi, han, cn, ti_le_mat=0.5)
        kh50b, _ = lap_ke_hoach(inp, lich, cap, chuoi, han, cn, ti_le_mat=0.5, bo_sung=True)
        ket_tap = dict(so_mua=int(sum(len(v) for v in kh1.values())), bo_qua=bq, phuong_an={})
        dai = mua_dai_hon_han(kh1, ng)
        kh_bo = {i: v for i, v in kh1.items() if i not in dai}           # them SAU khi thay test: ma mot lan dat khong phuc vu het mua giu quy tac thuong
        for ten, kh in (("goc", None), ("mot_lan", kh1), ("bo_sung", kh2), ("mot_lan_co50", kh50), ("bo_sung_co50", kh50b), ("mot_lan_bo_ma", kh_bo)):
            ket_tap["phuong_an"][ten] = danh_gia(inp, F, sig, z, b, kh, ng, the_tich, vung, dip, dinh, theo_sk)
            print(tap, ten, round(ket_tap["phuong_an"][ten]["co_han"]["toan_kho"]["cp_tong"] / 1e6, 1), round(ket_tap["phuong_an"][ten]["co_han"]["toan_kho"]["fill_rate"], 2), flush=True)
        ket_tap["ke_hoach_mot_lan"] = {sku.ma_sku.iloc[i]: v for i, v in kh1.items()}
        ket_tap["mua_dai_hon_han"] = sorted(sku.ma_sku.iloc[i] for i in mua_dai_hon_han(kh1, ng))
        ket["tap"][tap] = ket_tap
    pv = ket["tap"]["validation2"]["phuong_an"]
    ket["chon"] = chon_phuong_an(pv["goc"]["co_han"]["toan_kho"], {k: pv[k]["co_han"]["toan_kho"] for k in ("mot_lan", "bo_sung")})
    json.dump(json.loads(pd.Series([ket]).to_json(orient="records", default_handler=str))[0], open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    tr = lambda v: so(v / 1e6)
    TEN = {"goc": "Quy tắc hiện tại", "mot_lan": "Newsvendor, một lần", "bo_sung": "Newsvendor + bổ sung", "mot_lan_co50": "Một lần, xả được 50%", "bo_sung_co50": "Bổ sung, xả được 50%", "mot_lan_bo_ma": "Một lần, bỏ mã hạn ngắn (thêm sau khi thấy test)"}
    L = ["# Newsvendor cho hàng chỉ bán dịp lễ", "", f"Luật ghi trước: docs/10 mục 10.12. Dữ liệu mô phỏng; hạn sử dụng và chi phí hàng dư là giả định. {ket['so_ma']} mã, {ket['so_cap']} cặp mùa liên tiếp; r trung vị {so(ket['r']['p50'], 2)}, p10–p90 {so(ket['r']['p10'], 2)}–{so(ket['r']['p90'], 2)}.", ""]
    dau = "| Phương án | CP toàn kho (tr đ) | Fill toàn kho | Fill hàng dịp lễ | Tồn TB dịp lễ (tr đ) | Hàng loại (tr đ) | Tồn sau mùa (tr đ) | Đỉnh thể tích |\n|---|---:|---:|---:|---:|---:|---:|---:|"
    for tap in ("validation2", "test"):
        kt = ket["tap"][tap]
        L += [f"## {tap}", "", f"{kt['so_mua']} mùa theo newsvendor; {len(kt['bo_qua'])} mùa giữ quy tắc thường vì ngày đặt trước đầu kỳ, mùa ra ngoài kỳ, hoặc thiếu mùa trước.", ""]
        for mt, nhan in (("co_han", "Môi trường có hạn sử dụng (dùng để chọn trên validation2)"), ("khong_han", "Môi trường không hạn (thiên vị trữ dư)")):
            L += [f"### {nhan}", "", dau]
            for k, r in kt["phuong_an"].items():
                x = r[mt]
                L.append(f"| {TEN[k]} | {tr(x['toan_kho']['cp_tong'])} | {so(x['toan_kho']['fill_rate'], 2)}% | {so(x['dip_le']['fill_rate'], 2)}% | {tr(x['dip_le']['ton_tb'])} | {tr(x['toan_kho']['huy_gia_tri'])} | {tr(x['ton_sau_mua']) if x['ton_sau_mua'] is not None else '–'} | {so(x['dinh_pt'][0], 0)}% |")
            L += [""]
    L += ["## Theo luật", "", f"Trên validation2, môi trường có hạn: **{TEN[ket['chon']] if ket['chon'] else 'giữ quy tắc hiện tại, không phương án nào đạt'}**. Phương án bỏ mã hạn ngắn được thêm sau khi thấy test nên không dự chọn, chỉ để tham khảo.", ""]
    i = int(np.argmax(np.array(ket["tap"]["test"]["phuong_an"]["goc"]["khong_han"]["ton_cuoi"]) * the_tich))
    L += [f"## Mã chiếm chỗ nhất trên test: {sku.ten_sku.iloc[i]}", "", "| Phương án | Nhập | Tồn cuối kỳ |\n|---|---:|---:|"]
    L += [f"| {TEN[k]} | {so(r['khong_han']['nhap'][i], 0)} | {so(r['khong_han']['ton_cuoi'][i], 0)} |" for k, r in ket["tap"]["test"]["phuong_an"].items()]
    L += ["", f"Nhu cầu cả kỳ: {so(float(inp_t['dem'][i].sum()), 0)}.", ""]
    L += ["## Chẩn đoán theo từng dịp (thêm SAU khi thấy kết quả, không thuộc luật ghi trước)", "", "Quy tắc hiện tại so với newsvendor một lần. Chi phí gồm đặt hàng, lưu kho, lợi nhuận mất, hàng loại; triệu đ.", "",
          "| Tập | Môi trường | Dịp | CP hiện tại | CP newsvendor | Fill hiện tại | Fill newsvendor | Loại hiện tại | Loại newsvendor |\n|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for tap in ("validation2", "test"):
        for mt in ("co_han", "khong_han"):
            g_, n_ = ket["tap"][tap]["phuong_an"]["goc"][mt]["theo_su_kien"], ket["tap"][tap]["phuong_an"]["mot_lan"][mt]["theo_su_kien"]
            L += [f"| {tap} | {'Có hạn' if mt == 'co_han' else 'Không hạn'} | {k} | {tr(g_[k]['cp_tong'])} | {tr(n_[k]['cp_tong'])} | {so(g_[k]['fill_rate'])}% | {so(n_[k]['fill_rate'])}% | {tr(g_[k]['huy_gia_tri'])} | {tr(n_[k]['huy_gia_tri'])} |" for k in g_]
    L += ["", "Mã có thời gian từ ngày đặt đến hết mùa dài hơn số ngày được giao (một lần đặt không phục vụ hết mùa): " + "; ".join(f"{tap}: {', '.join(ket['tap'][tap]['mua_dai_hon_han']) or 'không có'}" for tap in ("validation2", "test")) + ".", ""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
