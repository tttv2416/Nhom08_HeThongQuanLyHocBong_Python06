# Quản lý sinh viên - Hướng dẫn chạy và test

Phần **quản lý sinh viên** của Hệ thống quản lý học bổng (Nhóm 08).
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275.

Phần học bổng (hồ sơ, xét duyệt, thống kê) chưa hoàn thành và không nằm trong tài liệu này.

## 1. Yêu cầu

- Python 3.10 trở lên.
- Tkinter (đi kèm Python trên Windows và macOS). Trên Linux có thể cần cài thêm: `sudo apt install python3-tk`.
- Không cần cài thư viện bên ngoài. Test dùng `unittest` có sẵn.

## 2. Cấu trúc thư mục

```
project/
├── config.py                  # đường dẫn file dữ liệu
├── data/                      # sinh_vien.json, ho_so.json (tự tạo nếu chưa có)
├── models/
│   └── sinh_vien.py           # lớp SinhVien, hàm kiểm tra dữ liệu nhập
├── services/
│   ├── luu_tru_json.py        # đọc/ghi file JSON an toàn, có file .bak
│   ├── quan_ly_sinh_vien.py   # thêm, sửa, xóa, tìm kiếm, sắp xếp
│   └── rang_buoc_ho_so.py     # kiểm tra sinh viên có hồ sơ học bổng không
├── ui/
│   ├── menu_sinh_vien.py      # giao diện console
│   └── giao_dien_sinh_vien.py # giao diện Tkinter
└── tests/                     # bộ test tự động
```

## 3. Quy tắc quan trọng khi làm việc

- **Luôn chạy lệnh từ thư mục gốc `project/`** (thư mục có `config.py`). Chạy từ thư mục khác sẽ lỗi `ModuleNotFoundError`.
- Dùng cú pháp `python -m <tên.module>` thay vì `python <đường dẫn file>`.
- Test không ghi vào `data/` thật. Mọi test dùng file tạm.

## 4. Chạy chương trình

### Giao diện Tkinter (khuyến nghị)

```bash
python -m ui.giao_dien_sinh_vien
```

Các chức năng:
- Form nhập bên trái, chi tiết và thanh tiến trình GPA/điểm rèn luyện bên phải.
- Bảng danh sách: bấm tiêu đề cột để sắp xếp, bấm lần nữa để đảo chiều.
- Tìm kiếm theo mã, họ tên, lớp; có tùy chọn "Gần đúng" và lọc theo lớp.
- Phím tắt: `F5` tải lại dữ liệu từ file, `Ctrl+F` đưa con trỏ tới ô tìm kiếm.

### Giao diện console

```bash
python -m ui.menu_sinh_vien
```

Chọn số tương ứng trong menu. Khi đang nhập liệu, gõ `huy` để hủy thao tác. Khi sửa, nhấn Enter để giữ giá trị cũ.

## 5. Quy tắc nhập liệu

| Trường | Quy tắc | Ví dụ hợp lệ |
|---|---|---|
| Mã sinh viên | Đúng 10 chữ số, không trùng | `2044240275` |
| Họ và tên | Chỉ chữ cái (có dấu được), ít nhất 2 từ | `Nguyễn Thị Đông Phương` |
| Lớp | 2-20 ký tự, chữ, số, `-`, `_`, `.`; tự viết hoa | `DHKL16A` |
| GPA | Số từ 0 đến 4.0, chấp nhận dấu phẩy | `3.25` hoặc `3,25` |
| Điểm rèn luyện | Số từ 0 đến 100 | `85` |

Mã sinh viên không sửa được sau khi tạo.

Xếp loại học lực theo GPA: Xuất sắc (≥ 3.6), Giỏi (≥ 3.2), Khá (≥ 2.5), Trung bình (≥ 2.0), Yếu (< 2.0).

Xếp loại rèn luyện: Xuất sắc (≥ 90), Tốt (≥ 80), Khá (≥ 65), Trung bình (≥ 50), Yếu (≥ 35), Kém (< 35).

## 6. Quy tắc xóa sinh viên

Sinh viên đang có hồ sơ học bổng trong `data/ho_so.json` **không được xóa**. Muốn xóa, phải xóa hồ sơ học bổng trước.

## 7. Chạy test

Từ thư mục gốc `project/`:

```bash
python -m unittest discover -s tests -t . -v
```

Hoặc dùng pytest nếu máy đã cài:

```bash
python -m pytest tests -v
```

Kết quả mong đợi: `Ran 81 tests ... OK (skipped=5)`. Số test bị bỏ qua (5) là test giao diện, chỉ chạy khi máy có Tkinter và màn hình. Nếu chạy trên máy có Tkinter, kết quả sẽ là `Ran 81 tests ... OK`.

Chạy riêng từng nhóm test:

```bash
python -m unittest tests.test_sinh_vien -v            # kiểm tra dữ liệu nhập
python -m unittest tests.test_quan_ly_sinh_vien -v    # thêm, sửa, xóa, tìm, lưu file
python -m unittest tests.test_menu_sinh_vien -v       # menu console, nhập sai, trùng mã
python -m unittest tests.test_giao_dien_sinh_vien -v  # giao diện Tkinter
```

## 8. Kịch bản kiểm tra thủ công

Chạy `python -m ui.menu_sinh_vien` và thử:

1. Chọn 2, nhập mã `2044240275` (đã tồn tại): báo "đã tồn tại".
2. Chọn 2, nhập mã `12345`: báo lỗi 10 chữ số, yêu cầu nhập lại.
3. Chọn 2, nhập GPA `4.5`: báo lỗi khoảng giá trị.
4. Chọn 2, gõ `huy` ở bất kỳ bước nào: thoát, không lưu gì.
5. Chọn 4, xóa sinh viên `2044240101` (có hồ sơ HS001): bị chặn.
6. Chọn 5, tìm `minh anh` với tiêu chí "Họ tên": tìm được Trần Minh Anh.

Chạy `python -m ui.giao_dien_sinh_vien` và thử:

1. Chọn một sinh viên, lọc sang lớp khác: ô mã phải mở lại được để nhập mã mới.
2. Nhập mã trùng rồi bấm "Thêm mới": báo "Trùng mã sinh viên".
3. Bấm tiêu đề cột "GPA" hai lần: danh sách đảo chiều.
e cho nhóm, chạy toàn bộ test và đảm bảo không có test nào lỗi.