"""Canh bao du bao lech, VONG 2. Luat ghi TRUOC khi chay: docs/10 muc 10.14 (vong 2). Chi doc CSDL, khong doi du bao hay chinh sach.
Khac vong 1: sai so gop theo tuan (TS = tong 4 tuan / MAD 13 tuan), sai so = so ban thuc te - du bao.
Phan 1 (lech keo dai, ca hai bo): dieu kien a, b, c nhu vong 1. Phan 2 (thay doi dot ngot, chi bo mo phong): dap an doc tu src/sinh_du_lieu.py bang ast.
Chay (tai thu muc goc hoac thu muc nguon): python src/canh_bao_lech_v2.py -> reports/canh_bao_lech_v2.md, reports/canh_bao_lech_v2_trang_thai.json
"""
import ast
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canh_bao_lech import NGUONG_THU, chon_nguong, danh_gia  # noqa: E402

SO_TUAN_TONG, SO_TUAN_MAD = 4, 13
NGAY_TOI_THIEU_TUAN, TUAN_TOI_THIEU_TONG, TUAN_TOI_THIEU_MAD = 4, 3, 8
HE_SO_TOI_THIEU, DOT_TOI_THIEU = 0.5, 7                           # (ma, dot): he so tac dong >= 0,5; dot dai >= 7 ngay
PHAT_HIEN, GAP_NEN, CANH_BAO_NEN = 0.5, 3.0, 0.20                 # dieu kien d, e, c'
KHONG_SU_KIEN_TRUOC, KHONG_SU_KIEN_SAU = 27, 7                    # cap (ma, moc) "khong co su kien": khong dot nao giao [m - 27, m + 7]
REPORT = "reports/canh_bao_lech_v2.md"
STATE = "reports/canh_bao_lech_v2_trang_thai.json"
NGUON_SINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sinh_du_lieu.py")


def sai_so_ban(d, ban):
    """d: du bao (ma_sku, ngay, ngay_thu, du_bao); ban: (ma_sku, ngay, qty_out, la_ngay_nghi). Moi (ma, ngay) lay du bao moi nhat; chi ngay mo cua.
    e = so ban - du bao."""
    g = d.sort_values("ngay_thu", kind="stable").drop_duplicates(["ma_sku", "ngay"])[["ma_sku", "ngay", "du_bao"]]
    g = g.assign(ngay=pd.to_datetime(g.ngay))
    b = ban.assign(ngay=pd.to_datetime(ban.ngay))
    x = g.merge(b[b.la_ngay_nghi == 0][["ma_sku", "ngay", "qty_out"]], on=["ma_sku", "ngay"], how="inner")
    return pd.DataFrame({"ma_sku": x.ma_sku.values, "ngay": x.ngay.values, "e": (x.qty_out - x.du_bao).values})


