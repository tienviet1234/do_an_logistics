"""Phan dung chung cho 4 man cua cong cu ke hoach dat hang (app/dashboard.py + app/trang/*).
CHI DOC co so du lieu data/kho_hang.db. Giao dien kieu "phieu ke hoach": khung va nhan in bang muc xanh Pho,
so lieu muc den, moi man mot mau lien giay, trang thai la con dau (luon co chu + bieu tuong, khong chi mau).
Bo loc chung (ngay, chinh sach, nhom ABC / XYZ) nam o dau phieu, ap cho moi man (giong slicer cua Power BI).
"""
import sqlite3
import sys
from contextlib import closing
from datetime import date, datetime
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from csdl import TRANG_THAI, de_xuat_ngay, hang_dang_ve, trang_thai_ton_kho  # noqa: E402,F401

DB = ROOT / "data" / "kho_hang.db"
MAIN = 0.95                                   # muc phuc vu cua mo phong (mo_phong_ngay chi luu muc nay)
CS_GOI_Y = "cong_thuc_du_bao_ai_hc"           # chinh sach de xuat sau GD F
MOC = "tb_truot_28"                           # du bao moc tot nhat (GD C)
HORIZON = 28                                  # moi dot du bao 28 ngay (ton_kho.HORIZON)
NGAY_MAC_DINH = date(2026, 2, 9)              # truoc Tet 2026: ngay co nhieu viec de trinh bay

# ------------------------------------------------------------------ mau (dung chung cho CSS va bieu do)
MUC, MUC2, PHIEU, KE = "#15171a", "#4a4d52", "#1d4f73", "#9db0bf"
DO, HO_PHACH, LA, QUANG = "#b3261e", "#93560a", "#2e6b3f", "#ffe45c"
C_THUC_TE, C_AI, C_AI2, C_MOC, C_HT = MUC, "#1f6fb2", "#8db7de", "#c0661c", "#8a8a85"
C_TT = ["#c8443b", "#e0a030", "#7fa6c4"]       # to mau dien tich: het hang / dat hom nay / dang ve
LIEN = {"hom-nay": "#fdfdfb", "mat-hang": "#fbf5d6", "ket-qua": "#f9ebe8", "du-lieu": "#eaf1e7"}   # mau lien giay

CS_TEN = {"hien_trang": "Hiện trạng*", "cong_thuc_du_bao_moc": "Công thức + dự báo mốc",
          "cong_thuc_du_bao_ai": "Công thức + dự báo AI", "cong_thuc_du_bao_ai_hc": "AI + hiệu chỉnh lệch (đề xuất)"}
CS_NGAN = {"hien_trang": "Hiện trạng*", "cong_thuc_du_bao_moc": "Dự báo mốc", "cong_thuc_du_bao_ai": "AI",
           "cong_thuc_du_bao_ai_hc": "AI + hiệu chỉnh"}
CS_MAU = {"hien_trang": C_HT, "cong_thuc_du_bao_moc": C_MOC, "cong_thuc_du_bao_ai": C_AI2, "cong_thuc_du_bao_ai_hc": C_AI}
CS_CONG_THUC = [c for c in CS_TEN if c != "hien_trang"]
NOTE = "Dữ liệu mô phỏng, không phải số liệu kho thật."
NOTE_HT = ("\\* Hiện trạng: người lập kế hoạch trong dữ liệu mô phỏng **biết trước nhu cầu kỳ vọng** (lệch ±10%), "
           "nên là đối thủ mạnh hơn thực tế.")

vn = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
ngay_vn = lambda s: pd.Timestamp(s).strftime("%d/%m/%Y")
dau_cong = lambda v, nd=1: ("+" if v > 0 else "") + vn(v, nd)

# ------------------------------------------------------------------ bieu tuong (SVG tu ve, net 1.75, theo currentColor)
_ICON = {
    "het": '<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z"/><path d="M4 4l16 16"/>',
    "dat": '<path d="M9 3.5h6v3H9z"/><path d="M8 5H5v15.5h14V5h-3"/><path d="M12 10v6M9 13h6"/>',
    "ve": '<path d="M2.5 6.5h11v9h-11zM13.5 9.5h4l3.5 3.5v2.5h-7.5"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "du": '<path d="M4.5 12.5l4.5 4.5L19.5 6.5"/>',
    "duyet": '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.2l2.8 2.8L16.2 9.5"/>',
    "sua": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    "bo": '<circle cx="12" cy="12" r="8.5"/><path d="M7.5 12h9"/>',
    "tai": '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5"/><path d="M4.5 19.5h15"/>',
}


