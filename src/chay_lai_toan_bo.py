"""Chay lai TOAN BO de tai tu dau tren mot BAN SACH (tieu chi "Tin cay": chay lai bang lenh ghi san, ra dung ket qua).
Ban sach = cac tep dang commit (git checkout-index) + du lieu dau vao; KHONG co ket qua cu (reports/, data/clean, data/features).
Moi buoc chay tuan tu, 1 tien trinh 1 luc (buoc GPU cung vay); loi o buoc nao thi dung o buoc do, chay lai thi tiep tu buoc chua xong.

  python src/chay_lai_toan_bo.py --tao <thu_muc>          tao ban sach (data/dominicks 13 GB dung lien ket, khong chep)
  python src/chay_lai_toan_bo.py --chay <thu_muc> [--den N] chay cac buoc chua xong (nhat ky: <thu_muc>/nhat_ky_chay_lai/)
  python src/chay_lai_toan_bo.py --ds                     in danh sach buoc
So voi ket qua hien co: src/so_sanh_chay_lai.py.
"""
import json
import os
import shutil
import subprocess
import sys
import time

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
NF = os.path.join(GOC, ".venv_nf", "Scripts", "python.exe")
M5, KHO = "du_lieu_nguon/m5", "du_lieu_nguon/m5_kho"
S = "../../src/"                       # duong dan script khi chay trong thu muc nguon


def _b(ten, lenh, cwd=".", py=None, gpu=False):
    return dict(ten=ten, lenh=lenh, cwd=cwd, py=py, gpu=gpu)


