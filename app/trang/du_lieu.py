"""Man Du lieu & phuong phap (cho hoi dong): du lieu la gi, cai gi that / gia dinh, luong xu ly, cac bieu do phan tich
(mua vu, thu trong tuan, khuyen mai, ABC x XYZ), mo hinh nao chinh xac nhat, cong thuc SS / ROP / EOQ."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import chung as C
from chung import ngay_vn, vn

THU = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


@st.cache_data(show_spinner="Đang tính số liệu tổng quan…")
def tong_quan():
    """Tinh tu giao_dich_sach. Mua vu, thu trong tuan, khuyen mai chi dung ngay kho mo cua va khong het hang (ngay het hang
    ban ra thap hon cau that). Chi so = luong ban TB trong nhom ngay / luong ban TB moi ngay cua chinh SKU do (1 = binh
    thuong), roi lay trung binh cac SKU -> SKU ban nhieu khong lan at SKU ban it."""
    g = C.q("""SELECT g.ngay, g.ma_sku, g.qty_out, g.het_hang, g.la_ngay_nghi, s.gia_von, s.nhom_hang
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
    km = C.q("SELECT ma_sku, tu_ngay, den_ngay FROM lich_khuyen_mai").reset_index(names="dot_km")
    km["d"] = [pd.date_range(a, b) for a, b in zip(km.tu_ngay, km.den_ngay)]
    kd = km.explode("d")[["dot_km", "ma_sku", "d"]]
    kd["d"] = pd.to_datetime(kd.d)
    x = ok.merge(kd, on=["ma_sku", "d"], how="left")
    nen = x[x.dot_km.isna()].groupby(["ma_sku", "ym"]).qty_out.mean().rename("nen")
    dot = (x[x.dot_km.notna()].groupby("dot_km").agg(ma_sku=("ma_sku", "first"), ym=("ym", "first"), q=("qty_out", "mean"))
           .join(nen, on=["ma_sku", "ym"]))
    tang = (100 * (dot.q / dot.nen - 1)).dropna().rename("tang").reset_index(drop=True)
    gt_train = (g[g.ngay <= "2025-09-30"].assign(gt=lambda f: f.qty_out * f.gia_von).groupby("ma_sku").gt.sum())
    p = C.q("SELECT ma_sku, abc_train AS abc, xyz_train AS xyz FROM phan_loai_sku").assign(gia_tri=lambda f: f.ma_sku.map(gt_train))
    abcxyz = p.groupby(["abc", "xyz"]).agg(so_ma=("ma_sku", "size"), gia_tri=("gia_tri", "sum")).reset_index()
    abcxyz["pt"] = 100 * abcxyz.gia_tri / abcxyz.gia_tri.sum()
    return tuan, nam.values, thu, mua, tang, abcxyz


n = C.q("""SELECT (SELECT COUNT(*) FROM dm_sku) AS sku, (SELECT COUNT(DISTINCT nhom_hang) FROM dm_sku) AS nhom,
                  (SELECT COUNT(*) FROM giao_dich_sach) AS dong, (SELECT COUNT(DISTINCT ngay) FROM giao_dich_sach) AS ngay,
                  (SELECT MIN(ngay) FROM giao_dich_sach) AS tu, (SELECT MAX(ngay) FROM giao_dich_sach) AS den,
                  (SELECT COUNT(*) FROM giao_dich_tho) AS tho, (SELECT COUNT(*) FROM nhat_ky_sua_loi) AS sua,
                  (SELECT AVG(het_hang) FROM giao_dich_sach WHERE la_ngay_nghi = 0) AS het""").iloc[0]
cm = C.mo_hinh_chon()

C.muc("Dữ liệu này là gì", "đọc trước khi xem kết quả", dau_tien=True)
C.o_hang([("Mặt hàng", f"{int(n.sku)}", f"{n.nhom} nhóm hàng", False),
          ("Số ngày", f"{n.ngay:,}".replace(",", "."), f"{ngay_vn(n.tu)} – {ngay_vn(n.den)}", False),
          ("Dòng nhập – xuất – tồn", f"{n.dong:,}".replace(",", "."), "mỗi mã × mỗi ngày 1 dòng", False),
          ("Dòng lỗi đã sửa", f"{int(n.sua)}", f"từ {n.tho:,} dòng thô".replace(",", "."), False)])
