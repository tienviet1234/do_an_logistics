---
name: Phiếu kế hoạch đặt hàng
description: Công cụ kế hoạch đặt hàng cho kho tổng, dựng như một bộ phiếu in sẵn nhiều liên được điền và đóng dấu.
colors:
  form-ink: "#1d4f73"
  form-ink-deep: "#173f5d"
  data-ink: "#15171a"
  data-ink-soft: "#4a4d52"
  rule: "#9db0bf"
  highlighter: "#ffe45c"
  highlighter-press: "#ffd820"
  stamp-red: "#b3261e"
  stamp-amber: "#93560a"
  stamp-green: "#2e6b3f"
  ply-white: "#fdfdfb"
  ply-canary: "#fbf5d6"
  ply-pink: "#f9ebe8"
  ply-green: "#eaf1e7"
  field-fill: "#eef1f2"
  scrollbar: "#b7c4ce"
  series-actual: "#15171a"
  series-ai: "#1f6fb2"
  series-ai-raw: "#8db7de"
  series-baseline: "#c0661c"
  series-current: "#8a8a85"
typography:
  form-title:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1.85rem"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  section:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1.18rem"
    fontWeight: 700
    lineHeight: 1.3
  item-title:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 800
    letterSpacing: "-0.01em"
  order-number:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 700
  tab:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
  note:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.88rem"
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.86rem"
    fontWeight: 400
  caption-small:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.84rem"
    fontWeight: 400
    lineHeight: 1.45
  field-label:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 600
    letterSpacing: "0.05em"
  field-value:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 700
    lineHeight: 1.25
  status-count:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "2.3rem"
    fontWeight: 800
    lineHeight: 1.05
  body:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  stamp:
    fontFamily: "Be Vietnam Pro, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 800
    letterSpacing: "0.06em"
rounded:
  none: "0px"
  control: "2px"
spacing:
  field-x: "0.7rem"
  field-y: "0.45rem"
  section-top: "1.6rem"
  section-bottom: "0.7rem"
components:
  button-action:
    backgroundColor: "{colors.highlighter}"
    textColor: "{colors.data-ink}"
    rounded: "{rounded.control}"
  button-action-hover:
    backgroundColor: "{colors.highlighter-press}"
  button-form:
    backgroundColor: "transparent"
    textColor: "{colors.form-ink}"
    rounded: "{rounded.control}"
  status-plate:
    backgroundColor: "{colors.form-ink}"
    textColor: "#ffffff"
    rounded: "{rounded.none}"
  status-box:
    backgroundColor: "transparent"
    textColor: "{colors.data-ink}"
    rounded: "{rounded.none}"
  field-row:
    backgroundColor: "transparent"
    textColor: "{colors.data-ink}"
    rounded: "{rounded.none}"
    padding: "0.45rem 0.7rem 0.55rem"
---

# Design System: Phiếu kế hoạch đặt hàng

## Overview

**Creative North Star: "Bộ phiếu in sẵn được điền và đóng dấu"**

Giao diện là một bộ phiếu kế hoạch đặt hàng nhiều liên. Khung, đường kẻ và nhãn ô được in bằng một màu mực phiếu xanh Phổ. Số liệu do hệ thống điền vào bằng mực đen. Quyết định của người lập kế hoạch hiện ra như con dấu cao su. Mỗi màn là một liên giấy có màu riêng: Hôm nay trắng, Mặt hàng vàng hoàng yến, Kịch bản & kết quả hồng, Dữ liệu & phương pháp xanh nhạt. Hệ thống không dùng thanh bên, không dùng lưới thẻ KPI, không bo góc mềm.

**Key Characteristics:**
- Một màu mực phiếu cho mọi cấu trúc (khung, nhãn, tiêu đề mục, trục biểu đồ); số liệu luôn bằng mực đen.
- Trạng thái là con dấu: viền đôi, nghiêng −3°, chữ hoa kèm biểu tượng tự vẽ. Không bao giờ chỉ dùng màu.
- Việc cần làm được tô bút dạ quang vàng; vàng chỉ xuất hiện ở chỗ có thể bấm hoặc phải xử lý.
- Mỗi màn có đúng một tấm nền đảo màu (mực phiếu, chữ trắng, điểm nhấn vàng).
- Số canh cột (tabular numerals), đọc rõ trên máy chiếu.

