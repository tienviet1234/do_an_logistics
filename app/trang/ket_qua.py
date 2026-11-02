"""Man Kich ban & ket qua: so sanh 4 chinh sach dat hang tren 12 thang kiem tra, TINH THEO BO LOC NHOM o dau phieu
(cong lai tung ma tu ket_qua_ton_kho / ket_qua_do_nhay, khong dung so toan kho co dinh). Bam 1 chinh sach tren bieu do ->
to dam chinh sach do o moi bieu do va dat lam chinh sach chung cho moi man (neu la chinh sach dung cong thuc)."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import chung as C
from chung import vn

s = st.session_state
p = C.sku_loc()
if p.empty:
    st.warning("Không có mã nào khớp bộ lọc nhóm ABC / XYZ ở đầu phiếu.")
    st.stop()
ids = set(p.ma_sku)
CS = list(C.CS_TEN)


def tong(k, by=("ma_chinh_sach",)):
    """Cong cac ma -> chi so cua chinh sach (cung cong thuc khung nhin v_so_sanh_chinh_sach)."""
    g = k.groupby(list(by))
    out = pd.DataFrame({"fr": 100 * g.da_dap_ung.sum() / g.nhu_cau.sum(), "thieu": g.so_ngay_thieu.sum(),
                        "ton": g.gia_tri_ton_tb.sum() / 1e6, "lan": g.so_lan_nhap.sum(),
                        "dl": (g.chi_phi_dat.sum() + g.chi_phi_luu.sum()) / 1e6, "ln": g.loi_nhuan_mat.sum() / 1e6})
    out["cp"] = out.dl + out.ln
    return out


s.setdefault("kq_lv", 0.95)
s["_kqlv_w"] = s.kq_lv
c1, c2 = st.columns([1.4, 3], vertical_alignment="bottom")
c1.segmented_control("Mức phục vụ mục tiêu", [0.90, 0.95, 0.99], format_func=lambda v: f"{v:.0%}", key="_kqlv_w",
                     on_change=lambda: s.update(kq_lv=s["_kqlv_w"] or s.kq_lv),
                     help="Hệ số z trong công thức SS. Hiện trạng* không dùng công thức nên giống nhau ở mọi mức.")
lv = s.kq_lv
c2.markdown(f'<div class="dp-phu phai">{C.mo_ta_loc()} ({len(ids)} mã) · 12 tháng kiểm tra '
            f'01/10/2025 – 29/09/2026 · {C.NOTE}</div>', unsafe_allow_html=True)

k = C.q("SELECT * FROM ket_qua_ton_kho WHERE ROUND(muc_phuc_vu, 2) = ?", (lv,))
k = k[k.ma_sku.isin(ids)]
v = tong(k).reindex(CS)
g, b, h = v.loc[C.CS_GOI_Y], v.loc["cong_thuc_du_bao_moc"], v.loc["hien_trang"]
pt = lambda a, o: f"{C.dau_cong((a / o - 1) * 100)}%"

# ------------------------------------------------------------------ truoc - sau
C.muc("Trước – sau", f"mức phục vụ {lv:.0%} · tiền tính bằng triệu đồng", dau_tien=True)
st.markdown(f'<div class="dao-mau"><b>AI + hiệu chỉnh lệch</b> so với dự báo mốc (cùng công thức): Fill Rate '
            f'<b>{C.dau_cong(g.fr - b.fr, 2)} điểm</b>, ngày thiếu hàng <b>{pt(g.thieu, b.thieu)}</b>, tồn kho {pt(g.ton, b.ton)}, '
            f'chi phí liên quan <b>{pt(g.cp, b.cp)}</b>. So với hiện trạng*: Fill Rate {C.dau_cong(g.fr - h.fr, 2)} điểm, '
            f'ngày thiếu {pt(g.thieu, h.thieu)}, tồn kho {pt(g.ton, h.ton)}, chi phí liên quan {pt(g.cp, h.cp)}.</div>',
            unsafe_allow_html=True)
st.write("")
dong = ""
for c in CS:
    r = v.loc[c]
    ten = C.CS_TEN[c].replace(" (đề xuất)", "") + (f"&nbsp; {C.dau('Đề xuất', 'la', 'duyet')}" if c == C.CS_GOI_Y else "")
    dong += (f'<tr{" class=chon" if c == s.cs else ""}><td>{ten}</td><td>{vn(r.fr, 2)}%</td><td>{vn(r.thieu, 0)}</td>'
             f'<td>{vn(r.ton)}</td><td>{vn(r.lan, 0)}</td><td>{vn(r.dl)}</td><td>{vn(r.ln)}</td><td><b>{vn(r.cp)}</b></td></tr>')
st.markdown(f'<div class="bang-cuon"><table class="phieu"><tr><th>Chính sách</th><th>Fill Rate</th><th>Ngày-mã thiếu</th>'
            f'<th>Tồn kho TB</th><th>Số lần nhập</th><th>CP đặt + lưu</th><th>Lợi nhuận mất</th><th>CP liên quan</th></tr>'
            f'{dong}</table></div>', unsafe_allow_html=True)
st.caption("Chi phí liên quan = chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do hết hàng. Dòng tô đậm là chính sách "
           "đang chọn ở đầu phiếu. " + C.NOTE_HT.replace("\\*", "*"))

# ------------------------------------------------------------------ 4 chi so, bam de to dam (loc cheo)
C.muc("Bốn chỉ số chính", "bấm một chính sách để tô đậm ở mọi biểu đồ và chọn nó cho mọi màn")
KPI = [("fr", "Fill Rate (%)", ".2f"), ("thieu", "Ngày-mã thiếu hàng", ",.0f"), ("ton", "Tồn kho TB (triệu đ)", ",.0f"),
       ("cp", "Chi phí liên quan (triệu đ)", ",.0f")]
mau_cs = alt.Scale(domain=CS, range=[C.CS_MAU[c] for c in CS])
for col, (cot_, ten, _) in zip(st.columns(4, gap="medium"), KPI):
    # 1 bieu do 1 lop moi chi so (Streamlit 1.45 chi cho chon tren bieu do 1 lop); so lieu ghi ngay tren nhan truc
    dd = v[[cot_]].rename(columns={cot_: "so"}).reset_index()
    dd["nhan"] = [f"{C.CS_NGAN[c]} · {vn(a, 2) if cot_ == 'fr' else vn(a, 0)}" for c, a in zip(dd.ma_chinh_sach, dd.so)]
    sel = alt.selection_point(name="chon_cs", fields=["ma_chinh_sach"], on="click", empty=False)
    bd = alt.Chart(dd).mark_bar(height=20).encode(
        y=alt.Y("nhan:N", sort=list(dd.nhan), title=None, axis=alt.Axis(labelLimit=200, labelFontSize=12.5, ticks=False,
                                                                         domain=False, labelColor=C.MUC)),
        x=alt.X("so:Q", title=None, axis=None, scale=alt.Scale(zero=True)),
        color=alt.Color("ma_chinh_sach:N", scale=mau_cs, legend=None),
        opacity=alt.condition(alt.datum.ma_chinh_sach == s.cs, alt.value(1), alt.value(0.3)),
        tooltip=[alt.Tooltip("nhan:N", title=ten)]).add_params(sel)
    col.markdown(f'<span class="nhan">{ten}</span>', unsafe_allow_html=True)
    khoa_cs = f"cs_{cot_}_{lv}_{''.join(s.abc)}_{''.join(s.xyz)}_{s.cs}"                  # du lieu doi -> khoa doi
    with col:
        C.ve_bd(bd.properties(height=150), selection_mode="chon_cs", key=khoa_cs, on_select=lambda k=khoa_cs: C.khi_chon_cs(k))
C.ghi("mỗi khung một chỉ số, thanh dài hơn = giá trị lớn hơn (Fill Rate: lớn là tốt; ba chỉ số còn lại: nhỏ là tốt). "
      "Thanh đậm là chính sách đang chọn ở đầu phiếu.",
      f"chính sách rẻ nhất (chi phí liên quan) với nhóm đang lọc: {C.CS_NGAN[v.cp.idxmin()]}; "
      f"đáp ứng cao nhất: {C.CS_NGAN[v.fr.idxmax()]}.")

# ------------------------------------------------------------------ theo nhom XYZ: danh doi ton kho - dap ung
C.muc("Theo nhóm XYZ: tồn kho đổi lấy mức đáp ứng", "góc trên bên trái là tốt: đáp ứng cao, tồn ít")
x = tong(k.merge(p[["ma_sku", "xyz_train"]], on="ma_sku"), by=("xyz_train", "ma_chinh_sach")).reset_index()
x["ten"] = x.ma_chinh_sach.map(C.CS_NGAN)
x["nhom"] = "Nhóm " + x.xyz_train + x.xyz_train.map({"X": " · ổn định", "Y": " · dao động vừa", "Z": " · mùa vụ, thất thường"})
diem = alt.Chart(x).mark_point(filled=True, size=150, opacity=1, stroke=C.MUC, strokeWidth=0.8).encode(
    x=alt.X("ton:Q", title="Tồn kho TB (triệu đồng)", scale=alt.Scale(zero=False, padding=24)),
    y=alt.Y("fr:Q", title="Fill Rate (%)", scale=alt.Scale(zero=False, padding=18)),
    color=alt.Color("ma_chinh_sach:N", scale=alt.Scale(domain=CS, range=[C.CS_MAU[c] for c in CS]),
                    legend=alt.Legend(orient="top", title=None, labelExpr="datum.label == 'hien_trang' ? 'Hiện trạng*' : "
                                      "datum.label == 'cong_thuc_du_bao_moc' ? 'Dự báo mốc' : datum.label == "
                                      "'cong_thuc_du_bao_ai' ? 'AI' : 'AI + hiệu chỉnh'")),
    shape=alt.Shape("ma_chinh_sach:N", scale=alt.Scale(domain=CS, range=["square", "triangle-up", "diamond", "circle"]),
                    legend=None),
    tooltip=[alt.Tooltip("nhom:N", title="Nhóm"), alt.Tooltip("ten:N", title="Chính sách"),
             alt.Tooltip("fr:Q", title="Fill Rate (%)", format=".1f"), alt.Tooltip("ton:Q", title="Tồn TB (tr đ)", format=",.0f"),
             alt.Tooltip("ln:Q", title="Lợi nhuận mất (tr đ)", format=",.0f")])
nhan = alt.Chart(x).mark_text(align="left", dx=10, dy=-9, fontSize=11, color=C.MUC2).encode(x="ton:Q", y="fr:Q", text="ten:N")
C.ve_bd((diem + nhan).properties(width=380, height=260).facet(
    column=alt.Column("nhom:N", title=None, header=alt.Header(labelFontSize=13, labelAnchor="start"))
).resolve_scale(x="independent", y="independent"), use_container_width=False)
if "Z" in set(x.xyz_train):
    z = x[x.xyz_train == "Z"].set_index("ma_chinh_sach")
    C.ghi("mỗi dấu là một chính sách; mỗi khung một nhóm, trục riêng.",
          f"nhóm Z: AI + hiệu chỉnh giữ tồn {vn(z.ton[C.CS_GOI_Y] / z.ton['hien_trang'], 1)} lần hiện trạng để đáp ứng "
          f"{vn(z.fr[C.CS_GOI_Y])}% (hiện trạng {vn(z.fr['hien_trang'])}%). Với quy tắc chọn trên validation, nhóm Z đặt bù đến mức "
          "(đủ bán đến lần đặt sau) thay vì EOQ, nên không còn đặt quá tay hàng chỉ bán dịp lễ như bản 28 ngày.")

# ------------------------------------------------------------------ chi so kho: von dong trong hang ton
C.muc("Chỉ số kho", f"mức phục vụ {lv:.0%} · vòng quay càng cao, số ngày tồn càng thấp thì vốn càng ít bị đọng")
gia = C.ds_sku().set_index("ma_sku")
k_kho = k.assign(gia_von=k.ma_sku.map(gia.gia_von), xyz=k.ma_sku.map(gia.xyz_train))
n_ngay = C.so_ngay_mo_phong()
kho = C.chi_so_theo_nhom(k_kho, ["ma_chinh_sach"], n_ngay).reindex(CS)
du_ma = {c: C.ton_du(c).pipe(lambda f: f[f.ma_sku.isin(ids)]) for c in CS}
du_cs = pd.DataFrame({c: {"du": du_ma[c].du_tb.sum() / 1e6, "tl": 100 * du_ma[c].du_tb.sum() / max(du_ma[c].ton_tb.sum(), 1)} for c in CS}).T
dong = ""
for c in CS:
    r, d = kho.loc[c], du_cs.loc[c]
    ten = C.CS_TEN[c].replace(" (đề xuất)", "") + (f"&nbsp; {C.dau('Đề xuất', 'la', 'duyet')}" if c == C.CS_GOI_Y else "")
    dong += (f'<tr{" class=chon" if c == s.cs else ""}><td>{ten}</td><td>{vn(r.vong_quay)}</td><td>{vn(r.doh)}</td>'
             f'<td>{vn(d.du)}</td><td>{vn(d.tl)}%</td></tr>')
st.markdown(f'<div class="bang-cuon"><table class="phieu"><tr><th>Chính sách</th><th>Vòng quay (lần/năm)</th><th>Số ngày tồn kho</th>'
            f'<th>Tồn dư TB, mức 95% (triệu đ)</th><th>Tồn dư / tồn kho</th></tr>{dong}</table></div>', unsafe_allow_html=True)
st.write("")
theo_xyz = C.chi_so_theo_nhom(k_kho, ["ma_chinh_sach", "xyz"], n_ngay).reset_index()
nhom_co = [n for n in ["X", "Y", "Z"] if n in set(theo_xyz.xyz)]
TEN_XYZ = {"X": "X, ổn định", "Y": "Y, dao động vừa", "Z": "Z, mùa vụ"}
for col, n in zip(st.columns(len(nhom_co), gap="medium"), nhom_co):
    with col:
        st.markdown(f'<div class="nhan-bd"><b>Nhóm {TEN_XYZ[n]}</b><span>số ngày tồn kho</span></div>', unsafe_allow_html=True)
        f = theo_xyz[theo_xyz.xyz == n].assign(ten=lambda t: t.ma_chinh_sach.map(C.CS_NGAN), nhan=lambda t: t.doh.map(vn))
        goc = alt.Chart(f).encode(y=alt.Y("ten:N", title=None, sort=[C.CS_NGAN[c] for c in CS], axis=alt.Axis(ticks=False, domain=False, labelLimit=120)),
                                  x=alt.X("doh:Q", title=None, axis=None, scale=alt.Scale(domain=[0, f.doh.replace(np.inf, 0).max() * 1.35 or 1])))
        bd = (goc.mark_bar(size=16, cornerRadiusEnd=3).encode(color=alt.Color("ma_chinh_sach:N", scale=mau_cs, legend=None)) +
              goc.mark_text(align="left", dx=5, color=C.MUC, fontWeight=600, fontSize=12).encode(text="nhan:N")).properties(height=140)
        C.ve_bd(bd)
top = du_ma[s.cs].sort_values("du_tb", ascending=False).head(10)
top = top.assign(ten=top.ma_sku.map(gia.ten_sku), xyz=top.ma_sku.map(gia.xyz_train), du=top.du_tb / 1e6, ton=top.ton_tb / 1e6)
tong_du = du_ma[s.cs].du_tb.sum()
C.muc("Hàng tồn dư nhiều nhất", f"{C.CS_NGAN[s.cs]} · mức phục vụ 95%, trung bình cả năm kiểm tra")
st.dataframe(top[["ma_sku", "ten", "xyz", "du", "ton"]], hide_index=True, use_container_width=True, height=38 + 35 * len(top), column_config={
    "ma_sku": st.column_config.TextColumn("Mã", width="small"), "ten": st.column_config.TextColumn("Tên hàng", width="large"),
    "xyz": st.column_config.TextColumn("XYZ", width="small"),
    "du": st.column_config.NumberColumn("Tồn dư TB (triệu đ)", format="%.1f"), "ton": st.column_config.NumberColumn("Tồn kho TB (triệu đ)", format="%.1f")})
if "Z" in nhom_co and "X" in nhom_co:
    z, x_ = theo_xyz[(theo_xyz.ma_chinh_sach == s.cs) & (theo_xyz.xyz == "Z")].doh.iloc[0], theo_xyz[(theo_xyz.ma_chinh_sach == s.cs) & (theo_xyz.xyz == "X")].doh.iloc[0]
    them = f"Chính sách đang chọn giữ hàng nhóm Z {vn(z)} ngày so với {vn(x_)} ngày của nhóm X. "
else:
    them = ""
C.ghi("vòng quay = giá vốn hàng xuất quy ra 1 năm ÷ tồn kho bình quân; số ngày tồn kho = tồn kho bình quân ÷ giá vốn hàng xuất 1 ngày. "
      "Tồn dư = phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp (nhìn lại để chấm, không dùng để ra quyết định), bỏ 28 ngày cuối kỳ.",
      f"{them}10 mã trong bảng chiếm {vn(100 * top.du_tb.sum() / max(tong_du, 1), 0)}% tồn dư.")

# ------------------------------------------------------------------ thu do nhay
C.muc("Thử độ nhạy: nếu hàng về trễ hoặc chi phí tăng", "mức phục vụ 95% · so với kịch bản bình thường")
dn = C.q("SELECT k.*, b.nhom, b.tham_so FROM ket_qua_do_nhay k JOIN kich_ban_do_nhay b USING (ma_kich_ban)")
if dn.empty:
    st.info("Chưa có kết quả thử độ nhạy. Chạy `python src/do_nhay.py` rồi bấm “Tải lại dữ liệu”.")
    st.stop()
dn = dn[dn.ma_sku.isin(ids)]
dn["kb"] = np.where(dn.nhom == "tac_cang", "tac_cang_" + dn.tham_so.fillna(0).astype(int).astype(str), dn.ma_kich_ban)
KB = {"tac_cang_3": "Tắc cảng, trễ +3 ngày", "tac_cang_5": "Tắc cảng, trễ +5 ngày", "tac_cang_7": "Tắc cảng, trễ +7 ngày",
      "lead_time_2": "Lead time +2, không cập nhật", "lead_time_2_cap_nhat": "Lead time +2, có cập nhật",
      "chi_phi_dat_120": "Chi phí đặt +20%", "chi_phi_luu_115": "Chi phí lưu kho +15%"}
s.setdefault("kq_kb", "tac_cang_7")
s["_kb_w"] = s.kq_kb
st.pills("Kịch bản", list(KB), format_func=KB.get, key="_kb_w", on_change=lambda: s.update(kq_kb=s["_kb_w"] or s.kq_kb))
kb = s.kq_kb
goc = tong(dn[dn.ma_kich_ban == "goc"])
dot = tong(dn[dn.kb == kb], by=("ma_kich_ban", "ma_chinh_sach")).groupby("ma_chinh_sach").mean()   # tac cang: TB 13 dot
d = dot.join(goc, rsuffix="_goc").reindex([c for c in CS if c in dot.index])
d["d_fr"], d["d_cp"] = d.fr - d.fr_goc, 100 * (d.cp / d.cp_goc - 1)
d = d.reset_index()
d["ten"] = d.ma_chinh_sach.map(C.CS_NGAN)
mau = alt.Scale(domain=CS, range=[C.CS_MAU[c] for c in CS])
c1, c2 = st.columns(2, gap="large")
for col, cot_, ten, dv in [(c1, "d_fr", "Fill Rate thay đổi (điểm %)", "điểm"), (c2, "d_cp", "Chi phí liên quan thay đổi (%)", "%")]:
    d["nhan"] = [C.dau_cong(a, 2 if cot_ == "d_fr" else 1) for a in d[cot_]]
    bb = alt.Chart(d).encode(y=alt.Y("ten:N", sort=[C.CS_NGAN[c] for c in CS], title=None),
                             x=alt.X(f"{cot_}:Q", title=ten, scale=alt.Scale(nice=True, padding=30)))
    ch = (bb.mark_bar(height=20).encode(color=alt.Color("ma_chinh_sach:N", scale=mau, legend=None))
          + bb.mark_text(align="left", dx=4, fontSize=12, fontWeight=600, color=C.MUC).encode(text="nhan:N")
          + bb.mark_rule(color=C.PHIEU).encode(x=alt.datum(0), y=alt.value(0), y2=alt.value(170)))   # vach 0: cung 1 bang voi cot
    with col:
        C.ve_bd(ch.properties(height=170))
re_nhat = d.loc[d.cp.idxmin(), "ten"]
C.ghi("so với kịch bản bình thường của chính sách đó; tắc cảng là trung bình 13 đợt trong năm, người lập kế hoạch không biết trước.",
      f"{KB[kb]}: chính sách rẻ nhất vẫn là {re_nhat}. Hiện trạng* chỉ so được khi đổi chi phí (đơn hàng của nó lấy từ dữ liệu).")
