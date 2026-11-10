"""Canh bao du bao bat dau lech (tracking signal). Luat ghi TRUOC khi chay: docs/10 muc 10.14. Chi doc CSDL, khong doi du bao hay chinh sach.
TS tai ngay lap phieu m = tong (thuc te - du bao) / MAD tren 28 ngay den het m; du bao cua moi ngay la ban moi nhat lap truoc ngay do.
Chay (tai thu muc goc hoac thu muc nguon): python src/canh_bao_lech.py -> reports/canh_bao_lech.md, reports/canh_bao_lech_trang_thai.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CUA_SO, TOI_THIEU = 28, 14
NGUONG_THU = [3, 4, 5, 6]
CUNG_CHIEU, BOI_SO, TI_LE_TOI_DA = 0.70, 2.0, 0.20          # luat 10.14
REPORT = "reports/canh_bao_lech.md"
STATE = "reports/canh_bao_lech_trang_thai.json"


def sai_so_moi_nhat(d):
    """d: ma_sku, ngay, moc, ngay_thu, du_bao, thuc_te. Moi (ma, ngay) lay ban du bao moi nhat (ngay_thu nho nhat); bo ngay khong co thuc te."""
    g = d.sort_values("ngay_thu", kind="stable").drop_duplicates(["ma_sku", "ngay"]).dropna(subset=["thuc_te"])
    return pd.DataFrame({"ma_sku": g.ma_sku.values, "ngay": pd.to_datetime(g.ngay).values, "e": (g.thuc_te - g.du_bao).values})


def tin_hieu(e, ngay, cua_so=CUA_SO, toi_thieu=TOI_THIEU):
    """TS tung ma tai ngay lap phieu: chi dung sai so cac ngay trong (ngay - cua_so, ngay]. Thieu ngay hoac MAD = 0 -> NaN."""
    t = pd.Timestamp(ngay)
    w = e[(e.ngay > t - pd.Timedelta(days=cua_so)) & (e.ngay <= t)]
    if not len(w):
        return pd.DataFrame(columns=["tong", "mad", "n", "ts"]).rename_axis("ma_sku")
    g = w.assign(a=w.e.abs()).groupby("ma_sku")
    r = pd.DataFrame({"tong": g.e.sum(), "mad": g.a.mean(), "n": g.e.size()})
    r["ts"] = np.where((r.n >= toi_thieu) & (r.mad > 0), r.tong / r.mad.where(r.mad > 0, 1.0), np.nan)
    return r


def lech_ke_tiep(d):
    """Do lech 28 ngay ke tiep cua du bao lap tai 1 moc: (tong thuc te - tong du bao) / tong du bao, chi ngay co thuc te. d: 1 moc."""
    x = d.dropna(subset=["thuc_te"])
    s = x.groupby("ma_sku").agg(y=("thuc_te", "sum"), f=("du_bao", "sum"))
    return ((s.y - s.f) / s.f.where(s.f > 0)).rename("b")


def danh_gia(bang, nguong):
    """bang: ts, b theo (ma, moc). Canh bao khi |ts| > nguong. Tra ve cac chi so cua luat 10.14."""
    x = bang.dropna(subset=["ts", "b"])
    cb = x.ts.abs() > nguong
    n_cb = int(cb.sum())
    cung = float((np.sign(x.ts[cb]) == np.sign(x.b[cb])).mean()) if n_cb else float("nan")
    m_cb, m_k = float(x.b[cb].abs().median()) if n_cb else float("nan"), float(x.b[~cb].abs().median()) if (~cb).any() else float("nan")
    boi = m_cb / m_k if n_cb and m_k > 0 else float("nan")
    ti_le = float(cb.mean()) if len(x) else float("nan")
    lau = float((x[cb].groupby(level="ma_sku").size() > 0.5 * x.index.get_level_values("moc").nunique()).sum()) if n_cb else 0.0
    dat = bool(n_cb and cung >= CUNG_CHIEU and boi >= BOI_SO and ti_le <= TI_LE_TOI_DA)
    return dict(nguong=nguong, so_cap=int(len(x)), so_canh_bao=n_cb, ti_le=ti_le, cung_chieu=cung, lech_cb=m_cb, lech_khong=m_k, boi=boi,
                ma_canh_bao_qua_nua=int(lau), dat=dat)


def chon_nguong(ket_qua):
    """Nguong nho nhat dat ca 3 dieu kien; khong co -> None."""
    dat = sorted(r["nguong"] for r in ket_qua if r["dat"])
    return dat[0] if dat else None


def bang_danh_gia(d, e, tap):
    """TS tai moi moc cua tap va do lech 28 ngay ke tiep -> bang (ma_sku, moc) x (ts, b)."""
    phan = []
    for moc, g in d[d.tap == tap].groupby("moc"):
        ts = tin_hieu(e, moc).ts
        b = lech_ke_tiep(g)
        phan.append(pd.DataFrame({"ts": ts, "b": b}).assign(moc=moc))
    return pd.concat(phan).rename_axis("ma_sku").reset_index().set_index(["ma_sku", "moc"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from csdl import doc
    from kiem_tra_du_lieu import nguon_du_lieu
    n = nguon_du_lieu()
    mh = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]
    d = doc("SELECT tap, moc, ngay, ma_sku, ngay_thu, du_bao, thuc_te FROM du_bao WHERE ma_mo_hinh = ? AND tap IN ('validation2', 'test')", (mh,))
    e = sai_so_moi_nhat(d)
    kq = {}
    for tap in ["validation2", "test"]:
        bg = bang_danh_gia(d, e, tap)
        kq[tap] = [danh_gia(bg, k) for k in NGUONG_THU]
        print(tap, [(r["nguong"], round(r["ti_le"], 3), round(r["cung_chieu"], 3), round(r["boi"], 2), r["dat"]) for r in kq[tap]], flush=True)
    nguong = chon_nguong(kq["validation2"])
    test = next((r for r in kq["test"] if r["nguong"] == nguong), None)
    json.dump(dict(nguon=n["ten"], mo_hinh=mh, nguong=nguong, cua_so=CUA_SO, toi_thieu=TOI_THIEU, validation2=kq["validation2"], test=test),
              open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    so = lambda v, nd=1: "–" if v != v else f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    dau = "| Ngưỡng \\|TS\\| | Cặp (mã, mốc) | Cảnh báo | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \\|lệch\\| có cảnh báo | Trung vị \\|lệch\\| không cảnh báo | Gấp | Mã bị cảnh báo quá nửa số mốc | Đạt luật |\n|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    dong = lambda r: (f"| {r['nguong']} | {so(r['so_cap'], 0)} | {so(r['so_canh_bao'], 0)} | {so(100 * r['ti_le'])}% | {so(100 * r['cung_chieu'])}% | {so(100 * r['lech_cb'])}% | "
                      f"{so(100 * r['lech_khong'])}% | {so(r['boi'], 2)} | {r['ma_canh_bao_qua_nua']} | {'✅' if r['dat'] else '❌'} |")
    L = ["# Cảnh báo dự báo bắt đầu lệch", "",
         f"Luật ghi trước: docs/10 mục 10.14. {'Dữ liệu mô phỏng' if n['la_mo_phong'] else 'Nguồn: ' + n['ten']}. Mô hình {mh}, dự báo gốc. "
         f"TS = tổng sai số / MAD trên {CUA_SO} ngày đến hết ngày lập phiếu (ít nhất {TOI_THIEU} ngày có thực tế). Lệch = (thực tế − dự báo) / dự báo của 28 ngày kế tiếp.", "",
         "## Validation2: chọn ngưỡng", "", dau] + [dong(r) for r in kq["validation2"]]
    L += ["", f"Theo luật: **{'ngưỡng |TS| > ' + str(nguong) if nguong is not None else 'không ngưỡng nào đạt, cảnh báo chưa đủ tin cậy'}**.", ""]
    if test:
        L += ["## Test (chỉ báo cáo, giữ ngưỡng)", "", dau, dong(test), ""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
