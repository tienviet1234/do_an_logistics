"""Cap nhat gia mat hang theo gia ban le thi truong (quyet dinh 24/10/2026, docs/09 muc 4).
Doc:  data/reference/gia_thi_truong.csv   (gia tra cuu tung ma: cach, nguon, ngay tra)
      data/reference/sku_master_mo_phong.csv (ban goc gia mo phong; tao tu dong o lan chay dau)
Ghi:  data/reference/sku_master.csv (gia_von, gia_ban, gia_tri_xuat_36t, phan_loai_ABC), reports/cap_nhat_gia.md
Chay: python src/cap_nhat_gia.py   (luon bat dau tu ban goc -> chay lai bao nhieu lan cung ra cung ket qua)
Sau do chay lai: eda, dac_trung, cac mo hinh, nap_database, ton_kho... (README).

Quy tac (gia dinh ghi ro):
  cach = tra_cuu    : gia_ban = gia ban le tra duoc (kho tong chuoi ban le -> cua hang mat dung gia ban le khi het hang).
                      gia_von = gia_ban / (gia_ban_cu / gia_von_cu): giu nguyen bien lai cu cua ma (gia nhap khong cong khai).
  cach = giu_nguyen : giu gia mo phong (hang chung chung khong co gia chuan, hoac khong tra duoc, hoac gia cu nam trong khoang tra duoc).
  gia_tri_xuat_36t, phan_loai_ABC tinh lai DUNG cach cua sinh_du_lieu.py (36 thang, qty_out ban sach goc x gia von, nguong 75% / 92%);
  truoc khi tinh, kiem tra cach tinh nay voi gia cu ra dung cot cu.
"""
import os
import shutil

import numpy as np
import pandas as pd

REF = "data/reference"
GOC = f"{REF}/sku_master_mo_phong.csv"
OUT = f"{REF}/sku_master.csv"
GIA = f"{REF}/gia_thi_truong.csv"
SACH = "data/answer_key/giao_dich_nhap_xuat_ton_SACH.csv"   # chi dung luong xuat de tinh gia tri (khong dua vao mo hinh)
REPORT = "reports/cap_nhat_gia.md"
csv = lambda p: pd.read_csv(p, encoding="utf-8-sig")
vn = lambda v: f"{v:,.0f}".replace(",", ".")


def gia_tri_va_abc(sku, tx):
    """Giong sinh_du_lieu.py: gia tri xuat 36 thang = qty_out x gia_von; ABC theo ty le cong don 75% / 92%."""
    val = (tx.qty_out * tx.ma_sku.map(sku.set_index("ma_sku").gia_von)).groupby(tx.ma_sku).sum().sort_values(ascending=False)
    cum = val.cumsum() / val.sum()
    abc = pd.Series(np.where(cum <= 0.75, "A", np.where(cum <= 0.92, "B", "C")), index=val.index)
    abc.iloc[0] = "A"
    return val, abc


if __name__ == "__main__":
    if not os.path.exists(GOC):
        shutil.copyfile(OUT, GOC)
        print(f"Tao ban goc {GOC} (gia mo phong ban dau)")
    goc, gia, tx = csv(GOC), csv(GIA), csv(SACH)
    assert set(gia.ma_sku) == set(goc.ma_sku) and len(gia) == len(goc), "gia_thi_truong.csv phai du 121 ma"
    assert gia.cach.isin(["tra_cuu", "giu_nguyen"]).all()

    # 1. kiem tra cach tinh voi gia cu
    val0, abc0 = gia_tri_va_abc(goc, tx)
    g0 = goc.set_index("ma_sku")
    assert np.allclose(val0.reindex(g0.index), g0.gia_tri_xuat_36t), "cach tinh gia tri xuat khong khop sinh_du_lieu.py"
    assert (abc0.reindex(g0.index) == g0.phan_loai_ABC).all(), "cach tinh ABC khong khop sinh_du_lieu.py"

    # 2. gia moi
    sku = goc.copy()
    m = sku.merge(gia[["ma_sku", "cach", "gia_ban_moi"]], on="ma_sku")
    doi = m.cach == "tra_cuu"
    bien = m.gia_ban / m.gia_von
    sku.loc[doi.values, "gia_ban"] = m.loc[doi, "gia_ban_moi"].astype(float).values
    sku.loc[doi.values, "gia_von"] = (np.round(m.loc[doi, "gia_ban_moi"] / bien[doi] / 500) * 500).astype(int).values
    val, abc = gia_tri_va_abc(sku, tx)
    sku["gia_tri_xuat_36t"] = sku.ma_sku.map(val).round().astype("int64")
    sku["phan_loai_ABC"] = sku.ma_sku.map(abc)
    assert (sku.gia_ban > sku.gia_von).all() and (sku.gia_von > 0).all()
    sku.to_csv(OUT, index=False, encoding="utf-8-sig")

    # 3. bao cao
    c = goc[["ma_sku", "ten_sku", "gia_von", "gia_ban", "phan_loai_ABC"]].merge(
        sku[["ma_sku", "gia_von", "gia_ban", "phan_loai_ABC"]], on="ma_sku", suffixes=("_cu", "_moi"))
    ch = c[c.gia_ban_cu != c.gia_ban_moi].assign(ty_le=lambda f: (f.gia_ban_moi / f.gia_ban_cu).round(2)).sort_values("ty_le")
    abc_doi = c[c.phan_loai_ABC_cu != c.phan_loai_ABC_moi]
    tong0, tong1 = val0.sum(), val.sum()
    L = ["# Cap nhat gia mat hang theo gia ban le thi truong", "",
         f"Tra ngay 2026-10-24, nguon tung ma: `{GIA}`. Kho duoc coi la kho tong chuoi sieu thi / bach hoa (docs/09 muc 4).",
         "gia_ban = gia ban le tra duoc; gia_von = gia_ban / (bien lai cu cua ma) la **gia dinh** (gia nhap khong cong khai). "
         "Du lieu nhu cau, giao dich van la mo phong.", "",
         f"- Ma doi gia: **{doi.sum()}**; giu gia cu: {(~doi).sum()} "
         f"({(gia.cach == 'giu_nguyen').sum()} ma: hang chung chung / khong tra duoc / gia cu nam trong khoang tra duoc).",
         f"- Gia moi / gia cu (ma doi gia): trung vi x{ch.ty_le.median():.2f}, thap nhat x{ch.ty_le.min():.2f}, cao nhat x{ch.ty_le.max():.2f}.",
         f"- Tong gia tri xuat 36 thang (gia von): {vn(tong0 / 1e9)} ty -> {vn(tong1 / 1e9)} ty ({(tong1 / tong0 - 1) * 100:+.1f}%).",
         f"- ABC (36 thang) truoc: {abc0.value_counts().sort_index().to_dict()} -> sau: {abc.value_counts().sort_index().to_dict()}; "
         f"{len(abc_doi)} ma doi nhom.", "",
         "## Ma doi gia", "", ch.to_markdown(index=False), "",
         "## Ma doi nhom ABC (36 thang)", "", abc_doi.to_markdown(index=False) if len(abc_doi) else "(khong co)", ""]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[5:9]))
    print(f"Da ghi {OUT}, {REPORT}")
