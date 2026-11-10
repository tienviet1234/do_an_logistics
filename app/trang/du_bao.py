"""Man Du bao: du bao 28 ngay CHUA XAY RA tu ngay cuoi cua du lieu (bang du_bao, tap 'tuong_lai'); bam de chay mo hinh ngay
(hoc LightGBM tren toan bo lich su, Prophet cho ma dang xem, ghep theo trong so da chon); giai thich vi sao ra con so (he so nhan
cua tung nhom yeu to, thanh phan Prophet). Lop tinh toan o src/chay_du_bao.py (dung dung ham da kiem chung, co test)."""
import time
from datetime import timedelta

import altair as alt
import pandas as pd
import streamlit as st

import chung as C
from chung import ngay_vn, vn

s = st.session_state
THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]
mh = C.mo_hinh_chon().ma_mo_hinh
sku = C.ds_sku().set_index("ma_sku")
p = C.sku_loc()


@st.cache_data(show_spinner=False)
def doc_tuong_lai(mo_hinh):
    return C.q("""SELECT moc, ngay, ma_sku, du_bao, thap_80, cao_80, thap_95, cao_95 FROM du_bao
                  WHERE tap = 'tuong_lai' AND ma_mo_hinh = ? ORDER BY ma_sku, ngay""", (mo_hinh,))


@st.cache_data(show_spinner=False)
def ban_gan_day(tu):
    return C.q("SELECT ngay, ma_sku, qty_out, la_ngay_nghi FROM giao_dich_sach WHERE ngay > ?", (tu,))


fb = doc_tuong_lai(mh)
if fb.empty:
    st.warning("Chưa có dự báo cho các ngày sau ngày cuối của dữ liệu. Chạy tại thư mục gốc dự án:")
    st.code("python src/du_bao_tuong_lai.py      # bộ mô phỏng\n# nguồn kiểm chứng (M5): xem docs/10 mục 10.15", language="bash")
    st.stop()
fb["ngay"] = pd.to_datetime(fb.ngay)
o = pd.Timestamp(fb.moc.iloc[0])
ngay = sorted(fb.ngay.unique())
DAU = str(C.DB.stat().st_mtime)

# ------------------------------------------------------------------ 1. 28 ngay toi, toan kho (theo bo loc)
C.muc("Dự báo 28 ngày tới", f"đứng ở ngày cuối của dữ liệu {ngay_vn(o)} · các ngày này chưa xảy ra, chưa có số thật để so", dau_tien=True)
st.caption("Màn này luôn đứng ở ngày cuối của dữ liệu, không theo ô “Ngày lập phiếu” ở đầu phiếu (ô đó dùng để giả lập lại các ngày đã qua). "
           f"Bộ lọc nhóm ABC / XYZ vẫn áp dụng: {C.mo_ta_loc()}.")
f_loc = fb[fb.ma_sku.isin(p.ma_sku)]
tong = f_loc.groupby("ngay").du_bao.sum()
ban = ban_gan_day((o - pd.Timedelta(days=56)).strftime("%Y-%m-%d"))
ban["ngay"] = pd.to_datetime(ban.ngay)
ban_loc = ban[ban.ma_sku.isin(p.ma_sku)]
tt = ban_loc.groupby("ngay").qty_out.sum()
dinh = tong.idxmax()
C.o_hang([("Ngày đứng dự báo", ngay_vn(o), "ngày cuối có số thật", False),
          ("Dự báo cho", f"{pd.Timestamp(ngay[0]):%d/%m} – {pd.Timestamp(ngay[-1]):%d/%m/%Y}", "28 ngày chưa xảy ra", False),
          ("Tổng 28 ngày", vn(tong.sum(), 0), f"{len(p)} mã theo bộ lọc", True),
          ("Ngày cao nhất", f"{THU[dinh.weekday()]} {dinh:%d/%m}", vn(tong.max(), 0) + " đơn vị", False),
          ("Mô hình", mh, "được chọn theo luật ghi trước", False)])
