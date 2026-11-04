"""Cham diem nha cung cap va canh bao giao cham. Luat ghi TRUOC khi chay: docs/10 muc 10.7. Ham thuan co test; chi doc CSDL.
Tu cac don mo phong cua chinh sach AI + hieu chinh: lead time hen (L = lead time TB lam tron) so voi thuc te. Mo phong luon giao du hang nen chi do DUNG HAN, chua do DU HANG (OTIF).
Canh bao chi dung don DA VE tai thoi diem xet (khong nhin truoc).
Chay: python src/cham_diem_ncc.py -> reports/cham_diem_ncc.md, reports/cham_diem_ncc.csv, reports/cham_diem_ncc_trang_thai.json
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TRE_CHO_PHEP = 1                 # tre toi da 1 ngay van tinh dung han
TRON_SO_DUNG_HAN = 0.6           # trong so trong diem (gia dinh), con lai cho do on dinh
LECH_TOI_DA = 5.0                # do lech chuan tre tu 5 ngay tro len: diem on dinh = 0
SO_DON_CANH_BAO, NGUONG_CANH_BAO = 8, 2.0      # trung binh tre cua 8 don vua ve >= 2 ngay thi canh bao
BIEN_SAU_SU_KIEN = 20            # don dat trong dot chiu anh huong ve muon: cua so xet them 20 ngay sau su kien
LOP = [(85, "Tốt"), (70, "Trung bình"), (0, "Cần theo dõi")]
CSV_RA, STATE, REPORT = "reports/cham_diem_ncc.csv", "reports/cham_diem_ncc_trang_thai.json", "reports/cham_diem_ncc.md"


def bang_don(dat, lt_thuc, ma, ncc, lead_tb):
    """Moi dong 1 don. dat, lt_thuc: mang (ma, ngay). tre = thuc te - hen; ve = chi so ngay hang ve."""
    i, t = np.nonzero(np.asarray(dat) > 0)
    hen = np.maximum(1, np.round(np.asarray(lead_tb, dtype=float)).astype(int))
    d = pd.DataFrame({"ma": np.asarray(ma)[i], "ncc": np.asarray(ncc)[i], "t": t, "hen": hen[i], "thuc": np.asarray(lt_thuc)[i, t]})
    return d.assign(tre=d.thuc - d.hen, ve=d.t + d.thuc)


def xep_lop(diem):
    return next(ten for nguong, ten in LOP if diem >= nguong)


def cham_diem(don, trong_so=TRON_SO_DUNG_HAN):
    """Chi tieu va diem tung nha cung cap (0-100, cao la tot), xep tu tot den kem. Khong co don -> bang rong."""
    if don.empty:
        return pd.DataFrame(columns=["ncc", "so_don", "dung_han_pt", "tre_tb", "tre_max", "tre_tu_3_pt", "lech_chuan", "diem", "xep_loai"])
    g = don.groupby("ncc").tre
    b = pd.DataFrame({"so_don": g.size(), "dung_han_pt": g.apply(lambda s: 100 * (s <= TRE_CHO_PHEP).mean()), "tre_tb": g.apply(lambda s: s.clip(lower=0).mean()), "tre_max": g.max(),
                      "tre_tu_3_pt": g.apply(lambda s: 100 * (s >= 3).mean()), "lech_chuan": g.std(ddof=0)}).reset_index()
    on_dinh = 1 - (b.lech_chuan / LECH_TOI_DA).clip(upper=1)
    b["diem"] = 100 * (trong_so * b.dung_han_pt / 100 + (1 - trong_so) * on_dinh)
    b["xep_loai"] = b.diem.map(xep_lop)
    return b.sort_values(["diem", "ncc"], ascending=[False, True]).reset_index(drop=True)


def canh_bao(don, so_don=SO_DON_CANH_BAO, nguong=NGUONG_CANH_BAO):
    """Cac ngay canh bao tung nha cung cap: tai moi ngay co hang ve, trung binh tre cua so_don don DA VE gan nhat >= nguong."""
    ra = {}
    for n, g in don.sort_values(["ve", "t"]).groupby("ncc"):
        tre = g.tre.values.astype(float)
        trung_binh = pd.Series(tre).rolling(so_don, min_periods=so_don).mean().values
        ngay = np.sort(np.unique(g.ve.values[np.nan_to_num(trung_binh, nan=-1e9) >= nguong]))
        ra[n] = ngay.astype(int).tolist()
    return ra


def danh_gia_canh_bao(bao, su_kien_ncc, chung, bien=BIEN_SAU_SU_KIEN):
    """su_kien_ncc: {ncc: [(tu, den)]} dot giao cham rieng; chung: [(tu, den)] ap cho moi ncc (bao). Tinh theo chi so ngay.
    Tra ve so dot phat hien duoc, so ngay tu dau dot den canh bao dau, so canh bao ngoai moi cua so (bao nham)."""
    phat_hien, cho, nham, tong_bao = [], [], 0, 0
    for n, dot in su_kien_ncc.items():
        for tu, den in dot:
            trung = [x for x in bao.get(n, []) if tu <= x <= den + bien]
            phat_hien.append(bool(trung))
            if trung:
                cho.append(trung[0] - tu)
    for n, ngay in bao.items():
        cua_so = list(su_kien_ncc.get(n, [])) + list(chung)
        tong_bao += len(ngay)
        nham += sum(not any(tu <= x <= den + bien for tu, den in cua_so) for x in ngay)
    return dict(so_dot=len(phat_hien), phat_hien=int(sum(phat_hien)), ngay_cho=cho, tong_ngay_canh_bao=tong_bao, bao_nham=nham)


def su_kien(inp):
    """Dot giao cham theo chi so ngay cua ky, tu su_kien_dot_bien (khong co thi rong)."""
    from csdl import doc
    s = doc("SELECT nhom_ly_do, su_kien, tu_ngay, den_ngay FROM su_kien_dot_bien WHERE nhom_ly_do IN ('Đứt gãy cung ứng', 'Thiên tai')")
    dau = inp["days"][0]
    chi_so = lambda x: (pd.Timestamp(x) - dau).days
    n_ngay = len(inp["days"])
    rieng, chung = {}, []
    for r in s.itertuples():
        a, b = chi_so(r.tu_ngay), chi_so(r.den_ngay)
        if b < 0 or a >= n_ngay:
            continue
        if r.nhom_ly_do == "Thiên tai":
            chung.append((a - 1, b))
        else:
            m = re.search(r"NCC\d+", r.su_kien)
            if m:
                rieng.setdefault(m.group(), []).append((a, b))
    return rieng, chung


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from gom_don import chuan_bi, mo_phong
    ket, bang_tap = {}, {}
    for tap in ["validation2", "test"]:
        inp, F, sig, z, buoc = chuan_bi(tap)
        ra = mo_phong(inp, F, sig, z, buoc)
        don = bang_don(ra["dat"], inp["LT"], inp["sku"].ma_sku, inp["sku"].ma_ncc, inp["sku"].lead_time_tb)
        b = cham_diem(don)
        bang_tap[tap] = b
        rieng, chung = su_kien(inp)
        bao = canh_bao(don)
        dau = inp["days"][0]
        ket[tap] = dict(so_don=len(don), dung_han_pt=float(100 * (don.tre <= TRE_CHO_PHEP).mean()), tre_tb=float(don.tre.clip(lower=0).mean()),
                        danh_gia=danh_gia_canh_bao(bao, rieng, chung), su_kien={k: [[str((dau + pd.Timedelta(days=a)).date()), str((dau + pd.Timedelta(days=c)).date())] for a, c in v] for k, v in rieng.items()},
                        canh_bao_dau={k: str((dau + pd.Timedelta(days=rv[0])).date()) for k, rv in bao.items() if rv},
                        hang_trong_so_khac=float(b.set_index("ncc").diem.corr(cham_diem(don, 0.8).set_index("ncc").diem, method="spearman")))
    t = bang_tap["test"]
    t.round(2).to_csv(CSV_RA, index=False, encoding="utf-8-sig")
    json.dump(ket, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    so = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    dg = ket["test"]["danh_gia"]
    L = ["# Chấm điểm nhà cung cấp", "", "Luật ghi trước: docs/10 mục 10.7. Dữ liệu mô phỏng: lead time được sinh theo quy tắc, nên bảng này **minh họa phương pháp**, không đánh giá một nhà cung cấp thật. "
         "Mô phỏng luôn giao đủ hàng nên chỉ đo đúng hạn, chưa đo đủ hàng (OTIF).", "", f"## Test: {ket['test']['so_don']} đơn, đúng hạn {so(ket['test']['dung_han_pt'])}%", "",
         "| Nhà cung cấp | Số đơn | Đúng hạn | Trễ TB (ngày) | Trễ lớn nhất | Trễ ≥ 3 ngày | Lệch chuẩn | Điểm | Xếp loại |", "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    L += [f"| {r.ncc} | {r.so_don} | {so(r.dung_han_pt)}% | {so(r.tre_tb, 2)} | {int(r.tre_max)} | {so(r.tre_tu_3_pt)}% | {so(r.lech_chuan, 2)} | {so(r.diem)} | {r.xep_loai} |" for r in t.itertuples()]
    L += ["", f"Thứ hạng khi đổi trọng số đúng hạn từ 0,6 sang 0,8: tương quan hạng {so(ket['test']['hang_trong_so_khac'], 2)}.", "", "## Cảnh báo giao chậm", "",
          "| Tập | Đợt giao chậm thật | Phát hiện | Ngày chờ từ đầu đợt | Ngày có cảnh báo | Báo nhầm |", "|---|---:|---:|---|---:|---:|"]
    for tp in ["validation2", "test"]:
        d = ket[tp]["danh_gia"]
        L.append(f"| {tp} | {d['so_dot']} | {d['phat_hien']} | {d['ngay_cho'] or '–'} | {d['tong_ngay_canh_bao']} | {d['bao_nham']} |")
    L.append("")
    open(REPORT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))
    print(ket["test"]["su_kien"], ket["validation2"]["su_kien"], {k: v for k, v in ket["test"]["canh_bao_dau"].items()})