def buoc():
    L = []
    # 1. Bo mo phong: du lieu -> dac trung -> mo hinh moc -> Prophet, LightGBM -> chon vong 1, 2
    L += [_b("ap gia thi truong", ["src/cap_nhat_gia.py"]), _b("lam sach", ["src/lam_sach.py"]), _b("dac trung", ["src/dac_trung.py"]),
          _b("EDA", ["src/eda.py"]), _b("Naive, Seasonal Naive", ["src/danh_gia.py"]), _b("mo hinh moc", ["src/mo_hinh_baseline.py"]),
          _b("Prophet", ["src/mo_hinh_prophet.py"]), _b("LightGBM", ["src/mo_hinh_lightgbm.py"]), _b("chon mo hinh vong 1", ["src/chon_mo_hinh.py"]),
          _b("TB truot validation2", ["src/mo_hinh_baseline.py", "--tap", "validation2", "--chi", "tb_truot_28"]),
          _b("LightGBM validation2", ["src/mo_hinh_lightgbm.py", "--tap", "validation2"]),
          _b("Prophet validation2", ["src/mo_hinh_prophet.py", "--tap", "validation2"]), _b("chon mo hinh vong 2", ["src/chon_mo_hinh.py", "--vong", "2"])]
    L += [_b(f"vong 3 {x}", ["src/nang_cap_du_bao.py", "--buoc", x]) for x in ("goc", "A", "B", "F", "ghep", "test", "bao_cao")]
    L += [_b("vong 4 rui ro", ["src/nang_cap_du_bao_v4.py", "--buoc", "rui_ro"])]
    L += [_b(f"vong 4 chay tuan {m}", ["src/nang_cap_du_bao_v4.py", "--buoc", "B3_chay", m]) for m in ("lgb", "prophet", "moc")]
    L += [_b(f"vong 4 {x}", ["src/nang_cap_du_bao_v4.py", "--buoc", x]) for x in ("B1", "B2")]
    # B3 mo phong ton kho qua ton_kho.py -> can CSDL voi mo hinh da chon LUC DO (ket_hop_v3); buoc "nap CSDL" ben duoi nap lai day du
    L += [_b("nap CSDL tam (ket_hop_v3)", ["src/nap_database.py", "--mo_hinh_chon", "ket_hop_v3"])]
    L += [_b(f"vong 4 {x}", ["src/nang_cap_du_bao_v4.py", "--buoc", x]) for x in ("B3", "B4")]
    L += [_b(f"vong 4 chay tuan {m} test", ["src/nang_cap_du_bao_v4.py", "--buoc", "B3_chay", m, "--tap", "test"]) for m in ("lgb", "prophet", "moc")]
    L += [_b(f"vong 4 {x}", ["src/nang_cap_du_bao_v4.py", "--buoc", x]) for x in ("test", "bao_cao")]
    # 2. CSDL, du bao tuong lai, ton kho va nghiep vu kho (bo mo phong)
    L += [_b("bang so sanh", ["src/tong_hop_ket_qua.py"]), _b("nap CSDL", ["src/nap_database.py"]),
          _b("du bao tuong lai: kiem lai", ["src/du_bao_tuong_lai.py", "--kiem_lai"]), _b("du bao tuong lai", ["src/du_bao_tuong_lai.py"]),
          _b("ton kho", ["src/ton_kho.py"]), _b("do nhay", ["src/do_nhay.py"])]
    L += [_b(x, [f"src/{x}.py"]) for x in ("chi_so_kho", "gom_don", "cham_diem_ncc", "rang_buoc_kho", "newsvendor_mua_vu", "tru_hang_live",
                                         "do_nhay_chi_phi_dat", "canh_bao_lech", "canh_bao_lech_v2")]
    L += [_b("so sanh khuyen mai", ["src/chay_du_bao.py", "--so_sanh_km"])]
    # 3. Hoc sau tren bo mo phong (GPU, khong duoc chon nhung co trong bang so sanh)
    L += [_b(f"LSTM/RNN {x}", ["src/mo_hinh_dl.py", "--buoc", x], gpu=True) for x in ("chon_ham",)]
    L += [_b(f"{c} validation2", ["src/mo_hinh_dl.py", "--buoc", "tuan", "--cell", c], gpu=True) for c in ("lstm", "rnn")]
    L += [_b("LSTM/RNN ghep", ["src/mo_hinh_dl.py", "--buoc", "ghep"], gpu=True)]
    L += [_b(f"{c} test", ["src/mo_hinh_dl.py", "--buoc", "tuan", "--cell", c, "--tap", "test"], gpu=True) for c in ("lstm", "rnn")]
    L += [_b(f"LSTM/RNN {x}", ["src/mo_hinh_dl.py", "--buoc", x], gpu=x == "test") for x in ("test", "bao_cao")]
    # 4. Nguon so ban that M5: dung thu muc lam viec -> dac trung -> 6 mo hinh -> chon -> test -> du bao tuong lai
    L += [_b("M5: dung thu muc", ["src/nguon/m5.py", "data/m5", M5]), _b("M5: dac trung", [S + "dac_trung.py"], M5)]
    md = ("tb_truot", "lap_tuan", "prophet", "lightgbm", "rnn", "lstm")
    L += [_b(f"M5: {m} validation2", [S + "kiem_chung_nguon.py", "--buoc", "tuan", "--mo_hinh", m], M5, gpu=m in ("rnn", "lstm")) for m in md]
    L += [_b("M5: chon", [S + "kiem_chung_nguon.py", "--buoc", "chon"], M5)]
    L += [_b(f"M5: {m} test", [S + "kiem_chung_nguon.py", "--buoc", "tuan", "--mo_hinh", m, "--tap", "test"], M5, gpu=m in ("rnn", "lstm")) for m in md]
    L += [_b(f"M5: {x}", [S + "kiem_chung_nguon.py", "--buoc", x], M5) for x in ("test", "bao_cao")]
    L += [_b("M5 tuong lai: kiem lai", [S + "du_bao_tuong_lai_kc.py", "--kiem_lai", "../../data/m5"], M5),
          _b("M5 tuong lai: RNN", [S + "du_bao_tuong_lai_kc.py", "--rnn", "../../data/m5"], M5, gpu=True),
          _b("M5 tuong lai: ghep", [S + "du_bao_tuong_lai_kc.py", "../../data/m5"], M5)]
    # 5. TiDE, N-HiTS, TFT (GPU, moi truong rieng); khong anh huong mo hinh duoc chon.
    #    Phai chay TRUOC "M5 kho: dung": kho M5 chep bang ket qua mo hinh cua M5 (chay sau thi thieu dong NF).
    for nh, cwd in (("mo phong", "."), ("M5", M5)):
        sc = "src/mo_hinh_nf.py" if cwd == "." else S + "mo_hinh_nf.py"
        L += [_b(f"NF {nh}: {m} validation2", [sc, "--buoc", "tuan", "--mo_hinh", m], cwd, NF, True) for m in ("tide", "nhits", "tft")]
        L += [_b(f"NF {nh}: ghep", [sc, "--buoc", "ghep"], cwd, NF)]
        L += [_b(f"NF {nh}: {m} test", [sc, "--buoc", "tuan", "--mo_hinh", m, "--tap", "test"], cwd, NF, True) for m in ("tide", "nhits", "tft")]
        L += [_b(f"NF {nh}: {x}", [sc, "--buoc", x], cwd, NF) for x in ("test", "bao_cao")]
    # 6. Bien lai Dominick's -> kho tong dung tu so ban M5 -> ton kho va nghiep vu kho tren M5
    L += [_b(f"Dominick's {x}", ["src/phan_tich_dominicks.py", "--buoc", x]) for x in ("gop", "tinh")]
    L += [_b("M5 kho: dung", ["src/nguon/m5_kho.py", M5, "data/m5", "du_lieu_nguon/dominicks/theo_tuan.csv.gz", KHO]),
          _b("M5 kho: nap CSDL", [S + "nap_database.py"], KHO), _b("M5 kho: ton kho", [S + "ton_kho.py"], KHO), _b("M5 kho: do nhay", [S + "do_nhay.py"], KHO)]
    L += [_b(f"M5 kho: {x}", [S + f"{x}.py"], KHO) for x in ("chi_so_kho", "gom_don", "do_nhay_chi_phi_dat", "canh_bao_lech", "canh_bao_lech_v2")]
    L += [_b("Dominick's sau doi chieu", ["src/phan_tich_dominicks.py", "--buoc", "sau_doi_chieu"])]
    # 7. Tong hop: bang so sanh, bieu do, Power BI, trang trinh bay, so so lieu
    L += [_b("bang so sanh (du mo hinh)", ["src/tong_hop_ket_qua.py"]), _b("bieu do ket qua", ["src/bieu_do_ket_qua.py"]),
          _b("Power BI", ["src/xuat_power_bi.py"]), _b("trang luong", ["src/tao_trang_luong.py"]), _b("so so lieu", ["src/so_lieu_do_an.py"]),
          _b("so do bao cao", ["src/tao_so_do_bao_cao.py", "--chua_co_word"])]   # so do kiem tra so so lieu da co -> chay sau
    return L


