"""GD E: chon / ket hop mo hinh. Luat chon CHI dung tap validation; tap test chi de cham diem sau cung.
Ung vien (du bao = w * LightGBM + (1 - w) * Prophet):
  prophet (w=0), lightgbm (w=1), trung_binh (w=0,5),
  ket_hop_toan_kho (1 trong so w do tren validation),
  ket_hop_theo_nhom (moi nhom XYZ 1 trong so w do tren validation).
Luat chon (viet truoc khi xem test): WMAPE validation thap nhat; neu chenh duoi 0,005 thi chon phuong an don gian hon
(thu tu don gian: prophet, lightgbm, trung_binh, ket_hop_toan_kho, ket_hop_theo_nhom).
Dau vao: reports/du_bao/{prophet_addi_validation, lightgbm_tweedie_validation, prophet_test, lightgbm_test}.csv
Chay: python src/chon_mo_hinh.py            (vong 1: validation 04-09/2025, khong co Tet)
      python src/chon_mo_hinh.py --vong 2   (vong 2: validation 10/2024-09/2025, cung mua voi test; cau hinh mo hinh va luat chon giu nguyen)
Ket qua: reports/chon_mo_hinh.md, them dong vao reports/ket_qua_mo_hinh.csv, du bao reports/du_bao/<ung_vien>_<tap>.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, save_results, score, score_week  # noqa: E402

D = "reports/du_bao"
VONG2 = "--vong" in sys.argv and sys.argv[sys.argv.index("--vong") + 1] == "2"
VAL = "validation2" if VONG2 else "validation"
SUFFIX = "_v2" if VONG2 else ""
FILES = {VAL: (f"prophet_addi_{VAL}", f"lightgbm_tweedie_{VAL}"),
         "test": ("prophet_test", "lightgbm_test")}
GRID = np.round(np.arange(0, 1.01, 0.1), 1)
ORDER = ["prophet", "lightgbm", "trung_binh", "ket_hop_toan_kho", "ket_hop_theo_nhom"]
GROUPS = ["X", "Y", "Z"]
TIE = 0.005


def pair(kind):
    fp, fl = FILES[kind]
    p = pd.read_csv(f"{D}/{fp}.csv", parse_dates=["date", "moc"])
    lg = pd.read_csv(f"{D}/{fl}.csv", parse_dates=["date", "moc"])[["date", "ma_sku", "moc", "du_bao"]]
    m = p.merge(lg, on=["date", "ma_sku", "moc"], suffixes=("_p", "_l"))
    assert len(m) == len(p) == len(lg), "hai file du bao khong khop dong"
    return m


def blend(m, w):
    """w: so (toan kho) hoac dict theo nhom XYZ."""
    ww = m.xyz_train.map(w).values if isinstance(w, dict) else w
    out = m.drop(columns=["du_bao_p", "du_bao_l"]).copy()
    out["du_bao"] = ww * m.du_bao_l.values + (1 - ww) * m.du_bao_p.values
    return out


def wmape(p):
    g = p.dropna(subset=["y_cham"])
    return (g.y_cham - g.du_bao).abs().sum() / g.y_cham.sum()


if __name__ == "__main__":
    df = load()
    val, test = pair(VAL), pair("test")

    # --- do trong so tren VALIDATION ---
    w_all = min(GRID, key=lambda w: wmape(blend(val, w)))
    w_grp = {g: min(GRID, key=lambda w: wmape(blend(val[val.xyz_train == g], w))) for g in GROUPS}
    cands = {"prophet": 0.0, "lightgbm": 1.0, "trung_binh": 0.5, "ket_hop_toan_kho": float(w_all),
             "ket_hop_theo_nhom": {g: float(v) for g, v in w_grp.items()}}

    rows = []
    for name in ORDER:
        w = cands[name]
        pv, pt = blend(val, w), blend(test, w)
        sv, st = score(pv, df).iloc[0], score(pt, df).iloc[0]
        stz = score(pt, df, by="xyz_train").set_index("xyz_train")
        rows.append({"ung_vien": name, "trong_so_LightGBM": str(w),
                     "val_WMAPE": sv.WMAPE, "val_Bias": sv.Bias_pct,
                     "test_WMAPE": st.WMAPE, "test_WMAPE_tuan": score_week(pt), "test_Bias": st.Bias_pct,
                     "test_WMAPE_Z": stz.loc["Z", "WMAPE"], "test_Bias_Z": stz.loc["Z", "Bias_pct"]})
        if name not in ("prophet", "lightgbm"):        # 2 mo hinh goc da co dong rieng
            save_results(name + SUFFIX, pv, df, VAL, f"w LightGBM = {w} (do tren {VAL})")
            save_results(name + SUFFIX, pt, df, "test", f"w LightGBM = {w} (do tren {VAL})")
    t = pd.DataFrame(rows)

    # --- luat chon: chi nhin cot val_WMAPE ---
    best_w = t.val_WMAPE.min()
    chosen = t[t.val_WMAPE <= best_w + TIE].iloc[0].ung_vien    # ORDER da xep tu don gian den phuc tap
    t["duoc_chon"] = np.where(t.ung_vien == chosen, "✅", "")

    fmt = lambda v: f"{v:.3f}".replace(".", ",") if isinstance(v, float) else str(v)
    cols = list(t.columns)
    lines = [f"# Chon mo hinh (GD E){' - vong 2' if VONG2 else ''}", f"Tap dung de chon: {VAL}.", "",
             f"Trong so LightGBM do tren validation: toan kho w = {w_all}; theo nhom {cands['ket_hop_theo_nhom']}.",
             f"Luat: WMAPE validation thap nhat, chenh duoi {TIE} thi chon phuong an don gian hon. **Duoc chon: {chosen}**.",
             "Cac cot test chi de bao cao, KHONG dung de chon. Bias duong = du bao thieu. Du lieu mo phong.", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in t.itertuples(index=False)]
    with open(f"reports/chon_mo_hinh{'_vong2' if VONG2 else ''}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
