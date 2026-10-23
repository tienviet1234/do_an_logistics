"""Tao trang trinh bay luong he thong (mo bang trinh duyet, KHONG can internet).
So lieu lay truc tiep tu co so du lieu -> trang luon khop du lieu that.
Chay: python src/nap_database.py && python src/tao_trang_luong.py
Ket qua: trinh_bay/luong_he_thong.html
"""
import html
import os
import sys
from contextlib import closing
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from csdl import ket_noi  # noqa: E402

OUT = "trinh_bay/luong_he_thong.html"
DONE, DOING, PLAN, OUTSIDE = ("done", "Đã làm"), ("doing", "Đang làm"), ("plan", "Kế hoạch"), ("out", "Ngoài hệ thống")


def vn(n, d=0):
    s = f"{n:,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def chip(st):
    return f'<span class="chip {st[0]}">{st[1]}</span>'


with closing(ket_noi()) as con:
    q = lambda sql: con.execute(sql).fetchone()[0]
    n = {t: q(f"SELECT COUNT(*) FROM {t}") for t in
         ["dm_sku", "dm_nha_cung_cap", "giao_dich_tho", "giao_dich_sach", "nhat_ky_sua_loi", "lich_su_kien",
          "lich_khuyen_mai", "lich_ngay_nghi", "su_kien_dot_bien", "du_bao", "ket_qua_mo_hinh", "mo_hinh"]}
    chon = con.execute("""SELECT k.ma_mo_hinh, k.wmape, k.wmape_tuan, k.bias_pct FROM ket_qua_mo_hinh k
                          JOIN mo_hinh m USING (ma_mo_hinh) WHERE m.duoc_chon = 1 AND k.tap = 'test'""").fetchone()
    sn7 = q("SELECT wmape FROM ket_qua_mo_hinh WHERE ma_mo_hinh='seasonal_naive_7' AND tap='test'")
    lech = q("""SELECT COUNT(*) FROM (SELECT ton_cuoi_ngay - (LAG(ton_cuoi_ngay) OVER (PARTITION BY ma_sku ORDER BY ngay)
                + qty_in - qty_out) AS l FROM giao_dich_sach) WHERE ABS(l) > 0.5""")
    fk_loi = len(con.execute("PRAGMA foreign_key_check").fetchall())
    het_hang = q("SELECT COUNT(*) FROM giao_dich_sach WHERE het_hang = 1")
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
    views = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    info = {}
    for t in tables:
        cols = con.execute(f"PRAGMA table_info({t})").fetchall()
        fks = {r[3]: f"{r[2]}.{r[4]}" for r in con.execute(f"PRAGMA foreign_key_list({t})").fetchall()}
        info[t] = (q(f"SELECT COUNT(*) FROM {t}"), cols, fks)
size_mb = os.path.getsize("data/kho_hang.db") / 1e6
ma_chon, w_chon, wt_chon, b_chon = chon

# ------------------------------------------------------------------ luong nghiep vu
business = [
    ("1", "Ghi nhận nhập – xuất – tồn hằng ngày", "Kho (WMS / ERP)", "File xuất nhập tồn theo ngày, từng SKU",
     OUTSIDE, "Trong đồ án: dữ liệu mô phỏng 121 SKU × 1.096 ngày."),
    ("2", "Gửi lịch khuyến mãi, ngày lễ, sale", "Bán hàng / Marketing", "Lịch khuyến mãi theo SKU, lịch lễ, lịch sale",
     OUTSIDE, f"{vn(n['lich_khuyen_mai'])} đợt khuyến mãi, {n['lich_su_kien']} sự kiện."),
    ("3", "Làm sạch, đối soát tồn kho", "Hệ thống", "Dữ liệu sạch, nhật ký sửa lỗi",
     DONE, f"Sửa {vn(n['nhat_ky_sua_loi'])} dòng; đẳng thức kho lệch {lech} dòng."),
    ("4", "Dự báo nhu cầu 28 ngày tới cho từng SKU", "Hệ thống (AI)", "Dự báo theo ngày, theo tuần",
     DONE, f"Kết hợp LightGBM + Prophet: sai số {vn(w_chon * 100, 1)}% (cách đơn giản: {vn(sn7 * 100, 1)}%)."),
    ("5", "Tính tồn kho an toàn, điểm đặt hàng, lượng đặt", "Hệ thống", "SS, ROP, EOQ cho từng SKU",
     DOING, "Giai đoạn F: dùng sai số dự báo để tính tồn kho an toàn."),
    ("6", "Cảnh báo SKU chạm điểm đặt hàng, đề xuất đơn", "Hệ thống → Người lập kế hoạch", "Danh sách cần đặt, số lượng đề xuất",
     PLAN, "Hiển thị trên dashboard; người lập kế hoạch duyệt."),
    ("7", "Đặt hàng nhà cung cấp, lên kế hoạch xe", "Mua hàng / Điều vận", "Đơn đặt hàng, lịch xe nhận – giao",
     OUTSIDE, "Phân hệ điều vận: mở rộng sau khi nộp."),
]

