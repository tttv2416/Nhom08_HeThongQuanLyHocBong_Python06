"""Module ui/cua_so_thong_ke.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ thống kê sinh viên, vẽ bằng Canvas với hiệu ứng chuyển động:
- Biểu đồ sóng: số sinh viên theo lớp, đường cong mượt, gợn sóng nhẹ liên tục.
- Biểu đồ donut: tỷ lệ học lực, quét dần khi mở và đếm tổng từ 0.
"""

import math
import time
import tkinter as tk
from tkinter import messagebox, ttk

from services.luu_tru_json import LoiFileError
from services.thong_ke_sinh_vien import dem_theo_hoc_luc, dem_theo_lop, tong_quan
from ui.theme import (FONT, FONT_DAM_NHO, FONT_NHAN_NHO, FONT_NHO, FONT_SO_LON, FONT_TIEU_DE,
                      FONT_TIEU_DE_THE, KHOANG, MAU_CHINH, MAU_CHINH_NHAT, MAU_CHU, MAU_CHU_PHU,
                      MAU_HOC_LUC, MAU_NEN, MAU_THE, MAU_VIEN, kich_thuoc_canvas, tao_the)

# ---- Cấu hình hiệu ứng ----
THOI_GIAN_DUNG_DAU = 0.9      # giây, thời gian sóng dâng / donut quét khi vẽ lại
DO_TRE_KHUNG_MS = 33          # ~30 khung hình mỗi giây
HIEU_UNG_LIEN_TUC = True      # False: sóng ngừng gợn, chỉ chạy hiệu ứng mở đầu
MAU_VUNG_SONG = "#E0E7FF"


def _ease_out_cubic(t):
    """Đường cong giảm tốc: bắt đầu nhanh, kết thúc êm."""
    return 1 - (1 - t) ** 3


def _catmull(diem, so_buoc=14):
    """Nội suy đường cong mượt đi qua tất cả các điểm (Catmull-Rom)."""
    if len(diem) < 3:
        return list(diem)
    ket_qua = []
    n = len(diem)
    for i in range(n - 1):
        p0 = diem[i - 1] if i > 0 else diem[i]
        p1 = diem[i]
        p2 = diem[i + 1]
        p3 = diem[i + 2] if i + 2 < n else diem[i + 1]
        for s in range(so_buoc):
            t = s / so_buoc
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            ket_qua.append((x, y))
    ket_qua.append(diem[-1])
    return ket_qua


def _phang(diem):
    return [toa for p in diem for toa in p]