def icon(ten, co=16):
    return (f'<svg class="ic" width="{co}" height="{co}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICON[ten]}</svg>')


def _mask(ten):                                # bieu tuong lam mat na CSS (cho nut bam cua Streamlit)
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' "
           f"stroke-linecap='round' stroke-linejoin='round'>{_ICON[ten]}</svg>").replace('"', "'").replace("#", "%23")
    return f'url("data:image/svg+xml;utf8,{svg}")'


# trang thai: (chu tren con dau, mau, bieu tuong) theo thu tu csdl.TRANG_THAI
# mau con dau dat bang class (Streamlit loc bo thuoc tinh style trong HTML), xem .dau.<lop> trong giao_dien()
LOP_MAU = {"do": DO, "hophach": HO_PHACH, "phieu": PHIEU, "la": LA, "xam": MUC2}
TT_DAU = [("Hết hàng", "do", "het"), ("Đặt hôm nay", "hophach", "dat"), ("Đang về", "phieu", "ve"), ("Đủ hàng", "la", "du")]
QD_DAU = {"duyet": ("Đã duyệt", "la", "duyet"), "sua": ("Đã sửa", "hophach", "sua"), "bo": ("Bỏ qua", "xam", "bo")}


def dau(chu, lop, ic, moi=False):
    """Con dau cao su: vien doi, nghieng nhe, co chu + bieu tuong. moi=True: hieu ung dong dau (1 lan)."""
    return f'<span class="dau {lop}{" dau-moi" if moi else ""}">{icon(ic, 15)}{chu}</span>'


dau_tt = lambda i, moi=False: dau(*TT_DAU[i], moi=moi)


