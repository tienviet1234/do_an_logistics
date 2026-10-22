"""Tong hop ket qua moi mo hinh tren CUNG mot tap diem (de so sanh cong bang).
Doc moi file reports/du_bao/<mo_hinh>_<tap>.csv, tinh WMAPE theo nhom.
Chay: python src/tong_hop_ket_qua.py [test|validation]   (mac dinh: test)
Ket qua: reports/bang_so_sanh_<tap>.md va .csv
"""
import glob
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from danh_gia import load, score, score_week  # noqa: E402

kind = sys.argv[1] if len(sys.argv) > 1 else "test"
df = load()
preds = {}
for f in sorted(glob.glob(f"reports/du_bao/*_{kind}.csv")):
    name = os.path.basename(f)[: -len(f"_{kind}.csv")]
    preds[name] = pd.read_csv(f, parse_dates=["date", "moc"])
if not preds:
    sys.exit(f"Chua co du bao nao cho tap {kind}")


def wmape(g):
    g = g.dropna(subset=["y_cham"])
    return (g.y_cham - g.du_bao).abs().sum() / g.y_cham.sum() if len(g) else float("nan")


ref = "seasonal_naive_7" if "seasonal_naive_7" in preds else next(iter(preds))
rows = []
for name, p in preds.items():
    full = p.ma_sku.nunique() == df.ma_sku.nunique()
    r = {"mo_hinh": name, "so_SKU": p.ma_sku.nunique()}
    r["WMAPE"] = score(p, df).WMAPE.iloc[0] if full else float("nan")
    r["WMAPE_tuan"] = score_week(p) if full else float("nan")
    r["Bias_pct"] = score(p, df).Bias_pct.iloc[0] if full else float("nan")
    for col, vals in [("abc_train", ["A"]), ("xyz_train", ["X", "Y", "Z"]), ("loai_nhu_cau", None)]:
        groups = vals or sorted(p[col].dropna().unique())
        for v in groups:
            key = f"WMAPE_{v.split(' ')[0]}" if col == "loai_nhu_cau" else f"WMAPE_{v}"
            sub = p[p[col] == v]
            r[key] = wmape(sub) if (full or col == "abc_train") else float("nan")
    rows.append(r)

t = pd.DataFrame(rows).set_index("mo_hinh")
if ref in t.index:
    t["FVA_vs_SN7"] = 1 - t.WMAPE / t.loc[ref, "WMAPE"]          # duong = tot hon Seasonal Naive 7
    t["FVA_A_vs_SN7"] = 1 - t.WMAPE_A / t.loc[ref, "WMAPE_A"]
t = t.sort_values("WMAPE", na_position="last")
os.makedirs("reports", exist_ok=True)
t.round(3).to_csv(f"reports/bang_so_sanh_{kind}.csv", encoding="utf-8-sig")

fmt = lambda v: "—" if pd.isna(v) else f"{v:.3f}".replace(".", ",")
cols = [c for c in t.columns if c != "so_SKU"]
lines = [f"# Bang so sanh mo hinh (tap {kind})", "",
         "WMAPE: thap hon = tot hon. FVA: muc giam sai so so voi Seasonal Naive 7 (duong = tot hon).",
         "Mo hinh chi chay mot nhom SKU (vd ARIMA chi nhom A) chi co cot cua nhom do; so sanh qua WMAPE_A.",
         "Du lieu mo phong, khong phai so lieu kho that.", "",
         "| Mo hinh | So SKU | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
for name, r in t.iterrows():
    lines.append(f"| {name} | {int(r.so_SKU)} | " + " | ".join(fmt(r[c]) for c in cols) + " |")
with open(f"reports/bang_so_sanh_{kind}.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
