"""GD F: tham so ton kho (SS, ROP, luong dat) va mo phong de so sanh chinh sach dat hang.
DOC TU CO SO DU LIEU (data/kho_hang.db), ghi ket qua nguoc vao CSDL. Chay sau: python src/nap_database.py
Chay: python src/ton_kho.py
Ket qua: CSDL (chinh_sach, tham_so_ton_kho, ket_qua_ton_kho, mo_phong_ngay, v_so_sanh_chinh_sach);
         reports/ton_kho_chon_quy_tac.md (buoc 1), reports/ton_kho_so_sanh.md (buoc 2)

Buoc 1 (VALIDATION2: 10/2024-09/2025): chon quy tac luong dat {eoq, dat_den_muc, lai} x chinh sach AI {co/khong hieu chinh}
        theo chi phi lien quan thap nhat = dat hang + luu kho + loi nhuan mat (luat ghi truoc: docs/10 muc 10.2).
Buoc 2 (TEST: 10/2025-09/2026): chay moi chinh sach theo cong thuc voi quy tac da chon + hien trang (do tu du lieu).

Moi chinh sach dung CHUNG: nhu cau that, thoi gian giao hang thuc te, ton va hang dang ve ban dau, chi phi, MOQ.
  hien_trang: do tu du lieu. Trong du lieu mo phong, nguoi lap ke hoach "biet truoc" duong nhu cau ky vong (lech +-10%)
              -> doi thu RAT MANH, manh hon thuc te.
Quy tac dat hang, kiem tra moi ngay kho mo cua:
  ROP_t = du bao nhu cau trong L ngay + SS_t ;  SS_t = z * sqrt(sigma_LTD^2 + d_t^2 * sigma_LT^2)
  sigma_LTD: do lech chuan tong sai so du bao trong L ngay (L = lead time TB), do tren validation2
  Neu ton hien co + hang dang ve (IP) <= ROP thi dat:
    eoq         : n * Q, Q = max(EOQ, MOQ), n nho nhat de IP + nQ > ROP;  EOQ = sqrt(2 D S / H), H = h * gia von
    dat_den_muc : max(MOQ, du bao trong (L + R) ngay + SS - IP), R = 7 ngay
    lai         : eoq cho nhom X/Y, dat_den_muc cho nhom Z
  Chi dung du bao cua MOC GAN NHAT DA QUA (khong nhin truoc). Mat ban khi het hang (khong no don).
"""
import os
import re
import sys
from contextlib import closing

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, os.path.dirname(__file__))
from csdl import ket_noi, doc  # noqa: E402
from danh_gia import HORIZON  # noqa: E402
from kiem_tra_du_lieu import nguon_du_lieu  # noqa: E402

SEED = 20261023
LEVELS = [0.90, 0.95, 0.99]
MAIN = 0.95
R_COVER = 7
RULES = ["eoq", "dat_den_muc", "lai"]
AI = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]   # chon o nap_database.MO_HINH_DUOC_CHON
NGUON_DL = nguon_du_lieu()
GHI_NGUON = "Du lieu mo phong." if NGUON_DL["la_mo_phong"] else f"Nguon: {NGUON_DL['ten']}."
POLICIES = {   # ma -> (mo ta, mo hinh du bao, hieu chinh lech)
    "hien_trang": (NGUON_DL.get("note_ht", "Hiện trạng trong dữ liệu (người lập kế hoạch biết trước nhu cầu kỳ vọng, lệch ±10%)").replace("\\* ", ""), None, 0),
    "cong_thuc_du_bao_moc": ("Công thức + dự báo mốc: trung bình trượt 28 ngày, cập nhật mỗi tuần", "tb_truot_28_tuan", 0),
    "cong_thuc_du_bao_ai": (NGUON_DL.get("mo_ta_ai", "Công thức + dự báo AI: kết hợp LightGBM + Prophet theo nhóm"), AI, 0),
    "cong_thuc_du_bao_ai_hc": ("Công thức + dự báo AI + hiệu chỉnh lệch theo nhóm XYZ (ước lượng trên validation)", AI, 1),
}