# ------------------------------------------------------------------ CSS cua phieu
def giao_dien(lien):
    masks = "\n".join(f".st-key-tt_{i} button::before, .st-key-tt_{i}_on button::before {{ -webkit-mask-image: {_mask(ic)}; "
                      f"mask-image: {_mask(ic)}; }}\n.st-key-tt_{i} button, .st-key-tt_{i}_on button {{ --c: {mau}; }}"
                      for i, (_, mau, ic) in enumerate((a, LOP_MAU[b], c) for a, b, c in TT_DAU))
    tabs = "\n".join(f".st-key-tab_{k.replace('-', '_')} a, .st-key-tab_{k.replace('-', '_')}_on a {{ background: {v}; }}"
                     for k, v in LIEN.items())
    st.markdown(f"""<style>
:root {{ --giay: {LIEN[lien]}; --phieu: {PHIEU}; --muc: {MUC}; --muc2: {MUC2}; --ke: {KE}; --quang: {QUANG};
        --do: {DO}; --hophach: {HO_PHACH}; --la: {LA}; }}
html {{ font-variant-numeric: tabular-nums; }}
.stApp {{ background: var(--giay); color: var(--muc); }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"] {{ max-width: 1480px; padding: 1.1rem 2rem 2.5rem; }}
::selection {{ background: var(--quang); color: var(--muc); }}
:focus-visible {{ outline: 2px solid var(--phieu) !important; outline-offset: 2px; }}
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-thumb {{ background: #b7c4ce; border: 2px solid var(--giay); }}
::-webkit-scrollbar-track {{ background: transparent; }}
.stApp a {{ color: var(--phieu); text-underline-offset: 3px; }}
.stApp p, .stApp li {{ line-height: 1.55; }}
.ic {{ flex: none; vertical-align: -3px; }}

/* dau phieu */
.dp-ten {{ font-size: 1.85rem; font-weight: 800; color: var(--phieu); letter-spacing: -0.01em; line-height: 1.15; margin: 0; }}
.dp-ma {{ font-size: 1.6rem; font-weight: 800; color: var(--muc); letter-spacing: -0.01em; margin: 0.7rem 0 0.8rem; }}
.dp-ma span {{ color: var(--phieu); }}
.phai {{ text-align: right; }}
.dau.do {{ --c: var(--do); }} .dau.hophach {{ --c: var(--hophach); }} .dau.phieu {{ --c: var(--phieu); }}
.dau.la {{ --c: var(--la); }} .dau.xam {{ --c: var(--muc2); }}
.o-hang.n2 {{ --n: 2; }} .o-hang.n3 {{ --n: 3; }} .o-hang.n4 {{ --n: 4; }} .o-hang.n5 {{ --n: 5; }} .o-hang.n6 {{ --n: 6; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{
        font-family: inherit !important; font-variant-numeric: tabular-nums; }}
.dp-phu {{ color: var(--muc2); font-size: 0.86rem; margin-top: 0.25rem; }}
.dp-so {{ border: 1px solid var(--phieu); padding: 0.35rem 0.7rem 0.45rem; text-align: right; }}
.dp-so b {{ display: block; font-size: 1.15rem; color: var(--muc); letter-spacing: 0.02em; }}
.nhan {{ font-size: 0.74rem; font-weight: 600; color: var(--phieu); letter-spacing: 0.05em; text-transform: uppercase; }}
.ke-doi {{ height: 4px; border-top: 1px solid var(--phieu); border-bottom: 1px solid var(--phieu); margin: 0.2rem 0 0.9rem; }}
.stApp [data-testid="stWidgetLabel"] p {{ font-size: 0.74rem; font-weight: 600; color: var(--phieu); letter-spacing: 0.05em;
                                          text-transform: uppercase; }}

.stApp [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{ text-transform: none; letter-spacing: 0;
        font-size: 0.95rem; font-weight: 500; color: var(--muc); }}

/* the man (lien giay) */
.st-key-nav {{ margin-top: 0.7rem; }}
.st-key-nav [data-testid="stHorizontalBlock"] {{ gap: 0.35rem; }}
.st-key-nav a {{ border: 1px solid var(--ke); border-bottom: none;
                 padding: 0.45rem 0.9rem 0.5rem; border-radius: 0; justify-content: flex-start; width: 100%; max-width: none; }}
.st-key-nav [data-testid="stPageLink"] {{ width: 100%; }}
.st-key-nav a p {{ font-weight: 600; color: var(--muc2); font-size: 0.95rem; }}
.st-key-nav a:hover {{ filter: brightness(0.97); }}
[class*="st-key-tab_"][class*="_on"] a {{ border: 1px solid var(--phieu); border-bottom: none; }}
[class*="st-key-tab_"][class*="_on"] a p {{ color: var(--phieu); font-weight: 800; }}
{tabs}

/* tieu de muc */
.muc {{ display: flex; align-items: baseline; gap: 0.75rem; border-bottom: 1px solid var(--phieu);
        padding-bottom: 0.3rem; margin: 1.6rem 0 0.7rem; flex-wrap: wrap; }}
.muc h2 {{ font-size: 1.18rem; font-weight: 700; color: var(--phieu); margin: 0; padding: 0; letter-spacing: 0.005em; }}
.muc span {{ color: var(--muc2); font-size: 0.86rem; }}
.muc.dau-tien {{ margin-top: 0.4rem; }}

/* con dau */
.dau {{ display: inline-flex; align-items: center; gap: 0.3rem; color: var(--c); border: 3px double var(--c);
        padding: 0.12rem 0.5rem 0.14rem 0.4rem; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.06em;
        text-transform: uppercase; transform: rotate(-3deg); white-space: nowrap; line-height: 1.3;
        background: color-mix(in srgb, var(--c) 6%, transparent); }}
.dau-moi {{ animation: dong-dau 340ms cubic-bezier(0.2, 0.9, 0.3, 1) both; }}
@keyframes dong-dau {{ 0% {{ transform: scale(1.9) rotate(-11deg); opacity: 0; filter: blur(1.5px); }}
                      62% {{ transform: scale(0.94) rotate(-4deg); opacity: 1; filter: blur(0); }}
                      100% {{ transform: scale(1) rotate(-3deg); opacity: 1; }} }}
@media (prefers-reduced-motion: reduce) {{ .dau-moi {{ animation: none; }} }}

/* o phieu (nhan + so) */
.o-hang {{ display: grid; grid-template-columns: repeat(var(--n, 4), minmax(0, 1fr)); border: 1px solid var(--phieu); }}
.o-hang > div {{ padding: 0.45rem 0.7rem 0.55rem; border-left: 1px solid var(--ke); min-width: 0; }}
.o-hang > div:first-child {{ border-left: none; }}
.o-hang .so {{ display: block; font-size: 1.3rem; font-weight: 700; color: var(--muc); line-height: 1.25; }}
.o-hang .phu {{ display: block; font-size: 0.8rem; color: var(--muc2); }}
.o-hang .dao {{ background: var(--phieu); color: #fff; }}
.o-hang .dao .nhan, .o-hang .dao .so, .o-hang .dao .phu {{ color: #fff; }}

/* 4 o trang thai bam duoc (loc cheo) */
.stApp [class*="st-key-tt_"] button[kind] {{ width: 100%; min-height: 6.2rem; justify-content: flex-start; align-items: flex-start;
        text-align: left; border: 1px solid var(--phieu); border-radius: 0; background: transparent;
        padding: 0.6rem 0.8rem 0.6rem 2.6rem; position: relative; color: var(--muc); }}
[class*="st-key-tt_"] button::before {{ content: ""; position: absolute; left: 0.75rem; top: 0.85rem; width: 1.35rem;
        height: 1.35rem; background: var(--c); -webkit-mask-size: contain; mask-size: contain; }}
[class*="st-key-tt_"] button p {{ font-size: 0.95rem; font-weight: 600; text-align: left; color: inherit; }}
[class*="st-key-tt_"] button strong {{ display: block; font-size: 2.3rem; font-weight: 800; line-height: 1.05;
        margin-bottom: 0.15rem; color: var(--c); }}
.stApp [class*="st-key-tt_"] button[kind]:hover {{ background: color-mix(in srgb, var(--c) 7%, transparent); color: var(--muc);
        border-color: var(--phieu); }}
.stApp .st-key-tt_1 button[kind], .stApp .st-key-tt_1_on button[kind] {{ background: var(--phieu); color: #fff; }}
.st-key-tt_1 button strong, .st-key-tt_1_on button strong {{ color: var(--quang); }}
.st-key-tt_1 button::before, .st-key-tt_1_on button::before {{ background: var(--quang); }}
.stApp .st-key-tt_1 button[kind]:hover, .stApp .st-key-tt_1_on button[kind]:hover {{ background: #173f5d; color: #fff; }}
.stApp [class*="st-key-tt_"][class*="_on"] button[kind] {{ box-shadow: inset 0 0 0 3px var(--quang); }}
{masks}

/* nut bam chung */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {{ border-radius: 2px; font-weight: 600; }}
.stButton button[kind="secondary"], .stDownloadButton button[kind="secondary"] {{ background: transparent;
        border: 1px solid var(--phieu); color: var(--phieu); }}
.stButton button[kind="secondary"]:hover, .stDownloadButton button[kind="secondary"]:hover {{
        background: color-mix(in srgb, var(--phieu) 8%, transparent); color: var(--phieu); border-color: var(--phieu); }}
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {{ background: var(--quang); color: var(--muc);
        border: 1px solid var(--muc); }}
.stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {{ background: #ffd820;
        color: var(--muc); border-color: var(--muc); }}
.stButton button[kind="tertiary"] {{ color: var(--phieu); text-decoration: underline; text-underline-offset: 3px; }}

/* dong don hang can duyet */
[class*="st-key-don_"] {{ border-bottom: 1px solid var(--ke); padding: 0.55rem 0 0.6rem; gap: 0.25rem; }}
.don-ma {{ font-weight: 800; color: var(--phieu); letter-spacing: 0.02em; }}
.don-ten {{ font-weight: 600; color: var(--muc); }}
.don-phu {{ color: var(--muc2); font-size: 0.84rem; line-height: 1.45; }}
.don-so {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.4rem; }}
.don-so span {{ display: block; font-size: 0.72rem; line-height: 1.25; font-weight: 600; color: var(--phieu); letter-spacing: 0.04em;
               text-transform: uppercase; }}
.don-so b {{ font-size: 1.05rem; font-weight: 700; }}
.quang {{ background: linear-gradient(100deg, transparent 0 3%, var(--quang) 4% 95%, transparent 96%);
          padding: 0 0.35rem; margin-left: -0.35rem; }}
[class*="st-key-don_"][class*="_bo"] .don-ten, [class*="st-key-don_"][class*="_bo"] .don-ma {{
          text-decoration: line-through; text-decoration-color: var(--muc2); }}
[class*="st-key-don_"][class*="_bo"] .quang {{ background: none; }}

[class*="st-key-don_"] [data-testid="stButtonGroup"] button {{ border-radius: 0; font-weight: 600; }}
[class*="st-key-don_"] [data-testid="stButtonGroup"] button:first-child {{ background: var(--quang); color: var(--muc);
        border-color: var(--muc); }}
[class*="st-key-don_"] [data-testid="stButtonGroup"] button:first-child:hover {{ background: #ffd820; }}
[class*="st-key-don_"] [data-testid="stButtonGroup"] button[kind*="Active"] {{ background: var(--phieu); color: #fff;
        border-color: var(--phieu); }}

/* ghi chu duoi bieu do */
.ghi {{ border-top: 1px dashed var(--ke); padding-top: 0.45rem; margin-top: 0.2rem; font-size: 0.88rem; color: var(--muc2);
        line-height: 1.5; }}
.ghi b {{ color: var(--phieu); font-weight: 700; }}

/* bang kieu phieu */
table.phieu {{ width: 100%; border-collapse: collapse; border: 1px solid var(--phieu); font-size: 0.95rem; }}
table.phieu th {{ text-align: right; font-size: 0.72rem; font-weight: 600; color: var(--phieu); letter-spacing: 0.04em;
                  text-transform: uppercase; padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--phieu);
                  vertical-align: bottom; }}
table.phieu th:first-child, table.phieu td:first-child {{ text-align: left; }}
table.phieu td {{ text-align: right; padding: 0.5rem 0.6rem; border-top: 1px solid var(--ke); white-space: nowrap; }}
table.phieu td small {{ display: block; color: var(--muc2); font-size: 0.78rem; }}
table.phieu tr.chon td {{ font-weight: 700; }}
table.phieu tr.chon td {{ background: color-mix(in srgb, var(--quang) 38%, transparent); }}
.bang-cuon {{ overflow-x: auto; }}

/* tam nen dao mau (moi man 1 tam) */
.dao-mau {{ background: var(--phieu); color: #fff; padding: 0.8rem 1rem; font-size: 1.02rem; line-height: 1.5; }}
.dao-mau b {{ color: var(--quang); }}

/* chan phieu */
.chan-ke {{ margin-top: 2.2rem; }}
.chan {{ margin-top: 0.1rem; color: var(--muc2); font-size: 0.84rem; }}
[data-testid="stExpander"] details {{ border-radius: 0; border-color: var(--ke); background: transparent; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; color: var(--phieu); }}
[data-testid="stAlert"] {{ border-radius: 0; }}
@media (max-width: 640px) {{
  [data-testid="stMainBlockContainer"] {{ padding: 0.8rem 1rem 2rem; }}
  .dp-ten {{ font-size: 1.3rem; }}
  .o-hang {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .o-hang > div:nth-child(odd) {{ border-left: none; }}
  .o-hang > div:nth-child(n+3) {{ border-top: 1px solid var(--ke); }}
}}
</style>""", unsafe_allow_html=True)