## Colors

Chiến lược Restrained: nền giấy theo liên, một màu mực phiếu cho cấu trúc, vàng dạ quang chỉ cho hành động, ba màu con dấu cho trạng thái.

### Primary
- **Mực phiếu** (`form-ink` #1d4f73): khung ô, nhãn ô, tiêu đề mục, đường kẻ chính, trục biểu đồ, tấm nền đảo màu, chữ của nút phụ.

### Secondary
- **Dạ quang** (`highlighter` #ffe45c): nút hành động chính (Duyệt, Tải phiếu đặt hàng), nét tô dưới số lượng đề xuất, vòng của ô trạng thái đang lọc, dòng bảng đang chọn (pha 38%). Trên tấm nền đảo màu, dạ quang là màu của con số.

### Tertiary
- **Con dấu:** đỏ `stamp-red` cho Hết hàng; hổ phách `stamp-amber` cho Đặt hôm nay và Đã sửa; xanh Phổ (`form-ink`) cho Đang về; xanh lá `stamp-green` cho Đủ hàng, Đã duyệt và Đề xuất. Màu xám `data-ink-soft` dùng cho Bỏ qua.
- **Chuỗi số liệu trong biểu đồ:** thực tế đen, AI `series-ai`, AI chưa hiệu chỉnh `series-ai-raw`, dự báo mốc `series-baseline` (nét đứt), hiện trạng `series-current`. Dải cả năm dùng #c8443b / #e0a030 / #7fa6c4 để tô diện tích, nhạt hơn màu con dấu.

### Neutral
- **Liên giấy:** `ply-white`, `ply-canary`, `ply-pink`, `ply-green`. Nền trang lấy theo màn đang mở; thẻ chuyển màn mang màu liên của chính màn đó.
- **Mực đen** `data-ink` cho số liệu và thân chữ; `data-ink-soft` cho chữ phụ. Đường kẻ phụ dùng `rule`; thanh cuộn dùng `scrollbar`.

### Named Rules
**Quy tắc một màu mực.** Mọi cấu trúc dùng `form-ink`. Không thêm màu thứ hai cho khung hay nhãn.
**Quy tắc vàng là việc.** Dạ quang chỉ đặt ở chỗ bấm được hoặc phải xử lý, không dùng làm trang trí.

## Typography

**Font:** Be Vietnam Pro (lưu trong `app/static/fonts`, khai báo `[[theme.fontFaces]]` với khóa `family`), dùng cho mọi vai trò kể cả nhãn trục biểu đồ.

### Hierarchy
- **Tên phiếu** (800, 1.85rem, −0.01em): một lần ở đầu phiếu, màu mực phiếu.
- **Mã + tên hàng** (800, 1.6rem): ở màn Mặt hàng; mã màu mực phiếu, tên màu mực đen.
- **Tiêu đề mục** (700, 1.18rem, mực phiếu): luôn có đường kẻ 1px mực phiếu phía dưới; chú thích ngắn màu chữ phụ đặt cùng hàng.
- **Nhãn ô** (600, 0.74rem, chữ hoa, +0.05em, mực phiếu): nằm trong ô phiếu hoặc trên ô nhập. Không bao giờ đặt làm dòng nhỏ phía trên tiêu đề.
- **Giá trị ô** (700, 1.3rem); **số trạng thái** (800, 2.3rem, màu con dấu).
- **Thân chữ** (400, 1rem, line-height 1.55); ghi chú dưới biểu đồ 0.88rem; chú thích cạnh tiêu đề mục 0.86rem; dòng phụ của đơn hàng và chân phiếu 0.84rem; chữ thẻ chuyển màn 0.95rem; số trong dòng đơn 1.05rem.

## Layout

- Khung chính rộng tối đa 1480px, đệm 2rem; trên điện thoại đệm 1rem.
- **Đầu phiếu:** tên phiếu | các ô lọc chung (ngày, chính sách, ABC, XYZ) | ô số phiếu (khung 1px mực phiếu). Dưới là hàng thẻ chuyển màn, rồi đường kẻ đôi `ke-doi` (2 nét 1px).
- **Ô phiếu** (`o-hang`): lưới cột đều theo class `n2`–`n6`, khung 1px mực phiếu, vách 1px màu đường kẻ; trên điện thoại gập thành 2 cột.
- **Màn Hôm nay:** hàng 4 ô trạng thái; thân chia 1,85 : 1 (đơn cần duyệt | dải cả năm); danh sách theo dõi trải toàn chiều rộng.
- Dòng đơn cần duyệt: 3 cột (mã và lý do | 4 số | ô chọn quyết định + con dấu), ngăn bằng đường kẻ 1px.

## Elevation & Depth

Phẳng như giấy. Phân lớp bằng đường kẻ và nền đảo màu, không dùng bóng. Hệ thống không có bóng nào, kể cả bóng cứng.

## Shapes

Góc vuông cho khung, ô phiếu, bảng, thẻ chuyển màn, con dấu và các ô thông báo. Nút và ô nhập bo 2px (`control`). Nút tròn chỉ còn ở các nút chọn ABC/XYZ mặc định của Streamlit.

## Components

### Buttons
- **Hành động** (`kind="primary"`): nền dạ quang, chữ mực đen, viền 1px mực đen; khi rê chuột thì sang #ffd820.
- **Nút phụ** (`kind="secondary"`): nền trong suốt, viền và chữ mực phiếu; khi rê chuột thì nền mực phiếu pha 8%.
- **Liên kết** (`kind="tertiary"`): chữ mực phiếu có gạch chân, cách chữ 3px.

### Ô trạng thái (lọc chéo)
Mỗi ô là một nút cao 6.2rem, khung 1px mực phiếu. Biểu tượng SVG tự vẽ được gắn bằng CSS mask, con số màu con dấu, nhãn phía dưới. Ô "Đặt hàng hôm nay" là tấm nền đảo màu của màn. Ô đang lọc có vòng dạ quang 3px phía trong và chữ "· đang lọc".

### Con dấu (signature)
`<span class="dau {do|hophach|phieu|la|xam}">`: viền đôi 3px theo màu, nền pha 6%, nghiêng −3°, có biểu tượng 15px. Con dấu mới hiện ra (`dau-moi`) có hiệu ứng nhấn xuống một lần trong 340ms: phóng 1,9 lần, mờ nhẹ, rồi về vị trí. Hiệu ứng tắt khi người dùng bật giảm chuyển động.

### Ô chọn quyết định
Ô chọn phân đoạn Duyệt / Sửa / Bỏ qua, góc vuông. "Duyệt" luôn tô dạ quang; lựa chọn đang chọn có nền mực phiếu và chữ trắng. Bấm lại lựa chọn đang chọn là hoàn tác.

### Bảng phiếu
`table.phieu`: khung 1px mực phiếu, tiêu đề cột theo kiểu nhãn ô (căn phải với cột số), dòng ngăn 1px màu đường kẻ, dòng đang chọn tô dạ quang 38% và chữ đậm.

### Navigation
Thẻ chuyển màn: khung 1px màu đường kẻ, không có cạnh dưới, nền là màu liên của màn đó. Thẻ của màn đang mở có khung mực phiếu và chữ 800.

### Biểu đồ (Altair)
Theme `phieu`: nền trong suốt, font Be Vietnam Pro, trục và tiêu đề màu mực phiếu, lưới chấm gạch mực phiếu 13%. Biểu đồ bấm được phải là biểu đồ một lớp dạng cột / ô / điểm (Streamlit 1.45; biểu đồ đường không nhận cú bấm), nên chỗ cần bấm chọn ngày dùng dải ô chữ nhật theo ngày. Mỗi biểu đồ có ghi chú "Cách đọc / Phát hiện" ở dưới, ngăn bằng nét đứt.

## Do's and Don'ts

- **Nên** đặt màu con dấu bằng class. Streamlit lọc bỏ thuộc tính `style` trong HTML.
- **Nên** luôn ghi chữ cùng biểu tượng cho trạng thái.
- **Nên** giữ đúng một tấm nền đảo màu cho mỗi màn.
- **Không** dùng viền màu dày một cạnh, bóng cứng, chữ gradient hay emoji làm biểu tượng.
- **Không** đặt nhãn nhỏ viết hoa phía trên tiêu đề mục.
- **Không** dùng dạ quang làm trang trí.
- **Không** thêm màu thứ hai cho khung hay nhãn.