# ------------------------------------------------------------------ du lieu dau vao (tu CSDL)
def load_inputs(tap):
    sku = doc("SELECT s.*, p.xyz_train FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku) ORDER BY ma_sku")
    rng_ = doc("SELECT MIN(moc) AS o, MAX(ngay) AS d FROM du_bao WHERE tap = ? AND ma_mo_hinh = ?", (tap, AI))
    o0 = pd.Timestamp(rng_.o.iloc[0])
    days = pd.date_range(o0 + pd.Timedelta(days=1), rng_.d.iloc[0])
    ds = [d.strftime("%Y-%m-%d") for d in days]
    nghi = set(doc("SELECT ngay FROM lich_ngay_nghi").ngay)
    closed = np.array([d in nghi for d in ds])
    dem = doc("SELECT ngay, ma_sku, nhu_cau FROM nhu_cau_that WHERE ngay BETWEEN ? AND ?", (ds[0], ds[-1]))
    dem = dem.pivot(index="ma_sku", columns="ngay", values="nhu_cau").reindex(index=sku.ma_sku, columns=ds).fillna(0).values
    g = doc("SELECT ngay, ma_sku, qty_in, qty_out, ton_cuoi_ngay FROM giao_dich_sach WHERE ngay BETWEEN ? AND ?",
            (o0.strftime("%Y-%m-%d"), ds[-1]))
    piv = lambda c: g.pivot(index="ma_sku", columns="ngay", values=c).reindex(index=sku.ma_sku)
    obs = {c: piv(c)[ds].values for c in ["qty_in", "qty_out", "ton_cuoi_ngay"]}
    init_onhand = piv("ton_cuoi_ngay")[o0.strftime("%Y-%m-%d")].values
    shocks = doc("SELECT nhom_ly_do, su_kien, tu_ngay, den_ngay, muc_do, tac_dong_chinh FROM su_kien_dot_bien")
    # hang dang ve luc bat dau: hang da ve trong L ngay dau theo du lieu (don cu, dat truoc moc dau)
    pipe0 = []
    for i, r in enumerate(sku.itertuples()):
        L = max(1, int(round(r.lead_time_tb)))
        pipe0.append([(t, obs["qty_in"][i, t]) for t in range(min(L, len(ds))) if obs["qty_in"][i, t] > 0])
    return dict(sku=sku, days=days, ds=ds, closed=closed, dem=dem, obs=obs, init=init_onhand, pipe0=pipe0,
                LT=lead_time_matrix(sku, days, shocks), origin0=o0)


def lead_time_matrix(sku, days, shocks):
    """Thoi gian giao hang thuc te neu dat ngay t (boc ngau nhien 1 lan, dung chung moi chinh sach).
    = round(N(lead_time_tb, lead_time_std)) + cham do bao (3 x muc do, tu ngay -1 den +10) + cham do nha cung cap."""
    n = len(days)
    storm = np.zeros(n)
    for r in shocks[shocks.nhom_ly_do == "Thiên tai"].itertuples():
        i0 = (pd.Timestamp(r.tu_ngay) - days[0]).days
        for k in range(-1, 11):
            if 0 <= i0 + k < n:
                storm[i0 + k] = max(storm[i0 + k], round(3 * r.muc_do))
    sup = {}
    for r in shocks[shocks.nhom_ly_do == "Đứt gãy cung ứng"].itertuples():
        ncc, add = re.search(r"NCC\d+", r.su_kien).group(), int(re.search(r"\+(\d+)", r.tac_dong_chinh).group(1))
        a = sup.setdefault(ncc, np.zeros(n))
        a[[r.tu_ngay <= d.strftime("%Y-%m-%d") <= r.den_ngay for d in days]] = add
    rng = np.random.default_rng(SEED)
    base = np.maximum(1, np.round(rng.normal(sku.lead_time_tb.values[:, None], sku.lead_time_std.values[:, None], (len(sku), n))))
    return (base + storm[None, :] + np.array([sup.get(c, np.zeros(n)) for c in sku.ma_ncc])).astype(int)


def forecasts(model, tap, sku, origin0):
    """F[i, k, h]: du bao SKU i tai moc k cho ngay thu h+1; buoc = khoang cach giua 2 moc (28 ngay, hoac 7 ngay voi du bao
    cap nhat moi tuan - docs/10 muc 9.6), lay tu du lieu."""
    d = doc("SELECT moc, ma_sku, ngay_thu, du_bao FROM du_bao WHERE ma_mo_hinh = ? AND tap = ?", (model, tap))
    origins = sorted(d.moc.unique())
    assert origins[0] == origin0.strftime("%Y-%m-%d"), f"moc dau {model}/{tap} khong khop"
    idx = {s: i for i, s in enumerate(sku.ma_sku)}
    oi = {o: k for k, o in enumerate(origins)}
    F = np.zeros((len(sku), len(origins), HORIZON))
    F[d.ma_sku.map(idx).values, d.moc.map(oi).values, d.ngay_thu.values - 1] = d.du_bao.values
    buoc = (pd.Timestamp(origins[1]) - pd.Timestamp(origins[0])).days if len(origins) > 1 else HORIZON
    assert all((pd.Timestamp(b) - pd.Timestamp(a)).days == buoc for a, b in zip(origins, origins[1:])), "moc khong deu"
    return F, buoc