def muc(ten, phu="", dau_tien=False):
    """Tieu de 1 muc cua phieu (duong ke mau muc phieu phia duoi)."""
    st.markdown(f'<div class="muc{" dau-tien" if dau_tien else ""}"><h2>{ten}</h2>'
                f'{f"<span>{phu}</span>" if phu else ""}</div>', unsafe_allow_html=True)


def ghi(cach_doc, phat_hien):
    """Ghi chu duoi moi bieu do: cach doc + dieu rut ra (tinh tu du lieu, khong ghi tay so lieu)."""
    st.markdown(f'<div class="ghi"><b>Cách đọc.</b> {cach_doc}<br><b>Phát hiện.</b> {phat_hien}</div>',
                unsafe_allow_html=True)


def o_hang(o, n=None):
    """Hang o phieu: o = [(nhan, so, phu, dao_mau)]."""
    the = "".join(f'<div class="{"dao" if d else ""}"><span class="nhan">{a}</span><span class="so">{b}</span>'
                  f'{f"<span class=phu>{c}</span>" if c else ""}</div>' for a, b, c, d in o)
    st.markdown(f'<div class="o-hang n{n or len(o)}">{the}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ bieu do (Altair) theo giao dien phieu
def _theme():
    return {"config": {
        "background": "transparent", "font": "Be Vietnam Pro",
        "view": {"stroke": None},
        "axis": {"labelColor": MUC2, "titleColor": PHIEU, "titleFontWeight": 600, "titleFontSize": 12, "labelFontSize": 12,
                 "domainColor": PHIEU, "tickColor": PHIEU, "gridColor": "#1d4f7322", "gridDash": [2, 3]},
        "legend": {"labelColor": MUC, "labelFontSize": 12, "titleColor": PHIEU, "symbolStrokeWidth": 2.5},
        "header": {"labelColor": PHIEU, "labelFontWeight": 600, "titleColor": PHIEU},
        "title": {"color": PHIEU, "fontWeight": 700, "fontSize": 13, "anchor": "start"},
        "text": {"color": MUC2, "fontSize": 12},
    }}


def theo_du_lieu(bd, *tham_so):
    """Gan tham so du lieu vao dac ta bieu do (usermeta). Streamlit 1.45: dac ta giu nguyen ma du lieu doi thi trinh duyet
    cap nhat du lieu tai cho theo ten bo du lieu (ma bam noi dung) va loi Vega "Unrecognized data set"; `key` khong co tac
    dung voi bieu do khong co chon. Dac ta doi theo du lieu -> Vega dung lai bieu do tu dau."""
    return bd.properties(usermeta={"du_lieu": "|".join(map(str, tham_so))})


try:
    alt.theme.register("phieu", enable=True)(_theme)
except AttributeError:                          # Altair cu
    alt.themes.register("phieu", _theme)
    alt.themes.enable("phieu")


# ------------------------------------------------------------------ doc CSDL (chi doc)
@st.cache_data(show_spinner=False)
def q(sql, params=()):
    with closing(sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)) as con:   # mode=ro: cong cu khong sua CSDL
        return pd.read_sql_query(sql, con, params=params)