# ------------------------------------------------------------------ luong du lieu
data_steps = [
    ("Nguồn dữ liệu", "File CSV xuất từ kho + lịch tham chiếu", "data/raw, data/reference",
     f"{vn(n['giao_dich_tho'])} dòng thô (có lỗi cài sẵn: trùng, thiếu, nhập sai)", DONE, None),
    ("1. Làm sạch", "Loại trùng; suy lượng xuất từ đẳng thức kho; gắn cờ hết hàng", "src/lam_sach.py",
     f"{vn(n['giao_dich_sach'])} dòng sạch · {vn(het_hang)} ngày hết hàng", DONE, "giao_dich_tho → giao_dich_sach, nhat_ky_sua_loi"),
    ("2. Tạo đặc trưng", "Lịch, lễ, sale, khuyến mãi, giá trị trễ; phân loại ABC/XYZ trên tập học", "src/dac_trung.py",
     "64 cột đặc trưng · 121 SKU được phân loại", DONE, "phan_loai_sku"),
    ("3. Phân tích khám phá", "Chu kỳ tuần, mùa vụ, tác động khuyến mãi", "src/eda.py", "8 biểu đồ cho Chương 4", DONE, None),
    ("4. Khung đánh giá", "Chia theo thời gian; 13 mốc dự báo, mỗi mốc 28 ngày; chỉ dùng thông tin biết trước",
     "src/danh_gia.py", "Cùng một đề thi cho mọi mô hình", DONE, None),
    ("5. Mô hình dự báo", "Mốc: Naive, TB trượt, ETS, ARIMA, Croston, TSB · AI: Prophet, LightGBM",
     "src/mo_hinh_*.py", f"{n['mo_hinh']} mô hình / phương án · {vn(n['du_bao'])} dòng dự báo", DONE, "du_bao, ket_qua_mo_hinh"),
    ("6. Chọn mô hình", "Luật chọn viết trước; chọn trên validation cùng mùa với tập test",
     "src/chon_mo_hinh.py", f"Được chọn: {ma_chon} · sai số {vn(w_chon * 100, 1)}%, theo tuần {vn(wt_chon * 100, 1)}%",
     DONE, "mo_hinh.duoc_chon"),
    ("7. Đẩy vào cơ sở dữ liệu", "Tạo lại CSDL từ schema; nạp theo thứ tự khóa ngoại; tự kiểm tra toàn vẹn",
     "src/nap_database.py", f"{len(tables)} bảng + {len(views)} khung nhìn · {vn(size_mb)} MB · vi phạm khóa ngoại: {fk_loi}",
     DONE, "data/kho_hang.db"),
    ("8. Tham số tồn kho và mô phỏng", "Đọc từ CSDL: chi phí, lead time, MOQ + dự báo được chọn → SS, ROP, EOQ; so sánh 3 chính sách",
     "src/ton_kho.py, src/mo_phong.py", "Bảng trước – sau: Fill Rate, hết hàng, tồn kho, chi phí", DOING, "đọc v_du_bao_chon, dm_sku"),
    ("9. Dashboard", "Đọc từ CSDL: dự báo, cảnh báo đặt hàng, KPI", "app/dashboard.py (Streamlit)",
     "Trình bày trực tiếp trên máy", PLAN, "đọc các khung nhìn"),
]

GROUPS = [("Danh mục", ["dm_nha_cung_cap", "dm_sku", "phan_loai_sku"]),
          ("Lịch và sự kiện", ["lich_su_kien", "lich_ngay_nghi", "lich_khuyen_mai", "su_kien_dot_bien"]),
          ("Giao dịch nhập – xuất – tồn", ["giao_dich_tho", "giao_dich_sach", "nhat_ky_sua_loi"]),
          ("Mô hình và dự báo", ["mo_hinh", "ket_qua_mo_hinh", "du_bao"]),
          ("Hệ thống", ["nhat_ky_chay"])]
