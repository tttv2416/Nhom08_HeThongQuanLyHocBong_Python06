"""Module ui/theme.py
Bảng màu, font, khoảng cách và tiện ích dùng chung cho giao diện sinh viên.
Phong cách: nền xám-xanh nhạt, thẻ trắng viền mảnh, điểm nhấn indigo.
Giữ nguyên tên các hằng số cũ để các module khác không cần sửa.
"""

import tkinter as tk

# ---- Font ----
# Windows: "Segoe UI". macOS: "SF Pro Text" hoặc "Helvetica". Linux: "Ubuntu" hoặc "DejaVu Sans".
FONT_HO = "Segoe UI"
FONT = (FONT_HO, 10)
FONT_DAM = (FONT_HO, 10, "bold")
FONT_NHO = (FONT_HO, 9)
FONT_DAM_NHO = (FONT_HO, 9, "bold")
FONT_NHAN_NHO = (FONT_HO, 8, "bold")        # nhãn viết hoa nhỏ (caption)
FONT_TIEU_DE_THE = (FONT_HO, 12, "bold")    # tiêu đề trong thẻ
FONT_TIEU_DE = (FONT_HO, 18, "bold")        # tiêu đề cửa sổ
FONT_SO_LON = (FONT_HO, 20, "bold")         # số liệu KPI

# ---- Nền và thẻ ----
MAU_NEN = "#F1F5F9"
MAU_THE = "#FFFFFF"
MAU_VIEN = "#E2E8F0"
MAU_DONG_LE = "#F8FAFC"
MAU_CHON = "#E0E7FF"

# ---- Chữ ----
MAU_CHU = "#0F172A"
MAU_CHU_PHU = "#64748B"

# ---- Điểm nhấn ----
MAU_CHINH = "#4F46E5"
MAU_CHINH_DAM = "#4338CA"
MAU_CHINH_NHAT = "#A5B4FC"
MAU_NGUY_HIEM = "#E11D48"
MAU_NGUY_HIEM_DAM = "#BE123C"
MAU_THANH_CONG = "#059669"
MAU_CANH_BAO = "#D97706"

# ---- Header ----
MAU_HEADER = "#0F172A"
MAU_HEADER_PHU = "#94A3B8"

KHOANG = 8

# Màu theo mức học lực (dùng cho huy hiệu, biểu đồ, chú thích)
MAU_HOC_LUC = {
    "Xuất sắc": "#059669",
    "Giỏi": "#2563EB",
    "Khá": "#D97706",
    "Trung bình": "#EA580C",
    "Yếu": "#DC2626",
}


def tao_the(master):
    """Thẻ trắng có viền mảnh, dùng thay cho LabelFrame cũ."""
    return tk.Frame(master, bg=MAU_THE, highlightbackground=MAU_VIEN,
                    highlightthickness=1, bd=0)


def kich_thuoc_canvas(canvas):
    """(rộng, cao) thực tế của Canvas; nếu chưa hiển thị thì dùng kích thước đã cấu hình."""
    rong, cao = canvas.winfo_width(), canvas.winfo_height()
    if rong <= 1:
        rong = int(canvas.cget("width"))
    if cao <= 1:
        cao = int(canvas.cget("height"))
    return rong, cao