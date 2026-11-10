// Tao bao cao Word tong hop do an. So lieu doc tu so_lieu.json (gom tu CSDL / file ket qua bang gom_so_lieu.py).
// Chay: node tao_bao_cao.js <so_lieu.json> <thu_muc_du_an> <anh_dashboard.png> <file_ra.docx>
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, ImageRun, TableOfContents, Footer, PageNumber, PageBreak, LevelFormat, VerticalAlign,
} = require("docx");

const [, , JSON_PATH, DU_AN, ANH_DASH, OUT] = process.argv;
const D = JSON.parse(fs.readFileSync(JSON_PATH, "utf8"));
const FONT = "Times New Roman";
const CM = 567;
const TEXT_W = Math.round((21 - 3 - 2) * CM);                 // be rong vung chu (DXA)

// ---------------------------------------------------------------- dinh dang so kieu Viet Nam
const vn = (x, nd = 1) => {
  const s = Number(x).toFixed(nd).split(".");
  s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return s.length > 1 ? `${s[0]},${s[1]}` : s[0];
};
const pt = (x, nd = 1) => `${x > 0 ? "+" : x < 0 ? "−" : ""}${vn(Math.abs(100 * x), nd)}%`;        // ty le -> %
const dau = (x, nd = 1) => `${x > 0 ? "+" : x < 0 ? "−" : ""}${vn(Math.abs(x), nd)}`;

// ---------------------------------------------------------------- khoi noi dung
const P = (text, o = {}) => new Paragraph({
  alignment: o.align ?? AlignmentType.JUSTIFIED,
  indent: o.noIndent ? undefined : { firstLine: CM },
  spacing: o.spacing,
  keepNext: o.keepNext,
  children: (Array.isArray(text) ? text : [text]).map((t) => (typeof t === "string" ? new TextRun(t) : t)),
});
const B = (t) => new TextRun({ text: t, bold: true });
const I = (t) => new TextRun({ text: t, italics: true });
const gach = (text) => new Paragraph({
  numbering: { reference: "gach", level: 0 }, alignment: AlignmentType.JUSTIFIED,
  children: (Array.isArray(text) ? text : [text]).map((t) => (typeof t === "string" ? new TextRun(t) : t)),
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const nguon = (t) => new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { before: 40, after: 160 },
  children: [new TextRun({ text: `Nguồn: ${t}`, italics: true, size: 22 })],
});
const SO = { bang: {}, hinh: {} };
let chuong = 0;
const soMuc = (loai) => { SO[loai][chuong] = (SO[loai][chuong] || 0) + 1; return `${chuong}.${SO[loai][chuong]}`; };
const tenBang = (t) => new Paragraph({
  alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 },
  children: [new TextRun({ text: `Bảng ${soMuc("bang")}. `, bold: true }), new TextRun({ text: t, bold: true })],
});
const vien = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const bang = (dau_cot, dong, rong, o = {}) => {
  const tong = rong.reduce((a, b) => a + b, 0);
  const w = rong.map((x) => Math.round((x / tong) * TEXT_W));
  w[w.length - 1] = TEXT_W - w.slice(0, -1).reduce((a, b) => a + b, 0);
  let giu = false;
  const o_ = (text, j, the) => new TableCell({
    width: { size: w[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    shading: the ? { type: ShadingType.CLEAR, color: "auto", fill: "D9E2EC" } : (o.toDam && o.toDam(text, j) ? { type: ShadingType.CLEAR, color: "auto", fill: "FFF2B3" } : undefined),
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    borders: { top: vien, bottom: vien, left: vien, right: vien },
    children: [new Paragraph({
      alignment: (j === 0 || (o.traiCot || []).includes(j)) ? AlignmentType.LEFT : AlignmentType.CENTER,
      spacing: { line: 252, before: 0, after: 0 }, keepNext: giu,
      children: [new TextRun({ text: String(text), bold: the || (o.dongDam && o.dongDam(text)), size: 23 })],
    })],
  });
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: w,
    rows: [(giu = true, new TableRow({ tableHeader: true, children: dau_cot.map((t, j) => o_(t, j, true)) })),
      ...dong.map((r, i) => { giu = dong.length <= 10 && i < dong.length - 1; return new TableRow({ cantSplit: true, children: r.map((t, j) => o_(t, j, false)) }); })],
  });
};
const kichThuocPng = (f) => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
const hinh = (file, chuThich, nguonHinh, rongCm = 15.5) => {
  const [w, h] = kichThuocPng(file);
  const wp = Math.round(rongCm * 37.8);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: wp, height: Math.round((wp * h) / w) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { after: 20 },
      children: [new TextRun({ text: `Hình ${soMuc("hinh")}. `, italics: true, bold: true }), new TextRun({ text: chuThich, italics: true })] }),
    nguon(nguonHinh),
  ];
};
const KQ = path.join(DU_AN, "reports", "ket_qua");
const NG_MP = "dữ liệu mô phỏng của đề tài (121 mã × 1.096 ngày), tính bằng chương trình của đề tài";

// ---------------------------------------------------------------- so lieu dung nhieu lan
const M = D.mo_hinh, TK = D.ton_kho, V4 = D.v4, T = V4.test;
const ai = TK.cong_thuc_du_bao_ai_hc, aiK = TK.cong_thuc_du_bao_ai, moc = TK.cong_thuc_du_bao_moc, ht = TK.hien_trang;
const lech = (a, b) => a / b - 1;
const du = D.du_lieu;
const kh = T.khoang;

