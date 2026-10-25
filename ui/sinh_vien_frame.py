"""Module ui/sinh_vien_frame.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

SinhVienFrame: khung quản lý sinh viên (KPI, form, chi tiết, tìm kiếm, bảng).
Có thể nhúng vào bất kỳ cửa sổ/Notebook nào của nhóm.
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
from services.thong_ke_sinh_vien import tong_quan
from ui.cua_so_nhat_ky import CuaSoNhatKy
from ui.cua_so_thong_ke import CuaSoThongKe
from ui.score_meter import ScoreMeter
from ui.theme import (FONT, FONT_DAM_NHO, FONT_NHAN_NHO, FONT_NHO, FONT_SO_LON, FONT_TIEU_DE_THE,
                      KHOANG, MAU_CANH_BAO, MAU_CHINH, MAU_CHINH_DAM, MAU_CHON, MAU_CHU,
                      MAU_CHU_PHU, MAU_DONG_LE, MAU_HOC_LUC, MAU_NEN, MAU_NGUY_HIEM,
                      MAU_NGUY_HIEM_DAM, MAU_THANH_CONG, MAU_THE, MAU_VIEN, tao_the)

# (mã cột, tiêu đề, độ rộng, căn lề)
CAC_COT = (
    ("ma_sv", "Mã SV", 110, "center"),
    ("ho_ten", "Họ và tên", 240, "w"),
    ("lop", "Lớp", 90, "center"),
    ("gpa", "GPA", 80, "center"),
    ("diem_ren_luyen", "Điểm RL", 90, "center"),
    ("hoc_luc", "Học lực", 110, "center"),
    ("ren_luyen", "Xếp loại RL", 120, "center"),
)
# cột hiển thị -> trường dùng để sắp xếp
TRUONG_SAP_XEP = {
    "ma_sv": "ma_sv", "ho_ten": "ho_ten", "lop": "lop", "gpa": "gpa",
    "diem_ren_luyen": "diem_ren_luyen", "hoc_luc": "gpa", "ren_luyen": "diem_ren_luyen",
}
TIEU_CHI_TIM = {"Tất cả": "tat_ca", "Mã SV": "ma_sv", "Họ tên": "ho_ten", "Lớp": "lop"}
TAT_CA_LOP = "Tất cả lớp"
NGUONG_CANH_BAO_GPA = 2.0  # GPA dưới ngưỡng này được tô đỏ và đếm vào "Cần theo dõi"


def _nhan(master, text="", bg=MAU_THE, font=FONT, fg=MAU_CHU, **kw):
    return tk.Label(master, text=text, bg=bg, font=font, fg=fg, anchor="w", **kw)


def _noi_dung(the):
    """Vùng nội dung bên trong thẻ, có đệm đều."""
    the.columnconfigure(0, weight=1)
    the.rowconfigure(0, weight=1)
    noi = tk.Frame(the, bg=MAU_THE)
    noi.grid(row=0, column=0, sticky="nsew", padx=18, pady=(10, 12))
    return noi


class SinhVienFrame(ttk.Frame):
    """Khung quản lý sinh viên: thêm, xem, sửa, xóa, tìm kiếm, lọc, sắp xếp."""

    def __init__(self, master, ql=None, kiem_tra_rang_buoc=None, duoc_chinh_sua=True):
        """
        ql                 : đối tượng QuanLySinhVien (mặc định đọc data/sinh_vien.json).
        kiem_tra_rang_buoc : hàm(ma_sv) -> True nếu sinh viên còn hồ sơ học bổng (không cho xóa).
        duoc_chinh_sua     : False với người dùng thường (chỉ xem/tìm), True với quản trị viên.
        """
        super().__init__(master, padding=(KHOANG * 2, KHOANG), style="Nen.TFrame")
        self.ql = ql if ql is not None else QuanLySinhVien()
        self.kiem_tra_rang_buoc = kiem_tra_rang_buoc or sinh_vien_co_ho_so
        self.duoc_chinh_sua = duoc_chinh_sua
        self._sap_xep = ("ma_sv", False)  # (trường, giảm dần?)
        self._cot_sap_xep = "ma_sv"       # cột đang sắp xếp (để vẽ mũi tên)
        self._ma_dang_chon = None
        self._dang_do_bang = False
        self._hen_tim = None
        self._cs_thong_ke = None
        self._cs_nhat_ky = None
        self._tao_style()
        self._tao_giao_dien()
        self.lam_moi_du_lieu(bao_loi=False)

    # ------------------------------------------------------------------
    # Style
    # ------------------------------------------------------------------
    def _tao_style(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", font=FONT, background=MAU_NEN, foreground=MAU_CHU)
        style.configure("Nen.TFrame", background=MAU_NEN)
        style.configure("The.TFrame", background=MAU_THE)
        style.configure("The.TCheckbutton", background=MAU_THE, font=FONT)
        style.map("The.TCheckbutton", background=[("active", MAU_THE)])

        # Ô nhập: nền trắng, viền xám, viền indigo khi có focus
        style.configure("TEntry", fieldbackground=MAU_THE, bordercolor=MAU_VIEN,
                        lightcolor=MAU_VIEN, darkcolor=MAU_VIEN, padding=(8, 5))
        style.map("TEntry", bordercolor=[("focus", MAU_CHINH)],
                  lightcolor=[("focus", MAU_CHINH)], darkcolor=[("focus", MAU_CHINH)])
        style.configure("TCombobox", fieldbackground=MAU_THE, bordercolor=MAU_VIEN,
                        arrowcolor=MAU_CHU_PHU, padding=(6, 4))
        style.map("TCombobox", fieldbackground=[("readonly", MAU_THE)],
                  bordercolor=[("focus", MAU_CHINH)])

        # Nút
        style.configure("TButton", padding=(10, 6), background=MAU_NEN, foreground=MAU_CHU,
                        bordercolor=MAU_VIEN, focusthickness=0, relief="flat")
        style.map("TButton", background=[("active", MAU_VIEN), ("disabled", MAU_NEN)],
                  foreground=[("disabled", "#94A3B8")])
        style.configure("Chinh.TButton", background=MAU_CHINH, foreground="white",
                        bordercolor=MAU_CHINH, font=FONT_DAM_NHO)
        style.map("Chinh.TButton", background=[("active", MAU_CHINH_DAM), ("disabled", "#C7D2FE")],
                  foreground=[("disabled", "white")])
        style.configure("Xoa.TButton", background=MAU_NGUY_HIEM, foreground="white",
                        bordercolor=MAU_NGUY_HIEM, font=FONT_DAM_NHO)
        style.map("Xoa.TButton", background=[("active", MAU_NGUY_HIEM_DAM), ("disabled", "#FECDD3")])

        # Bảng
        style.configure("Treeview", font=FONT, rowheight=26, background=MAU_THE,
                        fieldbackground=MAU_THE, foreground=MAU_CHU, bordercolor=MAU_THE, relief="flat")
        style.configure("Treeview.Heading", font=FONT_DAM_NHO, background=MAU_THE,
                        foreground=MAU_CHU_PHU, relief="flat", padding=(6, 5))
        style.map("Treeview.Heading", background=[("active", MAU_NEN)])
        style.map("Treeview", background=[("selected", MAU_CHON)], foreground=[("selected", MAU_CHU)])

    # ------------------------------------------------------------------
    # Dựng giao diện
    # ------------------------------------------------------------------
    def _tao_giao_dien(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1, minsize=180)  # bảng luôn có tối thiểu 180px

        self._tao_hang_kpi()  # hàng 0

        khung_tren = ttk.Frame(self, style="Nen.TFrame")  # hàng 1: form + chi tiết
        khung_tren.grid(row=1, column=0, sticky="ew", pady=(KHOANG, 0))
        khung_tren.columnconfigure(0, weight=3)
        khung_tren.columnconfigure(1, weight=2)
        self._tao_form(khung_tren)
        self._tao_chi_tiet(khung_tren)

        self._tao_tim_kiem()  # hàng 2
        self._tao_bang()      # hàng 3

        self.var_trang_thai = tk.StringVar()  # hàng 4
        tk.Label(self, textvariable=self.var_trang_thai, bg=MAU_NEN, fg=MAU_CHU_PHU,
                 font=FONT_NHO, anchor="w").grid(row=4, column=0, sticky="ew", pady=(KHOANG, 0))

        self._cap_nhat_tieu_de_cot()
        self._hien_chi_tiet(None)
        self._cap_nhat_trang_thai_nut()

    def _tao_hang_kpi(self):
        hang = ttk.Frame(self, style="Nen.TFrame")
        hang.grid(row=0, column=0, sticky="ew")
        self.var_kpi = {k: tk.StringVar(value="—") for k in ("tong", "gpa", "drl", "canh_bao")}
        self.var_kpi_phu = {k: tk.StringVar() for k in self.var_kpi}
        cau_hinh = (
            ("tong", "Tổng sinh viên", MAU_CHINH),
            ("gpa", "GPA trung bình", MAU_THANH_CONG),
            ("drl", "Điểm rèn luyện TB", MAU_CANH_BAO),
            ("canh_bao", "Cần theo dõi", MAU_NGUY_HIEM),
        )
        for c, (khoa, tieu_de, mau) in enumerate(cau_hinh):
            hang.columnconfigure(c, weight=1, uniform="kpi")
            the = tao_the(hang)
            the.grid(row=0, column=c, sticky="nsew", padx=(KHOANG if c else 0, 0))
            the.columnconfigure(1, weight=1)
            tk.Frame(the, bg=mau, width=4).grid(row=0, column=0, sticky="ns")  # vạch màu bên trái
            noi = tk.Frame(the, bg=MAU_THE)
            noi.grid(row=0, column=1, sticky="nsew", padx=14, pady=8)
            noi.columnconfigure(0, weight=1)
            _nhan(noi, tieu_de.upper(), font=FONT_NHAN_NHO, fg=MAU_CHU_PHU).grid(row=0, column=0, sticky="ew")
            _nhan(noi, textvariable=self.var_kpi[khoa], font=FONT_SO_LON, fg=mau).grid(
                row=1, column=0, sticky="w")
            _nhan(noi, textvariable=self.var_kpi_phu[khoa], font=FONT_NHO, fg=MAU_CHU_PHU).grid(
                row=2, column=0, sticky="w")

    def _tao_form(self, master):
        the = tao_the(master)
        the.grid(row=0, column=0, sticky="nsew", padx=(0, KHOANG * 2))
        noi = _noi_dung(the)
        for c in range(4):
            noi.columnconfigure(c, weight=1, uniform="o")
        _nhan(noi, "Thông tin sinh viên", font=FONT_TIEU_DE_THE).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        self.bien = {k: tk.StringVar() for k in ("ma_sv", "ho_ten", "lop", "gpa", "drl")}
        self.o_nhap = {}
        # (khóa, nhãn, hàng, cột, số cột chiếm)
        cac_truong = (
            ("ma_sv", "Mã sinh viên *", 1, 0, 1),
            ("lop", "Lớp *", 1, 1, 1),
            ("gpa", "GPA (0–4.0) *", 1, 2, 1),
            ("drl", "Điểm RL (0–100) *", 1, 3, 1),
            ("ho_ten", "Họ và tên *", 2, 0, 4),
        )
        for khoa, nhan, hang, cot, gop in cac_truong:
            khung = tk.Frame(noi, bg=MAU_THE)
            khung.grid(row=hang, column=cot, columnspan=gop, sticky="ew",
                       padx=(0, KHOANG * 2), pady=(0, 6))
            khung.columnconfigure(0, weight=1)
            _nhan(khung, nhan.upper(), font=FONT_NHAN_NHO, fg=MAU_CHU_PHU).grid(
                row=0, column=0, sticky="w", pady=(0, 3))
            if khoa == "lop":
                o = ttk.Combobox(khung, textvariable=self.bien[khoa])
            else:
                o = ttk.Entry(khung, textvariable=self.bien[khoa])
            o.grid(row=1, column=0, sticky="ew")
            self.o_nhap[khoa] = o

        # Tất cả nút trên một hàng
        khung_nut = ttk.Frame(noi, style="The.TFrame")
        khung_nut.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(2, 0))
        for c in range(8):
            khung_nut.columnconfigure(c, weight=1, uniform="nut")
        self.nut_them = ttk.Button(khung_nut, text="Thêm", style="Chinh.TButton", command=self.them)
        self.nut_sua = ttk.Button(khung_nut, text="Cập nhật", style="Chinh.TButton", command=self.cap_nhat)
        self.nut_xoa = ttk.Button(khung_nut, text="Xóa", style="Xoa.TButton", command=self.xoa)
        self.nut_moi = ttk.Button(khung_nut, text="Làm mới", command=self.lam_moi_form)
        self.nut_nhap = ttk.Button(khung_nut, text="Nhập file", command=self.nhap_tu_file)
        self.nut_xuat = ttk.Button(khung_nut, text="Xuất file", command=self.xuat_ra_file)
        self.nut_thong_ke = ttk.Button(khung_nut, text="Thống kê", command=self.mo_thong_ke)
        self.nut_nhat_ky = ttk.Button(khung_nut, text="Nhật ký", command=self.mo_nhat_ky)
        cac_nut = (self.nut_them, self.nut_sua, self.nut_xoa, self.nut_moi,
                   self.nut_nhap, self.nut_xuat, self.nut_thong_ke, self.nut_nhat_ky)
        for c, nut in enumerate(cac_nut):
            nut.grid(row=0, column=c, sticky="ew", padx=(0 if c == 0 else 4, 0))

    def _tao_chi_tiet(self, master):
        the = tao_the(master)
        the.grid(row=0, column=1, sticky="nsew")
        noi = _noi_dung(the)
        noi.columnconfigure(0, weight=1)

        _nhan(noi, "CHI TIẾT ĐANG CHỌN", font=FONT_NHAN_NHO, fg=MAU_CHU_PHU).grid(row=0, column=0, sticky="w")
        self.var_ct_ten = tk.StringVar()
        self.var_ct_phu = tk.StringVar()
        _nhan(noi, textvariable=self.var_ct_ten, font=FONT_TIEU_DE_THE).grid(
            row=1, column=0, sticky="w", pady=(4, 0))
        _nhan(noi, textvariable=self.var_ct_phu, fg=MAU_CHU_PHU).grid(row=2, column=0, sticky="w")
        self.badge = tk.Label(noi, font=FONT_DAM_NHO, fg="white", bg=MAU_THE, padx=10, pady=2)
        self.badge.grid(row=3, column=0, sticky="w", pady=(6, 6))

        _nhan(noi, "GPA", font=FONT_DAM_NHO, fg=MAU_CHU_PHU).grid(row=4, column=0, sticky="w")
        self.meter_gpa = ScoreMeter(noi, toi_da=4.0, nen=MAU_THE)
        self.meter_gpa.grid(row=5, column=0, sticky="ew", pady=(2, 2))
        self.var_ct_gpa = tk.StringVar()
        _nhan(noi, textvariable=self.var_ct_gpa).grid(row=6, column=0, sticky="w", pady=(0, 4))

        _nhan(noi, "Điểm rèn luyện", font=FONT_DAM_NHO, fg=MAU_CHU_PHU).grid(row=7, column=0, sticky="w")
        self.meter_drl = ScoreMeter(noi, toi_da=100.0, nen=MAU_THE)
        self.meter_drl.grid(row=8, column=0, sticky="ew", pady=(2, 2))
        self.var_ct_drl = tk.StringVar()
        _nhan(noi, textvariable=self.var_ct_drl).grid(row=9, column=0, sticky="w")

    def _tao_tim_kiem(self):
        the = tao_the(self)
        the.grid(row=2, column=0, sticky="ew", pady=(KHOANG, 0))
        noi = _noi_dung(the)
        noi.columnconfigure(1, weight=1)  # ô từ khóa giãn ngang

        self.var_tieu_chi = tk.StringVar(value="Tất cả")
        self.var_tu_khoa = tk.StringVar()
        self.var_gan_dung = tk.BooleanVar(value=False)
        self.var_loc_lop = tk.StringVar(value=TAT_CA_LOP)

        cb_tieu_chi = ttk.Combobox(noi, textvariable=self.var_tieu_chi, values=list(TIEU_CHI_TIM),
                                   state="readonly", width=9)
        cb_tieu_chi.grid(row=0, column=0, padx=(0, KHOANG))
        cb_tieu_chi.bind("<<ComboboxSelected>>", lambda _e: self.hien_thi())

        self.o_tu_khoa = ttk.Entry(noi, textvariable=self.var_tu_khoa)
        self.o_tu_khoa.grid(row=0, column=1, sticky="ew", padx=(0, KHOANG))
        self.o_tu_khoa.bind("<Return>", lambda _e: self.tim_kiem())
        self.var_tu_khoa.trace_add("write", self._hen_tim_truc_tiep)  # tìm ngay khi gõ

        ttk.Checkbutton(noi, text="Gần đúng", variable=self.var_gan_dung, style="The.TCheckbutton",
                        command=self.hien_thi).grid(row=0, column=2, padx=(0, KHOANG * 2))

        self.cb_loc_lop = ttk.Combobox(noi, textvariable=self.var_loc_lop, values=[TAT_CA_LOP],
                                       state="readonly", width=13)
        self.cb_loc_lop.grid(row=0, column=3, padx=(0, KHOANG))
        self.cb_loc_lop.bind("<<ComboboxSelected>>", lambda _e: self.hien_thi())

        ttk.Button(noi, text="Tìm", style="Chinh.TButton", command=self.tim_kiem).grid(
            row=0, column=4, padx=(0, KHOANG))
        ttk.Button(noi, text="Hiện tất cả", command=self.hien_tat_ca).grid(row=0, column=5, padx=(0, KHOANG))
        ttk.Button(noi, text="Tải lại", command=self.lam_moi_du_lieu).grid(row=0, column=6)

    def _tao_bang(self):
        the = tao_the(self)
        the.grid(row=3, column=0, sticky="nsew", pady=(KHOANG, 0))
        the.columnconfigure(0, weight=1)
        the.rowconfigure(0, weight=1)
        noi = tk.Frame(the, bg=MAU_THE)
        noi.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        noi.columnconfigure(0, weight=1)
        noi.rowconfigure(0, weight=1)

        self.bang = ttk.Treeview(noi, columns=[c[0] for c in CAC_COT], show="headings",
                                 selectmode="browse", height=8)
        for ma_cot, tieu_de, rong, can in CAC_COT:
            self.bang.heading(ma_cot, text=tieu_de, command=lambda c=ma_cot: self.sap_xep_theo_cot(c))
            self.bang.column(ma_cot, width=rong, anchor=can, stretch=(ma_cot == "ho_ten"))
        self.bang.tag_configure("le", background=MAU_DONG_LE)
        self.bang.tag_configure("canh_bao", foreground=MAU_NGUY_HIEM)

        cuon = ttk.Scrollbar(noi, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=cuon.set)
        self.bang.grid(row=0, column=0, sticky="nsew")
        cuon.grid(row=0, column=1, sticky="ns")
        self.bang.bind("<<TreeviewSelect>>", self._chon_dong)
        self.bang.bind("<Double-1>", lambda _e: self.o_nhap["ho_ten"].focus_set())

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
                tags = []
                if i % 2:
                    tags.append("le")
                if sv.gpa < NGUONG_CANH_BAO_GPA:
                    tags.append("canh_bao")
                self.bang.insert("", "end", iid=sv.ma_sv, tags=tuple(tags), values=(
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
        self._cap_nhat_trang_thai(ds)
        self._cap_nhat_kpi()
        self._lam_moi_cua_so_phu()

    def _cap_nhat_trang_thai(self, ds):
        n = self.ql.so_luong()
        so_canh_bao = sum(1 for sv in ds if sv.gpa < NGUONG_CANH_BAO_GPA)
        if n == 0:
            text = "Chưa có sinh viên nào. Nhấn Nhập file hoặc Thêm để bắt đầu."
        elif not ds:
            text = "Không có sinh viên nào phù hợp với bộ lọc hiện tại."
        else:
            text = f"Hiển thị {len(ds)} / {n} sinh viên"
            if so_canh_bao:
                text += f"   •   {so_canh_bao} SV có GPA dưới 2.0 (tô đỏ)"
            text += "   •   Nhấn tiêu đề cột để sắp xếp"
        self.var_trang_thai.set(text)

    def _cap_nhat_kpi(self):
        ds = self.ql.danh_sach()
        s = tong_quan(ds)
        n = s["tong"]
        canh_bao = sum(1 for sv in ds if sv.gpa < NGUONG_CANH_BAO_GPA)
        self.var_kpi["tong"].set(str(n))
        self.var_kpi_phu["tong"].set(f"thuộc {s['so_lop']} lớp" if n else "Chưa có dữ liệu")
        self.var_kpi["gpa"].set(f"{s['gpa_tb']:.2f}" if n else "—")
        self.var_kpi_phu["gpa"].set(f"Cao nhất: {s['gpa_cao_nhat'].gpa:.2f}" if n else "")
        self.var_kpi["drl"].set(f"{s['drl_tb']:.1f}" if n else "—")
        self.var_kpi_phu["drl"].set("trên thang 100" if n else "")
        self.var_kpi["canh_bao"].set(str(canh_bao))
        self.var_kpi_phu["canh_bao"].set("sinh viên có GPA < 2.0" if n else "")

    def _hien_chi_tiet(self, sv):
        if sv is None:
            self.var_ct_ten.set("Chưa chọn sinh viên")
            self.var_ct_phu.set("Chọn một dòng trong bảng để xem chi tiết")
            self.badge.configure(text="", bg=MAU_THE)
            self.var_ct_gpa.set("")
            self.var_ct_drl.set("")
            self.meter_gpa.dat_gia_tri(None)
            self.meter_drl.dat_gia_tri(None)
            return
        hoc_luc = sv.xep_loai_hoc_luc()
        self.var_ct_ten.set(sv.ho_ten)
        self.var_ct_phu.set(f"{sv.ma_sv}   •   Lớp {sv.lop}")
        self.badge.configure(text=hoc_luc, bg=MAU_HOC_LUC.get(hoc_luc, MAU_CHU_PHU))
        self.var_ct_gpa.set(f"{sv.gpa:.2f} / 4.0")
        self.var_ct_drl.set(f"{sv.diem_ren_luyen:.1f} / 100   •   {sv.xep_loai_ren_luyen()}")
        self.meter_gpa.dat_gia_tri(sv.gpa)
        self.meter_drl.dat_gia_tri(sv.diem_ren_luyen)

    def _lam_moi_cua_so_phu(self):
        """Cửa sổ thống kê / nhật ký đang mở thì cập nhật theo dữ liệu mới."""
        for cua_so in (self._cs_thong_ke, self._cs_nhat_ky):
            if cua_so is not None and cua_so.winfo_exists():
                cua_so.lam_moi()

    # ------------------------------------------------------------------
    # Tìm kiếm
    # ------------------------------------------------------------------
    def _hen_tim_truc_tiep(self, *_):
        """Gõ tới đâu lọc tới đó, chờ 250ms sau lần gõ cuối để khỏi lọc liên tục."""
        if self._hen_tim is not None:
            self.after_cancel(self._hen_tim)
        self._hen_tim = self.after(250, self._thuc_hien_tim)

    def _thuc_hien_tim(self):
        self._hen_tim = None
        self.hien_thi()

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

    # ------------------------------------------------------------------
    # Sắp xếp
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