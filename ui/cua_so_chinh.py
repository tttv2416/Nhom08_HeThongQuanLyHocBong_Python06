"""Module ui/cua_so_chinh.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ chính dùng chung cho toàn hệ thống quản lý học bổng:
- Thanh bên trái: điều hướng giữa các chức năng.
- Vùng nội dung: mỗi chức năng là một trang (Frame) riêng.
- Phần Sinh viên đã hoạt động đầy đủ (SinhVienFrame).
- Các phần khác hiển thị trang "đang triển khai", thay bằng Frame thật khi làm xong.

Chạy: python -m ui.cua_so_chinh
"""

import tkinter as tk
from tkinter import messagebox, ttk

from services.luu_tru_json import LoiFileError
from services.quan_ly_sinh_vien import QuanLySinhVien
from services.thong_ke_sinh_vien import tong_quan
from ui.cua_so_thong_ke import CuaSoThongKe
from ui.sinh_vien_frame import SinhVienFrame
from ui.theme import (FONT, FONT_DAM_NHO, FONT_NHAN_NHO, FONT_NHO, FONT_TIEU_DE, FONT_TIEU_DE_THE,
                      KHOANG, MAU_CANH_BAO, MAU_CHINH, MAU_CHU, MAU_CHU_PHU, MAU_HEADER,
                      MAU_HEADER_PHU, MAU_NEN, MAU_THE, tao_the)

RONG_THANH_BEN = 220
MAU_MENU_CHU = "#CBD5E1"

# (khóa trang, nhãn trên thanh bên)
DANH_MUC = (
    ("tong_quan", "Tổng quan"),
    ("sinh_vien", "Sinh viên"),
    ("ho_so", "Hồ sơ học bổng"),
    ("hoc_bong", "Học bổng"),
    ("phan_quyen", "Phân quyền"),
    ("bao_cao", "Báo cáo"),
)

# Mô tả cho các trang chưa triển khai
MO_TA_CHO = {
    "ho_so": "Quản lý hồ sơ đăng ký học bổng của sinh viên.",
    "hoc_bong": "Quản lý danh sách học bổng và điều kiện xét duyệt.",
    "phan_quyen": "Tài khoản đăng nhập và quyền truy cập theo vai trò.",
    "bao_cao": "Tổng hợp và xuất báo cáo cho toàn hệ thống.",
}


