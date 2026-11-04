"""Gom don theo nha cung cap. Luat ghi TRUOC khi chay: docs/10 muc 10.6. Chi doc CSDL, khong ghi CSDL.
Muc 1 - gom cung ngay: quyet dinh dat hang giu nguyen, cac dong cung nha cung cap cung ngay gop 1 phieu.
Muc 2 - dat kem (can-order): khi 1 ma cua nha cung cap phai dat, cac ma con lai dat kem neu trong kho + dang ve <= ROP + k ngay nhu cau du bao.
Chi phi 1 phieu = ti_le * S lon nhat trong phieu + (1 - ti_le) * tong S cac dong; phieu 1 dong dung bang S cu. ti_le la GIA DINH.
Chay: python src/gom_don.py   (tai thu muc goc) -> reports/gom_don.md, reports/gom_don_trang_thai.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TI_LE_CHINH = 0.5
TI_LE_THU = [0.3, 0.5, 0.7]
K_THU = [1, 2, 3, 5]
R_COVER = 7
NGUONG_CHI_PHI, NGUONG_FILL = 0.005, 0.2                  # luat 10.6: chi phi giam >= 0,5% va Fill Rate khong giam qua 0,2 diem
STATE = "reports/gom_don_trang_thai.json"
REPORT = "reports/gom_don.md"


def chi_phi_phieu(ds_s, ti_le):
    """Chi phi 1 phieu gom cac dong co chi phi dat rieng ds_s."""
    if not 0 <= ti_le <= 1:
        raise ValueError("ti_le phai trong [0, 1]")
    s = np.asarray(ds_s, dtype=float)
    return float(ti_le * s.max() + (1 - ti_le) * s.sum()) if len(s) else 0.0


def gom_cung_ngay(dat, ncc, s, ti_le=TI_LE_CHINH):
    """dat: mang (ma, ngay) luong dat; ncc, s theo ma. Tra ve dict: so dong, so phieu, chi phi khong gom, chi phi co gom."""
    dat, ncc, s = np.asarray(dat), np.asarray(ncc), np.asarray(s, dtype=float)
    if dat.shape[0] != len(ncc) or len(ncc) != len(s):
        raise ValueError("dat, ncc, s khong cung so ma")
    i, t = np.nonzero(dat > 0)
    if not len(i):
        return dict(so_dong=0, so_phieu=0, chi_phi_rieng=0.0, chi_phi_gom=0.0)
    d = pd.DataFrame({"t": t, "n": ncc[i], "s": s[i]})
    g = d.groupby(["t", "n"]).s
    return dict(so_dong=len(d), so_phieu=int(g.ngroups), chi_phi_rieng=float(d.s.sum()),
                chi_phi_gom=float(ti_le * g.max().sum() + (1 - ti_le) * g.sum().sum()))


def so_luong(rule, ip, muc, q_eoq, moq, fw_lr, ss):
    """Luong dat theo quy tac khi kiem tra voi muc (ROP, hoac muc dat kem). Cung cong thuc ton_kho.simulate."""
    if rule == "eoq":
        q = max(q_eoq, moq)
        return float(np.ceil((np.floor((muc - ip) / q) + 1) * q))
    return float(np.ceil(max(moq, fw_lr + ss - ip)))


def mo_phong(inp, F, sig, z, buoc, k_ngay=0, horizon=28):
    """Mo phong ca kho theo tung ngay. k_ngay = 0: tung ma doc lap, phai trung dung ton_kho.simulate (co test). F: (ma, moc, 28)."""
    sku, D, closed, LT = inp["sku"], inp["dem"], inp["closed"], inp["LT"]
    S_ma, n = len(sku), D.shape[1]
    ncc = sku.ma_ncc.values
    S, H, moq = sku.chi_phi_dat_hang.values.astype(float), (sku.ty_le_chi_phi_luu_kho * sku.gia_von).values.astype(float), sku.moq.values.astype(float)
    L = np.maximum(1, np.round(sku.lead_time_tb.values).astype(int))
    lt_std = sku.lead_time_std.values.astype(float)
    quy_tac = np.where(sku.xyz_train.values == "Z", "dat_den_muc", "eoq")
    onhand = np.array(inp["init"], dtype=float)
    pipe = [list(p) for p in inp["pipe0"]]
    ra = {c: np.zeros((S_ma, n)) for c in ["nhap", "xuat", "ton", "dat"]}
    nhom = {c: np.flatnonzero(ncc == c) for c in np.unique(ncc)}
    for t in range(n):
        if closed[t]:
            ra["ton"][:, t] = onhand
            continue
        state = {}
        for i in range(S_ma):
            rec = sum(q for a, q in pipe[i] if a <= t)
            pipe[i] = [(a, q) for a, q in pipe[i] if a > t]
            onhand[i] += rec
            ra["nhap"][i, t] = rec
            sold = min(D[i, t], onhand[i])
            onhand[i] -= sold
            ra["xuat"][i, t] = sold
            km = min((t + 1) // buoc, F.shape[1] - 1)
            f, st = F[i, km], t + 1 - buoc * km
            cua = f[st:] if st < horizon else f[-1:]
            fw = lambda m, c=f, b=st: (c[b:b + m] if b < horizon else c[-1:]).mean() * m
            ltd = fw(L[i])
            ss = z * np.sqrt(sig[i] ** 2 + (ltd / L[i]) ** 2 * lt_std[i] ** 2)
            dbar = f.mean()
            state[i] = dict(rop=ltd + ss, ss=ss, ip=onhand[i] + sum(q for _, q in pipe[i]), eoq=np.sqrt(2 * dbar * 365 * S[i] / H[i]) if dbar > 0 else 0.0,
                            fw_lr=fw(L[i] + R_COVER), d=ltd / L[i], _=cua)
        for ma_nhom in nhom.values():
            bat_buoc = [i for i in ma_nhom if state[i]["ip"] <= state[i]["rop"]]
            for i in ma_nhom:
                x = state[i]
                muc = x["rop"]
                if i not in bat_buoc:
                    if not (bat_buoc and k_ngay > 0):
                        continue
                    muc = x["rop"] + k_ngay * x["d"]
                    if x["ip"] > muc or x["d"] <= 0:
                        continue
                order = so_luong(quy_tac[i], x["ip"], muc, x["eoq"], moq[i], x["fw_lr"], x["ss"])
                pipe[i].append((t + LT[i, t], order))
                ra["dat"][i, t] = order
        ra["ton"][:, t] = onhand
    return ra


def tong_ket(inp, ra, ti_le=TI_LE_CHINH):
    """Chi tieu ca kho. Chi phi dat tinh theo dong dat (khong phai so ngay nhan hang nhu ket_qua_ton_kho) de so duoc voi gom don."""
    sku, D, closed = inp["sku"], inp["dem"], inp["closed"]
    o = ~closed
    gom = gom_cung_ngay(ra["dat"], sku.ma_ncc.values, sku.chi_phi_dat_hang.values, ti_le)
    thieu = np.clip(D - ra["xuat"], 0, None)
    gv = sku.gia_von.values
    luu = float((ra["ton"].mean(axis=1) * gv * sku.ty_le_chi_phi_luu_kho.values).sum() * D.shape[1] / 365)
    ln = float((thieu[:, o].sum(axis=1) * (sku.gia_ban.values - gv)).sum())
    return dict(**gom, luu=luu, loi_nhuan_mat=ln, fill_rate=float(100 * ra["xuat"][:, o].sum() / D[:, o].sum()), ton_tb=float((ra["ton"].mean(axis=1) * gv).sum()),
                so_ngay_thieu=int((thieu[:, o] > 0.5).sum()), cp_rieng=gom["chi_phi_rieng"] + luu + ln, cp_gom=gom["chi_phi_gom"] + luu + ln)


def giu_dat_kem(moi, goc, nguong_cp=NGUONG_CHI_PHI, nguong_fr=NGUONG_FILL):
    """Luat 10.6: so voi chi gom cung ngay, chi phi giam it nhat 0,5% va Fill Rate khong giam qua 0,2 diem."""
    return moi["cp_gom"] <= goc["cp_gom"] * (1 - nguong_cp) and goc["fill_rate"] - moi["fill_rate"] <= nguong_fr


def tach_loi_ich(moi, goc):
    """Chenh lech chi phi lien quan (goc - moi, duong la co loi) tach theo khoan: dat hang, luu kho, loi nhuan mat."""
    d = dict(dat_hang=goc["chi_phi_gom"] - moi["chi_phi_gom"], luu_kho=goc["luu"] - moi["luu"], loi_nhuan_mat=goc["loi_nhuan_mat"] - moi["loi_nhuan_mat"])
    return dict(d, tong=sum(d.values()))


def chuan_bi(tap):
    from scipy.stats import norm
    import ton_kho as T
    inp = T.load_inputs(tap)
    _, model, hc = T.POLICIES["cong_thuc_du_bao_ai_hc"]
    F, buoc = T.forecasts(model, tap, inp["sku"], inp["origin0"])
    hs, sig = T.validation_stats(model, inp["sku"], hc)
    return inp, F * hs[:, None, None], sig, float(norm.ppf(T.MAIN)), buoc


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    inp, F, sig, z, buoc = chuan_bi("validation2")
    goc = tong_ket(inp, mo_phong(inp, F, sig, z, buoc))
    bang = {"0": goc}
    for k in K_THU:
        bang[str(k)] = tong_ket(inp, mo_phong(inp, F, sig, z, buoc, k))
        print("validation2 k =", k, {a: round(b, 2) for a, b in bang[str(k)].items() if a in ("so_dong", "so_phieu", "fill_rate")}, round(bang[str(k)]["cp_gom"] / 1e6, 1), flush=True)
    dat = {k: v for k, v in bang.items() if k != "0" and giu_dat_kem(v, goc)}
    k_chon = int(min(dat, key=lambda k: dat[k]["cp_gom"])) if dat else 0
    inp_t, F_t, sig_t, z_t, buoc_t = chuan_bi("test")
    ra0 = mo_phong(inp_t, F_t, sig_t, z_t, buoc_t)
    ket = {"goc": {str(t): tong_ket(inp_t, ra0, t) for t in TI_LE_THU}}
    if k_chon:
        ra1 = mo_phong(inp_t, F_t, sig_t, z_t, buoc_t, k_chon)
        ket["dat_kem"] = {str(t): tong_ket(inp_t, ra1, t) for t in TI_LE_THU}
    json.dump(dict(validation2=bang, k_chon=k_chon, test=ket), open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    tr = lambda v: so(v / 1e6)
    dong = lambda t, r: f"| {t} | {so(r['so_dong'], 0)} | {so(r['so_phieu'], 0)} | {so(r['fill_rate'], 2)}% | {tr(r['ton_tb'])} | {tr(r['chi_phi_rieng'])} | {tr(r['chi_phi_gom'])} | {tr(r['cp_rieng'])} | {tr(r['cp_gom'])} |"
    dau = "| Phương án | Dòng đặt | Số phiếu | Fill Rate | Tồn TB (tr đ) | CP đặt riêng | CP đặt gom | CP liên quan riêng | CP liên quan gom |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    L = ["# Gom đơn theo nhà cung cấp", "", "Luật ghi trước: docs/10 mục 10.6. Chính sách AI + hiệu chỉnh, mức phục vụ 95%. Dữ liệu mô phỏng; tỉ lệ chi phí chung của phiếu là **giả định**. "
         "Chi phí đặt ở đây tính theo dòng đặt nên hơi khác `ket_qua_ton_kho` (tính theo số ngày nhận hàng).", "",
         f"## Validation2: chọn k (tỉ lệ {so(TI_LE_CHINH)})", "", dau + "\n".join(dong(f"k = {k}" if k != "0" else "Chỉ gom cùng ngày", r) for k, r in bang.items()), "",
         f"Theo luật: **{'đặt kèm k = ' + str(k_chon) if k_chon else 'không dùng đặt kèm, chỉ gom cùng ngày'}**.", "", "## Test (chỉ báo cáo)", "", dau
         + "\n".join(dong(f"{ten}, tỉ lệ {so(float(t))}", r) for ten, d in [("Chỉ gom cùng ngày", ket["goc"])] + ([(f"Đặt kèm k = {k_chon}", ket["dat_kem"])] if k_chon else []) for t, r in d.items()), ""]
    if k_chon:
        g0, d1 = ket["goc"][str(TI_LE_CHINH)], ket["dat_kem"][str(TI_LE_CHINH)]
        tach = tach_loi_ich(d1, g0)
        ket["tach"] = tach
        muc1 = g0["cp_rieng"] - g0["cp_gom"]
        L += ["## Lợi ích đến từ đâu (test, tỉ lệ 0,5)", "", f"- Mức 1, chỉ gom cùng ngày: giảm **{tr(muc1)} triệu đ** chi phí liên quan, không đổi tồn kho, không đổi Fill Rate.",
              f"- Mức 2 so với mức 1: giảm **{tr(tach['tong'])} triệu đ**, gồm đặt hàng {tr(tach['dat_hang'])}, lưu kho {tr(tach['luu_kho'])}, lợi nhuận mất {tr(tach['loi_nhuan_mat'])}.",
              "- Đặt kèm làm hàng được đặt sớm hơn, nên có tác dụng như **tăng thêm dự phòng**; phần giảm lợi nhuận mất đến từ đó, không phải từ việc chia sẻ chi phí phiếu.", ""]
        json.dump(dict(validation2=bang, k_chon=k_chon, test=ket), open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