def kiem_tra_csdl():
    lenh = "python src/nap_database.py\npython src/ton_kho.py"
    if not DB.exists():
        st.error(f"Chưa có cơ sở dữ liệu `{DB.relative_to(ROOT)}`. Chạy tại thư mục gốc dự án:")
        st.code(lenh, language="bash")
        st.stop()
    try:
        n = q("SELECT (SELECT COUNT(*) FROM mo_phong_ngay) AS mp, (SELECT COUNT(*) FROM mo_hinh WHERE duoc_chon = 1) AS mh")
    except Exception:                           # bang chua co (CSDL cu)
        n = pd.DataFrame({"mp": [0], "mh": [0]})
    if n.mp.iloc[0] == 0 or n.mh.iloc[0] == 0:
        st.error("CSDL chưa có kết quả tồn kho (GĐ F) hoặc chưa chọn mô hình. Chạy lại:")
        st.code(lenh, language="bash")
        st.stop()


@st.cache_data(show_spinner=False)
def mo_hinh_chon():
    return q("SELECT ma_mo_hinh, mo_ta FROM mo_hinh WHERE duoc_chon = 1").iloc[0]


@st.cache_data(show_spinner=False)
def ds_sku():
    return q("""SELECT s.ma_sku, s.ten_sku, s.nhom_hang, s.don_vi, s.ma_ncc, s.gia_von, s.lead_time_tb, s.lead_time_std, s.moq,
                       s.chi_phi_dat_hang, s.ty_le_chi_phi_luu_kho, p.abc_train, p.xyz_train, p.loai_nhu_cau
                FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku) ORDER BY s.ma_sku""")


