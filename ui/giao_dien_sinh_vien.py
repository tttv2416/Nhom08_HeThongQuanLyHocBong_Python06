"""Module ui/giao_dien_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Cửa sổ độc lập cho phần quản lý sinh viên: python -m ui.giao_dien_sinh_vien
Logic giao diện nằm trong ui/sinh_vien_frame.py.
"""

import tkinter as tk
from tkinter import messagebox

from services.luu_tru_json import LoiFileError
from services.quan_ly_sinh_vien import QuanLySinhVien
from ui.sinh_vien_frame import SinhVienFrame  # re-export để import cũ vẫn chạy
from ui.theme import FONT_NHO, FONT_TIEU_DE, MAU_CHINH, MAU_HEADER, MAU_HEADER_PHU, MAU_NEN

__all__ = ["SinhVienFrame", "UngDungSinhVien", "main"]


class UngDungSinhVien(tk.Tk):
    """Cửa sổ chính chạy riêng phần sinh viên (có header và Menu)."""

    def __init__(self, ql=None, kiem_tra_rang_buoc=None, duoc_chinh_sua=True):
        super().__init__()
        self.title("Quản lý sinh viên")
        self.geometry("1040x760")
        self.minsize(900, 640)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._tao_header()
        self.khung = SinhVienFrame(self, ql, kiem_tra_rang_buoc, duoc_chinh_sua)
        self.khung.grid(row=1, column=0, sticky="nsew")

        self._tao_menu()
        self.bind("<F5>", lambda _e: self.khung.lam_moi_du_lieu())
        self.bind("<Control-f>", lambda _e: self.khung.o_tu_khoa.focus_set())

        try:
            self.state("zoomed")  # Windows: phóng to đúng vùng làm việc của màn hình
        except tk.TclError:
            pass

    def _tao_header(self):
        header = tk.Frame(self, bg=MAU_HEADER)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        tk.Label(header, text="Quản lý sinh viên", bg=MAU_HEADER, fg="#F8FAFC",
                 font=FONT_TIEU_DE, anchor="w").grid(row=0, column=0, sticky="w", padx=24, pady=(12, 0))
        tk.Label(header, text="Hệ thống quản lý học bổng   •   Nhóm 08", bg=MAU_HEADER,
                 fg=MAU_HEADER_PHU, font=FONT_NHO, anchor="w").grid(
            row=1, column=0, sticky="w", padx=24, pady=(0, 10))
        tk.Frame(header, bg=MAU_CHINH, height=3).grid(row=2, column=0, sticky="ew")

    def _tao_menu(self):
        thanh = tk.Menu(self)
        m_tep = tk.Menu(thanh, tearoff=False)
        m_tep.add_command(label="Nhập sinh viên từ file CSV/JSON...", command=self.khung.nhap_tu_file)
        m_tep.add_command(label="Xuất danh sách ra file CSV/JSON...", command=self.khung.xuat_ra_file)
        m_tep.add_command(label="Xem nhật ký thao tác...", command=self.khung.mo_nhat_ky)
        m_tep.add_separator()
        m_tep.add_command(label="Tải lại dữ liệu từ file", accelerator="F5",
                          command=self.khung.lam_moi_du_lieu)
        m_tep.add_separator()
        m_tep.add_command(label="Thoát", command=self.destroy)
        thanh.add_cascade(label="Tệp", menu=m_tep)

        m_cn = tk.Menu(thanh, tearoff=False)
        m_cn.add_command(label="Thêm sinh viên mới", command=self.khung.lam_moi_form)
        m_cn.add_command(label="Tìm kiếm", accelerator="Ctrl+F",
                         command=self.khung.o_tu_khoa.focus_set)
        m_cn.add_command(label="Hiện tất cả", command=self.khung.hien_tat_ca)
        m_cn.add_command(label="Thống kê (biểu đồ)", command=self.khung.mo_thong_ke)
        thanh.add_cascade(label="Chức năng", menu=m_cn)

        m_gd = tk.Menu(thanh, tearoff=False)
        m_gd.add_command(label="Giới thiệu", command=lambda: messagebox.showinfo(
            "Giới thiệu",
            "Hệ thống quản lý học bổng - Nhóm 08\nPhần: Quản lý sinh viên\n"
            "Thực hiện: Nguyễn Thị Đông Phương - 2044240275", parent=self))
        thanh.add_cascade(label="Trợ giúp", menu=m_gd)
        self.configure(menu=thanh)

    def report_callback_exception(self, exc, val, tb):
        """Lỗi bất ngờ trong sự kiện: báo cho người dùng thay vì dừng đột ngột."""
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
    UngDungSinhVien(ql).mainloop()


if __name__ == "__main__":
    main()