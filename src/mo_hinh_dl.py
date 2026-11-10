"""GD E vong 5: mo hinh hoc sau LSTM va RNN. Luat va cau hinh ghi TRUOC khi chay: docs/10 muc 9.7.
Mot mo hinh chung 121 SKU, ma hoa - giai ma: doc 56 ngay gan nhat -> du bao truc tiep 28 ngay toi.
Khong nhin truoc: nhu cau sau moc la NaN truoc khi tinh moi dac trung; thong tin tuong lai chi la cot biet truoc (KNOWN_AHEAD).
Chay theo thu tu:
  python src/mo_hinh_dl.py --buoc thu                          1 moc: kiem tra khong nhin truoc + do thoi gian
  python src/mo_hinh_dl.py --buoc chon_ham                     luat 1: Tweedie / L1, validation2 moc 28 ngay
  python src/mo_hinh_dl.py --buoc tuan --cell lstm|rnn         luat 2: validation2 moc 7 ngay
  python src/mo_hinh_dl.py --buoc ghep                         luat 3, 4: ghep voi ket_hop_v4, quyet dinh theo validation2
  python src/mo_hinh_dl.py --buoc tuan --cell lstm|rnn --tap test
  python src/mo_hinh_dl.py --buoc test                         luat 5: chi bao cao
  python src/mo_hinh_dl.py --buoc bao_cao                      -> reports/mo_hinh_dl.md
Ket qua: reports/ket_qua_mo_hinh.csv (lstm_tuan, rnn_tuan, ket_hop_v5); du bao du moi moc: reports/du_bao/dl/.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
from torch import nn

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, folds, backtest, save_results, keep_awake, PRED_DIR, HORIZON  # noqa: E402
import nang_cap_du_bao as N  # noqa: E402
from nang_cap_du_bao_v4 import ban_moi_nhat, chi_so, doc_du_bao, giu  # noqa: E402

VAL = "validation2"
CUA_SO, AN, LOP, DROPOUT = 56, 64, 2, 0.1
BATCH, MAU_MOI_LUOT = 512, 40_000
LUOT_DAU, LR_DAU, LUOT_TIEP, LR_TIEP = 30, 1e-3, 4, 5e-4
HAT_GIONG = [20261102, 20261103, 20261104]
TWEEDIE_P = 1.2
NGUONG_HAM = 0.005
GRID_W = np.round(np.arange(0, 1.01, 0.1), 1)
CAT = [("ma_sku", 8), ("nhom_hang", 4), ("loai_mua_vu", 2), ("abc_train", 2), ("xyz_train", 2), ("loai_nhu_cau", 2)]
CO = ["khuyen_mai", "la_ngay_nghi", "ngay_sale", "cua_so_sale", "trong_tuan_tet", "cuoi_tuan", "dau_thang", "cuoi_thang"]
THU_MUC = f"{PRED_DIR}/dl"
STATE = "reports/mo_hinh_dl_trang_thai.json"
REPORT = "reports/mo_hinh_dl.md"
TB = "cuda" if torch.cuda.is_available() else "cpu"


class DuLieu:
    """Mang (ma, ngay, dac trung). Phan co dinh chi dung cot biet truoc; nhu cau + gia tri tre tinh lai o tung moc tu lich su."""

    def __init__(self, df, ev=None):
        """ev: lich su kien (mac dinh tep tham chieu; du bao tuong lai truyen lich da mo rong)."""
        self.df = df
        self.skus = sorted(df.ma_sku.unique())
        self.ngay = pd.DatetimeIndex(sorted(df.date.unique()))
        assert len(self.ngay) == (self.ngay[-1] - self.ngay[0]).days + 1, "thieu ngay trong du lieu"
        self.i_sku = {m: i for i, m in enumerate(self.skus)}
        self.i_ngay = {d: i for i, d in enumerate(self.ngay)}
        d = df.sort_values(["ma_sku", "date"]).reset_index(drop=True)
        assert len(d) == len(self.skus) * len(self.ngay), "du lieu khong du moi cap (ma, ngay)"
        S, T = len(self.skus), len(self.ngay)
        hinh = lambda c: pd.to_numeric(d[c]).fillna(0).values.reshape(S, T, 1).astype(np.float32)
        sk_cols = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
        cot = [hinh(c) for c in CO + sk_cols]
        cot.append(np.clip(hinh("so_ngay_den_tet"), 0, 60) / 60)
        cot.append(np.clip(hinh("so_ngay_sau_tet"), 0, 14) / 14)
        gia = hinh("gia_ban")
        cot.append(np.log(np.maximum(gia, 1) / np.maximum(gia.mean(axis=1, keepdims=True), 1)))
        cot.append(np.log1p(hinh("lead_time_tb")) / 3)
        ca = lambda v: np.repeat(np.asarray(v, dtype=np.float32).reshape(1, T, -1), S, axis=0)
        cot.append(ca(np.eye(7, dtype=np.float32)[self.ngay.weekday]))
        for chu_ky, v in [(365.25, self.ngay.dayofyear), (12, self.ngay.month)]:
            cot.append(ca(np.c_[np.sin(2 * np.pi * v / chu_ky), np.cos(2 * np.pi * v / chu_ky)]))
        cal = N.lich_su_kien(df.date.unique(), ev).set_index("date").reindex(self.ngay)
        ev = [c for c in cal.columns if c.startswith(("den_", "sau_"))]
        cot.append(ca(cal[ev].values / np.array([N.CLIP_DEN if c.startswith("den_") else N.CLIP_SAU for c in ev])))
        self.dich_am = cal.dich_am_lich.values
        self.co_dinh = torch.from_numpy(np.concatenate(cot, axis=2)).to(TB)
        self.nghi = torch.from_numpy(hinh("la_ngay_nghi")[:, :, 0] > 0).to(TB)
        tinh = d.groupby("ma_sku")[[c for c, _ in CAT if c != "ma_sku"]].first().reindex(self.skus).reset_index()
        self.so_nhom = [(tinh[c].nunique(), k) for c, k in CAT]
        self.cat = torch.tensor(np.c_[[pd.Categorical(tinh[c]).codes for c, _ in CAT]].T, dtype=torch.long, device=TB)
        self.y = d.y_cham.values.reshape(S, T).astype(np.float32)

    def theo_moc(self, moc, y=None):
        """Tensor nhu cau + gia tri tre chi tu du lieu den ngay moc (ngay sau moc la NaN)."""
        o = self.i_ngay[moc]
        Y = (self.y if y is None else y).copy()
        Y[:, o + 1:] = np.nan
        co = ~np.isnan(Y)
        tl = np.maximum(np.nan_to_num(np.nanmean(Y, axis=1), nan=0.0), 0.1).astype(np.float32)
        Z = np.log1p(np.nan_to_num(Y) / tl[:, None]).astype(np.float32)
        S, T = Y.shape
        tre = np.zeros((S, T, 6), dtype=np.float32)
        tre[:, 364:, 0], tre[:, 364:, 1] = Z[:, :-364], co[:, :-364]
        Y7 = pd.DataFrame(Y.T).rolling(7, center=True, min_periods=4).mean().values.T          # TB 7 ngay quanh 1 ngay
        Z7, co7 = np.log1p(np.nan_to_num(Y7) / tl[:, None]).astype(np.float32), ~np.isnan(Y7)
        for t in np.flatnonzero(~np.isnan(self.dich_am)):
            g = t - int(self.dich_am[t])
            if g >= 0 and g + 3 <= o:                                                          # cung ngay am lich nam truoc, cua so da qua
                tre[:, t, 2], tre[:, t, 3], tre[:, t, 4], tre[:, t, 5] = Z[:, g], co[:, g], Z7[:, g], co7[:, g]
        return dict(o=o, Y=torch.from_numpy(np.nan_to_num(Y)).to(TB), co=torch.from_numpy(co).to(TB) & ~self.nghi,
                    tl=torch.from_numpy(tl).to(TB), Z=torch.from_numpy(Z).to(TB), tre=torch.from_numpy(tre).to(TB))


class MaHoaGiaiMa(nn.Module):
    def __init__(self, loai, so_dt, so_nhom):
        super().__init__()
        self.nhung = nn.ModuleList([nn.Embedding(n, k) for n, k in so_nhom])
        tinh = sum(k for _, k in so_nhom)
        O = {"lstm": nn.LSTM, "rnn": nn.RNN}[loai]
        self.ma_hoa = O(so_dt + 2 + tinh, AN, LOP, batch_first=True, dropout=DROPOUT)
        self.giai_ma = O(so_dt + 1 + tinh, AN, LOP, batch_first=True, dropout=DROPOUT)
        self.ra = nn.Linear(AN, 1)

    def forward(self, x_mh, x_gm, cat):
        t = torch.cat([e(cat[:, i]) for i, e in enumerate(self.nhung)], 1)
        ghep = lambda x: torch.cat([x, t[:, None].expand(-1, x.shape[1], -1)], 2)
        _, h = self.ma_hoa(ghep(x_mh))
        o, _ = self.giai_ma(ghep(x_gm), h)
        return self.ra(o).squeeze(2).clamp(-12, 8)                                             # log(nhu cau / trung binh cua ma)


def lay_lo(d, m, s, o):
    """Dau vao cua 1 lo: s (ma), o (ngay lam moc rieng cua mau)."""
    i_mh = o[:, None] + torch.arange(-CUA_SO + 1, 1, device=TB)
    i_gm = o[:, None] + torch.arange(1, HORIZON + 1, device=TB)
    ss = s[:, None]
    x_mh = torch.cat([d.co_dinh[ss, i_mh], m["tre"][ss, i_mh], m["Z"][ss, i_mh][:, :, None], m["co"][ss, i_mh][:, :, None].float()], 2)
    h = (torch.arange(1, HORIZON + 1, device=TB, dtype=torch.float32) / HORIZON)[None, :, None].expand(len(s), -1, -1)
    x_gm = torch.cat([d.co_dinh[ss, i_gm], m["tre"][ss, i_gm], h], 2)
    return x_mh, x_gm, d.cat[s], i_gm, ss


def hoc(mh, opt, d, m, ham, so_luot, lr):
    for g in opt.param_groups:
        g["lr"] = lr
    mh.train()
    S, o_max = len(d.skus), m["o"]
    tb_tl = m["tl"].mean()
    for _ in range(so_luot):
        for _ in range(MAU_MOI_LUOT // BATCH):
            s = torch.randint(0, S, (BATCH,), device=TB)
            o = torch.randint(CUA_SO - 1, o_max, (BATCH,), device=TB)                          # o < moc; ngay sau moc co co = False
            x_mh, x_gm, cat, i_gm, ss = lay_lo(d, m, s, o)
            eta = mh(x_mh, x_gm, cat)
            r, co = m["Y"][ss, i_gm] / m["tl"][s][:, None], m["co"][ss, i_gm]
            if ham == "tweedie":                                                               # p = 1,2: nhu LightGBM
                loss = r * torch.exp((1 - TWEEDIE_P) * eta) / (TWEEDIE_P - 1) + torch.exp((2 - TWEEDIE_P) * eta) / (2 - TWEEDIE_P)
            else:
                loss = (r - torch.exp(eta)).abs()
            w = (m["tl"][s] / tb_tl)[:, None] * co                                             # ma ban nhieu nang hon, nhu WMAPE
            gia_tri = (loss * w).sum() / w.sum().clamp(min=1)
            opt.zero_grad(set_to_none=True)
            gia_tri.backward()
            nn.utils.clip_grad_norm_(mh.parameters(), 1.0)
            opt.step()


@torch.no_grad()
def du_doan(mh, d, m):
    mh.eval()
    s = torch.arange(len(d.skus), device=TB)
    x_mh, x_gm, cat, _, _ = lay_lo(d, m, s, torch.full_like(s, m["o"]))
    return (torch.exp(mh(x_mh, x_gm, cat)) * m["tl"][:, None]).cpu().numpy()


def make_model(d, loai, ham, ten=""):
    """Ham (hist, fut) -> du bao, dung trong backtest(). Moi hat giong 1 mo hinh, hoc tiep tu moc truoc."""
    so_dt = d.co_dinh.shape[2] + 6
    cap = []
    for hg in HAT_GIONG:
        torch.manual_seed(hg)
        mh = MaHoaGiaiMa(loai, so_dt, d.so_nhom).to(TB)
        cap.append((mh, torch.optim.Adam(mh.parameters(), lr=LR_DAU)))
    da_hoc = [False]

    def fn(hist, fut):
        moc = hist.date.max()
        m = d.theo_moc(moc)
        t0 = time.time()
        for k, (mh, opt) in enumerate(cap):
            torch.manual_seed(HAT_GIONG[k] + m["o"])
            hoc(mh, opt, d, m, ham, *((LUOT_TIEP, LR_TIEP) if da_hoc[0] else (LUOT_DAU, LR_DAU)))
        da_hoc[0] = True
        f = np.mean([du_doan(mh, d, m) for mh, _ in cap], axis=0)
        print(f"  {ten} moc {moc.date()}: {time.time() - t0:.0f}s", flush=True)
        ra = fut[["date", "ma_sku", "la_ngay_nghi"]].copy()
        i, j = ra.ma_sku.map(d.i_sku).values, (ra.date - moc).dt.days.values - 1
        ra["du_bao"] = np.where(ra.la_ngay_nghi == 1, 0, f[i, j])
        return ra[["date", "ma_sku", "du_bao"]]
    return fn


def kiem_khong_nhin_truoc(d, moc):
    """Doi het nhu cau sau moc thanh so rac: moi tensor dua vao mo hinh phai y nguyen."""
    a = d.theo_moc(moc)
    rac = d.y.copy()
    rac[:, a["o"] + 1:] = 1e6
    b = d.theo_moc(moc, rac)
    for k in ["Y", "co", "tl", "Z", "tre"]:
        assert torch.equal(a[k], b[k]), f"nhin truoc o {k}"
    assert not a["co"][:, a["o"] + 1:].any() and (a["Y"][:, a["o"] + 1:] == 0).all(), "con nhu cau sau moc"
    print(f"Khong nhin truoc: dat (moc {moc.date()})")


def doc_state():
    return json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}


def luu_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)


def ghi_day_du(p, ten, tap):
    os.makedirs(THU_MUC, exist_ok=True)
    p.to_csv(f"{THU_MUC}/{ten}_{tap}.csv", index=False, encoding="utf-8-sig")


def doc_day_du(ten, tap):
    return pd.read_csv(f"{THU_MUC}/{ten}_{tap}.csv", parse_dates=["date", "moc"])


def ghep(dl, v4, w_by):
    x = v4[["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]].merge(
        dl[["date", "ma_sku", "moc", "du_bao"]], on=["date", "ma_sku", "moc"], suffixes=("_v", "_d"), validate="1:1")
    assert len(x) == len(v4) == len(dl), "hai bo du bao khong khop dong"
    w = x.xyz_train.map(w_by).astype(float)
    x["du_bao"] = w * x.du_bao_d + (1 - w) * x.du_bao_v
    return x.drop(columns=["du_bao_v", "du_bao_d"])


if __name__ == "__main__":
    a = sys.argv
    buoc = a[a.index("--buoc") + 1]
    loai = a[a.index("--cell") + 1] if "--cell" in a else None
    tap = a[a.index("--tap") + 1] if "--tap" in a else VAL
    if buoc == "bao_cao":
        st = doc_state()
        r = pd.read_csv("reports/ket_qua_mo_hinh.csv", encoding="utf-8-sig")
        cot = ["mo_hinh", "WMAPE", "WMAPE_tuan", "Bias_pct", "WMAPE_X", "WMAPE_Y", "WMAPE_Z"]
        ds = ["ket_hop_v4", "lstm_tuan", "rnn_tuan", "ket_hop_v5", "lgb_v3_AB", "prophet", "prophet_addi", "tb_truot_28_tuan"]
        bang = {t: r[(r.tap == t) & r.mo_hinh.isin(ds)][cot].sort_values("WMAPE").round(4).to_markdown(index=False) for t in (VAL, "test")}
        L = ["# Mô hình học sâu LSTM và RNN (vòng 5)", "", "Luật và cấu hình ghi trước khi chạy: docs/10 mục 9.7. Quyết định chỉ dựa trên validation2. "
             "Dữ liệu mô phỏng.", "", "## Hàm mất mát (validation2, 13 mốc)", "", str(st.get("chon_ham")), "", "## Quyết định", "", str(st.get("quyet_dinh")), "",
             "## Validation2", "", bang[VAL], "", "## Test (đã mở từ 01/11, chỉ báo cáo)", "", bang["test"], ""]
        open(REPORT, "w", encoding="utf-8").write("\n".join(L))
        print("\n".join(L))
        sys.exit()

    keep_awake(True)
    df = load()
    d = DuLieu(df)
    st = doc_state()
    print(f"Thiet bi {TB}; {len(d.skus)} ma x {len(d.ngay)} ngay x {d.co_dinh.shape[2] + 6} dac trung", flush=True)

    if buoc == "thu":
        moc = folds(VAL)
        kiem_khong_nhin_truoc(d, moc[0])
        kiem_khong_nhin_truoc(d, folds("test")[-1])
        t0 = time.time()
        p = backtest(make_model(d, "lstm", "tweedie", "thu"), df, moc[:2], name="thu", verbose=False)
        print(f"2 moc validation2: {time.time() - t0:.0f}s; WMAPE {chi_so(p)['WMAPE']:.4f}, Bias {chi_so(p)['Bias']:+.4f}")
    elif buoc == "chon_ham":
        kq = {}
        for ham in ["tweedie", "l1"]:
            p = backtest(make_model(d, "lstm", ham, ham), df, folds(VAL), name=ham, verbose=False)
            ghi_day_du(p, f"lstm_{ham}_28", VAL)
            kq[ham] = chi_so(p)
            print(ham, kq[ham], flush=True)
        chon = "l1" if kq["tweedie"]["WMAPE"] - kq["l1"]["WMAPE"] >= NGUONG_HAM else "tweedie"     # luat 1
        st["chon_ham"] = dict(ket_qua=kq, chon=chon)
        print("Chon ham mat mat:", chon)
    elif buoc == "tuan":
        assert "chon_ham" in st, "chay --buoc chon_ham truoc"
        assert tap == VAL or "quyet_dinh" in st, "luat 9.7: test chi chay sau khi da quyet dinh tren validation2"
        ham = st["chon_ham"]["chon"]
        p = backtest(make_model(d, loai, ham, f"{loai}/{tap}"), df, folds(tap, step=7), name=loai, verbose=False)
        ghi_day_du(p, f"{loai}_tuan", tap)
        r = save_results(f"{loai}_tuan", ban_moi_nhat(p), df, tap, f"{loai.upper()} ma hoa - giai ma, {ham}, cap nhat moi 7 ngay (hoc tiep), docs/10 muc 9.7").iloc[0]
        st.setdefault("ket_qua", {}).setdefault(tap, {})[f"{loai}_tuan"] = dict(WMAPE=float(r.WMAPE), Bias=float(r.Bias_pct), tuan=float(r.WMAPE_tuan), Z=float(r.WMAPE_Z))
        print(loai, tap, st["ket_qua"][tap][f"{loai}_tuan"], flush=True)
    elif buoc == "ghep":
        v4 = doc_du_bao("ket_hop_v4", VAL)
        moi = {t: doc_day_du(f"{t}_tuan", VAL) for t in ["lstm", "rnn"]}
        nen = chi_so(ban_moi_nhat(v4))
        cs = {t: chi_so(ban_moi_nhat(p)) for t, p in moi.items()}
        tot = min(cs, key=lambda t: cs[t]["WMAPE"])
        w = {g: float(min(GRID_W, key=lambda v: chi_so(ban_moi_nhat(ghep(moi[tot][moi[tot].xyz_train == g], v4[v4.xyz_train == g], {g: v})))["WMAPE"]))
             for g in ["X", "Y", "Z"]}
        b = ghep(moi[tot], v4, w)
        ghi_day_du(b, "ket_hop_v5", VAL)
        r = save_results("ket_hop_v5", ban_moi_nhat(b), df, VAL, f"ket_hop_v4 + {tot}, w hoc sau = {w} (do tren {VAL}), docs/10 muc 9.7").iloc[0]
        cs["ket_hop_v5"] = dict(WMAPE=float(r.WMAPE), Bias=float(r.Bias_pct))
        dat = {t: v for t, v in cs.items() if giu(v, nen)}                                         # luat 4
        chon = min(dat, key=lambda t: dat[t]["WMAPE"]) if dat else "ket_hop_v4"
        st["quyet_dinh"] = dict(ket_hop_v4=nen, ung_vien=cs, hoc_sau_tot_hon=tot, w=w, chon=chon)
        print(json.dumps(st["quyet_dinh"], ensure_ascii=False, indent=1))
    elif buoc == "test":
        assert "test" not in st, "luat 9.7: test chi chay mot lan"
        q = st["quyet_dinh"]
        v4 = doc_du_bao("ket_hop_v4", "test")
        b = ghep(doc_day_du(f"{q['hoc_sau_tot_hon']}_tuan", "test"), v4, q["w"])
        ghi_day_du(b, "ket_hop_v5", "test")
        r = save_results("ket_hop_v5", ban_moi_nhat(b), df, "test", f"ket_hop_v4 + {q['hoc_sau_tot_hon']}, w = {q['w']} (giu tu {VAL}), docs/10 muc 9.7").iloc[0]
        st["test"] = dict(ket_hop_v4=chi_so(ban_moi_nhat(v4)), ket_hop_v5=dict(WMAPE=float(r.WMAPE), Bias=float(r.Bias_pct), tuan=float(r.WMAPE_tuan), Z=float(r.WMAPE_Z)),
                          **st.get("ket_qua", {}).get("test", {}))
        print(json.dumps(st["test"], ensure_ascii=False, indent=1))
    else:
        sys.exit(__doc__)
    luu_state(st)
    keep_awake(False)