@st.cache_data(show_spinner=False)
def mo_phong(cs):
    """Mo phong tung ngay cua 1 chinh sach (muc phuc vu 95%) + hang dang ve + trang thai canh bao (chi so trong TRANG_THAI)."""
    m = q("""SELECT ngay, ma_sku, nhap, nhu_cau, xuat, ton_cuoi, dat_hang, rop FROM mo_phong_ngay
             WHERE ma_chinh_sach = ? ORDER BY ma_sku, ngay""", (cs,))
    m[["dat_hang", "rop"]] = m[["dat_hang", "rop"]].astype(float)    # hien trang: toan NULL (khong dung cong thuc)
    gd = q("SELECT ngay, ma_sku, qty_in FROM giao_dich_sach WHERE ngay >= ? AND ngay < date(?, '+60 day')",
           (m.ngay.min(), m.ngay.min()))
    m["dang_ve"] = hang_dang_ve(m, ds_sku().set_index("ma_sku").lead_time_tb, gd)
    m["tt"] = trang_thai_ton_kho(m).map({s: i for i, s in enumerate(TRANG_THAI)})
    m.loc[m.rop.isna(), "tt"] = np.nan                               # ngay kho nghi: khong xet
    return m


@st.cache_data(show_spinner=False)
def ngay_mo_cua(cs):
    m = mo_phong(cs)
    return sorted(m.loc[m.rop.notna(), "ngay"].unique())


