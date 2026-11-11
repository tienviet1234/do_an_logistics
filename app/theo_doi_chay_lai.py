"""Trang theo doi lan chay lai toan bo (src/chay_lai_toan_bo.py), de trinh bay voi giang vien. CHI DOC: trang thai, nhat ky
cua ban sach; doi chieu voi ket qua hien co bang src/so_sanh_chay_lai.py khi bam nut.
Chay tai thu muc goc:  streamlit run app/theo_doi_chay_lai.py --server.port 8502 -- <thu_muc_ban_sach>
"""
import json
import os
import re
import sys
import time
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP.parent / "src"))
import chung as C  # noqa: E402
import chay_lai_toan_bo as R  # noqa: E402

st.set_page_config(page_title="Chạy lại toàn bộ", page_icon="🔁", layout="wide")
BAN = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CHAY_LAI_DIR", "")).resolve()
LOG = BAN.parent / "chay_lai.log"          # nhat ky chung cua lan chay (cung thu muc cha cua ban sach)
L = R.buoc()
GD = R.giai_doan_cua(L)

# ten buoc la khoa chay tiep (khong dau) -> chi doi cach hien thi
TU = [("ap gia thi truong", "áp giá thị trường"), ("lam sach", "làm sạch"), ("dac trung", "đặc trưng"), ("mo hinh moc", "mô hình mốc"),
      ("chon mo hinh vong", "chọn mô hình vòng"), ("TB truot", "TB trượt"), ("vong", "vòng"), ("chay tuan", "chạy theo tuần"),
      ("rui ro", "rủi ro"), ("bang so sanh", "bảng so sánh"), ("du mo hinh", "đủ mô hình"), ("nap CSDL", "nạp CSDL"),
      ("du bao tuong lai", "dự báo tương lai"), ("tuong lai", "tương lai"), ("kiem lai", "kiểm lại"), ("ton kho", "tồn kho"),
      ("do nhay", "độ nhạy"), ("so sanh khuyen mai", "so sánh khuyến mãi"), ("dung thu muc", "dựng thư mục"), ("dung", "dựng"),
      ("chon", "chọn"), ("ghep", "ghép"), ("sau doi chieu", "sau đối chiếu"), ("gop", "gộp"), ("tinh", "tính"),
      ("bieu do ket qua", "biểu đồ kết quả"), ("trang luong", "trang luồng"), ("so do bao cao", "sơ đồ báo cáo"),
      ("so so lieu", "sổ số liệu"), ("M5 kho", "Kho M5"), ("bao_cao", "báo cáo"), ("chon_ham", "chọn hàm mất mát")]


def nhan(ten):
    for a, b in TU:
        ten = re.sub(rf"\b{re.escape(a)}\b", b, ten)
    return ten


def tg(s):
    s = int(s)
    return f"{s // 3600} giờ {s % 3600 // 60:02d} phút" if s >= 3600 else f"{s // 60} phút {s % 60:02d} giây" if s >= 60 else f"{s} giây"


def doc_trang_thai():
    f = BAN / "chay_lai_trang_thai.json"
    xong = json.load(open(f, encoding="utf-8")) if f.exists() else {}
    log = LOG.read_text(encoding="utf-8", errors="replace").splitlines() if LOG.exists() else []
    dang, loi, luc = None, None, None
    for l in log:                                   # dong cuoi quyet dinh: "[dd/mm HH:MM] NN ten" -> dang chay; "LOI" -> loi
        m = re.match(r"\[(\d\d/\d\d \d\d:\d\d)\] (\d\d) ", l)
        if m:
            dang, loi, luc = int(m.group(2)), None, m.group(1)
        elif "LOI ma" in l:
            loi = l.strip()
        elif l.strip().startswith("xong") or l.startswith("XONG"):
            dang = None if l.startswith("XONG") else dang
    if dang is not None and f"{dang:02d} {L[dang - 1]['ten']}" in xong:
        dang = None
    song = False
    try:
        import psutil
        song = any("chay_lai_toan_bo.py" in " ".join(p.info["cmdline"] or []) and "--chay" in (p.info["cmdline"] or [])
                   for p in psutil.process_iter(["cmdline"]))
    except Exception:
        pass
    giu = next((l for l in reversed(log) if l.startswith("Giu may thuc")), "")
    return xong, dang, loi, luc, song, giu


def duoi_nhat_ky(i, n=14):
    f = BAN / "nhat_ky_chay_lai" / f"{i:02d}.log"
    if not f.exists():
        return [], None
    s = f.read_text(encoding="utf-8", errors="replace")
    dong = [x.strip() for l in s.splitlines() for x in re.split(r"\s{2,}(?=\S+/\S+ moc )", l) if x.strip()]   # tach dong tien do "ten/tap moc k/n" noi lien
    return dong[-n:], f.stat().st_mtime


