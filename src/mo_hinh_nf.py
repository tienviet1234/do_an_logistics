"""TiDE, N-HiTS, TFT (thu vien NeuralForecast) tren cung khung danh gia. Luat va cau hinh ghi TRUOC khi chay: docs/10 muc 9.9.
Chay bang moi truong rieng, tai thu muc goc (du lieu mo phong) hoac thu muc lam viec cua nguon:
  .venv_nf/Scripts/python.exe src/mo_hinh_nf.py --buoc thoi_gian --mo_hinh tide     (chi do thoi gian, KHONG in sai so)
  ... --buoc tuan --mo_hinh tide|nhits|tft [--tap test]
  ... --buoc ghep     quyet dinh theo validation2
  ... --buoc test     chi bao cao
  ... --buoc bao_cao  -> reports/mo_hinh_nf.md
"""
import json
import logging
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from danh_gia import backtest, folds, keep_awake, load, save_results, HORIZON  # noqa: E402

VAL = "validation2"
TAM_THU = {"tide": "TiDE", "nhits": "NHITS", "tft": "TFT"}
CUA_SO, MAX_STEPS, HOC_LAI_MOI, HAT_GIONG = 56, 1000, 4, 20261103     # hoc lai tu dau moi 4 moc (28 ngay), cac moc giua chi cap nhat dau vao
BATCH, WINDOWS = 32, 256
TFT_AN, TFT_WINDOWS, TFT_SO_BIEN, TFT_MAX_STEPS = 32, 64, 8, 500               # TFT gon: it bien tuong lai nhat (8 co lich + gia tri tre cung ky nam truoc)
NGUONG_WMAPE, NGUONG_BIAS = 0.005, 0.01
GRID_W = np.round(np.arange(0, 1.01, 0.1), 1)
THU_MUC = "reports/du_bao/nf"
STATE = "reports/mo_hinh_nf_trang_thai.json"
REPORT = "reports/mo_hinh_nf.md"
COT_GHEP = ["date", "ma_sku", "moc", "ngay_thu", "y_cham", "abc_train", "xyz_train", "loai_nhu_cau", "du_bao"]


def tao_khung(skus, ngay, o, y, co, x, tl, ten_x):
    """Bang hoc (ngay <= moc) va bang tuong lai (28 ngay sau moc, chi co dac trung biet truoc) theo dang NeuralForecast. Nhu cau chia theo trung binh cua ma.
    y (ma, ngay): nhu cau, 0 neu khong tin duoc; co (ma, ngay): nhu cau tin duoc; x (ma, ngay, dac trung); o: chi so ngay moc."""
    S = len(skus)
    if (np.asarray(co)[:, o + 1:]).any():
        raise ValueError("Co nhu cau sau moc: nhin truoc")
    n_hoc, n_tl = o + 1, HORIZON
    uid = np.array(skus)
    hoc = pd.DataFrame(x[:, :n_hoc].reshape(S * n_hoc, -1), columns=ten_x)
    hoc.insert(0, "unique_id", np.repeat(uid, n_hoc))
    hoc.insert(1, "ds", np.tile(ngay[:n_hoc].values, S))
    hoc.insert(2, "y", (y[:, :n_hoc] / tl[:, None]).ravel())
    hoc.insert(3, "available_mask", co[:, :n_hoc].ravel().astype(np.float32))
    tuong_lai = pd.DataFrame(x[:, o + 1:o + 1 + n_tl].reshape(S * n_tl, -1), columns=ten_x)
    tuong_lai.insert(0, "unique_id", np.repeat(uid, n_tl))
    tuong_lai.insert(1, "ds", np.tile(ngay[o + 1:o + 1 + n_tl].values, S))
    return hoc, tuong_lai


def bien_cua(ten, ten_x):
    """TFT tao 1 mang rieng cho moi bien nen chi lay nhom bien it nhat; hai mo hinh con lai dung du bien."""
    return ten_x[:TFT_SO_BIEN] + ten_x[-6:] if ten == "tft" else ten_x


def tao_mo_hinh(ten, ten_x, ten_tinh, max_steps=MAX_STEPS):
    from neuralforecast.losses.pytorch import MAE
    from neuralforecast.models import NHITS, TFT, TiDE
    chung = dict(h=HORIZON, input_size=CUA_SO, futr_exog_list=bien_cua(ten, ten_x), stat_exog_list=ten_tinh, loss=MAE(), max_steps=max_steps, batch_size=BATCH, windows_batch_size=WINDOWS,
                 scaler_type="identity", random_seed=HAT_GIONG, enable_progress_bar=False, enable_model_summary=False, logger=False, enable_checkpointing=False)
    if ten == "tide":
        return TiDE(hidden_size=128, decoder_output_dim=16, temporal_decoder_dim=64, num_encoder_layers=2, num_decoder_layers=2, **chung)
    if ten == "nhits":
        return NHITS(mlp_units=[[256, 256]] * 3, **chung)
    if ten == "tft":                                       # cau hinh gon: 4 GB GPU khong kham noi TFT day du (docs/10 muc 9.9)
        chung.update(windows_batch_size=TFT_WINDOWS, max_steps=min(max_steps, TFT_MAX_STEPS))
        return TFT(hidden_size=TFT_AN, **chung)
    raise SystemExit(f"Khong co mo hinh {ten}")