class CuaSoThongKe(tk.Toplevel):
    """Cửa sổ biểu đồ thống kê; gọi lam_moi() để vẽ lại khi dữ liệu thay đổi."""

    def __init__(self, master, ql):
        super().__init__(master)
        self.ql = ql
        self.title("Thống kê sinh viên")
        self.geometry("1040x600")
        self.minsize(860, 520)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self._du_cot = []
        self._du_tron = []
        self._t0 = time.perf_counter()
        self._pha = 0.0
        self._id_hen = None

        self.var_tong_quan = tk.StringVar()
        tk.Label(self, text="Thống kê sinh viên", bg=MAU_NEN, fg=MAU_CHU, font=FONT_TIEU_DE,
                 anchor="w").grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(16, 0))
        tk.Label(self, textvariable=self.var_tong_quan, bg=MAU_NEN, fg=MAU_CHU_PHU, font=FONT_NHO,
                 anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 0))

        self.cv_cot = self._tao_the_bieu_do(0, "Số sinh viên theo lớp", (18, KHOANG))
        self.cv_tron = self._tao_the_bieu_do(1, "Tỷ lệ học lực", (KHOANG, 18))

        khung_nut = tk.Frame(self, bg=MAU_NEN)
        khung_nut.grid(row=3, column=0, columnspan=2, sticky="e", padx=18, pady=14)
        ttk.Button(khung_nut, text="Làm mới", command=self.lam_moi_tu_file).grid(
            row=0, column=0, padx=(0, KHOANG))
        ttk.Button(khung_nut, text="Đóng", style="Chinh.TButton", command=self._dong).grid(row=0, column=1)
        self.protocol("WM_DELETE_WINDOW", self._dong)

        self.lam_moi()
        self._vong_hoat_anh()

    # ------------------------------------------------------------------
    def _tao_the_bieu_do(self, cot, tieu_de, padx):
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
        """Cập nhật dữ liệu và chạy lại hiệu ứng mở đầu."""
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
        self._du_cot = dem_theo_lop(ds)
        self._du_tron = [(nhan, n) for nhan, n in dem_theo_hoc_luc(ds) if n > 0]
        self._t0 = time.perf_counter()  # chạy lại hiệu ứng mở đầu

    def lam_moi_tu_file(self):
        try:
            self.ql.tai_du_lieu()
        except LoiFileError as e:
            messagebox.showerror("Không đọc được dữ liệu", str(e), parent=self)
            return
        self.lam_moi()

    def _dong(self):
        if self._id_hen is not None:
            self.after_cancel(self._id_hen)
            self._id_hen = None
        self.destroy()

    # ------------------------------------------------------------------
    # Vòng lặp hoạt ảnh
    # ------------------------------------------------------------------
    def _vong_hoat_anh(self):
        self._id_hen = None
        if not self.winfo_exists():
            return
        tien_do = min(1.0, (time.perf_counter() - self._t0) / THOI_GIAN_DUNG_DAU)
        e = _ease_out_cubic(tien_do)
        if HIEU_UNG_LIEN_TUC:
            self._pha += 0.08
        else:
            self._pha += 0.08 * (1 - tien_do)  # dừng gợn khi hiệu ứng mở đầu xong
        self.ve_cot(e)
        self.ve_tron(e)
        if HIEU_UNG_LIEN_TUC or tien_do < 1.0:
            self._id_hen = self.after(DO_TRE_KHUNG_MS, self._vong_hoat_anh)

    # ------------------------------------------------------------------
    @staticmethod
    def _thong_bao_trong(cv, noi_dung):
        w, h = kich_thuoc_canvas(cv)
        cv.create_text(w / 2, h / 2, text=noi_dung, font=FONT, fill=MAU_CHU_PHU)

    def ve_cot(self, e=1.0):
        """Biểu đồ sóng. e: tiến độ hiệu ứng từ 0 đến 1."""
        cv = self.cv_cot
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du = self._du_cot
        if not du:
            self._thong_bao_trong(cv, "Chưa có dữ liệu lớp")
            return
        le, ri, tren, duoi = 44, 24, 34, 44
        vung_rong = w - le - ri
        y0 = h - duoi
        yt = tren
        if vung_rong < 80 or y0 - yt < 60:
            return

        lon = max(n for _, n in du)
        tran = max(4, math.ceil(lon * 1.25))

        # lưới ngang
        for k in range(5):
            y = y0 - (y0 - yt) * k / 4
            if k:
                cv.create_line(le, y, w - ri, y, fill=MAU_VIEN, dash=(2, 4))
            cv.create_text(le - 10, y, text=str(round(tran * k / 4)), anchor="e",
                           font=FONT_NHO, fill=MAU_CHU_PHU)

        n = len(du)
        cot_mac_dinh = 0
        pts = []
        for i, (_lop, so) in enumerate(du):
            x = le + 16 + (vung_rong - 32) * i / (n - 1) if n > 1 else le + vung_rong / 2
            y = y0 - (y0 - yt) * e * so / tran
            gon = 3.0 * math.sin(self._pha + i * 0.9) * e  # gợn sóng
            pts.append((x, y + gon))
            if so == lon:
                cot_mac_dinh = i

        duong = _catmull(pts, 14)
        # vùng tô bên dưới đường sóng
        cv.create_polygon(_phang(duong) + [pts[-1][0], y0, pts[0][0], y0],
                          fill=MAU_VUNG_SONG, outline="", smooth=False)
        # đường sóng
        cv.create_line(_phang(duong), fill=MAU_CHINH, width=3, capstyle="round",
                       joinstyle="round")

        # chấm và nhãn
        so_ky_tu = max(4, int((vung_rong / max(n, 1)) // 7))
        for i, (x, y) in enumerate(pts):
            noi_bat = i == cot_mac_dinh
            r = 6 if noi_bat else 4.5
            cv.create_oval(x - r, y - r, x + r, y + r,
                           fill=MAU_CHINH if noi_bat else MAU_THE,
                           outline=MAU_CHINH, width=2)
            cv.create_text(x, y - 16, text=str(du[i][1]), font=FONT_DAM_NHO,
                           fill=MAU_CHU if noi_bat else MAU_CHU_PHU)
            ten = du[i][0]
            if len(ten) > so_ky_tu:
                ten = ten[:so_ky_tu - 1] + "…"
            cv.create_text(x, y0 + 18, text=ten, font=FONT_NHO, fill=MAU_CHU_PHU)
        cv.create_line(le, y0, w - ri, y0, fill=MAU_VIEN)

    def ve_tron(self, e=1.0):
        """Donut quét dần theo e. Tổng ở giữa đếm từ 0 lên."""
        cv = self.cv_tron
        cv.delete("all")
        w, h = kich_thuoc_canvas(cv)
        du = self._du_tron
        tong = sum(n for _, n in du)
        if tong == 0:
            self._thong_bao_trong(cv, "Chưa có dữ liệu học lực")
            return
        duong_kinh = min(h - 24, w * 0.5)
        if duong_kinh < 60:
            return
        r = duong_kinh / 2
        cx, cy = 10 + r, h / 2

        cung_hien = 360.0 * e          # số độ đã quét
        da_quet = 0.0                  # số độ của các lát trước đó
        goc_bat_dau = 90.0
        for nhan, n in du:
            phan = n / tong
            do_lat = 360.0 * phan
            vis = max(0.0, min(do_lat, cung_hien - da_quet))
            mau = MAU_HOC_LUC[nhan]
            if vis >= 359.9:
                cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=mau, outline=MAU_THE, width=3)
            elif vis > 0.5:
                cv.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=goc_bat_dau - da_quet, extent=-vis,
                              fill=mau, outline=MAU_THE, width=3, style="pieslice")
            da_quet += do_lat

        rt = r * 0.62
        cv.create_oval(cx - rt, cy - rt, cx + rt, cy + rt, fill=MAU_THE, outline="")
        cv.create_text(cx, cy - 8, text=str(round(tong * e)), font=FONT_SO_LON, fill=MAU_CHU)
        cv.create_text(cx, cy + 16, text="sinh viên", font=FONT_NHO, fill=MAU_CHU_PHU)

        # chú thích, hiện dần theo tiến độ
        if e < 0.2:
            return
        x_ct = 10 + duong_kinh + 26
        y_ct = cy - len(du) * 18
        for nhan, n in du:
            cv.create_oval(x_ct, y_ct - 6, x_ct + 12, y_ct + 6, fill=MAU_HOC_LUC[nhan], outline="")
            cv.create_text(x_ct + 20, y_ct, anchor="w", font=FONT_DAM_NHO, fill=MAU_CHU, text=nhan)
            cv.create_text(x_ct + 20, y_ct + 16, anchor="w", font=FONT_NHO, fill=MAU_CHU_PHU,
                           text=f"{n} SV   •   {n / tong * 100:.0f}%")
            y_ct += 40


def _cua_so_test():
    """Chạy thử riêng: python -m ui.cua_so_thong_ke"""
    from services.quan_ly_sinh_vien import QuanLySinhVien
    goc = tk.Tk()
    goc.withdraw()
    ql = QuanLySinhVien(nhat_ky=False)
    CuaSoThongKe(goc, ql)
    goc.mainloop()


if __name__ == "__main__":
    _cua_so_test()