# Giai doan (de trinh bay): ten, buoc dau tien, dieu giai doan nay chung minh. Ten buoc la khoa chay tiep -> khong doi ten buoc.
GIAI_DOAN = [
    ("Bộ mô phỏng: dữ liệu và chọn mô hình", "ap gia thi truong", "Làm sạch, đặc trưng, mô hình mốc, Prophet, LightGBM, 4 vòng chọn mô hình ra đúng số cũ"),
    ("CSDL, dự báo tương lai, tồn kho", "bang so sanh", "Nạp CSDL, dự báo 28 ngày chưa xảy ra, mô phỏng tồn kho 12 tháng, nghiệp vụ kho"),
    ("Học sâu trên bộ mô phỏng (GPU)", "LSTM/RNN chon_ham", "LSTM, RNN học lại từ đầu trên card đồ họa"),
    ("Số bán thật M5", "M5: dung thu muc", "Dựng lại dữ liệu M5 từ tệp gốc, chạy lại 6 mô hình, dự báo tương lai"),
    ("TiDE, N-HiTS, TFT (GPU)", "NF mo phong: tide validation2", "Ba mô hình học sâu mới trên cả hai bộ"),
    ("Kho dựng từ số bán M5", "Dominick's gop", "Biên lãi từ Dominick's, dựng kho, tồn kho và nghiệp vụ kho trên số thật"),
    ("Tổng hợp", "bang so sanh (du mo hinh)", "Bảng so sánh, biểu đồ, Power BI, sổ số liệu cho đồ án"),
]


def giai_doan_cua(L=None):
    """Danh sach (ten, chi so buoc dau, chi so buoc cuoi + 1, mo ta)."""
    L = L or buoc()
    dau = [next(i for i, b in enumerate(L) if b["ten"] == d) for _, d, _ in GIAI_DOAN]
    return [(t, a, b, m) for (t, _, m), a, b in zip(GIAI_DOAN, dau, dau[1:] + [len(L)])]


