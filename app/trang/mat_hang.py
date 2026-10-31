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
    s.sku = can_dat.ma_sku.iloc[0] if len(can_dat) else (p.ma_sku.iloc[0] if len(p) else "SKU001")
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
    long = pd.concat([y[["d", c]].rename(columns={c: "v"}).assign(chuoi=n) for n, _, c in chuoi])
    mau = alt.Scale(domain=[c[0] for c in chuoi], range=[c[1] for c in chuoi])
    # dung chung: bieu do ton kho + dai trang thai. Mien ngay phai la alt.DateTime: Timestamp bi doi thanh chuoi ISO,
    # Vega-Lite khong hieu -> truc thoi gian hong, bieu do trong (da gap, chi thay khi chup trinh duyet that)
    dau_, cuoi_ = y.d.min(), y.d.max() + pd.Timedelta(days=1)
    thang = alt.Scale(domain=[alt.DateTime(year=dau_.year, month=dau_.month, date=dau_.day),
                              alt.DateTime(year=cuoi_.year, month=cuoi_.month, date=cuoi_.day)])
    truc_x = alt.X("d:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False), scale=thang)
    duong = alt.Chart(long).mark_line(strokeWidth=1.8, interpolate="step-after").encode(
        x=truc_x, y=alt.Y("v:Q", title=r.don_vi), color=alt.Color("chuoi:N", scale=mau, title=None, legend=alt.Legend(orient="top")),
        strokeDash=alt.condition(alt.datum.chuoi == "ROP (điểm đặt hàng)", alt.value([5, 3]), alt.value([1, 0])))
    vach = alt.Chart(y[y.dat_hang > 0]).mark_tick(color=C.HO_PHACH, thickness=2, size=10).encode(
        x="d:T", y=alt.datum(0), tooltip=[alt.Tooltip("d:T", title="Ngày đặt", format="%d/%m/%Y"),
                                            alt.Tooltip("dat_hang:Q", title="Lượng đặt", format=",.0f")])
    gan = alt.selection_point(nearest=True, on="pointerover", fields=["d"], empty=False, clear="pointerout")
    re_ = alt.Chart(y).mark_rule(color=C.MUC2).encode(
        x="d:T", opacity=alt.condition(gan, alt.value(0.6), alt.value(0)),
        tooltip=[alt.Tooltip("d:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("ton_cuoi:Q", title="Tồn cuối", format=",.0f"),
                 alt.Tooltip("rop:Q", title="ROP", format=",.0f")]).add_params(gan)
    vh = alt.Chart(pd.DataFrame({"d": [pd.Timestamp(t)]})).mark_rule(color=C.MUC, strokeWidth=1.5, strokeDash=[3, 2]).encode(x="d:T")
    st.altair_chart(C.theo_du_lieu(alt.layer(duong, vach, re_, vh).properties(height=300), ma, cs, t, so_ht),
                    use_container_width=True)
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
    ev = st.altair_chart(C.theo_du_lieu(dai.properties(height=34), ma, cs, t), use_container_width=True,
                         on_select="rerun", selection_mode="chon_ngay", key=f"dai_{ma}_{cs}_{t}")   # du lieu doi -> khoa doi
    v = C.chon_tu_bieu_do(ev, "chon_ngay", "ngay", f"_dai_cu_{ma}")
    if v:
        C.doi_ngay(v)
    kq = C.q("""SELECT ma_chinh_sach, 100.0 * da_dap_ung / nhu_cau AS fr, so_ngay_thieu, ton_tb, so_lan_nhap
                FROM ket_qua_ton_kho WHERE ma_sku = ? AND ROUND(muc_phuc_vu, 2) = ?""", (ma, C.MAIN)).set_index("ma_chinh_sach")
    C.ghi("đường bậc thang là tồn cuối mỗi ngày (bậc nhảy lên là ngày hàng về); nét đứt là ROP; vạch nhỏ phía dưới là ngày "
          "đặt hàng; vạch đứt dọc là ngày đang xem. Dải màu dưới biểu đồ là trạng thái cuối mỗi ngày của mã: đỏ hết hàng, cam đặt hàng, xanh dương dưới ROP "
          "(hàng đang về), xanh lá đủ hàng, ô đen là ngày đang xem; bấm vào dải để lập phiếu ngày đó.",
          f"cả năm, {C.CS_NGAN[cs]} đáp ứng {vn(kq.fr[cs])}% nhu cầu, {int(kq.so_ngay_thieu[cs])} ngày thiếu, tồn bình quân "
          f"{vn(kq.ton_tb[cs], 0)} {r.don_vi}, nhập {int(kq.so_lan_nhap[cs])} lần. Hiện trạng*: {vn(kq.fr['hien_trang'])}%, "
          f"{int(kq.so_ngay_thieu['hien_trang'])} ngày thiếu, tồn {vn(kq.ton_tb['hien_trang'], 0)}.")

    # -------------------------------------------------------------- du bao so voi thuc te
    C.muc("Dự báo và thực tế", "12 tháng kiểm tra, dự báo làm mới mỗi 28 ngày")
    a1, a2 = st.columns([1, 1.4], vertical_alignment="center")
    gop = a1.segmented_control("Xem theo", ["Tuần", "Ngày"], default="Tuần", key="mh_gop") or "Tuần"
    so_moc = a2.toggle("So với dự báo mốc (TB trượt 28 ngày)", value=True, key="mh_moc")
    cm = C.mo_hinh_chon().ma_mo_hinh
    d = C.q("""SELECT ma_mo_hinh, ngay, du_bao, thuc_te FROM du_bao WHERE tap = 'test' AND ma_sku = ?
               AND ma_mo_hinh IN (?, ?)""", (ma, cm, C.MOC))
    w = d.pivot_table(index="ngay", columns="ma_mo_hinh", values="du_bao").rename(columns={cm: "ai", C.MOC: "moc"})
    w["thuc_te"] = d.drop_duplicates("ngay").set_index("ngay").thuc_te
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
    longs = []
    for c, n, _ in chuoi:
        z = g[["d", c]].rename(columns={c: "v"})
        z["doan"] = z.v.isna().cumsum()                    # ngay khong cham lam dut duong
        longs.append(z.dropna().assign(chuoi=n))
    long = pd.concat(longs)
    mau = alt.Scale(domain=[c[1] for c in chuoi], range=[c[2] for c in chuoi])
    lines = alt.Chart(long).mark_line(strokeWidth=1.8).encode(
        x=alt.X("d:T", title=None, axis=alt.Axis(format="%m/%Y", grid=False)),
        y=alt.Y("v:Q", title=f"{r.don_vi} / {gop.lower()}"), detail="doan:N",
        color=alt.Color("chuoi:N", scale=mau, title=None, legend=alt.Legend(orient="top")),
        strokeDash=alt.condition(alt.datum.chuoi == "Dự báo mốc", alt.value([5, 3]), alt.value([1, 0])))
    gan = alt.selection_point(nearest=True, on="pointerover", fields=["d"], empty=False, clear="pointerout")
    tip = [alt.Tooltip("d:T", title="Tuần từ" if gop == "Tuần" else "Ngày", format="%d/%m/%Y")] + [
        alt.Tooltip(f"{c}:Q", title=n, format=",.0f") for c, n, _ in chuoi]
    rule = alt.Chart(g).mark_rule(color=C.MUC2).encode(
        x="d:T", opacity=alt.condition(gan, alt.value(0.7), alt.value(0)), tooltip=tip).add_params(gan)
    st.altair_chart(C.theo_du_lieu(alt.layer(lines, rule).properties(height=280), ma, gop, so_moc), use_container_width=True)
    C.ghi("rê chuột để xem từng " + ("tuần" if gop == "Tuần" else "ngày") + ". Theo tuần chỉ cộng ngày được chấm.",
          "đường thực tế đứt ở ngày không chấm (kho nghỉ, hết hàng, đơn B2B đột biến). Dự báo chỉ dùng dữ liệu đến ngày lập dự báo.")

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
    st.caption("Chỉ tính lại cho ngày đang xem, không chạy lại mô phỏng cả năm. Ở 95% và không chậm, kết quả trùng đúng mô phỏng. "
               "Hàng về chậm: giả định sai số dự báo tăng theo căn bậc hai số ngày chờ.")

    C.muc("Kết quả cả năm của mã này", "mức phục vụ 95%")
    dong = "".join(f'<tr{" class=chon" if c == cs else ""}><td>{C.CS_NGAN[c]}</td><td>{vn(kq.fr[c])}%</td>'
                   f'<td>{int(kq.so_ngay_thieu[c])}</td><td>{vn(kq.ton_tb[c], 0)}</td></tr>' for c in C.CS_TEN)
    st.markdown(f'<div class="bang-cuon"><table class="phieu"><tr><th>Chính sách</th><th>Fill Rate</th><th>Ngày thiếu</th>'
                f'<th>Tồn TB</th></tr>{dong}</table></div>', unsafe_allow_html=True)
    st.caption(C.NOTE_HT)
