"""Chay mo hinh dang chon NGAY KHI BAM (man "Du bao" cua dashboard): hoc LightGBM tren toan bo lich su, hoc Prophet cho 1 ma, ghep theo
trong so da chon, giai thich theo yeu to, thu neu (bat khuyen mai). Dung DUNG cac ham da kiem chung (make_model, hoc_prophet, khung_tuong_lai);
ket qua phai trung du bao tuong lai da luu (src/du_bao_tuong_lai*.py). Khong ghi CSDL.
- Bo mo phong: ket_hop_v4 = w * LightGBM + (1 - w) * Prophet, w theo nhom XYZ.
- Nguon kiem chung (M5): ket_hop_dl = w2 * RNN + (1 - w2) * (w1 * LightGBM + (1 - w1) * Prophet). RNN hoc tiep moi tuan tren GPU nen
  khong hoc lai khi bam: dung ban da hoc (reports/du_bao/day_du/rnn_tuong_lai.csv).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from danh_gia import HORIZON, du_bao_mot_moc, load  # noqa: E402
from kiem_tra_du_lieu import nguon_du_lieu  # noqa: E402


def cau_hinh(goc):
    """goc: thu muc nguon cua dashboard. Thu muc chay du bao co the khac (M5 kho dung du bao cua du_lieu_nguon/m5)."""
    goc = Path(goc)
    n = nguon_du_lieu(goc)
    db = (goc / n["thu_muc_du_bao"]).resolve() if n.get("thu_muc_du_bao") else goc
    kc = db / "reports" / "kiem_chung_trang_thai.json"
    return dict(goc=goc, thu_muc=db, kieu="dl" if kc.exists() else "v4", lich_goc=(goc / n["lich_goc"]).resolve() if n.get("lich_goc") else None)


def chuan_bi(goc):
    """Doc du lieu, dung 28 ngay tuong lai va lich biet truoc; tra ve ngu canh dung cho cac ham sau."""
    import mo_hinh_prophet as P
    import nang_cap_du_bao as N
    from tuong_lai import doc_tham_chieu, khung_tuong_lai, mo_rong_lich
    c = cau_hinh(goc)
    db = c["thu_muc"]
    df = load(str(db / "data" / "features" / "dac_trung.csv"))
    o = df.date.max()
    lich, nghi, shock, km = doc_tham_chieu(str(db / "data" / "reference"))
    if c["kieu"] == "v4":
        fut, ghi = khung_tuong_lai(df, o, lich, nghi, shock, km)
        lich_mr, _ = mo_rong_lich(lich, fut.date.max())
        cw = json.load(open(db / "reports" / "nang_cap_du_bao_trang_thai.json", encoding="utf-8"))
        cfg, trong_so = cw["cfg"], dict(lgb=cw["w"])
        rnn = None
    else:
        from du_bao_tuong_lai_kc import lich_day_du
        lich_mr = lich_day_du(str(c["lich_goc"]), o + pd.Timedelta(days=HORIZON))
        fut, ghi = khung_tuong_lai(df, o, lich_mr, nghi, shock, km, mo_rong=False)
        ch = json.load(open(db / "reports" / "kiem_chung_trang_thai.json", encoding="utf-8"))["chon"]
        cfg, trong_so = {"A": True, "B": True, "params": {}}, dict(lgb=ch["w_ket_hop"], rnn=ch["w_ket_hop_dl"])
        rnn = pd.read_csv(db / "reports" / "du_bao" / "day_du" / "rnn_tuong_lai.csv", parse_dates=["date"])
        rnn = rnn.assign(du_bao=rnn.du_bao.clip(lower=0))                                     # chan duoi 0 nhu backtest
    cal = N.lich_su_kien(np.concatenate([df.date.unique(), fut.date.unique()]), ev=lich_mr)
    return dict(**c, df=df, o=o, fut=fut, ghi=ghi, cal=cal, hol=P.holidays_table(lich=lich_mr), cfg=cfg, trong_so=trong_so, rnn=rnn)


def hoc_lightgbm(ctx):
    """Hoc LightGBM tren moi ma, moi ngay den ngay cuoi (cung cach backtest). Tra ve (ham da hoc, du bao moi ma)."""
    import nang_cap_du_bao as N
    df = ctx["df"]
    cats = {c: sorted(df[c].dropna().unique()) for c in N.CAT}
    sk = [c for c in df.attrs["known_ahead"] if c.startswith("sk_")]
    fn = N.make_model(ctx["cfg"], cats, sk, ctx["cal"])
    return fn, du_bao_mot_moc(fn, df, ctx["fut"], ctx["o"])


def hoc_prophet_ma(ctx, ma):
    """Prophet cho 1 ma (cung cau hinh backtest, che do cong). Tra ve mo hinh (None neu qua it du lieu)."""
    import mo_hinh_prophet as P
    h = ctx["df"][ctx["df"].ma_sku == ma]
    train = h.assign(y=h.y_cham)[["date", "y", "khuyen_mai"]].rename(columns={"date": "ds"}).reset_index(drop=True)
    return P.hoc_prophet(train, ctx["hol"], "additive")


def du_bao_prophet(m, fut_ma):
    """Du bao Prophet + thanh phan cho cac ngay cua 1 ma; ngay kho nghi = 0, chan duoi 0 (cung backtest)."""
    from giai_thich import thanh_phan_prophet
    if m is None:
        return fut_ma[["date"]].assign(du_bao=0.0), None
    f = fut_ma[["date", "khuyen_mai"]].rename(columns={"date": "ds"}).reset_index(drop=True)
    fc = m.predict(f)
    tp = thanh_phan_prophet(fc, "khuyen_mai" in m.extra_regressors)
    du = np.where(fut_ma.la_ngay_nghi.values == 1, 0, fc.yhat.values)
    return pd.DataFrame({"date": fut_ma.date.values, "du_bao": np.clip(du, 0, None)}), tp


def ghep(ctx, ma, lgb_ma, pro_ma, rnn_ma=None):
    """Ghep theo trong so da chon cua nhom XYZ cua ma. Tra ve (bang theo ngay, mo ta trong so)."""
    xyz = ctx["fut"].loc[ctx["fut"].ma_sku == ma, "xyz_train"].iloc[0]
    w1 = float(ctx["trong_so"]["lgb"][xyz])
    x = lgb_ma[["date", "du_bao"]].rename(columns={"du_bao": "lgb"}).merge(pro_ma.rename(columns={"du_bao": "prophet"}), on="date")
    x["ket_hop"] = w1 * x.lgb + (1 - w1) * x.prophet
    if ctx["kieu"] == "v4":
        x["du_bao"] = x.ket_hop
        return x, dict(nhom=xyz, w_lgb=w1)
    w2 = float(ctx["trong_so"]["rnn"][xyz])
    x = x.merge(rnn_ma[["date", "du_bao"]].rename(columns={"du_bao": "rnn"}), on="date")
    x["du_bao"] = w2 * x.rnn + (1 - w2) * x.ket_hop
    return x, dict(nhom=xyz, w_lgb=w1, w_rnn=w2)


def chay_ma(ctx, fn, ma, m_prophet, fut_sua=None):
    """Du bao + giai thich cho 1 ma. fut_sua: khung tuong lai da sua (thu neu); None = khung goc. LightGBM khong hoc lai (dung fn da hoc)."""
    from giai_thich import gom_nhom
    fut = ctx["fut"] if fut_sua is None else fut_sua
    fm = fut[fut.ma_sku == ma]
    dg = fn.du_doan_lai(fm, dong_gop=True)
    lgb_ma = dg[["date", "du_bao"]].assign(du_bao=lambda d: d.du_bao.clip(lower=0))
    pro_ma, tp = du_bao_prophet(m_prophet, fm)
    rnn_ma = ctx["rnn"][ctx["rnn"].ma_sku == ma] if ctx["rnn"] is not None else None
    bang, w = ghep(ctx, ma, lgb_ma, pro_ma, rnn_ma)
    return dict(bang=bang.sort_values("date").reset_index(drop=True), trong_so=w, giai_thich=gom_nhom(dg).sort_values("date").reset_index(drop=True),
                prophet=tp)


def doi_chieu_da_luu(ctx, ma, bang):
    """So voi du bao tuong lai da luu (CSDL / tep). Tra ve lech tuyet doi lon nhat (None neu chua co ban luu)."""
    db = ctx["thu_muc"]
    f = db / "reports" / "du_bao" / ("ket_hop_v4_tuong_lai.csv" if ctx["kieu"] == "v4" else "day_du/ket_hop_dl_tuong_lai.csv")
    if not f.exists():
        return None
    luu = pd.read_csv(f, parse_dates=["date"])
    x = luu[luu.ma_sku == ma].merge(bang[["date", "du_bao"]], on="date", suffixes=("_luu", "_moi"))
    return float((x.du_bao_luu - x.du_bao_moi).abs().max()) if len(x) else None


def bat_khuyen_mai(fut, ma, tu, den):
    """Thu neu: ban sao khung tuong lai, bat khuyen_mai = 1 cho ma trong [tu, den]. Ma khac, cot khac giu nguyen."""
    tu, den = pd.Timestamp(tu), pd.Timestamp(den)
    if den < tu:
        raise ValueError("ngay ket thuc truoc ngay bat dau")
    f = fut.copy()
    chon = (f.ma_sku == ma) & (f.date >= tu) & (f.date <= den)
    if not chon.any():
        raise ValueError("khoang ngay khong nam trong 28 ngay du bao cua ma")
    f.loc[chon, "khuyen_mai"] = 1
    return f


def km_lich_su(df, ma):
    """Doi chieu voi lich su cua ma (chi de nguoi xem so voi muc mo hinh tang):
    - ti_so_tho: ban TB ngay co khuyen mai / ngay khong khuyen mai (lan mua vu: KM hay roi vao mua cao diem);
    - ti_so_cung_mua: tong ban ngay co KM / tong muc nen cua chinh nhung ngay do, muc nen = TB 28 ngay thuong (khong KM, mo cua) ngay truoc.
    Ngay mo cua, nhu cau tin duoc."""
    x = df[df.ma_sku == ma].sort_values("date").set_index("date")
    mo = (x.la_ngay_nghi == 0) & x.y_cham.notna()
    km, thuong = mo & (x.khuyen_mai == 1), mo & (x.khuyen_mai == 0)
    n = int(km.sum())
    co, khong = x.y_cham[km].mean(), x.y_cham[thuong].mean()
    nen = x.y_cham.where(thuong).rolling("28D", min_periods=10).mean().shift(1)
    cm = km & nen.notna()
    return dict(so_ngay_km=n, ban_co_km=float(co) if n else float("nan"), ban_khong_km=float(khong),
                ti_so_tho=float(co / khong) if n and khong > 0 else float("nan"),
                ti_so_cung_mua=float(x.y_cham[cm].sum() / nen[cm].sum()) if cm.any() and nen[cm].sum() > 0 else float("nan"))


def so_sanh_khuyen_mai(ctx, fn, so_ngay=7):
    """Toan kho: moi ma, he so LightGBM tang khi bat khuyen mai so_ngay ngay dau (thu neu, khong hoc lai) so voi lich su cung mua.
    Chi LightGBM (hoc Prophet cho moi ma mat vai phut)."""
    fut = ctx["fut"]
    den = fut.date.min() + pd.Timedelta(days=so_ngay - 1)
    f2 = fut.copy()
    f2.loc[f2.date <= den, "khuyen_mai"] = 1
    x = fn.du_doan_lai(fut).merge(fn.du_doan_lai(f2), on=["date", "ma_sku"], suffixes=("_goc", "_km"))
    x = x[(x.date <= den) & (x.la_ngay_nghi_goc == 0)]
    g = x.groupby("ma_sku")[["du_bao_goc", "du_bao_km"]].sum()
    ra = pd.DataFrame({"mo_hinh": g.du_bao_km / g.du_bao_goc.where(g.du_bao_goc > 0)})
    ra["lich_su"] = [km_lich_su(ctx["df"], m)["ti_so_cung_mua"] for m in ra.index]
    return ra


if __name__ == "__main__":
    # python src/chay_du_bao.py --so_sanh_km  (tai thu muc nguon) -> reports/so_sanh_khuyen_mai.json: so sanh toan kho cho bao cao
    sys.stdout.reconfigure(encoding="utf-8")
    if "--so_sanh_km" in sys.argv:
        ctx = chuan_bi(".")
        fn, _ = hoc_lightgbm(ctx)
        ss = so_sanh_khuyen_mai(ctx, fn).dropna()
        ra = dict(so_ma=int(len(ss)), so_ngay=7)
        if len(ss):
            ra.update(mo_hinh=dict(p25=float(ss.mo_hinh.quantile(.25)), p50=float(ss.mo_hinh.median()), p75=float(ss.mo_hinh.quantile(.75))),
                      lich_su=dict(p25=float(ss.lich_su.quantile(.25)), p50=float(ss.lich_su.median()), p75=float(ss.lich_su.quantile(.75))),
                      tuong_quan_hang=float(ss.mo_hinh.rank().corr(ss.lich_su.rank())), it_hon_lich_su=int((ss.mo_hinh < ss.lich_su).sum()))
        json.dump(ra, open("reports/so_sanh_khuyen_mai.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(ra)