def validation_stats(model, sku, hieu_chinh):
    """He so hieu chinh lech (theo nhom XYZ) va sigma_LTD tung SKU, CHI tu tap validation2."""
    v = doc("SELECT moc, ma_sku, ngay_thu, du_bao, thuc_te FROM du_bao WHERE ma_mo_hinh = ? AND tap = 'validation2'", (model,))
    v = v.merge(sku[["ma_sku", "xyz_train", "lead_time_tb"]], on="ma_sku")
    sc = v.dropna(subset=["thuc_te"])
    k = (sc.groupby("xyz_train").thuc_te.sum() / sc.groupby("xyz_train").du_bao.sum()) if hieu_chinh else None
    v["e"] = v.thuc_te - v.du_bao * (v.xyz_train.map(k) if hieu_chinh else 1.0)
    sig = {}
    for s, g in v.groupby("ma_sku"):
        L = max(1, int(round(g.lead_time_tb.iloc[0])))
        sums = []
        for _, o in g.sort_values("ngay_thu").groupby("moc"):
            if len(o) >= L:
                w = np.convolve(o.e.values, np.ones(L), "valid")      # cua so co ngay khong cham (NaN) bi loai
                sums += list(w[~np.isnan(w)])
        sig[s] = np.std(sums) if len(sums) >= 5 else np.sqrt(L) * np.nanstd(g.e)
    hs = sku.xyz_train.map(k).values if hieu_chinh else np.ones(len(sku))
    return hs, np.array([sig[s] for s in sku.ma_sku])


