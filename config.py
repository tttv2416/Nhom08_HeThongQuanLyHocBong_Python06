"""Cấu hình chung: đường dẫn thư mục và file dữ liệu.

Khi đóng gói bằng PyInstaller, thư mục data nằm cạnh file .exe để ghi được dữ liệu.
"""

import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

DUONG_DAN_SINH_VIEN = os.path.join(DATA_DIR, "sinh_vien.json")
DUONG_DAN_HOC_BONG = os.path.join(DATA_DIR, "hoc_bong.json")
DUONG_DAN_HO_SO = os.path.join(DATA_DIR, "ho_so.json")
DUONG_DAN_TAI_KHOAN = os.path.join(DATA_DIR, "tai_khoan.json")
DUONG_DAN_NHAT_KY = os.path.join(DATA_DIR, "nhat_ky.log")