gop = pd.concat([pd.DataFrame({"ngay": tt.index, "so": tt.values, "loai": "Số bán thật (đã xảy ra)"}),
                 pd.DataFrame({"ngay": tong.index, "so": tong.values, "loai": "Dự báo (chưa xảy ra)"})])
mau = alt.Scale(domain=["Số bán thật (đã xảy ra)", "Dự báo (chưa xảy ra)"], range=[C.C_THUC_TE, C.C_AI])
truc = alt.X("ngay:T", title=None, axis=alt.Axis(format="%d/%m"))
duong = alt.Chart(gop).mark_line(strokeWidth=2).encode(x=truc, y=alt.Y("so:Q", title="Đơn vị / ngày, toàn kho"),
                                                        color=alt.Color("loai:N", scale=mau, legend=alt.Legend(orient="top", title=None)),
                                                        strokeDash=alt.condition("datum.loai == 'Dự báo (chưa xảy ra)'", alt.value([5, 3]), alt.value([1, 0])),
                                                        tooltip=[alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("loai:N", title=" "),
                                                                 alt.Tooltip("so:Q", title="Đơn vị", format=",.0f")])
vach = alt.Chart(pd.DataFrame({"ngay": [o], "nhan": [f"Hôm nay {o:%d/%m}"]})).mark_rule(color=C.MUC2, strokeDash=[2, 2]).encode(x="ngay:T")
chu = alt.Chart(pd.DataFrame({"ngay": [o], "nhan": [f"ngày đứng dự báo {o:%d/%m}"]})).mark_text(align="left", dx=4, dy=-6, color=C.MUC2, fontSize=11).encode(
    x="ngay:T", y=alt.value(8), text="nhan:N")
C.ve_bd((duong + vach + chu).properties(height=250))
C.ghi("nét liền là số bán thật 8 tuần gần nhất, nét đứt là dự báo 28 ngày tới; vạch dọc là ngày đứng dự báo.",
      f"trung bình dự báo {vn(tong.mean(), 0)} / ngày so với {vn(tt.mean(), 0)} / ngày của 8 tuần qua; "
      f"chủ nhật dự báo bằng {vn(tong[[pd.Timestamp(d).weekday() == 6 for d in tong.index]].mean() / tong[[pd.Timestamp(d).weekday() < 6 for d in tong.index]].mean() * 100, 0)}% ngày thường.")

# ------------------------------------------------------------------ 2. mot ma hang
C.muc("Một mã hàng", "dự báo từng ngày và khoảng có thể xảy ra")
ds = list(f_loc.groupby("ma_sku").du_bao.sum().sort_values(ascending=False).index) or list(fb.ma_sku.unique())
if s.get("db_ma") not in ds:
    s.db_ma = s.sku if s.get("sku") in ds else ds[0]
s["_db_ma_w"] = s.db_ma
st.selectbox("Mặt hàng", ds, key="_db_ma_w", format_func=lambda v: f"{v} · {sku.ten_sku[v]} · nhóm {sku.xyz_train[v]}",
             on_change=lambda: s.update(db_ma=s["_db_ma_w"]), help="Xếp theo tổng dự báo 28 ngày, lớn trước.")
ma = s.db_ma
fm = fb[fb.ma_sku == ma]
bm = ban[ban.ma_sku == ma]
goc = alt.Chart(fm).encode(x=alt.X("ngay:T", title=None, axis=alt.Axis(format="%d/%m")))
d95 = goc.mark_area(color=C.C_AI, opacity=0.10).encode(y=alt.Y("thap_95:Q", title=f"{sku.don_vi[ma]} / ngày"), y2="cao_95:Q")
d80 = goc.mark_area(color=C.C_AI, opacity=0.20).encode(y="thap_80:Q", y2="cao_80:Q")
dbm = goc.mark_line(color=C.C_AI, strokeWidth=2, strokeDash=[5, 3], point=alt.OverlayMarkDef(size=18)).encode(
    y="du_bao:Q", tooltip=[alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("du_bao:Q", title="Dự báo", format=",.1f"),
                           alt.Tooltip("thap_80:Q", title="Khoảng 80% từ", format=",.1f"), alt.Tooltip("cao_80:Q", title="đến", format=",.1f")])
