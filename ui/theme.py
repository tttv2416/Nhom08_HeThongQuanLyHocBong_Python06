"""Module ui/theme.py
Font, màu sắc, khoảng cách dùng chung cho các màn hình sinh viên (giao diện thống nhất).
"""

FONT = ("Segoe UI", 10)
FONT_DAM = ("Segoe UI", 10, "bold")
FONT_NHO = ("Segoe UI", 9)
FONT_DAM_NHO = ("Segoe UI", 9, "bold")
FONT_TIEU_DE = ("Segoe UI", 16, "bold")

MAU_NEN = "#f4f6fa"
MAU_CHINH = "#1f4e8c"
MAU_NGUY_HIEM = "#b3261e"
MAU_DONG_LE = "#eaf1fb"
KHOANG = 6

# màu theo mức học lực (dùng cho biểu đồ tròn)
MAU_HOC_LUC = {
    "Xuất sắc": "#2e7d32",
    "Giỏi": "#1f6fb2",
    "Khá": "#e0a100",
    "Trung bình": "#f08a24",
    "Yếu": "#c62828",
}


def kich_thuoc_canvas(canvas):
    """(rộng, cao) thực tế của Canvas; nếu cửa sổ chưa hiển thị thì dùng kích thước đã cấu hình."""
    rong, cao = canvas.winfo_width(), canvas.winfo_height()
    if rong <= 1:
        rong = int(canvas.cget("width"))
    if cao <= 1:
        cao = int(canvas.cget("height"))
    return rong, cao