def make_model(d, ten, max_steps=MAX_STEPS):
    from neuralforecast import NeuralForecast
    so = d.co_dinh.shape[2]
    ten_x = [f"x{i}" for i in range(so + 6)]
    tinh = pd.get_dummies(pd.DataFrame(d.cat.cpu().numpy()[:, 1:], columns=[c for c, _ in __import__("mo_hinh_dl").CAT[1:]]).astype(str), dtype=float)
    ten_tinh = [f"s{i}" for i in range(tinh.shape[1])]
    tinh.columns = ten_tinh
    tinh.insert(0, "unique_id", d.skus)
    dem = [0]
    nf = [None]
    x0 = d.co_dinh.cpu().numpy()

    def fn(hist, fut):
        moc = hist.date.max()
        m = d.theo_moc(moc)
        x = np.concatenate([x0, m["tre"].cpu().numpy()], axis=2)
        tl = m["tl"].cpu().numpy()
        hoc, tl_f = tao_khung(d.skus, d.ngay, m["o"], m["Y"].cpu().numpy(), m["co"].cpu().numpy(), x, tl, ten_x)
        if dem[0] % HOC_LAI_MOI == 0:
            t0 = time.time()
            nf[0] = NeuralForecast(models=[tao_mo_hinh(ten, ten_x, ten_tinh, max_steps)], freq="D")
            nf[0].fit(df=hoc, static_df=tinh, val_size=0)
            print(f"  {ten} hoc lai tai moc {moc.date()}: {time.time() - t0:.0f}s", flush=True)
        dem[0] += 1
        dd = nf[0].predict(df=hoc, static_df=tinh, futr_df=tl_f).reset_index()
        ket = dd.rename(columns={"ds": "date", TAM_THU[ten]: "f"})[["unique_id", "date", "f"]]
        ra = fut[["date", "ma_sku", "la_ngay_nghi"]].merge(ket, left_on=["ma_sku", "date"], right_on=["unique_id", "date"], how="left", validate="1:1")
        if ra.f.isna().any():
            raise ValueError("Thieu du bao")
        ra["du_bao"] = np.where(ra.la_ngay_nghi == 1, 0, ra.f.values * ra.ma_sku.map(dict(zip(d.skus, tl))).values)
        return ra[["date", "ma_sku", "du_bao"]]
    return fn


def ban_moi_nhat(p):
    return p.sort_values("ngay_thu").drop_duplicates(["date", "ma_sku"]).sort_values(["moc", "ma_sku", "date"])


def chi_so(p):
    g = ban_moi_nhat(p).dropna(subset=["y_cham"])
    e = g.y_cham - g.du_bao
    return dict(WMAPE=float(e.abs().sum() / g.y_cham.sum()), Bias=float(e.sum() / g.y_cham.sum()))


def dat_luat(moi, nen):
    """Luat 9.9: WMAPE giam >= 0,005 va |Bias| khong tang qua 1 diem so voi mo hinh dang dung."""
    return nen["WMAPE"] - moi["WMAPE"] >= NGUONG_WMAPE and abs(moi["Bias"]) - abs(nen["Bias"]) <= NGUONG_BIAS


def ghep(a, b, w_by):
    x = b[COT_GHEP].merge(a[["date", "ma_sku", "moc", "du_bao"]], on=["date", "ma_sku", "moc"], suffixes=("_b", "_a"), validate="1:1")
    if not len(x) == len(a) == len(b):
        raise ValueError("Hai bo du bao khong khop dong")
    w = x.xyz_train.map(w_by).astype(float)
    x["du_bao"] = w * x.du_bao_a + (1 - w) * x.du_bao_b
    return x.drop(columns=["du_bao_a", "du_bao_b"])


def doc_nen(tap):
    """Mo hinh dang dung cua nguon du lieu nay (du moi moc tuan): nguon kiem chung lay mo hinh da chon; du lieu mo phong lay ket_hop_v4."""
    f = "reports/kiem_chung_trang_thai.json"
    if os.path.exists(f):
        ten = json.load(open(f, encoding="utf-8"))["chon"]["chon"]
        return ten, pd.read_csv(f"reports/du_bao/day_du/{ten}_{tap}.csv", parse_dates=["date", "moc"])
    return "ket_hop_v4", pd.read_csv(f"reports/du_bao/ket_hop_v4_{tap}.csv", parse_dates=["date", "moc"])


