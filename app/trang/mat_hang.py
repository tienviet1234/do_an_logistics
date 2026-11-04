"""Man Mat hang: 1 ma hang. Nhan ma hang, ton kho 12 thang (bam de doi ngay lap phieu), du bao so voi thuc te,
"Thu neu..." (doi muc phuc vu / hang ve cham -> SS, ROP, EOQ, luong dat tinh lai ngay theo dung cong thuc mo phong),
ket qua ca nam cua ma theo tung chinh sach."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import chung as C
from chung import ngay_vn, vn

s = st.session_state
cs = s.cs
t, nghi = C.ngay_lam_viec()
p = C.sku_loc()
sku = C.ds_sku().set_index("ma_sku")
m = C.mo_phong(cs)
if nghi:
    st.info(nghi)

# ------------------------------------------------------------------ chon ma (giu qua cac man; di sau tu man Hom nay)
if s.sku is None:
    can_dat = m[(m.ngay == t) & (m.tt == 1) & m.ma_sku.isin(p.ma_sku)]
    s.sku = can_dat.ma_sku.iloc[0] if len(can_dat) else (p.ma_sku.iloc[0] if len(p) else C.ds_sku().ma_sku.iloc[0])
ds = list(p.ma_sku) + ([s.sku] if s.sku not in set(p.ma_sku) else [])
s["_sku_w"] = s.sku
c1, c2 = st.columns([2.2, 3], vertical_alignment="bottom")
c1.selectbox("Mặt hàng", ds, key="_sku_w", format_func=lambda v: f"{v} · {sku.ten_sku[v]}",
             on_change=lambda: s.update(sku=s["_sku_w"]),
             help=f"Danh sách theo bộ lọc ở đầu phiếu ({C.mo_ta_loc()}).")
ma = s.sku
r = sku.loc[ma]
hom = m[(m.ma_sku == ma) & (m.ngay == t)].iloc[0]
c2.markdown(f'<div class="phai">{C.dau_tt(int(hom.tt))}&nbsp; <span class="dp-phu">cuối ngày {ngay_vn(t)} · '
            f'{C.CS_NGAN[cs]}</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="dp-ma"><span>{ma}</span> · {r.ten_sku}</div>', unsafe_allow_html=True)
C.o_hang([("Nhóm hàng", r.nhom_hang, r.loai_nhu_cau, False),
          ("ABC · XYZ", f"{r.abc_train} · {r.xyz_train}", "giá trị · độ ổn định", False),
          ("Nhà cung cấp", r.ma_ncc, f"MOQ {vn(r.moq, 0)} {r.don_vi}", False),
          ("Chờ hàng (lead time)", f"{vn(r.lead_time_tb)} ngày", f"± {vn(r.lead_time_std)} ngày", False),
          ("Trong kho cuối ngày", vn(hom.ton_cuoi, 0), r.don_vi, False),
          ("Đang về", vn(hom.dang_ve, 0), f"ROP {vn(hom.rop, 0)}", False)])

trai, phai = st.columns([1.9, 1], gap="large")

# ------------------------------------------------------------------ ton kho 12 thang
with trai:
    C.muc("Tồn kho 12 tháng kiểm tra", "bấm dải trạng thái bên dưới để lập phiếu ngày đó")
    so_ht = st.toggle("So với hiện trạng*", key="mh_ht")
    y = m[m.ma_sku == ma][["ngay", "ton_cuoi", "rop", "dat_hang", "tt"]].copy()
    y["rop"] = y.rop.ffill()                                       # ngay kho nghi giu ROP ngay truoc
    y["d"] = pd.to_datetime(y.ngay)
    chuoi = [(f"Tồn cuối ngày: {C.CS_NGAN[cs]}", C.CS_MAU[cs], "ton_cuoi"), ("ROP (điểm đặt hàng)", C.MUC2, "rop")]
    if so_ht:
        ht = C.mo_phong("hien_trang")
        y["ton_ht"] = ht[ht.ma_sku == ma].set_index("ngay").ton_cuoi.reindex(y.ngay).values
        chuoi.append(("Tồn cuối ngày: hiện trạng*", C.C_HT, "ton_ht"))
    mau = alt.Scale(domain=[c[0] for c in chuoi], range=[c[1] for c in chuoi])
    ten_chuoi = " : ".join(f"datum.key == '{c}' ? '{n}'" for n, _, c in chuoi) + " : ''"
    # dung chung: bieu do ton kho + dai trang thai. Mien ngay phai la alt.DateTime: Timestamp bi doi thanh chuoi ISO,
    # Vega-Lite khong hieu -> truc thoi gian hong, bieu do trong (da gap, chi thay khi chup trinh duyet that)
    dau_, cuoi_ = y.d.min(), y.d.max() + pd.Timedelta(days=1)
    thang = alt.Scale(domain=[alt.DateTime(year=dau_.year, month=dau_.month, date=dau_.day),
                              alt.DateTime(year=cuoi_.year, month=cuoi_.month, date=cuoi_.day)])
    truc_x = alt.X("d:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False), scale=thang)
    # moi lop dung chung 1 bang (y): duong gop cot bang transform_fold, vach dat hang / ngay dang xem la bo loc
    y["dang_xem"] = (y.ngay == t).astype(int)
    goc_y = alt.Chart(y)
    duong = goc_y.transform_fold([c for _, _, c in chuoi]).transform_calculate(chuoi=ten_chuoi).mark_line(
        strokeWidth=1.8, interpolate="step-after").encode(
        x=truc_x, y=alt.Y("value:Q", title=r.don_vi),
        color=alt.Color("chuoi:N", scale=mau, title=None, legend=alt.Legend(orient="top")),
        strokeDash=alt.condition(alt.datum.key == "rop", alt.value([5, 3]), alt.value([1, 0])))
    vach = goc_y.transform_filter(alt.datum.dat_hang > 0).mark_tick(color=C.HO_PHACH, thickness=2, size=10).encode(
        x="d:T", y=alt.datum(0), tooltip=[alt.Tooltip("d:T", title="Ngày đặt", format="%d/%m/%Y"),
                                            alt.Tooltip("dat_hang:Q", title="Lượng đặt", format=",.0f")])
    gan = alt.selection_point(nearest=True, on="pointerover", fields=["d"], empty=False, clear="pointerout")
    re_ = goc_y.mark_rule(color=C.MUC2).encode(
        x="d:T", opacity=alt.condition(gan, alt.value(0.6), alt.value(0)),
        tooltip=[alt.Tooltip("d:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("ton_cuoi:Q", title="Tồn cuối", format=",.0f"),
                 alt.Tooltip("rop:Q", title="ROP", format=",.0f")]).add_params(gan)
    vh = goc_y.transform_filter(alt.datum.dang_xem == 1).mark_rule(color=C.MUC, strokeWidth=1.5, strokeDash=[3, 2]).encode(x="d:T")
    C.ve_bd(alt.layer(duong, vach, re_, vh).properties(height=300))
    # dai trang thai tung ngay cua ma (1 lop o chu nhat: Streamlit 1.45 chi bat duoc cu bam tren bieu do 1 lop, va bieu do
    # duong khong nhan cu bam "gan nhat") -> bam 1 ngay de doi ngay lap phieu
    dt_ = y[y.tt.notna()].copy()
    dt_["d2"] = dt_.d + pd.Timedelta(days=1)
    TEN4 = C.TRANG_THAI + ["Ngày đang xem"]
    dt_["nhom"] = np.where(dt_.ngay == t, "Ngày đang xem", dt_.tt.map(lambda i: C.TRANG_THAI[int(i)]))
    sel = alt.selection_point(name="chon_ngay", fields=["ngay"], on="click", empty=False)
    dai = alt.Chart(dt_).mark_rect().encode(
        x=alt.X("d:T", title=None, axis=None, scale=thang), x2="d2:T",
        y=alt.value(0), y2=alt.value(34),                          # o chu nhat khong co y thi cao 0: khong hien, khong bam duoc
        color=alt.Color("nhom:N", title=None, scale=alt.Scale(domain=TEN4, range=C.C_TT + ["#c9dccb", C.MUC]),
                        legend=None),               # chu thich lam vung ve 34px gan bang 0 -> giai thich mau o ghi chu ben duoi
        tooltip=[alt.Tooltip("d:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("nhom:N", title="Trạng thái"),
                 alt.Tooltip("ton_cuoi:Q", title="Tồn cuối", format=",.0f")]).add_params(sel)
    khoa_dai = f"dai_{ma}_{cs}_{t}"                                # du lieu doi -> khoa doi
    C.ve_bd(dai.properties(height=34), selection_mode="chon_ngay", key=khoa_dai, on_select=lambda: C.khi_chon_ngay(khoa_dai))
    kq = C.q("""SELECT ma_chinh_sach, 100.0 * da_dap_ung / nhu_cau AS fr, so_ngay_thieu, ton_tb, so_lan_nhap
                FROM ket_qua_ton_kho WHERE ma_sku = ? AND ROUND(muc_phuc_vu, 2) = ?""", (ma, C.MAIN)).set_index("ma_chinh_sach")
    C.ghi("đường bậc thang là tồn cuối mỗi ngày (bậc nhảy lên là ngày hàng về); nét đứt là ROP; vạch nhỏ phía dưới là ngày "
          "đặt hàng; vạch đứt dọc là ngày đang xem. Dải màu dưới biểu đồ là trạng thái cuối mỗi ngày của mã: đỏ hết hàng, cam đặt hàng, xanh dương dưới ROP "
          "(hàng đang về), xanh lá đủ hàng, ô đen là ngày đang xem; bấm vào dải để lập phiếu ngày đó.",
          f"cả năm, {C.CS_NGAN[cs]} đáp ứng {vn(kq.fr[cs])}% nhu cầu, {int(kq.so_ngay_thieu[cs])} ngày thiếu, tồn bình quân "
          f"{vn(kq.ton_tb[cs], 0)} {r.don_vi}, nhập {int(kq.so_lan_nhap[cs])} lần. Hiện trạng*: {vn(kq.fr['hien_trang'])}%, "
          f"{int(kq.so_ngay_thieu['hien_trang'])} ngày thiếu, tồn {vn(kq.ton_tb['hien_trang'], 0)}.")

    # -------------------------------------------------------------- du bao so voi thuc te
    C.muc("Dự báo và thực tế", "12 tháng kiểm tra, dự báo cập nhật mỗi tuần, mỗi ngày dùng bản mới nhất")
    a1, a2 = st.columns([1, 1.4], vertical_alignment="center")
    gop = a1.segmented_control("Xem theo", ["Tuần", "Ngày"], default="Tuần", key="mh_gop") or "Tuần"
    so_moc = a2.toggle("So với dự báo mốc (TB trượt 28 ngày)", value=True, key="mh_moc")
    cm = C.mo_hinh_chon().ma_mo_hinh
    d = C.q("""SELECT ma_mo_hinh, ngay, ngay_thu, du_bao, thuc_te, thap_80, cao_80 FROM du_bao WHERE tap = 'test'
               AND ma_sku = ? AND ma_mo_hinh IN (?, ?)""", (ma, cm, C.MOC))
    d = d.sort_values("ngay_thu").drop_duplicates(["ma_mo_hinh", "ngay"])   # moi ngay: ban moi nhat (cap nhat moi tuan)
    w = d.pivot(index="ngay", columns="ma_mo_hinh", values="du_bao").rename(columns={cm: "ai", C.MOC: "moc"})
    w["thuc_te"] = d.drop_duplicates("ngay").set_index("ngay").thuc_te
    kh = d[d.ma_mo_hinh == cm].set_index("ngay")
    w["thap_80"], w["cao_80"] = kh.thap_80, kh.cao_80
    w = w.reset_index()
    w["d"] = pd.to_datetime(w.ngay)
    ok = w.thuc_te.notna()
    tong = w.thuc_te[ok].sum()
    wm = lambda c: np.abs(w.thuc_te[ok] - w[c][ok]).sum() / tong if tong > 0 else np.nan
    bias = (w.thuc_te[ok] - w.ai[ok]).sum() / tong if tong > 0 else np.nan
    C.o_hang([("WMAPE dự báo AI", "–" if np.isnan(wm("ai")) else vn(wm("ai"), 3), "thấp = tốt", False),
              ("WMAPE dự báo mốc", "–" if np.isnan(wm("moc")) else vn(wm("moc"), 3), "TB trượt 28 ngày", False),
              ("Bias dự báo AI", "–" if np.isnan(bias) else f"{C.dau_cong(bias * 100)}%", "dương = dự báo thiếu", False),
              ("Ngày được chấm", f"{int(ok.sum())}/{len(w)}", "bỏ ngày nghỉ, hết hàng, B2B", False)])
    chuoi = [("thuc_te", "Thực tế (nhu cầu tin được)", C.C_THUC_TE), ("ai", "Dự báo AI (được chọn)", C.C_AI)]
    if so_moc:
        chuoi.append(("moc", "Dự báo mốc", C.C_MOC))
    if gop == "Tuần":
        g = w[ok].copy()                                   # chi cong ngay duoc cham de thuc te va du bao so cung ngay
        g["d"] = g.d - pd.to_timedelta(g.d.dt.weekday, unit="D")
        g = g.groupby("d", as_index=False)[["thuc_te", "ai", "moc"]].sum()
    else:
        g = w
    # moi lop dung CHUNG 1 bang (g): duong gop cot bang transform_fold, doan dut theo tung chuoi (ngay khong cham lam dut duong).
    # Moi lop 1 bang rieng thi khi doi xem Tuan / Ngay Streamlit 1.45 thinh thoang loi Vega "Unrecognized data set" (da gap).
    g = g.copy()
    for c, _, _ in chuoi:
        g[f"doan_{c}"] = g[c].isna().cumsum()
    mau = alt.Scale(domain=[c[1] for c in chuoi], range=[c[2] for c in chuoi])
    goc_g = alt.Chart(g)
    lines = goc_g.transform_fold([c for c, _, _ in chuoi]).transform_filter("isValid(datum.value)").transform_calculate(
        chuoi=" : ".join(f"datum.key == '{c}' ? '{n}'" for c, n, _ in chuoi) + " : ''",
        doan=" : ".join(f"datum.key == '{c}' ? datum.doan_{c}" for c, _, _ in chuoi) + " : 0").mark_line(strokeWidth=1.8).encode(
        x=alt.X("d:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False)),
        y=alt.Y("value:Q", title=f"{r.don_vi} / {gop.lower()}"), detail="doan:N",
        color=alt.Color("chuoi:N", scale=mau, title=None, legend=alt.Legend(orient="top")),
        strokeDash=alt.condition(alt.datum.key == "moc", alt.value([5, 3]), alt.value([1, 0])))
    gan = alt.selection_point(nearest=True, on="pointerover", fields=["d"], empty=False, clear="pointerout")
    tip = [alt.Tooltip("d:T", title="Tuần từ" if gop == "Tuần" else "Ngày", format="%d/%m/%Y")] + [
        alt.Tooltip(f"{c}:Q", title=n, format=",.0f") for c, n, _ in chuoi]
    rule = goc_g.mark_rule(color=C.MUC2).encode(
        x="d:T", opacity=alt.condition(gan, alt.value(0.7), alt.value(0)), tooltip=tip).add_params(gan)
    lop = [lines, rule]
    if gop == "Ngày" and w.thap_80.notna().any():          # khoang 80% chi ve theo ngay (cong phan vi theo tuan khong dung)
        tip.append(alt.Tooltip("thap_80:Q", title="Khoảng 80%: thấp", format=",.0f"))
        tip.append(alt.Tooltip("cao_80:Q", title="Khoảng 80%: cao", format=",.0f"))
        rule = rule.encode(tooltip=tip)
        dai = goc_g.transform_filter("isValid(datum.thap_80)").mark_area(color=C.C_AI, opacity=0.16).encode(
            x="d:T", y="thap_80:Q", y2="cao_80:Q")
        lop = [dai, lines, rule]
    C.ve_bd(alt.layer(*lop).properties(height=280))
    trong = w[ok & w.thap_80.notna()]
    phu = ((trong.thuc_te >= trong.thap_80) & (trong.thuc_te <= trong.cao_80)).mean() if len(trong) else np.nan
    C.ghi("rê chuột để xem từng " + ("tuần" if gop == "Tuần" else "ngày") + ". Theo tuần chỉ cộng ngày được chấm. "
          "Xem theo ngày có dải xanh nhạt: khoảng 80% (80% khả năng nhu cầu nằm trong dải).",
          "đường thực tế đứt ở ngày không chấm (kho nghỉ, hết hàng, đơn B2B đột biến). Dự báo chỉ dùng dữ liệu đến ngày lập dự báo."
          + ("" if phu != phu else f" Mã này: {vn(100 * phu, 0)}% số ngày thực tế nằm trong khoảng 80%."))

# ------------------------------------------------------------------ thu neu...
with phai:
    C.muc("Thử nếu…", f"tính lại cho ngày {ngay_vn(t)}")
    s.setdefault("thu_lv", 95.0)
    s.setdefault("thu_lt", 0)
    s["_lv_w"], s["_lt_w"] = s.thu_lv, s.thu_lt
    st.slider("Mức phục vụ mục tiêu (%)", 90.0, 99.5, step=0.5, format="%.1f", key="_lv_w", on_change=lambda: s.update(thu_lv=s["_lv_w"]),
              help="Xác suất không hết hàng trong thời gian chờ hàng; quyết định hệ số z trong công thức SS.")
    st.slider("Hàng về chậm thêm (ngày)", 0, 7, key="_lt_w", on_change=lambda: s.update(thu_lt=s["_lt_w"]),
              help="Lead time dài thêm k ngày và công thức được cập nhật theo lead time mới.")
    goc = C.thu_neu(cs, ma, t)
    thu = C.thu_neu(cs, ma, t, s.thu_lv / 100, s.thu_lt)
    hang = [("SS (dự phòng)", "ss"), ("ROP (điểm đặt)", "rop"), ("EOQ (mỗi lần đặt)", "eoq"), ("Đặt hôm nay", "dat")]
    dong = "".join(f'<tr{" class=chon" if k == "dat" else ""}><td>{n}</td><td>{vn(goc[k], 0)}</td><td>{vn(thu[k], 0)}</td>'
                   f'<td>{C.dau_cong(thu[k] - goc[k], 0) if abs(thu[k] - goc[k]) >= 0.5 else "0"}</td></tr>' for n, k in hang)
    st.markdown(f'<table class="phieu"><tr><th>Đơn vị: {r.don_vi}</th><th>Hiện tại<br>95% · {goc["L"]} ngày</th>'
                f'<th>Thử<br>{vn(s.thu_lv)}% · {thu["L"]} ngày</th><th>Chênh</th></tr>{dong}</table>', unsafe_allow_html=True)
    st.write("")
    von = (thu["ss"] - goc["ss"]) * r.gia_von / 1e6
    if thu["dat"] > 0 and goc["dat"] == 0:
        viec = f"hôm nay <b>phải đặt {vn(thu['dat'], 0)} {r.don_vi}</b> (hiện tại chưa cần đặt)"
    elif thu["dat"] == 0 and goc["dat"] > 0:
        viec = f"hôm nay <b>chưa cần đặt</b> (hiện tại đặt {vn(goc['dat'], 0)})"
    elif thu["dat"] > 0:
        viec = f"hôm nay đặt <b>{vn(thu['dat'], 0)} {r.don_vi}</b> (hiện tại {vn(goc['dat'], 0)})"
    else:
        viec = "hôm nay vẫn <b>chưa cần đặt</b>"
    st.markdown(f'<div class="dao-mau">Trong kho + đang về {vn(goc["ip"], 0)} {r.don_vi}. Với mức phục vụ <b>{vn(s.thu_lv)}%</b>'
                f'{f" và hàng về chậm <b>{s.thu_lt} ngày</b>" if s.thu_lt else ""}, {viec}. Dự phòng '
                f'{"tăng" if von >= 0 else "giảm"} <b>{vn(abs(von))} triệu đồng</b> vốn (theo giá vốn).</div>',
                unsafe_allow_html=True)
    st.caption(f"Quy tắc lượng đặt của mã này: {'đặt bù đến mức (hàng mùa vụ Z)' if goc['quy_tac'] == 'dat_den_muc' else 'bội số EOQ'}. "
               "Chỉ tính lại cho ngày đang xem, không chạy lại mô phỏng cả năm. Ở 95% và không chậm, kết quả trùng đúng mô phỏng. "
               "Hàng về chậm: giả định sai số dự báo tăng theo căn bậc hai số ngày chờ.")

    C.muc("Kết quả cả năm của mã này", "mức phục vụ 95%")
    dong = "".join(f'<tr{" class=chon" if c == cs else ""}><td>{C.CS_NGAN[c]}</td><td>{vn(kq.fr[c])}%</td>'
                   f'<td>{int(kq.so_ngay_thieu[c])}</td><td>{vn(kq.ton_tb[c], 0)}</td></tr>' for c in C.CS_TEN)
    st.markdown(f'<div class="bang-cuon"><table class="phieu"><tr><th>Chính sách</th><th>Fill Rate</th><th>Ngày thiếu</th>'
                f'<th>Tồn TB</th></tr>{dong}</table></div>', unsafe_allow_html=True)
    st.caption(C.NOTE_HT)

# ------------------------------------------------------------------ tru hang cho phien livestream (src/tru_hang_live.py, docs/10 muc 10.8)
C.muc("Trữ hàng cho phiên livestream", "chưa có phiên live thật: hệ số khuyến mãi lấy từ siêu thị Mỹ 1989–1997 hoặc dữ liệu mô phỏng, phần còn lại là giả định")
LIVE = C.LIVE
mau_ht, _, nc_live, km_live, nghi_live = C.du_lieu_live()
hs_that = C.he_so_that()
NGUON_DEAL = {"that": "Số thật Dominick's, theo mức giảm", "he_thong": "Dữ liệu của hệ thống + độ co giãn"}
nguon_co = ([] if hs_that is None else ["that"]) + (["he_thong"] if len(mau_ht) >= LIVE.TOI_THIEU_MAU_DEAL else [])
nen_live = LIVE.muc_nen_gan_nhat(nc_live, km_live, nghi_live, t).get(ma, np.nan)
if not nguon_co:
    st.info("Chưa có hệ số khuyến mãi: nguồn dữ liệu này không có lịch khuyến mãi và chưa có tệp số thật (chạy src/phan_tich_dominicks.py --buoc sau_doi_chieu).")
elif not (r.gia_ban > 0 and r.gia_von > 0):
    st.info(f"{ma} chưa có giá bán hoặc giá vốn nên chưa tính được lãi.")
else:
    def giu(k, mac_dinh):
        """Gia tri giu qua cac man va cac lan chay lai; tra ve ham cap nhat cho on_change."""
        s.setdefault(k, mac_dinh)
        s[f"_{k}_w"] = s[k]
        return lambda: s.update({k: s[f"_{k}_w"]})

    vao, ra = st.columns([1, 2.1], gap="large")
    with vao:
        nen_do = float(nen_live) if nen_live > 0 else None
        if nen_do is None:                                        # hang mua vu trai mua: moi mat hang deu ban online duoc nen cho nhap tay, khong chan
            s.setdefault("lv_nen_tay", 10)
            s["_lv_nen_w"] = s.lv_nen_tay
            st.number_input(f"Nhu cầu ngày thường ({r.don_vi}/ngày, tự nhập)", 1, 100000, step=1, key="_lv_nen_w", on_change=lambda: s.update(lv_nen_tay=s["_lv_nen_w"]),
                            help=f"{ma} không có nhu cầu ngày thường trong {LIVE.CUA_SO_NEN} ngày trước {ngay_vn(t)}, nên hệ thống chưa đo được mức nền.")
        nen_live = nen_do if nen_do is not None else float(s.lv_nen_tay)
        st.slider("Mức giảm giá (%)", 0, 50, step=5, key="_lv_giam_w", on_change=giu("lv_giam", 15))
        st.slider("Nhãn hàng tài trợ (% phần giảm)", 0, 100, step=5, key="_lv_tt_w", on_change=giu("lv_tt", int(100 * LIVE.TAI_TRO_SAU_DOI_CHIEU)),
                  help="Mặc định làm tròn từ số đo trên Dominick's, chỉ là ước lượng; khác nhiều giữa các ngành. Có hợp đồng với nhãn hàng thì nhập đúng số đó.")
        st.slider("Khả năng lên xu hướng (%)", 0, 80, step=5, key="_lv_p_w", on_change=giu("lv_p", 20),
                  help="Khả năng phiên được thuật toán đẩy. Không đoán trước được, nên nhập theo kinh nghiệm các phiên trước.")
        st.slider("Quy mô phiên (ngày bán thường)", 0.5, 10.0, step=0.5, format="%.1f", key="_lv_qm_w", on_change=giu("lv_qm", 1.0),
                  help="Phiên chưa lên xu hướng bán được bằng mấy ngày bán thường, trước khi nhân hệ số deal.")
        st.selectbox("Hàng thừa sau phiên", list(LIVE.HANG_THUA), format_func=LIVE.HANG_THUA.get, key="_lv_ht_w", on_change=giu("lv_ht", "ve_kho"))
        st.selectbox("Hàng bổ sung về sau", [2, 6, 12, 24], format_func=lambda g: f"{g} giờ", key="_lv_ve_w", on_change=giu("lv_ve", 6))
        st.selectbox("Hệ số khuyến mãi", nguon_co, format_func=NGUON_DEAL.get, key="_lv_ng_w", on_change=giu("lv_ng", nguon_co[0]),
                     help="Số thật: đúng dải giảm giá đang chọn, siêu thị Mỹ 1989–1997, theo tuần. Dữ liệu của hệ thống: đo từ dữ liệu đang dùng, nhân thêm độ co giãn đo trên số thật.")
    if s.lv_ng not in nguon_co:                                    # doi nguon du lieu giua chung: nguon da chon khong con
        s.lv_ng = nguon_co[0]
    gd_live = dict(giam_gia=s.lv_giam / 100, tai_tro=s.lv_tt / 100, p_xu_huong=s.lv_p / 100, quy_mo=float(s.lv_qm), gio_ve=int(s.lv_ve),
                   co_gian=float(hs_that["co_gian"]) if s.lv_ng == "he_thong" and hs_that is not None else 0.0)
    mau_deal = C.mau_live(s.lv_ng, gd_live["giam_gia"])
    if s.lv_ng == "that":
        dai_lv = LIVE.dai_theo_giam(hs_that, gd_live["giam_gia"])
        mo_ta_deal = f"hệ số deal từ {vn(dai_lv['n'], 0)} tuần giảm {vn(100 * dai_lv['tu'], 0)}–{vn(100 * dai_lv['den'], 0)}% của Dominick's (siêu thị Mỹ 1989–1997), trung vị ×{vn(dai_lv['p50'], 2)}"
    else:
        mo_ta_deal = f"hệ số deal đo từ {vn(len(mau_ht), 0)} ngày khuyến mãi trước kỳ kiểm tra" + (f", nhân độ co giãn {vn(gd_live['co_gian'], 2)}" if gd_live["co_gian"] else "")
    gd_o = LIVE.GiaDinh(**gd_live)
    kq_live = C.tinh_live(float(nen_live), float(r.gia_ban), float(r.gia_von), float(r.ty_le_chi_phi_luu_kho), s.lv_ht, gd_live, s.lv_ng)
    pa = kq_live["phuong_an"]
    nv = pa["newsvendor"]
    with ra:
        if kq_live["cu"] <= 0:
            hv = LIVE.tai_tro_hoa_von(float(r.gia_ban), float(r.gia_von), gd_o)
            can = "Nhãn hàng tài trợ hết phần giảm vẫn lỗ, nên giảm ít hơn." if hv is None else f"Nhãn hàng cần tài trợ ít nhất <b>{vn(100 * hv, 0)}%</b> phần giảm thì mới hòa vốn."
            st.markdown(f'<div class="dao-mau"><b>Không nên trữ cho phiên này.</b> Với mức giảm và tài trợ trên, mỗi {r.don_vi} bán ra lỗ <b>{vn(-kq_live["cu"], 0)} đ</b>. {can}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="dao-mau">Nên trữ <b>{vn(nv["q"], 0)} {r.don_vi}</b> ({vn(nv["q"] * r.gia_von / 1e6)} triệu đ vốn), đủ cho khoảng <b>{vn(100 * kq_live["ti_le"], 0)}%</b> số phiên: '
                        f'thiếu 1 {r.don_vi} mất <b>{vn(kq_live["cu"], 0)} đ</b> lãi, thừa 1 {r.don_vi} mất <b>{vn(kq_live["co"], 0)} đ</b>.</div>', unsafe_allow_html=True)
        st.write("")
        hang_pa = [("ngay_thuong", "Theo ngày thường"), ("trung_binh", "Theo trung bình"), ("newsvendor", "Newsvendor"), ("hai_buoc_2", "Newsvendor + bổ sung theo giờ")]
        dong_pa = "".join(f'<tr{" class=chon" if k == "newsvendor" else ""}><td>{n}</td><td>{vn(pa[k]["q"], 0)}</td><td>{vn(pa[k]["q2"], 0)}</td><td>{vn(pa[k]["lai"] / 1e3, 0)}</td>'
                          f'<td>{vn(pa[k]["p_het"], 0)}%</td><td>{vn(pa[k]["thua"], 0)}</td></tr>' for k, n in hang_pa)
        st.markdown(f'<div class="bang-cuon"><table class="phieu"><tr><th>Cách trữ · {r.don_vi}</th><th>Trữ trước</th><th>Bổ sung TB</th><th>Lãi kỳ vọng (nghìn đ)</th><th>Phiên hết hàng</th><th>Thừa TB</th></tr>{dong_pa}</table></div>', unsafe_allow_html=True)
        if kq_live["cu"] > 0:
            # truc ngang theo vung ra quyet dinh: he so that co duoi rat dai, ve het thi vung quanh Q bi ep lai (da gap khi chup that)
            dl = C.duong_lai_live(float(nen_live), kq_live["cu"], kq_live["co"], gd_live, s.lv_ng, float(max(2.5 * nv["q"], 1.5 * pa["trung_binh"]["q"], 2 * pa["ngay_thuong"]["q"])))
            moc_q = pd.DataFrame({"q": [pa["ngay_thuong"]["q"], pa["trung_binh"]["q"], nv["q"]], "ten": ["Ngày thường", "Trung bình", "Newsvendor"], "dong": [2, 18, 34]})    # 3 dong khac nhau: cac vach co the rat gan nhau
            moc_q = moc_q[moc_q.q <= dl.q.max()]
            truc = alt.X("q:Q", title=f"Lượng trữ trước phiên ({r.don_vi})", axis=alt.Axis(format=",.0f", grid=False))
            cao_q, thap_q = float(dl.lai.max()), float(dl.lai.min())
            duong_q = alt.Chart(dl).mark_line(color=C.C_AI, strokeWidth=2).encode(x=truc, y=alt.Y("lai:Q", title="Lãi kỳ vọng 1 phiên (đ)", scale=alt.Scale(domain=[thap_q, cao_q + 0.4 * max(cao_q - thap_q, 1)], nice=False), axis=alt.Axis(format=",.0f")))     # chua cho 3 dong nhan phia tren
            diem_q = alt.Chart(dl).mark_circle(opacity=0, size=220).encode(x="q:Q", y="lai:Q", tooltip=[alt.Tooltip("q:Q", title="Trữ", format=",.0f"), alt.Tooltip("lai:Q", title="Lãi kỳ vọng (đ)", format=",.0f")])
            vach_q = alt.Chart(moc_q).mark_rule(color=C.MUC2, strokeDash=[4, 3]).encode(x="q:Q")
            nhan_q = alt.Chart(moc_q).mark_text(align="left", dx=4, baseline="top", color=C.MUC, angle=0, fontSize=12).encode(x="q:Q", y=alt.Y("dong:Q", scale=None), text="ten:N")
            C.ve_bd(alt.layer(vach_q, duong_q, diem_q, nhan_q).properties(height=230))
            chenh = pa["hai_buoc_2"]["lai"] - nv["lai"]
            C.ghi(f"mỗi điểm trên đường là lãi kỳ vọng nếu trữ đúng lượng đó, tính trên {vn(LIVE.SO_PHIEN_DO_NHAY, 0)} phiên giả lập độc lập. " + (f"Mức nền {vn(nen_live, 0)} {r.don_vi}/ngày đo từ {LIVE.CUA_SO_NEN} ngày trước {ngay_vn(t)}, không tính ngày khuyến mãi; " if nen_do is not None else f"Mức nền {vn(nen_live, 0)} {r.don_vi}/ngày do bạn nhập, chưa đo được từ dữ liệu; ") + f"{mo_ta_deal}.",
                  f"với các giả định đang chọn, bổ sung theo giờ {'gần như không đổi lãi' if abs(chenh) < 0.01 * max(abs(nv['lai']), 1) else ('tăng lãi' if chenh > 0 else 'giảm lãi')} so với chỉ trữ một lần ({C.dau_cong(chenh / 1e3, 1)} nghìn đ/phiên). "
                  f"Newsvendor thắng ở đây là tất yếu vì tính trên chính phân phối giả định; kết quả thử trên số thật ở docs/10 mục 10.9, 10.10.")

    if kq_live["cu"] > 0:
        C.muc("Phát lại một phiên", "từng giờ, hệ thống chỉ thấy số liệu đến giờ đó")
        a1, a2, a3 = st.columns([1.2, 1, 1], vertical_alignment="bottom")
        kieu = a1.segmented_control("Kiểu phiên", ["Lên xu hướng", "Bình thường"], default="Lên xu hướng", key="lv_kieu") or "Lên xu hướng"
        s.setdefault("lv_hat", 1)
        s.setdefault("lv_gio", 6)
        if a2.button("Phiên khác", key="lv_khac"):
            s.lv_hat += 1
            s.lv_gio = 3
        tu_chay = a3.toggle("Tự chạy", key="lv_chay", help="Mỗi giây sang 1 giờ của phiên.")
        ban_dau = C.phat_lai_live(float(nen_live), float(pa["hai_buoc_2"]["q"]), float(r.gia_ban), float(r.gia_von), float(r.ty_le_chi_phi_luu_kho), s.lv_ht, gd_live, s.lv_ng, kieu == "Lên xu hướng", 20261200 + int(s.lv_hat))
        H_live = gd_o.so_gio
        du_kien = float(nen_live) * gd_o.quy_mo * float(np.median(mau_deal)) * (1 - gd_o.huy_don) * LIVE.he_so_gia(gd_o)    # trung vi: vai tuan rat cao keo trung binh len

        @st.fragment(run_every="1s" if tu_chay else None)
        def khung_phat_lai():
            if tu_chay and s.lv_gio < H_live:
                s.lv_gio += 1
            s["_lv_gio_w"] = s.lv_gio
            st.slider("Đang ở cuối giờ thứ", 1, H_live, key="_lv_gio_w", on_change=lambda: s.update(lv_gio=s["_lv_gio_w"]))
            h = int(s.lv_gio)
            da = ban_dau[ban_dau.gio <= h]
            b = da.iloc[-1]
            dat_da = da[da.dat > 0]
            C.o_hang([("Nhu cầu đến giờ này", vn(b.nhu_cau_cd, 0), f"dự kiến phiên thường {vn(du_kien * h / H_live, 0)}", False),
                      ("Đã bán", vn(b.ban_cd, 0), r.don_vi, False),
                      ("Mất bán", vn(b.nhu_cau_cd - b.ban_cd, 0), "do hết hàng", False),
                      ("Đã đặt bổ sung", vn(dat_da.dat.sum(), 0), f"{len(dat_da)} lần" if len(dat_da) else "chưa đặt", False)])
            dai = pd.DataFrame({"gio": list(da.gio) * 3, "gia_tri": list(da.nhu_cau_cd) + list(da.hang_co) + [du_kien * g / H_live for g in da.gio],
                                "chuoi": ["Nhu cầu cộng dồn"] * len(da) + ["Hàng đã có"] * len(da) + ["Dự kiến phiên thường"] * len(da)})
            mau_lv = alt.Scale(domain=["Nhu cầu cộng dồn", "Hàng đã có", "Dự kiến phiên thường"], range=[C.C_THUC_TE, C.C_AI, C.MUC2])
            tran_y = float(max(ban_dau.nhu_cau_cd.max(), ban_dau.hang_co.max(), du_kien)) * 1.05
            bd = alt.Chart(dai).mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=28)).encode(
                x=alt.X("gio:Q", title="Giờ của phiên", scale=alt.Scale(domain=[1, H_live]), axis=alt.Axis(grid=False, tickMinStep=1, format="d")),
                y=alt.Y("gia_tri:Q", title=r.don_vi, scale=alt.Scale(domain=[0, tran_y]), axis=alt.Axis(format=",.0f")),
                color=alt.Color("chuoi:N", scale=mau_lv, title=None, legend=alt.Legend(orient="top")),
                strokeDash=alt.condition(alt.datum.chuoi == "Dự kiến phiên thường", alt.value([5, 3]), alt.value([1, 0])),
                tooltip=[alt.Tooltip("gio:Q", title="Giờ"), alt.Tooltip("chuoi:N", title="Đường"), alt.Tooltip("gia_tri:Q", title="Số lượng", format=",.0f")])
            C.ve_bd(bd.properties(height=260))
            if len(dat_da):
                d0 = dat_da.iloc[-1]
                st.markdown(f'<div class="dao-mau">Cuối giờ {int(d0.gio)}: đặt thêm <b>{vn(d0.dat, 0)} {r.don_vi}</b>, về đầu giờ {int(d0.gio) + gd_o.gio_ve + 1}.</div>', unsafe_allow_html=True)
            elif h >= H_live:
                st.markdown('<div class="dao-mau">Hết phiên, hệ thống không cần đặt bổ sung.</div>', unsafe_allow_html=True)
            st.caption("Phiên giả lập theo giả định, không phải phiên thật. Khi đã hết hàng, hệ thống chỉ thấy số đã bán nên giữ tốc độ cao nhất đã thấy; đường nhu cầu ở đây để minh họa. "
                       "Kết nối đơn thật từ sàn là hướng phát triển.")

        khung_phat_lai()
