"""Module services/quan_ly_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

QuanLySinhVien: lớp nghiệp vụ CRUD + tìm kiếm + lọc + sắp xếp sinh viên.
"""

import os
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from config import DUONG_DAN_NHAT_KY, DUONG_DAN_SINH_VIEN
from models.sinh_vien import SinhVien, DuLieuKhongHopLeError
from services.luu_tru_json import LuuTruJSON, LoiFileError
from services.nhat_ky import NhatKy


def bo_dau(text):
    """Bỏ dấu tiếng Việt và chuyển về chữ thường để tìm kiếm không phân biệt dấu."""
    text = str(text).replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn").lower()


@dataclass
class KetQuaNhap:
    """Kết quả nhập hàng loạt: số bản ghi thêm/cập nhật và lý do từng dòng bị bỏ qua."""
    them: int = 0
    cap_nhat: int = 0
    bo_qua: list = field(default_factory=list)

    def tom_tat(self, toi_da=8):
        dong = [f"Đã thêm: {self.them} | Đã cập nhật: {self.cap_nhat} | Bỏ qua: {len(self.bo_qua)}"]
        dong += self.bo_qua[:toi_da]
        if len(self.bo_qua) > toi_da:
            dong.append(f"... và {len(self.bo_qua) - toi_da} dòng khác.")
        return "\n".join(dong)


class QuanLySinhVien:
    """Quản lý danh sách sinh viên (CRUD + tìm kiếm), lưu trong file JSON."""

    TIEU_CHI_TIM = ("tat_ca", "ma_sv", "ho_ten", "lop")
    TRUONG_SAP_XEP = ("ma_sv", "ho_ten", "lop", "gpa", "diem_ren_luyen")

    def __init__(self, duong_dan=DUONG_DAN_SINH_VIEN, nhat_ky=None, nguoi_dung="admin"):
        """
        nhat_ky   : None  -> tự ghi nhật ký vào file nhat_ky.log cạnh file dữ liệu;
                    False -> tắt nhật ký;  hoặc truyền một đối tượng NhatKy có sẵn.
        nguoi_dung: tên người thao tác được ghi vào nhật ký (khi có đăng nhập thì gán
                    ql.nguoi_dung = tên_đăng_nhập).
        """
        self.__luu_tru = LuuTruJSON(duong_dan)
        self.__ds = {}  # ma_sv -> SinhVien
        self.loi_khi_tai = []  # các bản ghi lỗi bị bỏ qua khi tải
        self.nguoi_dung = nguoi_dung
        if nhat_ky is False:
            self.nhat_ky = None
        elif nhat_ky is None:
            if duong_dan == DUONG_DAN_SINH_VIEN:
                duong_dan_log = DUONG_DAN_NHAT_KY
            else:
                duong_dan_log = os.path.join(os.path.dirname(duong_dan), "nhat_ky.log")
            self.nhat_ky = NhatKy(duong_dan_log)
        else:
            self.nhat_ky = nhat_ky
        self.tai_du_lieu()

    # ---------- Nhật ký ----------
    def _ghi_nhat_ky(self, hanh_dong, ma_sv, chi_tiet=""):
        """Ghi nhật ký; lỗi ghi nhật ký không bao giờ làm hỏng thao tác chính."""
        if self.nhat_ky is not None:
            self.nhat_ky.ghi(self.nguoi_dung, hanh_dong, ma_sv, chi_tiet)

    @staticmethod
    def _mo_ta_sv(sv):
        return f"{sv.ho_ten} - {sv.lop} - GPA {sv.gpa:.2f} - ĐRL {sv.diem_ren_luyen:.1f}"

    @staticmethod
    def _mo_ta_thay_doi(cu, moi):
        cac_cap = (("Họ tên", cu.ho_ten, moi.ho_ten), ("Lớp", cu.lop, moi.lop),
                   ("GPA", f"{cu.gpa:.2f}", f"{moi.gpa:.2f}"),
                   ("ĐRL", f"{cu.diem_ren_luyen:.1f}", f"{moi.diem_ren_luyen:.1f}"))
        khac = [f"{nhan}: {a} -> {b}" for nhan, a, b in cac_cap if a != b]
        return "; ".join(khac) or "Không thay đổi giá trị"

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
        self._ghi_nhat_ky("THEM", sv.ma_sv, self._mo_ta_sv(sv))
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
        self._ghi_nhat_ky("SUA", moi.ma_sv, self._mo_ta_thay_doi(cu, moi))
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
        self._ghi_nhat_ky("XOA", sv.ma_sv, self._mo_ta_sv(sv))
        return sv

    # ---------- Nhập hàng loạt (từ file CSV/JSON) ----------
    def nhap_hang_loat(self, ban_ghi, ghi_de=False):
        """Nhập nhiều sinh viên cùng lúc. ban_ghi: list dict; khóa '_dong' (nếu có) là số dòng trong file.
        ghi_de=False: mã đã tồn tại -> bỏ qua dòng đó; ghi_de=True: cập nhật theo file.
        Dòng sai được ghi lại lý do và bỏ qua. Ghi file một lần; nếu ghi lỗi thì hoàn tác tất cả."""
        ket_qua = KetQuaNhap()
        ban_cu = dict(self.__ds)
        for i, d in enumerate(ban_ghi, start=1):
            dong = d.get("_dong", i) if isinstance(d, dict) else i
            try:
                if not isinstance(d, dict):
                    raise DuLieuKhongHopLeError("Bản ghi không đúng định dạng.")
                sv = SinhVien.from_dict(d)
            except DuLieuKhongHopLeError as e:
                ket_qua.bo_qua.append(f"Dòng {dong}: {e}")
                continue
            if sv.ma_sv in self.__ds:
                if not ghi_de:
                    ket_qua.bo_qua.append(f"Dòng {dong}: mã {sv.ma_sv} đã tồn tại, bỏ qua.")
                    continue
                ket_qua.cap_nhat += 1
            else:
                ket_qua.them += 1
            self.__ds[sv.ma_sv] = sv
        if ket_qua.them or ket_qua.cap_nhat:
            try:
                self.luu()
            except LoiFileError:
                self.__ds = ban_cu  # hoàn tác toàn bộ
                raise
            self._ghi_nhat_ky("NHAP_FILE", "-", f"Thêm {ket_qua.them}, cập nhật {ket_qua.cap_nhat}, "
                                                 f"bỏ qua {len(ket_qua.bo_qua)}")
        return ket_qua

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
