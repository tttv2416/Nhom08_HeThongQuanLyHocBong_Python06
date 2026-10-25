"""Module ui/cua_so_thong_ke.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ thống kê sinh viên, hai biểu đồ tự vẽ bằng Canvas (không cần cài thư viện nào):
- Biểu đồ cột : số sinh viên theo lớp.
- Biểu đồ tròn: tỷ lệ học lực (Xuất sắc, Giỏi, Khá, Trung bình, Yếu).
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk

from services.luu_tru_json import LoiFileError
from services.thong_ke_sinh_vien import dem_theo_hoc_luc, dem_theo_lop, tong_quan
from ui.theme import (FONT, FONT_DAM, FONT_DAM_NHO, FONT_NHO, KHOANG, MAU_CHINH, MAU_HOC_LUC,
                      MAU_NEN, kich_thuoc_canvas)


class CuaSoThongKe(tk.Toplevel):
    """Cửa sổ biểu đồ thống kê; gọi lam_moi() để vẽ lại khi dữ liệu thay đổi."""

    def __init__(self, master, ql):
        super().__init__(master)
        self.ql = ql
        self.title("Thống kê sinh viên")
        self.geometry("940x540")
        self.minsize(780, 460)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.var_tong_quan = tk.StringVar()
        ttk.Label(self, textvariable=self.var_tong_quan, font=FONT_DAM, wraplength=880,
                  justify="left").grid(row=0, column=0, columnspan=2, sticky="ew",
                                       padx=12, pady=(12, KHOANG))

        khung_cot = ttk.LabelFrame(self, text="Số sinh viên theo lớp", padding=KHOANG + 2)
        khung_cot.grid(row=1, column=0, sticky="nsew", padx=(12, KHOANG))
        khung_tron = ttk.LabelFrame(self, text="Tỷ lệ học lực", padding=KHOANG + 2)
        khung_tron.grid(row=1, column=1, sticky="nsew", padx=(KHOANG, 12))
        for khung in (khung_cot, khung_tron):
            khung.columnconfigure(0, weight=1)
            khung.rowconfigure(0, weight=1)

        self.cv_cot = tk.Canvas(khung_cot, bg="white", highlightthickness=0, width=420, height=330)
        self.cv_cot.grid(row=0, column=0, sticky="nsew")
        self.cv_tron = tk.Canvas(khung_tron, bg="white", highlightthickness=0, width=420, height=330)
        self.cv_tron.grid(row=0, column=0, sticky="nsew")
        self.cv_cot.bind("<Configure>", lambda _e: self.ve_cot())
        self.cv_tron.bind("<Configure>", lambda _e: self.ve_tron())

        khung_nut = ttk.Frame(self)
        khung_nut.grid(row=2, column=0, columnspan=2, sticky="e", padx=12, pady=12)
        ttk.Button(khung_nut, text="Làm mới", command=self.lam_moi_tu_file).grid(row=0, column=0, padx=(0, KHOANG))
        ttk.Button(khung_nut, text="Đóng", command=self.destroy).grid(row=0, column=1)

        self.lam_moi()

    # ------------------------------------------------------------------
    def lam_moi(self):
        """Vẽ lại theo dữ liệu hiện có trong bộ nhớ."""
        ds = self.ql.danh_sach()
        s = tong_quan(ds)
        if s["tong"] == 0:
            self.var_tong_quan.set("Chưa có sinh viên nào để thống kê.")
        else:
            cao = s["gpa_cao_nhat"]
            self.var_tong_quan.set(
                f"Tổng {s['tong']} sinh viên thuộc {s['so_lop']} lớp   |   "
                f"GPA trung bình: {s['gpa_tb']:.2f}   |   "
                f"Điểm rèn luyện trung bình: {s['drl_tb']:.1f}   |   "
                f"GPA cao nhất: {cao.ho_ten} ({cao.gpa:.2f})")
        self.ve_cot()
        self.ve_tron()

    def lam_moi_tu_file(self):
        """Đọc lại dữ liệu từ file JSON rồi vẽ lại."""
        try:
            self.ql.tai_du_lieu()
        except LoiFileError as e:
            messagebox.showerror("Không đọc được dữ liệu", str(e), parent=self)
            return
        self.lam_moi()

    # ------------------------------------------------------------------
    @staticmethod
    def _buoc_chia(lon_nhat):
        """Khoảng cách giữa các vạch trục tung (số nguyên, tối đa khoảng 5 vạch)."""
        return 1 if lon_nhat <= 5 else max(1, -(-lon_nhat // 5))

    def ve_cot(self):
        cv = self.cv_cot
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du_lieu = dem_theo_lop(self.ql.danh_sach())
        if not du_lieu:
            cv.create_text(w / 2, h / 2, text="Chưa có dữ liệu", font=FONT, fill="#666666")
            return
        le_trai, le_phai, le_tren, le_duoi = 40, 16, 26, 36
        vung_rong = w - le_trai - le_phai
        vung_cao = h - le_tren - le_duoi
        if vung_rong < 30 or vung_cao < 30:
            return
        lon_nhat = max(n for _, n in du_lieu)
        buoc = self._buoc_chia(lon_nhat)
        tran = -(-lon_nhat // buoc) * buoc  # làm tròn lên bội của bước chia
        day = h - le_duoi

        for gia_tri in range(0, tran + 1, buoc):  # đường lưới và nhãn trục tung
            y = day - vung_cao * gia_tri / tran
            cv.create_line(le_trai, y, w - le_phai, y, fill="#e3e7ee")
            cv.create_text(le_trai - 6, y, text=str(gia_tri), anchor="e", font=FONT_NHO, fill="#555555")

        o_rong = vung_rong / len(du_lieu)
        rong_cot = min(60, o_rong * 0.6)
        so_ky_tu = max(3, int(o_rong // 7))
        for i, (lop, n) in enumerate(du_lieu):
            x = le_trai + o_rong * (i + 0.5)
            y_dinh = day - vung_cao * n / tran
            cv.create_rectangle(x - rong_cot / 2, y_dinh, x + rong_cot / 2, day, fill=MAU_CHINH, outline="")
            cv.create_text(x, y_dinh - 9, text=str(n), font=FONT_DAM_NHO, fill=MAU_CHINH)
            ten = lop if len(lop) <= so_ky_tu else lop[:so_ky_tu - 1] + "."
            cv.create_text(x, day + 14, text=ten, font=FONT_NHO, fill="#333333")
        cv.create_line(le_trai, day, w - le_phai, day, fill="#888888")

    def ve_tron(self):
        cv = self.cv_tron
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du_lieu = dem_theo_hoc_luc(self.ql.danh_sach())
        tong = sum(n for _, n in du_lieu)
        if tong == 0:
            cv.create_text(w / 2, h / 2, text="Chưa có dữ liệu", font=FONT, fill="#666666")
            return
        duong_kinh = min(h - 30, w * 0.52)
        if duong_kinh < 40:
            return
        r = duong_kinh / 2
        cx, cy = 16 + r, h / 2

        goc = 90.0  # bắt đầu từ 12 giờ, quay theo chiều kim đồng hồ
        for nhan, n in du_lieu:
            if n == 0:
                continue
            phan = n / tong
            quet = -360.0 * phan
            mau = MAU_HOC_LUC[nhan]
            if phan >= 0.9999:  # một mức duy nhất: cung 360 độ không vẽ được, dùng hình tròn
                cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=mau, outline="white", width=2)
            else:
                cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=goc, extent=quet,
                              fill=mau, outline="white", width=2, style="pieslice")
            if phan >= 0.06:  # lát đủ lớn mới ghi phần trăm
                g = math.radians(goc + quet / 2)
                cv.create_text(cx + 0.62 * r * math.cos(g), cy - 0.62 * r * math.sin(g),
                               text=f"{phan * 100:.0f}%", font=FONT_DAM_NHO, fill="white")
            goc += quet

        # chú thích bên phải
        x_ct = 16 + duong_kinh + 24
        y_ct = h / 2 - len(du_lieu) * 14
        for nhan, n in du_lieu:
            cv.create_rectangle(x_ct, y_ct - 6, x_ct + 12, y_ct + 6, fill=MAU_HOC_LUC[nhan], outline="")
            cv.create_text(x_ct + 20, y_ct, anchor="w", font=FONT_NHO, fill="#333333",
                           text=f"{nhan}: {n} ({n / tong * 100:.0f}%)")
            y_ct += 28
