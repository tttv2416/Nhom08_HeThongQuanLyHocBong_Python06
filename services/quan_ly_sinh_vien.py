"""Module services/quan_ly_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

QuanLySinhVien: lớp nghiệp vụ CRUD + tìm kiếm + lọc + sắp xếp sinh viên.
"""

import unicodedata
from difflib import SequenceMatcher

from config import DUONG_DAN_SINH_VIEN
from models.sinh_vien import SinhVien, DuLieuKhongHopLeError
from services.luu_tru_json import LuuTruJSON, LoiFileError


def bo_dau(text):
    """Bỏ dấu tiếng Việt và chuyển về chữ thường để tìm kiếm không phân biệt dấu."""
    text = str(text).replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn").lower()


class QuanLySinhVien:
    """Quản lý danh sách sinh viên (CRUD + tìm kiếm), lưu trong file JSON."""

    TIEU_CHI_TIM = ("tat_ca", "ma_sv", "ho_ten", "lop")
    TRUONG_SAP_XEP = ("ma_sv", "ho_ten", "lop", "gpa", "diem_ren_luyen")

    def __init__(self, duong_dan=DUONG_DAN_SINH_VIEN):
        self.__luu_tru = LuuTruJSON(duong_dan)
        self.__ds = {}  # ma_sv -> SinhVien
        self.loi_khi_tai = []  # các bản ghi lỗi bị bỏ qua khi tải
        self.tai_du_lieu()

    # ---------- Read ----------
    def tai_du_lieu(self):
        """Đọc dữ liệu từ file JSON (gọi khi khởi động hoặc làm mới)."""
        du_lieu = self.__luu_tru.doc()  # đọc trước: nếu lỗi thì giữ nguyên dữ liệu đang có
        self.__ds.clear()
        self.loi_khi_tai = []
        for i, d in enumerate(du_lieu, start=1):
            try:
                sv = SinhVien.from_dict(d)
            except DuLieuKhongHopLeError as e:
                self.loi_khi_tai.append(f"Bản ghi #{i}: {e}")
                continue
            if sv.ma_sv in self.__ds:
                self.loi_khi_tai.append(f"Bản ghi #{i}: trùng mã {sv.ma_sv}, đã bỏ qua.")
                continue
            self.__ds[sv.ma_sv] = sv

    def luu(self):
        self.__luu_tru.ghi([sv.to_dict() for sv in self.__ds.values()])

    def danh_sach(self):
        return list(self.__ds.values())

    def so_luong(self):
        return len(self.__ds)

    def lay_theo_ma(self, ma_sv):
        return self.__ds.get(str(ma_sv).strip())

    def ton_tai(self, ma_sv):
        return str(ma_sv).strip() in self.__ds

    # ---------- Create ----------
    def them(self, ma_sv, ho_ten, lop, gpa, diem_ren_luyen):
        sv = SinhVien(ma_sv, ho_ten, lop, gpa, diem_ren_luyen)  # kiểm tra dữ liệu
        if sv.ma_sv in self.__ds:
            raise DuLieuKhongHopLeError(f"Mã sinh viên {sv.ma_sv} đã tồn tại.")
        self.__ds[sv.ma_sv] = sv
        try:
            self.luu()
        except LoiFileError:
            del self.__ds[sv.ma_sv]  # hoàn tác nếu ghi file lỗi
            raise
        return sv

    # ---------- Update ----------
    def sua(self, ma_sv, ho_ten, lop, gpa, diem_ren_luyen):
        """Sửa thông tin (không đổi mã sinh viên)."""
        sv = self.lay_theo_ma(ma_sv)
        if sv is None:
            raise DuLieuKhongHopLeError(f"Không tìm thấy sinh viên có mã {ma_sv}.")
        moi = SinhVien(sv.ma_sv, ho_ten, lop, gpa, diem_ren_luyen)  # kiểm tra trước
        cu = sv
        self.__ds[sv.ma_sv] = moi
        try:
            self.luu()
        except LoiFileError:
            self.__ds[sv.ma_sv] = cu
            raise
        return moi

    # ---------- Delete ----------
    def xoa(self, ma_sv, kiem_tra_rang_buoc=None):
        """Xóa sinh viên.
        kiem_tra_rang_buoc: hàm nhận ma_sv, trả về True nếu sinh viên còn hồ sơ học bổng
        liên quan (do module hồ sơ cung cấp) -> không cho xóa.
        """
        sv = self.lay_theo_ma(ma_sv)
        if sv is None:
            raise DuLieuKhongHopLeError(f"Không tìm thấy sinh viên có mã {ma_sv}.")
        if kiem_tra_rang_buoc and kiem_tra_rang_buoc(sv.ma_sv):
            raise DuLieuKhongHopLeError(
                f"Sinh viên {sv.ma_sv} đang có hồ sơ học bổng, hãy xóa hồ sơ trước.")
        del self.__ds[sv.ma_sv]
        try:
            self.luu()
        except LoiFileError:
            self.__ds[sv.ma_sv] = sv
            raise
        return sv

    # ---------- Search / Filter / Sort ----------
    def tim_kiem(self, tu_khoa="", tieu_chi="tat_ca", gan_dung=False):
        """Tìm theo mã, họ tên, lớp (không phân biệt hoa/thường, dấu).
        gan_dung=True: dùng độ giống chuỗi (difflib) cho tìm kiếm gần đúng."""
        if tieu_chi not in self.TIEU_CHI_TIM:
            raise ValueError(f"Tiêu chí tìm kiếm không hợp lệ: {tieu_chi}")
        kw = bo_dau(tu_khoa).strip()
        if not kw:
            return self.danh_sach()
        truong = ("ma_sv", "ho_ten", "lop") if tieu_chi == "tat_ca" else (tieu_chi,)
        ket_qua = []
        for sv in self.__ds.values():
            for t in truong:
                gia_tri = bo_dau(getattr(sv, t))
                if kw in gia_tri or (
                        gan_dung and SequenceMatcher(None, kw, gia_tri).ratio() >= 0.6):
                    ket_qua.append(sv)
                    break
        return ket_qua

    def loc(self, lop=None, gpa_min=None, gpa_max=None, drl_min=None, drl_max=None):
        """Lọc theo lớp, khoảng GPA, khoảng điểm rèn luyện."""
        ket_qua = []
        for sv in self.__ds.values():
            if lop and sv.lop != lop.strip().upper():
                continue
            if gpa_min is not None and sv.gpa < gpa_min:
                continue
            if gpa_max is not None and sv.gpa > gpa_max:
                continue
            if drl_min is not None and sv.diem_ren_luyen < drl_min:
                continue
            if drl_max is not None and sv.diem_ren_luyen > drl_max:
                continue
            ket_qua.append(sv)
        return ket_qua

    def sap_xep(self, truong="ma_sv", giam_dan=False, ds=None):
        if truong not in self.TRUONG_SAP_XEP:
            raise ValueError(f"Không thể sắp xếp theo '{truong}'.")
        ds = self.danh_sach() if ds is None else ds
        if truong == "ho_ten":  # sắp theo tên (từ cuối) cho đúng thói quen tiếng Việt
            khoa = lambda sv: (bo_dau(sv.ho_ten.split()[-1]), bo_dau(sv.ho_ten))
        else:
            khoa = lambda sv: getattr(sv, truong)
        return sorted(ds, key=khoa, reverse=giam_dan)

    def danh_sach_lop(self):
        return sorted({sv.lop for sv in self.__ds.values()})
