"""GD E vong 4: rui ro, tu hieu chinh, cap nhat hang tuan, khoang du bao. Luat ghi TRUOC khi chay: docs/10 muc 9.5.
TEST GIU KIN (nguoi dung quyet dinh 31/10): khong chay, khong cham, khong mo phong ton kho tren test.
Moi buoc hoc tu sai so chi dung du lieu da co thuc te tai moc du bao (ngay <= moc): moc k chi hoc tu cac moc truoc.
Chay:
  python src/nang_cap_du_bao_v4.py --buoc rui_ro              bang rui ro dinh luong (du lieu den 30/09/2025)
  python src/nang_cap_du_bao_v4.py --buoc B3_chay lgb|prophet chay lai lgb_v3_AB / prophet_addi moi 7 ngay (lau)
  python src/nang_cap_du_bao_v4.py --buoc B1 | B2 | B3 | B4    theo thu tu trong luat
  python src/nang_cap_du_bao_v4.py --buoc bao_cao             -> reports/nang_cap_du_bao_v4.md
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, keep_awake, PRED_DIR, TRAIN_END  # noqa: E402

VAL = "validation2"
NGUONG_WMAPE, NGUONG_BIAS = 0.005, 0.01                  # nhu vong 3
N0, KEP = 500, (0.8, 1.25)                               # B1: co ve 1 theo so dong, kep he so
CANH_BAO, TRUOC, SAU, KEP_BAO = 4, 3, 10, (0.7, 3.0)     # B2: canh bao 4 ngay truoc; cua so [vao-3, vao-1], [vao, vao+10]
MUC_KHOANG = {80: (0.10, 0.90), 95: (0.025, 0.975)}      # B4
NGUONG_PHU = 3.0                                          # B4: lech toi da (diem %) so voi muc danh nghia
STATE = "reports/nang_cap_du_bao_v4_trang_thai.json"
REPORT = "reports/nang_cap_du_bao_v4.md"
RUI_RO_MD, RUI_RO_CSV = "reports/rui_ro_du_bao.md", "reports/rui_ro_du_bao.csv"
V3_STATE = "reports/nang_cap_du_bao_trang_thai.json"     # cau hinh + trong so ghep cua ket_hop_v3


# ------------------------------------------------------------------ chung
TAM_DIR = f"{PRED_DIR}/v4"          # file trung gian (nap_database chi nap reports/du_bao/*.csv, khong nap thu muc con)


def doc_du_bao(ten, tap=VAL):
    f = f"{TAM_DIR}/{ten}_{tap}.csv"
    return pd.read_csv(f if os.path.exists(f) else f"{PRED_DIR}/{ten}_{tap}.csv", parse_dates=["date", "moc"])


def ghi_du_bao(p, ten, tap=VAL, cuoi=False):
    """cuoi=True: mo hinh dua vao he thong -> reports/du_bao/ (nap vao CSDL); con lai -> thu muc trung gian."""
    os.makedirs(TAM_DIR, exist_ok=True)
    p.to_csv(f"{PRED_DIR if cuoi else TAM_DIR}/{ten}_{tap}.csv", index=False, encoding="utf-8-sig")


def tam(ngay_thu):
    return pd.cut(ngay_thu, [0, 7, 14, 28], labels=["1-7", "8-14", "15-28"]).astype(str)


def chi_so(p):
    g = p.dropna(subset=["y_cham"])
    e = g.y_cham - g.du_bao
    return dict(WMAPE=float(e.abs().sum() / g.y_cham.sum()), Bias=float(e.sum() / g.y_cham.sum()), dong=int(len(g)))


def giu(moi, cu):
    """Luat docs/10 muc 9.5 (nhu vong 3): WMAPE giam >= 0,005 va |Bias| khong tang qua 0,01."""
    dw, db = cu["WMAPE"] - moi["WMAPE"], abs(moi["Bias"]) - abs(cu["Bias"])
    ok = dw >= NGUONG_WMAPE and db <= NGUONG_BIAS
    print(f"  -> WMAPE {cu['WMAPE']:.4f} -> {moi['WMAPE']:.4f} (giam {dw:+.4f}, can >= {NGUONG_WMAPE}); |Bias| "
          f"{abs(cu['Bias']):.4f} -> {abs(moi['Bias']):.4f} (tang {db:+.4f}, toi da {NGUONG_BIAS}): {'GIU' if ok else 'BO'}")
    return ok


def doc_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"phien_ban": "ket_hop_v3", "nhat_ky": []}


def luu_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


# ------------------------------------------------------------------ B1: tu hieu chinh lech (online)
def hieu_chinh_lech(p):
    """He so r = tong thuc te / tong du bao tren dong da co thuc te tai moc (moc truoc, ngay <= moc), theo XYZ x tam;
    co ve 1: r* = 1 + (r - 1) n / (n + N0); kep KEP. Moc dau: khong co du lieu -> he so 1."""
    p = p.copy()
    p["tam"] = tam(p.ngay_thu)
    p["he_so_b1"] = 1.0
    for o in sorted(p.moc.unique()):
        qk = p[(p.moc < o) & (p.date <= o) & p.y_cham.notna()]
        if qk.empty:
            continue
        g = qk.groupby(["xyz_train", "tam"]).agg(y=("y_cham", "sum"), f=("du_bao", "sum"), n=("y_cham", "size"))
        r = g.y / g.f.where(g.f > 0)
        rs = (1 + (r - 1) * g.n / (g.n + N0)).clip(*KEP).fillna(1.0).to_dict()
        m = p.moc == o
        p.loc[m, "he_so_b1"] = [rs.get((x, t), 1.0) for x, t in zip(p.loc[m, "xyz_train"], p.loc[m, "tam"])]
    p["du_bao"] = p.du_bao * p.he_so_b1
    return p.drop(columns="tam")


# ------------------------------------------------------------------ B2: canh bao bao ngan han
def bang_bao():
    s = pd.read_csv("data/reference/su_kien_dot_bien.csv", encoding="utf-8-sig")
    s = s[s.nhom_ly_do == "Thiên tai"].copy()
    s["vao"] = pd.to_datetime(s.tu_ngay)
    s["m"] = s.muc_do_0_1.astype(float)
    s["canh_bao"] = s.vao - pd.Timedelta(days=CANH_BAO)
    s["ket_thuc"] = s.vao + pd.Timedelta(days=SAU)
    return s[["su_kien", "vao", "m", "canh_bao", "ket_thuc"]].sort_values("vao").reset_index(drop=True)


GIAI_DOAN = [("truoc", -TRUOC, -1), ("sau", 0, SAU)]
SK_BIET_TRUOC = ["sk_tet", "sk_trung_thu", "sk_noel", "sk_halloween"]     # su kien lon mo hinh da co dac trung
NEN_TOI_THIEU = 1.0                                                       # don vi / ngay


def ngay_su_kien_lon(df):
    """Ngay nam trong cua so su kien biet truoc (co su kien ap cho ca lich): khong tach duoc tac dong rui ro khac."""
    c = [x for x in SK_BIET_TRUOC if x in df]
    return set(df.loc[df[c].sum(axis=1) > 0, "date"].unique())


def tac_dong_bao(df, bao):
    """Moi tran bao x giai doan x nhom hang: ti le tong thuc te / tong muc nen (TB 28 ngay truoc cua so, cung ma).
    Chi dung du lieu den TRAIN_END (khong cham vao giai doan test). Bo ngay trong cua so su kien biet truoc va ma co
    muc nen < NEN_TOI_THIEU (bo sung luat 31/10, docs/10 muc 9.5)."""
    lon = ngay_su_kien_lon(df)
    y = df.loc[(df.date <= TRAIN_END) & ~df.date.isin(lon), ["date", "ma_sku", "nhom_hang", "y_cau"]]
    rows = []
    for b in bao.itertuples():
        nen = y[(y.date >= b.vao - pd.Timedelta(days=TRUOC + 28)) & (y.date < b.vao - pd.Timedelta(days=TRUOC))] \
            .groupby("ma_sku").y_cau.mean()
        nen = nen[nen >= NEN_TOI_THIEU]
        for gd, a, z in GIAI_DOAN:
            w = y[(y.date >= b.vao + pd.Timedelta(days=a)) & (y.date <= b.vao + pd.Timedelta(days=z)) & y.y_cau.notna()]
            w = w.assign(nen=w.ma_sku.map(nen)).dropna(subset=["nen"])
            if w.empty:
                continue
            for nh, r in w.groupby("nhom_hang")[["y_cau", "nen"]].sum().iterrows():
                rows.append(dict(su_kien=b.su_kien, vao=b.vao, m=b.m, ket_thuc=b.ket_thuc, giai_doan=gd, nhom_hang=nh,
                                 ti_le=r.y_cau / r.nen if r.nen > 0 else np.nan, du_lieu_den=w.date.max(),
                                 cuoi_cua_so=b.vao + pd.Timedelta(days=z)))
    return pd.DataFrame(rows)


def canh_bao_bao(p, df):
    """Khi co canh bao (4 ngay truoc), nhan du bao cac ngay trong cua so voi u = 1 + beta m (beta theo nhom hang x giai
    doan, hoc tu cac tran bao da KET THUC truoc ngay canh bao: (ti_le - 1) = beta m, binh phuong nho nhat qua goc)."""
    bao = bang_bao()
    td = tac_dong_bao(df, bao)
    nhom = df.drop_duplicates("ma_sku").set_index("ma_sku").nhom_hang
    p = p.copy()
    p["u_bao"] = 1.0
    nh = p.ma_sku.map(nhom)
    hoc = []
    for b in bao.itertuples():
        # tran da ket thuc truoc ngay canh bao, va du lieu phu toi cuoi cua so cua chinh giai doan do
        # (sua loi lan chay dau: so voi ngay ket thuc sau bao -> giai doan "truoc" bi loai het)
        qk = td[(td.ket_thuc < b.canh_bao) & (td.du_lieu_den >= td.cuoi_cua_so - pd.Timedelta(days=2))].dropna(subset=["ti_le"])
        if qk.empty:
            continue
        for gd, a, z in GIAI_DOAN:
            q = qk[qk.giai_doan == gd]
            s = q.assign(tu=q.m * (q.ti_le - 1), mau=q.m ** 2).groupby("nhom_hang")[["tu", "mau"]].sum()
            u = (1 + s.tu / s.mau * b.m).clip(*KEP_BAO)
            m = (p.date >= b.vao + pd.Timedelta(days=a)) & (p.date <= b.vao + pd.Timedelta(days=z))
            if m.any():
                p.loc[m, "u_bao"] = nh[m].map(u).fillna(1.0).values          # bao sau (canh bao moi hon) ghi de bao truoc
                hoc.append(dict(su_kien=b.su_kien, giai_doan=gd, hoc_tu=", ".join(sorted(qk.su_kien.unique())),
                                u_tb=float(u.mean()), u_min=float(u.min()), u_max=float(u.max()), so_dong=int(m.sum())))
    p["du_bao"] = p.du_bao * p.u_bao
    return p, pd.DataFrame(hoc)


def cua_so_bao(p):
    m = pd.Series(False, index=p.index)
    for b in bang_bao().itertuples():
        m |= (p.date >= b.vao - pd.Timedelta(days=TRUOC)) & (p.date <= b.ket_thuc)
    return m


# ------------------------------------------------------------------ B3: cap nhat moi tuan
def chay_tuan(loai, tap=VAL):
    df = load()
    moc = folds(tap, step=7)
    print(f"{len(moc)} moc moi 7 ngay ({moc[0].date()} .. {moc[-1].date()})", flush=True)
    if loai == "lgb":
        import nang_cap_du_bao as N
        cats = {c: sorted(df[c].dropna().unique()) for c in N.CAT}
        sk_cols = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
        cfg = json.load(open(V3_STATE, encoding="utf-8"))["cfg"]
        p = backtest(N.make_model(cfg, cats, sk_cols, N.lich_su_kien(df.date.unique())), df, moc, name="lgb_v3_AB_tuan")
        ten, cu_ten = "lgb_v3_AB_tuan", "lgb_v3_AB"
    elif loai == "moc":
        import mo_hinh_baseline as M
        M.ACTIVE = ["tb_truot_28"]
        p = backtest(M.model_fn("tb_truot_28"), df, moc, name="tb_truot_28_tuan")
        ten, cu_ten = "tb_truot_28_tuan", "tb_truot_28"
    else:
        from concurrent.futures import ProcessPoolExecutor
        import mo_hinh_prophet as P
        P._quiet()
        with ProcessPoolExecutor(max_workers=P.WORKERS, initializer=P._quiet) as pool:
            p = backtest(P.make_model("additive", pool, P.holidays_table()), df, moc, name="prophet_addi_tuan")
        ten, cu_ten = "prophet_addi_tuan", "prophet_addi" if tap == VAL else "prophet"   # Prophet test cua v3 = additive
    ghi_du_bao(p, ten, tap)
    # tai lap: cac moc trung voi moc 28 ngay phai cho dung du bao cu
    cu = doc_du_bao(cu_ten, tap)
    x = cu.merge(p, on=["date", "ma_sku", "moc"], suffixes=("_cu", "_moi"))
    lech = (x.du_bao_cu - x.du_bao_moi).abs().max()
    print(f"Tai lap tren {x.moc.nunique()} moc trung voi moc 28 ngay ({len(x):,} dong): lech toi da {lech:.2e}")


def ban_moi_nhat(p):
    """Moi ngay dung du bao cua moc moi nhat truoc no (ngay_thu nho nhat)."""
    return p.sort_values("ngay_thu").drop_duplicates(["date", "ma_sku"]).sort_values(["moc", "ma_sku", "date"])


def mo_phong_validation2(du_bao, buoc):
    """Mo phong ton kho validation2: AI + hieu chinh lech, EOQ, 95%, giu nguyen he so hieu chinh va sigma cua v3."""
    import ton_kho as T
    from scipy.stats import norm
    if not hasattr(mo_phong_validation2, "_inp"):
        inp = T.load_inputs(VAL)
        mo_phong_validation2._inp = (inp, *T.validation_stats(T.AI, inp["sku"], 1))
    inp, hs, sig = mo_phong_validation2._inp
    sku = inp["sku"]
    moc = sorted(du_bao.moc.unique())
    assert pd.Timestamp(moc[0]) == inp["origin0"], "moc dau khong khop"
    F = np.zeros((len(sku), len(moc), 28))
    i_sku = {s: i for i, s in enumerate(sku.ma_sku)}
    i_moc = {m: k for k, m in enumerate(moc)}
    F[du_bao.ma_sku.map(i_sku).values, du_bao.moc.map(i_moc).values, du_bao.ngay_thu.values - 1] = du_bao.du_bao.values
    F = F * hs[:, None, None]
    res = []
    for i, r in enumerate(sku.itertuples()):
        o = T.simulate(F[i], sig[i], norm.ppf(0.95), inp["dem"][i], inp["LT"][i], inp["closed"], inp["init"][i],
                       inp["pipe0"][i], r.chi_phi_dat_hang, r.ty_le_chi_phi_luu_kho * r.gia_von, r.moq, r.lead_time_tb,
                       r.lead_time_std, "eoq", buoc=buoc)
        res.append(dict(ma_chinh_sach="x", **T.kpis(inp["dem"][i], inp["closed"], r, o["nhap"], o["xuat"], o["ton"])))
    return T.tong(pd.DataFrame(res)).iloc[0].to_dict()


# ------------------------------------------------------------------ B4: khoang du bao (online)
def _phan_vi(cal, lo, hi):
    a = cal[cal.f >= 1]
    b = cal[cal.f < 1]
    r = (a.y / a.f)
    return (r.quantile(lo), r.quantile(hi), b.y.quantile(lo) if len(b) else 0.0, b.y.quantile(hi) if len(b) else 0.0)


def khoang_online(x, nhom_cols, moc_cot="moc", den_cot="den"):
    """x: cot y, f, moc, den (ngay cuoi cua gia tri) + nhom_cols. Moc o dung phan vi tu dong co moc < o va den <= o."""
    x = x.copy()
    for muc in MUC_KHOANG:
        x[f"lo{muc}"], x[f"hi{muc}"] = np.nan, np.nan
    for o in sorted(x[moc_cot].unique()):
        cal_all = x[(x[moc_cot] < o) & (x[den_cot] <= o) & x.y.notna()]
        if cal_all.empty:
            continue
        m_o = x[moc_cot] == o
        for key, idx in x[m_o].groupby(nhom_cols).groups.items():
            key = key if isinstance(key, tuple) else (key,)
            cal = cal_all
            for c, v in zip(nhom_cols, key):
                cal = cal[cal[c] == v]
            if len(cal) < 50:
                continue
            f = x.loc[idx, "f"]
            for muc, (lo, hi) in MUC_KHOANG.items():
                rlo, rhi, alo, ahi = _phan_vi(cal, lo, hi)
                x.loc[idx, f"lo{muc}"] = np.where(f >= 1, f * rlo, alo)
                x.loc[idx, f"hi{muc}"] = np.where(f >= 1, f * rhi, ahi)
    return x


def danh_gia_khoang(x, tu_moc):
    e = x[(x.moc >= tu_moc) & x.y.notna() & x.lo80.notna()]
    out = {}
    for muc in MUC_KHOANG:
        trong = (e.y >= e[f"lo{muc}"]) & (e.y <= e[f"hi{muc}"])
        do_rong = ((e[f"hi{muc}"] - e[f"lo{muc}"]) / e.f.clip(lower=1)).median()
        out[muc] = dict(phu=float(100 * trong.mean()), do_rong_trung_vi=float(do_rong), dong=int(len(e)),
                        theo_nhom={g: float(100 * t.mean()) for g, t in trong.groupby(e.xyz_train)})
    return out


def tong_lead_time(p):
    """Tong du bao / thuc te trong L ngay dau cua moi moc, tung ma (chi cong ngay duoc cham, can >= L/2 ngay)."""
    lt = pd.read_csv("data/reference/sku_master.csv", encoding="utf-8-sig").set_index("ma_sku").lead_time_tb.round().clip(lower=1)
    q = p[p.ngay_thu <= p.ma_sku.map(lt)]
    s = q.dropna(subset=["y_cham"]).groupby(["moc", "ma_sku", "xyz_train"]).agg(
        y=("y_cham", "sum"), f=("du_bao", "sum"), n=("y_cham", "size"), den=("date", "max")).reset_index()
    s = s[s.n >= s.ma_sku.map(lt) / 2]
    return s


# ------------------------------------------------------------------ san sai so (doi chieu, khong dua vao mo hinh)
def san_sai_so(p):
    """E|D - mu| / E[D] voi D ~ nhi thuc am (mu, (cv mu)^2 + mu) nhu bo sinh du lieu; mu thay bang du bao (khong luu mu
    that). cv: tham so bo sinh (dm_sku.cv_nhu_cau_mp) - chi doi chieu."""
    from scipy.stats import nbinom
    from csdl import doc
    cv = doc("SELECT ma_sku, cv_nhu_cau_mp cv FROM dm_sku").set_index("ma_sku").cv
    g = p.dropna(subset=["y_cham"])
    mu = g.du_bao.clip(lower=0.05).round(1)
    c = g.ma_sku.map(cv).round(3)
    bang = pd.DataFrame({"mu": mu, "cv": c}).drop_duplicates()

    def ea(m, k):
        var = (k * max(m, 0.05)) ** 2 + m
        pp = min(max(m / var, 1e-3), 0.999)
        n = max(m * pp / (1 - pp), 0.3)
        x = np.arange(0, int(m + 12 * np.sqrt(var)) + 5)
        return float((np.abs(x - m) * nbinom.pmf(x, n, pp)).sum())
    bang["ea"] = [ea(m, k) for m, k in zip(bang.mu, bang.cv)]
    x = pd.DataFrame({"mu": mu, "cv": c, "xyz": g.xyz_train.values}).merge(bang, on=["mu", "cv"], how="left")
    return float(x.ea.sum() / x.mu.sum()), (x.groupby("xyz").ea.sum() / x.groupby("xyz").mu.sum()).round(3).to_dict()


# ------------------------------------------------------------------ B5: bang rui ro dinh luong
KHONG_BIET_TRUOC = {"bao", "sk_nang_nong", "sk_ret_dam", "sk_dich_cum", "sk_sot_xuat_huyet", "sk_tin_don_gia"}
THEO_MA = {"khuyen_mai", "don_b2b"}                       # rui ro rieng tung ma (con lai: ap cho ca lich)
RUI_RO = [  # (ma, ten, cach nhan dien, biet truoc bao lau, he thong xu ly)
    ("bao", "Bão lũ", "cửa sổ 3 ngày trước – 10 ngày sau ngày bão vào", "3–5 ngày (bản tin bão)", "B2: cảnh báo bão ngắn hạn; tồn kho an toàn"),
    ("sk_nang_nong", "Nắng nóng", "cờ sự kiện của mã", "7–10 ngày (dự báo thời tiết)", "tồn kho an toàn; theo dõi"),
    ("sk_ret_dam", "Rét đậm", "cờ sự kiện của mã", "7–10 ngày", "tồn kho an toàn; theo dõi"),
    ("sk_dich_cum", "Dịch cúm", "cờ sự kiện của mã", "vài ngày (tin y tế)", "tồn kho an toàn"),
    ("sk_sot_xuat_huyet", "Sốt xuất huyết", "cờ sự kiện của mã", "vài ngày", "tồn kho an toàn"),
    ("sk_tin_don_gia", "Tin đồn tăng giá", "cờ sự kiện của mã", "không biết trước", "tồn kho an toàn; khoảng dự báo"),
    ("sk_the_thao", "Giải thể thao lớn", "cờ sự kiện của mã", "hàng tháng (lịch thi đấu)", "đặc trưng biết trước của mô hình"),
    ("sk_tet", "Tết Nguyên đán", "cờ sự kiện của mã", "cả năm (âm lịch)", "đặc trưng biết trước + âm lịch (vòng 3)"),
    ("khuyen_mai", "Khuyến mãi của mã", "lịch khuyến mãi", "theo lịch bộ phận bán hàng gửi", "đặc trưng biết trước"),
    ("don_b2b", "Đơn B2B đột biến", "đơn lớn 1–2 ngày", "không biết trước", "không chấm vào dự báo; xử lý bằng đơn riêng"),
]


def rui_ro(df):
    d = df[df.date <= TRAIN_END].sort_values(["ma_sku", "date"]).copy()
    nam = (d.date.max() - d.date.min()).days / 365.25
    g = d.groupby("ma_sku")
    d["nen"] = g.y_cau.transform(lambda s: s.shift(1).rolling(28, min_periods=14).mean())
    d["nen_b2b"] = g.y.transform(lambda s: s.shift(1).rolling(28, min_periods=14).mean())
    bao = bang_bao()
    d["bao"] = 0
    for b in bao[bao.vao <= TRAIN_END].itertuples():
        d.loc[(d.date >= b.vao - pd.Timedelta(days=TRUOC)) & (d.date <= b.ket_thuc), "bao"] = 1
    lon = ngay_su_kien_lon(d)
    rows = []
    for ma, ten, cach, biet, xu_ly in RUI_RO:
        if ma not in d or not (d[ma] > 0).any():
            continue
        co_goc = d[ma] > 0
        # so dot: rui ro theo lich -> dem cum ngay lien tiep tren lich; rui ro theo ma -> dem dot cua tung ma / (so ma x nam)
        ngay_lich = d.loc[co_goc, "date"].drop_duplicates().sort_values()
        if ma in THEO_MA:
            xx = d.assign(co=co_goc)
            n_dot = int((xx.co & ~xx.groupby("ma_sku").co.shift(1, fill_value=False)).sum())
            so_dot = n_dot / nam if ma == "don_b2b" else n_dot / (d.ma_sku.nunique() * nam)
        else:
            so_dot = int((ngay_lich.diff().dt.days.fillna(99) > 1).sum()) / nam
        trung = 100 * ngay_lich.isin(lon).mean() if ma in KHONG_BIET_TRUOC else np.nan
        # tac dong: rui ro khong biet truoc -> bo ngay trung su kien lon (khong tach duoc, vd bao Yagi trong mua Trung thu)
        co = co_goc & ~d.date.isin(lon) if ma in KHONG_BIET_TRUOC else co_goc
        x = d.assign(co=co)
        x["dot"] = (x.co & ~x.groupby("ma_sku").co.shift(1, fill_value=False)).groupby(x.ma_sku).cumsum()
        e = x[x.co]
        cot_y, cot_nen = ("y", "nen_b2b") if ma == "don_b2b" else ("y_cau", "nen")
        dot = e.groupby(["ma_sku", "dot"]).agg(y=(cot_y, "mean"), nen=(cot_nen, "first"), nhom=("nhom_hang", "first"),
                                               so_ngay=("date", "size"))           # muc nen tai ngay dau dot
        dot = dot[dot.nen >= NEN_TOI_THIEU].dropna(subset=["y"])
        dot["ti_le"] = dot.y / dot.nen
        nhom = dot.groupby("nhom").ti_le.agg(["median", "size"])
        nhom = nhom[nhom["size"] >= 3].sort_values("median", ascending=False)
        co_dl = len(dot) > 0
        rows.append(dict(
            rui_ro=ten, nhan_dien=cach, so_dot_moi_nam=round(so_dot, 1),
            so_ngay_tb_moi_dot=round(float(e.groupby(["ma_sku", "dot"]).size().mean()), 1) if co_dl else np.nan,
            pt_ngay_trung_su_kien_lon=round(trung, 0) if trung == trung else np.nan,
            so_ma_bi_anh_huong=int(dot.index.get_level_values(0).nunique()),
            tac_dong_trung_vi=round(float(dot.ti_le.median()), 2) if co_dl else np.nan,
            p10=round(float(dot.ti_le.quantile(0.1)), 2) if co_dl else np.nan,
            p90=round(float(dot.ti_le.quantile(0.9)), 2) if co_dl else np.nan,
            nhom_tang_manh=", ".join(f"{k} ×{v:.2f}" for k, v in nhom["median"].head(2).items()) if co_dl
            else "không tách được (trùng sự kiện lớn)",
            biet_truoc=biet, he_thong_xu_ly=xu_ly))
    # dut gay cung ung (lead time) va het hang (kiem duyet nhu cau)
    s = pd.read_csv("data/reference/su_kien_dot_bien.csv", encoding="utf-8-sig")
    dg = s[(s.nhom_ly_do == "Đứt gãy cung ứng") & (pd.to_datetime(s.tu_ngay) <= TRAIN_END)]
    them = dg.tac_dong_chinh.str.extract(r"\+(\d+)")[0].astype(float)
    so_ngay = (pd.to_datetime(dg.den_ngay) - pd.to_datetime(dg.tu_ngay)).dt.days + 1
    rows.append(dict(rui_ro="Đứt gãy cung ứng (nhà cung cấp chậm)", nhan_dien="bảng sự kiện đột biến",
                     so_dot_moi_nam=round(len(dg) / nam, 1), so_ngay_tb_moi_dot=round(float(so_ngay.mean()), 1),
                     so_ma_bi_anh_huong=int(d[d.nha_cung_cap.isin(dg.su_kien.str.extract(r"(NCC\d+)")[0])].ma_sku.nunique()),
                     tac_dong_trung_vi=np.nan, p10=np.nan, p90=np.nan,
                     nhom_tang_manh=f"lead time +{them.min():.0f}–{them.max():.0f} ngày",
                     biet_truoc="vài ngày (nhà cung cấp báo)", he_thong_xu_ly="thử độ nhạy lead time; cập nhật lead time vào công thức"))
    hh = d[d.la_ngay_nghi == 0]
    rows.append(dict(rui_ro="Hết hàng (số bán thấp hơn nhu cầu thật)", nhan_dien="cột hết hàng",
                     so_dot_moi_nam=np.nan, so_ngay_tb_moi_dot=np.nan, so_ma_bi_anh_huong=int(hh[hh.het_hang == 1].ma_sku.nunique()),
                     tac_dong_trung_vi=np.nan, p10=np.nan, p90=np.nan,
                     nhom_tang_manh=f"{100 * hh.het_hang.mean():.1f}% ngày-mã; " + ", ".join(
                         f"{k} {100 * v:.1f}%" for k, v in hh.groupby("xyz_train").het_hang.mean().items()),
                     biet_truoc="—", he_thong_xu_ly="bỏ khỏi huấn luyện và chấm điểm (không coi là nhu cầu)"))
    t = pd.DataFrame(rows)
    t.to_csv(RUI_RO_CSV, index=False, encoding="utf-8-sig")
    L = ["# Bảng rủi ro dự báo (định lượng từ dữ liệu)", "",
         f"Dữ liệu {d.date.min().date()} – {d.date.max().date()} ({nam:.1f} năm; KHÔNG dùng giai đoạn test). Dữ liệu mô phỏng.",
         "Tác động = số bán trung bình trong đợt / mức nền (TB 28 ngày trước đợt, cùng mã); 1,00 = không đổi; chỉ tính mã có "
         "mức nền ≥ 1 đơn vị/ngày; nhóm hàng cần ≥ 3 đợt-mã. Đơn B2B tính trên số xuất thực (kể cả đơn lớn). Khuyến mãi: số đợt "
         "trên mỗi mã mỗi năm; đơn B2B: số đơn của cả kho mỗi năm.",
         "Rủi ro không biết trước (bão, thời tiết, dịch, tin đồn): BỎ các ngày trùng cửa sổ Tết / Trung thu / Noel / Halloween khi "
         "tính tác động, vì không tách được (VD bão Yagi 04–17/09/2024 nằm trọn trong mùa Trung thu: đồ chơi tăng do Trung thu, "
         "không do bão). Cột % ngày trùng cho biết bao nhiêu phần bị bỏ.", "",
         t.rename(columns={"rui_ro": "Rủi ro", "nhan_dien": "Nhận diện", "so_dot_moi_nam": "Đợt / năm",
                           "so_ngay_tb_moi_dot": "Ngày / đợt", "pt_ngay_trung_su_kien_lon": "% ngày trùng Tết/Trung thu/Noel/Halloween",
                           "so_ma_bi_anh_huong": "Số mã", "tac_dong_trung_vi": "Tác động (trung vị)",
                           "p10": "p10", "p90": "p90", "nhom_tang_manh": "Nhóm chịu tác động mạnh nhất",
                           "biet_truoc": "Biết trước", "he_thong_xu_ly": "Hệ thống xử lý"}).to_markdown(index=False), ""]
    open(RUI_RO_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


# ------------------------------------------------------------------ bao cao
def bao_cao(st):
    pt = lambda v: f"{100 * v:.1f}%"
    L = ["# Nâng cấp dự báo vòng 4 (GĐ E): rủi ro, tự hiệu chỉnh, cập nhật hằng tuần, khoảng dự báo", "",
         "Luật ghi trước khi chạy: `docs/10` mục 9.5 (kèm bổ sung trước B2). Chọn và báo cáo trên **validation2**; "
         "**test giữ kín** (không chạy, không chấm). Mọi bước học từ sai số chỉ dùng dữ liệu đã có thực tế tại mốc. "
         "Dữ liệu mô phỏng.", ""]
    v3 = st["B1"]["truoc"] if "B1" in st else None
    if "san" in st:
        san, san_g = st["san"]
        L += ["## Mức sai số tối thiểu (đối chiếu)", "",
              f"Nếu biết đúng nhu cầu kỳ vọng từng ngày, WMAPE theo ngày vẫn còn khoảng **{san:.3f}** "
              f"(X {san_g.get('X')} · Y {san_g.get('Y')} · Z {san_g.get('Z')}) do nhu cầu ngẫu nhiên (nhị thức âm). "
              f"Phiên bản cuối: **{st['cuoi']['WMAPE']:.3f}**.", ""]
    L += ["## Kết quả từng bước (validation2)", "", "| Bước | WMAPE | Bias | So với phiên bản đang giữ | Theo luật |", "|---|---|---|---|---|"]
    if v3:
        L.append(f"| Đang giữ: `ket_hop_v3` | {v3['WMAPE']:.4f} | {pt(v3['Bias'])} | | |")
    ten = {"B1": "B1 – tự hiệu chỉnh lệch từ sai số đã qua", "B2": "B2 – cảnh báo bão 4 ngày trước",
           "B3": "B3 – cập nhật dự báo mỗi tuần (bản mới nhất mỗi ngày)"}
    for k in ["B1", "B2", "B3"]:
        if k in st:
            x = st[k]
            L.append(f"| {ten[k]} | {x['WMAPE']:.4f} | {pt(x['Bias'])} | {x['truoc']['WMAPE']:.4f} / {pt(x['truoc']['Bias'])} "
                     f"({x['truoc']['dong']:,} dòng) | {'✅ giữ' if x['giu'] else '❌ bỏ'} |")
    if "B2" in st:
        c = st["B2"]["cua_so_bao"]
        L += ["", f"Riêng cửa sổ bão (B2): WMAPE {c['truoc']['WMAPE']:.3f} → {c['sau']['WMAPE']:.3f}, Bias {pt(c['truoc']['Bias'])} → "
              f"{pt(c['sau']['Bias'])}. Hệ số học được theo nhóm hàng dao động rộng (xem `hoc` trong file trạng thái): "
              "1–2 trận bão là quá ít để học hệ số ổn định."]
    if "B3" in st:
        t = st["B3"]["ton_kho"]
        L += ["", "**Tồn kho validation2** (AI + hiệu chỉnh, EOQ, 95%; giữ hệ số hiệu chỉnh và σ của v3):", "",
              "| Dự báo | Fill Rate | Tồn TB (tr đ) | CP đặt + lưu | LN mất | CP liên quan |", "|---|---|---|---|---|---|"]
        for k, n in [("v3", "v3, mỗi 28 ngày"), ("moi_28_ngay", "đang giữ, mỗi 28 ngày"), ("moi_tuan", "cập nhật mỗi tuần")]:
            r = t[k]
            L.append(f"| {n} | {r['fill_rate_pt']:.2f}% | {r['ton_tb_trieu']:,.1f} | {r['chi_phi_dat_luu_trieu']:,.1f} | "
                     f"{r['loi_nhuan_mat_trieu']:,.1f} | {r['chi_phi_lien_quan_trieu']:,.1f} |")
    if "B4" in st:
        b = st["B4"]
        L += ["", f"## B4 – Khoảng dự báo (tính từ mốc {b['tu_moc']}, chỉ học từ mốc trước)", "",
              "| Mức | Theo ngày: tỉ lệ thực tế nằm trong khoảng | Độ rộng (trung vị, × dự báo) | Tổng lead time: tỉ lệ nằm trong khoảng | Độ rộng |",
              "|---|---|---|---|---|"]
        for m in ["80", "95"]:
            a, c = b["theo_ngay"][m], b["lead_time"][m]
            L.append(f"| {m}% | {a['phu']:.1f}% (X {a['theo_nhom'].get('X', 0):.0f} · Y {a['theo_nhom'].get('Y', 0):.0f} · "
                     f"Z {a['theo_nhom'].get('Z', 0):.0f}) | {a['do_rong_trung_vi']:.2f} | {c['phu']:.1f}% | {c['do_rong_trung_vi']:.2f} |")
        L += ["", f"Theo luật (lệch ≤ ±{NGUONG_PHU:.0f} điểm so với danh nghĩa): **{'đạt' if b['dat'] else 'không đạt'}**."]
    if os.path.exists(f"{TAM_DIR}/v4_khoang_{VAL}.csv"):
        L += ["", "## Ví dụ: con số dự báo kèm khoảng (validation2, sữa tươi Vinamilk SKU009, 7 ngày sau mốc 20/01/2025, trước Tết)", "",
              "| Ngày | Dự báo | Khoảng 80% | Khoảng 95% | Thực tế | Trong khoảng 80% |", "|---|---|---|---|---|---|"]
        k = doc_du_bao("v4_khoang")
        k = k[(k.ma_sku == "SKU009") & (k.moc == pd.Timestamp("2025-01-20"))].sort_values("date")
        for r in k.itertuples():
            thuc = "—" if pd.isna(r.y_cham) else f"{r.y_cham:,.0f}"
            trong = "—" if pd.isna(r.y_cham) or pd.isna(r.lo80) else ("✓" if r.lo80 <= r.y_cham <= r.hi80 else "✗")
            L.append(f"| {r.date:%d/%m} | {r.du_bao:,.0f} | {r.lo80:,.0f}–{r.hi80:,.0f} | {r.lo95:,.0f}–{r.hi95:,.0f} | {thuc} | {trong} |")
        lt = pd.read_csv(f"{TAM_DIR}/v4_khoang_lead_time_{VAL}.csv", parse_dates=["moc"])
        x = lt[(lt.ma_sku == "SKU009") & (lt.moc == pd.Timestamp("2025-01-20"))]
        if len(x):
            x = x.iloc[0]
            L += ["", f"Tổng nhu cầu trong thời gian chờ hàng ({int(x.n)} ngày): dự báo **{x.f:,.0f}**, khoảng 80% "
                  f"{x.lo80:,.0f}–{x.hi80:,.0f}, khoảng 95% {x.lo95:,.0f}–{x.hi95:,.0f}; thực tế **{x.y:,.0f}**."]
    if "test" in st:
        t = st["test"]
        c, k = t["test_cung_dong"], t["khoang"]
        L += ["", "## Test (mở 31/10 theo quyết định người dùng; chạy một lần, chỉ báo cáo — luật `docs/10` mục 9.6)", "",
              "| Test | WMAPE | Bias | WMAPE tuần | Nhóm Z | Nhóm X | WMAPE lead time |", "|---|---|---|---|---|---|---|",
              f"| `ket_hop_v4` (cập nhật mỗi tuần, bản mới nhất) | **{t['test']['v4']['WMAPE']:.4f}** | {pt(t['test']['v4']['Bias'])} | "
              f"{t['test']['v4']['tuan']:.4f} | {t['test']['v4']['Z']:.4f} | {t['test']['v4']['X']:.4f} | {t['test']['v4']['lead_time']:.4f} |",
              f"| `ket_hop_v3` (mỗi 28 ngày), cùng các dòng | {c['v3']['WMAPE']:.4f} | {pt(c['v3']['Bias'])} | | | | {c['v3_lead_time']:.4f} |",
              f"| Mốc TB trượt 28 ngày, cập nhật mỗi tuần | {t['test']['moc_tuan']['WMAPE']:.4f} | {pt(t['test']['moc_tuan']['Bias'])} | | | | |",
              "", f"Khoảng dự báo trên test (học online từ validation2 rồi các mốc test trước; tính từ mốc {k['tu_moc']}):", "",
              "| Mức | Theo ngày (bản mới nhất) | Độ rộng | Tổng lead time | Độ rộng |", "|---|---|---|---|---|"]
        for m in ["80", "95"]:
            a, b2 = k["theo_ngay"][m], k["lead_time"][m]
            L.append(f"| {m}% | {a['phu']:.1f}% | {a['do_rong_trung_vi']:.2f} | {b2['phu']:.1f}% | {b2['do_rong_trung_vi']:.2f} |")
    L += ["", "## Bảng rủi ro", "", f"Xem `{RUI_RO_MD}` (định lượng từ dữ liệu đến 30/09/2025).", "",
          "## Nhật ký", ""] + [f"- {x}" for x in st["nhat_ky"]] + [
        "", "B2 chạy 2 lần: lần đầu có lỗi code (điều kiện \"dữ liệu phủ hết cửa sổ\" so với ngày kết thúc SAU bão nên giai "
        "đoạn \"trước bão\" không được học, hệ số = 1); lần 2 sau khi sửa. Kết luận như nhau: bỏ (WMAPE 0,3820 rồi 0,3836)."]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


# ------------------------------------------------------------------ chay
if __name__ == "__main__":
    buoc = sys.argv[sys.argv.index("--buoc") + 1] if "--buoc" in sys.argv else None
    keep_awake(True)
    st = doc_state()
    if buoc == "rui_ro":
        rui_ro(load())
        sys.exit()
    if buoc == "B3_chay":
        chay_tuan(sys.argv[sys.argv.index("B3_chay") + 1], sys.argv[sys.argv.index("--tap") + 1] if "--tap" in sys.argv else VAL)
        sys.exit()
    df = load()
    cur = doc_du_bao(st["phien_ban"])
    if buoc == "B1":
        cu = chi_so(cur)
        moi = hieu_chinh_lech(cur)
        r = chi_so(moi)
        print(f"B1 tu hieu chinh lech: WMAPE {r['WMAPE']:.4f} Bias {r['Bias']:+.4f} (dang giu {st['phien_ban']}: "
              f"{cu['WMAPE']:.4f} / {cu['Bias']:+.4f})")
        print(moi.groupby([moi.xyz_train, tam(moi.ngay_thu)]).he_so_b1.agg(["min", "median", "max"]).round(3).to_string())
        ok = giu(r, cu)
        st["B1"] = dict(giu=ok, WMAPE=r["WMAPE"], Bias=r["Bias"], truoc=cu)
        if ok:
            ghi_du_bao(moi, "v4_B1")
            st["phien_ban"] = "v4_B1"
    elif buoc == "B2":
        cu = chi_so(cur)
        moi, hoc = canh_bao_bao(cur, df)
        r = chi_so(moi)
        w0, w1 = chi_so(cur[cua_so_bao(cur)]), chi_so(moi[cua_so_bao(moi)])
        print(f"B2 canh bao bao: WMAPE {r['WMAPE']:.4f} Bias {r['Bias']:+.4f} (dang giu {st['phien_ban']}: {cu['WMAPE']:.4f} / "
              f"{cu['Bias']:+.4f}); rieng cua so bao: {w0['WMAPE']:.4f} / {w0['Bias']:+.4f} -> {w1['WMAPE']:.4f} / {w1['Bias']:+.4f}")
        print(hoc.round(3).to_string(index=False))
        ok = giu(r, cu)
        st["B2"] = dict(giu=ok, WMAPE=r["WMAPE"], Bias=r["Bias"], truoc=cu, cua_so_bao=dict(truoc=w0, sau=w1),
                        hoc=hoc.round(3).to_dict("records"))
        if ok:
            ghi_du_bao(moi, "v4_B2")
            st["phien_ban"] = "v4_B2"
    elif buoc == "B3":
        import nang_cap_du_bao as N
        w = json.load(open(V3_STATE, encoding="utf-8"))["w"]
        b = N.blend(doc_du_bao("prophet_addi_tuan"), doc_du_bao("lgb_v3_AB_tuan"), w)
        if st.get("B1", {}).get("giu"):
            b = hieu_chinh_lech(b)
        if st.get("B2", {}).get("giu"):
            b, _ = canh_bao_bao(b, df)
        ghi_du_bao(b, "v4_tuan_day_du")
        tuan = ban_moi_nhat(b)
        chung = cur[["date", "ma_sku"]].merge(tuan[["date", "ma_sku"]], on=["date", "ma_sku"])
        cu = chi_so(cur.merge(chung, on=["date", "ma_sku"]))
        r = chi_so(tuan.merge(chung, on=["date", "ma_sku"]))
        print(f"B3 cap nhat moi tuan (ban moi nhat cho moi ngay): WMAPE {r['WMAPE']:.4f} Bias {r['Bias']:+.4f} | moi 28 ngay "
              f"({st['phien_ban']}): {cu['WMAPE']:.4f} / {cu['Bias']:+.4f} ({cu['dong']:,} dong chung)")
        ok = giu(r, cu)
        v3 = doc_du_bao("ket_hop_v3")
        kq_v3 = mo_phong_validation2(v3, 28)
        kq_cu = mo_phong_validation2(cur, 28) if st["phien_ban"] != "ket_hop_v3" else kq_v3
        kq_tuan = mo_phong_validation2(b, 7)
        print(f"Ton kho validation2 (AI + hieu chinh, EOQ, 95%): v3 {kq_v3} | {st['phien_ban']} {kq_cu} | moi tuan {kq_tuan}")
        st["B3"] = dict(giu=ok, WMAPE=r["WMAPE"], Bias=r["Bias"], truoc=cu, ton_kho=dict(v3=kq_v3, moi_28_ngay=kq_cu, moi_tuan=kq_tuan))
        if ok:
            ghi_du_bao(tuan, "v4_B3")
            st["phien_ban"] = "v4_B3"
            st["day_du"] = "v4_tuan_day_du"
    elif buoc == "B4":
        x = cur.rename(columns={"y_cham": "y", "du_bao": "f"}).assign(den=lambda q: q.date, tam=lambda q: tam(q.ngay_thu))
        moc = sorted(x.moc.unique())
        tu = moc[2] if st["phien_ban"] != "v4_B3" else moc[min(8, len(moc) - 1)]   # moc thu 3 (28 ngay) ~ 8 tuan
        kn = khoang_online(x, ["xyz_train", "tam"])
        dg_ngay = danh_gia_khoang(kn, tu)
        full = doc_du_bao(st.get("day_du", st["phien_ban"]))
        lt = tong_lead_time(full)
        kl = khoang_online(lt, ["xyz_train"])
        dg_lt = danh_gia_khoang(kl, tu)
        dat = all(abs(v["phu"] - m) <= NGUONG_PHU for d_ in (dg_ngay, dg_lt) for m, v in d_.items())
        for ten, d_ in [("theo ngay", dg_ngay), ("tong lead time", dg_lt)]:
            for m, v in d_.items():
                print(f"B4 {ten} {m}%: phu {v['phu']:.1f}% (danh nghia {m}%), do rong trung vi {v['do_rong_trung_vi']:.2f} x du bao, "
                      f"{v['dong']:,} dong; theo nhom {({k: round(z, 1) for k, z in v['theo_nhom'].items()})}")
        print(f"  -> {'DAT' if dat else 'KHONG DAT'} (lech toi da {NGUONG_PHU} diem)")
        out = cur.merge(kn[["date", "ma_sku", "moc", "lo80", "hi80", "lo95", "hi95"]], on=["date", "ma_sku", "moc"], how="left")
        ghi_du_bao(out, "v4_khoang")
        kl.to_csv(f"{TAM_DIR}/v4_khoang_lead_time_{VAL}.csv", index=False, encoding="utf-8-sig")
        st["B4"] = dict(dat=dat, tu_moc=str(pd.Timestamp(tu).date()), theo_ngay=dg_ngay, lead_time=dg_lt)
        st["san"] = san_sai_so(cur)
        st["cuoi"] = chi_so(cur)
    elif buoc == "test":                          # luat docs/10 muc 9.6: chay MOT lan, chi bao cao
        import nang_cap_du_bao as N
        from danh_gia import save_results
        assert "test" not in st, "test da chay (luat 9.6: chi chay mot lan)"
        w = json.load(open(V3_STATE, encoding="utf-8"))["w"]
        ful = {t: N.blend(doc_du_bao("prophet_addi_tuan", t), doc_du_bao("lgb_v3_AB_tuan", t), w) for t in (VAL, "test")}
        moc_t0 = pd.Timestamp(ful["test"].moc.min())
        # khoang du bao: hoc online qua cac moc validation2 roi test (moc k chi hoc tu dong da co thuc te tai moc)
        x = pd.concat([ful[VAL].assign(tap=VAL), ful["test"].assign(tap="test")], ignore_index=True)
        x = x.rename(columns={"y_cham": "y", "du_bao": "f"}).assign(den=lambda q: q.date, tam=lambda q: tam(q.ngay_thu))
        kn = khoang_online(x, ["xyz_train", "tam"])
        dg_ngay = danh_gia_khoang(ban_moi_nhat(kn[kn.tap == "test"]), moc_t0)
        lt = tong_lead_time(pd.concat([ful[VAL], ful["test"]], ignore_index=True))
        dg_lt = danh_gia_khoang(khoang_online(lt, ["xyz_train"]), moc_t0)
        kn = kn.rename(columns={"y": "y_cham", "f": "du_bao", "lo80": "thap_80", "hi80": "cao_80", "lo95": "thap_95",
                                "hi95": "cao_95"}).drop(columns=["den", "tam"])
        cot = ["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]
        ghi_chu = f"Cap nhat moi 7 ngay (docs/10 muc 9.6): lgb_v3_AB + Prophet additive, w LightGBM = {w}; cham tren ban moi nhat moi ngay"
        ket = {}
        for t in (VAL, "test"):
            moi = kn[kn.tap == t].drop(columns="tap")
            mm = doc_du_bao("tb_truot_28_tuan", t)
            # bang ket qua: cham tren ban moi nhat moi ngay (cach dung that); CSV / CSDL: du moi moc tuan (+ cot khoang)
            r = save_results("ket_hop_v4", ban_moi_nhat(moi)[cot], df, t, ghi_chu).iloc[0]
            rm = save_results("tb_truot_28_tuan", ban_moi_nhat(mm)[cot], df, t,
                              "TB 28 ngay gan nhat, cap nhat moi 7 ngay (docs/10 muc 9.6); cham tren ban moi nhat").iloc[0]
            ghi_du_bao(moi, "ket_hop_v4", t, cuoi=True)
            ghi_du_bao(mm, "tb_truot_28_tuan", t, cuoi=True)
            ket[t] = dict(v4=dict(WMAPE=float(r.WMAPE), Bias=float(r.Bias_pct), tuan=float(r.WMAPE_tuan), Z=float(r.WMAPE_Z),
                                  X=float(r.WMAPE_X), lead_time=float(N.wmape_lead_time(moi))),
                          moc_tuan=dict(WMAPE=float(rm.WMAPE), Bias=float(rm.Bias_pct)))
        # so voi ket_hop_v3 (moi 28 ngay) tren cung cac dong test
        lat = ban_moi_nhat(kn[kn.tap == "test"])
        v3 = doc_du_bao("ket_hop_v3", "test")
        k = lat[["date", "ma_sku"]].merge(v3[["date", "ma_sku"]], on=["date", "ma_sku"])
        a, b = chi_so(lat.merge(k, on=["date", "ma_sku"])), chi_so(v3.merge(k, on=["date", "ma_sku"]))
        ket["test_cung_dong"] = dict(v4=a, v3=b, v3_lead_time=float(N.wmape_lead_time(v3)))
        ket["khoang"] = dict(theo_ngay=dg_ngay, lead_time=dg_lt, tu_moc=str(moc_t0.date()))
        st["test"] = ket
        print(json.dumps(ket, ensure_ascii=False, indent=1, default=str))
    elif buoc == "bao_cao":
        bao_cao(st)
        sys.exit()
    else:
        sys.exit("Dung: --buoc rui_ro | B3_chay lgb|prophet | B1 | B2 | B3 | B4")
    st["nhat_ky"].append([buoc, st["phien_ban"]])
    luu_state(st)
    keep_awake(False)
