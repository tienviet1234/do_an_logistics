"""Man Hom nay: viec can lam trong ngay lap phieu. 4 o trang thai (bam de loc cheo dai ca nam va danh sach theo doi),
cac dong don can duyet (Duyet / Sua / Bo qua, chi giu trong phien), tai phieu dat hang theo nha cung cap,
dai ca nam (bam 1 ngay de doi ngay lap phieu), danh sach theo doi (bam 1 dong de mo man Mat hang)."""
import altair as alt
import pandas as pd
import streamlit as st

import chung as C
from chung import ngay_vn, vn

s = st.session_state
cs = s.cs
t, nghi = C.ngay_lam_viec()
p = C.sku_loc()
m = C.mo_phong(cs)
F, t0 = C.du_bao_dot(cs)
i_ngay = (pd.Timestamp(t) - t0).days
x = m[(m.ngay == t) & m.ma_sku.isin(p.ma_sku)].merge(p, on="ma_sku")
x["d_tb"] = x.ma_sku.map(lambda ma: F[ma][min((i_ngay + 1) // C.HORIZON, F[ma].shape[0] - 1)].mean())   # du bao 1 ngay
x["du_ban"] = x.ton_cuoi / x.d_tb.where(x.d_tb > 0)
dem = x.tt.value_counts()
NHAN = ["Hết hàng, mất bán", "Đặt hàng hôm nay", "Dưới ROP, hàng đang về", "Đủ hàng"]

if nghi:
    st.info(nghi)
if p.empty:
    st.warning("Không có mã nào khớp bộ lọc nhóm ABC / XYZ ở đầu phiếu.")
    st.stop()

# ------------------------------------------------------------------ 4 o trang thai (loc cheo)
C.muc(f"Tình trạng cuối ngày {ngay_vn(t)}", f"{C.mo_ta_loc()} · bấm một ô để lọc dải cả năm và danh sách theo dõi",
      dau_tien=True)
for i, col in enumerate(st.columns(4)):
    dang_loc = s.loc_tt == i
    with col.container(key=f"tt_{i}{'_on' if dang_loc else ''}"):
        if st.button(f"**{int(dem.get(i, 0))}** {NHAN[i]}{' · đang lọc' if dang_loc else ''}", key=f"b_tt_{i}",
                     use_container_width=True, help="Bấm để lọc theo trạng thái này; bấm lại để bỏ lọc."):
            s.loc_tt = None if dang_loc else i
            st.rerun()


# ------------------------------------------------------------------ don can duyet
QD = {"Duyệt": "duyet", "Sửa": "sua", "Bỏ qua": "bo"}
QD_NGUOC = {v: k for k, v in QD.items()}


def dat_qd(k, qd, sl):
    s.qd[k] = {"qd": qd, "sl": sl}


def doi_qd(k, de_xuat):
    """O chon Duyet / Sua / Bo qua cua 1 dong; bam lai lua chon dang chon = hoan tac."""
    v = QD.get(s[f"qd_{k}"])
    if v is None:
        s.qd.pop(k, None)
    else:
        dat_qd(k, v, 0.0 if v == "bo" else s.qd.get(k, {}).get("sl", de_xuat) if v == "sua" else de_xuat)


def sua_sl(k):
    s.qd[k]["sl"] = float(s[f"sl_{k}"])


trai, phai = st.columns([1.85, 1], gap="large")
don = x[x.tt == 1].sort_values("du_ban")
with trai:
    C.muc("Đơn cần duyệt", f"{len(don)} dòng hệ thống đề xuất · {C.CS_NGAN[cs]}")
    if don.empty:
        st.markdown(f'{C.dau_tt(3)}&nbsp; Không có mã nào phải đặt trong ngày này.', unsafe_allow_html=True)
    for r in don.itertuples():
        k = f"{t}|{cs}|{r.ma_sku}"
        d = s.qd.get(k, {})
        qd = d.get("qd")
        sl = d.get("sl", r.dat_hang)
        ip = r.ton_cuoi + r.dang_ve - r.dat_hang
        with st.container(key=f"don_{r.ma_sku}_{qd or 'cho'}"):
            a, b, c = st.columns([3.6, 3.7, 3.2], vertical_alignment="center")
            a.markdown(f'<span class="don-ma">{r.ma_sku}</span> <span class="don-ten">{r.ten_sku}</span>'
                       f'<div class="don-phu">{r.ma_ncc} · chờ hàng ~{vn(r.lead_time_tb, 0)} ngày · đủ bán {vn(r.du_ban)} ngày<br>'
                       f'Trong kho {vn(r.ton_cuoi, 0)} + đang về {vn(ip - r.ton_cuoi, 0)} = {vn(ip, 0)} ≤ ROP {vn(r.rop, 0)}'
                       f'</div>', unsafe_allow_html=True)
            b.markdown(f'<div class="don-so"><div><span>Trong kho</span><b>{vn(r.ton_cuoi, 0)}</b></div>'
                       f'<div><span>Đang về</span><b>{vn(ip - r.ton_cuoi, 0)}</b></div><div><span>ROP</span><b>{vn(r.rop, 0)}</b></div>'
                       f'<div><span>Đặt ({r.don_vi})</span><b class="quang">{vn(sl, 0)}</b></div></div>', unsafe_allow_html=True)
            with c:
                s[f"qd_{k}"] = QD_NGUOC.get(qd)
                st.segmented_control("Quyết định", list(QD), key=f"qd_{k}", on_change=doi_qd, args=(k, r.dat_hang),
                                     label_visibility="collapsed",
                                     help="Duyệt: đặt đúng đề xuất · Sửa: đổi số lượng · Bỏ qua: không đặt. Bấm lại để hoàn tác.")
                if qd == "sua":
                    st.number_input(f"Số lượng đặt ({r.don_vi})", min_value=0.0, value=float(sl), step=float(r.moq),
                                    format="%.0f", key=f"sl_{k}", on_change=sua_sl, args=(k,),
                                    help=f"Đề xuất {vn(r.dat_hang, 0)}; MOQ {vn(r.moq, 0)}.")
                if qd:
                    st.markdown(C.dau(*C.QD_DAU[qd], moi=True), unsafe_allow_html=True)
            if a.button("Xem mặt hàng", key=f"xem_{k}", type="tertiary"):
                s.sku = r.ma_sku
                st.switch_page("trang/mat_hang.py")

    if not don.empty:
        qd_ngay = {r.ma_sku: s.qd.get(f"{t}|{cs}|{r.ma_sku}") for r in don.itertuples()}
        dat = don.assign(qd=don.ma_sku.map(lambda ma: (qd_ngay[ma] or {}).get("qd")),
                         sl=don.apply(lambda r: (qd_ngay[r.ma_sku] or {}).get("sl", r.dat_hang), axis=1))
        ok = dat[dat.qd.isin(["duyet", "sua"]) & (dat.sl > 0)]
        cho = dat[dat.qd.isna()]
        st.write("")
        C.o_hang([("Chờ duyệt", f"{len(cho)}", "dòng", False), ("Đã duyệt / sửa", f"{len(ok)}", "dòng", False),
                  ("Bỏ qua", f"{int((dat.qd == 'bo').sum())}", "dòng", False),
                  ("Giá trị phiếu (giá vốn)", f"{vn((ok.sl * ok.gia_von).sum() / 1e6)}", "triệu đồng", False)])
        st.write("")
        h1, h2, _ = st.columns([1.3, 1.5, 1.4])
        if h1.button(f"Duyệt {len(cho)} dòng còn lại", disabled=cho.empty, use_container_width=True):
            for r in cho.itertuples():
                dat_qd(f"{t}|{cs}|{r.ma_sku}", "duyet", r.dat_hang)
            st.rerun()
        po = ok.assign(ngay_ve=lambda f: [ngay_vn(pd.Timestamp(t) + pd.Timedelta(days=round(v))) for v in f.lead_time_tb])
        po = po.sort_values(["ma_ncc", "ma_sku"])[["ma_ncc", "ma_sku", "ten_sku", "sl", "don_vi", "gia_von", "ngay_ve", "qd"]]
        po = po.assign(thanh_tien=po.sl * po.gia_von, qd=po.qd.map({"duyet": "Duyệt", "sua": "Đã sửa số lượng"}))
        po.columns = ["Nhà cung cấp", "Mã hàng", "Tên hàng", "Số lượng", "Đơn vị", "Giá vốn (đ)", "Dự kiến về (theo lead time TB)",
                      "Quyết định", "Thành tiền (đ)"]
        h2.download_button(f"Tải phiếu đặt hàng ({po['Nhà cung cấp'].nunique()} nhà cung cấp)", type="primary",
                           data=po.to_csv(index=False).encode("utf-8-sig"), disabled=po.empty, use_container_width=True,
                           file_name=f"phieu_dat_hang_KH-{t.replace('-', '')[2:]}.csv", mime="text/csv",
                           help="CSV mở bằng Excel: các dòng đã duyệt / sửa, xếp theo nhà cung cấp.")
        st.caption("Quyết định chỉ giữ trong phiên làm việc (không ghi vào CSDL). Chưa ước tính số chuyến xe: dữ liệu chưa có "
                   "thể tích / trọng lượng từng mã.")

# ------------------------------------------------------------------ dai ca nam (bam de doi ngay)
with phai:
    C.muc("Cả năm kiểm tra", "bấm một ngày để lập phiếu ngày đó")
    # 1 bieu do 1 lop (Streamlit 1.45 chi cho chon tren bieu do 1 lop): moi ngay 1 cot phu kin chieu cao de bam o dau cung
    # duoc; phan tren cot trong suot, rieng ngay dang xem to dam -> vach "hom nay"
    a = m[m.ma_sku.isin(p.ma_sku) & (m.tt < 3)].groupby(["ngay", "tt"]).size().rename("so").reset_index()
    mo = pd.DataFrame({"ngay": C.ngay_mo_cua(cs)})
    a = mo.merge(a, on="ngay", how="left").fillna({"tt": 0, "so": 0})
    tran = max(1, a.groupby("ngay").so.sum().max()) * 1.04
    a = a.sort_values(["ngay", "tt"])
    a["y1"] = a.groupby("ngay").so.cumsum()
    a["y0"] = a.y1 - a.so
    tong = a.groupby("ngay").so.sum()
    phu = pd.DataFrame({"ngay": tong.index, "tt": 9, "so": 0, "y0": tong.values, "y1": tran})
    a = pd.concat([a[a.so > 0], phu])
    a["nhom"] = a.tt.map(dict(enumerate(C.TRANG_THAI[:3])))
    a.loc[a.tt == 9, "nhom"] = "_"
    a.loc[(a.tt == 9) & (a.ngay == t), "nhom"] = "Ngày đang xem"
    a["tong"] = a.ngay.map(tong)
    a["d"] = pd.to_datetime(a.ngay)
    a["d2"] = a.d + pd.Timedelta(days=1)
    sel = alt.selection_point(name="chon_ngay", fields=["ngay"], on="click", empty=False)
    mien = C.TRANG_THAI[:3] + ["Ngày đang xem", "_"]
    sang = (alt.datum.tt == s.loc_tt) | (alt.datum.tt == 9) if s.loc_tt in (0, 1, 2) else alt.datum.tt >= 0
    cot = alt.Chart(a).mark_rect().encode(
        x=alt.X("d:T", title=None, axis=alt.Axis(format="%m/%y", labelAngle=0, tickCount=6, grid=False)), x2="d2:T",
        y=alt.Y("y0:Q", title="Số mã cần chú ý", scale=alt.Scale(domain=[0, tran], nice=False)), y2="y1:Q",
        color=alt.Color("nhom:N", title=None, scale=alt.Scale(domain=mien, range=C.C_TT + [C.MUC, "transparent"]),
                        legend=alt.Legend(orient="top", direction="vertical", values=mien[:4])),
        opacity=alt.condition(sang, alt.value(1), alt.value(0.18)),
        tooltip=[alt.Tooltip("d:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("tong:Q", title="Mã cần chú ý")]
    ).add_params(sel)
    ev = st.altair_chart(C.theo_du_lieu(cot.properties(height=360), cs, t, s.abc, s.xyz), use_container_width=True,
                         on_select="rerun", selection_mode="chon_ngay",
                         key=f"dai_nam_{cs}_{t}_{''.join(s.abc)}_{''.join(s.xyz)}")   # du lieu doi -> khoa doi (tranh loi Vega "Unrecognized data set")
    v = C.chon_tu_bieu_do(ev, "chon_ngay", "ngay", "_dai_nam_cu")
    if v:
        C.doi_ngay(v)
    tb_dat = a[a.tt == 1].groupby("ngay").so.sum().reindex(C.ngay_mo_cua(cs)).fillna(0)
    nhieu = tb_dat.idxmax()
    C.ghi("mỗi cột là một ngày làm việc, cao = số mã cần chú ý; cột đen là ngày đang lập phiếu.",
          f"trung bình mỗi ngày {vn(tb_dat.mean())} mã phải đặt; nhiều nhất {ngay_vn(nhieu)} ({int(tb_dat.max())} mã).")

# ------------------------------------------------------------------ danh sach theo doi (bam dong -> man Mat hang)
loc = s.loc_tt
td = x[(x.tt == loc) if loc is not None else (x.tt < 3)].sort_values(["tt", "du_ban"])
C.muc("Danh sách theo dõi", (f"lọc: {NHAN[loc]}" if loc is not None else "mọi mã cần chú ý") + " · bấm một dòng để mở mặt hàng")
td = td.assign(trang_thai=td.tt.map(dict(enumerate(C.TRANG_THAI))))
bang = td[["trang_thai", "ma_sku", "ten_sku", "ton_cuoi", "dang_ve", "rop", "dat_hang", "du_ban", "lead_time_tb", "don_vi"]]
ev = st.dataframe(bang, hide_index=True, use_container_width=True, height=min(420, 38 + 35 * max(len(bang), 1)),
                  on_select="rerun", selection_mode="single-row", key=f"bang_td_{t}_{cs}_{loc}", column_config={
                      "trang_thai": st.column_config.TextColumn("Trạng thái", width="medium"),
                      "ma_sku": st.column_config.TextColumn("Mã", width="small"),
                      "ten_sku": st.column_config.TextColumn("Tên hàng", width="large"),
                      "ton_cuoi": st.column_config.NumberColumn("Trong kho", format="%.0f"),
                      "dang_ve": st.column_config.NumberColumn("Đang về", format="%.0f"),
                      "rop": st.column_config.NumberColumn("ROP", format="%.0f", help="Điểm đặt hàng"),
                      "dat_hang": st.column_config.NumberColumn("Đề xuất đặt", format="%.0f"),
                      "du_ban": st.column_config.NumberColumn("Đủ bán (ngày)", format="%.1f"),
                      "lead_time_tb": st.column_config.NumberColumn("Chờ hàng (ngày)", format="%.0f"),
                      "don_vi": st.column_config.TextColumn("Đơn vị", width="small")})
if bang.empty:
    st.markdown(f'{C.dau_tt(3)}&nbsp; Không có mã nào ở trạng thái này trong ngày.', unsafe_allow_html=True)
dong = ev.selection.rows if ev else []
if dong:
    r = bang.iloc[dong[0]]
    c1, c2 = st.columns([3, 1.2], vertical_alignment="center")
    c1.markdown(f'Đã chọn <span class="don-ma">{r.ma_sku}</span> {r.ten_sku}', unsafe_allow_html=True)
    if c2.button("Mở phiếu mặt hàng", type="primary", use_container_width=True):
        s.sku = r.ma_sku
        st.switch_page("trang/mat_hang.py")
with st.expander("Giải thích các cột"):
    st.markdown(
        "- **Trong kho:** số lượng thực có trong kho cuối ngày.\n"
        "- **Đang về:** hàng đã đặt nhà cung cấp nhưng chưa nhận (tính cả đơn đặt hôm nay).\n"
        "- **ROP (điểm đặt hàng)** = nhu cầu dự báo trong thời gian chờ hàng + tồn kho an toàn (SS). "
        "Nếu *trong kho + đang về* (chưa tính đơn hôm nay) ≤ ROP thì đặt thêm.\n"
        "- **Đề xuất đặt:** bội số của lượng đặt kinh tế (EOQ), tối thiểu MOQ.\n"
        "- **Đủ bán (ngày):** trong kho ÷ nhu cầu dự báo 1 ngày. Nhỏ hơn *Chờ hàng* mà không có hàng đang về thì có nguy cơ hết.\n"
        "- **Chờ hàng (ngày):** thời gian giao hàng trung bình của nhà cung cấp (lead time).")
