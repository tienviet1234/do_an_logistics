"""So ket qua cua lan chay lai tren ban sach (src/chay_lai_toan_bo.py) voi ket qua hien co. CHI DOC.
  python src/so_sanh_chay_lai.py <thu_muc_ban_sach> [--chi_co]   (--chi_co: chi so tep da co o ban sach, bo qua tep chua tao)
Tep van ban (.md, .json): so tung dong, bo dong thoi diem tao. Tep .csv: so so lieu voi sai so tuong doi DUNG (1e-6), cot chu phai trung.
reports/ket_qua_mo_hinh.csv: so theo (mo_hinh, tap) vi thu tu dong phu thuoc thu tu chay.
Ket qua: bang GIONG / KHAC / THIEU tung tep; thoat ma 1 neu co KHAC.
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUNG = 1e-6
BO_DONG = re.compile(r"(Tạo tự động lúc|Ngày chạy|chạy lúc|Chay luc|Thời gian chạy|giay\)|giây\)|\d+s\b)")
THU_MUC = ["reports", "du_lieu_nguon/m5/reports", "du_lieu_nguon/m5_kho/reports"]


def dong(p):
    s = open(p, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
    return [l for l in s.split("\n") if not BO_DONG.search(l)]


def so_csv(a, b, khoa=None, giao=False):
    """giao=True (lan chay chua xong): chi so cac dong co khoa o ca hai ben."""
    x, y = pd.read_csv(a, encoding="utf-8-sig"), pd.read_csv(b, encoding="utf-8-sig")
    if khoa and giao:
        chung = x[khoa].merge(y[khoa]).drop_duplicates()
        x, y = x.merge(chung), y.merge(chung)
    if khoa and set(khoa) <= set(x.columns) and set(khoa) <= set(y.columns):
        x, y = x.sort_values(khoa).reset_index(drop=True), y.sort_values(khoa).reset_index(drop=True)
    if list(x.columns) != list(y.columns):
        return f"cot khac: {sorted(set(x.columns) ^ set(y.columns))}"
    if len(x) != len(y):
        return f"so dong {len(x)} / {len(y)}"
    for c in x.columns:
        if pd.api.types.is_numeric_dtype(x[c]) and pd.api.types.is_numeric_dtype(y[c]):
            u, v = x[c].to_numpy(float), y[c].to_numpy(float)
            nan = np.isnan(u) != np.isnan(v)
            lech = np.abs(u - v) / np.maximum(np.abs(u), 1.0)
            lech = np.where(np.isnan(u) & np.isnan(v), 0, lech)
            if nan.any() or np.nanmax(lech, initial=0) > DUNG:
                i = int(np.nanargmax(np.where(nan, np.inf, lech)))
                return f"cot {c}: lech toi da {np.nanmax(lech):.2e} (dong {i}: {u[i]} / {v[i]})"
        elif not (x[c].astype(str) == y[c].astype(str)).all():
            i = int((x[c].astype(str) != y[c].astype(str)).to_numpy().argmax())
            return f"cot {c} dong {i}: {x[c].iloc[i]!r} / {y[c].iloc[i]!r}"
    return None


def so_tep(a, b, ten, giao=False):
    if ten.endswith(".csv"):
        khoa = ["mo_hinh", "tap"] if ten.endswith("ket_qua_mo_hinh.csv") else None
        return so_csv(a, b, khoa, giao)
    if ten.endswith((".md", ".json")):
        x, y = dong(a), dong(b)
        if x == y:
            return None
        k = [(i, u, v) for i, (u, v) in enumerate(zip(x, y)) if u != v]
        if not k:
            return f"so dong {len(x)} / {len(y)}"
        i, u, v = k[0]
        return f"{len(k)} dong khac, vd dong {i}: {u[:90]!r} / {v[:90]!r}"
    return "bo qua"


def danh_sach(goc):
    for d in THU_MUC:
        p = os.path.join(goc, d)
        for r, _, fs in os.walk(p):
            for f in fs:
                if f.endswith((".md", ".json", ".csv")):
                    yield os.path.relpath(os.path.join(r, f), goc).replace("\\", "/")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ban = sys.argv[1]
    chi_co = "--chi_co" in sys.argv
    kq = {"GIONG": [], "KHAC": [], "THIEU": []}
    for t in sorted(set(danh_sach(GOC))):
        b = os.path.join(ban, t)
        if not os.path.exists(b):
            if not chi_co:
                kq["THIEU"].append(t)
            continue
        ly_do = so_tep(os.path.join(GOC, t), b, t, chi_co)
        if ly_do == "bo qua":
            continue
        (kq["GIONG"] if ly_do is None else kq["KHAC"]).append((t, ly_do) if ly_do else t)
    if "--json" in sys.argv:                         # cho trang theo doi: ghi ket qua ra tep (ghi tep tam roi doi ten, khong de tep do dang)
        f = sys.argv[sys.argv.index("--json") + 1]
        nhan = {k: sys.argv[sys.argv.index(k) + 1] for k in ("--nhan",) if k in sys.argv}
        tam = f + ".tam"
        json.dump({"luc": __import__("datetime").datetime.now().isoformat(timespec="seconds"), **nhan,
                   "giong": kq["GIONG"], "khac": [list(x) for x in kq["KHAC"]]}, open(tam, "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(tam, f)
    print(f"GIONG {len(kq['GIONG'])} | KHAC {len(kq['KHAC'])} | THIEU {len(kq['THIEU'])}")
    for t, l in kq["KHAC"]:
        print("  KHAC ", t, "->", l)
    for t in kq["THIEU"][:40]:
        print("  THIEU", t)
    sys.exit(1 if kq["KHAC"] else 0)