def tao(ra):
    """Ban sach: tep dang commit + du lieu dau vao; xoa ket qua da commit de moi buoc phai tao lai."""
    ra = os.path.abspath(ra)
    if os.path.exists(ra):
        sys.exit(f"{ra} da ton tai")
    subprocess.run(["git", "checkout-index", "-a", f"--prefix={ra}/"], cwd=GOC, check=True)
    for d in ("reports", "data/clean", "data/features"):     # tep Excel trong reports/ la tai lieu soan tay, khong script nao tao: giu
        p = os.path.join(ra, d)
        if os.path.isdir(p):
            for f in os.listdir(p):
                q = os.path.join(p, f)
                if not f.endswith(".xlsx"):
                    shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    shutil.copytree(os.path.join(GOC, "data/m5"), os.path.join(ra, "data/m5"))
    if os.name == "nt":                  # 13 GB, chi doc: lien ket thu muc thay vi chep
        subprocess.run(["cmd", "/c", "mklink", "/J", os.path.join(ra, "data", "dominicks"), os.path.join(GOC, "data", "dominicks")], check=True,
                       capture_output=True)
    else:
        os.symlink(os.path.join(GOC, "data/dominicks"), os.path.join(ra, "data/dominicks"))
    os.makedirs(os.path.join(ra, "du_lieu_nguon"), exist_ok=True)
    print("Ban sach:", ra)


def giu_may_thuc(bat=True):
    """Windows: giu may thuc SUOT lan chay (tien trinh nay song tu dau den cuoi). Phai giu ca man hinh: may Modern Standby
    (S0) vao che do cho khi man hinh tu tat, ES_SYSTEM_REQUIRED mot minh KHONG chan duoc (dem 10-11/11: 'Idle Timeout' luc 00:12
    du buoc dang chay da xin ES_SYSTEM_REQUIRED). Tra ve (da dat duoc, dang cam sac: True/False/None)."""
    if os.name != "nt":
        return False, None
    import ctypes

    class TrangThaiNguon(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_byte), ("BatteryFlag", ctypes.c_byte), ("BatteryLifePercent", ctypes.c_byte),
                    ("SystemStatusFlag", ctypes.c_byte), ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED = 0x80000000, 0x00000001, 0x00000002
    co = ES_CONTINUOUS | ((ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED) if bat else 0)
    ok = bool(ctypes.windll.kernel32.SetThreadExecutionState(co))
    tt = TrangThaiNguon()
    sac = {0: False, 1: True}.get(tt.ACLineStatus) if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(tt)) else None
    return ok, sac


def chay(ra, den=None):
    ok, sac = giu_may_thuc(True)
    print(f"Giu may thuc suot lan chay: {'co' if ok else 'KHONG dat duoc'}; nguon: "
          f"{'dang cam sac' if sac else 'DANG CHAY PIN - cam sac, neu khong Windows van ep may cho khi het han muc pin' if sac is False else 'khong ro'}", flush=True)
    try:
        _chay(ra, den)
    finally:
        giu_may_thuc(False)


def _chay(ra, den=None):
    ra = os.path.abspath(ra)
    nk = os.path.join(ra, "nhat_ky_chay_lai")
    os.makedirs(nk, exist_ok=True)
    f_tt = os.path.join(ra, "chay_lai_trang_thai.json")
    tt = json.load(open(f_tt, encoding="utf-8")) if os.path.exists(f_tt) else {}
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.pop("KHO_GOC", None)
    L = buoc()
    for i, b in enumerate(L, 1):
        if den and i > den:
            break
        k = f"{i:02d} {b['ten']}"
        if k in tt:
            continue
        t0 = time.time()
        print(f"[{time.strftime('%d/%m %H:%M')}] {k}{' (GPU)' if b['gpu'] else ''}", flush=True)
        with open(os.path.join(nk, f"{i:02d}.log"), "w", encoding="utf-8") as lg:
            r = subprocess.run([b["py"] or PY, *b["lenh"]], cwd=os.path.join(ra, b["cwd"]), env=env, stdout=lg, stderr=subprocess.STDOUT)
        if r.returncode:
            print(f"   LOI ma {r.returncode} sau {time.time() - t0:.0f}s, xem {nk}/{i:02d}.log", flush=True)
            sys.exit(1)
        tt[k] = round(time.time() - t0)
        json.dump(tt, open(f_tt, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"   xong {tt[k]}s", flush=True)
    print("XONG", len(tt), "/", len(L), "buoc, tong", round(sum(tt.values()) / 3600, 1), "gio", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv
    if "--ds" in a:
        for i, b in enumerate(buoc(), 1):
            print(f"{i:02d} {'GPU ' if b['gpu'] else '    '}{b['cwd']:22s} {b['ten']}")
    elif "--tao" in a:
        tao(a[a.index("--tao") + 1])
    elif "--chay" in a:
        chay(a[a.index("--chay") + 1], int(a[a.index("--den") + 1]) if "--den" in a else None)
    else:
        sys.exit(__doc__)