def doc_nf(ten, tap):
    return pd.read_csv(f"{THU_MUC}/{ten}_{tap}.csv", parse_dates=["date", "moc"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    logging.getLogger("pytorch_lightning").setLevel(logging.ERROR)
    logging.getLogger("lightning_fabric").setLevel(logging.ERROR)
    a = sys.argv
    buoc = a[a.index("--buoc") + 1]
    tap = a[a.index("--tap") + 1] if "--tap" in a else VAL
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    if buoc == "bao_cao":
        ten_nen, _ = doc_nen(VAL)
        q = st["quyet_dinh"]
        L = ["# TiDE, N-HiTS, TFT", "", f"Luật ghi trước: docs/10 mục 9.9. Quyết định chỉ dựa trên validation2. Mô hình đang dùng: {ten_nen}.", "",
             "| Mô hình | Validation2 WMAPE | Validation2 Bias | Test WMAPE | Test Bias |", "|---|---:|---:|---:|---:|"]
        for t in [ten_nen, "tide", "nhits", "tft", "ket_hop_nf"]:
            v, x = q["bang"][t], st["test"][t]
            L.append(f"| {t} | {v['WMAPE']:.3f} | {100 * v['Bias']:+.1f}% | {x['WMAPE']:.3f} | {100 * x['Bias']:+.1f}% |")
        L += ["", f"Quyết định: **{q['chon']}** (trọng số ghép theo nhóm {q['w']}, ghép với {q['tot_nhat']}).", ""]
        open(REPORT, "w", encoding="utf-8").write("\n".join(L))
        print("\n".join(L))
        sys.exit()
    keep_awake(True)
    os.makedirs(THU_MUC, exist_ok=True)
    df = load()
    if buoc == "thoi_gian":
        import mo_hinh_dl as D
        ten = a[a.index("--mo_hinh") + 1]
        so_buoc = int(a[a.index("--so_buoc") + 1]) if "--so_buoc" in a else 100
        moc = folds(VAL, step=7)[:1]
        t0 = time.time()
        backtest(make_model(D.DuLieu(df), ten, so_buoc), df, moc, name=ten, verbose=False)
        print(f"{ten}: {so_buoc} buoc {time.time() - t0:.0f}s (khong in sai so)", flush=True)
        sys.exit()
    if buoc == "tuan":
        import mo_hinh_dl as D
        ten = a[a.index("--mo_hinh") + 1]
        assert tap == VAL or "quyet_dinh" in st, "luat 9.9: test chi chay sau khi da quyet dinh tren validation2"
        p = backtest(make_model(D.DuLieu(df), ten), df, folds(tap, step=7), name=ten, verbose=False)
        p.to_csv(f"{THU_MUC}/{ten}_{tap}.csv", index=False, encoding="utf-8-sig")
        save_results(f"{ten}_tuan", ban_moi_nhat(p), df, tap, f"{TAM_THU[ten]}, hoc lai moi 28 ngay, cap nhat dau vao moi 7 ngay, docs/10 muc 9.9")
        print(ten, tap, "xong", flush=True)
    elif buoc == "ghep":
        ten_nen, nen = doc_nen(VAL)
        ds = {t: doc_nf(t, VAL) for t in TAM_THU}
        bang = {ten_nen: chi_so(nen), **{t: chi_so(p) for t, p in ds.items()}}
        tot = min(TAM_THU, key=lambda t: bang[t]["WMAPE"])
        w = {}
        for g in sorted(nen.xyz_train.dropna().unique()):
            aa, bb = ds[tot][ds[tot].xyz_train == g], nen[nen.xyz_train == g]
            w[g] = float(min(GRID_W, key=lambda v: chi_so(ghep(aa, bb, {g: v}))["WMAPE"]))
        kh = ghep(ds[tot], nen, w)
        kh.to_csv(f"{THU_MUC}/ket_hop_nf_{VAL}.csv", index=False, encoding="utf-8-sig")
        save_results("ket_hop_nf", ban_moi_nhat(kh), df, VAL, f"{ten_nen} + {tot}, w = {w}, docs/10 muc 9.9")
        bang["ket_hop_nf"] = chi_so(kh)
        dat = {t: v for t, v in bang.items() if t != ten_nen and dat_luat(v, bang[ten_nen])}
        st["quyet_dinh"] = dict(bang=bang, tot_nhat=tot, w=w, nen=ten_nen, dat=list(dat), chon=min(dat, key=lambda t: dat[t]["WMAPE"]) if dat else ten_nen)
        print(json.dumps(st["quyet_dinh"], ensure_ascii=False, indent=1))
    elif buoc == "test":
        assert "test" not in st, "luat 9.9: test chi chay mot lan"
        q = st["quyet_dinh"]
        ten_nen, nen = doc_nen("test")
        kh = ghep(doc_nf(q["tot_nhat"], "test"), nen, q["w"])
        kh.to_csv(f"{THU_MUC}/ket_hop_nf_test.csv", index=False, encoding="utf-8-sig")
        save_results("ket_hop_nf", ban_moi_nhat(kh), df, "test", f"{ten_nen} + {q['tot_nhat']}, w = {q['w']} (giu tu {VAL}), docs/10 muc 9.9")
        st["test"] = {ten_nen: chi_so(nen), **{t: chi_so(doc_nf(t, "test")) for t in TAM_THU}, "ket_hop_nf": chi_so(kh)}
        print(json.dumps(st["test"], ensure_ascii=False, indent=1))
    else:
        raise SystemExit(__doc__)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    keep_awake(False)