that = alt.Chart(bm).mark_line(color=C.C_THUC_TE, strokeWidth=1.6).encode(x="ngay:T", y="qty_out:Q",
                                                                            tooltip=[alt.Tooltip("ngay:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("qty_out:Q", title="Bán thật")])
C.ve_bd((d95 + d80 + that + dbm + vach).properties(height=240))
C.ghi("đường đen là số bán thật 8 tuần qua; đường xanh đứt là dự báo; dải đậm là khoảng 80%, dải nhạt là 95% "
      "(tính từ sai số mô hình đã mắc ở các lần dự báo trước, cùng nhóm và cùng độ xa).",
      f"tổng 28 ngày dự báo {vn(fm.du_bao.sum(), 0)} {sku.don_vi[ma]}; 8 tuần qua bán trung bình {vn(bm.qty_out.mean() if len(bm) else 0, 1)} / ngày, "
      f"dự báo trung bình {vn(fm.du_bao.mean(), 1)} / ngày.")

# ------------------------------------------------------------------ 3. chay mo hinh ngay
C.muc("Chạy mô hình ngay", "hệ thống học lại từ dữ liệu và tính dự báo cho mã đang xem, từng bước")


@st.cache_resource(show_spinner=False)
def ngu_canh(goc, dau):
    from chay_du_bao import chuan_bi
    return chuan_bi(goc)


@st.cache_resource(show_spinner=False)
def lightgbm(goc, dau):
    from chay_du_bao import hoc_lightgbm
    t0 = time.time()
    fn, _ = hoc_lightgbm(ngu_canh(goc, dau))
    return fn, time.time() - t0


@st.cache_resource(show_spinner=False)
def prophet(goc, dau, ma):
    from chay_du_bao import hoc_prophet_ma
    t0 = time.time()
    return hoc_prophet_ma(ngu_canh(goc, dau), ma), time.time() - t0


s.setdefault("db_kq", {})
khoa = (str(C.GOC_DU_LIEU), DAU, ma)
if st.button(f"Chạy mô hình cho {ma}", type="primary", key="db_chay",
             help="Lần bấm đầu học LightGBM trên toàn bộ lịch sử của mọi mã (khoảng nửa phút đến một phút); các mã sau dùng lại mô hình vừa học."):
    from chay_du_bao import chay_ma, doi_chieu_da_luu
    with st.status("Mô hình đang chạy…", expanded=True) as tt_chay:
        t0 = time.time()
        ctx = ngu_canh(str(C.GOC_DU_LIEU), DAU)
        st.write(f"**1. Đọc dữ liệu đến {ngay_vn(o)}:** {vn(len(ctx['df']), 0)} dòng (mã × ngày) của {ctx['df'].ma_sku.nunique()} mã, "
                 f"từ {ngay_vn(ctx['df'].date.min())}.")
        sk = ctx["ghi"].get("su_kien_tuong_lai") or {}
        st.write(f"**2. Dựng 28 ngày chưa xảy ra** ({ngay_vn(ctx['fut'].date.min())} – {ngay_vn(ctx['fut'].date.max())}) với thông tin biết trước: "
                 "thứ trong tuần, tháng, ngày lễ, Tết, sale, khuyến mãi đã lên lịch"
                 + (f"; sự kiện trong 28 ngày: {', '.join(sk)}." if sk else "; không đoán các sự kiện không biết trước (bão, dịch, thời tiết)."))
        fn, giay = lightgbm(str(C.GOC_DU_LIEU), DAU)
        st.write(f"**3. Học LightGBM** (3 mô hình cho tầm 1–7, 8–14, 15–28 ngày) trên toàn bộ lịch sử: {vn(giay, 0)} giây"
                 + (" (đã học ở lần bấm trước, dùng lại)." if time.time() - t0 < giay else "."))
        m_p, giay_p = prophet(str(C.GOC_DU_LIEU), DAU, ma)
        st.write(f"**4. Học Prophet riêng cho {ma}** (xu hướng, mùa tuần, mùa năm, ngày lễ): {vn(giay_p, 1)} giây.")
        if ctx["kieu"] == "dl":
            st.write("**5. RNN:** dùng bản đã học tiếp mỗi tuần đến ngày cuối (học trên GPU qua cả chuỗi mốc, không học lại khi bấm).")
        kq = chay_ma(ctx, fn, ma, m_p)
        lech = doi_chieu_da_luu(ctx, ma, kq["bang"])
        w = kq["trong_so"]
        st.write(f"**{6 if ctx['kieu'] == 'dl' else 5}. Ghép theo trọng số đã chọn cho nhóm {w['nhom']}** "
                 f"(LightGBM {vn(w['w_lgb'] * 100, 0)}%, Prophet {vn((1 - w['w_lgb']) * 100, 0)}%"
                 + (f"; sau đó RNN {vn(w['w_rnn'] * 100, 0)}%, phần còn lại {vn((1 - w['w_rnn']) * 100, 0)}%" if "w_rnn" in w else "") + ")."
                 + ("" if lech is None else f" So với bản đã lưu trong CSDL: lệch lớn nhất dưới 0,000001 đơn vị (sai số làm tròn của máy) → **trùng**." if lech < 1e-6 else f" So với bản đã lưu: lệch lớn nhất {lech:.3f}."))
        tt_chay.update(label=f"Xong: dự báo 28 ngày cho {ma} trong {vn(time.time() - t0, 0)} giây", state="complete", expanded=False)
    s.db_kq[khoa] = kq

kq = s.db_kq.get(khoa)
if kq is None:
    st.info("Bấm nút ở trên để xem mô hình chạy và phần giải thích vì sao ra con số.")
    st.stop()

# ------------------------------------------------------------------ 4. vi sao ra con so nay
C.muc("Vì sao ra con số này", "chọn một ngày trong 28 ngày tới")
b = kq["bang"]
cac_ngay = [x.strftime("%Y-%m-%d") for x in b.date]                 # chuoi ngay: an toan cho widget (Timestamp lam loi trang thai)
if s.get("db_ngay") not in cac_ngay:
    s.db_ngay = cac_ngay[0]
s["_db_ngay_w"] = s.db_ngay
st.select_slider("Ngày", options=cac_ngay, key="_db_ngay_w", format_func=lambda v: f"{THU[pd.Timestamp(v).weekday()]} {pd.Timestamp(v):%d/%m}",
                 on_change=lambda: s.update(db_ngay=s["_db_ngay_w"]))
d = pd.Timestamp(s.db_ngay)
r = b[b.date == d].iloc[0]
w = kq["trong_so"]
gt = kq["giai_thich"]
g = gt[gt.date == d].iloc[0]
from giai_thich import he_so  # noqa: E402
nen, hs = he_so(g)
dong_cong = (f"{vn(w['w_lgb'] * 100, 0)}% × LightGBM {vn(r.lgb, 1)} + {vn((1 - w['w_lgb']) * 100, 0)}% × Prophet {vn(r.prophet, 1)}")
if "w_rnn" in w:
    st.markdown(f"**Dự báo {d:%d/%m} = {vn(w['w_rnn'] * 100, 0)}% × RNN {vn(r.rnn, 1)} + {vn((1 - w['w_rnn']) * 100, 0)}% × ({dong_cong} = {vn(r.ket_hop, 1)}) "
                f"= {vn(r.du_bao, 1)} {sku.don_vi[ma]}**")
    st.caption("Phần RNN chỉ có con số tổng: mạng nơ-ron không tách được đóng góp theo từng yếu tố như LightGBM, Prophet. "
               "Hai biểu đồ dưới giải thích phần còn lại.")
else:
    st.markdown(f"**Dự báo {d:%d/%m} = {dong_cong} = {vn(r.du_bao, 1)} {sku.don_vi[ma]}**")
if g.la_ngay_nghi == 1:
    st.info("Ngày này kho nghỉ nên dự báo bằng 0; phần dưới cho thấy mô hình sẽ đoán bao nhiêu nếu kho mở cửa.")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown(f'<div class="nhan-bd"><b>LightGBM nhân từ mức nền</b><span>mỗi nhóm yếu tố làm tăng / giảm bao nhiêu</span></div>', unsafe_allow_html=True)
    hh = pd.DataFrame(hs, columns=["nhom", "he_so"])
    hh["pt"] = (hh.he_so - 1) * 100
    hh["chieu"] = hh.pt.map(lambda v: "Làm tăng" if v >= 0 else "Làm giảm")
    hh["nhan"] = hh.he_so.map(lambda v: f"× {vn(v, 2)}")
    hh["vi_tri"] = hh.pt.clip(lower=0)                                       # nhan dat ben phai so 0 / dau thanh duong: khong de len thanh am
    mien = [min(0.0, hh.pt.min()) * 1.15 - 5, max(hh.pt.max(), 5) * 1.25]
    bd = alt.Chart(hh).encode(y=alt.Y("nhom:N", sort=list(hh.nhom), title=None, axis=alt.Axis(labelLimit=230, labelOverlap=False)))
    C.ve_bd((bd.mark_bar(height=16).encode(x=alt.X("pt:Q", title="% so với mức nền", scale=alt.Scale(domain=mien, nice=False), axis=alt.Axis(labelFlush=True, labelExpr="replace(format(datum.value, ','), regexp(',', 'g'), '.')")),
                                            color=alt.Color("chieu:N", scale=alt.Scale(domain=["Làm tăng", "Làm giảm"], range=[C.C_AI, C.HO_PHACH]),
                                                            legend=alt.Legend(orient="top", title=None)),
                                            tooltip=[alt.Tooltip("nhom:N", title="Nhóm"), alt.Tooltip("nhan:N", title="Hệ số")])
             + bd.mark_text(align="left", dx=5, color=C.MUC2, fontSize=11).encode(x="vi_tri:Q", text="nhan:N")).properties(height=30 * len(hh) + 110, padding={"left": 5, "top": 5, "right": 28, "bottom": 5}))        # chieu cao gom ca chu giai, truc: cong phan do
    chuoi = " × ".join(f"{t.lower()} {vn(v, 2)}" for t, v in hs if abs(v - 1) >= 0.02)
    C.ghi(f"mức nền {vn(nen, 1)} là dự báo trung bình của mọi mã hàng, mọi ngày khi chưa xét yếu tố nào; mỗi thanh là hệ số nhân của một nhóm yếu tố "
          "(× 1,30 = tăng 30%). “Đặc điểm mã hàng” cho biết mã này bán nhiều hay ít hơn mã trung bình.",
          f"{vn(nen, 1)} × {chuoi or 'các hệ số gần 1'} ≈ {vn(g.du_bao_tho, 1)}. Mạnh nhất: {hs[0][0].lower()} (× {vn(hs[0][1], 2)}).")
with c2:
    st.markdown('<div class="nhan-bd"><b>Prophet cộng các thành phần</b><span>đơn vị / ngày</span></div>', unsafe_allow_html=True)
    if kq["prophet"] is None:
        st.caption("Mã này quá ít dữ liệu nên Prophet trả về 0.")
    else:
        tp = kq["prophet"][kq["prophet"].date == d].iloc[0]
        cot = ["Xu hướng", "Mùa trong tuần", "Mùa trong năm", "Ngày lễ, sự kiện", "Khuyến mãi"]
        pp = pd.DataFrame({"tp": cot, "gia_tri": [float(tp[c]) for c in cot]})
        pp["chieu"] = pp.gia_tri.map(lambda v: "Cộng thêm" if v >= 0 else "Trừ bớt")
        pp["nhan"] = pp.gia_tri.map(lambda v: ("+" if v >= 0 else "") + vn(v, 1))
        pp["vi_tri"] = pp.gia_tri.clip(lower=0)
        mien2 = [min(0.0, pp.gia_tri.min()) * 1.15 - 1, max(pp.gia_tri.max(), 1) * 1.25]
        bd2 = alt.Chart(pp).encode(y=alt.Y("tp:N", sort=cot, title=None, axis=alt.Axis(labelOverlap=False)))
        C.ve_bd((bd2.mark_bar(height=16).encode(x=alt.X("gia_tri:Q", title=f"{sku.don_vi[ma]} / ngày", scale=alt.Scale(domain=mien2, nice=False), axis=alt.Axis(labelFlush=True, labelExpr="replace(format(datum.value, ','), regexp(',', 'g'), '.')")),
                                                 color=alt.Color("chieu:N", scale=alt.Scale(domain=["Cộng thêm", "Trừ bớt"], range=[C.C_AI, C.HO_PHACH]),
                                                                 legend=alt.Legend(orient="top", title=None)))
                 + bd2.mark_text(align="left", dx=5, color=C.MUC2, fontSize=11).encode(x="vi_tri:Q", text="nhan:N")).properties(height=30 * len(pp) + 110, padding={"left": 5, "top": 5, "right": 28, "bottom": 5}))
        C.ghi("Prophet cộng xu hướng dài hạn với dao động theo tuần, theo năm và ảnh hưởng ngày lễ.",
              f"tổng các thành phần {vn(tp['Tổng (Prophet)'], 1)} (âm thì lấy 0) → Prophet {vn(r.prophet, 1)}.")

# ------------------------------------------------------------------ 5. thu neu: bat khuyen mai (mo hinh tinh lai, khong hoc lai)
C.muc("Thử nếu: bật khuyến mãi", "mô hình vừa học tính lại ngay cho mã đang xem, không học lại")
from chay_du_bao import bat_khuyen_mai, chay_ma, km_lich_su, so_sanh_khuyen_mai  # noqa: E402
ctx = ngu_canh(str(C.GOC_DU_LIEU), DAU)
fn_lgb, _ = lightgbm(str(C.GOC_DU_LIEU), DAU)
m_pro, _ = prophet(str(C.GOC_DU_LIEU), DAU, ma)
ls = km_lich_su(ctx["df"], ma)
if ls["so_ngay_km"] == 0:
    st.info(("Dữ liệu nguồn này không có lịch khuyến mãi" if not C.NGUON["la_mo_phong"] else f"Mã {ma} chưa từng có ngày khuyến mãi trong dữ liệu")
            + ", nên mô hình không học được khuyến mãi làm bán tăng bao nhiêu: bật lên thì dự báo gần như không đổi. Đây là giới hạn của dữ liệu, không phải lỗi.")
# thanh truot ngay chuan (select_slider dang khoang cua Streamlit 1.45 loi o trinh duyet: "Cannot read properties of null")
nk = [pd.Timestamp(x).date() for x in cac_ngay]
v = s.get("_db_km_w")
if not (isinstance(v, tuple) and len(v) == 2 and nk[0] <= v[0] <= v[1] <= nk[-1]):
    s["_db_km_w"] = (nk[0], nk[min(6, len(nk) - 1)])
st.slider("Khuyến mãi từ ngày … đến ngày", min_value=nk[0], max_value=nk[-1], step=timedelta(days=1), format="DD/MM/YYYY", key="_db_km_w")
tu, den = (pd.Timestamp(x) for x in s["_db_km_w"])
moi = chay_ma(ctx, fn_lgb, ma, m_pro, bat_khuyen_mai(ctx["fut"], ma, tu, den))
nb, nm = kq["bang"], moi["bang"]
trong = nb.date.between(tu, den).values
goc_km, moi_km = nb.du_bao[trong].sum(), nm.du_bao[trong].sum()
pt_km = (moi_km / goc_km - 1) * 100 if goc_km > 0 else 0.0
C.o_hang([("Dự báo gốc, các ngày khuyến mãi", vn(goc_km, 0), f"{int(trong.sum())} ngày, {sku.don_vi[ma]}", False),
          ("Nếu khuyến mãi", vn(moi_km, 0), f"{'+' if pt_km >= 0 else ''}{vn(pt_km, 1)}%", True),
          ("Cả 28 ngày thay đổi", ("+" if nm.du_bao.sum() >= nb.du_bao.sum() else "") + vn(nm.du_bao.sum() - nb.du_bao.sum(), 0), sku.don_vi[ma], False),
          ("Lịch sử của mã, cùng mùa", ("× " + vn(ls["ti_so_cung_mua"], 2)) if ls["ti_so_cung_mua"] == ls["ti_so_cung_mua"] else "—",
           f"{ls['so_ngay_km']} ngày có khuyến mãi so với 28 ngày thường ngay trước", False)])
hai = pd.concat([nb[["date", "du_bao"]].assign(loai="Dự báo gốc"), nm[["date", "du_bao"]].assign(loai="Nếu khuyến mãi")])
mau2 = alt.Scale(domain=["Dự báo gốc", "Nếu khuyến mãi"], range=[C.C_AI2, C.C_AI])
nen_km = alt.Chart(pd.DataFrame({"tu": [tu - pd.Timedelta(hours=12)], "den": [den + pd.Timedelta(hours=12)]})).mark_rect(color=C.QUANG, opacity=0.35).encode(
    x="tu:T", x2="den:T")
dg = alt.Chart(hai).mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=16)).encode(
    x=alt.X("date:T", title=None, axis=alt.Axis(format="%d/%m")), y=alt.Y("du_bao:Q", title=f"{sku.don_vi[ma]} / ngày"),
    color=alt.Color("loai:N", scale=mau2, legend=alt.Legend(orient="top", title=None)),
    tooltip=[alt.Tooltip("date:T", title="Ngày", format="%d/%m/%Y"), alt.Tooltip("loai:N", title=" "), alt.Tooltip("du_bao:Q", title="Dự báo", format=",.1f")])
C.ve_bd((nen_km + dg).properties(height=230))
hs_goc = float(pd.Series(kq["giai_thich"]["Khuyến mãi"].values[trong]).map(lambda v: 2.718281828 ** v).mean())
hs_moi = float(pd.Series(moi["giai_thich"]["Khuyến mãi"].values[trong]).map(lambda v: 2.718281828 ** v).mean())
km_pro = (float(moi["prophet"]["Khuyến mãi"].values[trong].mean()) if moi["prophet"] is not None else 0.0)
C.ghi("dải vàng là các ngày bật khuyến mãi; đường nhạt là dự báo gốc (không khuyến mãi), đường đậm là dự báo nếu khuyến mãi. "
      "Chỉ cột khuyến mãi của mã này đổi, mọi thông tin khác giữ nguyên.",
      f"LightGBM: hệ số khuyến mãi trung bình × {vn(hs_goc, 2)} → × {vn(hs_moi, 2)}; Prophet: thành phần khuyến mãi {('+' if km_pro >= 0 else '') + vn(km_pro, 1)} / ngày"
      + ("; RNN giữ nguyên (không tính lại khi bấm)" if ctx["kieu"] == "dl" else "")
      + f". Lịch sử của mã: ngày có khuyến mãi bán gấp {vn(ls['ti_so_cung_mua'], 2) if ls['ti_so_cung_mua'] == ls['ti_so_cung_mua'] else '—'} lần "
      f"28 ngày thường ngay trước (so thô với mọi ngày thường: {vn(ls['ti_so_tho'], 2) if ls['ti_so_tho'] == ls['ti_so_tho'] else '—'}, lẫn mùa vụ). "
      "Hàng mùa vụ ngoài mùa thường tăng ít hơn lịch sử vì các đợt khuyến mãi cũ rơi vào mùa cao điểm.")
khoa_ss = (str(C.GOC_DU_LIEU), DAU)
co_km = int(ctx["df"].khuyen_mai.sum()) > 0                               # nguon khong co khuyen mai (VD M5): khong co gi de so
if co_km and st.button("So sánh toàn kho", key="db_ss_km", help="Bật khuyến mãi 7 ngày đầu cho mọi mã (chỉ phần LightGBM), so với lịch sử cùng mùa của từng mã."):
    with st.spinner("Đang tính cho mọi mã…"):
        s.db_ss_km_kq = (khoa_ss, so_sanh_khuyen_mai(ctx, fn_lgb).reset_index())     # khoa khac khoa cua nut
if co_km and s.get("db_ss_km_kq") and s.db_ss_km_kq[0] == khoa_ss:
    ss = s.db_ss_km_kq[1].dropna()
    if ss.empty:
        st.caption("Không có mã nào có lịch sử khuyến mãi để so.")
    else:
        C.o_hang([("Mô hình tăng (trung vị)", "× " + vn(ss.mo_hinh.median(), 2), "LightGBM, bật 7 ngày đầu", True),
                  ("Lịch sử cùng mùa (trung vị)", "× " + vn(ss.lich_su.median(), 2), f"{len(ss)} mã có khuyến mãi", False),
                  ("Mô hình tăng ít hơn lịch sử", f"{int((ss.mo_hinh < ss.lich_su).sum())} mã", "trên đường chéo là mô hình tăng nhiều hơn", False)])
        ss = ss[(ss.mo_hinh > 0) & (ss.lich_su > 0)]
        mx = [ss.lich_su.min() * 0.9, ss.lich_su.max() * 1.1]                    # ti so: thang log, moi truc 1 mien rieng (diem mo hinh nam gon)
        my = [ss.mo_hinh.min() * 0.8, ss.mo_hinh.max() * 1.25]
        lim = [max(mx[0], my[0]), min(mx[1], my[1])]                             # duong cheo chi ve phan 2 mien chong nhau
        cheo = alt.Chart(pd.DataFrame({"a": lim, "b": lim})).mark_line(color=C.MUC2, strokeDash=[4, 3]).encode(
            x=alt.X("a:Q", scale=alt.Scale(type="log", domain=mx)), y=alt.Y("b:Q", scale=alt.Scale(type="log", domain=my)))
        diem = alt.Chart(ss).mark_circle(size=60, color=C.C_AI, opacity=0.75).encode(
            x=alt.X("lich_su:Q", title="Lịch sử cùng mùa (lần)", scale=alt.Scale(type="log", domain=mx)),
            y=alt.Y("mo_hinh:Q", title="Mô hình (lần)", scale=alt.Scale(type="log", domain=my)),
            tooltip=[alt.Tooltip("ma_sku:N", title="Mã"), alt.Tooltip("lich_su:Q", title="Lịch sử", format=".2f"), alt.Tooltip("mo_hinh:Q", title="Mô hình", format=".2f")])
        C.ve_bd((cheo + diem).properties(height=300))
        C.ghi("mỗi chấm là một mã; nằm trên đường chéo nghĩa là mô hình tăng đúng bằng lịch sử; hai trục theo thang log vì là tỉ số. "
              "Chấm ở xa hai bên thường là hàng mùa vụ: đợt khuyến mãi cũ rơi vào lúc vào mùa (bên phải, 28 ngày trước gần như không bán) "
              "hoặc lúc hết mùa (bên trái), nên tỉ số lịch sử bị lệch.",
              f"trung vị mô hình × {vn(ss.mo_hinh.median(), 2)}, lịch sử × {vn(ss.lich_su.median(), 2)}; tương quan thứ hạng {vn(ss.mo_hinh.rank().corr(ss.lich_su.rank()), 2)} "
              "(mã nào lịch sử tăng mạnh thì mô hình có xu hướng tăng mạnh hay không).")