# ------------------------------------------------------------------ mo phong 1 SKU
def simulate(F, sigma, z, D, LTr, closed, onhand0, pipe0, S, H, moq, lt_tb, lt_std, rule, buoc=HORIZON):
    """buoc: khoang cach giua 2 moc du bao (mac dinh 28 = moi dot 28 ngay; GD E vong 4 thu 7 = cap nhat moi tuan)."""
    n = len(D)
    L = max(1, int(round(lt_tb)))
    onhand, pipe = float(onhand0), list(pipe0)
    out = {k: np.zeros(n) for k in ["nhap", "xuat", "ton", "dat", "ss", "eoq"]}
    out["rop"] = np.full(n, np.nan)
    for t in range(n):
        if not closed[t]:
            rec = sum(q for a, q in pipe if a <= t)
            pipe = [(a, q) for a, q in pipe if a > t]
            onhand += rec
            out["nhap"][t] = rec
        sold = 0.0 if closed[t] else min(D[t], onhand)
        onhand -= sold
        out["xuat"][t] = sold
        if not closed[t]:
            k = min((t + 1) // buoc, F.shape[0] - 1)                 # moc gan nhat da qua
            f, st = F[k], t + 1 - buoc * k
            fw = lambda m: (f[st:st + m] if st < HORIZON else f[-1:]).mean() * m   # du bao m ngay toi (trong pham vi moc)
            ltd = fw(L)
            ss = z * np.sqrt(sigma ** 2 + (ltd / L) ** 2 * lt_std ** 2)
            rop = ltd + ss
            dbar = f.mean()
            eoq = np.sqrt(2 * dbar * 365 * S / H) if dbar > 0 else 0.0
            ip = onhand + sum(q for _, q in pipe)
            if ip <= rop:
                if rule == "eoq":
                    q = max(eoq, moq)
                    order = (np.floor((rop - ip) / q) + 1) * q
                else:                                                # dat_den_muc
                    order = max(moq, fw(L + R_COVER) + ss - ip)
                order = float(np.ceil(order))
                pipe.append((t + LTr[t], order))
                out["dat"][t] = order
            out["rop"][t], out["ss"][t], out["eoq"][t] = rop, ss, eoq
        out["ton"][t] = onhand
    return out


def kpis(D, closed, r, nhap, xuat, ton):
    o = ~closed
    unmet = np.clip(D - xuat, 0, None)[o].sum()
    return dict(nhu_cau=D[o].sum(), da_dap_ung=xuat[o].sum(), so_ngay_thieu=int((np.clip(D - xuat, 0, None)[o] > 0.5).sum()),
                ton_tb=ton.mean(), gia_tri_ton_tb=ton.mean() * r.gia_von, so_lan_nhap=int((nhap > 0).sum()),
                chi_phi_dat=(nhap > 0).sum() * r.chi_phi_dat_hang,
                chi_phi_luu=ton.mean() * r.gia_von * r.ty_le_chi_phi_luu_kho * len(D) / 365,
                doanh_thu_mat=unmet * r.gia_ban, loi_nhuan_mat=unmet * (r.gia_ban - r.gia_von), ton_cuoi_ky=ton[-1])


def run(inp, tap, pol, rule, levels, keep_daily=False):
    _, model, hc = POLICIES[pol]
    sku = inp["sku"]
    F, buoc = forecasts(model, tap, sku, inp["origin0"])
    hs, sig = validation_stats(model, sku, hc)
    F = F * hs[:, None, None]
    res, params, daily = [], [], []
    for lv in levels:
        z = norm.ppf(lv)
        for i, r in enumerate(sku.itertuples()):
            ru = ("dat_den_muc" if r.xyz_train == "Z" else "eoq") if rule == "lai" else rule
            o = simulate(F[i], sig[i], z, inp["dem"][i], inp["LT"][i], inp["closed"], inp["init"][i], inp["pipe0"][i],
                         r.chi_phi_dat_hang, r.ty_le_chi_phi_luu_kho * r.gia_von, r.moq, r.lead_time_tb, r.lead_time_std, ru,
                         buoc=buoc)
            res.append(dict(ma_chinh_sach=pol, muc_phuc_vu=lv, ma_sku=r.ma_sku,
                            **kpis(inp["dem"][i], inp["closed"], r, o["nhap"], o["xuat"], o["ton"])))
            params.append(dict(ma_chinh_sach=pol, muc_phuc_vu=lv, ma_sku=r.ma_sku, he_so_hieu_chinh=hs[i], sigma_ltd=sig[i],
                               ss_tb=np.nanmean(o["ss"][~inp["closed"]]), rop_tb=np.nanmean(o["rop"]),
                               eoq_tb=np.nanmean(o["eoq"][~inp["closed"]])))
            if keep_daily and lv == MAIN:
                daily.append(pd.DataFrame({"ma_chinh_sach": pol, "ngay": inp["ds"], "ma_sku": r.ma_sku, "nhap": o["nhap"],
                                           "nhu_cau": inp["dem"][i], "xuat": o["xuat"], "ton_cuoi": o["ton"],
                                           "dat_hang": o["dat"], "rop": o["rop"]}))
    return pd.DataFrame(res), pd.DataFrame(params), daily


def tong(res):
    g = res.groupby("ma_chinh_sach")
    t = pd.DataFrame({"fill_rate_pt": 100 * g.da_dap_ung.sum() / g.nhu_cau.sum(),
                      "ton_tb_trieu": g.gia_tri_ton_tb.sum() / 1e6,
                      "chi_phi_dat_luu_trieu": (g.chi_phi_dat.sum() + g.chi_phi_luu.sum()) / 1e6,
                      "loi_nhuan_mat_trieu": g.loi_nhuan_mat.sum() / 1e6})
    t["chi_phi_lien_quan_trieu"] = t.chi_phi_dat_luu_trieu + t.loi_nhuan_mat_trieu
    return t.round(2)


if __name__ == "__main__":
    # ---------------- Buoc 1: chon quy tac luong dat tren VALIDATION2 ----------------
    val = load_inputs("validation2")
    print(f"Buoc 1 - validation2: {len(val['sku'])} SKU x {len(val['ds'])} ngay ({val['ds'][0]} .. {val['ds'][-1]}), muc phuc vu {MAIN:.0%}")
    rows = []
    for rule in RULES:
        for pol in ["cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]:
            r, _, _ = run(val, "validation2", pol, rule, [MAIN])
            t = tong(r).iloc[0]
            rows.append(dict(quy_tac=rule, chinh_sach=pol, **t.to_dict()))
    sel = pd.DataFrame(rows).sort_values("chi_phi_lien_quan_trieu").reset_index(drop=True)
    best_rule, best_pol = sel.quy_tac.iloc[0], sel.chinh_sach.iloc[0]
    sel["duoc_chon"] = np.where(sel.index == 0, "✅", "")
    txt = ["# Chon quy tac luong dat (GD F, buoc 1: validation2)", "",
           f"Giai doan {val['ds'][0]} .. {val['ds'][-1]}, muc phuc vu {MAIN:.0%}. Tieu chi: chi phi lien quan = dat + luu + loi nhuan mat (thap nhat).",
           f"**Duoc chon: quy tac {best_rule}, chinh sach {best_pol}.** {GHI_NGUON}", "", sel.to_markdown(index=False)]
    with open("reports/ton_kho_chon_quy_tac.md", "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    print("\n".join(txt[3:]))

    # ---------------- Buoc 2: chay TEST voi quy tac da chon ----------------
    te = load_inputs("test")
    print(f"\nBuoc 2 - test: {len(te['ds'])} ngay ({te['ds'][0]} .. {te['ds'][-1]}), quy tac {best_rule}")
    res, params, daily = [], [], []
    sku = te["sku"]
    for i, r in enumerate(sku.itertuples()):            # hien trang: do tu du lieu
        k = kpis(te["dem"][i], te["closed"], r, te["obs"]["qty_in"][i], te["obs"]["qty_out"][i], te["obs"]["ton_cuoi_ngay"][i])
        res += [dict(ma_chinh_sach="hien_trang", muc_phuc_vu=lv, ma_sku=r.ma_sku, **k) for lv in LEVELS]
        daily.append(pd.DataFrame({"ma_chinh_sach": "hien_trang", "ngay": te["ds"], "ma_sku": r.ma_sku,
                                   "nhap": te["obs"]["qty_in"][i], "nhu_cau": te["dem"][i], "xuat": te["obs"]["qty_out"][i],
                                   "ton_cuoi": te["obs"]["ton_cuoi_ngay"][i], "dat_hang": np.nan, "rop": np.nan}))
    res = [pd.DataFrame(res)]
    for pol in ["cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"]:
        r_, p_, d_ = run(te, "test", pol, best_rule, LEVELS, keep_daily=True)
        res.append(r_); params.append(p_); daily += d_
        print(f"  xong {pol}")
    res, params, daily = pd.concat(res, ignore_index=True), pd.concat(params, ignore_index=True), pd.concat(daily, ignore_index=True)

    with closing(ket_noi()) as con:
        for t in ["mo_phong_ngay", "ket_qua_ton_kho", "tham_so_ton_kho", "chinh_sach"]:
            con.execute(f"DELETE FROM {t}")
        pd.DataFrame([dict(ma_chinh_sach=k, mo_ta=v[0], mo_hinh_du_bao=v[1], hieu_chinh_lech=v[2],
                           quy_tac_luong_dat=None if v[1] is None else best_rule) for k, v in POLICIES.items()]
                     ).to_sql("chinh_sach", con, if_exists="append", index=False)
        params.to_sql("tham_so_ton_kho", con, if_exists="append", index=False)
        res.to_sql("ket_qua_ton_kho", con, if_exists="append", index=False)
        daily.to_sql("mo_phong_ngay", con, if_exists="append", index=False, chunksize=20000)
        con.commit()
        bad = len(con.execute("PRAGMA foreign_key_check").fetchall())
    print(f"Da ghi CSDL (vi pham khoa ngoai: {bad})")

    v = doc("SELECT * FROM v_so_sanh_chinh_sach ORDER BY muc_phuc_vu, chi_phi_lien_quan_trieu")
    main = v[v.muc_phuc_vu == MAIN].drop(columns=["muc_phuc_vu", "mo_ta"])
    m = res[res.muc_phuc_vu == MAIN].merge(sku[["ma_sku", "xyz_train"]], on="ma_sku")
    grp = m.groupby(["xyz_train", "ma_chinh_sach"]).apply(lambda g: pd.Series({
        "fill_rate_pt": 100 * g.da_dap_ung.sum() / g.nhu_cau.sum(), "ton_tb_trieu": g.gia_tri_ton_tb.sum() / 1e6,
        "loi_nhuan_mat_trieu": g.loi_nhuan_mat.sum() / 1e6})).round(1).reset_index()
    sens = v[v.ma_chinh_sach != "hien_trang"][["ma_chinh_sach", "muc_phuc_vu", "fill_rate_pt", "ton_tb_trieu_vnd", "chi_phi_lien_quan_trieu"]]
    lines = ["# So sanh chinh sach ton kho (GD F, buoc 2: test)", "",
             f"12 thang test ({te['ds'][0]} .. {te['ds'][-1]}), {len(sku)} SKU, quy tac luong dat **{best_rule}** (chon tren validation2), "
             f"muc phuc vu chinh {MAIN:.0%}. {GHI_NGUON}",
             ("Hien trang: nguoi lap ke hoach trong du lieu biet truoc nhu cau ky vong (lech +-10%) -> doi thu manh hon thuc te." if NGUON_DL["la_mo_phong"] else "Hien trang: " + POLICIES["hien_trang"][0]), "",
             "## Toan kho (95%)", "", main.to_markdown(index=False), "",
             "## Theo nhom XYZ (95%)", "", grp.to_markdown(index=False), "",
             "## Do nhay theo muc phuc vu", "", sens.to_markdown(index=False)]
    with open("reports/ton_kho_so_sanh.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[5:]))