@st.cache_data(show_spinner=False)
def du_bao_dot(cs):
    """Du bao 28 ngay cua tung dot (da nhan he so hieu chinh) cho chinh sach cs: {ma_sku: mang (so dot, 28)}, ngay dau mo phong."""
    mh = MOC if cs == "cong_thuc_du_bao_moc" else mo_hinh_chon().ma_mo_hinh
    d = q("SELECT moc, ma_sku, ngay_thu, du_bao FROM du_bao WHERE ma_mo_hinh = ? AND tap = 'test'", (mh,))
    dots = sorted(d.moc.unique())
    hs = tham_so(cs).he_so_hieu_chinh
    F = {s: g.pivot(index="moc", columns="ngay_thu", values="du_bao").reindex(dots).values * hs[s] for s, g in d.groupby("ma_sku")}
    return F, pd.Timestamp(dots[0]) + pd.Timedelta(days=1)


@st.cache_data(show_spinner=False)
def tham_so(cs, lv=MAIN):
    return q("""SELECT ma_sku, he_so_hieu_chinh, sigma_ltd, ss_tb, rop_tb, eoq_tb FROM tham_so_ton_kho
                WHERE ma_chinh_sach = ? AND ROUND(muc_phuc_vu, 2) = ?""", (cs, lv)).set_index("ma_sku")