def tin_hieu_tuan(e, ngay):
    """TS theo tuan tai ngay lap phieu: tuan j = (ngay - 7j - 7, ngay - 7j]. Tra ve DataFrame theo ma: rsfe, mad, ts."""
    t = pd.Timestamp(ngay)
    w = e[(e.ngay > t - pd.Timedelta(days=7 * SO_TUAN_MAD)) & (e.ngay <= t)]
    if not len(w):
        return pd.DataFrame(columns=["rsfe", "mad", "ts"]).rename_axis("ma_sku")
    j = ((t - w.ngay).dt.days // 7).values
    g = w.assign(j=j).groupby(["ma_sku", "j"]).e.agg(["sum", "size"])
    tuan = g["sum"].where(g["size"] >= NGAY_TOI_THIEU_TUAN).unstack("j").reindex(columns=range(SO_TUAN_MAD))
    gan = tuan.iloc[:, :SO_TUAN_TONG]
    rsfe = gan.sum(axis=1, min_count=1)
    mad = tuan.abs().mean(axis=1)
    du = (gan.notna().sum(axis=1) >= TUAN_TOI_THIEU_TONG) & (tuan.notna().sum(axis=1) >= TUAN_TOI_THIEU_MAD) & (mad > 0)
    return pd.DataFrame({"rsfe": rsfe, "mad": mad, "ts": np.where(du, rsfe / mad.where(mad > 0, 1.0), np.nan)})


def lech_ke_tiep_ban(dmoc, ban):
    """Do lech 28 ngay ke tiep cua du bao lap tai 1 moc, theo so ban (chi ngay mo cua): (tong ban - tong du bao) / tong du bao."""
    b = ban.assign(ngay=pd.to_datetime(ban.ngay))
    x = dmoc.assign(ngay=pd.to_datetime(dmoc.ngay)).merge(b[b.la_ngay_nghi == 0][["ma_sku", "ngay", "qty_out"]], on=["ma_sku", "ngay"], how="inner")
    s = x.groupby("ma_sku").agg(y=("qty_out", "sum"), f=("du_bao", "sum"))
    return ((s.y - s.f) / s.f.where(s.f > 0)).rename("b")


def doc_dap_an(duong=NGUON_SINH):
    """Doc danh sach dot (OTHER) va he so tac dong theo tu khoa (OTHER_AFF) tu trinh sinh du lieu, KHONG chay trinh sinh."""
    cay = ast.parse(open(duong, encoding="utf-8").read())
    gia_tri = {}
    for nut in cay.body:
        if isinstance(nut, ast.Assign) and len(nut.targets) == 1 and isinstance(nut.targets[0], ast.Name) and nut.targets[0].id in ("OTHER", "OTHER_AFF"):
            gia_tri[nut.targets[0].id] = ast.literal_eval(nut.value)
    if set(gia_tri) != {"OTHER", "OTHER_AFF"}:
        raise ValueError("Khong tim thay OTHER / OTHER_AFF trong trinh sinh du lieu")
    return [(o[0], o[2], o[3]) for o in gia_tri["OTHER"]], gia_tri["OTHER_AFF"]


def he_so_cua_ma(ten, bang_tu_khoa):
    """Cung cach trinh sinh: duyet tu khoa theo thu tu, tu khoa khop SAU ghi de he so truoc."""
    a = None
    for kw, he_so in bang_tu_khoa.items():
        if kw in ten:
            a = he_so
    return a


def cap_su_kien(ten_sku, dot, aff, he_so_min=HE_SO_TOI_THIEU, dai_min=DOT_TOI_THIEU):
    """ten_sku: {ma: ten}. Tra ve (danh sach (ma, khoa, tu, den, he_so), so dot bi loai vi ngan)."""
    ra, ngan = [], 0
    for khoa, tu, den in dot:
        if khoa not in aff:
            continue
        if (pd.Timestamp(den) - pd.Timestamp(tu)).days + 1 < dai_min:
            ngan += 1
            continue
        for ma, ten in ten_sku.items():
            a = he_so_cua_ma(ten, aff[khoa])
            if a is not None and a >= he_so_min:
                ra.append((ma, khoa, pd.Timestamp(tu), pd.Timestamp(den), a))
    return ra, ngan


def moc_phat_hien(tu, cac_moc):
    """Moc tuan dau tien da thay it nhat 7 ngay cua dot (moc >= tu + 6 ngay); khong co -> None."""
    m = [x for x in sorted(cac_moc) if x >= tu + pd.Timedelta(days=DOT_TOI_THIEU - 1)]
    return m[0] if m else None


def khong_su_kien(ma, moc, cap):
    """Cap (ma, moc) khong co dot nao cua ma giao [moc - 27, moc + 7]."""
    lo, hi = moc - pd.Timedelta(days=KHONG_SU_KIEN_TRUOC), moc + pd.Timedelta(days=KHONG_SU_KIEN_SAU)
    return not any(c[0] == ma and c[2] <= hi and c[3] >= lo for c in cap)


def danh_gia_dot_bien(ts, cap, cac_moc, nguong):
    """ts: Series theo (ma_sku, moc). Phat hien = TS > nguong tai moc phat hien. Nen = cap khong co su kien."""
    cac_moc = sorted(cac_moc)
    det = []
    for ma, khoa, tu, den, a in cap:
        m = moc_phat_hien(tu, cac_moc)
        if m is None or m > den + pd.Timedelta(days=7):
            continue
        v = ts.get((ma, m), np.nan)
        if v == v:
            det.append(v > nguong)
    nen = ts[[khong_su_kien(ma, m, cap) for ma, m in ts.index]].dropna()
    ti_le_det = float(np.mean(det)) if det else float("nan")
    duong = float((nen > nguong).mean()) if len(nen) else float("nan")
    tuyet_doi = float((nen.abs() > nguong).mean()) if len(nen) else float("nan")
    gap = ti_le_det / duong if duong and duong == duong and duong > 0 else (float("inf") if ti_le_det == ti_le_det and ti_le_det > 0 else float("nan"))
    dat = bool(det and ti_le_det >= PHAT_HIEN and gap >= GAP_NEN and tuyet_doi <= CANH_BAO_NEN)
    return dict(nguong=nguong, so_cap_dot=len(det), phat_hien=ti_le_det, so_cap_nen=int(len(nen)), nen_duong=duong, nen_tuyet_doi=tuyet_doi, gap=gap, dat=dat)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from csdl import doc
    from kiem_tra_du_lieu import nguon_du_lieu
    n = nguon_du_lieu()
    mh = doc("SELECT ma_mo_hinh FROM mo_hinh WHERE duoc_chon = 1").ma_mo_hinh.iloc[0]
    d = doc("SELECT tap, moc, ngay, ma_sku, ngay_thu, du_bao FROM du_bao WHERE ma_mo_hinh = ? AND tap IN ('validation2', 'test')", (mh,))
    ban = doc("SELECT ngay, ma_sku, qty_out, la_ngay_nghi FROM giao_dich_sach")
    e = sai_so_ban(d, ban)
    cap, ngan = [], 0
    if n["la_mo_phong"]:
        dot, aff = doc_dap_an()
        ten = dict(doc("SELECT ma_sku, ten_sku FROM dm_sku").values)
        cap, ngan = cap_su_kien(ten, dot, aff)
    kq, dbg = {}, {}
    for tap in ["validation2", "test"]:
        phan = []
        for moc, g in d[d.tap == tap].groupby("moc"):
            m = pd.Timestamp(moc)
            phan.append(pd.DataFrame({"ts": tin_hieu_tuan(e, m).ts, "b": lech_ke_tiep_ban(g, ban)}).assign(moc=m))
        bg = pd.concat(phan).rename_axis("ma_sku").reset_index().set_index(["ma_sku", "moc"])
        kq[tap] = dict(p1=[danh_gia(bg, k) for k in NGUONG_THU])
        if cap:
            kq[tap]["p2"] = [danh_gia_dot_bien(bg.ts, cap, bg.index.get_level_values("moc").unique(), k) for k in NGUONG_THU]
        print(tap, "p1", [(r["nguong"], round(r["ti_le"], 3), round(r["cung_chieu"], 3), round(r["boi"], 2), r["dat"]) for r in kq[tap]["p1"]], flush=True)
        if cap:
            print(tap, "p2", [(r["nguong"], r["so_cap_dot"], round(r["phat_hien"], 3), round(r["nen_duong"], 3), round(r["nen_tuyet_doi"], 3), r["dat"]) for r in kq[tap]["p2"]], flush=True)
    chon = {"p1": chon_nguong(kq["validation2"]["p1"])}
    if cap:
        chon["p2"] = chon_nguong(kq["validation2"]["p2"])
    test = {p: next((r for r in kq["test"][p] if r["nguong"] == k), None) for p, k in chon.items()}
    json.dump(dict(nguon=n["ten"], mo_hinh=mh, nguong=chon, so_cap_dot=len(cap), so_dot_ngan_bi_loai=ngan, validation2=kq["validation2"], test=test),
              open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    so = lambda v, nd=1: "–" if v != v else ("∞" if v == float("inf") else f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", "."))
    d1 = "| Ngưỡng \\|TS\\| | Cặp (mã, mốc) | Tỉ lệ cảnh báo | Cùng chiều | Trung vị \\|lệch\\| có / không cảnh báo | Gấp | Đạt (a, b, c) |\n|---:|---:|---:|---:|---:|---:|---|"
    r1 = lambda r: f"| {r['nguong']} | {so(r['so_cap'], 0)} | {so(100 * r['ti_le'])}% | {so(100 * r['cung_chieu'])}% | {so(100 * r['lech_cb'])}% / {so(100 * r['lech_khong'])}% | {so(r['boi'], 2)} | {'✅' if r['dat'] else '❌'} |"
    d2 = "| Ngưỡng | (mã, đợt) xét được | Phát hiện | Cặp không sự kiện | TS > ngưỡng ở cặp không sự kiện | \\|TS\\| > ngưỡng ở cặp không sự kiện | Gấp | Đạt (d, e, c') |\n|---:|---:|---:|---:|---:|---:|---:|---|"
    r2 = lambda r: f"| {r['nguong']} | {r['so_cap_dot']} | {so(100 * r['phat_hien'])}% | {so(r['so_cap_nen'], 0)} | {so(100 * r['nen_duong'])}% | {so(100 * r['nen_tuyet_doi'])}% | {so(r['gap'], 2)} | {'✅' if r['dat'] else '❌'} |"
    L = ["# Cảnh báo dự báo lệch, vòng 2", "",
         f"Luật ghi trước: docs/10 mục 10.14 (vòng 2). {'Dữ liệu mô phỏng' if n['la_mo_phong'] else 'Nguồn: ' + n['ten']}. Mô hình {mh}, dự báo gốc. "
         f"TS = tổng sai số {SO_TUAN_TONG} tuần / MAD theo tuần của {SO_TUAN_MAD} tuần; sai số = số bán − dự báo.", "",
         "## Phần 1: lệch kéo dài, validation2", "", d1] + [r1(r) for r in kq["validation2"]["p1"]]
    L += ["", f"Theo luật: **{'ngưỡng |TS| > ' + str(chon['p1']) if chon['p1'] is not None else 'không ngưỡng nào đạt'}**.", ""]
    if cap:
        L += ["## Phần 2: thay đổi đột ngột, validation2", "", f"{len(cap)} cặp (mã, đợt) có hệ số tác động ≥ {so(HE_SO_TOI_THIEU)} trong các đợt dài ≥ {DOT_TOI_THIEU} ngày (cả kỳ dữ liệu); {ngan} đợt ngắn hơn bị loại. "
              "Bão và đơn B2B nằm ngoài phạm vi.", "", d2] + [r2(r) for r in kq["validation2"]["p2"]]
        L += ["", f"Theo luật: **{'ngưỡng TS > ' + str(chon['p2']) if chon['p2'] is not None else 'không ngưỡng nào đạt'}**.", ""]
    if any(test.values()):
        L += ["## Test (chỉ báo cáo, giữ ngưỡng)", ""]
        if test.get("p1"):
            L += ["Phần 1:", "", d1, r1(test["p1"]), ""]
        if test.get("p2"):
            L += ["Phần 2:", "", d2, r2(test["p2"]), ""]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
