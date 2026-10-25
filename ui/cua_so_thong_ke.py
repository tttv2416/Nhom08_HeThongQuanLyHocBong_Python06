"""Module ui/cua_so_thong_ke.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ thống kê phong cách hiện đại, vẽ bằng Canvas (không cần thư viện ngoài):
- Biểu đồ cột bo góc: số sinh viên theo lớp, cột cao nhất được nhấn màu đậm.
- Biểu đồ donut: tỷ lệ học lực, tổng ở giữa và chú thích bên phải.
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk

from services.luu_tru_json import LoiFileError
from services.thong_ke_sinh_vien import dem_theo_hoc_luc, dem_theo_lop, tong_quan
from ui.theme import (FONT, FONT_DAM_NHO, FONT_NHAN_NHO, FONT_NHO, FONT_SO_LON, FONT_TIEU_DE,
                      FONT_TIEU_DE_THE, KHOANG, MAU_CHINH, MAU_CHINH_NHAT, MAU_CHU, MAU_CHU_PHU,
                      MAU_HOC_LUC, MAU_NEN, MAU_THE, MAU_VIEN, kich_thuoc_canvas, tao_the)


class CuaSoThongKe(tk.Toplevel):
    """Cửa sổ biểu đồ thống kê; gọi lam_moi() để vẽ lại khi dữ liệu thay đổi."""

    def __init__(self, master, ql):
        super().__init__(master)
        self.ql = ql
        self.title("Thống kê sinh viên")
        self.geometry("980x580")
        self.minsize(820, 500)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.var_tong_quan = tk.StringVar()
        tk.Label(self, text="Thống kê sinh viên", bg=MAU_NEN, fg=MAU_CHU, font=FONT_TIEU_DE,
                 anchor="w").grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(16, 0))
        tk.Label(self, textvariable=self.var_tong_quan, bg=MAU_NEN, fg=MAU_CHU_PHU, font=FONT_NHO,
                 anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 0))

        self.cv_cot = self._tao_the_bieu_do(0, "Số sinh viên theo lớp", (18, KHOANG))
        self.cv_tron = self._tao_the_bieu_do(1, "Tỷ lệ học lực", (KHOANG, 18))
        self.cv_cot.bind("<Configure>", lambda _e: self.ve_cot())
        self.cv_tron.bind("<Configure>", lambda _e: self.ve_tron())

        khung_nut = tk.Frame(self, bg=MAU_NEN)
        khung_nut.grid(row=3, column=0, columnspan=2, sticky="e", padx=18, pady=14)
        ttk.Button(khung_nut, text="Làm mới", command=self.lam_moi_tu_file).grid(
            row=0, column=0, padx=(0, KHOANG))
        ttk.Button(khung_nut, text="Đóng", style="Chinh.TButton", command=self.destroy).grid(row=0, column=1)

        self.lam_moi()

    # ------------------------------------------------------------------
    def _tao_the_bieu_do(self, cot, tieu_de, padx):
        """Thẻ chứa biểu đồ: tiêu đề nhỏ phía trên, Canvas phía dưới."""
        the = tao_the(self)
        the.grid(row=2, column=cot, sticky="nsew", padx=padx, pady=(12, 0))
        the.columnconfigure(0, weight=1)
        the.rowconfigure(1, weight=1)
        tk.Label(the, text=tieu_de.upper(), bg=MAU_THE, fg=MAU_CHU_PHU, font=FONT_NHAN_NHO,
                 anchor="w").grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        cv = tk.Canvas(the, bg=MAU_THE, highlightthickness=0, width=400, height=320)
        cv.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 12))
        return cv

    def lam_moi(self):
        """Vẽ lại theo dữ liệu hiện có trong bộ nhớ."""
        ds = self.ql.danh_sach()
        s = tong_quan(ds)
        if s["tong"] == 0:
            self.var_tong_quan.set("Chưa có sinh viên nào để thống kê.")
        else:
            cao = s["gpa_cao_nhat"]
            self.var_tong_quan.set(
                f"{s['tong']} sinh viên   •   {s['so_lop']} lớp   •   "
                f"GPA TB {s['gpa_tb']:.2f}   •   ĐRL TB {s['drl_tb']:.1f}   •   "
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

    @staticmethod
    def _cot_bo_goc(cv, x1, y1, x2, y2, mau, r=8):
        """Cột có góc trên bo tròn."""
        r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        if r < 2:
            cv.create_rectangle(x1, y1, x2, y2, fill=mau, outline="")
            return
        diem = [x1, y2, x1, y1 + r, x1 + r, y1, x2 - r, y1, x2, y1 + r, x2, y2]
        cv.create_polygon(diem, fill=mau, outline="", smooth=True)

    @staticmethod
    def _thong_bao_trong(cv, noi_dung):
        w, h = kich_thuoc_canvas(cv)
        cv.create_text(w / 2, h / 2, text=noi_dung, font=FONT, fill=MAU_CHU_PHU)

    def ve_cot(self):
        cv = self.cv_cot
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du_lieu = dem_theo_lop(self.ql.danh_sach())
        if not du_lieu:
            self._thong_bao_trong(cv, "Chưa có dữ liệu lớp")
            return
        le_trai, le_phai, le_tren, le_duoi = 36, 12, 30, 34
        vung_rong = w - le_trai - le_phai
        vung_cao = h - le_tren - le_duoi
        if vung_rong < 40 or vung_cao < 40:
            return
        lon_nhat = max(n for _, n in du_lieu)
        buoc = self._buoc_chia(lon_nhat)
        tran = -(-lon_nhat // buoc) * buoc
        day = h - le_duoi

        for gia_tri in range(0, tran + 1, buoc):  # lưới ngang và nhãn trục tung
            y = day - vung_cao * gia_tri / tran
            if gia_tri:
                cv.create_line(le_trai, y, w - le_phai, y, fill=MAU_VIEN, dash=(2, 4))
            cv.create_text(le_trai - 8, y, text=str(gia_tri), anchor="e", font=FONT_NHO, fill=MAU_CHU_PHU)

        o_rong = vung_rong / len(du_lieu)
        rong_cot = min(48, o_rong * 0.55)
        so_ky_tu = max(3, int(o_rong // 7))
        for i, (lop, n) in enumerate(du_lieu):
            x = le_trai + o_rong * (i + 0.5)
            cao = vung_cao * n / tran
            noi_bat = n == lon_nhat
            if cao > 0:
                self._cot_bo_goc(cv, x - rong_cot / 2, day - cao, x + rong_cot / 2, day,
                                 MAU_CHINH if noi_bat else MAU_CHINH_NHAT)
            cv.create_text(x, day - cao - 11, text=str(n), font=FONT_DAM_NHO,
                           fill=MAU_CHU if noi_bat else MAU_CHU_PHU)
            ten = lop if len(lop) <= so_ky_tu else lop[:so_ky_tu - 1] + "…"
            cv.create_text(x, day + 14, text=ten, font=FONT_NHO, fill=MAU_CHU_PHU)
        cv.create_line(le_trai, day, w - le_phai, day, fill=MAU_VIEN)

    def ve_tron(self):
        cv = self.cv_tron
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du_lieu = dem_theo_hoc_luc(self.ql.danh_sach())
        tong = sum(n for _, n in du_lieu)
        if tong == 0:
            self._thong_bao_trong(cv, "Chưa có dữ liệu học lực")
            return
        duong_kinh = min(h - 24, w * 0.5)
        if duong_kinh < 60:
            return
        r = duong_kinh / 2
        cx, cy = 10 + r, h / 2

        goc = 90.0  # bắt đầu từ 12 giờ, quay theo chiều kim đồng hồ
        for nhan, n in du_lieu:
            if n == 0:
                continue
            phan = n / tong
            quet = -360.0 * phan
            mau = MAU_HOC_LUC[nhan]
            if phan >= 0.9999:  # một mức duy nhất: cung 360 độ không vẽ được
                cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=mau, outline=MAU_THE, width=3)
            else:
                cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=goc, extent=quet,
                              fill=mau, outline=MAU_THE, width=3, style="pieslice")
            goc += quet

        # lỗ giữa tạo hình donut, ghi tổng số ở giữa
        rt = r * 0.58
        cv.create_oval(cx - rt, cy - rt, cx + rt, cy + rt, fill=MAU_THE, outline="")
        cv.create_text(cx, cy - 8, text=str(tong), font=FONT_SO_LON, fill=MAU_CHU)
        cv.create_text(cx, cy + 16, text="sinh viên", font=FONT_NHO, fill=MAU_CHU_PHU)

        # chú thích bên phải: màu + tên mức + số lượng và tỷ lệ
        x_ct = 10 + duong_kinh + 26
        y_bat_dau = cy - len(du_lieu) * 18
        y_ct = y_bat_dau
        for nhan, n in du_lieu:
            cv.create_oval(x_ct, y_ct - 6, x_ct + 12, y_ct + 6, fill=MAU_HOC_LUC[nhan], outline="")
            cv.create_text(x_ct + 20, y_ct, anchor="w", font=FONT_DAM_NHO, fill=MAU_CHU, text=nhan)
            cv.create_text(x_ct + 20, y_ct + 16, anchor="w", font=FONT_NHO, fill=MAU_CHU_PHU,
                           text=f"{n} SV   •   {n / tong * 100:.0f}%")
            y_ct += 40