// ================================================================ BIA
const bia = [
  P([B("[TÊN TRƯỜNG]")], { align: AlignmentType.CENTER, noIndent: true }),
  P([B("[TÊN KHOA / NGÀNH LOGISTICS VÀ QUẢN LÝ CHUỖI CUNG ỨNG]")], { align: AlignmentType.CENTER, noIndent: true }),
  new Paragraph({ spacing: { before: 1800 }, children: [] }),
  P([new TextRun({ text: "BÁO CÁO TỔNG HỢP ĐỒ ÁN TỐT NGHIỆP", bold: true, size: 30 })], { align: AlignmentType.CENTER, noIndent: true }),
  new Paragraph({ spacing: { before: 400 }, children: [] }),
  ...["ỨNG DỤNG TRÍ TUỆ NHÂN TẠO", "TRONG DỰ BÁO NHU CẦU VÀ", "TỐI ƯU HÓA QUẢN LÝ TỒN KHO"].map((t) =>
    P([new TextRun({ text: t, bold: true, size: 34 })], { align: AlignmentType.CENTER, noIndent: true })),
  P([I("Áp dụng cho kho tổng của một chuỗi siêu thị / bách hóa (dữ liệu mô phỏng)")], { align: AlignmentType.CENTER, noIndent: true }),
  new Paragraph({ spacing: { before: 1600 }, children: [] }),
  ...[["Sinh viên thực hiện", "[Họ và tên – MSSV]"], ["Lớp", "[Lớp]"], ["Giảng viên hướng dẫn", "[Học hàm, học vị, họ và tên]"]]
    .map(([a, b]) => new Paragraph({ indent: { left: 3 * CM }, spacing: { after: 80 }, children: [new TextRun({ text: `${a}: `, bold: true }), new TextRun(b)] })),
  new Paragraph({ spacing: { before: 2000 }, children: [] }),
  P([B("[Thành phố], tháng 11 năm 2026")], { align: AlignmentType.CENTER, noIndent: true }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ================================================================ MUC LUC, VIET TAT, TOM TAT
const mucLuc = [
  P([new TextRun({ text: "MỤC LỤC", bold: true, size: 28 })], { align: AlignmentType.CENTER, noIndent: true }),
  new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-3" }),
  P([I("(Nếu mục lục chưa hiện số trang: bấm chuột phải vào mục lục → Update Field → Update entire table.)")], { noIndent: true, align: AlignmentType.LEFT }),
  new Paragraph({ children: [new PageBreak()] }),
  P([new TextRun({ text: "DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ", bold: true, size: 28 })], { align: AlignmentType.CENTER, noIndent: true }),
  bang(["Từ viết tắt / thuật ngữ", "Giải thích"], [
    ["AI", "Trí tuệ nhân tạo (Artificial Intelligence)"],
    ["ABC / XYZ", "Phân nhóm mặt hàng theo giá trị xuất kho (A cao → C thấp) và độ ổn định nhu cầu (X ổn định → Z thất thường / mùa vụ)"],
    ["Bias", "Độ lệch có hệ thống của dự báo = Σ(thực tế − dự báo) / Σ thực tế; dương là dự báo thiếu"],
    ["CSDL", "Cơ sở dữ liệu (SQLite, tệp data/kho_hang.db)"],
    ["EOQ", "Lượng đặt hàng kinh tế (Economic Order Quantity)"],
    ["Fill Rate", "Tỉ lệ nhu cầu được đáp ứng ngay từ kho"],
    ["Lead time", "Thời gian từ lúc đặt hàng đến lúc hàng về kho"],
    ["MOQ", "Lượng đặt tối thiểu nhà cung cấp quy định"],
    ["ROP", "Điểm đặt hàng (Reorder Point)"],
    ["SKU / mã hàng", "Đơn vị quản lý tồn kho (Stock Keeping Unit)"],
    ["SS", "Tồn kho an toàn (Safety Stock)"],
    ["WMAPE", "Sai số dự báo theo trọng số = Σ|thực tế − dự báo| / Σ thực tế; càng thấp càng tốt"],
    ["Chi phí liên quan", "Chi phí đặt hàng + chi phí lưu kho + lợi nhuận mất do thiếu hàng"],
    ["Validation / test", "Tập dùng để chọn phương án / tập chỉ dùng để báo cáo kết quả cuối"],
  ], [3, 9], { traiCot: [1] }),
  new Paragraph({ children: [new PageBreak()] }),
  P([new TextRun({ text: "TÓM TẮT", bold: true, size: 28 })], { align: AlignmentType.CENTER, noIndent: true }),
  P(`Đề tài xây dựng một quy trình hoàn chỉnh cho kho tổng của một chuỗi siêu thị: từ dữ liệu nhập – xuất – tồn hằng ngày, làm sạch, dự báo nhu cầu 28 ngày tới bằng trí tuệ nhân tạo, tính tồn kho an toàn (SS), điểm đặt hàng (ROP), lượng đặt kinh tế (EOQ), đến mô phỏng 12 tháng để đo lợi ích và một công cụ hỗ trợ quyết định cho người lập kế hoạch. Dữ liệu là dữ liệu mô phỏng (${du.sku} mã hàng × ${vn(du.ngay, 0)} ngày) vì chưa có dữ liệu kho thật; lịch lễ, bão, sale và giá bán lẻ của 37 mã lấy từ nguồn thật. Mọi lựa chọn mô hình được làm trên tập validation theo luật ghi trước; tập test chỉ dùng để báo cáo.`),
  P("Kết quả chính trên 12 tháng kiểm tra (01/10/2025 – 29/09/2026):", { keepNext: true }),
  gach([B("Dự báo: "), `mô hình kết hợp LightGBM + Prophet theo nhóm hàng, cập nhật mỗi tuần, có sai số theo ngày WMAPE ${vn(M.ket_hop_v4.wmape, 3)} và lệch ${pt(M.ket_hop_v4.bias_pct)}, giảm ${vn(100 * (1 - M.ket_hop_v4.wmape / M.seasonal_naive_7.wmape), 0)}% sai số so với phương pháp lặp lại tuần trước; gần mức sai số tối thiểu không thể tránh (≈ ${vn(V4.san[0], 3)}) do nhu cầu ngẫu nhiên.`]),
  gach([B("Khoảng dự báo: "), `mỗi con số dự báo kèm khoảng 80% / 95%; trên tập kiểm tra, thực tế rơi vào khoảng đúng ${vn(kh.theo_ngay["80"].phu)}% / ${vn(kh.theo_ngay["95"].phu)}% số ngày.`]),
  gach([B("Tồn kho: "), `chính sách AI + hiệu chỉnh lệch đạt Fill Rate ${vn(ai.fill_rate_pt, 2)}%, giảm ${vn(-100 * lech(ai.chi_phi_lien_quan_trieu, moc.chi_phi_lien_quan_trieu))}% chi phí liên quan so với cùng công thức dùng dự báo trung bình trượt; so với "hiện trạng" (người lập kế hoạch được biết trước nhu cầu kỳ vọng) tồn kho ${pt(lech(ai.ton_tb_trieu_vnd, ht.ton_tb_trieu_vnd))}, số ngày thiếu hàng ${pt(lech(ai.so_ngay_sku_thieu, ht.so_ngay_sku_thieu), 0)}, chi phí liên quan ${pt(lech(ai.chi_phi_lien_quan_trieu, ht.chi_phi_lien_quan_trieu))}.`]),
  gach([B("Rủi ro và độ nhạy: "), "bảng rủi ro định lượng từ dữ liệu (bão, thời tiết, dịch, khuyến mãi, đơn B2B, nhà cung cấp chậm); tắc cảng trễ 3–7 ngày chỉ làm Fill Rate giảm 0,5–1,5 điểm; lead time dài ra lâu dài mà không cập nhật công thức là rủi ro lớn nhất."]),
  gach([B("Nghiệp vụ kho: "), "thêm chỉ số kho, gom đơn, chấm điểm nhà cung cấp, hạn sử dụng theo lô, sức chứa, newsvendor cho hàng dịp lễ và trữ hàng phiên livestream; phát hiện chính sách còn đặt quá tay với hàng chỉ bán dịp lễ, newsvendor đã thử nhưng tập kiểm tra chưa xác nhận nên chưa đưa vào chính sách."]),
  gach([B("Kiểm chứng trên số thật: "), `trên số bán thật M5, mô hình giảm ${vn(100 * (1 - D.m5.ket_hop_dl.test.wmape / D.m5.tb_truot.test.wmape))}% sai số so với trung bình trượt, so với ${vn(100 * (1 - M.ket_hop_v4.wmape / M.tb_truot_28_tuan.wmape), 0)}% trên dữ liệu mô phỏng; số thật Dominick's cho thấy mức tài trợ khuyến mãi và đuôi nhu cầu khác giả định ban đầu.`]),
  gach([B("Hệ thống: "), "CSDL SQLite chạy lại được từ đầu, dashboard 5 màn (Hôm nay, Dự báo, Mặt hàng, Kịch bản & kết quả, Dữ liệu & phương pháp) có duyệt đơn, tải phiếu đặt hàng và “Thử nếu…”, dữ liệu xuất cho Power BI."]),
  gach([B("Dự báo cho ngày chưa xảy ra: "), `màn Dự báo đứng ở ngày cuối của dữ liệu, dự báo 28 ngày tới, chạy lại mô hình khi bấm (trùng bản đã chấm), giải thích từng con số theo nhóm yếu tố và thử nếu bật khuyến mãi; trên toàn kho mô hình tăng trung vị × ${vn(D.ss_km.mo_hinh.p50, 2)} khi bật khuyến mãi, sát mức lịch sử × ${vn(D.ss_km.lich_su.p50, 2)}.`]),
  gach([B("AI có giá trị ở đâu: "), `trên bộ dữ liệu kho dựng từ số bán thật M5, AI chỉ giảm ${vn(-100 * (D.m5_tk.cong_thuc_du_bao_ai_hc.cp / D.m5_tk.cong_thuc_du_bao_moc.cp - 1))}% chi phí tồn kho so với dự báo mốc, không do giả định chi phí đặt; trên mô phỏng, ${vn(100 * D.z.ton)}% mức giảm tồn kho đến từ hàng mùa vụ (nhóm Z), loại hàng M5 gần như không có.`]),
  new Paragraph({ children: [new PageBreak()] }),
];

// ================================================================ CHUONG 1
chuong = 1;
const c1 = [
  H1("CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI"),
  H2("1.1. Bối cảnh và lý do chọn đề tài"),
  P("Tồn kho là khoản chi phí lớn của hoạt động logistics: giữ nhiều hàng làm đọng vốn, tăng chi phí lưu kho và rủi ro hàng tồn; giữ ít hàng dẫn đến hết hàng, mất doanh thu. Mọi quyết định đặt hàng đều bắt đầu từ một con số dự báo nhu cầu. Nhu cầu hàng tiêu dùng tại Việt Nam có mùa vụ mạnh và lệch lịch (Tết Nguyên đán, Trung thu theo âm lịch), chịu tác động của khuyến mãi, các đợt sale, bão lũ; số bán ở những ngày hết hàng thấp hơn nhu cầu thật. Đề tài kiểm chứng liệu trí tuệ nhân tạo có giúp dự báo tốt hơn và từ đó giảm chi phí tồn kho một cách đo được hay không."),
  H2("1.2. Mục tiêu"),
  gach("Xây dựng mô hình dự báo nhu cầu theo ngày cho từng mã hàng, so sánh công bằng với các phương pháp đơn giản."),
  gach("Chuyển dự báo thành tham số tồn kho (SS, ROP, EOQ) và quy tắc đặt hàng; đo lợi ích bằng mô phỏng 12 tháng."),
  gach("Nhận diện và định lượng các rủi ro ảnh hưởng nhu cầu; thử độ nhạy của chính sách trước các cú sốc."),
  gach("Xây dựng công cụ hỗ trợ quyết định cho người lập kế hoạch kho, chạy lại được toàn bộ từ dữ liệu."),
  H2("1.3. Phạm vi và đối tượng"),
  P(`Đối tượng là kho tổng (trung tâm phân phối) của một chuỗi siêu thị / bách hóa với ${du.sku} mã hàng thuộc ${du.nhom} nhóm hàng, ${du.ncc} nhà cung cấp, dữ liệu 3 năm từ 01/10/2023 đến 30/09/2026. Phạm vi gồm dự báo nhu cầu, chính sách đặt hàng và tồn kho; không gồm vận tải, xếp dỡ và tối ưu chuyến xe.`),
  H2("1.4. Dữ liệu và nguyên tắc trung thực"),
  P(["Dữ liệu là ", B("dữ liệu mô phỏng"), " do chưa có dữ liệu từ kho thật. Các thông tin lấy từ nguồn thật: lịch lễ Tết, Trung thu, các đợt sale 11.11 / 12.12 / Black Friday, ngày các cơn bão (ví dụ bão số 3 Yagi 07/09/2024) và giá bán lẻ thị trường của 37 mã (tra ngày 24/10/2026). Các thông tin là giả định: lượng bán từng ngày, mức tăng do lễ / bão / khuyến mãi, giá vốn, chi phí đặt hàng và lưu kho, thời gian giao hàng, lỗi cài sẵn trong dữ liệu thô. Mục tiêu là xây dựng ", B("quy trình"), " và so sánh các cách làm trên cùng dữ liệu; khi có dữ liệu thật cùng cấu trúc, chạy lại toàn bộ là ra kết quả thật."]),
  H2("1.5. Phương pháp và quy trình"),
  P("Quy trình gồm 7 bước, mỗi bước là một chương trình chạy lại được và ghi kết quả vào CSDL:", { keepNext: true }),
  tenBang("Các bước của quy trình"),
  bang(["Bước", "Nội dung", "Kết quả"], [
    ["1. Làm sạch", "Phát hiện và sửa lỗi dữ liệu thô, đánh dấu ngày hết hàng và ngày kho nghỉ", "Dữ liệu sạch, nhật ký sửa lỗi"],
    ["2. Đặc trưng", "Lịch lễ, âm lịch, khuyến mãi, mùa, số bán quá khứ", "Bảng đặc trưng theo ngày × mã"],
    ["3. Khám phá dữ liệu", "Mùa vụ, thứ trong tuần, khuyến mãi, phân nhóm ABC × XYZ", "8 biểu đồ, nhận xét"],
    ["4. Dự báo", "Mô hình mốc, Prophet, LightGBM, kết hợp; cập nhật mỗi tuần", "Dự báo 28 ngày + khoảng 80 / 95%"],
    ["5. Tồn kho", "SS, ROP, EOQ, quy tắc đặt hàng", "Tham số từng mã"],
    ["6. Mô phỏng", "12 tháng theo từng ngày cho 4 chính sách; thử độ nhạy", "Bảng trước – sau"],
    ["7. Hỗ trợ quyết định", "CSDL, dashboard, dữ liệu Power BI", "Công cụ cho người lập kế hoạch"],
  ], [2.2, 6, 3.8], { traiCot: [1, 2] }),
  nguon("đề tài."),
  H2("1.6. Nguyên tắc đánh giá"),
  gach([B("Chia theo thời gian: "), "mô hình chỉ dùng dữ liệu đến ngày lập dự báo; không trộn ngẫu nhiên."]),
  gach([B("Hai tập riêng biệt: "), "validation (01/10/2024 – 29/09/2025, cùng mùa với tập kiểm tra) để chọn phương án; test (01/10/2025 – 29/09/2026) chỉ để báo cáo, chạy một lần."]),
  gach([B("Luật ghi trước: "), "điều kiện giữ / bỏ một cải tiến được ghi vào báo cáo trước khi chạy (ví dụ WMAPE phải giảm ít nhất 0,005 và lệch không tăng quá 1 điểm)."]),
  gach([B("Đáp án chỉ để chấm: "), "nhu cầu thật (kể cả ngày hết hàng) chỉ dùng để chấm kết quả tồn kho, không đưa vào mô hình."]),
];

// ================================================================ CHUONG 2
chuong = 2;
const ab = Object.fromEntries(D.abcxyz.map(([a, x, n]) => [`${a}${x}`, n]));
const c2 = [
  H1("CHƯƠNG 2. DỮ LIỆU VÀ CHUẨN BỊ DỮ LIỆU"),
  H2("2.1. Mô tả dữ liệu"),
  tenBang("Tổng quan dữ liệu"),
  bang(["Hạng mục", "Giá trị"], [
    ["Số mã hàng / nhóm hàng / nhà cung cấp", `${du.sku} / ${du.nhom} / ${du.ncc}`],
    ["Thời gian", `${vn(du.ngay, 0)} ngày (01/10/2023 – 30/09/2026)`],
    ["Dòng nhập – xuất – tồn (sau làm sạch)", vn(du.dong, 0)],
    ["Dòng dữ liệu thô", vn(du.tho, 0)],
    ["Lịch khuyến mãi / sự kiện lịch / sự kiện đột biến", `${vn(du.km, 0)} đợt / ${du.le} ngày / ${du.sk} sự kiện`],
    ["Tỉ lệ ngày-mã hết hàng (ngày kho mở cửa)", `${vn(100 * du.het)}%`],
  ], [6, 6]),
  nguon(NG_MP + "."),
  H2("2.2. Làm sạch dữ liệu"),
  P(`Từ ${vn(du.tho, 0)} dòng thô, chương trình loại ${vn(du.tho - du.dong, 0)} dòng trùng và sửa ${du.sua} dòng lỗi (${D.loi.map(([l, n]) => `${n} dòng ${l === "thieu_qty_out" ? "thiếu số xuất" : "nhập sai giá trị bất thường"}`).join(", ")}), mọi lần sửa ghi vào nhật ký. Ngày hết hàng (số bán thấp hơn nhu cầu thật) và ngày kho nghỉ không được coi là nhu cầu: bị bỏ khỏi huấn luyện và chấm điểm dự báo.`),
  H2("2.3. Đặc trưng cho mô hình"),
  P("Đặc trưng được chia theo một nguyên tắc: chỉ thông tin biết trước tại ngày lập dự báo mới được dùng cho 28 ngày tới.", { keepNext: true }),
  gach([B("Biết trước: "), "thứ trong tuần, tháng, mùa, khoảng cách đến / sau Tết và các lễ, ngày sale, lịch khuyến mãi do bộ phận bán hàng gửi, giá bán, số bán cùng ngày âm lịch năm trước."]),
  gach([B("Không biết trước 28 ngày: "), "bão lũ, nắng nóng, rét đậm, dịch bệnh, tin đồn giá. Các yếu tố này không đưa vào dự báo mà được xử lý bằng khoảng dự báo, tồn kho an toàn và bảng rủi ro (Chương 4)."]),
  H2("2.4. Phân nhóm ABC × XYZ"),
  tenBang("Số mã hàng theo nhóm ABC × XYZ (tính trên dữ liệu huấn luyện)"),
  bang(["ABC \\ XYZ", "X (ổn định)", "Y (dao động vừa)", "Z (mùa vụ, thất thường)"], ["A", "B", "C"].map((a) => [a, ab[`${a}X`] || 0, ab[`${a}Y`] || 0, ab[`${a}Z`] || 0]), [3, 3, 3, 3]),
  nguon(NG_MP + "."),
  H2("2.5. Phát hiện từ khám phá dữ liệu"),
  gach("Nhu cầu gần như đi ngang qua 3 năm; biến động chủ yếu do mùa và sự kiện."),
  gach("Đỉnh mùa vụ trùng Tết (tháng 1–2), mùa hè, Trung thu (tháng 9), Noel (tháng 12); một số nhóm (đồ chơi, trang trí, quà tặng) bán gấp nhiều lần bình thường trong mùa."),
  gach("Chủ nhật bán thấp hơn hẳn các ngày khác; khuyến mãi làm số bán tăng trung vị khoảng 50%."),
  ...hinh(path.join(DU_AN, "reports", "eda", "h04_chi_so_mua.png"), "Chỉ số mùa vụ theo nhóm hàng và tháng", NG_MP + "."),
];

// ================================================================ CHUONG 3
chuong = 3;
const TEN_MH = { naive: "Lấy ngày gần nhất", seasonal_naive_7: "Lặp lại tuần trước", tb_truot_28: "Trung bình trượt 28 ngày", ets: "ETS (Holt-Winters)",
  croston_sba: "Croston SBA", tsb: "TSB", arima: "ARIMA (chỉ nhóm A)", prophet: "Prophet", lightgbm: "LightGBM",
  ket_hop_theo_nhom_v2: "Kết hợp theo nhóm (v2)", ket_hop_v3: "Kết hợp v3 (cập nhật 28 ngày)", ket_hop_v4: "Kết hợp v4 – cập nhật mỗi tuần (chọn)",
  tb_truot_28_tuan: "Trung bình trượt 28 ngày, cập nhật mỗi tuần" };
const dsMH = ["naive", "seasonal_naive_7", "ets", "tsb", "croston_sba", "tb_truot_28", "tb_truot_28_tuan", "arima", "prophet", "lightgbm", "ket_hop_theo_nhom_v2", "ket_hop_v3", "ket_hop_v4"];
const v2 = D.mo_hinh_val2;
const c3 = [
  H1("CHƯƠNG 3. DỰ BÁO NHU CẦU"),
  H2("3.1. Khung đánh giá"),
  P("Mọi mô hình được chấm cùng một cách: lập dự báo tại nhiều mốc, mỗi mốc dự báo 28 ngày tới chỉ với dữ liệu đến mốc đó, rồi so với nhu cầu tin được. Hai chỉ số chính là WMAPE (sai số tuyệt đối theo trọng số, càng thấp càng tốt) và Bias (lệch có hệ thống; dương là dự báo thiếu, dễ dẫn đến hết hàng)."),
  H2("3.2. Các mô hình"),
  gach([B("Mô hình mốc: "), "lấy ngày gần nhất, lặp lại tuần trước, trung bình trượt 28 ngày, ETS, Croston, TSB (cho hàng bán thưa), ARIMA (chỉ nhóm A)."]),
  gach([B("Prophet: "), "mỗi mã một mô hình, có mùa năm / tuần, lịch lễ, sale và khuyến mãi làm biến giải thích."]),
  gach([B("LightGBM: "), "một mô hình chung cho cả 121 mã, hàm mất mát Tweedie; dự báo theo tầm (3 mô hình cho ngày 1–7, 8–14, 15–28 sau mốc), đặc trưng lịch sự kiện và số bán cùng ngày âm lịch năm trước."]),
  gach([B("Kết hợp: "), "trung bình có trọng số LightGBM – Prophet theo nhóm XYZ (trọng số LightGBM X 0,9 · Y 1,0 · Z 0,7), chọn trên validation."]),
  gach([B("Cập nhật mỗi tuần (vòng 4): "), "chạy lại mô hình kết hợp mỗi 7 ngày thay vì mỗi 28 ngày, mỗi ngày dùng bản dự báo mới nhất – đúng cách một kho vận hành thật."]),
  H2("3.3. Kết quả so sánh trên tập kiểm tra"),
  tenBang("Sai số dự báo của các mô hình trên tập kiểm tra"),
  bang(["Mô hình", "WMAPE", "WMAPE tuần", "Bias", "WMAPE nhóm Z"],
    dsMH.map((k) => [TEN_MH[k], vn(M[k].wmape, 3), vn(M[k].wmape_tuan, 3), pt(M[k].bias_pct), M[k].wmape_z == null ? "–" : vn(M[k].wmape_z, 3)]),
    [5.5, 1.6, 1.8, 1.6, 2], { dongDam: (t) => String(t).includes("(chọn)"), toDam: (t, j) => false }),
  nguon(NG_MP + ". ARIMA chỉ chạy cho mã nhóm A nên chỉ so được trong nhóm A. Hai mô hình cập nhật mỗi tuần chấm trên bản mới nhất cho mỗi ngày."),
  ...hinh(path.join(KQ, "k01_xep_hang_mo_hinh.png"), "Xếp hạng sai số dự báo theo ngày của các mô hình (tập kiểm tra)", NG_MP + "."),
  P(`Mô hình AI kết hợp cập nhật mỗi tuần sai ${vn(100 * M.ket_hop_v4.wmape)}% theo ngày và ${vn(100 * M.ket_hop_v4.wmape_tuan)}% theo tuần, so với ${vn(100 * M.tb_truot_28_tuan.wmape)}% của trung bình trượt 28 ngày cũng cập nhật mỗi tuần. Các phương pháp thống kê cổ điển không tốt hơn trung bình trượt; lợi thế lớn nhất của AI ở nhóm mùa vụ Z (WMAPE ${vn(M.ket_hop_v4.wmape_z, 3)} so với ${vn(M.tb_truot_28_tuan.wmape_z, 3)}).`),
  ...hinh(path.join(KQ, "k02_du_bao_vs_thuc_te_tet.png"), "Dự báo so với thực tế quanh Tết và Trung thu 2026 (tổng toàn kho)", NG_MP + "."),
  H2("3.4. Quá trình nâng cấp có kiểm soát"),
  P("Mỗi cải tiến chỉ được giữ nếu đạt luật ghi trước trên validation. Các vòng nâng cấp và kết quả:", { keepNext: true }),
  tenBang("Các vòng nâng cấp dự báo"),
  bang(["Vòng", "Cải tiến", "Kết quả theo luật"], [
    ["2", "Kết hợp LightGBM – Prophet theo nhóm XYZ", `Giữ; test WMAPE ${vn(M.ket_hop_theo_nhom_v2.wmape, 3)}, Bias ${pt(M.ket_hop_theo_nhom_v2.bias_pct)}`],
    ["3", "Dự báo theo tầm + lịch sự kiện / âm lịch", `Giữ; test WMAPE ${vn(M.ket_hop_v3.wmape, 3)}, Bias ${pt(M.ket_hop_v3.bias_pct)} (lần đầu đạt ±5%)`],
    ["3", "Dò tham số LightGBM (8 cấu hình)", "Bỏ: chỉ giảm 0,0016"],
    ["4", "Tự hiệu chỉnh lệch từ sai số đã qua", `Bỏ: lệch giảm một nửa nhưng WMAPE tăng (${vn(V4.B1.truoc.WMAPE, 3)} → ${vn(V4.B1.WMAPE, 3)})`],
    ["4", "Cảnh báo bão 4 ngày trước", `Bỏ: chỉ 1–2 trận để học, WMAPE cửa sổ bão tăng`],
    ["4", "Cập nhật dự báo mỗi tuần", `Giữ; validation ${vn(V4.B3.truoc.WMAPE, 3)} → ${vn(V4.B3.WMAPE, 3)}; test ${vn(T.test_cung_dong.v3.WMAPE, 3)} → ${vn(T.test.v4.WMAPE, 3)}`],
  ], [1, 5, 6], { traiCot: [1, 2] }),
  nguon("đề tài (luật và nhật ký từng vòng trong báo cáo kỹ thuật docs/10)."),
  P(["Hai cải tiến bị bỏ vẫn cho bài học: với sai số theo ngày, con số tối ưu là ", B("trung vị"), " (thấp hơn trung bình khi nhu cầu lệch phải), nên phần lệch phải xử lý ở khâu tồn kho chứ không phải sửa con số dự báo; rủi ro hiếm như bão không sửa được bằng hệ số cố định khi có quá ít dữ liệu."]),
  H2("3.5. Mức sai số tối thiểu và khoảng dự báo"),
  P(`Nhu cầu mỗi ngày có phần ngẫu nhiên: ngay cả khi biết đúng nhu cầu kỳ vọng, WMAPE theo ngày vẫn còn khoảng ${vn(V4.san[0], 3)} (nhóm X ${vn(V4.san[1].X, 3)}, Y ${vn(V4.san[1].Y, 3)}, Z ${vn(V4.san[1].Z, 3)}). Vì vậy dự báo "gần đúng" được trình bày theo hai cách: kèm khoảng dao động, và gộp theo đúng mức ra quyết định (theo tuần, theo tổng thời gian chờ hàng).`),
  tenBang("Độ tin cậy của khoảng dự báo trên tập kiểm tra"),
  bang(["Mức", "Theo ngày: tỉ lệ thực tế nằm trong khoảng", "Độ rộng (trung vị, × dự báo)", "Tổng trong lead time: tỉ lệ nằm trong khoảng", "Độ rộng"],
    ["80", "95"].map((m) => [`${m}%`, `${vn(kh.theo_ngay[m].phu)}%`, vn(kh.theo_ngay[m].do_rong_trung_vi, 2), `${vn(kh.lead_time[m].phu)}%`, vn(kh.lead_time[m].do_rong_trung_vi, 2)]),
    [1.2, 3.5, 2.5, 3.5, 1.5]),
  nguon(NG_MP + ". Khoảng học theo từng mốc chỉ từ dữ liệu đã có thực tế tại mốc đó."),
  P("Ví dụ sữa tươi Vinamilk (SKU009), mốc 20/01/2025: ngày 21/01 dự báo 433 thùng, khoảng 80% là 236 – 677 thùng, thực tế 283; cả 7 ngày đầu thực tế đều nằm trong khoảng 80%. Tổng 3 ngày chờ hàng dự báo 1.127 thùng (khoảng 80%: 872 – 1.454), thực tế 781 – nằm ngoài khoảng 80% nhưng trong khoảng 95%, đúng tinh thần “80% thì vẫn còn 20% trượt”."),
];

// ================================================================ CHUONG 4
chuong = 4;
const RR = D.rui_ro.filter((r) => r.rui_ro);
const c4 = [
  H1("CHƯƠNG 4. NHẬN DIỆN VÀ ĐỊNH LƯỢNG RỦI RO"),
  H2("4.1. Phân loại rủi ro"),
  P("Rủi ro được chia theo khả năng biết trước: rủi ro biết trước (lễ, khuyến mãi, giải thể thao) được đưa vào mô hình dự báo; rủi ro không biết trước (bão, thời tiết cực đoan, dịch, tin đồn giá, đơn hàng đột biến) được xử lý bằng khoảng dự báo, tồn kho an toàn và kịch bản."),
  H2("4.2. Bảng rủi ro định lượng"),
  tenBang("Tần suất và tác động của các rủi ro (dữ liệu đến 30/09/2025)"),
  bang(["Rủi ro", "Đợt / năm", "Tác động (trung vị; p10 – p90)", "Nhóm chịu tác động mạnh nhất", "Biết trước"],
    RR.map((r) => [r.rui_ro, r.so_dot_moi_nam === "" ? "–" : vn(r.so_dot_moi_nam), r.tac_dong_trung_vi === "" ? "–" : `×${vn(r.tac_dong_trung_vi, 2)} (${vn(r.p10, 2)} – ${vn(r.p90, 2)})`,
      String(r.nhom_tang_manh).replace(/(\d)\.(\d)/g, "$1,$2"), r.biet_truoc]), [3.4, 1.4, 2.6, 3.6, 2.4], { traiCot: [3, 4] }),
  nguon(NG_MP + ". Tác động = số bán trung bình trong đợt / mức nền 28 ngày trước đợt; 1,00 = không đổi."),
  H2("4.3. Bài học khi định lượng rủi ro"),
  gach([B("Trùng sự kiện: "), "bão Yagi (09/2024) rơi đúng mùa Trung thu nên đồ chơi “tăng ×6 khi có bão” thực ra do Trung thu; rủi ro không biết trước phải bỏ các ngày trùng lễ lớn khi đo tác động. Rét đậm trùng hoàn toàn mùa Tết / Noel nên được ghi là “không tách được”."]),
  gach([B("Ít dữ liệu: "), "chỉ 1–2 trận bão để học thì hệ số dao động 0,7 – 3,0; áp vào trận sau còn tệ hơn không áp."]),
];

// ================================================================ CHUONG 5
chuong = 5;
const qt = D.quy_tac_md.slice(2).map((l) => l.split("|").map((x) => x.trim()).filter((x) => x !== ""));
const TEN_QT = { eoq: "EOQ", dat_den_muc: "Đặt đến mức", lai: "Lai" };
const TEN_CS = { hien_trang: "Hiện trạng*", cong_thuc_du_bao_moc: "Công thức + dự báo mốc", cong_thuc_du_bao_ai: "Công thức + dự báo AI", cong_thuc_du_bao_ai_hc: "AI + hiệu chỉnh lệch (đề xuất)" };
const nhom = {}; D.nhom.forEach(([x, cs, fr, ton, ln]) => { nhom[`${x}|${cs}`] = { fr, ton, ln }; });
const c5 = [
  H1("CHƯƠNG 5. TỐI ƯU TỒN KHO"),
  H2("5.1. Công thức và quy tắc đặt hàng"),
  gach([B("Tồn kho an toàn: "), "SS = z × √(σ_LTD² + d² × σ_LT²), với z theo mức phục vụ (95% → 1,64), σ_LTD là độ lệch chuẩn tổng sai số dự báo trong lead time (đo trên validation), d là nhu cầu dự báo bình quân / ngày, σ_LT là độ lệch chuẩn lead time."]),
  gach([B("Điểm đặt hàng: "), "ROP = nhu cầu dự báo trong lead time + SS. Mỗi ngày, nếu tồn kho + hàng đang về ≤ ROP thì đặt hàng."]),
  gach([B("Lượng đặt: "), "EOQ = √(2 × D × S / H) (D nhu cầu năm, S chi phí một lần đặt, H chi phí lưu kho một đơn vị / năm); hàng ổn định (X, Y) đặt bội số của max(EOQ, MOQ); hàng mùa vụ (Z) “đặt đến mức” đủ bán lead time + 7 ngày + SS (quy tắc lai, chọn trên validation)."]),
  H2("5.2. Thiết kế mô phỏng"),
  P("Mô phỏng 12 tháng kiểm tra theo từng ngày cho 121 mã với cùng nhu cầu thật, cùng thời gian giao hàng ngẫu nhiên (có chậm do bão và nhà cung cấp), so sánh 4 chính sách: hiện trạng (đo từ dữ liệu), công thức + dự báo mốc (trung bình trượt 28 ngày), công thức + dự báo AI, AI + hiệu chỉnh lệch theo nhóm XYZ. Lưu ý: “hiện trạng” trong dữ liệu mô phỏng là người lập kế hoạch được biết trước nhu cầu kỳ vọng (lệch ±10%), tức đối thủ mạnh hơn thực tế; so sánh chính là AI với dự báo mốc dùng cùng công thức."),
  H2("5.3. Chọn quy tắc đặt hàng trên validation"),
  tenBang("Chọn quy tắc lượng đặt trên validation (mức phục vụ 95%, dự báo cập nhật mỗi tuần)"),
  bang(["Quy tắc", "Chính sách", "Fill Rate", "Tồn TB (tr đ)", "Chi phí liên quan (tr đ)"],
    qt.map((r) => [TEN_QT[r[0]] || r[0], TEN_CS[r[1]] || r[1], `${vn(+r[2], 2)}%`, vn(+r[3]), vn(+r[6]) + (r[7] ? " ✓" : "")]),
    [2, 4.5, 1.8, 2, 2.5], { traiCot: [1], dongDam: (t) => String(t).endsWith("✓") }),
  nguon(NG_MP + ". ✓: được chọn (chi phí liên quan thấp nhất)."),
  H2("5.4. Kết quả trước – sau trên tập kiểm tra"),
  tenBang("So sánh 4 chính sách tồn kho (12 tháng kiểm tra, mức phục vụ 95%)"),
  bang(["Chỉ tiêu", "Hiện trạng*", "Dự báo mốc", "Dự báo AI", "AI + hiệu chỉnh (đề xuất)"], [
    ["Fill Rate", ...[ht, moc, aiK, ai].map((x) => `${vn(x.fill_rate_pt, 2)}%`)],
    ["Số ngày-mã thiếu hàng", ...[ht, moc, aiK, ai].map((x) => vn(x.so_ngay_sku_thieu, 0))],
    ["Tồn kho bình quân (tr đ)", ...[ht, moc, aiK, ai].map((x) => vn(x.ton_tb_trieu_vnd))],
    ["Số lần nhập hàng", ...[ht, moc, aiK, ai].map((x) => vn(x.so_lan_nhap, 0))],
    ["Chi phí đặt + lưu kho (tr đ)", ...[ht, moc, aiK, ai].map((x) => vn(x.tong_chi_phi_trieu))],
    ["Lợi nhuận mất do thiếu hàng (tr đ)", ...[ht, moc, aiK, ai].map((x) => vn(x.loi_nhuan_mat_trieu))],
    ["Chi phí liên quan (tr đ)", ...[ht, moc, aiK, ai].map((x) => vn(x.chi_phi_lien_quan_trieu))],
  ], [4, 2, 2, 2, 2.6]),
  nguon(NG_MP + ". *Hiện trạng: người lập kế hoạch được biết trước nhu cầu kỳ vọng."),
  P(["So với dự báo mốc dùng cùng công thức: Fill Rate ", B(`${dau(ai.fill_rate_pt - moc.fill_rate_pt, 2)} điểm`), `, số ngày thiếu ${pt(lech(ai.so_ngay_sku_thieu, moc.so_ngay_sku_thieu), 0)}, tồn kho ${pt(lech(ai.ton_tb_trieu_vnd, moc.ton_tb_trieu_vnd))}, `, B(`chi phí liên quan ${pt(lech(ai.chi_phi_lien_quan_trieu, moc.chi_phi_lien_quan_trieu))}`), ". So với hiện trạng (đối thủ biết trước nhu cầu): Fill Rate ", `${dau(ai.fill_rate_pt - ht.fill_rate_pt, 2)} điểm, số ngày thiếu ${pt(lech(ai.so_ngay_sku_thieu, ht.so_ngay_sku_thieu), 0)}, tồn kho ${pt(lech(ai.ton_tb_trieu_vnd, ht.ton_tb_trieu_vnd))}, chi phí liên quan ${pt(lech(ai.chi_phi_lien_quan_trieu, ht.chi_phi_lien_quan_trieu))}; đổi lại số lần nhập hàng nhiều hơn ${pt(lech(ai.so_lan_nhap, ht.so_lan_nhap), 0)}.`]),
  P(`Ghi nhận trung thực: trên tập kiểm tra, chính sách AI không hiệu chỉnh còn rẻ hơn (${vn(aiK.chi_phi_lien_quan_trieu)} tr đ) nhưng Fill Rate thấp hơn; trên validation AI + hiệu chỉnh rẻ hơn nên theo luật vẫn giữ lựa chọn này. So với bản dự báo cập nhật 28 ngày (v3), cập nhật mỗi tuần giảm tồn kho 27% và chi phí liên quan 12,7% với Fill Rate gần như giữ nguyên: cải thiện đến từ quy trình, không từ mô hình phức tạp hơn.`),
  ...hinh(path.join(KQ, "k05_truoc_sau.png"), "So sánh chỉ tiêu tồn kho giữa các chính sách", NG_MP + "."),
  H2("5.5. Theo nhóm hàng và mức phục vụ"),
  tenBang("Kết quả theo nhóm XYZ (mức phục vụ 95%)"),
  bang(["Nhóm", "Chính sách", "Fill Rate", "Tồn TB (tr đ)", "Lợi nhuận mất (tr đ)"],
    ["X", "Y", "Z"].flatMap((x) => ["cong_thuc_du_bao_ai_hc", "hien_trang", "cong_thuc_du_bao_moc"].map((cs) => {
      const r = nhom[`${x}|${cs}`]; return [x, TEN_CS[cs].replace(" (đề xuất)", ""), `${vn(r.fr)}%`, vn(r.ton), vn(r.ln)];
    })), [1.2, 4, 2, 2.4, 2.6], { traiCot: [1] }),
  nguon(NG_MP + "."),
  P(`Hàng ổn định (X): AI đáp ứng ${vn(nhom["X|cong_thuc_du_bao_ai_hc"].fr)}% so với ${vn(nhom["X|hien_trang"].fr)}% của hiện trạng mà tồn kho thấp hơn ${vn(-100 * lech(nhom["X|cong_thuc_du_bao_ai_hc"].ton, nhom["X|hien_trang"].ton), 0)}%. Hàng mùa vụ (Z): AI đáp ứng ${vn(nhom["Z|cong_thuc_du_bao_ai_hc"].fr)}% với tồn ${vn(nhom["Z|cong_thuc_du_bao_ai_hc"].ton / 1000, 2)} tỷ so với ${vn(nhom["Z|hien_trang"].ton / 1000, 2)} tỷ của hiện trạng; quy tắc đặt đến mức giảm mạnh so với bản EOQ trước đó (tồn 12,1 tỷ) nhưng chưa giải hết vấn đề hàng chỉ bán dịp lễ (mục 7.5, 7.6). Chi phí liên quan theo mức phục vụ: ${D.muc_phuc_vu.map(([m, fr, cp]) => `${vn(100 * m, 0)}% → ${vn(cp / 1000, 2)} tỷ`).join("; ")}.`),
  ...hinh(path.join(KQ, "k04_ton_kho_theo_thoi_gian.png"), "Giá trị tồn kho cuối ngày theo chính sách (12 tháng kiểm tra)", NG_MP + "."),
  H2("5.6. Đối chiếu tiêu chí thành công"),
  tenBang("Đối chiếu tiêu chí thành công đặt ra từ đầu"),
  bang(["Tiêu chí", "Kết quả", "Đánh giá"], [
    ["Sai số dự báo AI thấp hơn mô hình mốc", `WMAPE ${vn(M.ket_hop_v4.wmape, 3)} so với ${vn(M.tb_truot_28_tuan.wmape, 3)}`, "Đạt"],
    ["Bias trong khoảng ±5%", pt(M.ket_hop_v4.bias_pct), "Đạt"],
    ["Fill Rate ≥ 95%", `${vn(ai.fill_rate_pt, 2)}%`, "Đạt"],
    ["Tồn kho không cao hơn hiện trạng", pt(lech(ai.ton_tb_trieu_vnd, ht.ton_tb_trieu_vnd)), "Đạt"],
    ["Giảm ngày thiếu hàng và tổng chi phí so với hiện trạng", `${pt(lech(ai.so_ngay_sku_thieu, ht.so_ngay_sku_thieu), 0)}; ${pt(lech(ai.chi_phi_lien_quan_trieu, ht.chi_phi_lien_quan_trieu))}`, "Đạt"],
  ], [5, 4.5, 2], { traiCot: [1] }),
  nguon("đề tài."),
];

// ================================================================ CHUONG 6
chuong = 6;
const c6 = [
  H1("CHƯƠNG 6. THỬ ĐỘ NHẠY"),
  P("Mỗi kịch bản chỉ đổi một yếu tố, mọi thứ khác giữ nguyên; tắc cảng được thử ở 13 thời điểm trong năm để không chọn đợt có lợi. Mọi mức tác động là giả định."),
  tenBang("Kết quả thử độ nhạy của chính sách AI + hiệu chỉnh (mức phục vụ 95%)"),
  bang(["Kịch bản", "Fill Rate", "Đổi Fill Rate (điểm)", "Chi phí liên quan (tr đ)", "Đổi chi phí"],
    D.do_nhay.map(([t, fr, dfr, cp, dcp], i) => [t, `${vn(fr, 2)}%`, i === 0 ? "" : dau(dfr, 2), vn(cp), i === 0 ? "" : `${dau(dcp)}%`]),
    [5.6, 1.6, 1.8, 2.2, 1.6], { traiCot: [] }),
  nguon(NG_MP + "."),
  ...hinh(path.join(KQ, "k07_do_nhay_lead_time.png"), "Thử độ nhạy: tắc cảng và lead time dài thêm", NG_MP + "."),
  gach("Tắc cảng tạm thời chỉ làm Fill Rate giảm 0,5 – 1,5 điểm vì tồn kho an toàn hấp thụ được; chính sách dùng dự báo AI có chi phí thấp nhất ở cả 39 lần thử."),
  gach("Đợt nguy hiểm nhất là trước Tết, khi tồn kho đang được đẩy lên cho cao điểm."),
  gach("Lead time dài thêm 2 ngày cả năm mà không cập nhật công thức là rủi ro lớn nhất (Fill Rate giảm khoảng 5 điểm); cập nhật lead time vào công thức thì gần như hồi phục: công thức chỉ tốt khi tham số được cập nhật."),
];

// ================================================================ CHUONG 7 (nghiep vu kho bo sung)
chuong = 7;
const tr = (x, nd = 1) => vn(x / 1e6, nd);
const TEN_HT = { ve_kho: "Về kho thường", tra_ncc: "Trả nhà cung cấp", xa_hang: "Phải xả" };
const CK = D.kho, G = D.gom.test, G5 = G.goc["0.5"], GK = G.dat_kem ? G.dat_kem["0.5"] : null;
const NCC = D.ncc, NB = D.ncc_bang, RB = D.rb, HT = RB.han.test, CD = RB.chan_doan.test, C100 = RB.chua.muc["1.0"], TOPV = CD.top[0];
const NV = D.nv, NT = NV.tap.test.phuong_an, NVV = NV.tap.validation2.phuong_an, SK = NT.goc.co_han.theo_su_kien, SKN = NT.mot_lan.co_han.theo_su_kien;
const LS = D.live_sau, LV = D.live, DM = D.dom;
const NG_GD = NG_MP + "; hạn sử dụng, thể tích, sức chứa và chi phí hàng dư là giả định";
const c7 = [
  H1("CHƯƠNG 7. NGHIỆP VỤ KHO BỔ SUNG"),
  P("Chương này mở rộng sang các nghiệp vụ mà kho thật phải xử lý. Các phân tích đều chỉ đọc kết quả, không đổi chính sách đề xuất ở Chương 5; luật được ghi trước khi chạy. Dữ liệu chưa có hạn sử dụng, thể tích, sức chứa hay phiên livestream, nên các phần đó dùng giả định và chỉ cho thấy phương pháp cùng độ lớn tương đối."),
  H2("7.1. Chỉ số kho"),
  tenBang("Vòng quay và tồn dư theo chính sách (12 tháng kiểm tra, mức phục vụ 95%)"),
  bang(["Chính sách", "Vòng quay (lần / năm)", "Số ngày tồn", "Tồn dư TB (tr đ)", "Tồn dư / tồn kho"],
    ["hien_trang", "cong_thuc_du_bao_moc", "cong_thuc_du_bao_ai", "cong_thuc_du_bao_ai_hc"].map((c) => [TEN_CS[c].replace(" (đề xuất)", ""), vn(CK[c][0]), vn(CK[c][1]), vn(CK[c][3]), `${vn(CK[c][4])}%`]), [4.4, 2, 1.8, 2.2, 2], {}),
  nguon(NG_MP + ". Tồn dư: phần tồn cuối ngày vượt nhu cầu thật của 28 ngày kế tiếp."),
  P(`Chính sách đề xuất có vòng quay ngang hiện trạng (${vn(CK.cong_thuc_du_bao_ai_hc[0])} so với ${vn(CK.hien_trang[0])} lần / năm) nhưng tồn dư cao hơn: ${vn(CK.cong_thuc_du_bao_ai_hc[3])} so với ${vn(CK.hien_trang[3])} triệu đồng. Đây là điểm yếu, nguyên nhân nằm ở hàng chỉ bán dịp lễ (mục 7.5, 7.6).`),
  H2("7.2. Gom đơn theo nhà cung cấp"),
  tenBang("Gom đơn trên tập kiểm tra (tỉ lệ chi phí chung của phiếu 0,5 là giả định)"),
  bang(["Phương án", "Số phiếu", "Fill Rate", "Chi phí liên quan (tr đ)"], [
    ["Không gom", vn(G5.so_dong, 0), `${vn(G5.fill_rate, 2)}%`, tr(G5.cp_rieng)],
    ["Gom cùng ngày", vn(G5.so_phieu, 0), `${vn(G5.fill_rate, 2)}%`, tr(G5.cp_gom)],
    ...(GK ? [[`Đặt kèm (k = ${D.gom.k_chon})`, vn(GK.so_phieu, 0), `${vn(GK.fill_rate, 2)}%`, tr(GK.cp_gom)]] : []),
  ], [4, 2, 2, 3], {}),
  nguon(NG_MP + "."),
  P(`Gom cùng ngày chỉ đổi cách lập phiếu nên giảm ${tr(G5.cp_rieng - G5.cp_gom)} triệu đồng mà không đổi tồn kho hay Fill Rate.${GK ? ` Đặt kèm giảm thêm ${tr(G.tach.tong)} triệu đồng, nhưng phần lớn (${tr(G.tach.loi_nhuan_mat)} triệu đồng) đến từ việc mất bán ít hơn: đặt kèm làm hàng được đặt sớm hơn, có tác dụng như tăng dự phòng, nên chưa đưa vào chính sách chính.` : ""}`),
  H2("7.3. Chấm điểm nhà cung cấp và cảnh báo giao chậm"),
  P(`Điểm = 60% tỉ lệ đúng hạn + 40% độ ổn định (trọng số là giả định; đổi sang 80 / 20 thứ hạng gần như không đổi, tương quan hạng ${vn(NCC.test.hang_trong_so_khac, 2)}). Trên ${vn(NCC.test.so_don, 0)} đơn của tập kiểm tra, đúng hạn ${vn(NCC.test.dung_han_pt)}%; cao nhất ${NB.dau.ncc} (${vn(NB.dau.diem)} điểm), thấp nhất ${NB.cuoi.ncc} (${vn(NB.cuoi.diem)} điểm); ${Object.entries(NB.loai).map(([k, n]) => `${n} ${k}`).join(", ")}. Lead time là số mô phỏng nên đây chỉ minh họa phương pháp, và mô phỏng luôn giao đủ hàng nên chưa đo được đủ hàng (OTIF).`),
  P(`Cảnh báo dùng trung bình trễ của 8 đơn đã về gần nhất. Cảnh báo phát hiện đúng đợt giao chậm cài trong dữ liệu nhưng muộn: ${NCC.test.danh_gia.ngay_cho[0]} ngày sau khi đợt bắt đầu trên test, ${NCC.validation2.danh_gia.ngay_cho[0]} ngày trên validation2, trong khi mỗi đợt chỉ khoảng 15 ngày. Vì vậy nó giúp nhận ra nhà cung cấp đang xấu đi, chưa đủ để phản ứng sớm với một đợt ngắn.`),
  H2("7.4. Hạn sử dụng"),
  P(`Theo dõi từng lô, xuất lô về trước, ${RB.so_ma_han} / ${RB.so_ma} mã có hạn theo bảng giả định. Theo quy tắc 1/3 (giả định), kho chỉ được giao trong 1/3 thời hạn kể từ lúc hàng về; quá mốc đó hàng bị loại. Khi tắt mọi ràng buộc, bộ mô phỏng trùng từng mã từng ngày với kết quả trong CSDL.`),
  tenBang("Hạn sử dụng trên tập kiểm tra (các mã có hạn)"),
  bang(["Phương án", "Fill Rate", "Hàng loại (tr đ)", "% hàng nhập", "Tổng chi phí (tr đ)"],
    [["Có hạn, không trần", HT.khong_tran], ["Có hạn, có trần lượng đặt", HT.co_tran], ["Không trần, xả được 50%", HT.khong_tran_mat_50]].map(([t, r]) => [t, `${vn(r.fill_rate, 2)}%`, tr(r.huy_gia_tri), `${vn(r.huy_pt_nhap, 2)}%`, tr(r.cp_tong)]), [4.4, 1.8, 2, 1.8, 2.2], {}),
  nguon(NG_GD + "."),
  P(`Hàng loại tập trung ở rất ít mã: ${CD.so_ma_loai} mã có hàng loại, ${CD.so_ma_dip_le} mã chỉ bán dịp lễ chiếm ${vn(CD.loai_dip_le_pt)}% giá trị. Con số ${tr(HT.khong_tran.huy_gia_tri, 0)} triệu đồng là mức trần bi quan vì coi hàng dư mất trắng. Trần lượng đặt theo hạn đạt luật trên validation2 nhưng gần như chỉ có tác dụng với hàng bán đều, chưa đưa vào chính sách chính.`),
  H2("7.5. Sức chứa"),
  P(`Hai vùng riêng (kho thường, kho lạnh), sức chứa lấy bằng đỉnh hàng thực tồn trên validation2, thử thêm mức 90% và 80%. So hai cách khi vượt: A thuê kho ngoài, không đổi quyết định đặt hàng; B cắt đơn khi hết chỗ, mã ít ngày tồn nhất được đặt trước.`),
  tenBang("Sức chứa trên tập kiểm tra"),
  bang(["Sức chứa", "Phương án", "Fill Rate", "Đỉnh kho thường", "Ngày vượt", "Tổng chi phí (tr đ)"],
    Object.entries(RB.chua.muc).flatMap(([m, d]) => [["A", "thuê ngoài"], ["B", "cắt đơn"]].map(([k, t]) => [`${vn(100 * +m, 0)}%`, `${k}, ${t}`, `${vn(d.test[k].fill_rate, 2)}%`, `${vn(d.test[k].dinh_pt[0], 0)}%`, vn(d.test[k].so_ngay, 0), tr(d.test[k].cp_chua)])), [1.4, 2.6, 1.8, 2, 1.6, 2.4], { traiCot: [1] }),
  nguon(NG_GD + "."),
  P(`Theo luật trên validation2, cả 3 mức đều chọn thuê ngoài. Chẩn đoán cho thấy vấn đề gần như do một mã: ${TOPV.ten} được đặt ${vn(TOPV.nhap, 0)} trong khi nhu cầu cả kỳ ${vn(TOPV.nhu_cau, 0)}, hiện trạng nhập ${vn(TOPV.nhap_ht, 0)}, cuối kỳ dư ${vn(TOPV.ton_cuoi, 0)}. Bỏ riêng mã này, đỉnh thể tích từ ${vn(C100.test.A.dinh_pt[0], 0)}% còn ${vn(CD.bo_ma_lon_nhat.dinh_pt[0], 0)}%, số ngày vượt từ ${C100.test.A.so_ngay} còn ${CD.bo_ma_lon_nhat.so_ngay}. Đây là điểm yếu có sẵn trong kết quả chính ở Chương 5, không phải do phần sức chứa tạo ra. Cắt đơn nguy hiểm vì ${vn(CD.vuot_pt)}% thể tích là hàng vượt nhu cầu 60 ngày tới, gần như toàn nhóm Z: tồn chết chiếm chỗ nên hàng bán chạy bị chặn. Muốn có chỗ phải xả tồn chết, không phải cắt đơn mới.`),
  H2("7.6. Newsvendor cho hàng chỉ bán dịp lễ"),
  P(`Hai mục trên cùng chỉ về chính sách cho ${NV.so_ma} mã chỉ bán dịp lễ. Phương án: đặt một lần trước mùa, Q = tổng nhu cầu mùa trước × phân vị Cu / (Cu + Co) của tỉ số giữa hai mùa liên tiếp; Cu là lãi một đơn vị, Co là thiệt hại khi dư. Q dùng lịch sử mùa trước vì lúc phải đặt, dự báo 28 ngày chưa phủ hết mùa.`),
  tenBang("Newsvendor hàng dịp lễ, toàn kho, tập kiểm tra"),
  bang(["Phương án", "Có hạn: chi phí (tr đ)", "Có hạn: Fill Rate", "Không hạn: chi phí (tr đ)", "Không hạn: Fill Rate", "Tồn TB dịp lễ (tr đ)"],
    [["goc", "Quy tắc hiện tại"], ["mot_lan", "Đặt một lần (theo luật)"], ["mot_lan_bo_ma", "Bỏ mã hạn ngắn*"]].map(([k, t]) => [t, tr(NT[k].co_han.toan_kho.cp_tong, 0), `${vn(NT[k].co_han.toan_kho.fill_rate, 2)}%`, tr(NT[k].khong_han.toan_kho.cp_tong, 0), `${vn(NT[k].khong_han.toan_kho.fill_rate, 2)}%`, tr(NT[k].khong_han.dip_le.ton_tb, 0)]), [3.6, 1.8, 1.6, 1.8, 1.6, 1.8], {}),
  nguon(NG_GD + ". *Thêm sau khi đã thấy tập kiểm tra, chỉ để tham khảo."),
  P(`Trên validation2, luật chọn đặt một lần (chi phí giảm ${vn(100 * (1 - NVV.mot_lan.co_han.toan_kho.cp_tong / NVV.goc.co_han.toan_kho.cp_tong))}%). Tập kiểm tra không xác nhận trong môi trường có hạn: chi phí tăng ${vn(100 * (NT.mot_lan.co_han.toan_kho.cp_tong / NT.goc.co_han.toan_kho.cp_tong - 1))}%, Fill Rate dưới 95%, nên phương án không được đưa vào chính sách chính. Nguyên nhân là bánh trung thu (${NV.tap.test.mua_dai_hon_han.join(", ")}): hạn ngắn nên hàng hết hạn giữa mùa, chi phí nhóm Trung thu từ ${tr(SK.trung_thu.cp_tong, 0)} lên ${tr(SKN.trung_thu.cp_tong, 0)} triệu đồng. Validation2 không có mùa Trung thu nào được chấm nên phép chọn không thấy trước rủi ro này.`),
  P(`Ở các dịp còn lại, đặt một lần có ích: chi phí Halloween ${tr(SK.halloween.cp_tong, 0)} còn ${tr(SKN.halloween.cp_tong, 0)}, Noel ${tr(SK.noel.cp_tong, 0)} còn ${tr(SKN.noel.cp_tong, 0)}, Tết ${tr(SK.tet.cp_tong, 0)} còn ${tr(SKN.tet.cp_tong, 0)} triệu đồng, đổi lại Fill Rate Noel từ ${vn(SK.noel.fill_rate)}% còn ${vn(SKN.noel.fill_rate)}%. Phương án bỏ mã hạn ngắn trông tốt nhất nhưng được thêm sau khi đã thấy tập kiểm tra và dữ liệu không còn năm nào chưa xem để kiểm lại, nên chỉ là đề xuất cải tiến.`),
  H2("7.7. Trữ hàng cho phiên livestream"),
  P("Chuỗi chủ yếu là phân phối, có bán online và giao từ chính kho. Dữ liệu chưa có phiên live nào nên phần này là công cụ dựng sẵn với tham số giả định; số tiền chỉ để so sánh tương đối. Trước phiên, trữ Q = phân vị Cu / (Cu + Co) của nhu cầu phiên (newsvendor); trong phiên, ước lượng lại từ số đã bán theo giờ để đặt bổ sung nếu kịp. Hệ số khuyến mãi lấy từ số thật Dominick's theo đúng dải giảm giá (mục 8.3), tài trợ mặc định 45%."),
  tenBang("Lãi kỳ vọng toàn kho, mỗi mã 1 phiên, giảm 15% (triệu đồng)"),
  bang(["Hàng thừa sau phiên", "Trước đối chiếu", "Sau đối chiếu", "Vốn trữ sau đối chiếu", "Giá trị theo dõi theo giờ"],
    Object.entries(TEN_HT).map(([h, t]) => [t, tr(LS.truoc[h].phuong_an.newsvendor.lai), tr(LS.sau[h].phuong_an.newsvendor.lai), tr(LS.sau[h].phuong_an.newsvendor.q), dau((LS.sau[h].phuong_an.hai_buoc_2.lai - LS.sau[h].phuong_an.newsvendor.lai) / 1e6)]), [3.2, 2, 2, 2.2, 2.4], {}),
  nguon("mô phỏng của đề tài với hệ số khuyến mãi từ Dominick's; bùng nổ, phí sàn, tỉ lệ hủy là giả định. Trước đối chiếu: hệ số mô phỏng, tài trợ 70%."),
  P(`Newsvendor không thua hai cách trữ đơn giản ở cả ${LS.newsvendor.length} trường hợp chấm trên hệ số thật (${LS.thua.length ? `trừ: ${LS.thua.join("; ")}` : "không có trường hợp thua"}), còn trữ theo trung bình rất rủi ro vì vài phiên bùng nổ kéo trung bình lên. Giá trị theo dõi theo giờ nhỏ vì lãi sau phụ phí nguồn nhanh rất mỏng. Bài học lớn nhất đến từ điều kiện kinh doanh: mức nhãn hàng tài trợ ảnh hưởng đến lãi nhiều hơn cách tính lượng trữ. Quy tắc bổ sung ghi trước thua cả việc không làm gì và đã phải sửa; bản sửa được viết sau khi thấy kết quả nên nhẹ cân hơn một kiểm định ghi trước.`),
];

// ================================================================ CHUONG 8 (hoc sau, kiem chung tren so that)
chuong = 8;
const DLM = D.dl, M5 = D.m5, W_ = (x) => (x ? `${vn(x.wmape, 3)} (${pt(x.bias)})` : "–");
const giamM5 = 1 - M5.ket_hop_dl.test.wmape / M5.tb_truot.test.wmape, giamMP = 1 - M.ket_hop_v4.wmape / M.tb_truot_28_tuan.wmape;
const TEN_NF = { ket_hop_v4: "Kết hợp v4 (đang dùng)", ket_hop_v5: "Kết hợp v5 (thêm học sâu)", lstm_tuan: "LSTM", rnn_tuan: "RNN", tide_tuan: "TiDE", nhits_tuan: "N-HiTS", tft_tuan: "TFT", ket_hop_nf: "Kết hợp v4 + mô hình tốt nhất trong ba" };
const NF_DU = Boolean(DLM.tide_tuan.test && DLM.nhits_tuan.test && DLM.tft_tuan.test);
const dongNF = (nguonNf) => Object.keys(TEN_NF).filter((k) => nguonNf[k] && (nguonNf[k].validation2 || nguonNf[k].test));
const M5T = D.m5_tk, TKD = D.tk_db, DNS = D.dn_s, TL = D.tl, SSK = D.ss_km;
const g5 = D.m5_gom.test;
const theoNguong = (ds, k) => ds.find((r) => r.nguong === k);
const cbmp = theoNguong(D.cb2.mp.validation2.p1, 4), cbm5 = theoNguong(D.cb2.m5.validation2.p1, 4), cbz = theoNguong(D.cb2.mp.validation2.p2, 4);
const ngay_ = (x) => x.split("-").reverse().join("/");
const muTu = (x) => { const [m, e] = x.toExponential(1).split("e"); const so = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  return `${m.replace(".", ",")} × 10${[...String(+e)].map((c) => so[c]).join("")}`; };
const ANH = (f) => path.join(DU_AN, "reports", "word", "anh", f);
const c8 = [
  H1("CHƯƠNG 8. HỌC SÂU VÀ KIỂM CHỨNG TRÊN SỐ THẬT"),
  P("Kết quả ở các chương trước dùng dữ liệu mô phỏng, do chính đề tài sinh ra. Chương này trả lời hai câu hỏi hội đồng dễ đặt ra nhất: mô hình phức tạp hơn có tốt hơn không, và kết quả có giữ được trên số bán thật không."),
  H2("8.1. Mô hình học sâu trên dữ liệu mô phỏng"),
  tenBang("WMAPE (Bias) của các mô hình học sâu trên dữ liệu mô phỏng"),
  bang(["Mô hình", "Validation2", "Tập kiểm tra"], dongNF(DLM).map((k) => [TEN_NF[k], W_(DLM[k].validation2), W_(DLM[k].test)]), [5, 3, 3], {}),
  nguon(NG_MP + (NF_DU ? "." : ". “–”: chưa chạy xong.")),
  P(`LSTM và RNN có cấu hình mã hóa – giải mã, 3 hạt giống. Theo luật, mô hình chỉ được thay khi WMAPE trên validation2 giảm đủ và Bias không tăng quá 1 điểm: kết hợp v5 giảm WMAPE từ ${vn(DLM.ket_hop_v4.validation2.wmape, 3)} xuống ${vn(DLM.ket_hop_v5.validation2.wmape, 3)} nhưng lệch tăng từ ${pt(DLM.ket_hop_v4.validation2.bias)} lên ${pt(DLM.ket_hop_v5.validation2.bias)}, nên hệ thống giữ kết hợp v4. ${NF_DU ? "TiDE, N-HiTS và TFT được đánh giá theo cùng luật." : "TiDE, N-HiTS và TFT đang chạy, phần còn lại sẽ tự cập nhật khi tạo lại báo cáo."} TFT dùng cấu hình gọn vì GPU 4 GB, nên không phản ánh hết năng lực của nó.`),
  H2("8.2. Kiểm chứng trên số bán thật M5"),
  P("M5 là số bán thật của Walmart. Đề tài cộng 10 cửa hàng thành một kho tổng, lấy mẫu 121 mã phân tầng theo phòng ban trước khi xem số bán, rồi chạy nguyên quy trình và chọn mô hình trên validation2 của M5. Số bán giữ nguyên, không chỉnh sửa."),
  tenBang("Kết quả trên số bán thật M5, tập kiểm tra"),
  bang(["Mô hình", "WMAPE", "Bias", "WMAPE nhóm X", "WMAPE nhóm Z"], Object.entries({ ket_hop_dl: "LightGBM + Prophet + RNN (được chọn)", rnn: "RNN", ket_hop: "LightGBM + Prophet", lightgbm: "LightGBM", lstm: "LSTM", tb_truot: "Trung bình trượt 28 ngày", prophet: "Prophet", lap_tuan: "Lặp tuần trước" }).map(([k, t]) => [t, vn(M5[k].test.wmape, 3), pt(M5[k].test.bias), vn(M5[k].test.wmape_x, 3), vn(M5[k].test.wmape_z, 3)]), [5, 1.6, 1.6, 1.8, 1.8], {}),
  nguon("Bộ dữ liệu M5 Forecasting (Walmart), tính bằng chương trình của đề tài."),
  P(["Mô hình chọn giảm ", B(`${vn(100 * giamM5)}%`), " sai số so với trung bình trượt, trong khi trên dữ liệu mô phỏng là ", B(`${vn(100 * giamMP, 0)}%`), `. Mức cải thiện trên số thật chỉ bằng khoảng một phần ba, có thể vì dữ liệu mô phỏng có quy luật rõ, sinh từ chính các yếu tố mà mô hình được biết trước; đề tài chưa tách riêng được nguyên nhân này. Vì vậy con số ${vn(100 * giamMP, 0)}% không nên hiểu là hiệu quả dự kiến khi dùng thật. Thứ hạng giống một phần: mô hình ghép và học sâu đứng đầu, nhưng trên M5 trung bình trượt lại tốt hơn Prophet, ngược với dữ liệu mô phỏng. M5 không có tên hàng, khuyến mãi hay cờ hết hàng nên chưa dùng được đặc trưng khuyến mãi; phần tồn kho chưa chạy trên M5 vì lead time và chi phí đều phải giả định.`]),
  H2("8.3. Đối chiếu giả định với số thật Dominick's"),
  P(`Dominick's là số bán theo tuần, có giá và lãi gộp, của một chuỗi siêu thị Mỹ giai đoạn 1989–1997 (${DM.so_nganh} ngành, ${vn(DM.so_ma, 0)} mã). Đây không phải Việt Nam và không phải livestream, nên chỉ dùng để kiểm tra giả định, không dùng huấn luyện mô hình. Nguồn: James M. Kilts Center, University of Chicago Booth School of Business.`),
  tenBang("Đối chiếu giả định của đề tài với số thật Dominick's"),
  bang(["Điểm so sánh", "Số thật", "Đề tài đang dùng", "Đánh giá"], [
    ["Hệ số khuyến mãi, trung vị", `×${vn(DM.deal.p50, 2)}`, `×${vn(DM.deal_mo_phong.p50, 2)}`, DM.deal_lech ? "Lệch" : "Không lệch"],
    ["Tỉ lệ tuần bán từ ×5 trở lên", `${vn(DM.deal.tu_5)}%`, `${vn(DM.deal_mo_phong.tu_5)}%`, "Mô phỏng quá ít ca tăng mạnh"],
    ["Nhà sản xuất tài trợ phần giảm giá", `${vn(100 * DM.tai_tro.gop)}%`, "70% (bản đầu), 45% (bản sau)", DM.tai_tro_lech ? "Bản đầu lệch" : "Không lệch"],
    ["Biên lãi gộp theo mã, trung vị", `${vn(100 * DM.bien.ma_p50)}%`, "10–23%", "Mô phỏng thấp hơn"],
    ["Độ co giãn theo giá", vn(DM.do_sau.co_gian, 2), "Bản đầu chưa có", "Đã bổ sung"],
    ["Tuần ngay sau khuyến mãi", `×${vn(DM.sau_km.p50, 2)}`, "Từng nêu là có giảm", "Không rõ hiện tượng"],
  ], [4.4, 1.8, 3, 3], { traiCot: [2, 3] }),
  nguon("Dominick's Dataset, James M. Kilts Center, University of Chicago Booth School of Business; đề tài tính lại toàn chuỗi theo mã và tuần."),
  P(`Đo hệ số khuyến mãi trên 2/3 đầu rồi kiểm trên 1/3 sau: phép gộp mọi mức giảm không đạt (chỉ ${DM.phu_nganh_dat} / ${Object.keys(DM.phu.theo_nganh).length} ngành giữ được), chia theo dải giảm giá thì đạt ${Object.values(LS.phu).filter((x) => x.dat).length} / ${Object.keys(LS.phu).length} dải. Trên dữ liệu mô phỏng cùng phép kiểm lại đạt, vì một quy luật sinh ra cả hai giai đoạn. Do đó hệ số phải được đo lại định kỳ, không thể đo một lần rồi dùng mãi. Độ co giãn chỉ là tương quan vì khuyến mãi siêu thị đi kèm trưng bày và tờ rơi; giá vốn là giá bình quân tồn kho nên mức tài trợ chỉ là ước lượng.`),
  H2("8.4. Nghiệp vụ kho trên số thật M5 và AI có giá trị ở đâu"),
  P("Đề tài dựng thêm một bộ dữ liệu kho từ số bán thật M5: số bán và giá bán giữ nguyên, khuyến mãi suy từ giá, biên lãi đo từ Dominick's; lead time, chi phí đặt, chi phí lưu kho và nhà cung cấp là giả định. Bộ này chạy nguyên chính sách tồn kho của chương 5."),
  tenBang("Tồn kho trên bộ dữ liệu kho từ M5, tập kiểm tra, mức phục vụ 95%"),
  bang(["Chính sách", "Fill Rate", "Ngày-mã thiếu", "Tồn kho TB (triệu đ)", "Chi phí liên quan (triệu đ)"],
    [["cong_thuc_du_bao_ai_hc", "AI + hiệu chỉnh lệch"], ["cong_thuc_du_bao_ai", "AI"], ["cong_thuc_du_bao_moc", "Dự báo mốc (trung bình trượt)"], ["hien_trang", "Quy tắc kinh nghiệm (giả định)"]]
      .map(([k, t]) => [t, `${vn(M5T[k].fill, 2)}%`, vn(M5T[k].thieu, 0), vn(M5T[k].ton), vn(M5T[k].cp)]), [4.6, 2, 2, 2.6, 2.8], {}),
  nguon("bộ dữ liệu kho dựng từ M5 Forecasting (Walmart) và Dominick's, tính bằng chương trình của đề tài; lead time, chi phí, tồn kho là giả định."),
  P(`Trên M5, chính sách AI + hiệu chỉnh chỉ giảm ${vn(-100 * lech(M5T.cong_thuc_du_bao_ai_hc.cp, M5T.cong_thuc_du_bao_moc.cp))}% chi phí liên quan so với dự báo mốc, trong khi trên dữ liệu mô phỏng là ${vn(-100 * lech(TKD.cong_thuc_du_bao_ai_hc.cp, TKD.cong_thuc_du_bao_moc.cp))}%. Thử độ nhạy theo chi phí đặt (từ × 0,1 đến × 2) cho thấy khoảng cách này không do giả định chi phí đặt: theo luật ghi trước, cả hai bộ đều “không phụ thuộc rõ” (lợi ích của AI ở chi phí đặt × 0,1 chỉ cao hơn ở × 1 là ${vn(DNS.m5.ket_luan.chenh_diem)} điểm trên M5 và ${vn(DNS.mp.ket_luan.chenh_diem)} điểm trên mô phỏng, ngưỡng 5 điểm).`),
  tenBang("Lợi ích của AI + hiệu chỉnh so với dự báo mốc theo chi phí đặt, tập kiểm tra"),
  bang(["Chi phí đặt so với gốc", "M5: lượng đặt (ngày bán)", "M5: lợi ích AI", "Mô phỏng: lượng đặt (ngày bán)", "Mô phỏng: lợi ích AI"],
    Object.keys(DNS.m5.ket_qua).map((k) => [`× ${vn(+k, 2)}`, vn(DNS.m5.ket_qua[k].eoq_ngay), pt(DNS.m5.ket_qua[k].loi_ich / 100), vn(DNS.mp.ket_qua[k].eoq_ngay), pt(DNS.mp.ket_qua[k].loi_ich / 100)]),
    [3, 2.6, 2.2, 2.8, 2.2], {}),
  nguon("tính bằng chương trình của đề tài; lợi ích = (chi phí liên quan của dự báo mốc − của AI + hiệu chỉnh) / của dự báo mốc; lượng đặt EOQ tính bằng số ngày bán, trung vị."),
  P(["Lời giải thích nằm ở loại hàng. Trên dữ liệu mô phỏng, ", B(`${vn(100 * D.z.ton)}%`), " mức giảm tồn kho và ", B(`${vn(100 * D.z.lnm)}%`),
    ` mức giảm lợi nhuận mất của AI so với dự báo mốc đến từ ${D.z.so_z} mã nhóm Z (mùa vụ, theo sự kiện), nơi trung bình trượt chỉ đạt Fill Rate ${vn(D.z.fill_moc_z)}%. Bộ M5 chỉ có ${D.z_m5} mã nhóm Z; với hàng bán đều, trung bình trượt cộng tồn kho an toàn đã đủ. AI đáng dùng nhất cho hàng mùa vụ và hàng theo sự kiện.`]),
  P(`Các nghiệp vụ còn lại trên M5: gom đơn theo nhà cung cấp chọn đặt kèm k = ${D.m5_gom.k_chon}; trên tập kiểm tra, gom cùng ngày giảm ${vn(-100 * lech(g5.goc["0.5"].cp_gom, g5.goc["0.5"].cp_rieng))}% chi phí liên quan, đặt kèm giảm thêm ${vn(-100 * lech(g5.dat_kem["0.5"].cp_gom, g5.goc["0.5"].cp_gom))}% nhưng tồn kho tăng ${vn(100 * lech(g5.dat_kem["0.5"].ton_tb, g5.goc["0.5"].ton_tb))}%; lợi ích chủ yếu đến từ chia sẻ chi phí phiếu nên phụ thuộc giả định tỉ lệ chi phí chung. Chấm điểm nhà cung cấp, hạn sử dụng, sức chứa và newsvendor hàng dịp lễ không áp dụng cho M5 (mọi nhà cung cấp cùng lead time giả định, không có tên hàng để suy hạn dùng và thể tích, không có hàng chỉ bán dịp lễ).`),
  H2("8.5. Cảnh báo dự báo bắt đầu lệch: kết quả âm tính"),
  P(`Đề tài thử thêm tín hiệu theo dõi (tracking signal): tổng sai số 4 tuần gần nhất chia cho sai số tuyệt đối trung bình theo tuần, cảnh báo khi vượt ngưỡng. Luật ghi trước yêu cầu cảnh báo phải báo đúng chiều lệch của 28 ngày tới và không báo quá nhiều. Sau hai vòng, kết quả không đạt ở cả hai bộ. Ở ngưỡng 4, trên mô phỏng chiều lệch của 28 ngày tới chỉ trùng ${vn(100 * cbmp.cung_chieu)}% (như tung đồng xu), có thể vì mô hình đã cập nhật mỗi tuần; trên M5 trùng ${vn(100 * cbm5.cung_chieu)}% nhưng độ lệch của nhóm bị cảnh báo chỉ gấp ${vn(cbm5.boi, 2)} lần nhóm còn lại. Với các đợt tăng đột ngột (nắng nóng, rét, dịch), tín hiệu phát hiện ${vn(100 * cbz.phat_hien)}% số đợt ngay tuần đầu, gấp ${vn(cbz.gap, 1)} lần tỉ lệ báo nhầm, nhưng chưa đạt 50%: cảnh báo dựa trên sai số đã qua đến muộn, nhất là khi hết hàng làm số bán không phản ánh nhu cầu. Muốn bắt kịp cần thông tin bên ngoài như dự báo thời tiết, tin dịch bệnh.`),
];

// ================================================================ CHUONG 9 (he thong)
chuong = 9;
const nBang = D.bang.filter(([, t]) => t === "table").length, nView = D.bang.filter(([, t]) => t === "view").length;
const cb = D.canh_bao_0902;
const c9 = [
  H1("CHƯƠNG 9. HỆ THỐNG HỖ TRỢ QUYẾT ĐỊNH"),
  H2("9.1. Cơ sở dữ liệu và luồng chạy lại"),
  P(`Toàn bộ dữ liệu và kết quả nằm trong một tệp SQLite (${nBang} bảng, ${nView} khung nhìn): danh mục (mã hàng, nhà cung cấp, phân nhóm), giao dịch thô và sạch, lịch sự kiện / khuyến mãi / ngày nghỉ, mô hình và dự báo (có khoảng 80 / 95%), tham số và kết quả tồn kho, mô phỏng theo ngày, thử độ nhạy, nhật ký chạy. Mỗi bước là một chương trình chạy lại được (Phụ lục A); chạy lại từ đầu cho kết quả trùng từng byte.`),
  H2("9.2. Dashboard cho người lập kế hoạch"),
  P("Dashboard (Streamlit, chạy trên máy, không cần mạng) gồm 5 màn với cơ chế tương tự Power BI: bộ lọc chung (ngày, chính sách, nhóm ABC / XYZ) áp cho mọi màn; bấm vào biểu đồ / ô trạng thái để lọc chéo; bấm một dòng để đi sâu sang màn Mặt hàng.", { keepNext: true }),
  gach([B("Hôm nay: "), `tình trạng cuối ngày, các đơn đề xuất kèm lý do bằng số (trong kho + đang về ≤ ROP), duyệt / sửa / bỏ qua từng dòng, tải phiếu đặt hàng theo nhà cung cấp. Ví dụ ngày 09/02/2026 (trước Tết): ${cb["Hết hàng"]} mã hết hàng, ${cb["Đặt hàng hôm nay"]} mã cần đặt, ${cb["Dưới ROP, hàng đang về"]} mã dưới ROP nhưng hàng đang về, ${cb["Đủ hàng"]} mã đủ hàng.`]),
  gach([B("Dự báo: "), "dự báo 28 ngày chưa xảy ra, mô hình chạy lại khi bấm, giải thích từng con số theo yếu tố và thử nếu bật khuyến mãi (mục 9.3)."]),
  gach([B("Mặt hàng: "), "tồn kho 12 tháng, dải trạng thái theo ngày, dự báo so với thực tế kèm khoảng 80%, khung “Thử nếu…” tính lại SS / ROP / EOQ và lượng đặt khi đổi mức phục vụ hoặc lead time (tái lập đúng 127.776 / 127.776 dòng của mô phỏng); khối trữ hàng cho phiên livestream dùng được cho mọi mã."]),
  gach([B("Kịch bản & kết quả: "), "bảng trước – sau, 4 chỉ số chính, đánh đổi tồn kho – mức đáp ứng theo nhóm, chỉ số kho, gom đơn, chấm điểm nhà cung cấp, hạn sử dụng và sức chứa, newsvendor hàng dịp lễ, thử độ nhạy."]),
  gach([B("Dữ liệu & phương pháp: "), "dữ liệu là gì, cái gì thật / giả định, các biểu đồ phân tích, xếp hạng mô hình, công thức."]),
  ...hinh(ANH("hom_nay_mp.png"), "Màn “Hôm nay” của dashboard (ngày 09/02/2026)", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  H2("9.3. Dự báo ngày chưa xảy ra: mô hình chạy khi bấm và giải thích"),
  P("Các màn trên đứng ở một ngày đã qua để so dự báo với thực tế. Màn “Dự báo” trả lời câu hỏi người lập kế hoạch thật sự cần: 28 ngày tới sẽ bán bao nhiêu, vì sao mô hình nghĩ vậy, và nếu thay đổi thì sao."),
  gach([B("Dự báo cho ngày chưa xảy ra: "), "đứng ở ngày cuối của dữ liệu, dự báo 28 ngày tiếp theo bằng đúng mô hình đã chọn. Thông tin biết trước của 28 ngày này (thứ, lễ, Tết, sale, khuyến mãi đã lên lịch) được dựng theo đúng quy tắc của lịch hiện có; dựng thử cho các khoảng ngày đã qua thì trùng mọi cột với dữ liệu. Sự kiện không biết trước (bão, dịch, thời tiết) không được đoán. Dữ liệu M5 lấy thẳng lịch gốc có sẵn đến hết 28 ngày tới."]),
  gach([B("Chạy lại phải trùng bản đã chấm: "), `chạy lại mốc tuần cuối của tập kiểm tra cho ra đúng dự báo đã lưu, chỉ lệch ở mức làm tròn của máy. RNN trên M5 học tiếp qua từng tuần nên phải chạy lại cả chuỗi mốc của tập kiểm tra rồi học tiếp ${D.rnn_kl.hoc_tiep.length} lần đến ngày cuối; mốc cuối của tập kiểm tra lệch tổng ${muTu(D.rnn_kl.kiem_lai.lech_tuong_doi_tong)} so với bản đã lưu.`]),
  tenBang("Dự báo 28 ngày chưa xảy ra và đối chiếu với số bán đã qua (toàn kho, trung bình mỗi ngày)"),
  bang(["", "Dữ liệu mô phỏng", "Số bán thật M5"], [
    ["Ngày đứng dự báo", ngay_(TL.mp.ngay_lap), ngay_(TL.m5.ngay_lap)],
    ["Dự báo cho", `${ngay_(TL.mp.tu)} – ${ngay_(TL.mp.den)}`, `${ngay_(TL.m5.tu)} – ${ngay_(TL.m5.den)}`],
    ["Mô hình", TL.mp.mo_hinh, TL.m5.mo_hinh],
    ["Dự báo", vn(TL.mp.tb, 0), vn(TL.m5.tb, 0)],
    ["Cùng kỳ 1 năm trước", vn(TL.mp.cung_ky_1, 0), vn(TL.m5.cung_ky_1, 0)],
    ["Cùng kỳ 1 năm trước, bỏ dòng có khuyến mãi", vn(TL.mp.cung_ky_1_khong_km, 0), "không có khuyến mãi"],
    ["Cùng kỳ 2 năm trước, bỏ dòng có khuyến mãi", vn(TL.mp.cung_ky_2_khong_km, 0), vn(TL.m5.cung_ky_2_khong_km, 0)],
    ["28 ngày gần nhất trước ngày đứng dự báo", vn(TL.mp.gan, 0), vn(TL.m5.gan, 0)],
  ], [5.2, 3, 3], {}),
  nguon("tính bằng chương trình của đề tài; cùng kỳ lùi 364 hoặc 728 ngày để cùng thứ trong tuần."),
  P(`Trên dữ liệu mô phỏng, dự báo thấp hơn cùng kỳ năm trước vì tháng 10/2025 có Trung thu và khuyến mãi; bỏ dòng có khuyến mãi, cùng kỳ 2 năm trước (không có Trung thu trong tháng 10) là ${vn(TL.mp.cung_ky_2_khong_km, 0)}, sát mức dự báo ${vn(TL.mp.tb, 0)}. Dự báo coi như không khuyến mãi vì chưa có lịch khuyến mãi gửi trước.`),
  ...hinh(ANH("db_tong_mp.png"), "Màn “Dự báo”: 28 ngày chưa xảy ra so với 8 tuần số bán đã qua", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  ...hinh(ANH("db_ma_mp.png"), "Dự báo từng ngày của một mã kèm khoảng 80% và 95%", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  P("Bấm “Chạy mô hình”, hệ thống làm lại từng bước và hiện ra: đọc dữ liệu đến ngày cuối, dựng 28 ngày chưa xảy ra, học LightGBM trên toàn bộ lịch sử (lần đầu khoảng nửa phút, các mã sau dùng lại), học Prophet riêng cho mã đang xem, ghép theo trọng số đã chọn của nhóm hàng, rồi tự so với bản đã lưu trong cơ sở dữ liệu.", { keepNext: true }),
  ...hinh(ANH("db_chay_mp.png"), "Các bước mô hình chạy khi bấm và kết quả so với bản đã lưu", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  P("Phần “Vì sao ra con số này” chọn một ngày bất kỳ: hiện công thức ghép có số, hệ số nhân của từng nhóm yếu tố trong LightGBM (tách từ đóng góp của từng cột; LightGBM dùng hàm Tweedie theo thang log nên các đóng góp nhân với nhau, và tích các hệ số đúng bằng dự báo) và các thành phần cộng của Prophet (xu hướng, mùa trong tuần, mùa trong năm, ngày lễ, khuyến mãi). Mức nền là dự báo trung bình của mọi mã; “đặc điểm mã hàng” cho biết mã này bán nhiều hay ít hơn mã trung bình.", { keepNext: true }),
  ...hinh(ANH("db_giai_thich_mp.png"), "Giải thích một ngày dự báo (dữ liệu mô phỏng)", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  ...hinh(ANH("db_giai_thich_m5.png"), "Giải thích một ngày dự báo trên M5: RNN ghép với LightGBM và Prophet", "dashboard của đề tài, số bán thật M5. Phần RNN chỉ có con số tổng: mạng nơ-ron không tách được theo từng yếu tố.", 15.5),
  P(`Phần “Thử nếu” bật khuyến mãi cho mã đang xem trong khoảng ngày tự chọn; LightGBM và Prophet tính lại bằng chính mô hình vừa học, RNN giữ nguyên. Để người xem tự kiểm tra mô hình có “nghĩ” hợp lý không, màn hình đặt cạnh mức tăng lịch sử của chính mã đó, so ngày có khuyến mãi với 28 ngày thường ngay trước (so với mọi ngày thường thì bị phóng đại vì khuyến mãi hay rơi vào mùa cao điểm). Trên toàn kho, bật khuyến mãi 7 ngày làm mô hình tăng trung vị × ${vn(SSK.mo_hinh.p50, 2)} (khoảng giữa ${vn(SSK.mo_hinh.p25, 2)}–${vn(SSK.mo_hinh.p75, 2)}), sát mức lịch sử × ${vn(SSK.lich_su.p50, 2)} (${vn(SSK.lich_su.p25, 2)}–${vn(SSK.lich_su.p75, 2)}); nhưng tương quan thứ hạng chỉ ${vn(SSK.tuong_quan_hang, 2)}: mô hình đúng ở mức chung, chưa phân biệt tốt mã nào tăng mạnh. Dữ liệu M5 không có khuyến mãi nên mô hình không học được tác động này; màn hình ghi rõ.`, { keepNext: true }),
  ...hinh(ANH("db_thu_neu_mp.png"), "Thử nếu bật khuyến mãi 7 ngày cho một mã", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  ...hinh(ANH("db_toan_kho_mp.png"), "Mức tăng khi bật khuyến mãi: mô hình so với lịch sử cùng mùa, từng mã", "dashboard của đề tài, dữ liệu mô phỏng.", 15.5),
  H2("9.4. Dữ liệu cho Power BI và kiểm thử"),
  P("Sáu tệp CSV theo mô hình hình sao (3 danh mục, 3 sự kiện) được xuất kèm sổ đối chiếu số liệu với CSDL. Hệ thống được kiểm thử bằng: chạy lại toàn chuỗi so sánh mã băm, đối chiếu tự động mọi con số trong báo cáo với CSDL, kiểm thử tự động giao diện và bấm chuột thật trên trình duyệt cho các thao tác chính."),
];

// ================================================================ CHUONG 10, KET LUAN, PHU LUC
chuong = 10;
const c10 = [
  H1("CHƯƠNG 10. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN"),
  H2("10.1. Hạn chế"),
  gach("Dữ liệu mô phỏng: kết quả chứng minh quy trình và phương pháp, chưa phải số liệu của một kho cụ thể."),
  gach("“Hiện trạng” trong dữ liệu biết trước nhu cầu kỳ vọng nên là đối thủ mạnh hơn thực tế."),
  gach(`Trên số bán thật M5, mức giảm sai số so với trung bình trượt chỉ ${vn(100 * giamM5)}%, so với ${vn(100 * giamMP, 0)}% trên dữ liệu mô phỏng.`),
  gach("Chính sách cho hàng chỉ bán dịp lễ còn đặt quá tay ở mùa cao điểm; newsvendor đã thử nhưng chưa được tập kiểm tra xác nhận (mục 7.6)."),
  gach(`Trên bộ dữ liệu kho từ M5, AI gần như không giảm được chi phí tồn kho (${vn(-100 * lech(D.m5_tk.cong_thuc_du_bao_ai_hc.cp, D.m5_tk.cong_thuc_du_bao_moc.cp))}%); lợi ích của AI tập trung ở hàng mùa vụ (mục 8.4).`),
  gach(`Phần RNN không giải thích được theo từng yếu tố và giữ nguyên khi thử nếu; M5 không có khuyến mãi nên mô hình không học được tác động khuyến mãi; mô hình chưa phân biệt tốt mã nào tăng mạnh khi khuyến mãi (tương quan thứ hạng ${vn(D.ss_km.tuong_quan_hang, 2)}).`),
  gach("Cảnh báo dự báo lệch dựa trên sai số đã qua chưa đạt luật (mục 8.5). Lịch âm lịch cho ngày tương lai (Tết, Trung thu, Giỗ Tổ) lấy từ bảng nhập tay, cần đối chiếu lịch chính thức; lịch thể thao không tự suy ra được."),
  gach("Hạn sử dụng, thể tích, sức chứa và phiên livestream đều dùng giả định; hạn sử dụng và sức chứa được xét riêng, chưa gộp. Chưa xét lịch đặt hàng cố định theo nhà cung cấp, gom đủ xe và số chuyến xe nhận hàng."),
  H2("10.2. Hướng phát triển"),
  gach([B("Dữ liệu thật: "), "nạp dữ liệu nhập – xuất – tồn từ hệ thống quản lý kho vào cùng cấu trúc và chạy lại toàn bộ."]),
  gach([B("Hàng chỉ bán dịp lễ: "), "đưa đặt một lần vào chính sách khi có thêm dữ liệu để kiểm chứng độc lập; hàng hạn ngắn có mùa dài cần giao nhiều đợt."]),
  gach([B("Phiên livestream: "), "thay tham số giả định bằng lịch phiên, đơn theo giờ và tỉ lệ hoàn đơn thật; kết nối đơn từ sàn."]),
  gach([B("Tồn kho an toàn theo phân vị sai số thực "), "thay cho giả định phân phối chuẩn (luật đã ghi, chưa chạy)."]),
  gach([B("Thông tin bên ngoài: "), "dự báo thời tiết, tin dịch bệnh để báo sớm các đợt tăng đột ngột mà cảnh báo dựa trên sai số đã qua chưa bắt kịp (mục 8.5)."]),
  gach([B("Ràng buộc vận hành: "), "gộp hạn sử dụng với sức chứa, lịch đặt hàng cố định, ước tính chuyến xe khi có thể tích và trọng lượng thật của từng mã."]),
];
const kl = [
  H1("KẾT LUẬN"),
  P(`Đề tài đã xây dựng được quy trình hoàn chỉnh từ dữ liệu đến quyết định đặt hàng cho kho tổng của một chuỗi siêu thị. Dự báo AI cập nhật mỗi tuần sai ${vn(100 * M.ket_hop_v4.wmape)}% theo ngày, gần mức tối thiểu do nhu cầu ngẫu nhiên, và mỗi con số dự báo có khoảng tin cậy đã được kiểm chứng. Khi đưa vào chính sách tồn kho, chính sách đề xuất đạt Fill Rate ${vn(ai.fill_rate_pt, 2)}%, giảm ${vn(-100 * lech(ai.chi_phi_lien_quan_trieu, moc.chi_phi_lien_quan_trieu))}% chi phí so với cùng công thức dùng dự báo đơn giản, và tốt hơn cả “hiện trạng” được biết trước nhu cầu về tồn kho, số ngày thiếu hàng lẫn tổng chi phí. Bài học quan trọng nhất là cách dùng dự báo – cập nhật thường xuyên, quy tắc đặt hàng hợp với từng loại hàng, cập nhật tham số khi lead time thay đổi – quan trọng không kém độ chính xác của mô hình.`),
  P(`Các con số trên đo trên dữ liệu mô phỏng. Khi chạy nguyên quy trình trên số bán thật M5, mô hình vẫn tốt hơn phương pháp đơn giản nhưng mức giảm sai số chỉ ${vn(100 * giamM5)}%, so với ${vn(100 * giamMP, 0)}% trên mô phỏng; đối chiếu với Dominick's cũng cho thấy một số giả định chưa sát. Đề tài cũng tự phát hiện điểm yếu của chính sách với hàng chỉ bán dịp lễ, đã thử newsvendor nhưng chưa đủ căn cứ đưa vào chính sách chính. Đóng góp của đề tài vì vậy là quy trình và phương pháp kiểm chứng có thể chạy lại trên dữ liệu thật, chưa phải một con số tiết kiệm cho kho cụ thể.`),
  P(`Hệ thống không chỉ đọc lại kết quả đã tính: màn Dự báo đứng ở ngày cuối của dữ liệu, dự báo 28 ngày chưa xảy ra, chạy lại mô hình ngay khi bấm (ra đúng bản đã chấm), giải thích từng con số theo nhóm yếu tố và cho thử nếu bật khuyến mãi. Khi bật khuyến mãi, mô hình tăng gần đúng mức lịch sử trên toàn kho. Kiểm chứng trên số thật cũng chỉ ra nơi AI có giá trị: lợi ích tồn kho gần như biến mất trên M5 nhưng rất lớn với hàng mùa vụ trên mô phỏng (${vn(100 * D.z.ton)}% mức giảm tồn kho); người quản lý kho nên ưu tiên dùng AI cho hàng mùa vụ, hàng theo sự kiện.`),
  new Paragraph({ children: [new PageBreak()] }),
  H1("PHỤ LỤC"),
  H2("A. Lệnh chạy lại toàn bộ (tại thư mục gốc dự án)"),
  ...["python src/lam_sach.py; python src/dac_trung.py; python src/eda.py",
    "python src/mo_hinh_baseline.py; python src/mo_hinh_prophet.py; python src/mo_hinh_lightgbm.py",
    "python src/chon_mo_hinh.py --vong 2; python src/nang_cap_du_bao.py --buoc …; python src/nang_cap_du_bao_v4.py --buoc …",
    "python src/tong_hop_ket_qua.py; python src/nap_database.py; python src/ton_kho.py; python src/do_nhay.py",
    "python src/bieu_do_ket_qua.py; python src/xuat_power_bi.py; python src/tao_trang_luong.py",
    "python src/chi_so_kho.py; python src/gom_don.py; python src/cham_diem_ncc.py; python src/rang_buoc_kho.py; python src/newsvendor_mua_vu.py; python src/tru_hang_live.py",
    "python src/phan_tich_dominicks.py --buoc gop; … --buoc tinh; … --buoc sau_doi_chieu; python src/so_lieu_do_an.py",
    "python src/do_nhay_chi_phi_dat.py; python src/canh_bao_lech_v2.py; python src/du_bao_tuong_lai.py; python src/chay_du_bao.py --so_sanh_km",
    "cd du_lieu_nguon/m5; python ../../src/du_bao_tuong_lai_kc.py --rnn ../../data/m5; python ../../src/du_bao_tuong_lai_kc.py ../../data/m5",
    "streamlit run app/dashboard.py"].map((l) => new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: l, font: "Consolas", size: 20 })] })),
  H2("B. Tài liệu kỹ thuật kèm theo"),
  gach("docs/10_bao_cao_giai_doan_2.md: báo cáo kỹ thuật chi tiết, luật ghi trước và nhật ký từng bước."),
  gach("reports/: bảng so sánh mô hình, báo cáo tồn kho, thử độ nhạy, bảng rủi ro, biểu đồ kết quả; reports/so_lieu_do_an.md: sổ gom mọi số liệu kèm nguồn."),
  gach("data/kho_hang.db: cơ sở dữ liệu; app/: dashboard; reports/power_bi/: dữ liệu Power BI."),
];

// ================================================================ TAI LIEU
const doc = new Document({
  creator: "Đồ án tốt nghiệp", title: "Báo cáo tổng hợp đồ án: Ứng dụng AI trong dự báo nhu cầu và tối ưu tồn kho",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 26 }, paragraph: { spacing: { line: 312, after: 120 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, allCaps: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 240, after: 240 }, outlineLevel: 0, pageBreakBefore: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, italics: true, font: FONT }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: { config: [{ reference: "gach", levels: [{ level: 0, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: Math.round(1.2 * CM), hanging: Math.round(0.5 * CM) } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 2 * CM, bottom: 2 * CM, left: 3 * CM, right: 2 * CM } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 24 })] })] }) },
    children: [...bia, ...mucLuc, ...c1, ...c2, ...c3, ...c4, ...c5, ...c6, ...c7, ...c8, ...c9, ...c10, ...kl],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("Da ghi", OUT, Math.round(buf.length / 1024), "KB"); });