PURPOSE = {"dm_nha_cung_cap": "Nhà cung cấp", "dm_sku": "Mã hàng: giá, chi phí đặt hàng, lưu kho, lead time, MOQ",
           "phan_loai_sku": "ABC, XYZ, loại nhu cầu (tính trên tập học)", "lich_su_kien": "Ngày lễ, sự kiện; cờ biết trước 28 ngày",
           "lich_ngay_nghi": "Ngày kho đóng cửa", "lich_khuyen_mai": "Đợt khuyến mãi theo SKU",
           "su_kien_dot_bien": "Bão, cú sốc, đơn B2B; ghi nguồn thật / mô phỏng",
           "giao_dich_tho": "Vùng tạm: nhận nguyên văn file kho, chưa kiểm tra",
           "giao_dich_sach": "Mỗi (ngày, SKU) một dòng, đã đối soát", "nhat_ky_sua_loi": "Truy vết từng dòng đã sửa",
           "mo_hinh": "Danh sách mô hình; mô hình được chọn", "ket_qua_mo_hinh": "Sai số từng mô hình theo tập",
           "du_bao": "Dự báo từng ngày, từng SKU, từng mốc", "nhat_ky_chay": "Mỗi lần nạp: bảng, số dòng, trạng thái"}


def table_card(t):
    rows, cols, fks = info[t]
    lines = []
    for c in cols:
        name, typ, notnull, pk = c[1], c[2], c[3], c[5]
        tag = '<b class="pk">PK</b>' if pk else ""
        if name in fks:
            tag += f'<b class="fk" title="→ {html.escape(fks[name])}">FK → {html.escape(fks[name].split(".")[0])}</b>'
        lines.append(f"<li><code>{name}</code> <span class='typ'>{typ}</span>{tag}</li>")
    return (f'<div class="tcard"><div class="thead"><code>{t}</code><span>{vn(rows)} dòng</span></div>'
            f'<p>{PURPOSE.get(t, "")}</p><details><summary>{len(cols)} cột</summary><ul>{"".join(lines)}</ul></details></div>')


biz_html = "".join(
    f'<div class="bstep"><div class="num">{i}</div><div class="bbody"><h3>{html.escape(t)}</h3>'
    f'<p class="who">{html.escape(who)}</p><p><b>Kết quả:</b> {html.escape(o)}</p><p class="note">{html.escape(note)}</p>'
    f'{chip(st)}</div></div>'
    for k, (i, t, who, o, st, note) in enumerate(business))

data_html = "".join(
    f'<div class="dstep {st[0]}"><div class="dmain"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p>'
    f'<p class="out">{html.escape(o)}</p></div><div class="dmeta"><code>{html.escape(script)}</code>{chip(st)}'
    + (f'<div class="db">CSDL: {html.escape(db)}</div>' if db else "") + "</div></div>"
    + ('<div class="varrow">↓</div>' if k < len(data_steps) - 1 else "")
    for k, (t, d, script, o, st, db) in enumerate(data_steps))

db_html = "".join(f'<section class="grp"><h3>{g}</h3><div class="tgrid">{"".join(table_card(t) for t in ts if t in info)}</div></section>'
                  for g, ts in GROUPS)
fk_list = sorted({(t, col, ref) for t, (_, _, fks) in info.items() for col, ref in fks.items()})
fk_html = "".join(f"<li><code>{t}.{c}</code> → <code>{r}</code></li>" for t, c, r in fk_list)