C.giao_dien("du-lieu")
st.markdown("""<style>
.gd { display: grid; grid-template-columns: minmax(0, 1fr) 150px 120px; gap: 0.35rem 1rem; align-items: center;
      border-top: 1px solid var(--ke); padding: 0.6rem 0; }
.gd b { color: var(--muc); } .gd .mo { color: var(--muc2); font-size: 0.86rem; display: block; }
.thanh { height: 10px; background: #e3e8eb; position: relative; } .thanh i { position: absolute; inset: 0 auto 0 0; background: var(--phieu); }
.thanh.xong i { background: var(--la); }
.dau-tt { font-size: 0.74rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; border: 1.5px solid currentColor;
          padding: 0.1rem 0.45rem; display: inline-block; }
.dau-tt.xong { color: var(--la); } .dau-tt.dang { color: var(--phieu); background: var(--quang); border-color: var(--phieu); }
.dau-tt.cho { color: var(--muc2); } .dau-tt.loi { color: var(--do); }
.nk { font-family: Consolas, monospace; font-size: 0.8rem; background: #f4f6f7; border: 1px solid var(--ke); padding: 0.6rem 0.8rem;
      white-space: pre-wrap; color: var(--muc); max-height: 330px; overflow: auto; }
@media (max-width: 640px) { .gd { grid-template-columns: 1fr; } }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="dp-ten">Chạy lại toàn bộ hệ thống từ đầu</div><div class="dp-phu">Bản sạch: chỉ có mã nguồn đã commit và dữ liệu đầu vào, '
            'không có kết quả cũ. Mỗi bước chạy lại phải ra <b>đúng</b> kết quả đã báo cáo trong đồ án. Trang tự cập nhật mỗi 10 giây.</div>'
            '<div class="ke-doi"></div>', unsafe_allow_html=True)
if not BAN.exists():
    st.error(f"Không thấy thư mục bản sạch: {BAN}. Chạy: streamlit run app/theo_doi_chay_lai.py -- <thư mục>")
    st.stop()


@st.fragment(run_every=10)
def tinh_hinh():
    xong, dang, loi, luc, song, giu = doc_trang_thai()
    tong_tg = sum(xong.values())
    da_chay = 0
    if dang and luc and song:
        bd = datetime.strptime(f"{datetime.now().year}/{luc}", "%Y/%d/%m %H:%M")
        da_chay = max(0, (datetime.now() - bd).total_seconds())
    trang = "Đang chạy" if song and dang else ("Dừng vì lỗi" if loi else "Xong" if len(xong) == len(L) else "Đang dừng")
    C.o_hang([("Tình trạng", trang, ("máy giữ thức, đang cắm sạc" if "cam sac" in giu else giu[:40]) if song else "chạy tiếp: --chay <thư mục>", trang == "Đang chạy"),
              ("Bước đã xong", f"{len(xong)} / {len(L)}", f"{100 * len(xong) / len(L):.0f}%", False),
              ("Thời gian máy đã chạy", tg(tong_tg + da_chay), "cộng các bước, không tính lúc dừng", False),
              ("Bước đang chạy", f"{dang}" if dang and song else "–", nhan(L[dang - 1]["ten"]) if dang and song else "", False)])
    st.progress(len(xong) / len(L))

    C.muc("Theo giai đoạn", "mỗi giai đoạn chứng minh một phần của đồ án chạy lại được")
    h = []
    for t, a, b, m in GD:
        n = sum(f"{i + 1:02d} {L[i]['ten']}" in xong for i in range(a, b))
        dang_o = bool(dang and song and a < dang <= b)
        lop, chu = ("xong", "Xong") if n == b - a else ("dang", "Đang chạy") if dang_o else ("loi", "Lỗi") if (loi and dang and a < dang <= b) else ("cho", "Chờ")
        h.append(f'<div class="gd"><div><b>{escape(t)}</b><span class="mo">{escape(m)} · bước {a + 1}–{b}</span></div>'
                 f'<div><div class="thanh {lop}"><i style="width:{100 * n / (b - a):.0f}%"></i></div>'
                 f'<span class="mo">{n}/{b - a} bước</span></div><div><span class="dau-tt {lop}">{chu}</span></div></div>')
    st.markdown("".join(h), unsafe_allow_html=True)

    if dang:
        b = L[dang - 1]
        C.muc(f"Bước {dang}: {escape(nhan(b['ten']))}", "dùng card đồ họa" if b["gpu"] else "đang chạy")
        lenh = " ".join(b["lenh"])
        st.markdown(f'<span class="dp-phu">Lệnh: <code>{escape(lenh)}</code> · thư mục <code>{escape(b["cwd"])}</code>'
                    f'{f" · bắt đầu {luc}, đã chạy {tg(da_chay)}" if luc and song else ""}</span>', unsafe_allow_html=True)
        dong, mt = duoi_nhat_ky(dang)
        if dong:
            st.markdown(f'<div class="nk">{escape(chr(10).join(dong))}</div>', unsafe_allow_html=True)
            st.caption(f"Nhật ký cập nhật lúc {datetime.fromtimestamp(mt):%H:%M:%S}. Một số bước chỉ ghi khi xong từng mô hình, nên có lúc đứng yên vài phút.")
    if loi:
        st.error(f"Bước {dang} dừng: {loi}")


tinh_hinh()

C.muc("Đối chiếu với kết quả đã báo cáo", "chạy lại có ra đúng số cũ không")
st.markdown('<span class="dp-phu">So từng tệp kết quả của lần chạy lại với tệp hiện có: số liệu lệch quá 0,0001% là <b>khác</b>. '
            'Chỉ so các tệp lần chạy lại đã tạo ra; bảng kết quả mô hình chỉ so các dòng đã có ở cả hai bên. '
            'Tự đối chiếu lại mỗi khi xong thêm một bước.</span>', unsafe_allow_html=True)
F_DC, F_KHOA = BAN / "doi_chieu.json", BAN / "doi_chieu.dang_chay"


def dang_doi_chieu():
    try:
        import psutil
        return F_KHOA.exists() and psutil.pid_exists(int(F_KHOA.read_text()))
    except Exception:
        return False


def bat_doi_chieu(so_buoc):
    """Chay so_sanh_chay_lai.py thanh tien trinh rieng (khong bi trang tu lam moi cat ngang), ghi doi_chieu.json."""
    import subprocess
    p = subprocess.Popen([sys.executable, str(APP.parent / "src" / "so_sanh_chay_lai.py"), str(BAN), "--chi_co", "--json", str(F_DC),
                          "--nhan", str(so_buoc)], cwd=str(APP.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    F_KHOA.write_text(str(p.pid))


@st.fragment(run_every=10)
def doi_chieu():
    xong = doc_trang_thai()[0]
    kq = json.load(open(F_DC, encoding="utf-8")) if F_DC.exists() else None
    if not dang_doi_chieu() and (kq is None or str(kq.get("--nhan")) != str(len(xong))):
        bat_doi_chieu(len(xong))
    if st.button("Đối chiếu ngay", key="dc", disabled=dang_doi_chieu()):
        bat_doi_chieu(len(xong))
    if dang_doi_chieu():
        st.caption("Đang so từng tệp (khoảng 1–2 phút)…")
    if kq:
        gi = kq["giong"]
        con_chay = int(kq.get("--nhan", 0)) < len(L)
        # luc con chay: tep trang thai (*_trang_thai.json) cua buoc chua xong chac chan khac -> tach rieng, khong tinh la khac
        do = [x for x in kq["khac"] if con_chay and x[0].endswith("_trang_thai.json")]
        kh = [x for x in kq["khac"] if x not in do]
        C.o_hang([("Tệp giống hệt", f"{len(gi)}", "chạy lại ra đúng số cũ", False),
                  ("Tệp khác", f"{len(kh)}", "cần xem" if kh else "không có", bool(kh)),
                  ("Tệp đang ghi dở", f"{len(do)}", "trạng thái của bước chưa xong" if do else "không có", False),
                  ("Đối chiếu lúc", kq["luc"][11:16], f"khi đã xong {kq.get('--nhan', '?')} bước", False)])
        if kh:
            st.markdown("**Tệp khác:**")
            st.dataframe([{"Tệp": t, "Khác ở đâu": l} for t, l in kh], hide_index=True, use_container_width=True)
        if do:
            st.caption("Tệp đang ghi dở: " + ", ".join(t for t, _ in do) + ". Bước tạo ra tệp này chưa chạy xong; sẽ so lại khi xong.")
        with st.expander(f"Xem {len(gi)} tệp giống hệt"):
            st.dataframe([{"Tệp": t} for t in gi], hide_index=True, use_container_width=True)


doi_chieu()

with st.expander(f"Danh sách đủ {len(L)} bước"):
    xong = doc_trang_thai()[0]
    st.dataframe([{"Bước": i + 1, "Giai đoạn": next(t for t, a, b, _ in GD if a <= i < b), "Việc": nhan(x["ten"]),
                   "GPU": "có" if x["gpu"] else "", "Thời gian": tg(xong[f"{i + 1:02d} {x['ten']}"]) if f"{i + 1:02d} {x['ten']}" in xong else ""}
                  for i, x in enumerate(L)], hide_index=True, use_container_width=True, height=420)
