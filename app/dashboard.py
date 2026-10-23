"""GD G: dashboard ban gon (Streamlit). DOC TU CO SO DU LIEU data/kho_hang.db, CHI DOC (khong ghi gi vao CSDL).
Chay (tai thu muc goc du an):  streamlit run app/dashboard.py
Can chay truoc:                python src/nap_database.py && python src/ton_kho.py
5 khu: (1) tong quan du lieu (du lieu la gi, mua vu, thu trong tuan, khuyen mai, ABC x XYZ, xep hang mo hinh),
       (2) du bao vs thuc te theo SKU, (3) canh bao ton kho theo ngay (het hang, cham ROP, ton duoi ROP),
       (4) KPI truoc - sau giua cac chinh sach + thu do nhay, (5) bang tham so SS / ROP / EOQ tung SKU.
Moi bieu do kem "cach doc" va "phat hien"; phat hien tinh tu du lieu (khong ghi tay so lieu).
Mau giong reports/ket_qua (src/bieu_do_ket_qua.py): thuc te = den, AI = xanh duong, du bao moc = cam, hien trang = xam.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from csdl import TRANG_THAI, hang_dang_ve, trang_thai_ton_kho  # noqa: E402  (dung chung voi src/xuat_power_bi.py)

DB = ROOT / "data" / "kho_hang.db"
MAIN = 0.95                                   # muc phuc vu chinh (GD F); mo_phong_ngay chi luu muc nay
CS_GOI_Y = "cong_thuc_du_bao_ai_hc"           # chinh sach de xuat sau GD F
MOC = "tb_truot_28"                           # du bao moc tot nhat (GD C)

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
BLUE, ORANGE = "#2a78d6", "#eb6834"
CS_TEN = {"hien_trang": "Hiện trạng*", "cong_thuc_du_bao_moc": "Công thức + dự báo mốc",
          "cong_thuc_du_bao_ai": "Công thức + dự báo AI", "cong_thuc_du_bao_ai_hc": "AI + hiệu chỉnh lệch (đề xuất)"}
CS_MAU = {"hien_trang": MUTED, "cong_thuc_du_bao_moc": ORANGE, "cong_thuc_du_bao_ai": "#86b6ef", "cong_thuc_du_bao_ai_hc": BLUE}
CS_CONG_THUC = [c for c in CS_TEN if c != "hien_trang"]
ICON = ["🔴", "🟠", "🟡", "🟢"]                 # theo thu tu csdl.TRANG_THAI; trang thai luon kem chu, khong chi mau
MAU_TT = ["#d03b3b", "#ec835a", "#fab219"]     # mau trang thai (het hang / dat hang / duoi ROP), khong dung cho chuoi so lieu
SURFACE, AQUA, YELLOW = "#fcfcfb", "#1baf7a", "#eda100"
THU = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
NOTE = "Dữ liệu mô phỏng, không phải số liệu kho thật."
NOTE_HT = ("\\* Hiện trạng: người lập kế hoạch trong dữ liệu mô phỏng **biết trước nhu cầu kỳ vọng** (lệch ±10%), "
           "nên là đối thủ mạnh hơn thực tế.")
vn = lambda v, nd=1: f"{v:,.{nd}f}".replace(",", "_").replace(".", ",").replace("_", ".")
ngay_vn = lambda s: pd.Timestamp(s).strftime("%d/%m/%Y")

st.set_page_config(page_title="Dự báo & tồn kho", page_icon="📦", layout="wide")


# ------------------------------------------------------------------ doc CSDL (chi doc)
@st.cache_data(show_spinner=False)
def q(sql, params=()):
    with closing(sqlite3.connect(DB.as_uri() + "?mode=ro", uri=True)) as con:   # mode=ro: dashboard khong sua CSDL
        return pd.read_sql_query(sql, con, params=params)


def kiem_tra_csdl():
    lenh = "python src/nap_database.py\npython src/ton_kho.py"
    if not DB.exists():
        st.error(f"Chưa có cơ sở dữ liệu `{DB.relative_to(ROOT)}`. Chạy tại thư mục gốc dự án:")
        st.code(lenh, language="bash")
        st.stop()
    try:
        n = q("SELECT (SELECT COUNT(*) FROM mo_phong_ngay) AS mp, (SELECT COUNT(*) FROM mo_hinh WHERE duoc_chon = 1) AS mh")
    except Exception as e:                    # bang chua co (CSDL cu)
        n = pd.DataFrame({"mp": [0], "mh": [0], "loi": [str(e)]})
    if n.mp.iloc[0] == 0 or n.mh.iloc[0] == 0:
        st.error("CSDL chưa có kết quả tồn kho (GĐ F) hoặc chưa chọn mô hình. Chạy lại:")
        st.code(lenh, language="bash")
        st.stop()


@st.cache_data(show_spinner=False)
def ds_sku():
    return q("""SELECT s.ma_sku, s.ten_sku, s.nhom_hang, s.don_vi, s.lead_time_tb, s.lead_time_std, s.moq,
                       p.abc_train, p.xyz_train, p.loai_nhu_cau
                FROM dm_sku s JOIN phan_loai_sku p USING (ma_sku) ORDER BY s.ma_sku""")


@st.cache_data(show_spinner=False)
def mo_phong(cs):
    """Mo phong tung ngay cua 1 chinh sach (muc phuc vu 95%) + hang dang ve cuoi ngay (csdl.hang_dang_ve)."""
    m = q("""SELECT ngay, ma_sku, nhap, nhu_cau, xuat, ton_cuoi, dat_hang, rop FROM mo_phong_ngay
             WHERE ma_chinh_sach = ? ORDER BY ma_sku, ngay""", (cs,))
    m[["dat_hang", "rop"]] = m[["dat_hang", "rop"]].astype(float)    # hien trang: toan NULL (khong dung cong thuc)
    gd = q("SELECT ngay, ma_sku, qty_in FROM giao_dich_sach WHERE ngay >= ? AND ngay < date(?, '+60 day')",
           (m.ngay.min(), m.ngay.min()))
    m["dang_ve"] = hang_dang_ve(m, ds_sku().set_index("ma_sku").lead_time_tb, gd)
    return m


@st.cache_data(show_spinner=False)
def du_bao_chon():
    return q("SELECT moc, ngay, ma_sku, du_bao, thuc_te FROM v_du_bao_chon")


@st.cache_data(show_spinner=False)
def he_so(cs):
    return q("SELECT ma_sku, he_so_hieu_chinh FROM tham_so_ton_kho WHERE ma_chinh_sach = ? AND ROUND(muc_phuc_vu, 2) = ?",
             (cs, MAIN)).set_index("ma_sku").he_so_hieu_chinh


@st.cache_data(show_spinner="Đang tính số liệu tổng quan…")
def tong_quan():
    """So lieu cho khu Tong quan, tinh tu giao_dich_sach. Mua vu, thu trong tuan, khuyen mai chi dung ngay kho mo cua va
    khong het hang (ngay het hang ban ra thap hon cau that). Chi so = luong ban TB trong nhom ngay / luong ban TB moi ngay
    cua chinh SKU do (1 = binh thuong), roi lay trung binh cac SKU -> SKU ban nhieu khong lan at SKU ban it."""
    g = q("""SELECT g.ngay, g.ma_sku, g.qty_out, g.het_hang, g.la_ngay_nghi, s.gia_von, s.nhom_hang
             FROM giao_dich_sach g JOIN dm_sku s USING (ma_sku)""")
    g["d"] = pd.to_datetime(g.ngay)
    tuan = (g.assign(trieu=g.qty_out * g.gia_von / 1e6).groupby("d").trieu.sum()
            .resample("W-MON", label="left", closed="left").sum().reset_index().rename(columns={"d": "ngay"}))
    nam = g.assign(gt=g.qty_out * g.gia_von).groupby(pd.cut(g.d, pd.to_datetime(["2023-10-01", "2024-10-01", "2025-10-01",
                                                                                  "2026-10-01"]), right=False), observed=False).gt.sum()
    ok = g[(g.het_hang == 0) & (g.la_ngay_nghi == 0)].copy()
    tb = ok.groupby("ma_sku").qty_out.mean()
    ok["thu"], ok["thang"], ok["ym"] = ok.d.dt.weekday, ok.d.dt.month, ok.d.dt.to_period("M")
    thu = (ok.groupby(["ma_sku", "thu"]).qty_out.mean() / tb).groupby("thu").mean().rename("chi_so").reset_index()
    mua = ((ok.groupby(["ma_sku", "thang"]).qty_out.mean() / tb).rename("chi_so").reset_index()
           .merge(g[["ma_sku", "nhom_hang"]].drop_duplicates(), on="ma_sku")
           .groupby(["nhom_hang", "thang"]).chi_so.mean().reset_index())
    # khuyen mai: luong ban TB trong dot so voi ngay khong khuyen mai cung SKU, cung thang
    km = q("SELECT ma_sku, tu_ngay, den_ngay FROM lich_khuyen_mai").reset_index(names="dot_km")
    km["d"] = [pd.date_range(a, b) for a, b in zip(km.tu_ngay, km.den_ngay)]
    kd = km.explode("d")[["dot_km", "ma_sku", "d"]]
    kd["d"] = pd.to_datetime(kd.d)
    x = ok.merge(kd, on=["ma_sku", "d"], how="left")
    nen = x[x.dot_km.isna()].groupby(["ma_sku", "ym"]).qty_out.mean().rename("nen")
    dot = (x[x.dot_km.notna()].groupby("dot_km").agg(ma_sku=("ma_sku", "first"), ym=("ym", "first"), q=("qty_out", "mean"))
           .join(nen, on=["ma_sku", "ym"]))
    tang = (100 * (dot.q / dot.nen - 1)).dropna().rename("tang").reset_index(drop=True)
    gt_train = (g[g.ngay <= "2025-09-30"].assign(gt=lambda f: f.qty_out * f.gia_von).groupby("ma_sku").gt.sum())
    p = q("SELECT ma_sku, abc_train AS abc, xyz_train AS xyz FROM phan_loai_sku").assign(gia_tri=lambda f: f.ma_sku.map(gt_train))
    abcxyz = p.groupby(["abc", "xyz"]).agg(so_ma=("ma_sku", "size"), gia_tri=("gia_tri", "sum")).reset_index()
    abcxyz["pt"] = 100 * abcxyz.gia_tri / abcxyz.gia_tri.sum()
    return tuan, nam.values, thu, mua, tang, abcxyz


@st.cache_data(show_spinner=False)
def trang_thai_ca_nam(cs):
    """So SKU moi trang thai canh bao, tung ngay kho mo cua trong nam test."""
    m = mo_phong(cs)
    m = m[m.rop.notna()].copy()
    m["trang_thai"] = trang_thai_ton_kho(m)
    return m[m.trang_thai != TRANG_THAI[3]].groupby(["ngay", "trang_thai"]).size().rename("so_sku").reset_index()


# ------------------------------------------------------------------ bieu do duong dung chung
def bieu_do_duong(df, series, y_title, x_fmt="%d/%m/%Y", ngay_chon=None, height=340):
    """df: cot 'ngay' + moi chuoi 1 cot. series: [(cot, nhan, mau, net_dut)].
    Ngay khong co gia tri (NaN) lam dut duong, khong noi qua. Re chuot: duong doc + tooltip moi chuoi."""
    nhan = [s[1] for s in series]
    longs = []
    for cot, ten, _, _ in series:
        x = df[["ngay", cot]].rename(columns={cot: "gia_tri"})
        x["doan"] = x.gia_tri.isna().cumsum()             # moi khoang trong mo 1 doan moi
        longs.append(x.dropna().assign(chuoi=ten))
    long = pd.concat(longs)
    color = alt.Color("chuoi:N", title=None, scale=alt.Scale(domain=nhan, range=[s[2] for s in series]),
                      legend=alt.Legend(orient="top", labelLimit=320))
    dash = alt.StrokeDash("chuoi:N", scale=alt.Scale(domain=nhan, range=[[6, 4] if s[3] else [1, 0] for s in series]),
                          legend=None)
    x_enc = alt.X("ngay:T", title=None, axis=alt.Axis(format="%m/%Y", labelColor=MUTED, grid=False))
    lines = alt.Chart(long).mark_line(strokeWidth=2).encode(
        x=x_enc, y=alt.Y("gia_tri:Q", title=y_title, axis=alt.Axis(format="d")), color=color, strokeDash=dash, detail="doan:N")
    near = alt.selection_point(nearest=True, on="pointerover", fields=["ngay"], empty=False, clear="pointerout")
    tip = [alt.Tooltip("ngay:T", title="Ngày", format=x_fmt)] + [
        alt.Tooltip(f"{cot}:Q", title=ten, format=".0f") for cot, ten, _, _ in series]
    rule = alt.Chart(df).mark_rule(color=MUTED, strokeWidth=1).encode(
        x="ngay:T", opacity=alt.condition(near, alt.value(0.8), alt.value(0)), tooltip=tip).add_params(near)
    layers = [lines, rule]
    if ngay_chon is not None:
        mark = pd.DataFrame({"ngay": [pd.Timestamp(ngay_chon)]})
        layers.append(alt.Chart(mark).mark_rule(color=INK2, strokeWidth=1.5, strokeDash=[2, 2]).encode(x="ngay:T"))
    st.altair_chart(alt.layer(*layers).properties(height=height), use_container_width=True)


def chi_so(a, f):
    """WMAPE va Bias % tren cac ngay duoc cham (thuc te khac NaN). Bias duong = du bao thieu (giong danh_gia.py)."""
    ok = ~np.isnan(a)
    s = a[ok].sum()
    if s <= 0:
        return np.nan, np.nan
    e = a[ok] - f[ok]
    return np.abs(e).sum() / s, e.sum() / s


# ================================================================== GIAO DIEN
kiem_tra_csdl()
sku = ds_sku()
TEN_SKU = dict(zip(sku.ma_sku, sku.ten_sku))
chon = q("SELECT ma_mo_hinh, mo_ta FROM mo_hinh WHERE duoc_chon = 1").iloc[0]

with st.sidebar:
    st.markdown("### 📦 Dự báo nhu cầu & tồn kho")
    st.caption(NOTE)
    st.markdown(f"**Mô hình dự báo đang dùng:** `{chon.ma_mo_hinh}`  \n{chon.mo_ta}")
    st.markdown(f"**Chính sách đề xuất:** {CS_TEN[CS_GOI_Y]}, mức phục vụ {MAIN:.0%}")
    st.markdown("**Giai đoạn kiểm tra:** 12 tháng test 01/10/2025 – 29/09/2026, 121 SKU")
    st.caption(f"CSDL `data/kho_hang.db`, cập nhật lúc {datetime.fromtimestamp(DB.stat().st_mtime):%H:%M %d/%m/%Y}. "
               "Dashboard chỉ đọc, không sửa dữ liệu.")
    if st.button("🔄 Tải lại dữ liệu từ CSDL", help="Bấm sau khi chạy lại nap_database.py / ton_kho.py"):
        st.cache_data.clear()
        st.rerun()

st.title("Dự báo nhu cầu và tối ưu tồn kho")
st.caption(f"{NOTE} Mọi số liệu đọc trực tiếp từ cơ sở dữ liệu SQLite của dự án.")
tab0, tab1, tab2, tab3, tab4 = st.tabs(["① Tổng quan dữ liệu", "② Dự báo theo SKU", "③ Cảnh báo tồn kho",
                                        "④ Trước – sau", "⑤ Tham số SS / ROP / EOQ"])


def doc_bieu_do(cach_doc, phat_hien):
    """Moi bieu do kem 2 dong: cach doc va dieu rut ra (tinh tu du lieu, khong ghi tay)."""
    st.markdown(f"<small>**Cách đọc:** {cach_doc}<br>**Phát hiện:** {phat_hien}</small>", unsafe_allow_html=True)


# ------------------------------------------------------------------ KHU 0: tong quan du lieu
with tab0:
    n = q("""SELECT (SELECT COUNT(*) FROM dm_sku) AS sku, (SELECT COUNT(DISTINCT nhom_hang) FROM dm_sku) AS nhom,
                    (SELECT COUNT(*) FROM giao_dich_sach) AS dong, (SELECT COUNT(DISTINCT ngay) FROM giao_dich_sach) AS ngay,
                    (SELECT MIN(ngay) FROM giao_dich_sach) AS tu, (SELECT MAX(ngay) FROM giao_dich_sach) AS den,
                    (SELECT COUNT(*) FROM giao_dich_tho) AS tho, (SELECT COUNT(*) FROM nhat_ky_sua_loi) AS sua,
                    (SELECT AVG(het_hang) FROM giao_dich_sach WHERE la_ngay_nghi = 0) AS het""").iloc[0]
    st.markdown("#### Dữ liệu này là gì")
    for col, (nhan, gt, phu) in zip(st.columns(4), [
            ("Mặt hàng (SKU)", int(n.sku), f"{n.nhom} nhóm hàng"),
            ("Số ngày", f"{n.ngay:,}".replace(",", "."), f"{ngay_vn(n.tu)} – {ngay_vn(n.den)}"),
            ("Dòng nhập – xuất – tồn", f"{n.dong:,}".replace(",", "."), "mỗi mặt hàng × mỗi ngày 1 dòng"),
            ("Dòng lỗi đã sửa khi làm sạch", int(n.sua), f"từ {n.tho:,} dòng thô có lỗi".replace(",", "."))]):
        col.metric(nhan, gt)
        col.caption(phu)
    st.info(
        "**Đây là dữ liệu mô phỏng** (máy sinh ra theo quy tắc), vì chưa có dữ liệu từ kho thật. "
        "Tên hàng là sản phẩm phổ biến trên thị trường nhưng **mọi con số không phải của hãng hay của kho nào**.\n\n"
        "- **Lấy từ nguồn thật:** ngày các cơn bão (bão Yagi 07/09/2024, các bão năm 2025), ngày lễ Tết, Trung thu, "
        "lịch sale 11.11 / 12.12 / Black Friday.\n"
        "- **Giả định:** lượng bán từng ngày, mức tăng do lễ, bão, khuyến mãi; giá vốn, chi phí đặt hàng, lưu kho; "
        f"thời gian giao hàng; lỗi cài sẵn trong dữ liệu thô (thiếu số, nhập sai, dòng trùng); {vn(n.het * 100)}% ngày-mặt hàng hết hàng.\n"
        "- **Vì sao vẫn dùng được:** mục tiêu là xây **quy trình** dự báo và đặt hàng, rồi **so sánh các cách làm với nhau** "
        "trên cùng dữ liệu. Khi có file xuất – nhập – tồn của kho thật (cùng tên cột), chạy lại toàn bộ là ra kết quả thật.")

    tuan, nam, thu, mua, tang, abcxyz = tong_quan()

    st.markdown("#### 1. Giá trị hàng xuất kho mỗi tuần, 3 năm")
    su_kien = pd.DataFrame(
        [("Tết", d) for d in q("SELECT ngay FROM lich_su_kien WHERE ten_su_kien = 'tet'").ngay]
        + [("Trung thu", d) for d in q("SELECT ngay FROM lich_su_kien WHERE ten_su_kien = 'trung_thu'").ngay]
        + [("Bão Yagi", "2024-09-07")] + [("Sale 11.11", f"{y}-11-11") for y in (2023, 2024, 2025)],
        columns=["su_kien", "ngay"])
    su_kien["ngay"] = pd.to_datetime(su_kien.ngay)
    sk_mau = alt.Scale(domain=["Tết", "Trung thu", "Bão Yagi", "Sale 11.11"], range=[ORANGE, AQUA, MUTED, YELLOW])
    test = pd.DataFrame({"tu": [pd.Timestamp("2025-10-01")], "den": [tuan.ngay.max()], "nhan": ["Năm dùng để kiểm tra mô hình"]})
    near = alt.selection_point(nearest=True, on="pointerover", fields=["ngay"], empty=False, clear="pointerout")
    nen = alt.Chart(test).mark_rect(color="#f0efec").encode(x="tu:T", x2="den:T")
    nen_txt = alt.Chart(test).mark_text(align="left", dx=6, dy=10, baseline="top", color=MUTED, fontSize=11).encode(
        x="tu:T", y=alt.value(0), text="nhan:N")
    duong = alt.Chart(tuan).mark_line(color=INK, strokeWidth=1.5).encode(
        x=alt.X("ngay:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False)),
        y=alt.Y("trieu:Q", title="Triệu đồng / tuần (theo giá vốn)", axis=alt.Axis(format="d")))
    moc = alt.Chart(su_kien).mark_rule(strokeWidth=1.5, strokeDash=[4, 3]).encode(
        x="ngay:T", color=alt.Color("su_kien:N", scale=sk_mau, title=None, legend=alt.Legend(orient="top")),
        tooltip=[alt.Tooltip("su_kien:N", title="Sự kiện"), alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y")])
    re = alt.Chart(tuan).mark_rule(color=MUTED).encode(
        x="ngay:T", opacity=alt.condition(near, alt.value(0.7), alt.value(0)),
        tooltip=[alt.Tooltip("ngay:T", title="Tuần từ", format="%d/%m/%Y"),
                 alt.Tooltip("trieu:Q", title="Triệu đồng", format=".0f")]).add_params(near)
    st.altair_chart(alt.layer(nen, nen_txt, duong, moc, re).properties(height=300), use_container_width=True)
    dinh = tuan.loc[tuan.trieu.idxmax()]
    tet = su_kien[su_kien.su_kien == "Tết"].ngay
    cach_tet = (tet[tet >= dinh.ngay] - dinh.ngay).dt.days.min()
    ghi_tet = f" ({cach_tet} ngày trước Tết)" if cach_tet <= 30 else ""
    doc_bieu_do("mỗi điểm là tổng giá trị hàng xuất trong 1 tuần (số lượng × giá vốn, cộng 121 mặt hàng). "
                "Đường đứt màu là các sự kiện; vùng xám là năm dùng để chấm điểm mô hình.",
                f"tuần cao nhất bắt đầu {ngay_vn(dinh.ngay)}{ghi_tet}, gấp {vn(dinh.trieu / tuan.trieu.median())} lần một "
                f"tuần bình thường; tuần Tết kho nghỉ nên tụt sâu. Tổng năm 3 so với năm 1: "
                f"{'+' if nam[2] >= nam[0] else ''}{vn((nam[2] / nam[0] - 1) * 100)}% → nhu cầu gần như đi ngang, "
                "biến động chủ yếu do mùa và sự kiện.")

    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.markdown("#### 2. Mùa vụ: tháng nào bán nhiều, theo nhóm hàng")
        hm = mua.copy()
        hm["mau"] = np.log2(hm.chi_so.clip(lower=0.125)).clip(-3, 3)        # log: gap doi va giam mot nua cach deu 1
        hm["nhan"] = np.where(hm.chi_so >= 2, "×" + hm.chi_so.map(lambda v: vn(v, 1)), "")
        thu_tu = hm.groupby("nhom_hang").chi_so.max().sort_values(ascending=False).index.tolist()
        base = alt.Chart(hm).encode(x=alt.X("thang:O", title="Tháng", axis=alt.Axis(labelAngle=0)),
                                    y=alt.Y("nhom_hang:N", sort=thu_tu, title=None))
        o = base.mark_rect(stroke=SURFACE, strokeWidth=2).encode(
            color=alt.Color("mau:Q", scale=alt.Scale(domain=[-3, 0, 3], range=[BLUE, "#f1f0ec", "#c4452c"], interpolate="rgb"), legend=None),
            tooltip=[alt.Tooltip("nhom_hang:N", title="Nhóm hàng"), alt.Tooltip("thang:O", title="Tháng"),
                     alt.Tooltip("chi_so:Q", title="So với bình thường (lần)", format=".2f")])
        chu = base.mark_text(fontSize=10).encode(
            text="nhan:N", color=alt.condition(alt.datum.chi_so >= 3, alt.value("white"), alt.value(INK)))
        st.altair_chart((o + chu).properties(height=430), use_container_width=True)
        top = hm.loc[hm.groupby("nhom_hang").chi_so.idxmax()].sort_values("chi_so", ascending=False).head(3)
        doc_bieu_do("1 = bán bình thường của chính nhóm đó. **Đỏ** = bán nhiều hơn (ô ghi ×2 trở lên), "
                    "**xanh** = bán ít hơn, xám nhạt = bình thường.",
                    "mạnh nhất: " + "; ".join(f"{r.nhom_hang} tháng {r.thang} ×{vn(r.chi_so)}" for r in top.itertuples())
                    + ". Các đỉnh trùng Tết (tháng 1–2), mùa hè, Trung thu (tháng 9), Noel (tháng 12): "
                    "mô hình phải biết lịch này, đặt hàng cũng phải sớm hơn.")
    with c2:
        st.markdown("#### 3. Thứ trong tuần")
        tw = thu.assign(ten=lambda f: f.thu.map(dict(enumerate(THU))))
        b = alt.Chart(tw).encode(x=alt.X("ten:N", sort=THU, title=None, axis=alt.Axis(labelAngle=0)),
                                 y=alt.Y("chi_so:Q", title="So với ngày bình thường (lần)", scale=alt.Scale(domain=[0, 1.35])))
        cot = b.mark_bar(color=BLUE, cornerRadiusEnd=4, width=26).encode(
            tooltip=[alt.Tooltip("ten:N", title="Thứ"), alt.Tooltip("chi_so:Q", title="Lần", format=".2f")])
        nhan = b.mark_text(dy=-8, color=INK2, fontSize=11).encode(text=alt.Text("chi_so:Q", format=".2f"))
        mot = alt.Chart(pd.DataFrame({"y": [1]})).mark_rule(color=MUTED, strokeDash=[4, 3]).encode(y="y:Q")
        st.altair_chart((cot + nhan + mot).properties(height=210), use_container_width=True)
        cn, cao = thu.chi_so.iloc[6], thu.loc[thu.chi_so.idxmax()]
        doc_bieu_do("1 = trung bình mọi ngày của chính mặt hàng đó.",
                    f"Chủ nhật chỉ bằng {vn(cn, 2)}, {THU[int(cao.thu)]} cao nhất ({vn(cao.chi_so, 2)}): "
                    "có thể xếp ca làm, lịch nhận và giao hàng nhiều hơn vào cuối tuần, ít hơn vào Chủ nhật.")
        st.markdown("#### 4. Khuyến mãi làm bán tăng bao nhiêu")
        h = tang.clip(-50, 249).to_frame()
        hist = alt.Chart(h).mark_bar(color=BLUE, cornerRadiusEnd=2).encode(
            x=alt.X("tang:Q", bin=alt.Bin(step=20, extent=[-60, 260]), title="Bán tăng so với ngày thường cùng tháng (%)"),
            y=alt.Y("count():Q", title="Số đợt"), tooltip=[alt.Tooltip("count():Q", title="Số đợt")])
        tv = alt.Chart(pd.DataFrame({"x": [tang.median()]})).mark_rule(color=INK, strokeWidth=2).encode(x="x:Q")
        st.altair_chart((hist + tv).properties(height=190), use_container_width=True)
        doc_bieu_do(f"mỗi cột là số đợt khuyến mãi (tổng {len(tang):,} đợt) theo mức bán tăng; vạch đen là trung vị.".replace(",", "."),
                    f"một nửa số đợt bán tăng ít nhất {vn(tang.median(), 0)}%, 1/4 số đợt tăng từ {vn(tang.quantile(0.75), 0)}% trở lên. "
                    "Kho cần biết lịch khuyến mãi trước khi đặt hàng.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 5. Phân nhóm mặt hàng ABC × XYZ")
        abcxyz["nhan"] = abcxyz.so_ma.astype(str) + " mã\n" + abcxyz.pt.map(lambda v: vn(v)) + "%"
        base = alt.Chart(abcxyz).encode(x=alt.X("xyz:N", title="XYZ: X ổn định → Z thất thường / mùa vụ", axis=alt.Axis(labelAngle=0)),
                                        y=alt.Y("abc:N", title="ABC: A giá trị cao → C thấp"))
        o = base.mark_rect(stroke=SURFACE, strokeWidth=3, cornerRadius=4).encode(
            color=alt.Color("pt:Q", scale=alt.Scale(range=["#eef4fc", BLUE]), legend=None),
            tooltip=[alt.Tooltip("abc:N", title="ABC"), alt.Tooltip("xyz:N", title="XYZ"), alt.Tooltip("so_ma:Q", title="Số mã"),
                     alt.Tooltip("pt:Q", title="% giá trị xuất", format=".1f")])
        chu = base.mark_text(lineBreak="\n", fontSize=12).encode(
            text="nhan:N", color=alt.condition(alt.datum.pt >= 30, alt.value("white"), alt.value(INK)))
        st.altair_chart((o + chu).properties(height=260), use_container_width=True)
        ax = abcxyz[(abcxyz.abc == "A") & (abcxyz.xyz == "X")].iloc[0]
        doc_bieu_do("mỗi ô: số mặt hàng và % tổng giá trị xuất kho (2 năm đầu). Màu càng đậm càng nhiều giá trị.",
                    f"{ax.so_ma} mã A-X ({vn(100 * ax.so_ma / abcxyz.so_ma.sum(), 0)}% số mã) chiếm {vn(ax.pt)}% giá trị: "
                    "bán nhiều và ổn định → nên áp dụng đặt hàng tự động cho nhóm này trước.")
    with c2:
        st.markdown("#### 6. Mô hình dự báo nào chính xác nhất")
        TEN_MH = {chon.ma_mo_hinh: "AI kết hợp (được chọn)", "lightgbm": "LightGBM (AI)", "prophet": "Prophet (AI)",
                  MOC: "Trung bình 28 ngày", "croston_sba": "Croston (hàng bán thưa)", "tsb": "TSB (hàng bán thưa)",
                  "ets": "ETS / Holt-Winters", "naive": "Lấy ngày gần nhất", "seasonal_naive_7": "Lặp lại tuần trước"}
        xh = q("SELECT ma_mo_hinh, wmape FROM v_xep_hang_mo_hinh WHERE pham_vi = 'Toan bo 121 SKU'")
        xh = xh[xh.ma_mo_hinh.isin(TEN_MH)].assign(ten=lambda f: f.ma_mo_hinh.map(TEN_MH), pt=lambda f: f.wmape * 100)
        xh["loai"] = np.where(xh.ma_mo_hinh == chon.ma_mo_hinh, "chon", np.where(xh.ma_mo_hinh == MOC, "moc", "khac"))
        base = alt.Chart(xh).encode(y=alt.Y("ten:N", sort=xh.sort_values("pt").ten.tolist(), title=None, axis=alt.Axis(labelLimit=220)),
                                    x=alt.X("pt:Q", title="WMAPE năm kiểm tra (%), thấp = tốt",
                                            scale=alt.Scale(domain=[0, xh.pt.max() * 1.15])))
        cot = base.mark_bar(height=16, cornerRadiusEnd=4).encode(
            color=alt.Color("loai:N", scale=alt.Scale(domain=["chon", "moc", "khac"], range=[BLUE, ORANGE, "#c9c8c3"]), legend=None),
            tooltip=[alt.Tooltip("ten:N", title="Mô hình"), alt.Tooltip("pt:Q", title="WMAPE (%)", format=".1f")])
        nhan = base.mark_text(align="left", dx=4, color=INK2, fontSize=11).encode(text=alt.Text("pt:Q", format=".1f"))
        st.altair_chart((cot + nhan).properties(height=260), use_container_width=True)
        w_ai, w_moc = xh.set_index("ma_mo_hinh").pt[[chon.ma_mo_hinh, MOC]]
        doc_bieu_do("WMAPE = tổng sai lệch giữa dự báo và thực tế chia tổng thực tế, tính theo ngày trên 12 tháng kiểm tra.",
                    f"AI sai {vn(w_ai)}%, cách đơn giản tốt nhất (trung bình 28 ngày) sai {vn(w_moc)}%: "
                    f"AI giảm {vn((1 - w_ai / w_moc) * 100, 0)}% sai số. Các cách thống kê cổ điển không hơn trung bình 28 ngày.")

# ------------------------------------------------------------------ KHU 1: du bao vs thuc te
with tab1:
    c1, c2, c3 = st.columns([3, 1, 1])
    nhom = c2.selectbox("Nhóm XYZ", ["Tất cả", "X", "Y", "Z"], key="k1_nhom",
                        help="X: nhu cầu ổn định · Y: dao động vừa · Z: mùa vụ / thất thường (tính trên tập train)")
    cand = sku if nhom == "Tất cả" else sku[sku.xyz_train == nhom]
    ma = c1.selectbox("Chọn SKU", cand.ma_sku, format_func=lambda m: f"{m} · {TEN_SKU[m]}", key="k1_sku")
    gop = c3.radio("Xem theo", ["Tuần", "Ngày"], horizontal=True, key="k1_gop")
    r = sku.set_index("ma_sku").loc[ma]
    st.caption(f"{r.nhom_hang} · ABC {r.abc_train} · XYZ {r.xyz_train} · loại nhu cầu {r.loai_nhu_cau} · "
               f"lead time TB {vn(r.lead_time_tb)} ngày · MOQ {r.moq} {r.don_vi}")

    d = q("""SELECT d.ma_mo_hinh, d.ngay, d.du_bao, d.thuc_te FROM du_bao d JOIN mo_hinh m USING (ma_mo_hinh)
             WHERE d.tap = 'test' AND d.ma_sku = ? AND (m.duoc_chon = 1 OR d.ma_mo_hinh = ?)""", (ma, MOC))
    w = d.pivot_table(index="ngay", columns="ma_mo_hinh", values="du_bao").rename(columns={chon.ma_mo_hinh: "ai", MOC: "moc"})
    w["thuc_te"] = d.drop_duplicates("ngay").set_index("ngay").thuc_te
    w = w.reset_index()
    w["ngay"] = pd.to_datetime(w.ngay)

    a = w.thuc_te.values
    wm_ai, bias_ai = chi_so(a, w.ai.values)
    wm_moc, _ = chi_so(a, w.moc.values)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("WMAPE dự báo AI", "–" if np.isnan(wm_ai) else vn(wm_ai, 3),
              None if np.isnan(wm_ai) else f"{vn((wm_ai / wm_moc - 1) * 100)}% so với mốc", delta_color="inverse",
              help="Tổng |thực tế − dự báo| / tổng thực tế. Càng nhỏ càng tốt.")
    m2.metric("WMAPE dự báo mốc (TB trượt 28 ngày)", "–" if np.isnan(wm_moc) else vn(wm_moc, 3))
    m3.metric("Bias dự báo AI", "–" if np.isnan(bias_ai) else f"{vn(bias_ai * 100)}%",
              help="Dương = dự báo THIẾU (dễ hết hàng); âm = dự báo thừa (dễ tồn kho dư).")
    m4.metric("Số ngày được chấm", f"{int(np.isfinite(a).sum())} / {len(a)}",
              help="Bỏ ngày kho nghỉ, ngày hết hàng (bán ra thấp hơn cầu thật), ngày đơn B2B đột biến.")

    so_moc = st.checkbox("So với dự báo mốc (TB trượt 28 ngày)", value=True, key="k1_moc")
    series = [("thuc_te", "Thực tế (nhu cầu tin được)", INK, False), ("ai", "Dự báo AI (được chọn)", BLUE, False)]
    if so_moc:
        series.append(("moc", "Dự báo mốc (TB trượt 28 ngày)", ORANGE, True))
    if gop == "Tuần":
        s = w.dropna(subset=["thuc_te"]).copy()          # chi cong ngay duoc cham, de thuc te va du bao so cung ngay
        s["ngay"] = s.ngay - pd.to_timedelta(s.ngay.dt.weekday, unit="D")
        s = s.groupby("ngay", as_index=False)[["thuc_te", "ai", "moc"]].sum()
        bieu_do_duong(s, series, f"{r.don_vi} / tuần", x_fmt="tuần từ %d/%m/%Y")
        st.caption("Theo tuần: chỉ cộng các ngày được chấm, để thực tế và dự báo so trên cùng ngày.")
    else:
        bieu_do_duong(w, series, f"{r.don_vi} / ngày")
        st.caption("Đường thực tế bị đứt ở ngày không chấm (kho nghỉ, hết hàng, đơn B2B đột biến). "
                   "Dự báo làm mới mỗi 28 ngày, chỉ dùng dữ liệu đến ngày lập dự báo.")

# ------------------------------------------------------------------ KHU 2: canh bao ton kho
with tab2:
    c1, c2 = st.columns([2, 1])
    cs2 = c1.selectbox("Chính sách đặt hàng", CS_CONG_THUC, index=CS_CONG_THUC.index(CS_GOI_Y),
                       format_func=CS_TEN.get, key="k2_cs")
    m = mo_phong(cs2)
    mo_cua = sorted(m.loc[m.rop.notna(), "ngay"].unique())          # rop = NaN: ngay kho nghi, khong xet dat hang
    d0, d1 = date.fromisoformat(mo_cua[0]), date.fromisoformat(mo_cua[-1])
    ngay = c2.date_input("Ngày xem (giả lập “hôm nay”)", value=date(2026, 2, 9), min_value=d0, max_value=d1,
                         format="DD/MM/YYYY", key="k2_ngay")
    t = ngay.isoformat()
    if t not in mo_cua:
        t = max(x for x in mo_cua if x <= t) if any(x <= t for x in mo_cua) else mo_cua[0]
        st.info(f"{ngay_vn(ngay)} kho nghỉ, hiển thị ngày làm việc gần nhất trước đó: {ngay_vn(t)}.")

    x = m[m.ngay == t].merge(sku, on="ma_sku")
    db = du_bao_chon()
    moc_t = db.loc[db.ngay == t, "moc"].iloc[0]                       # dot du bao dang dung tai ngay t
    d_tb = db[db.moc == moc_t].groupby("ma_sku").du_bao.mean() * he_so(cs2)
    x["d_tb"] = x.ma_sku.map(d_tb)
    x["du_ban"] = np.where(x.d_tb > 0, x.ton_cuoi / x.d_tb, np.nan)
    x["thu_tu"] = trang_thai_ton_kho(x).map({s: i for i, s in enumerate(TRANG_THAI)})
    x["trang_thai"] = x.thu_tu.map(dict(enumerate(f"{ic} {s}" for ic, s in zip(ICON, TRANG_THAI))))
    dem = x.thu_tu.value_counts()

    st.caption("Trang này giả lập **màn hình buổi sáng của người lập kế hoạch**: chọn một ngày trong năm kiểm tra, xem "
               "mặt hàng nào đã hết, mặt hàng nào phải đặt thêm. Số liệu lấy từ mô phỏng 12 tháng (dữ liệu mô phỏng).")
    st.markdown(f"#### Tình trạng cuối ngày {ngay_vn(t)}")
    for col, i, nhan in zip(st.columns(4), range(4), ["Hết hàng, mất bán", "Đặt hàng hôm nay",
                                                       "Tồn dưới ROP, hàng đang về", "Đủ hàng"]):
        col.metric(f"{ICON[i]} {nhan}", int(dem.get(i, 0)))

    st.markdown("#### Cả năm: mỗi ngày có bao nhiêu mặt hàng cần chú ý")
    tn = trang_thai_ca_nam(cs2).pivot(index="ngay", columns="trang_thai", values="so_sku").reindex(
        columns=TRANG_THAI[:3]).fillna(0)
    tn = tn.reindex(sorted(mo_cua)).fillna(0)
    tl = tn.reset_index().melt(id_vars="ngay", var_name="trang_thai", value_name="so_sku")
    tl["ngay"] = pd.to_datetime(tl.ngay)
    tl["thu_tu"] = tl.trang_thai.map({s: i for i, s in enumerate(TRANG_THAI)})
    near = alt.selection_point(nearest=True, on="pointerover", fields=["ngay"], empty=False, clear="pointerout")
    vung = alt.Chart(tl).mark_area(opacity=0.9).encode(
        x=alt.X("ngay:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False)),
        y=alt.Y("so_sku:Q", stack="zero", title="Số mặt hàng"),
        color=alt.Color("trang_thai:N", scale=alt.Scale(domain=TRANG_THAI[:3], range=MAU_TT), title=None,
                        legend=alt.Legend(orient="top")),
        order=alt.Order("thu_tu:Q", sort="ascending"))
    tw = tn.reset_index().rename(columns=dict(zip(TRANG_THAI[:3], ["het", "dat", "duoi"])))
    tw["ngay"] = pd.to_datetime(tw.ngay)
    re = alt.Chart(tw).mark_rule(color=INK2).encode(
        x="ngay:T", opacity=alt.condition(near, alt.value(0.7), alt.value(0)),
        tooltip=[alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("het:Q", title="Hết hàng"),
                 alt.Tooltip("dat:Q", title="Đặt hàng hôm nay"), alt.Tooltip("duoi:Q", title="Dưới ROP, hàng đang về")]
    ).add_params(near)
    hom_nay = alt.Chart(pd.DataFrame({"ngay": [pd.Timestamp(t)]})).mark_rule(color=INK, strokeWidth=1.5, strokeDash=[2, 2]).encode(x="ngay:T")
    st.altair_chart(alt.layer(vung, re, hom_nay).properties(height=230), use_container_width=True)
    dn_het = tn[TRANG_THAI[0]]
    sau = dn_het[dn_het.index >= (pd.Timestamp(mo_cua[0]) + pd.Timedelta(days=28)).strftime("%Y-%m-%d")]
    dau_ky = (f"; nhiều nhất là {ngay_vn(dn_het.idxmax())} ({int(dn_het.max())} mã), rơi vào 4 tuần đầu vì tồn kho ban đầu "
              "lấy từ dữ liệu, chưa theo chính sách mới" if dn_het.idxmax() not in sau.index else "")
    doc_bieu_do("chiều cao mỗi màu = số mặt hàng ở trạng thái đó trong ngày; đường chấm đen là ngày đang xem. "
                "Rê chuột để xem từng ngày.",
                f"trung bình mỗi ngày {vn(tn[TRANG_THAI[1]].mean())} mặt hàng cần đặt và {vn(dn_het.mean())} mặt hàng hết hàng"
                f"{dau_ky}. Sau 4 tuần đầu, ngày nhiều mặt hàng hết nhất là {ngay_vn(sau.idxmax())} ({int(sau.max())} mã).")

    canh_bao = x[x.thu_tu < 3].sort_values(["thu_tu", "du_ban"])
    st.markdown(f"#### Danh sách mặt hàng cần chú ý ngày {ngay_vn(t)}")
    vd = []
    for i in range(3):                                   # moi trang thai 1 cau vi du bang loi
        r_ = canh_bao[canh_bao.thu_tu == i].head(1)
        if r_.empty:
            continue
        r_ = r_.iloc[0]
        dv, ten = r_.don_vi, f"**{r_.ten_sku}** ({r_.ma_sku})"
        if i == 0:
            vd.append(f"{ICON[0]} {ten}: kho hết sạch; hôm nay khách cần {vn(r_.nhu_cau, 0)} {dv} nhưng chỉ giao được "
                      f"{vn(r_.xuat, 0)}. Đang có {vn(r_.dang_ve, 0)} {dv} trên đường về.")
        elif i == 1:
            truoc = r_.ton_cuoi + r_.dang_ve - r_.dat_hang
            vd.append(f"{ICON[1]} {ten}: còn {vn(r_.ton_cuoi, 0)} {dv} trong kho + {vn(r_.dang_ve - r_.dat_hang, 0)} đang về "
                      f"= {vn(truoc, 0)}, không vượt điểm đặt hàng (ROP) {vn(r_.rop, 0)} → đặt thêm {vn(r_.dat_hang, 0)} {dv}.")
        else:
            vd.append(f"{ICON[2]} {ten}: còn {vn(r_.ton_cuoi, 0)} {dv}, thấp hơn ROP {vn(r_.rop, 0)}, nhưng đang có "
                      f"{vn(r_.dang_ve, 0)} {dv} trên đường về → tổng đã vượt ROP nên **chưa cần đặt**, chỉ theo dõi.")
    if vd:
        st.markdown("**Đọc bảng bằng ví dụ:**\n\n" + "\n".join(f"- {v}" for v in vd))
    st.dataframe(
        canh_bao[["trang_thai", "ma_sku", "ten_sku", "ton_cuoi", "dang_ve", "rop", "dat_hang", "du_ban", "lead_time_tb", "don_vi"]],
        hide_index=True, use_container_width=True, height=320,
        column_config={
            "trang_thai": st.column_config.TextColumn("Trạng thái", width="medium"),
            "ma_sku": st.column_config.TextColumn("Mã", width="small"),
            "ten_sku": st.column_config.TextColumn("Tên hàng", width="medium"),
            "ton_cuoi": st.column_config.NumberColumn("Trong kho", format="%.0f"),
            "dang_ve": st.column_config.NumberColumn("Đang về", format="%.0f"),
            "rop": st.column_config.NumberColumn("ROP", format="%.0f", help="Điểm đặt hàng"),
            "dat_hang": st.column_config.NumberColumn("Đặt hôm nay", format="%.0f"),
            "du_ban": st.column_config.NumberColumn("Đủ bán (ngày)", format="%.1f"),
            "lead_time_tb": st.column_config.NumberColumn("Chờ hàng (ngày)", format="%.0f"),
            "don_vi": st.column_config.TextColumn("Đơn vị", width="small")})
    if canh_bao.empty:
        st.success("Không có mặt hàng nào cần chú ý trong ngày này.")
    with st.expander("Giải thích các cột"):
        st.markdown(
            "- **Trong kho:** số lượng thực có trong kho cuối ngày.\n"
            "- **Đang về:** hàng đã đặt nhà cung cấp nhưng chưa nhận (tính cả đơn đặt hôm nay).\n"
            "- **ROP (điểm đặt hàng):** = nhu cầu dự báo trong thời gian chờ hàng + tồn kho an toàn. "
            "Quy tắc: nếu *trong kho + đang về* (chưa tính đơn hôm nay) ≤ ROP thì đặt thêm.\n"
            "- **Đặt hôm nay:** lượng hệ thống đề xuất đặt (bội số của lượng đặt kinh tế EOQ, tối thiểu MOQ).\n"
            "- **Đủ bán (ngày):** trong kho ÷ nhu cầu dự báo 1 ngày. Nhỏ hơn *Chờ hàng* thì có nguy cơ hết "
            "trước khi hàng mới về (nếu không có hàng đang về).\n"
            "- **Chờ hàng (ngày):** thời gian giao hàng trung bình của nhà cung cấp (lead time).")

    st.markdown("#### Diễn biến tồn kho 12 tháng của 1 SKU")
    c1, c2 = st.columns([3, 1])
    mac_dinh = canh_bao.ma_sku.iloc[0] if len(canh_bao) else "SKU001"
    ma2 = c1.selectbox("SKU", sku.ma_sku, index=int(np.flatnonzero(sku.ma_sku == mac_dinh)[0]),
                       format_func=lambda s: f"{s} · {TEN_SKU[s]}", key=f"k2_sku_{t}_{cs2}")
    so_ht = c2.checkbox("So với hiện trạng*", value=False, key="k2_ht")
    y = m[m.ma_sku == ma2][["ngay", "ton_cuoi", "rop"]].copy()
    series = [("ton_cuoi", f"Tồn cuối ngày: {CS_TEN[cs2]}", CS_MAU[cs2], False), ("rop", "ROP (điểm đặt hàng)", INK2, True)]
    if so_ht:
        ht = mo_phong("hien_trang")
        y["ton_ht"] = ht[ht.ma_sku == ma2].set_index("ngay").ton_cuoi.reindex(y.ngay).values
        series.append(("ton_ht", "Tồn cuối ngày: hiện trạng*", MUTED, False))
    y["ngay"] = pd.to_datetime(y.ngay)
    y["rop"] = y.rop.ffill()                                         # ngay kho nghi giu ROP ngay truoc
    bieu_do_duong(y, series, f"{sku.set_index('ma_sku').don_vi[ma2]}", ngay_chon=t)
    kq = q("""SELECT ma_chinh_sach, 100.0 * da_dap_ung / nhu_cau AS fr, so_ngay_thieu, ton_tb FROM ket_qua_ton_kho
              WHERE ma_sku = ? AND ROUND(muc_phuc_vu, 2) = ?""", (ma2, MAIN)).set_index("ma_chinh_sach")
    st.caption(f"Cả năm test, {CS_TEN[cs2]}: Fill Rate {vn(kq.fr[cs2])}%, {kq.so_ngay_thieu[cs2]} ngày thiếu hàng, "
               f"tồn bình quân {vn(kq.ton_tb[cs2], 0)}. Hiện trạng*: Fill Rate {vn(kq.fr['hien_trang'])}%, "
               f"{kq.so_ngay_thieu['hien_trang']} ngày thiếu, tồn bình quân {vn(kq.ton_tb['hien_trang'], 0)}. "
               "Đường đứt đoạn dọc: ngày đang xem.")
    st.caption(NOTE_HT)

# ------------------------------------------------------------------ KHU 3: KPI truoc - sau
with tab3:
    lv = st.radio("Mức phục vụ mục tiêu (z trong công thức SS)", [0.90, 0.95, 0.99], index=1, horizontal=True,
                  format_func=lambda v: f"{v:.0%}", key="k3_lv")
    v = q("SELECT * FROM v_so_sanh_chinh_sach WHERE ROUND(muc_phuc_vu, 2) = ?", (lv,)).set_index("ma_chinh_sach")
    v = v.loc[list(CS_TEN)]
    g, b, h = v.loc[CS_GOI_Y], v.loc["cong_thuc_du_bao_moc"], v.loc["hien_trang"]
    pct = lambda new, old: f"{vn((new / old - 1) * 100)}%"
    st.markdown(f"#### {CS_TEN[CS_GOI_Y]}, so với dự báo mốc (cùng công thức)")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fill Rate", f"{vn(g.fill_rate_pt, 2)}%", f"{vn(g.fill_rate_pt - b.fill_rate_pt, 2)} điểm %",
              help="Tỷ lệ nhu cầu được đáp ứng ngay từ kho")
    k2.metric("Số ngày-SKU thiếu hàng", f"{int(g.so_ngay_sku_thieu):,}".replace(",", "."),
              pct(g.so_ngay_sku_thieu, b.so_ngay_sku_thieu), delta_color="inverse")
    k3.metric("Giá trị tồn kho bình quân", f"{vn(g.ton_tb_trieu_vnd / 1000, 2)} tỷ đ",
              pct(g.ton_tb_trieu_vnd, b.ton_tb_trieu_vnd), delta_color="inverse")
    k4.metric("Chi phí liên quan", f"{vn(g.chi_phi_lien_quan_trieu / 1000, 2)} tỷ đ",
              pct(g.chi_phi_lien_quan_trieu, b.chi_phi_lien_quan_trieu), delta_color="inverse",
              help="Chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do hết hàng")
    st.caption(f"So với hiện trạng\\*: Fill Rate {vn(g.fill_rate_pt - h.fill_rate_pt, 2)} điểm %, ngày thiếu "
               f"{pct(g.so_ngay_sku_thieu, h.so_ngay_sku_thieu)}, tồn kho {pct(g.ton_tb_trieu_vnd, h.ton_tb_trieu_vnd)}, "
               f"chi phí liên quan {pct(g.chi_phi_lien_quan_trieu, h.chi_phi_lien_quan_trieu)}.")

    kpi = [("fill_rate_pt", "Fill Rate (%)", ".2f"), ("so_ngay_sku_thieu", "Số ngày-SKU thiếu hàng", ".0f"),
           ("ton_tb_trieu_vnd", "Tồn kho bình quân (triệu đ)", ".0f"),
           ("chi_phi_lien_quan_trieu", "Chi phí liên quan (triệu đ)", ".0f")]
    bars = v.reset_index().assign(ten=lambda f: f.ma_chinh_sach.map(CS_TEN))
    cols = st.columns(2)
    for i, (cot, ten, fmt) in enumerate(kpi):          # 4 bieu do nho, moi chi so 1 truc rieng (khong 2 truc y)
        base = alt.Chart(bars).encode(
            y=alt.Y("ten:N", sort=list(CS_TEN.values()), title=None, axis=alt.Axis(labelLimit=260)),
            x=alt.X(f"{cot}:Q", title=None, axis=alt.Axis(format="d"),
                    scale=alt.Scale(domain=[0, bars[cot].max() * 1.15])),   # chua cho nhan so o cuoi thanh
            tooltip=[alt.Tooltip("ten:N", title="Chính sách"), alt.Tooltip(f"{cot}:Q", title=ten, format=fmt)])
        bar = base.mark_bar(height=22, cornerRadiusEnd=4).encode(
            color=alt.Color("ma_chinh_sach:N", scale=alt.Scale(domain=list(CS_MAU), range=list(CS_MAU.values())),
                            legend=None))
        txt = base.mark_text(align="left", dx=4, color=INK2).encode(text=alt.Text(f"{cot}:Q", format=fmt))
        with cols[i % 2]:
            st.markdown(f"**{ten}**")
            st.altair_chart((bar + txt).properties(height=150), use_container_width=True)

    st.markdown("#### Bảng trước – sau toàn kho")
    bang = v.reset_index().assign(ma_chinh_sach=lambda f: f.ma_chinh_sach.map(CS_TEN)).drop(columns=["mo_ta", "muc_phuc_vu"])
    st.dataframe(bang, hide_index=True, use_container_width=True, column_config={
        "ma_chinh_sach": "Chính sách", "fill_rate_pt": st.column_config.NumberColumn("Fill Rate (%)", format="%.2f"),
        "so_ngay_sku_thieu": "Ngày-SKU thiếu", "ton_tb_trieu_vnd": "Tồn TB (tr đ)", "so_lan_nhap": "Số lần nhập",
        "chi_phi_dat_trieu": "CP đặt hàng (tr đ)", "chi_phi_luu_trieu": "CP lưu kho (tr đ)",
        "tong_chi_phi_trieu": "CP đặt + lưu (tr đ)", "doanh_thu_mat_trieu": "Doanh thu mất (tr đ)",
        "loi_nhuan_mat_trieu": "Lợi nhuận mất (tr đ)", "chi_phi_lien_quan_trieu": "CP liên quan (tr đ)"})

    st.markdown("#### Theo nhóm XYZ")
    xyz = q("""SELECT p.xyz_train, k.ma_chinh_sach, 100.0 * SUM(k.da_dap_ung) / SUM(k.nhu_cau) AS fr,
                      SUM(k.so_ngay_thieu) AS thieu, SUM(k.gia_tri_ton_tb) / 1e6 AS ton, SUM(k.loi_nhuan_mat) / 1e6 AS lnm
               FROM ket_qua_ton_kho k JOIN phan_loai_sku p USING (ma_sku)
               WHERE ROUND(k.muc_phuc_vu, 2) = ? GROUP BY p.xyz_train, k.ma_chinh_sach""", (lv,))
    xyz["thu_tu"] = xyz.ma_chinh_sach.map({c: i for i, c in enumerate(CS_TEN)})
    xyz = xyz.sort_values(["xyz_train", "thu_tu"]).assign(ma_chinh_sach=lambda f: f.ma_chinh_sach.map(CS_TEN))
    st.dataframe(xyz.drop(columns="thu_tu"), hide_index=True, use_container_width=True, column_config={
        "xyz_train": "Nhóm", "ma_chinh_sach": "Chính sách", "fr": st.column_config.NumberColumn("Fill Rate (%)", format="%.1f"),
        "thieu": "Ngày-SKU thiếu", "ton": st.column_config.NumberColumn("Tồn TB (tr đ)", format="%.0f"),
        "lnm": st.column_config.NumberColumn("Lợi nhuận mất (tr đ)", format="%.0f")})
    st.caption(f"12 tháng test, 121 SKU. {NOTE} Hiện trạng giống nhau ở mọi mức phục vụ (đo từ dữ liệu, không dùng công thức).")
    st.caption(NOTE_HT)

    st.markdown("#### Thử độ nhạy: nếu hàng về trễ hoặc chi phí tăng (mức phục vụ 95%)")
    try:
        dn = q("SELECT * FROM v_do_nhay")
    except Exception:
        dn = pd.DataFrame()
    if dn.empty:
        st.info("Chưa có kết quả thử độ nhạy. Chạy `python src/do_nhay.py` rồi bấm “Tải lại dữ liệu từ CSDL”.")
    else:
        KB = {"tac_cang_3": "Tắc cảng 3 tuần, hàng về trễ +3 ngày (TB 13 đợt)",
              "tac_cang_5": "Tắc cảng 3 tuần, hàng về trễ +5 ngày (TB 13 đợt)",
              "tac_cang_7": "Tắc cảng 3 tuần, hàng về trễ +7 ngày (TB 13 đợt)",
              "lead_time_2": "Lead time +2 ngày cả năm, công thức KHÔNG cập nhật",
              "lead_time_2_cap_nhat": "Lead time +2 ngày cả năm, công thức CÓ cập nhật",
              "chi_phi_dat_120": "Chi phí đặt hàng +20% (cước tăng)", "chi_phi_luu_115": "Chi phí lưu kho +15% (giá điện)"}
        kb = st.selectbox("Kịch bản", list(KB), format_func=KB.get, key="k3_kb")
        dn["nhom_kb"] = np.where(dn.nhom == "tac_cang", "tac_cang_" + dn.tham_so.fillna(0).astype(int).astype(str), dn.ma_kich_ban)
        cot = ["fill_rate_pt", "so_ngay_sku_thieu", "ton_tb_trieu_vnd", "chi_phi_lien_quan_trieu"]
        goc = dn[dn.ma_kich_ban == "goc"].set_index("ma_chinh_sach")[cot]
        x = dn[dn.nhom_kb == kb].groupby("ma_chinh_sach")[cot].mean()       # tac cang: trung binh 13 dot
        x = x.join(goc, rsuffix="_goc").reindex([c for c in CS_TEN if c in x.index])
        x["d_fr"] = x.fill_rate_pt - x.fill_rate_pt_goc
        x["d_cp"] = 100 * (x.chi_phi_lien_quan_trieu / x.chi_phi_lien_quan_trieu_goc - 1)
        x = x.reset_index().assign(ma_chinh_sach=lambda f: f.ma_chinh_sach.map(CS_TEN))
        st.dataframe(x[["ma_chinh_sach", "fill_rate_pt", "d_fr", "so_ngay_sku_thieu", "ton_tb_trieu_vnd",
                        "chi_phi_lien_quan_trieu", "d_cp"]], hide_index=True, use_container_width=True, column_config={
            "ma_chinh_sach": "Chính sách", "fill_rate_pt": st.column_config.NumberColumn("Fill Rate (%)", format="%.2f"),
            "d_fr": st.column_config.NumberColumn("Đổi Fill Rate (điểm %)", format="%+.2f"),
            "so_ngay_sku_thieu": st.column_config.NumberColumn("Ngày-SKU thiếu", format="%.0f"),
            "ton_tb_trieu_vnd": st.column_config.NumberColumn("Tồn TB (tr đ)", format="%.0f"),
            "chi_phi_lien_quan_trieu": st.column_config.NumberColumn("CP liên quan (tr đ)", format="%.0f"),
            "d_cp": st.column_config.NumberColumn("Đổi CP liên quan (%)", format="%+.1f")})
        st.caption("So với kịch bản bình thường (kết quả ở trên). Người lập kế hoạch không biết trước đợt tắc cảng. "
                   "Hiện trạng\\* chỉ so được khi đổi chi phí: đơn hàng của nó lấy từ dữ liệu, không chạy lại được khi lead time đổi. "
                   "Chi tiết: `reports/do_nhay.md`.")

# ------------------------------------------------------------------ KHU 4: bang SS / ROP / EOQ
with tab4:
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    cs4 = c1.selectbox("Chính sách", CS_CONG_THUC, index=CS_CONG_THUC.index(CS_GOI_Y), format_func=CS_TEN.get, key="k4_cs")
    lv4 = c2.selectbox("Mức phục vụ", [0.90, 0.95, 0.99], index=1, format_func=lambda v: f"{v:.0%}", key="k4_lv")
    abc = c3.multiselect("ABC", ["A", "B", "C"], placeholder="Tất cả", key="k4_abc")
    xyz4 = c4.multiselect("XYZ", ["X", "Y", "Z"], placeholder="Tất cả", key="k4_xyz")
    tim = st.text_input("Tìm theo mã hoặc tên hàng", key="k4_tim")
    p = q("""SELECT t.ma_sku, s.ten_sku, p.abc_train, p.xyz_train, k.nhu_cau / 364.0 AS ban_ngay, t.ss_tb, t.rop_tb, t.eoq_tb,
                    s.moq, s.don_vi, 100.0 * k.da_dap_ung / k.nhu_cau AS fill_rate,
                    s.lead_time_tb, t.sigma_ltd, t.he_so_hieu_chinh, k.so_ngay_thieu, k.ton_tb, k.so_lan_nhap, s.nhom_hang, s.gia_von
             FROM tham_so_ton_kho t
             JOIN dm_sku s USING (ma_sku) JOIN phan_loai_sku p USING (ma_sku)
             JOIN ket_qua_ton_kho k ON k.ma_chinh_sach = t.ma_chinh_sach AND k.muc_phuc_vu = t.muc_phuc_vu AND k.ma_sku = t.ma_sku
             WHERE t.ma_chinh_sach = ? AND ROUND(t.muc_phuc_vu, 2) = ? ORDER BY t.ma_sku""", (cs4, lv4))
    p["ss_ngay"] = p.ss_tb / p.ban_ngay
    if abc:
        p = p[p.abc_train.isin(abc)]
    if xyz4:
        p = p[p.xyz_train.isin(xyz4)]
    if tim:
        p = p[p.ma_sku.str.contains(tim, case=False) | p.ten_sku.str.contains(tim, case=False)]
    if p.empty:
        st.warning("Không có mặt hàng nào khớp bộ lọc.")
        st.stop()
    st.caption(f"{len(p)} mặt hàng. Ba con số quyết định đặt hàng của mỗi mặt hàng: **tồn kho an toàn (SS)** = hàng dự phòng, "
               "**điểm đặt hàng (ROP)** = mức tồn để bắt đầu đặt, **lượng đặt kinh tế (EOQ)** = mỗi lần đặt bao nhiêu. "
               "Chúng được tính lại mỗi ngày theo dự báo; bảng ghi giá trị **bình quân** trong 12 tháng kiểm tra. Dữ liệu mô phỏng.")

    ma4 = st.selectbox("Giải thích bằng lời cho mặt hàng", p.ma_sku, format_func=lambda s: f"{s} · {TEN_SKU[s]}", key="k4_vd")
    r4 = p.set_index("ma_sku").loc[ma4]
    st.info(f"**{r4.ten_sku}** bán trung bình **{vn(r4.ban_ngay, 0)} {r4.don_vi}/ngày**, nhà cung cấp giao sau khoảng "
            f"**{vn(r4.lead_time_tb, 0)} ngày**.\n\n"
            f"- Giữ **{vn(r4.ss_tb, 0)} {r4.don_vi} dự phòng** (SS), đủ bán khoảng {vn(r4.ss_ngay)} ngày nếu dự báo sai hoặc hàng về trễ.\n"
            f"- Khi *còn trong kho + đang về* xuống tới **{vn(r4.rop_tb, 0)} {r4.don_vi}** (ROP) thì đặt hàng: "
            f"= lượng bán dự báo trong {vn(r4.lead_time_tb, 0)} ngày chờ + phần dự phòng.\n"
            f"- Mỗi lần đặt khoảng **{vn(r4.eoq_tb, 0)} {r4.don_vi}** (EOQ, cân bằng chi phí đặt hàng và lưu kho), "
            f"không dưới {vn(r4.moq, 0)} (MOQ, nhà cung cấp quy định).\n"
            f"- Kết quả cả năm mô phỏng: đáp ứng **{vn(r4.fill_rate)}%** nhu cầu, {int(r4.so_ngay_thieu)} ngày thiếu, "
            f"nhập {int(r4.so_lan_nhap)} lần.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Tiền nằm trong hàng dự phòng (SS), theo nhóm**")
        p["tien_ss"] = p.ss_tb * p.gia_von / 1e6
        nh = p.groupby(["abc_train", "xyz_train"]).agg(tien=("tien_ss", "sum"), so_ma=("ma_sku", "size")).reset_index()
        nh["nhom"] = nh.abc_train + "-" + nh.xyz_train
        base = alt.Chart(nh).encode(y=alt.Y("nhom:N", sort="-x", title=None, axis=alt.Axis(labelOverlap=False)),
                                    x=alt.X("tien:Q", title="Triệu đồng (theo giá vốn)", scale=alt.Scale(domain=[0, nh.tien.max() * 1.18])))
        cot = base.mark_bar(color=BLUE, height=16, cornerRadiusEnd=4).encode(
            tooltip=[alt.Tooltip("nhom:N", title="Nhóm"), alt.Tooltip("so_ma:Q", title="Số mã"),
                     alt.Tooltip("tien:Q", title="Triệu đồng", format=",.0f")])
        nhan = base.mark_text(align="left", dx=4, color=INK2, fontSize=11).encode(text=alt.Text("tien:Q", format=".0f"))
        st.altair_chart((cot + nhan).properties(height=270), use_container_width=True)
        z = nh[nh.xyz_train == "Z"]
        doc_bieu_do("chữ đầu là ABC (giá trị), chữ sau là XYZ (độ ổn định). Cột dài = nhiều vốn nằm trong hàng dự phòng.",
                    f"nhóm Z (khó dự báo) giữ {vn(100 * z.tien.sum() / nh.tien.sum(), 0)}% tiền dự phòng với "
                    f"{z.so_ma.sum()}/{nh.so_ma.sum()} mã: hàng càng khó đoán càng cần nhiều hàng dự phòng.")
    with c2:
        st.markdown("**Mức đáp ứng (Fill Rate) của từng mặt hàng**")
        pf = p.assign(ten=p.ma_sku + " · " + p.ten_sku)
        diem = alt.Chart(pf).mark_circle(size=70, opacity=0.75, color=BLUE, stroke=SURFACE, strokeWidth=1).encode(
            x=alt.X("fill_rate:Q", title="Fill Rate cả năm (%)", scale=alt.Scale(domain=[max(0, pf.fill_rate.min() - 3), 101], nice=False)),
            y=alt.Y("xyz_train:N", title=None, sort=["X", "Y", "Z"]),
            yOffset=alt.YOffset("jitter:Q"),
            tooltip=[alt.Tooltip("ten:N", title="Mặt hàng"), alt.Tooltip("fill_rate:Q", title="Fill Rate (%)", format=".1f")]
        ).transform_calculate(jitter="random()")
        muc = alt.Chart(pd.DataFrame({"x": [lv4 * 100]})).mark_rule(color=INK, strokeDash=[4, 3]).encode(x="x:Q")
        st.altair_chart((diem + muc).properties(height=270), use_container_width=True)
        thap, duoi = pf.nsmallest(3, "fill_rate"), pf[pf.fill_rate < lv4 * 100]
        doc_bieu_do(f"mỗi chấm là 1 mặt hàng; vạch đứt là mức phục vụ mục tiêu {lv4:.0%}. Rê chuột để xem tên.",
                    f"{len(duoi)}/{len(pf)} mã dưới mục tiêu, trong đó {int((duoi.xyz_train == 'Z').sum())} mã nhóm Z "
                    "(mùa vụ / thất thường). Thấp nhất: " + "; ".join(f"{r.ten_sku} {vn(r.fill_rate)}%" for r in thap.itertuples())
                    + ".")

    chi_tiet = st.toggle("Hiện thêm cột kỹ thuật (lead time, sai số dự báo, hệ số hiệu chỉnh, tồn, số lần nhập)", key="k4_ky_thuat")
    cot_hien = ["ma_sku", "ten_sku", "abc_train", "xyz_train", "ban_ngay", "ss_tb", "ss_ngay", "rop_tb", "eoq_tb", "moq",
                "don_vi", "fill_rate"]
    if chi_tiet:
        cot_hien += ["lead_time_tb", "sigma_ltd", "he_so_hieu_chinh", "so_ngay_thieu", "ton_tb", "so_lan_nhap", "nhom_hang"]
    so = lambda nhan, fmt="%.0f", **k: st.column_config.NumberColumn(nhan, format=fmt, **k)
    st.dataframe(p[cot_hien], hide_index=True, use_container_width=True, height=420, column_config={
        "ma_sku": st.column_config.TextColumn("Mã", width="small"), "ten_sku": st.column_config.TextColumn("Tên hàng", width="medium"),
        "nhom_hang": "Nhóm hàng", "abc_train": st.column_config.TextColumn("ABC", width="small"),
        "xyz_train": st.column_config.TextColumn("XYZ", width="small"),
        "ban_ngay": so("Bán/ngày"), "ss_tb": so("SS", help="Tồn kho an toàn: hàng dự phòng"),
        "ss_ngay": so("SS đủ (ngày)", "%.1f", help="Hàng dự phòng đủ bán bao nhiêu ngày"),
        "rop_tb": so("ROP", help="Điểm đặt hàng: trong kho + đang về xuống tới mức này thì đặt"),
        "eoq_tb": so("EOQ", help="Lượng đặt kinh tế: mỗi lần đặt bao nhiêu"),
        "moq": so("MOQ", help="Lượng đặt tối thiểu nhà cung cấp quy định"),
        "don_vi": st.column_config.TextColumn("Đơn vị", width="small"),
        "fill_rate": so("Đáp ứng (%)", "%.1f", help="Fill Rate cả năm mô phỏng"),
        "lead_time_tb": st.column_config.NumberColumn("Chờ hàng TB (ngày)", format="%.1f"),
        "he_so_hieu_chinh": st.column_config.NumberColumn("Hệ số hiệu chỉnh", format="%.3f",
                                                          help="Nhân với dự báo để bù lệch có hệ thống (ước lượng trên validation)"),
        "sigma_ltd": st.column_config.NumberColumn("Sai số dự báo trong thời gian chờ (σ)", format="%.0f"),
        "so_ngay_thieu": "Ngày thiếu", "ton_tb": st.column_config.NumberColumn("Tồn TB", format="%.0f"),
        "so_lan_nhap": "Số lần nhập"})
    st.download_button("⬇ Tải bảng (CSV, mở được bằng Excel)", p.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"tham_so_ton_kho_{cs4}_{int(lv4 * 100)}.csv", mime="text/csv")
    with st.expander("Công thức dùng trong bảng"):
        st.markdown(
            "- **SS** (tồn kho an toàn) = z × √(σ_LTD² + d² × σ_LT²): z theo mức phục vụ (90% → 1,28; 95% → 1,64; "
            "99% → 2,33); σ_LTD = độ lệch chuẩn tổng sai số dự báo trong lead time (đo trên validation); "
            "d = nhu cầu dự báo bình quân/ngày; σ_LT = độ lệch chuẩn lead time.\n"
            "- **ROP** (điểm đặt hàng) = nhu cầu dự báo trong lead time + SS. Khi tồn kho + hàng đang về ≤ ROP thì đặt hàng.\n"
            "- **EOQ** (lượng đặt kinh tế) = √(2 × D × S / H): D = nhu cầu năm, S = chi phí 1 lần đặt, "
            "H = chi phí lưu kho 1 đơn vị/năm. Lượng đặt thực tế = bội số của max(EOQ, MOQ).")
