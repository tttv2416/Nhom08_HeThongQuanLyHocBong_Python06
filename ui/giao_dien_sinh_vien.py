"""Module ui/giao_dien_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Giao diện Tkinter quản lý sinh viên:
- SinhVienFrame   : khung chức năng (form, Treeview, tìm kiếm, Progressbar) có thể nhúng
                    vào cửa sổ chính của cả nhóm (Notebook/Frame).
- UngDungSinhVien : cửa sổ độc lập có Menu, dùng để chạy riêng:  python -m ui.giao_dien_sinh_vien

Quy ước layout: mỗi vùng chứa chỉ dùng một Layout Manager (ở đây là grid()).
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models.sinh_vien import (
    DuLieuKhongHopLeError,
    kiem_tra_diem_ren_luyen,
    kiem_tra_gpa,
    kiem_tra_ho_ten,
    kiem_tra_lop,
    kiem_tra_ma_sv,
)
from services.luu_tru_json import LoiFileError
from services.nhap_xuat_sinh_vien import doc_file, xuat_file
from services.quan_ly_sinh_vien import QuanLySinhVien
from services.rang_buoc_ho_so import sinh_vien_co_ho_so
from ui.cua_so_nhat_ky import CuaSoNhatKy
from ui.cua_so_thong_ke import CuaSoThongKe
from ui.score_meter import ScoreMeter
from ui.theme import (FONT, FONT_DAM, FONT_TIEU_DE, KHOANG, MAU_CHINH, MAU_DONG_LE, MAU_NEN,
                      MAU_NGUY_HIEM)

# (mã cột, tiêu đề, độ rộng, căn lề)
CAC_COT = (
    ("ma_sv", "Mã SV", 110, "center"),
    ("ho_ten", "Họ và tên", 230, "w"),
    ("lop", "Lớp", 90, "center"),
    ("gpa", "GPA", 70, "center"),
    ("diem_ren_luyen", "Điểm RL", 80, "center"),
    ("hoc_luc", "Học lực", 100, "center"),
    ("ren_luyen", "Xếp loại RL", 110, "center"),
)
# cột hiển thị -> trường dùng để sắp xếp
TRUONG_SAP_XEP = {
    "ma_sv": "ma_sv", "ho_ten": "ho_ten", "lop": "lop", "gpa": "gpa",
    "diem_ren_luyen": "diem_ren_luyen", "hoc_luc": "gpa", "ren_luyen": "diem_ren_luyen",
}
TIEU_CHI_TIM = {"Tất cả": "tat_ca", "Mã SV": "ma_sv", "Họ tên": "ho_ten", "Lớp": "lop"}
TAT_CA_LOP = "Tất cả lớp"


class SinhVienFrame(ttk.Frame):
    """Khung quản lý sinh viên: thêm, xem, sửa, xóa, tìm kiếm, lọc, sắp xếp."""

    def __init__(self, master, ql=None, kiem_tra_rang_buoc=None, duoc_chinh_sua=True):
        """
        ql                 : đối tượng QuanLySinhVien (mặc định đọc data/sinh_vien.json).
        kiem_tra_rang_buoc : hàm(ma_sv) -> True nếu sinh viên còn hồ sơ học bổng (không cho xóa).
        duoc_chinh_sua     : False với người dùng thường (chỉ xem/tìm), True với quản trị viên.
        """
        super().__init__(master, padding=10)
        self.ql = ql if ql is not None else QuanLySinhVien()
        self.kiem_tra_rang_buoc = kiem_tra_rang_buoc or sinh_vien_co_ho_so
        self.duoc_chinh_sua = duoc_chinh_sua
        self._sap_xep = ("ma_sv", False)  # (trường, giảm dần?)
        self._cot_sap_xep = "ma_sv"       # cột đang được sắp xếp (để vẽ mũi tên)
        self._ma_dang_chon = None
        self._dang_do_bang = False
        self._cs_thong_ke = None   # cửa sổ thống kê (nếu đang mở)
        self._cs_nhat_ky = None    # cửa sổ nhật ký (nếu đang mở)
        self._tao_style()
        self._tao_giao_dien()
        self.lam_moi_du_lieu(bao_loi=False)

    # ------------------------------------------------------------------
    # Dựng giao diện
    # ------------------------------------------------------------------
    def _tao_style(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=FONT)
        style.configure("TFrame", background=MAU_NEN)
        style.configure("TLabel", background=MAU_NEN)
        style.configure("TLabelframe", background=MAU_NEN)
        style.configure("TLabelframe.Label", background=MAU_NEN, font=FONT_DAM, foreground=MAU_CHINH)
        style.configure("TCheckbutton", background=MAU_NEN)
        style.configure("TButton", padding=(10, 4))
        style.configure("Chinh.TButton", background=MAU_CHINH, foreground="white", font=FONT_DAM)
        style.map("Chinh.TButton", background=[("active", "#2a63ad"), ("disabled", "#9fb3cf")])
        style.configure("Xoa.TButton", background=MAU_NGUY_HIEM, foreground="white", font=FONT_DAM)
        style.map("Xoa.TButton", background=[("active", "#d03a31"), ("disabled", "#d9a5a1")])
        style.configure("Treeview", font=FONT, rowheight=26)
        style.configure("Treeview.Heading", font=FONT_DAM, background="#dbe6f5")
        style.configure("TProgressbar", thickness=14, background=MAU_CHINH, troughcolor="#d6dce6")

    def _tao_giao_dien(self):
        self.configure(style="TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # hàng chứa bảng giãn theo cửa sổ

        # ===== Hàng 0: form nhập + chi tiết =====
        khung_tren = ttk.Frame(self)
        khung_tren.grid(row=0, column=0, sticky="ew")
        khung_tren.columnconfigure(0, weight=3)
        khung_tren.columnconfigure(1, weight=2)

        # --- form ---
        khung_form = ttk.LabelFrame(khung_tren, text="Thông tin sinh viên", padding=KHOANG + 2)
        khung_form.grid(row=0, column=0, sticky="nsew", padx=(0, KHOANG))
        khung_form.columnconfigure(1, weight=1)
        khung_form.columnconfigure(3, weight=1)

        self.bien = {k: tk.StringVar() for k in ("ma_sv", "ho_ten", "lop", "gpa", "drl")}
        self.o_nhap = {}
        # (khóa, nhãn, hàng, cột nhãn, số cột ô nhập chiếm)
        cac_truong = (
            ("ma_sv", "Mã sinh viên (*)", 0, 0, 1),
            ("lop", "Lớp (*)", 0, 2, 1),
            ("ho_ten", "Họ và tên (*)", 1, 0, 3),
            ("gpa", "GPA (0 - 4.0) (*)", 2, 0, 1),
            ("drl", "Điểm rèn luyện (0 - 100) (*)", 2, 2, 1),
        )
        for khoa, nhan, hang, cot, gop in cac_truong:
            ttk.Label(khung_form, text=nhan).grid(row=hang, column=cot, sticky="w",
                                                  padx=(0, KHOANG), pady=KHOANG // 2)
            if khoa == "lop":
                o = ttk.Combobox(khung_form, textvariable=self.bien[khoa], width=18)
            else:
                o = ttk.Entry(khung_form, textvariable=self.bien[khoa], width=22)
            o.grid(row=hang, column=cot + 1, columnspan=gop, sticky="ew",
                   padx=(0, KHOANG * 2), pady=KHOANG // 2)
            self.o_nhap[khoa] = o

        khung_nut = ttk.Frame(khung_form)
        khung_nut.grid(row=3, column=0, columnspan=4, sticky="w", pady=(KHOANG + 2, 0))
        self.nut_them = ttk.Button(khung_nut, text="Thêm mới", style="Chinh.TButton", command=self.them)
        self.nut_sua = ttk.Button(khung_nut, text="Cập nhật", style="Chinh.TButton", command=self.cap_nhat)
        self.nut_xoa = ttk.Button(khung_nut, text="Xóa", style="Xoa.TButton", command=self.xoa)
        self.nut_moi = ttk.Button(khung_nut, text="Làm mới form", command=self.lam_moi_form)
        self.nut_nhap = ttk.Button(khung_nut, text="Nhập từ file...", command=self.nhap_tu_file)
        self.nut_xuat = ttk.Button(khung_nut, text="Xuất ra file...", command=self.xuat_ra_file)
        self.nut_thong_ke = ttk.Button(khung_nut, text="Thống kê (biểu đồ)", command=self.mo_thong_ke)
        self.nut_nhat_ky = ttk.Button(khung_nut, text="Nhật ký thao tác", command=self.mo_nhat_ky)
        for i, nut in enumerate((self.nut_them, self.nut_sua, self.nut_xoa, self.nut_moi)):
            nut.grid(row=0, column=i, padx=(0, KHOANG))
        self.nut_nhap.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, KHOANG), pady=(KHOANG, 0))
        self.nut_xuat.grid(row=1, column=2, columnspan=2, sticky="ew", padx=(0, KHOANG), pady=(KHOANG, 0))
        self.nut_thong_ke.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(0, KHOANG), pady=(KHOANG, 0))
        self.nut_nhat_ky.grid(row=2, column=2, columnspan=2, sticky="ew", padx=(0, KHOANG), pady=(KHOANG, 0))

        # --- chi tiết với Progressbar (thang đo GPA và điểm rèn luyện) ---
        khung_ct = ttk.LabelFrame(khung_tren, text="Chi tiết sinh viên đang chọn", padding=KHOANG + 2)
        khung_ct.grid(row=0, column=1, sticky="nsew")
        khung_ct.columnconfigure(0, weight=1)
        self.var_ct_ten = tk.StringVar()
        self.var_ct_gpa = tk.StringVar()
        self.var_ct_drl = tk.StringVar()
        ttk.Label(khung_ct, textvariable=self.var_ct_ten, font=FONT_DAM).grid(row=0, column=0, sticky="w")
        ttk.Label(khung_ct, text="GPA").grid(row=1, column=0, sticky="w", pady=(KHOANG, 0))
        self.meter_gpa = ScoreMeter(khung_ct, toi_da=4.0, nen=MAU_NEN)
        self.meter_gpa.grid(row=2, column=0, sticky="ew")
        ttk.Label(khung_ct, textvariable=self.var_ct_gpa).grid(row=3, column=0, sticky="w")
        ttk.Label(khung_ct, text="Điểm rèn luyện").grid(row=4, column=0, sticky="w", pady=(KHOANG, 0))
        self.meter_drl = ScoreMeter(khung_ct, toi_da=100.0, nen=MAU_NEN)
        self.meter_drl.grid(row=5, column=0, sticky="ew")
        ttk.Label(khung_ct, textvariable=self.var_ct_drl).grid(row=6, column=0, sticky="w")

        # ===== Hàng 1: tìm kiếm / lọc =====
        khung_tim = ttk.LabelFrame(self, text="Tìm kiếm và lọc", padding=KHOANG + 2)
        khung_tim.grid(row=1, column=0, sticky="ew", pady=KHOANG + 2)
        khung_tim.columnconfigure(3, weight=1)

        self.var_tieu_chi = tk.StringVar(value="Tất cả")
        self.var_tu_khoa = tk.StringVar()
        self.var_gan_dung = tk.BooleanVar(value=False)
        self.var_loc_lop = tk.StringVar(value=TAT_CA_LOP)

        ttk.Label(khung_tim, text="Tìm theo").grid(row=0, column=0, padx=(0, KHOANG))
        ttk.Combobox(khung_tim, textvariable=self.var_tieu_chi, values=list(TIEU_CHI_TIM),
                     state="readonly", width=9).grid(row=0, column=1, padx=(0, KHOANG))
        ttk.Label(khung_tim, text="Từ khóa").grid(row=0, column=2, padx=(0, KHOANG))
        self.o_tu_khoa = ttk.Entry(khung_tim, textvariable=self.var_tu_khoa)
        self.o_tu_khoa.grid(row=0, column=3, sticky="ew", padx=(0, KHOANG))
        self.o_tu_khoa.bind("<Return>", lambda _e: self.tim_kiem())
        ttk.Checkbutton(khung_tim, text="Gần đúng", variable=self.var_gan_dung).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(KHOANG, 0))
        ttk.Label(khung_tim, text="Lớp").grid(row=1, column=2, padx=(0, KHOANG), pady=(KHOANG, 0))
        self.cb_loc_lop = ttk.Combobox(khung_tim, textvariable=self.var_loc_lop, values=[TAT_CA_LOP],
                                       state="readonly", width=12)
        self.cb_loc_lop.grid(row=1, column=3, sticky="w", pady=(KHOANG, 0))
        self.cb_loc_lop.bind("<<ComboboxSelected>>", lambda _e: self.hien_thi())
        ttk.Button(khung_tim, text="Tìm", style="Chinh.TButton", command=self.tim_kiem).grid(row=0, column=4, padx=(0, KHOANG))
        ttk.Button(khung_tim, text="Hiện tất cả", command=self.hien_tat_ca).grid(row=0, column=5)
        ttk.Button(khung_tim, text="Tải lại từ file", command=self.lam_moi_du_lieu).grid(
            row=1, column=4, columnspan=2, sticky="ew", pady=(KHOANG, 0))

        # ===== Hàng 2: bảng dữ liệu =====
        khung_bang = ttk.Frame(self)
        khung_bang.grid(row=2, column=0, sticky="nsew")
        khung_bang.columnconfigure(0, weight=1)
        khung_bang.rowconfigure(0, weight=1)
        self.bang = ttk.Treeview(khung_bang, columns=[c[0] for c in CAC_COT], show="headings",
                                 selectmode="browse", height=10)
        for ma_cot, tieu_de, rong, can in CAC_COT:
            self.bang.heading(ma_cot, text=tieu_de, command=lambda c=ma_cot: self.sap_xep_theo_cot(c))
            self.bang.column(ma_cot, width=rong, anchor=can, stretch=(ma_cot == "ho_ten"))
        self.bang.tag_configure("le", background=MAU_DONG_LE)
        thanh_cuon = ttk.Scrollbar(khung_bang, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=thanh_cuon.set)
        self.bang.grid(row=0, column=0, sticky="nsew")
        thanh_cuon.grid(row=0, column=1, sticky="ns")
        self.bang.bind("<<TreeviewSelect>>", self._chon_dong)

        # ===== Hàng 3: thanh trạng thái =====
        self.var_trang_thai = tk.StringVar()
        ttk.Label(self, textvariable=self.var_trang_thai, anchor="w").grid(
            row=3, column=0, sticky="ew", pady=(KHOANG, 0))

        self._cap_nhat_tieu_de_cot()
        self._hien_chi_tiet(None)
        self._cap_nhat_trang_thai_nut()

    # ------------------------------------------------------------------
    # Hiển thị dữ liệu
    # ------------------------------------------------------------------
    def lam_moi_du_lieu(self, bao_loi=True):
        """Đọc lại dữ liệu từ file JSON rồi hiển thị."""
        try:
            self.ql.tai_du_lieu()
        except LoiFileError as e:
            if bao_loi:
                messagebox.showerror("Không đọc được dữ liệu", str(e), parent=self)
            return
        if self.ql.loi_khi_tai and bao_loi:
            messagebox.showwarning(
                "Có bản ghi bị bỏ qua",
                "\n".join(self.ql.loi_khi_tai[:8]), parent=self)
        lop_hien_tai = self.var_loc_lop.get()
        cac_lop = self.ql.danh_sach_lop()
        self.cb_loc_lop.configure(values=[TAT_CA_LOP] + cac_lop)
        self.o_nhap["lop"].configure(values=cac_lop)
        if lop_hien_tai not in cac_lop:
            self.var_loc_lop.set(TAT_CA_LOP)
        self.hien_thi()

    def hien_thi(self):
        """Áp dụng tìm kiếm + lọc lớp + sắp xếp hiện tại rồi đổ vào bảng."""
        tieu_chi = TIEU_CHI_TIM.get(self.var_tieu_chi.get(), "tat_ca")
        ds = self.ql.tim_kiem(self.var_tu_khoa.get().strip(), tieu_chi, self.var_gan_dung.get())
        lop = self.var_loc_lop.get()
        if lop and lop != TAT_CA_LOP:
            ds = [sv for sv in ds if sv.lop == lop]
        truong, giam_dan = self._sap_xep
        ds = self.ql.sap_xep(truong, giam_dan, ds)
        self._do_bang(ds)
        return ds

    def _do_bang(self, ds):
        self._dang_do_bang = True
        try:
            self.bang.delete(*self.bang.get_children())
            for i, sv in enumerate(ds):
                self.bang.insert("", "end", iid=sv.ma_sv, tags=("le",) if i % 2 else (), values=(
                    sv.ma_sv, sv.ho_ten, sv.lop, f"{sv.gpa:.2f}", f"{sv.diem_ren_luyen:.1f}",
                    sv.xep_loai_hoc_luc(), sv.xep_loai_ren_luyen()))
            if self._ma_dang_chon and self.bang.exists(self._ma_dang_chon):
                self.bang.selection_set(self._ma_dang_chon)
                self.bang.see(self._ma_dang_chon)
        finally:
            self._dang_do_bang = False
        if self._ma_dang_chon and not self.bang.exists(self._ma_dang_chon):
            self._ma_dang_chon = None
            self._hien_chi_tiet(None)
            self._cap_nhat_trang_thai_nut()
        self.var_trang_thai.set(
            f"Hiển thị {len(ds)} / {self.ql.so_luong()} sinh viên. "
            f"Nhấn vào tiêu đề cột để sắp xếp.")
        self._lam_moi_cua_so_phu()

    def _lam_moi_cua_so_phu(self):
        """Cửa sổ thống kê / nhật ký đang mở thì cập nhật theo dữ liệu mới."""
        for cua_so in (self._cs_thong_ke, self._cs_nhat_ky):
            if cua_so is not None and cua_so.winfo_exists():
                cua_so.lam_moi()

    # ------------------------------------------------------------------
    # Thống kê (biểu đồ) và nhật ký thao tác
    # ------------------------------------------------------------------
    def mo_thong_ke(self):
        """Mở cửa sổ biểu đồ thống kê (nếu đang mở thì đưa lên trước)."""
        if self._cs_thong_ke is not None and self._cs_thong_ke.winfo_exists():
            self._cs_thong_ke.lam_moi()
            self._cs_thong_ke.lift()
            return
        self._cs_thong_ke = CuaSoThongKe(self.winfo_toplevel(), self.ql)

    def mo_nhat_ky(self):
        """Mở cửa sổ nhật ký thao tác. Chỉ quản trị viên (duoc_chinh_sua=True) được xem."""
        if not self.duoc_chinh_sua:
            messagebox.showwarning("Không có quyền",
                                   "Chỉ quản trị viên mới được xem nhật ký thao tác.", parent=self)
            return
        if self.ql.nhat_ky is None:
            messagebox.showinfo("Nhật ký đang tắt",
                                "Nhật ký thao tác chưa được bật cho danh sách sinh viên này.", parent=self)
            return
        if self._cs_nhat_ky is not None and self._cs_nhat_ky.winfo_exists():
            self._cs_nhat_ky.lam_moi()
            self._cs_nhat_ky.lift()
            return
        self._cs_nhat_ky = CuaSoNhatKy(self.winfo_toplevel(), self.ql.nhat_ky)

    def _hien_chi_tiet(self, sv):
        if sv is None:
            self.var_ct_ten.set("Chưa chọn sinh viên")
            self.var_ct_gpa.set("")
            self.var_ct_drl.set("")
            self.meter_gpa.dat_gia_tri(None)
            self.meter_drl.dat_gia_tri(None)
            return
        self.var_ct_ten.set(f"{sv.ho_ten}\n{sv.ma_sv} - {sv.lop}")
        self.var_ct_gpa.set(f"{sv.gpa:.2f} / 4.0  -  {sv.xep_loai_hoc_luc()}")
        self.var_ct_drl.set(f"{sv.diem_ren_luyen:.1f} / 100  -  {sv.xep_loai_ren_luyen()}")
        self.meter_gpa.dat_gia_tri(sv.gpa)
        self.meter_drl.dat_gia_tri(sv.diem_ren_luyen)

    # ------------------------------------------------------------------
    # Sắp xếp, tìm kiếm
    # ------------------------------------------------------------------
    def sap_xep_theo_cot(self, ma_cot):
        """Bấm tiêu đề cột: lần đầu tăng dần, bấm lại đảo chiều."""
        giam_dan = (not self._sap_xep[1]) if ma_cot == self._cot_sap_xep else False
        self._cot_sap_xep = ma_cot
        self._sap_xep = (TRUONG_SAP_XEP[ma_cot], giam_dan)
        self._cap_nhat_tieu_de_cot()
        self.hien_thi()

    def _cap_nhat_tieu_de_cot(self):
        mui_ten = " ▼" if self._sap_xep[1] else " ▲"
        for ma_cot, tieu_de, _, _ in CAC_COT:
            self.bang.heading(ma_cot, text=tieu_de + (mui_ten if ma_cot == self._cot_sap_xep else ""))

    def tim_kiem(self):
        ds = self.hien_thi()
        if not ds:
            messagebox.showinfo("Kết quả tìm kiếm", "Không tìm thấy sinh viên nào phù hợp.", parent=self)

    def hien_tat_ca(self):
        self.var_tu_khoa.set("")
        self.var_tieu_chi.set("Tất cả")
        self.var_gan_dung.set(False)
        self.var_loc_lop.set(TAT_CA_LOP)
        self.hien_thi()

    # ------------------------------------------------------------------
    # Chọn dòng / form
    # ------------------------------------------------------------------
    def _chon_dong(self, _event=None):
        if self._dang_do_bang:
            return
        chon = self.bang.selection()
        if not chon:
            return
        sv = self.ql.lay_theo_ma(chon[0])
        if sv is None:
            return
        self._ma_dang_chon = sv.ma_sv
        self.bien["ma_sv"].set(sv.ma_sv)
        self.bien["ho_ten"].set(sv.ho_ten)
        self.bien["lop"].set(sv.lop)
        self.bien["gpa"].set(f"{sv.gpa:.2f}")
        self.bien["drl"].set(f"{sv.diem_ren_luyen:.1f}")
        self.o_nhap["ma_sv"].configure(state="readonly")  # mã là khóa chính, không sửa
        self._hien_chi_tiet(sv)
        self._cap_nhat_trang_thai_nut()

    def lam_moi_form(self):
        self._ma_dang_chon = None
        self.o_nhap["ma_sv"].configure(state="normal")
        for bien in self.bien.values():
            bien.set("")
        self.bang.selection_remove(*self.bang.selection())
        self._hien_chi_tiet(None)
        self._cap_nhat_trang_thai_nut()
        self.o_nhap["ma_sv"].focus_set()

    def dat_quyen_chinh_sua(self, duoc_chinh_sua):
        """Bật/tắt quyền thêm-sửa-xóa (dùng khi đăng nhập/đăng xuất, phân quyền)."""
        self.duoc_chinh_sua = bool(duoc_chinh_sua)
        self._cap_nhat_trang_thai_nut()

    def _cap_nhat_trang_thai_nut(self):
        co_chon = self._ma_dang_chon is not None
        self.nut_them.state(["!disabled"] if self.duoc_chinh_sua and not co_chon else ["disabled"])
        self.nut_sua.state(["!disabled"] if self.duoc_chinh_sua and co_chon else ["disabled"])
        self.nut_xoa.state(["!disabled"] if self.duoc_chinh_sua and co_chon else ["disabled"])
        self.nut_nhap.state(["!disabled"] if self.duoc_chinh_sua else ["disabled"])
        self.nut_nhat_ky.state(["!disabled"] if self.duoc_chinh_sua else ["disabled"])

    # ------------------------------------------------------------------
    # Nhập / xuất file CSV, JSON
    # ------------------------------------------------------------------
    def nhap_tu_file(self, duong_dan=None):
        """Nhập hàng loạt sinh viên từ file CSV/JSON. duong_dan=None -> mở hộp chọn file."""
        if not self._co_quyen():
            return
        if duong_dan is None:
            duong_dan = filedialog.askopenfilename(
                parent=self, title="Chọn file sinh viên cần nhập",
                filetypes=[("CSV hoặc JSON", "*.csv *.json"), ("CSV", "*.csv"), ("JSON", "*.json")])
            if not duong_dan:
                return
        try:
            ban_ghi = doc_file(duong_dan)
        except LoiFileError as e:
            messagebox.showerror("Không đọc được file", str(e), parent=self)
            return
        if not ban_ghi:
            messagebox.showinfo("File trống", "File không có sinh viên nào để nhập.", parent=self)
            return
        tra_loi = messagebox.askyesnocancel(
            "Nhập từ file",
            f"Đọc được {len(ban_ghi)} dòng dữ liệu.\n\n"
            f"Nếu trùng mã sinh viên với dữ liệu hiện có:\n"
            f"  - Yes: cập nhật theo file\n  - No: bỏ qua dòng trùng\n  - Cancel: hủy nhập",
            parent=self)
        if tra_loi is None:
            return
        try:
            ket_qua = self.ql.nhap_hang_loat(ban_ghi, ghi_de=tra_loi)
        except LoiFileError as e:
            messagebox.showerror("Không lưu được dữ liệu", str(e), parent=self)
            return
        hop_thoai = messagebox.showwarning if ket_qua.bo_qua else messagebox.showinfo
        hop_thoai("Kết quả nhập file", ket_qua.tom_tat(), parent=self)
        self.lam_moi_du_lieu(bao_loi=False)

    def xuat_ra_file(self, duong_dan=None, chi_dang_hien_thi=True):
        """Xuất danh sách ra CSV/JSON. Mặc định xuất đúng những dòng đang hiển thị (sau tìm kiếm/lọc)."""
        ds = self.hien_thi() if chi_dang_hien_thi else self.ql.sap_xep("ma_sv")
        if not ds:
            messagebox.showinfo("Không có dữ liệu", "Không có sinh viên nào để xuất.", parent=self)
            return
        if duong_dan is None:
            duong_dan = filedialog.asksaveasfilename(
                parent=self, title="Lưu danh sách sinh viên", defaultextension=".csv",
                initialfile="danh_sach_sinh_vien.csv",
                filetypes=[("CSV (mở bằng Excel)", "*.csv"), ("JSON", "*.json")])
            if not duong_dan:
                return
        try:
            xuat_file(ds, duong_dan)
        except LoiFileError as e:
            messagebox.showerror("Không xuất được file", str(e), parent=self)
            return
        messagebox.showinfo("Thành công", f"Đã xuất {len(ds)} sinh viên ra file:\n{duong_dan}", parent=self)

    # ------------------------------------------------------------------
    # Thêm / Sửa / Xóa
    # ------------------------------------------------------------------
    def _co_quyen(self):
        if not self.duoc_chinh_sua:
            messagebox.showwarning("Không có quyền",
                                   "Tài khoản của bạn chỉ được xem và tìm kiếm, "
                                   "không được thêm, sửa hoặc xóa sinh viên.", parent=self)
        return self.duoc_chinh_sua

    def _lay_du_lieu_form(self):
        """Kiểm tra từng ô theo thứ tự. Trả về (ma, ten, lop, gpa, drl) hoặc None nếu có lỗi."""
        cac_kiem_tra = (("ma_sv", kiem_tra_ma_sv), ("ho_ten", kiem_tra_ho_ten), ("lop", kiem_tra_lop),
                        ("gpa", kiem_tra_gpa), ("drl", kiem_tra_diem_ren_luyen))
        gia_tri = []
        for khoa, ham in cac_kiem_tra:
            try:
                gia_tri.append(ham(self.bien[khoa].get()))
            except DuLieuKhongHopLeError as e:
                messagebox.showerror("Dữ liệu không hợp lệ",
                                     f"{e}\n\nVui lòng sửa lại rồi thử lại.", parent=self)
                self.o_nhap[khoa].focus_set()
                return None
        return tuple(gia_tri)

    def them(self):
        if not self._co_quyen():
            return
        du_lieu = self._lay_du_lieu_form()
        if du_lieu is None:
            return
        if self.ql.ton_tai(du_lieu[0]):
            messagebox.showerror("Trùng mã sinh viên",
                                 f"Mã sinh viên {du_lieu[0]} đã tồn tại. Hãy nhập mã khác.", parent=self)
            self.o_nhap["ma_sv"].focus_set()
            return
        try:
            sv = self.ql.them(*du_lieu)
        except (DuLieuKhongHopLeError, LoiFileError) as e:
            messagebox.showerror("Không thêm được", str(e), parent=self)
            return
        messagebox.showinfo("Thành công", f"Đã thêm sinh viên {sv.ho_ten} ({sv.ma_sv}).", parent=self)
        self.lam_moi_form()
        self.lam_moi_du_lieu(bao_loi=False)
        if self.bang.exists(sv.ma_sv):
            self.bang.selection_set(sv.ma_sv)
            self.bang.see(sv.ma_sv)

    def cap_nhat(self):
        if not self._co_quyen():
            return
        if self._ma_dang_chon is None:
            messagebox.showwarning("Chưa chọn sinh viên",
                                   "Hãy chọn một sinh viên trong bảng trước khi cập nhật.", parent=self)
            return
        du_lieu = self._lay_du_lieu_form()
        if du_lieu is None:
            return
        ma = self._ma_dang_chon
        try:
            self.ql.sua(ma, *du_lieu[1:])
        except (DuLieuKhongHopLeError, LoiFileError) as e:
            messagebox.showerror("Không cập nhật được", str(e), parent=self)
            return
        messagebox.showinfo("Thành công", f"Đã cập nhật sinh viên {ma}.", parent=self)
        self.hien_thi()
        self._chon_dong_theo_ma(ma)

    def xoa(self):
        if not self._co_quyen():
            return
        if self._ma_dang_chon is None:
            messagebox.showwarning("Chưa chọn sinh viên",
                                   "Hãy chọn một sinh viên trong bảng trước khi xóa.", parent=self)
            return
        ma = self._ma_dang_chon
        sv = self.ql.lay_theo_ma(ma)
        try:
            con_rang_buoc = self.kiem_tra_rang_buoc(ma)
        except LoiFileError as e:
            messagebox.showerror("Không kiểm tra được hồ sơ",
                                 f"{e}\nVì an toàn, chưa thể xóa sinh viên này.", parent=self)
            return
        if con_rang_buoc:
            messagebox.showwarning("Không thể xóa",
                                   f"Sinh viên {ma} đang có hồ sơ học bổng.\n"
                                   f"Hãy xóa hồ sơ học bổng của sinh viên này trước.", parent=self)
            return
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Bạn chắc chắn muốn xóa sinh viên {sv.ho_ten} ({ma})?\n"
                                   f"Thao tác này không thể hoàn tác.", parent=self):
            return
        try:
            self.ql.xoa(ma, self.kiem_tra_rang_buoc)
        except (DuLieuKhongHopLeError, LoiFileError) as e:
            messagebox.showerror("Không xóa được", str(e), parent=self)
            return
        messagebox.showinfo("Thành công", f"Đã xóa sinh viên {ma}.", parent=self)
        self.lam_moi_form()
        self.lam_moi_du_lieu(bao_loi=False)

    def _chon_dong_theo_ma(self, ma):
        if self.bang.exists(ma):
            self.bang.selection_set(ma)
            self.bang.see(ma)
            self._chon_dong()


# ======================================================================
# Cửa sổ độc lập
# ======================================================================
class UngDungSinhVien(tk.Tk):
    """Cửa sổ chính chạy riêng phần sinh viên (có Menu)."""

    def __init__(self, ql=None, kiem_tra_rang_buoc=None, duoc_chinh_sua=True):
        super().__init__()
        self.title("Quản lý sinh viên - Hệ thống quản lý học bổng")
        self.geometry("1000x780")
        self.minsize(900, 660)
        self.configure(bg=MAU_NEN)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.khung = SinhVienFrame(self, ql, kiem_tra_rang_buoc, duoc_chinh_sua)
        self.khung.grid(row=1, column=0, sticky="nsew")
        # tạo style tiêu đề sau khi khung đã chọn theme (đổi theme sẽ làm mất style đã đặt trước)
        ttk.Style(self).configure("TieuDe.TLabel", background=MAU_CHINH, foreground="white",
                                  font=FONT_TIEU_DE, padding=(14, 10))
        ttk.Label(self, text="QUẢN LÝ SINH VIÊN", style="TieuDe.TLabel").grid(row=0, column=0, sticky="ew")

        self._tao_menu()
        self.bind("<F5>", lambda _e: self.khung.lam_moi_du_lieu())
        self.bind("<Control-f>", lambda _e: self.khung.o_tu_khoa.focus_set())

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
