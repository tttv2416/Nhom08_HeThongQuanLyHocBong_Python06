"""Module ui/cua_so_nhat_ky.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ xem nhật ký thao tác (thêm/sửa/xóa/nhập file), thao tác mới nhất nằm trên cùng.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from services.luu_tru_json import LoiFileError
from services.nhat_ky import NHAN_HANH_DONG
from ui.theme import KHOANG, MAU_CHINH, MAU_DONG_LE, MAU_NEN, MAU_NGUY_HIEM

SO_DONG_TOI_DA = 500
CAC_COT = (
    ("thoi_gian", "Thời gian", 175, "center"),
    ("nguoi_dung", "Người thực hiện", 120, "center"),
    ("hanh_dong", "Hành động", 90, "center"),
    ("ma_sv", "Mã SV", 100, "center"),
    ("chi_tiet", "Chi tiết", 420, "w"),
)
MAU_THEO_HANH_DONG = {"THEM": "#2e7d32", "SUA": MAU_CHINH, "XOA": MAU_NGUY_HIEM, "NHAP_FILE": "#8a5a00"}


class CuaSoNhatKy(tk.Toplevel):
    """Cửa sổ xem nhật ký; gọi lam_moi() để đọc lại file."""

    def __init__(self, master, nhat_ky):
        super().__init__(master)
        self.nhat_ky = nhat_ky
        self.title("Nhật ký thao tác sinh viên")
        self.geometry("960x480")
        self.minsize(720, 320)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.var_thong_tin = tk.StringVar()
        ttk.Label(self, textvariable=self.var_thong_tin).grid(
            row=0, column=0, sticky="ew", padx=12, pady=(12, KHOANG))

        khung = ttk.Frame(self)
        khung.grid(row=1, column=0, sticky="nsew", padx=12)
        khung.columnconfigure(0, weight=1)
        khung.rowconfigure(0, weight=1)
        self.bang = ttk.Treeview(khung, columns=[c[0] for c in CAC_COT], show="headings", selectmode="browse")
        for ma_cot, tieu_de, rong, can in CAC_COT:
            self.bang.heading(ma_cot, text=tieu_de)
            self.bang.column(ma_cot, width=rong, anchor=can, stretch=(ma_cot == "chi_tiet"))
        for hanh_dong, mau in MAU_THEO_HANH_DONG.items():
            self.bang.tag_configure(hanh_dong, foreground=mau)
        thanh_cuon = ttk.Scrollbar(khung, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=thanh_cuon.set)
        self.bang.grid(row=0, column=0, sticky="nsew")
        thanh_cuon.grid(row=0, column=1, sticky="ns")

        khung_nut = ttk.Frame(self)
        khung_nut.grid(row=2, column=0, sticky="e", padx=12, pady=12)
        ttk.Button(khung_nut, text="Làm mới", command=self.lam_moi).grid(row=0, column=0, padx=(0, KHOANG))
        ttk.Button(khung_nut, text="Đóng", command=self.destroy).grid(row=0, column=1)

        self.lam_moi()

    def lam_moi(self):
        try:
            ban_ghi = self.nhat_ky.doc_gan_day(SO_DONG_TOI_DA)
        except LoiFileError as e:
            messagebox.showerror("Không đọc được nhật ký", str(e), parent=self)
            return
        self.bang.delete(*self.bang.get_children())
        for i, d in enumerate(ban_ghi):
            nhan = NHAN_HANH_DONG.get(d["hanh_dong"], d["hanh_dong"])
            self.bang.insert("", "end", iid=str(i), tags=(d["hanh_dong"],), values=(
                d["thoi_gian"], d["nguoi_dung"], nhan, d["ma_sv"], d["chi_tiet"]))
        if ban_ghi:
            self.var_thong_tin.set(f"Hiển thị {len(ban_ghi)} thao tác gần nhất (mới nhất ở trên). "
                                   f"File: {self.nhat_ky.duong_dan}")
        else:
            self.var_thong_tin.set(f"Chưa có thao tác nào được ghi lại. File: {self.nhat_ky.duong_dan}")