def thu_neu(cs, ma, t, lv=MAIN, them_ngay=0):
    """SS, ROP, EOQ va luong dat cua 1 ma tai ngay t khi doi muc phuc vu / lead time (csdl.de_xuat_ngay, cung cong thuc
    mo phong). Lead time dai them k ngay: L' = L + k; sai so du bao trong L' ngay gia dinh tang theo can bac 2 (sai so
    tung ngay doc lap) - gia dinh, khong do lai tren validation."""
    F, t0 = du_bao_dot(cs)
    r = ds_sku().set_index("ma_sku").loc[ma]
    m = mo_phong(cs)
    hom = m[(m.ma_sku == ma) & (m.ngay == t)].iloc[0]
    i = (pd.Timestamp(t) - t0).days
    k = min((i + 1) // HORIZON, F[ma].shape[0] - 1)
    L = max(1, int(round(r.lead_time_tb)))
    sig = tham_so(cs).sigma_ltd[ma] * np.sqrt((L + them_ngay) / L)
    o = de_xuat_ngay(F[ma][k], i + 1 - HORIZON * k, L + them_ngay, sig, norm.ppf(lv), r.lead_time_std,
                     r.chi_phi_dat_hang, r.ty_le_chi_phi_luu_kho * r.gia_von, r.moq, hom.ton_cuoi + hom.dang_ve - hom.dat_hang)
    return o | dict(ip=hom.ton_cuoi + hom.dang_ve - hom.dat_hang, L=L + them_ngay)


# ------------------------------------------------------------------ bo loc chung (slicer)
LOC_CHUNG = dict(ngay=NGAY_MAC_DINH, cs=CS_GOI_Y, abc=[], xyz=[])   # bo loc chung o dau phieu


def khoi_tao():
    """Gia tri that cua bo loc chung luu o khoa rieng (ngay, cs, abc, xyz); o nhap o dau phieu dung khoa _w_<ten> va chep
    qua lai. Khong dung thang khoa cua widget: chuyen man bang st.switch_page thi Streamlit tao widget moi va DAT LAI gia tri
    mac dinh (da gap: doi ngay o Hom nay, bam "Xem mat hang" -> ngay quay ve 09/02)."""
    s = st.session_state
    for k, v in dict(LOC_CHUNG, sku=None, qd={}, loc_tt=None).items():
        s.setdefault(k, v)
    for k in LOC_CHUNG:                         # o nhap ve lai o lan chay nay mang gia tri that
        s[f"_w_{k}"] = s[k]


def _chep(k):
    st.session_state[k] = st.session_state[f"_w_{k}"]


def doi_ngay(d):
    """Dat ngay 'hom nay' tu thao tac tren bieu do (o ngay da ve trong lan chay nay -> hien ngay moi o lan chay sau)."""
    d = pd.Timestamp(d).date()
    if d != st.session_state.ngay:
        st.session_state.ngay = d
        st.rerun()


def doi_chinh_sach(cs):
    if cs != st.session_state.cs:
        st.session_state.cs = cs
        st.rerun()


def chon_tu_bieu_do(su_kien, ten, cot, khoa):
    """Gia tri vua bam tren bieu do (on_select). Chi tra ve khi lua chon MOI (bieu do giu lua chon qua cac lan chay)."""
    sel = (su_kien or {}).get("selection", {}).get(ten) or []
    v = sel[0].get(cot) if sel else None
    if v is None or st.session_state.get(khoa) == v:
        st.session_state[khoa] = v
        return None
    st.session_state[khoa] = v
    return v


def sku_loc():
    """Danh sach ma theo bo loc nhom ABC / XYZ o dau phieu."""
    s, p = st.session_state, ds_sku()
    if s.abc:
        p = p[p.abc_train.isin(s.abc)]
    if s.xyz:
        p = p[p.xyz_train.isin(s.xyz)]
    return p


def mo_ta_loc():
    s = st.session_state
    phan = ([f"ABC {', '.join(s.abc)}"] if s.abc else []) + ([f"XYZ {', '.join(s.xyz)}"] if s.xyz else [])
    return " · ".join(phan) if phan else "cả 121 mã"


def ngay_lam_viec():
    """Ngay dang xem (chuoi ISO) = ngay chon o dau phieu, neu kho nghi thi lui ve ngay lam viec gan nhat."""
    mo = ngay_mo_cua(st.session_state.cs)
    t = st.session_state.ngay.isoformat()
    if t in mo:
        return t, None
    truoc = [x for x in mo if x <= t]
    t2 = truoc[-1] if truoc else mo[0]
    return t2, f"{ngay_vn(t)} kho nghỉ, phiếu lập theo ngày làm việc gần nhất trước đó: {ngay_vn(t2)}."


def dau_phieu(trang, cac_trang):
    """Dau phieu: ten phieu, cac o loc chung, so phieu, the chuyen man (moi man 1 lien giay)."""
    s = st.session_state
    mo = ngay_mo_cua(s.cs)
    c = st.columns([3.1, 1.25, 1.75, 1.15, 1.15, 1.25], vertical_alignment="bottom")
    c[0].markdown('<div class="dp-ten">Phiếu kế hoạch đặt hàng</div><div class="dp-phu">Kho tổng chuỗi siêu thị · 121 mã hàng · '
                  'dữ liệu mô phỏng</div>', unsafe_allow_html=True)
    c[1].date_input("Ngày lập phiếu", key="_w_ngay", on_change=_chep, args=("ngay",), min_value=date.fromisoformat(mo[0]), max_value=date.fromisoformat(mo[-1]),
                    format="DD/MM/YYYY", help="Giả lập “hôm nay” trong 12 tháng kiểm tra (01/10/2025 – 29/09/2026).")
    c[2].selectbox("Chính sách đặt hàng", CS_CONG_THUC, key="_w_cs", on_change=_chep, args=("cs",), format_func=CS_TEN.get,
                   help="Cách tính SS / ROP / EOQ dùng để mô phỏng. Áp cho mọi màn.")
    c[3].pills("Nhóm ABC", ["A", "B", "C"], selection_mode="multi", key="_w_abc", on_change=_chep, args=("abc",),
               help="A: giá trị xuất cao → C: thấp. Không chọn = tất cả.")
    c[4].pills("Nhóm XYZ", ["X", "Y", "Z"], selection_mode="multi", key="_w_xyz", on_change=_chep, args=("xyz",),
               help="X: nhu cầu ổn định · Y: dao động vừa · Z: mùa vụ / thất thường. Không chọn = tất cả.")
    t, _ = ngay_lam_viec()
    c[5].markdown(f'<div class="dp-so"><span class="nhan">Số phiếu</span><b>KH-{t[2:4]}{t[5:7]}{t[8:]}</b></div>',
                  unsafe_allow_html=True)
    with st.container(key="nav"):
        cols = st.columns([1, 1, 1.25, 1.35, 2.2])
        for col, (k, p) in zip(cols, cac_trang.items()):
            with col.container(key=f"tab_{k.replace('-', '_')}{'_on' if k == trang else ''}"):
                st.page_link(p, label=p.title)
    st.markdown('<div class="ke-doi"></div>', unsafe_allow_html=True)


def chan_phieu():
    cm = mo_hinh_chon()
    st.markdown('<div class="ke-doi chan-ke"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([5, 1], vertical_alignment="center")
    c1.markdown(f'<div class="chan">{NOTE} Mọi số liệu đọc trực tiếp (chỉ đọc) từ cơ sở dữ liệu SQLite '
                f'<code>data/kho_hang.db</code>, cập nhật lúc {datetime.fromtimestamp(DB.stat().st_mtime):%H:%M %d/%m/%Y}. '
                f'Mô hình dự báo đang dùng: <code>{cm.ma_mo_hinh}</code>. Quyết định duyệt đơn chỉ giữ trong phiên làm việc.</div>',
                unsafe_allow_html=True)
    if c2.button("Tải lại dữ liệu", help="Bấm sau khi chạy lại nap_database.py / ton_kho.py", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