class CuaSoChinh(tk.Tk):
    """Cửa sổ chính của hệ thống. Các trang được tạo sẵn và chuyển qua lại bằng tkraise()."""

    def __init__(self, ql=None, duoc_chinh_sua=True):
        """
        ql               : đối tượng QuanLySinhVien dùng chung cho các trang (mặc định đọc file dữ liệu).
        duoc_chinh_sua   : quyền thêm/sửa/xóa của người dùng hiện tại (sẽ nối với phân quyền sau).
        """
        super().__init__()
        self.title("Hệ thống quản lý học bổng")
        self.geometry("1040x760")
        self.minsize(960, 640)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.ql = QuanLySinhVien() if ql is None else ql
        self.duoc_chinh_sua = duoc_chinh_sua
        self._trang = {}
        self._nut_menu = {}
        self._cs_thong_ke = None
        self._khoa_hien_tai = None

        self._tao_thanh_ben()
        self._tao_vung_noi_dung()
        self._tao_cac_trang()
        self.chon_trang("tong_quan")

        self.bind("<F5>", lambda _e: self._tai_lai())
        self.bind("<Control-f>", lambda _e: self.chon_trang("sinh_vien") or self.sv.o_tu_khoa.focus_set())

        try:
            self.state("zoomed")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Thanh bên
    # ------------------------------------------------------------------
    def _tao_thanh_ben(self):
        thanh = tk.Frame(self, bg=MAU_HEADER, width=RONG_THANH_BEN)
        thanh.grid(row=0, column=0, sticky="ns")
        thanh.grid_propagate(False)
        thanh.columnconfigure(0, weight=1)

        tk.Label(thanh, text="QUẢN LÝ HỌC BỔNG", bg=MAU_HEADER, fg="#F8FAFC", font=FONT_TIEU_DE_THE,
                 anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(22, 2))
        tk.Label(thanh, text="Nhóm 08", bg=MAU_HEADER, fg=MAU_HEADER_PHU, font=FONT_NHO,
                 anchor="w").grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        for i, (khoa, nhan) in enumerate(DANH_MUC, start=2):
            nut = tk.Button(
                thanh, text=nhan, anchor="w", font=FONT, bd=0, relief="flat", cursor="hand2",
                padx=20, pady=10, bg=MAU_HEADER, fg=MAU_MENU_CHU,
                activebackground="#1E293B", activeforeground="white",
                command=lambda k=khoa: self.chon_trang(k))
            nut.grid(row=i, column=0, sticky="ew")
            self._nut_menu[khoa] = nut

        hang_cuoi = len(DANH_MUC) + 2
        thanh.rowconfigure(hang_cuoi, weight=1)
        vai_tro = "Quản trị viên" if self.duoc_chinh_sua else "Chỉ xem"
        tk.Label(thanh, text=f"Quyền: {vai_tro}", bg=MAU_HEADER, fg=MAU_HEADER_PHU, font=FONT_NHO,
                 anchor="w").grid(row=hang_cuoi, column=0, sticky="sw", padx=20, pady=18)

    # ------------------------------------------------------------------
    # Vùng nội dung và các trang
    # ------------------------------------------------------------------
    def _tao_vung_noi_dung(self):
        self.vung = tk.Frame(self, bg=MAU_NEN)
        self.vung.grid(row=0, column=1, sticky="nsew", padx=KHOANG * 3, pady=KHOANG * 3)
        self.vung.columnconfigure(0, weight=1)
        self.vung.rowconfigure(0, weight=1)
        for khoa, _ in DANH_MUC:
            khung = tk.Frame(self.vung, bg=MAU_NEN)
            khung.grid(row=0, column=0, sticky="nsew")
            khung.columnconfigure(0, weight=1)
            khung.rowconfigure(0, weight=1)
            self._trang[khoa] = khung

    def _tao_cac_trang(self):
        self._xay_tong_quan(self._trang["tong_quan"])

        self.sv = SinhVienFrame(self._trang["sinh_vien"], self.ql, duoc_chinh_sua=self.duoc_chinh_sua)
        self.sv.grid(row=0, column=0, sticky="nsew")

        for khoa, _ in DANH_MUC:
            if khoa not in ("tong_quan", "sinh_vien"):
                self._xay_trang_cho(self._trang[khoa], khoa)

    def chon_trang(self, khoa):
        """Hiện trang có khóa tương ứng và đổi màu nút trên thanh bên."""
        self._trang[khoa].tkraise()
        self._khoa_hien_tai = khoa
        for k, nut in self._nut_menu.items():
            dang_chon = k == khoa
            nut.configure(bg=MAU_CHINH if dang_chon else MAU_HEADER,
                          fg="white" if dang_chon else MAU_MENU_CHU)
        if khoa == "tong_quan":
            self._lam_moi_tong_quan()

    def _tai_lai(self):
        if self._khoa_hien_tai == "sinh_vien":
            self.sv.lam_moi_du_lieu()
        elif self._khoa_hien_tai == "tong_quan":
            self.ql.tai_du_lieu()
            self._lam_moi_tong_quan()

    # ----- Trang Tổng quan -----
    def _xay_tong_quan(self, khung):
        the = tao_the(khung)
        the.grid(row=0, column=0, sticky="nsew")
        the.columnconfigure(0, weight=1)
        noi = tk.Frame(the, bg=MAU_THE)
        noi.grid(row=0, column=0, sticky="nsew", padx=32, pady=28)
        noi.columnconfigure(0, weight=1)

        tk.Label(noi, text="Chào mừng bạn", bg=MAU_THE, fg=MAU_CHU, font=FONT_TIEU_DE,
                 anchor="w").grid(row=0, column=0, sticky="ew")
        self.var_tong_quan = tk.StringVar()
        tk.Label(noi, textvariable=self.var_tong_quan, bg=MAU_THE, fg=MAU_CHINH, font=FONT_DAM_NHO,
                 anchor="w", justify="left", wraplength=640).grid(row=1, column=0, sticky="ew", pady=(8, 4))
        tk.Label(noi, text="Chọn một chức năng ở thanh bên trái. Phần Sinh viên đã sẵn sàng sử dụng; "
                           "các phần còn lại đang được triển khai.",
                 bg=MAU_THE, fg=MAU_CHU_PHU, font=FONT, anchor="w", justify="left",
                 wraplength=640).grid(row=2, column=0, sticky="ew", pady=(0, 20))

        hang_nut = tk.Frame(noi, bg=MAU_THE)
        hang_nut.grid(row=3, column=0, sticky="w")
        ttk.Button(hang_nut, text="Mở quản lý sinh viên", style="Chinh.TButton",
                   command=lambda: self.chon_trang("sinh_vien")).grid(row=0, column=0, padx=(0, KHOANG))
        ttk.Button(hang_nut, text="Xem thống kê", command=self.mo_thong_ke).grid(row=0, column=1)

    def _lam_moi_tong_quan(self):
        ds = self.ql.danh_sach()
        if not ds:
            self.var_tong_quan.set("Chưa có sinh viên nào. Vào mục Sinh viên để thêm hoặc nhập từ file.")
            return
        s = tong_quan(ds)
        self.var_tong_quan.set(f"Hiện có {s['tong']} sinh viên thuộc {s['so_lop']} lớp.   "
                               f"GPA trung bình: {s['gpa_tb']:.2f}")

    def mo_thong_ke(self):
        if self._cs_thong_ke is not None and self._cs_thong_ke.winfo_exists():
            self._cs_thong_ke.lam_moi()
            self._cs_thong_ke.lift()
            return
        self._cs_thong_ke = CuaSoThongKe(self, self.ql)

    # ----- Trang chưa triển khai -----
    def _xay_trang_cho(self, khung, khoa):
        nhan = dict(DANH_MUC)[khoa]
        the = tao_the(khung)
        the.grid(row=0, column=0, sticky="nsew")
        the.columnconfigure(0, weight=1)
        the.rowconfigure(0, weight=1)

        noi = tk.Frame(the, bg=MAU_THE)
        noi.grid(row=0, column=0)  # để trống hai bên nên nội dung nằm giữa thẻ
        tk.Label(noi, text=nhan, bg=MAU_THE, fg=MAU_CHU, font=FONT_TIEU_DE).grid(
            row=0, column=0, pady=(0, 8))
        tk.Label(noi, text=MO_TA_CHO.get(khoa, ""), bg=MAU_THE, fg=MAU_CHU_PHU, font=FONT,
                 wraplength=420, justify="center").grid(row=1, column=0, pady=(0, 16))
        tk.Label(noi, text="  CHƯA TRIỂN KHAI  ", bg="#FEF3C7", fg="#92400E",
                 font=FONT_NHAN_NHO).grid(row=2, column=0)

    # ------------------------------------------------------------------
    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("Đã xảy ra lỗi", f"{val}\n\nỨng dụng vẫn tiếp tục chạy.", parent=self)


def main():
    try:
        ql = QuanLySinhVien()
    except LoiFileError as e:
        goc = tk.Tk()
        goc.withdraw()
        messagebox.showerror("Không đọc được dữ liệu",
                             f"{e}\n\nỨng dụng sẽ đóng để tránh ghi đè dữ liệu.")
        goc.destroy()
        return
    CuaSoChinh(ql).mainloop()


if __name__ == "__main__":
    main()