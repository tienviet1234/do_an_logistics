"""Man Hom nay: viec can lam trong ngay lap phieu. 4 o trang thai (bam de loc cheo dai ca nam va danh sach theo doi),
cac dong don can duyet (Duyet / Sua / Bo qua, chi giu trong phien), tai phieu dat hang theo nha cung cap, bang so sanh ngay
nay voi trung binh ca nam, lich 12 thang (bam 1 ngay de doi ngay lap phieu) + so trung binh theo thang,
danh sach theo doi (bam 1 dong de mo man Mat hang)."""
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
F, t0, buoc = C.du_bao_dot(cs)
i_ngay = (pd.Timestamp(t) - t0).days
x = m[(m.ngay == t) & m.ma_sku.isin(p.ma_sku)].merge(p, on="ma_sku")
x["d_tb"] = x.ma_sku.map(lambda ma: F[ma][min((i_ngay + 1) // buoc, F[ma].shape[0] - 1)].mean())   # du bao 1 ngay (dot dang dung)
x["du_ban"] = x.ton_cuoi / x.d_tb.where(x.d_tb > 0)
dem = x.tt.value_counts()
NHAN = ["Hết hàng, mất bán", "Đặt hàng hôm nay", "Dưới ROP, hàng đang về", "Đủ hàng"]

if nghi:
    st.info(nghi)
if p.empty:
    st.warning("Không có mã nào khớp bộ lọc nhóm ABC / XYZ ở đầu phiếu.")
    st.stop()

# ------------------------------------------------------------------ 4 o trang thai (loc cheo)
C.muc(f"Tình trạng cuối ngày {ngay_vn(t)}", f"{C.mo_ta_loc()} · bấm một ô để lọc lịch cả năm và danh sách theo dõi",
      dau_tien=True)
for i, col in enumerate(st.columns(4)):
    dang_loc = s.loc_tt == i
    with col.container(key=f"tt_{i}{'_on' if dang_loc else ''}"):
        st.button(f"**{int(dem.get(i, 0))}** {NHAN[i]}{' · đang lọc' if dang_loc else ''}", key=f"b_tt_{i}",
                  use_container_width=True, help="Bấm để lọc theo trạng thái này; bấm lại để bỏ lọc.",
                  on_click=lambda v=(None if dang_loc else i): s.update(loc_tt=v))


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

# ------------------------------------------------------------------ so lieu tung ngay trong nam (theo bo loc nhom)
mo_cua = set(C.ngay_mo_cua(cs))
lich = (m[m.ma_sku.isin(p.ma_sku)].groupby(["ngay", "tt"]).size().unstack(fill_value=0).reindex(columns=range(4), fill_value=0)
        .rename(columns={0: "het", 1: "dat", 2: "ve", 3: "du"}).rename_axis(columns=None))
ca_ky = pd.date_range(min(mo_cua), max(mo_cua)).strftime("%Y-%m-%d")      # ca ngay kho nghi (mo phong khong co dong): van hien o tren lich
lich = lich.reindex(ca_ky, fill_value=0).rename_axis("ngay").reset_index()
lich["xl"] = lich.het + lich.dat
lam = lich[lich.ngay.isin(mo_cua)]
hom = lich[lich.ngay == t].iloc[0]
sau_kd = lam[lam.ngay >= (pd.Timestamp(lam.ngay.min()) + pd.Timedelta(days=C.NGAY_KHOI_DONG)).strftime("%Y-%m-%d")]   # bo giai doan khoi dong

# ------------------------------------------------------------------ ngay nay so voi binh thuong
with phai:
    C.muc("So với bình thường", f"ngày {ngay_vn(t)} và trung bình cả năm")
    dong = "".join(
        f'<tr><td>{C.icon(ic)} {ten}</td><td><b>{int(hom[c])}</b></td><td>{vn(lam[c].mean())}</td></tr>'
        for ten, c, ic in [("Hết hàng", "het", "het"), ("Phải đặt hôm nay", "dat", "dat"), ("Dưới ROP, hàng đang về", "ve", "ve"), ("Đủ hàng", "du", "du")])
    st.markdown(f'<table class="phieu"><tr><th>Số mã hàng</th><th>Ngày này</th><th>TB năm</th></tr>{dong}'
                f'<tr class="chon"><td>Phải xử lý (hết + đặt)</td><td>{int(hom.xl)}</td><td>{vn(lam.xl.mean())}</td></tr></table>',
                unsafe_allow_html=True)
    C.ghi("trung bình tính trên các ngày kho mở cửa, theo bộ lọc nhóm hàng đang chọn.",
          f"ngày này nhiều việc hơn {vn(100 * (lam.xl < hom.xl).mean(), 0)}% số ngày làm việc trong năm.")
    st.write("")
    for k, (ten, c) in enumerate([("nhiều việc nhất", "xl"), ("nhiều mã hết hàng nhất", "het")]):
        r = sau_kd.loc[sau_kd[c].idxmax()]
        st.button(f"Xem ngày {ten}: {ngay_vn(r.ngay)} ({int(r[c])} mã)", key=f"nhay_{k}", use_container_width=True, disabled=r.ngay == t,
                  on_click=C.dat_ngay, args=(r.ngay,))

# ------------------------------------------------------------------ ca nam: lich chon ngay + so trung binh theo thang
TEN_DO = ["số mã hết hàng", "số mã phải đặt", "số mã dưới ROP, hàng đang về", "số mã đủ hàng"]
do = "xl" if s.loc_tt is None else ["het", "dat", "ve", "du"][s.loc_tt]
ten_do = "số mã phải xử lý (hết hàng + phải đặt)" if s.loc_tt is None else TEN_DO[s.loc_tt]
lop = C.chia_lop_mau(lam[do])
mau_lop = C.C_LICH[-len(lop):] if lop else []
nhan_lop = [f"{a}" if a == b else f"{a}–{b}" for a, b in lop]


def nhom_o(r):
    if r.ngay == t:
        return "Ngày đang xem"
    if r.ngay not in mo_cua:
        return "Kho nghỉ"
    return next((n for n, (a, b) in zip(nhan_lop, lop) if a <= r[do] <= b), "0")


su_kien = C.q("SELECT ngay, ghi_chu FROM lich_su_kien")
su_kien = su_kien.assign(ghi_chu=su_kien.ghi_chu.str.split(" (", regex=False).str[0]).groupby("ngay").ghi_chu.agg("; ".join)
THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]
d = pd.to_datetime(lich.ngay)
lich = lich.assign(ngay_so=d.dt.day, thang=d.dt.strftime("%m/%Y"), nhom=lich.apply(nhom_o, axis=1), su_kien=lich.ngay.map(su_kien).fillna("Không có"),
                   ngay_chu=[f"{THU[v.weekday()]}, {v.strftime('%d/%m/%Y')}" for v in d],
                   tinh_trang=[("Kho mở cửa" if v in mo_cua else "Kho nghỉ") for v in lich.ngay])
cac_thang = list(dict.fromkeys(lich.thang))
# lich va 2 bieu do cot cung chieu cao + cung truc duoi (cot: chu trong suot) -> hang cua tung thang thang nhau
CAO_BD = 28 * len(cac_thang) + 50
truc_thang = alt.Y("thang:O", title=None, sort=cac_thang, scale=alt.Scale(paddingInner=0.1),
                   axis=alt.Axis(ticks=False, domain=False, labelPadding=6, labelOverlap=False))
C.muc("Cả năm kiểm tra", "bấm một ô trên lịch để lập phiếu ngày đó · rê chuột để xem số của ngày")
c_lich, c_het, c_dat = st.columns([3.3, 1, 1], gap="medium")
with c_lich:
    st.markdown(f'<div class="nhan-bd"><b>Lịch 12 tháng</b><span>càng đậm càng nhiều {ten_do}</span></div>', unsafe_allow_html=True)
    mien = ["Kho nghỉ", "0"] + nhan_lop + ["Ngày đang xem"]
    mau_mien = [C.C_KHO_NGHI, C.C_KHONG] + mau_lop + [C.QUANG]
    sel = alt.selection_point(name="chon_ngay", fields=["ngay"], on="click", empty=False)
    dang_xem = alt.datum.nhom == "Ngày đang xem"
    o = alt.Chart(lich).mark_rect(cornerRadius=2).encode(
        x=alt.X("ngay_so:O", title="Ngày trong tháng", scale=alt.Scale(domain=list(range(1, 32)), paddingInner=0.1),
                axis=alt.Axis(values=[1, 5, 10, 15, 20, 25, 31], labelAngle=0, ticks=False, domain=False)),
        y=truc_thang,
        color=alt.Color("nhom:N", scale=alt.Scale(domain=mien, range=mau_mien), legend=None),
        stroke=alt.condition(dang_xem, alt.value(C.MUC), alt.value("transparent")),
        strokeWidth=alt.condition(dang_xem, alt.value(2), alt.value(0)),
        tooltip=[alt.Tooltip("ngay_chu:N", title="Ngày"), alt.Tooltip("tinh_trang:N", title="Tình trạng"),
                 alt.Tooltip("het:Q", title="Hết hàng"), alt.Tooltip("dat:Q", title="Phải đặt"), alt.Tooltip("ve:Q", title="Dưới ROP, hàng đang về"),
                 alt.Tooltip("du:Q", title="Đủ hàng"), alt.Tooltip("su_kien:N", title="Sự kiện")]
    ).add_params(sel).properties(height=CAO_BD)
    khoa_lich = f"dai_nam_{cs}_{t}_{''.join(s.abc)}_{''.join(s.xyz)}_{s.loc_tt}"          # du lieu doi -> khoa doi
    C.ve_bd(o, selection_mode="chon_ngay", key=khoa_lich,
            on_select=lambda: C.khi_chon_ngay(khoa_lich))
    st.markdown('<div class="chu-giai">' + "".join(
        f'<span><svg width="13" height="13" aria-hidden="true"><rect x="1" y="1" width="11" height="11" rx="2" fill="{mau}"'
        f'{f" stroke={chr(34)}{C.MUC}{chr(34)}" if ten_mau == "Ngày đang xem" else ""}/></svg> {ten_mau}</span>'
        for ten_mau, mau in zip(mien, mau_mien)) + "</div>", unsafe_allow_html=True)

theo_thang = lam.assign(thang=pd.to_datetime(lam.ngay).dt.strftime("%m/%Y")).groupby("thang")[["het", "dat"]].mean().reindex(cac_thang).reset_index()
for cot_st, cot, ten, mau in [(c_het, "het", "Mã hết hàng", C.C_TT[0]), (c_dat, "dat", "Mã phải đặt", C.C_TT[1])]:
    with cot_st:
        st.markdown(f'<div class="nhan-bd"><b>{ten}</b><span>trung bình mỗi ngày</span></div>', unsafe_allow_html=True)
        f = theo_thang.assign(nhan=theo_thang[cot].map(vn))
        goc = alt.Chart(f).encode(y=truc_thang, x=alt.X(f"{cot}:Q", title="Ngày trong tháng", scale=alt.Scale(domain=[0, max(f[cot].max(), 0.1) * 1.45]),
                                                     axis=alt.Axis(values=[0], ticks=False, domain=False, grid=False, labelColor="transparent", titleColor="transparent")))
        cot_bd = (goc.mark_bar(size=15, color=mau, cornerRadiusEnd=3) +
                  goc.mark_text(align="left", dx=5, color=C.MUC, fontWeight=600, fontSize=12).encode(text="nhan:N")).properties(height=CAO_BD)
        C.ve_bd(cot_bd)
dinh = theo_thang.loc[theo_thang.het.idxmax()]
C.ghi("mỗi ô là một ngày, ô vàng là ngày đang lập phiếu, ô xám là ngày kho nghỉ. Bấm ô trạng thái ở đầu màn để lịch chỉ tô theo trạng thái đó.",
      f"cả năm trung bình {vn(lam.dat.mean())} mã phải đặt và {vn(lam.het.mean())} mã hết hàng mỗi ngày; hết hàng cao nhất tháng {dinh.thang} "
      f"({vn(dinh.het)} mã/ngày). {C.NGAY_KHOI_DONG} ngày đầu kỳ là giai đoạn khởi động: tồn đầu kỳ chưa được đặt theo chính sách nên hết hàng cao hơn hẳn.")

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
        "- **Đề xuất đặt:** theo quy tắc của chính sách (chọn trên validation): hàng ổn định (X, Y) đặt bội số của lượng đặt "
        "kinh tế (EOQ); hàng mùa vụ (Z) đặt bù đến mức đủ bán thời gian chờ hàng + 7 ngày + dự phòng; tối thiểu MOQ.\n"
        "- **Đủ bán (ngày):** trong kho ÷ nhu cầu dự báo 1 ngày. Nhỏ hơn *Chờ hàng* mà không có hàng đang về thì có nguy cơ hết.\n"
        "- **Chờ hàng (ngày):** thời gian giao hàng trung bình của nhà cung cấp (lead time).")
