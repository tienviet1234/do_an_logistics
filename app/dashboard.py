"""GD G: cong cu ke hoach dat hang (Streamlit). DOC TU CO SO DU LIEU data/kho_hang.db, CHI DOC (khong ghi gi vao CSDL).
Chay (tai thu muc goc du an):  streamlit run app/dashboard.py
Can chay truoc:                python src/nap_database.py && python src/ton_kho.py
4 man (app/trang/): Hom nay (viec can lam, duyet don, phieu dat hang) · Mat hang (ton kho, du bao, "Thu neu...")
· Kich ban & ket qua (truoc - sau, theo nhom, thu do nhay) · Du lieu & phuong phap (cho hoi dong).
Co che kieu Power BI: bo loc chung o dau phieu (ngay, chinh sach, nhom ABC / XYZ) ap cho moi man; bam bieu do / o trang thai
/ dong bang de loc cheo; tu dong ma hang di sau sang man Mat hang. Phan dung chung: app/chung.py.
"""
import sys
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Phiếu kế hoạch đặt hàng", page_icon=":material/receipt_long:", layout="wide",
                   initial_sidebar_state="collapsed")

sys.path.insert(0, str(Path(__file__).resolve().parent))      # cac man trong app/trang/ dung chung app/chung.py
import chung as C  # noqa: E402

TRANG = {
    "hom-nay": st.Page("trang/hom_nay.py", title="Hôm nay", default=True),
    "mat-hang": st.Page("trang/mat_hang.py", title="Mặt hàng", url_path="mat-hang"),
    "ket-qua": st.Page("trang/ket_qua.py", title="Kịch bản & kết quả", url_path="ket-qua"),
    "du-lieu": st.Page("trang/du_lieu.py", title="Dữ liệu & phương pháp", url_path="du-lieu"),
}

C.kiem_tra_csdl()
C.khoi_tao()
pg = st.navigation(list(TRANG.values()), position="hidden")
trang = next(k for k, p in TRANG.items() if p.title == pg.title)
C.giao_dien(trang)
C.dau_phieu(trang, TRANG)
pg.run()
C.chan_phieu()