st.write("")
a, b = st.columns([1.15, 1], gap="large")
a.markdown(
    '<div class="dao-mau"><b>Đây là dữ liệu mô phỏng</b> (máy sinh ra theo quy tắc), vì chưa có dữ liệu từ kho thật. Tên hàng là '
    'sản phẩm phổ biến trên thị trường nhưng <b>mọi con số không phải của hãng hay của kho nào</b>. Mục tiêu là xây <b>quy trình</b> '
    'dự báo và đặt hàng rồi so sánh các cách làm trên cùng dữ liệu; có file xuất – nhập – tồn của kho thật (cùng tên cột) thì '
    'chạy lại toàn bộ là ra kết quả thật.</div>', unsafe_allow_html=True)
b.markdown(
    f"- **Lấy từ nguồn thật:** ngày các cơn bão (Yagi 07/09/2024, các bão năm 2025), lễ Tết, Trung thu, lịch sale 11.11 / 12.12 "
    f"/ Black Friday; giá bán lẻ 37 mã tra ngày 24/10/2026.\n"
    f"- **Giả định:** lượng bán từng ngày, mức tăng do lễ, bão, khuyến mãi; giá vốn, chi phí đặt hàng, lưu kho; thời gian giao "
    f"hàng; lỗi cài sẵn trong dữ liệu thô; {vn(n.het * 100)}% ngày-mặt hàng hết hàng.")

C.muc("Hệ thống chạy thế nào", "mỗi bước là một script chạy lại được trong src/")
buoc = [("Ghi nhận", "nhập – xuất – tồn hằng ngày", "lam_sach.py"), ("Đặc trưng", "lịch lễ, mùa, khuyến mãi, trễ", "dac_trung.py"),
        ("Dự báo 28 ngày, cập nhật mỗi tuần", f"{cm.ma_mo_hinh}", "nang_cap_du_bao_v4.py"), ("SS · ROP · EOQ", "theo mức phục vụ", "ton_kho.py"),
        ("Cảnh báo, đề xuất", "người lập kế hoạch duyệt", "app/dashboard.py")]
C.o_hang([(f"Bước {i + 1}", t_, f"{p_} · {f_}", False) for i, (t_, p_, f_) in enumerate(buoc)])

tuan, nam, thu, mua, tang, abcxyz = tong_quan()

C.muc("Giá trị hàng xuất kho mỗi tuần", "3 năm, theo giá vốn")
sk = pd.DataFrame(
    [("Tết", d) for d in C.q("SELECT ngay FROM lich_su_kien WHERE ten_su_kien = 'tet'").ngay]
    + [("Trung thu", d) for d in C.q("SELECT ngay FROM lich_su_kien WHERE ten_su_kien = 'trung_thu'").ngay]
    + [("Bão Yagi", "2024-09-07")] + [("Sale 11.11", f"{y}-11-11") for y in (2023, 2024, 2025)], columns=["su_kien", "ngay"])
sk["ngay"] = pd.to_datetime(sk.ngay)
sk_mau = alt.Scale(domain=["Tết", "Trung thu", "Bão Yagi", "Sale 11.11"], range=[C.DO, C.LA, C.MUC2, C.HO_PHACH])
test = pd.DataFrame({"tu": [pd.Timestamp("2025-10-01")], "den": [tuan.ngay.max()], "nhan": ["Năm dùng để kiểm tra mô hình"]})
gan = alt.selection_point(nearest=True, on="pointerover", fields=["ngay"], empty=False, clear="pointerout")
nen = alt.Chart(test).mark_rect(color="#1d4f7314").encode(x="tu:T", x2="den:T")
nen_txt = alt.Chart(test).mark_text(align="left", dx=6, dy=10, baseline="top", color=C.PHIEU, fontSize=11, fontWeight=600).encode(
    x="tu:T", y=alt.value(0), text="nhan:N")