page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luồng hệ thống</title>
<style>
:root {{ --bg:#f7f7f5; --card:#ffffff; --ink:#111; --ink2:#4a4a46; --muted:#7a7a74; --line:#dcdcd6;
  --accent:#2a78d6; --done:#0c7a3a; --done-bg:#e3f4e9; --doing:#9a5b00; --doing-bg:#fdf0d8;
  --plan:#4a3aa7; --plan-bg:#ecebfa; --out:#55554f; --out-bg:#ececea; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#141413; --card:#1f1f1d; --ink:#f3f3f0;
  --ink2:#c9c8c0; --muted:#9a998f; --line:#3a3a36; --accent:#5a9be6; --done:#5fd08a; --done-bg:#16301f;
  --doing:#f0b55a; --doing-bg:#33270f; --plan:#a99cf0; --plan-bg:#25213f; --out:#bdbdb6; --out-bg:#2b2b28; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 "Segoe UI", system-ui, sans-serif; }}
header {{ padding:24px 32px 8px; }} h1 {{ margin:0; font-size:28px; }} .sub {{ color:var(--ink2); margin:4px 0 0; }}
nav {{ display:flex; gap:8px; padding:12px 32px; position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line); z-index:2; flex-wrap:wrap; }}
nav button {{ font:inherit; font-weight:600; padding:8px 16px; border-radius:8px; border:1px solid var(--line); background:var(--card); color:var(--ink); cursor:pointer; }}
nav button.on {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
main {{ padding:24px 32px 48px; }} .tab {{ display:none; }} .tab.on {{ display:block; }}
h2 {{ margin:0 0 4px; font-size:22px; }} .lead {{ color:var(--ink2); margin:0 0 20px; max-width:900px; }}
.chip {{ display:inline-block; font-size:13px; font-weight:600; padding:2px 10px; border-radius:999px; margin-top:8px; }}
.chip.done {{ color:var(--done); background:var(--done-bg); }} .chip.doing {{ color:var(--doing); background:var(--doing-bg); }}
.chip.plan {{ color:var(--plan); background:var(--plan-bg); }} .chip.out {{ color:var(--out); background:var(--out-bg); }}
.bflow {{ display:grid; grid-template-columns:repeat(4, minmax(0, 260px)); gap:16px 28px; }}
.bstep {{ position:relative; display:flex; gap:10px; background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; }}
.bstep:not(:nth-child(4n)):not(:last-child)::after {{ content:"→"; position:absolute; right:-23px; top:40%; font-size:22px; color:var(--muted); }}
.num {{ flex:none; width:32px; height:32px; border-radius:50%; background:var(--accent); color:#fff; font-weight:700; display:grid; place-items:center; }}
.bstep h3 {{ margin:0 0 4px; font-size:16px; }} .bstep p {{ margin:4px 0; font-size:14px; color:var(--ink2); }}
.who {{ font-weight:600; color:var(--ink) !important; }} .note {{ color:var(--muted) !important; }}
.loop {{ margin-top:16px; padding:12px 16px; border-left:4px solid var(--accent); background:var(--card); border-radius:8px; max-width:900px; }}
.dflow {{ max-width:980px; }}
.dstep {{ display:flex; gap:16px; justify-content:space-between; background:var(--card); border:1px solid var(--line);
  border-left:6px solid var(--line); border-radius:12px; padding:14px 18px; }}
.dstep.done {{ border-left-color:var(--done); }} .dstep.doing {{ border-left-color:var(--doing); }} .dstep.plan {{ border-left-color:var(--plan); }}
.dstep h3 {{ margin:0 0 4px; font-size:17px; }} .dstep p {{ margin:2px 0; color:var(--ink2); font-size:14px; }}
.dstep .out {{ color:var(--ink); font-weight:600; }} .dmeta {{ text-align:right; min-width:230px; }}
.dmeta code {{ font-size:13px; }} .db {{ margin-top:6px; font-size:13px; color:var(--accent); }}
.varrow {{ text-align:center; color:var(--muted); font-size:22px; line-height:1.4; max-width:980px; }}
.honest {{ margin:20px 0 0; padding:12px 16px; background:var(--doing-bg); border-radius:8px; max-width:980px; color:var(--ink); }}
.stats {{ display:flex; flex-wrap:wrap; gap:12px; margin:0 0 20px; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 16px; min-width:170px; }}
.stat b {{ display:block; font-size:24px; }} .stat span {{ color:var(--ink2); font-size:14px; }}
.grp h3 {{ margin:20px 0 8px; font-size:17px; }} .tgrid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:12px; }}
.tcard {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 14px; }}
.thead {{ display:flex; justify-content:space-between; gap:8px; align-items:baseline; }} .thead code {{ font-weight:700; font-size:15px; }}
.thead span {{ color:var(--muted); font-size:13px; white-space:nowrap; }} .tcard p {{ margin:6px 0; font-size:14px; color:var(--ink2); }}
.tcard ul {{ list-style:none; padding:0; margin:6px 0 0; font-size:13px; }} .tcard li {{ padding:2px 0; border-top:1px dashed var(--line); }}
.typ {{ color:var(--muted); }} .pk, .fk {{ font-size:11px; margin-left:6px; padding:0 6px; border-radius:4px; }}
.pk {{ background:var(--done-bg); color:var(--done); }} .fk {{ background:var(--plan-bg); color:var(--plan); }}
summary {{ cursor:pointer; color:var(--accent); font-size:13px; }}
.fks {{ columns:2; font-size:14px; max-width:900px; }} footer {{ color:var(--muted); font-size:13px; padding:0 32px 24px; }}
@media (max-width:700px) {{ header, nav, main {{ padding-left:16px; padding-right:16px; }} .bflow {{ grid-template-columns:1fr; }} .bstep::after {{ display:none; }}
  .dstep {{ flex-direction:column; }} .dmeta {{ text-align:left; }} .fks {{ columns:1; }} }}
</style></head><body>
<header><h1>Luồng hệ thống dự báo nhu cầu và tối ưu tồn kho</h1>
<p class="sub">Đồ án tốt nghiệp · Dữ liệu mô phỏng (121 SKU × 1.096 ngày), không phải số liệu kho thật · Cập nhật {datetime.now().strftime('%d/%m/%Y %H:%M')}</p></header>
<nav><button class="on" data-t="t1">1. Luồng nghiệp vụ</button><button data-t="t2">2. Luồng dữ liệu</button><button data-t="t3">3. Cơ sở dữ liệu</button></nav>
<main>
<section id="t1" class="tab on"><h2>Luồng nghiệp vụ: ai làm gì, theo thứ tự nào</h2>
<p class="lead">Từ số liệu nhập – xuất – tồn hằng ngày đến quyết định đặt hàng và kế hoạch xe. Hệ thống trong đồ án đảm nhận bước 3–6; bước 1, 2, 7 là công việc của các bộ phận trong doanh nghiệp.</p>
<div class="bflow">{biz_html}</div>
<div class="loop"><b>Vòng lặp hằng ngày:</b> hàng về kho → số liệu mới → làm sạch → dự báo lại → cảnh báo đặt hàng. Mỗi tháng đánh giá lại sai số mô hình; khi sai số tăng hoặc có SKU mới thì học lại mô hình.</div>
</section>
<section id="t2" class="tab"><h2>Luồng dữ liệu: dữ liệu đi qua những bước nào</h2>
<p class="lead">Mỗi bước là một chương trình chạy lại được, có kiểm tra kết quả. Ô màu xanh: đã làm; vàng: đang làm; tím: kế hoạch. Dòng "CSDL" cho biết bước đó ghi vào / đọc từ bảng nào trong cơ sở dữ liệu.</p>
<div class="dflow">{data_html}</div>
<p class="honest"><b>Hiện trạng (nói rõ khi trình bày):</b> bước 1–6 xử lý trên file; bước 7 đẩy toàn bộ dữ liệu và kết quả vào cơ sở dữ liệu, kèm kiểm tra toàn vẹn. Từ bước 8, các bước đọc trực tiếp từ cơ sở dữ liệu.</p>
</section>
<section id="t3" class="tab"><h2>Cơ sở dữ liệu: <code>data/kho_hang.db</code> (SQLite)</h2>
<p class="lead">Thiết kế ở <code>database/schema.sql</code>: khóa chính, khóa ngoại và ràng buộc kiểm tra chặn dữ liệu sai ngay khi ghi (ví dụ: lượng xuất âm, mã hàng không có trong danh mục, trùng ngày – SKU, dự báo cho ngày trước mốc).</p>
<div class="stats">
<div class="stat"><b>{len(tables)}</b><span>bảng · {len(views)} khung nhìn</span></div>
<div class="stat"><b>{vn(sum(v[0] for v in info.values()))}</b><span>dòng dữ liệu</span></div>
<div class="stat"><b>{fk_loi}</b><span>vi phạm khóa ngoại</span></div>
<div class="stat"><b>{lech}</b><span>dòng lệch đẳng thức kho</span></div>
<div class="stat"><b>{vn(size_mb)} MB</b><span>một file, không cần máy chủ</span></div></div>
{db_html}
<section class="grp"><h3>Quan hệ khóa ngoại</h3><ul class="fks">{fk_html}</ul>
<p class="lead">Khung nhìn: {", ".join(f"<code>{v}</code>" for v in views)}. Truy vấn mẫu để trình bày: <code>database/truy_van_mau.sql</code> hoặc <code>python src/xem_database.py</code>.</p></section>
</section>
</main>
<footer>Tạo tự động bởi <code>src/tao_trang_luong.py</code> từ cơ sở dữ liệu. Chạy lại sau mỗi lần cập nhật dữ liệu.</footer>
<script>
const show = id => {{
  document.querySelectorAll('nav button').forEach(x => x.classList.toggle('on', x.dataset.t === id));
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', t.id === id));
}};
document.querySelectorAll('nav button').forEach(b => b.onclick = () => {{ show(b.dataset.t); history.replaceState(null, '', '#' + b.dataset.t.slice(1)); }});
if (/^#[123]$/.test(location.hash)) show('t' + location.hash.slice(1));
</script></body></html>"""

os.makedirs("trinh_bay", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print(f"Da ghi {OUT}")
