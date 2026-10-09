"""Buoc 1-5: kiem tra va lam sach du lieu nhap-xuat-ton tho.

Chay (tu thu muc goc du an):
    python src/lam_sach.py

Dau vao : data/raw/giao_dich_nhap_xuat_ton_THO.csv
          data/reference/sku_master.csv, lich_ngay_nghi_kho.csv
Dau ra  : data/clean/giao_dich_sach.csv
          reports/bao_cao_lam_sach.md, reports/dong_da_sua.csv
Neu co data/answer_key/ (chi co voi du lieu mo phong) thi doi chieu ket qua.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/giao_dich_nhap_xuat_ton_THO.csv"
REF = ROOT / "data/reference"
KEY = ROOT / "data/answer_key"
CLEAN = ROOT / "data/clean"
REP = ROOT / "reports"
CLEAN.mkdir(exist_ok=True); REP.mkdir(exist_ok=True)

lines = []  # noi dung bao cao
def say(s=""):
    print(s); lines.append(s)

# ---------- Buoc 1: doc va kiem tra cau truc ----------
df = pd.read_csv(RAW, encoding="utf-8-sig", parse_dates=["date"])
sku = pd.read_csv(REF / "sku_master.csv", encoding="utf-8-sig")
nghi = pd.read_csv(REF / "lich_ngay_nghi_kho.csv", encoding="utf-8-sig", parse_dates=["date"])
say("# Bao cao lam sach du lieu\n")
say("## 1. Cau truc")
say(f"- So dong ban dau: {len(df):,}; so SKU: {df.ma_sku.nunique()}; "
    f"tu {df.date.min().date()} den {df.date.max().date()}")
say(f"- O trong theo cot: {df.isna().sum()[df.isna().sum() > 0].to_dict()}")

# ---------- Buoc 2: lam sach loi nhap lieu ----------
say("\n## 2. Lam sach")
df["ma_sku"] = df["ma_sku"].astype(str).str.strip().str.upper()
la_la = ~df.ma_sku.isin(sku.ma_sku)
say(f"- Dong co SKU khong co trong SKU_master: {int(la_la.sum())}")
df = df[~la_la]

trung = df.duplicated(keep="first")
n_trung = int(trung.sum())
say(f"- Dong trung hoan toan (loai bo): {n_trung}")
df = df[~trung]
trung_khoa = int(df.duplicated(["date", "ma_sku"]).sum())
say(f"- Con trung theo (ngay, SKU) sau khi loai: {trung_khoa} (neu > 0 can xem tay)")
df = df.sort_values(["ma_sku", "date"]).reset_index(drop=True)

# Du ngay cho moi SKU?
n_ngay = (df.date.max() - df.date.min()).days + 1
thieu = df.groupby("ma_sku").size().rsub(n_ngay)
say(f"- SKU thieu ngay trong chuoi: {int((thieu > 0).sum())}")

# ---------- Buoc 3: kiem tra logic kho ----------
# Dinh luat: ton_cuoi = ton_dau + nhap - xuat  =>  xuat = ton_dau + nhap - ton_cuoi
say("\n## 3. Kiem tra logic kho (ton_cuoi = ton_dau + nhap - xuat)")
ton0 = sku.set_index("ma_sku")["ton_kho_ban_dau"]
df["ton_dau"] = df.groupby("ma_sku")["ton_cuoi_ngay"].shift(1)
dau = df.ton_dau.isna()
df.loc[dau, "ton_dau"] = df.loc[dau, "ma_sku"].map(ton0)
df["qty_out_suy_ra"] = df.ton_dau + df.qty_in - df.ton_cuoi_ngay
am = int((df.ton_cuoi_ngay < 0).sum())
say(f"- Dong co ton cuoi am: {am}")
say(f"- Dong co qty_out suy ra am (vo ly): {int((df.qty_out_suy_ra < 0).sum())}")

# Ngay kho dong cua phai khong co xuat
df["la_ngay_nghi"] = df.date.isin(nghi.date).astype(int)
vi_pham = df[(df.la_ngay_nghi == 1) & (df.qty_out_suy_ra.fillna(0) > 0)]
say(f"- Dong xuat hang vao ngay kho dong cua: {len(vi_pham)}")

# ---------- Buoc 4: phan biet loi nhap voi dot bien that ----------
say("\n## 4. Loi nhap lieu hay dot bien that")
thieu_out = df.qty_out.isna()
lech = (~thieu_out) & ((df.qty_out - df.qty_out_suy_ra).abs() > 0.5)
say(f"- qty_out bi thieu (NaN): {int(thieu_out.sum())}")
say(f"- qty_out khac gia tri suy ra tu ton kho (nghi nhap sai): {int(lech.sum())}")
say("  Cach xu ly: dot bien that (bao, sale) van khop voi ton kho nen KHONG bi coi la loi.")
say("  Chi dong lech voi ton kho moi bi sua.")

fix = df[thieu_out | lech][["date", "ma_sku", "qty_out", "qty_out_suy_ra"]].copy()
fix["loai_loi"] = np.where(fix.qty_out.isna(), "thieu_qty_out", "outlier_nhap_sai")
fix.rename(columns={"qty_out": "qty_out_tho", "qty_out_suy_ra": "qty_out_da_sua"}).to_csv(
    REP / "dong_da_sua.csv", index=False, encoding="utf-8-sig")

df["co_sua"] = (thieu_out | lech).astype(int)
df["qty_out"] = df["qty_out_suy_ra"]  # dung gia tri suy ra tu ton kho
say(f"- Da sua: {int(df.co_sua.sum())} dong (chi tiet o reports/dong_da_sua.csv)")

# ---------- Buoc 5: ngay het hang (cau bi che) ----------
say("\n## 5. Ngay het hang")
df["het_hang"] = (df.ton_cuoi_ngay <= 0).astype(int)
say(f"- Ngay ton cuoi = 0: {int(df.het_hang.sum())} dong "
    f"({df.het_hang.mean()*100:.2f}% tong so dong)")
say("- Tren cac ngay nay, luong xuat THAP HON cau that vi khong du hang.")
say("  Khi huan luyen mo hinh can loai ra hoac uoc luong lai (xem buoc dac trung).")

out = df[["date", "ma_sku", "qty_in", "qty_out", "ton_cuoi_ngay", "la_ngay_nghi", "het_hang", "co_sua"]]
out.to_csv(CLEAN / "giao_dich_sach.csv", index=False, encoding="utf-8-sig")
say(f"\n=> Da ghi {len(out):,} dong vao data/clean/giao_dich_sach.csv")

# ---------- Doi chieu dap an (chi du lieu mo phong) ----------
if (KEY / "giao_dich_nhap_xuat_ton_SACH.csv").exists():
    say("\n## 6. Doi chieu voi dap an (du lieu mo phong)")
    ans = pd.read_csv(KEY / "giao_dich_nhap_xuat_ton_SACH.csv", encoding="utf-8-sig", parse_dates=["date"])
    m = out.merge(ans[["date", "ma_sku", "qty_out"]], on=["date", "ma_sku"], suffixes=("", "_dung"))
    sai = (m.qty_out - m.qty_out_dung).abs() > 0.5
    say(f"- So dong khop khoa (ngay, SKU) voi dap an: {len(m):,} / {len(ans):,}")
    say(f"- Dong qty_out con sai so voi dap an: {int(sai.sum())}")
    log = pd.read_csv(KEY / "nhat_ky_loi_co_chu_dich.csv", encoding="utf-8-sig")
    log = log[log.loai_loi != "loai_loi"]
    cai = log.loai_loi.value_counts()
    say(f"- Loi da cai san: {cai.to_dict()}")
    say(f"- Loi dong_trung phat hien: {n_trung} (cai san {cai.get('dong_trung', 0)})")
    say(f"- Loi thieu/outlier da sua: {int(df.co_sua.sum())} "
        f"(cai san {cai.get('thieu_qty_out', 0) + cai.get('outlier_nhap_sai', 0)})")

(REP / "bao_cao_lam_sach.md").write_text("\n".join(lines), encoding="utf-8")