duong = alt.Chart(tuan).mark_line(color=C.MUC, strokeWidth=1.5).encode(
    x=alt.X("ngay:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False)),
    y=alt.Y("trieu:Q", title="Triệu đồng / tuần", axis=alt.Axis(format=",d")))
moc = alt.Chart(sk).mark_rule(strokeWidth=1.5, strokeDash=[4, 3]).encode(
    x="ngay:T", color=alt.Color("su_kien:N", scale=sk_mau, title=None, legend=alt.Legend(orient="top")),
    tooltip=[alt.Tooltip("su_kien:N", title="Sự kiện"), alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y")])
re_ = alt.Chart(tuan).mark_rule(color=C.MUC2).encode(
    x="ngay:T", opacity=alt.condition(gan, alt.value(0.7), alt.value(0)),
    tooltip=[alt.Tooltip("ngay:T", title="Tuần từ", format="%d/%m/%Y"), alt.Tooltip("trieu:Q", title="Triệu đồng", format=",.0f")]
).add_params(gan)
C.ve_bd(alt.layer(nen, nen_txt, duong, moc, re_).properties(height=280))
dinh = tuan.loc[tuan.trieu.idxmax()]
tet = sk[sk.su_kien == "Tết"].ngay
cach_tet = (tet[tet >= dinh.ngay] - dinh.ngay).dt.days.min()
C.ghi("mỗi điểm là tổng giá trị hàng xuất trong 1 tuần (số lượng × giá vốn, 121 mã). Vạch đứt màu là sự kiện; vùng tô là năm kiểm tra.",
      f"tuần cao nhất bắt đầu {ngay_vn(dinh.ngay)}{f' ({cach_tet} ngày trước Tết)' if cach_tet <= 30 else ''}, gấp "
      f"{vn(dinh.trieu / tuan.trieu.median())} lần tuần bình thường; tuần Tết kho nghỉ nên tụt sâu. Năm 3 so với năm 1: "
      f"{C.dau_cong((nam[2] / nam[0] - 1) * 100)}% → nhu cầu gần như đi ngang, biến động chủ yếu do mùa và sự kiện.")

c1, c2 = st.columns([1.35, 1], gap="large")
with c1:
    C.muc("Mùa vụ theo nhóm hàng", "1 = bán bình thường của chính nhóm đó")
    hm = mua.copy()
    hm["mau"] = np.log2(hm.chi_so.clip(lower=0.125)).clip(-3, 3)       # log: gap doi va giam mot nua cach deu 1
    hm["nhan"] = np.where(hm.chi_so >= 2, "×" + hm.chi_so.map(lambda v: vn(v, 1)), "")
    thu_tu = hm.groupby("nhom_hang").chi_so.max().sort_values(ascending=False).index.tolist()
    base = alt.Chart(hm).encode(x=alt.X("thang:O", title="Tháng", axis=alt.Axis(labelAngle=0)),
                                y=alt.Y("nhom_hang:N", sort=thu_tu, title=None))
    o = base.mark_rect(stroke=C.LIEN["du-lieu"], strokeWidth=2).encode(
        color=alt.Color("mau:Q", scale=alt.Scale(domain=[-3, 0, 3], range=[C.PHIEU, "#f3f1ea", C.DO], interpolate="rgb"), legend=None),
        tooltip=[alt.Tooltip("nhom_hang:N", title="Nhóm hàng"), alt.Tooltip("thang:O", title="Tháng"),
                 alt.Tooltip("chi_so:Q", title="So với bình thường (lần)", format=".2f")])
    chu = base.mark_text(fontSize=10, fontWeight=600).encode(
        text="nhan:N", color=alt.condition(alt.datum.chi_so >= 3, alt.value("white"), alt.value(C.MUC)))
    C.ve_bd((o + chu).properties(height=420))
    top = hm.loc[hm.groupby("nhom_hang").chi_so.idxmax()].sort_values("chi_so", ascending=False).head(3)
    C.ghi("đỏ = bán nhiều hơn bình thường (ô ghi ×2 trở lên), xanh = ít hơn.",
          "mạnh nhất: " + "; ".join(f"{r.nhom_hang} tháng {r.thang} ×{vn(r.chi_so)}" for r in top.itertuples())
          + ". Đỉnh trùng Tết, hè, Trung thu, Noel: mô hình phải biết lịch này, đặt hàng cũng phải sớm hơn.")
with c2:
    C.muc("Thứ trong tuần", "1 = trung bình mọi ngày")
    tw = thu.assign(ten=lambda f: f.thu.map(dict(enumerate(THU))))
    bb = alt.Chart(tw).encode(x=alt.X("ten:N", sort=THU, title=None, axis=alt.Axis(labelAngle=0)),
                              y=alt.Y("chi_so:Q", title="Lần", scale=alt.Scale(domain=[0, 1.35])))
    cot = bb.mark_bar(color=C.C_AI, width=24).encode(tooltip=[alt.Tooltip("ten:N", title="Thứ"),
                                                              alt.Tooltip("chi_so:Q", title="Lần", format=".2f")])
    nh = bb.mark_text(dy=-8, color=C.MUC, fontSize=11, fontWeight=600).encode(text=alt.Text("chi_so:Q", format=".2f"))
    mot = alt.Chart(pd.DataFrame({"y": [1]})).mark_rule(color=C.PHIEU, strokeDash=[4, 3]).encode(y="y:Q")
    C.ve_bd((cot + nh + mot).properties(height=190))
    cn, cao = thu.chi_so.iloc[6], thu.loc[thu.chi_so.idxmax()]
    C.ghi("cột cao = bán nhiều hơn ngày trung bình.",
          f"Chủ nhật chỉ {vn(cn, 2)}, {THU[int(cao.thu)]} cao nhất ({vn(cao.chi_so, 2)}): xếp ca, lịch nhận – giao nhiều hơn cuối tuần.")
    C.muc("Khuyến mãi làm bán tăng bao nhiêu", f"{len(tang):,} đợt".replace(",", "."))
    hh = tang.clip(-50, 249).to_frame()
    hist = alt.Chart(hh).mark_bar(color=C.C_AI).encode(
        x=alt.X("tang:Q", bin=alt.Bin(step=20, extent=[-60, 260]), title="Bán tăng so với ngày thường cùng tháng (%)"),
        y=alt.Y("count():Q", title="Số đợt"), tooltip=[alt.Tooltip("count():Q", title="Số đợt")])
    tv = alt.Chart(pd.DataFrame({"x": [tang.median()]})).mark_rule(color=C.MUC, strokeWidth=2).encode(x="x:Q")
    C.ve_bd((hist + tv).properties(height=170))
    C.ghi("mỗi cột là số đợt theo mức bán tăng; vạch đen là trung vị.",
          f"một nửa số đợt tăng ít nhất {vn(tang.median(), 0)}%, 1/4 số đợt từ {vn(tang.quantile(0.75), 0)}% trở lên.")

c1, c2 = st.columns(2, gap="large")
with c1:
    C.muc("Phân nhóm ABC × XYZ", "số mã và % giá trị xuất (2 năm đầu)")
    abcxyz["nhan"] = abcxyz.so_ma.astype(str) + " mã\n" + abcxyz.pt.map(lambda v: vn(v)) + "%"
    base = alt.Chart(abcxyz).encode(x=alt.X("xyz:N", title="XYZ: X ổn định → Z thất thường / mùa vụ", axis=alt.Axis(labelAngle=0)),
                                    y=alt.Y("abc:N", title="ABC: A giá trị cao → C thấp"))
    o = base.mark_rect(stroke=C.LIEN["du-lieu"], strokeWidth=3).encode(
        color=alt.Color("pt:Q", scale=alt.Scale(range=["#f3f1ea", C.PHIEU]), legend=None),
        tooltip=[alt.Tooltip("abc:N", title="ABC"), alt.Tooltip("xyz:N", title="XYZ"), alt.Tooltip("so_ma:Q", title="Số mã"),
                 alt.Tooltip("pt:Q", title="% giá trị xuất", format=".1f")])
    chu = base.mark_text(lineBreak="\n", fontSize=12, fontWeight=600).encode(
        text="nhan:N", color=alt.condition(alt.datum.pt >= 30, alt.value("white"), alt.value(C.MUC)))
    C.ve_bd((o + chu).properties(height=250))
    ax = abcxyz[(abcxyz.abc == "A") & (abcxyz.xyz == "X")].iloc[0]
    C.ghi("màu càng đậm càng nhiều giá trị.",
          f"{ax.so_ma} mã A-X ({vn(100 * ax.so_ma / abcxyz.so_ma.sum(), 0)}% số mã) chiếm {vn(ax.pt)}% giá trị: bán nhiều và ổn định → "
          "nên tự động hóa đặt hàng nhóm này trước.")
with c2:
    C.muc("Mô hình dự báo nào chính xác nhất", "WMAPE năm kiểm tra, thấp = tốt")
    TEN_MH = {cm.ma_mo_hinh: "AI kết hợp, cập nhật tuần (được chọn)", "ket_hop_v3": "AI kết hợp, cập nhật 28 ngày",
              "lightgbm": "LightGBM (AI)", "prophet": "Prophet (AI)", "lstm_tuan": "LSTM (học sâu, không được chọn)", "rnn_tuan": "RNN (học sâu, không được chọn)",
              C.MOC: "Trung bình 28 ngày, cập nhật tuần",
              "tb_truot_28": "Trung bình 28 ngày, cập nhật 28 ngày", "croston_sba": "Croston (bán thưa)", "tsb": "TSB (bán thưa)",
              "ets": "ETS / Holt-Winters", "naive": "Lấy ngày gần nhất", "seasonal_naive_7": "Lặp lại tuần trước"}
    xh = C.q("SELECT ma_mo_hinh, wmape FROM v_xep_hang_mo_hinh WHERE pham_vi = 'Toan bo 121 SKU'")
    xh = xh[xh.ma_mo_hinh.isin(TEN_MH)].assign(ten=lambda f: f.ma_mo_hinh.map(TEN_MH), pt=lambda f: f.wmape * 100)
    xh["loai"] = np.where(xh.ma_mo_hinh == cm.ma_mo_hinh, "chon", np.where(xh.ma_mo_hinh == C.MOC, "moc", "khac"))
    base = alt.Chart(xh).encode(y=alt.Y("ten:N", sort=xh.sort_values("pt").ten.tolist(), title=None, axis=alt.Axis(labelLimit=220, labelOverlap=False)),
                                x=alt.X("pt:Q", title="WMAPE (%)", scale=alt.Scale(domain=[0, xh.pt.max() * 1.15])))
    cot = base.mark_bar(height=16).encode(
        color=alt.Color("loai:N", scale=alt.Scale(domain=["chon", "moc", "khac"], range=[C.C_AI, C.C_MOC, "#c3c9cd"]), legend=None),
        tooltip=[alt.Tooltip("ten:N", title="Mô hình"), alt.Tooltip("pt:Q", title="WMAPE (%)", format=".1f")])
    nh = base.mark_text(align="left", dx=4, color=C.MUC, fontSize=11, fontWeight=600).encode(text=alt.Text("pt:Q", format=".1f"))
    C.ve_bd((cot + nh).properties(height=300))
    w_ai, w_moc = xh.set_index("ma_mo_hinh").pt[[cm.ma_mo_hinh, C.MOC]]
    C.ghi("WMAPE = tổng |thực tế − dự báo| ÷ tổng thực tế, theo ngày, 12 tháng kiểm tra. Mô hình chọn trên validation, test chạy một lần. "
          "Bản cập nhật tuần chấm trên bản dự báo mới nhất cho mỗi ngày (cách dùng thật).",
          f"AI sai {vn(w_ai)}%, trung bình 28 ngày sai {vn(w_moc)}%: AI giảm {vn((1 - w_ai / w_moc) * 100, 0)}% sai số.")

C.muc("Công thức đặt hàng", "tính lại mỗi ngày theo dự báo")
st.markdown(
    "- **SS** (tồn kho an toàn) = z × √(σ_LTD² + d² × σ_LT²): z theo mức phục vụ (90% → 1,28; 95% → 1,64; 99% → 2,33); "
    "σ_LTD = độ lệch chuẩn tổng sai số dự báo trong lead time (đo trên validation); d = nhu cầu dự báo bình quân/ngày; "
    "σ_LT = độ lệch chuẩn lead time.\n"
    "- **ROP** (điểm đặt hàng) = nhu cầu dự báo trong lead time + SS. Khi trong kho + hàng đang về ≤ ROP thì đặt hàng.\n"
    "- **EOQ** (lượng đặt kinh tế) = √(2 × D × S / H): D = nhu cầu năm, S = chi phí 1 lần đặt, H = chi phí lưu kho 1 đơn vị/năm. "
    "Hàng ổn định (X, Y): lượng đặt = bội số của max(EOQ, MOQ). Hàng mùa vụ (Z): đặt bù đến mức = dự báo (lead time + 7 ngày) "
    "+ SS − (trong kho + đang về), tối thiểu MOQ (quy tắc \"lai\", chọn trên validation vì EOQ giả định nhu cầu đều).\n"
    f"- **Dự báo:** mô hình `{cm.ma_mo_hinh}`, kết hợp LightGBM (dự báo theo tầm, lịch sự kiện / âm lịch) với Prophet theo "
    "nhóm XYZ; trọng số chọn trên validation, test chạy một lần.")
