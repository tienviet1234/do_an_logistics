---
version: 1
slug: "app-dashboard-py"
primary_target: "app/dashboard.py"
related_targets: ["app/trang"]
---

# Surface brief: công cụ kế hoạch đặt hàng (app/dashboard.py + app/trang/*)

Mode: Operate. Người dùng chính: người lập kế hoạch kho (tự thao tác để ra kết quả); bối cảnh demo trước hội đồng bằng máy chiếu, offline.
Job: mở ra thấy việc cần làm hôm nay, duyệt đơn, hiểu vì sao, thử "nếu… thì sao", so sánh chính sách, giải thích dữ liệu và phương pháp.
4 màn: Hôm nay · Mặt hàng · Kịch bản & kết quả · Dữ liệu & phương pháp. Cơ chế kiểu Power BI: thanh lọc chung (ngày, chính sách, nhóm), lọc chéo bằng bấm biểu đồ / ô trạng thái / dòng bảng, đi sâu từ dòng mã hàng sang màn Mặt hàng.
Constraints: Streamlit 1.45 + Altair 5.5, chỉ đọc CSDL, tiếng Việt, dữ liệu mô phỏng phải ghi rõ; duyệt đơn chỉ giữ trong phiên + tải phiếu đặt hàng (CSV). Không có dữ liệu thể tích / trọng lượng → không ước tính số chuyến xe.

## Direction contract

THESIS: Công cụ là một bộ phiếu kế hoạch đặt hàng in sẵn mà người lập kế hoạch điền và đóng dấu, không phải một dashboard thẻ số liệu. Từ chối bố cục mặc định của ngành: thanh bên + hàng thẻ KPI + lưới biểu đồ.

OWN-WORLD: Giấy phiếu nhiều liên (mỗi màn một màu liên: trắng, vàng hoàng yến, hồng, vàng nghệ nhạt). Khung, đường kẻ, nhãn ô in bằng một màu "mực in phiếu" xanh Phổ; số liệu in bằng mực đen. Ô có số thứ tự như vận đơn. Trạng thái là con dấu cao su (viền đôi, nghiêng nhẹ): đỏ HẾT HÀNG, nâu hổ phách ĐẶT HÔM NAY, xanh Phổ ĐANG VỀ, xanh lá ĐỦ HÀNG. Việc cần làm được tô bút dạ quang vàng. Be Vietnam Pro tự lưu, số canh cột.

STORY: Người lập kế hoạch thấy số phiếu của ngày, mấy mã phải đặt, đóng dấu Duyệt / Sửa / Bỏ qua từng dòng, tải phiếu đặt hàng theo nhà cung cấp; hội đồng thấy hệ thống trả lời theo từng thao tác.

FIRST VIEWPORT: Đầu phiếu (tên phiếu, số phiếu theo ngày, các ô lọc ngày / chính sách / nhóm bên phải, đường kẻ đôi). Dưới: hàng 4 ô trạng thái bấm được; ô "Đặt hàng hôm nay" là tấm nền đảo màu duy nhất. Thân: trái 2/3 là các dòng đơn cần duyệt (tô dạ quang, nút Duyệt là hành động chính); phải 1/3 là dải cả năm bấm để đổi ngày.

FORM: Phiếu vận đơn / phiếu nhiều liên; vị trí 6 trong danh sách 7 hướng; seed key fd27efb6.
Raises: (từ kệ phim trực tuyến) chọn một mã thì mọi phần khác mờ xuống, chỉ mã được chọn đậm; (từ giá phiếu giờ tàu) mỗi màn chỉ một tấm nền đảo màu; (từ trang có ray giữa) mọi đường kẻ cùng một độ dày, không bo góc lớn; (từ lưới Crouwel) khung ô của phiếu là lưới bố cục thật, không trang trí.
Signature interaction: bấm Duyệt thì con dấu ĐÃ DUYỆT đóng xuống dòng đó (một lần, nhấn rồi nảy nhẹ).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
