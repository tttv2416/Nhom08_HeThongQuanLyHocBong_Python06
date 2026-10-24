"""Module sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Chứa lớp SinhVien (lớp dữ liệu) và các hàm kiểm tra dữ liệu đầu vào.
Quy ước: GPA theo thang 4.0, điểm rèn luyện theo thang 100.
"""

import re

# ---------- Regular Expression ----------
MA_SV_PATTERN = re.compile(r"^\d{10}$")                      # 10 chữ số, vd: 2044240275
HO_TEN_PATTERN = re.compile(r"^[^\W\d_]+(?: [^\W\d_]+)+$")   # chỉ chữ cái (có dấu), >= 2 từ
LOP_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{1,19}$")  # vd: DHKL16A, 20DTH1


class DuLieuKhongHopLeError(ValueError):
    """Lỗi dữ liệu sinh viên không hợp lệ (thông báo bằng tiếng Việt, dễ hiểu)."""


# ---------- Hàm kiểm tra ----------
def chuan_hoa_ho_ten(ho_ten):
    """Xóa khoảng trắng thừa và viết hoa chữ cái đầu mỗi từ."""
    return " ".join(str(ho_ten).split()).title()


def kiem_tra_ma_sv(ma_sv):
    ma_sv = str(ma_sv).strip()
    if not ma_sv:
        raise DuLieuKhongHopLeError("Mã sinh viên không được để trống.")
    if not MA_SV_PATTERN.match(ma_sv):
        raise DuLieuKhongHopLeError(
            "Mã sinh viên phải gồm đúng 10 chữ số (ví dụ: 2044240275).")
    return ma_sv


def kiem_tra_ho_ten(ho_ten):
    ho_ten = chuan_hoa_ho_ten(ho_ten)
    if not ho_ten:
        raise DuLieuKhongHopLeError("Họ tên không được để trống.")
    if not HO_TEN_PATTERN.match(ho_ten):
        raise DuLieuKhongHopLeError(
            "Họ tên chỉ gồm chữ cái, có ít nhất 2 từ và không chứa số/ký tự đặc biệt.")
    return ho_ten


def kiem_tra_lop(lop):
    lop = str(lop).strip().upper()
    if not lop:
        raise DuLieuKhongHopLeError("Lớp không được để trống.")
    if not LOP_PATTERN.match(lop):
        raise DuLieuKhongHopLeError(
            "Tên lớp dài 2-20 ký tự, chỉ gồm chữ, số, '-', '_' hoặc '.' (ví dụ: DHKL16A).")
    return lop


def kiem_tra_gpa(gpa):
    try:
        gpa = float(str(gpa).strip().replace(",", "."))
    except ValueError:
        raise DuLieuKhongHopLeError("GPA phải là một số (ví dụ: 3.25).") from None
    if not 0.0 <= gpa <= 4.0:
        raise DuLieuKhongHopLeError("GPA phải nằm trong khoảng từ 0 đến 4.0.")
    return round(gpa, 2)


def kiem_tra_diem_ren_luyen(diem):
    try:
        diem = float(str(diem).strip().replace(",", "."))
    except ValueError:
        raise DuLieuKhongHopLeError("Điểm rèn luyện phải là một số (ví dụ: 85).") from None
    if not 0.0 <= diem <= 100.0:
        raise DuLieuKhongHopLeError("Điểm rèn luyện phải nằm trong khoảng từ 0 đến 100.")
    return round(diem, 1)


# ---------- Lớp SinhVien ----------
class SinhVien:
    """Đối tượng sinh viên. Các thuộc tính được đóng gói, kiểm tra qua property setter."""

    def __init__(self, ma_sv, ho_ten, lop, gpa, diem_ren_luyen):
        self.ma_sv = ma_sv
        self.ho_ten = ho_ten
        self.lop = lop
        self.gpa = gpa
        self.diem_ren_luyen = diem_ren_luyen

    # --- properties (getter/setter có kiểm tra) ---
    @property
    def ma_sv(self):
        return self.__ma_sv

    @ma_sv.setter
    def ma_sv(self, value):
        self.__ma_sv = kiem_tra_ma_sv(value)

    @property
    def ho_ten(self):
        return self.__ho_ten

    @ho_ten.setter
    def ho_ten(self, value):
        self.__ho_ten = kiem_tra_ho_ten(value)

    @property
    def lop(self):
        return self.__lop

    @lop.setter
    def lop(self, value):
        self.__lop = kiem_tra_lop(value)

    @property
    def gpa(self):
        return self.__gpa

    @gpa.setter
    def gpa(self, value):
        self.__gpa = kiem_tra_gpa(value)

    @property
    def diem_ren_luyen(self):
        return self.__diem_ren_luyen

    @diem_ren_luyen.setter
    def diem_ren_luyen(self, value):
        self.__diem_ren_luyen = kiem_tra_diem_ren_luyen(value)

    # --- nghiệp vụ ---
    def xep_loai_ren_luyen(self):
        d = self.diem_ren_luyen
        if d >= 90:
            return "Xuất sắc"
        if d >= 80:
            return "Tốt"
        if d >= 65:
            return "Khá"
        if d >= 50:
            return "Trung bình"
        if d >= 35:
            return "Yếu"
        return "Kém"

    def xep_loai_hoc_luc(self):
        g = self.gpa
        if g >= 3.6:
            return "Xuất sắc"
        if g >= 3.2:
            return "Giỏi"
        if g >= 2.5:
            return "Khá"
        if g >= 2.0:
            return "Trung bình"
        return "Yếu"

    # --- chuyển đổi dữ liệu ---
    def to_dict(self):
        return {
            "ma_sv": self.ma_sv,
            "ho_ten": self.ho_ten,
            "lop": self.lop,
            "gpa": self.gpa,
            "diem_ren_luyen": self.diem_ren_luyen,
        }

    @classmethod
    def from_dict(cls, data):
        """Tạo SinhVien từ dict (đọc từ JSON). Thiếu khóa -> DuLieuKhongHopLeError."""
        try:
            return cls(data["ma_sv"], data["ho_ten"], data["lop"],
                       data["gpa"], data["diem_ren_luyen"])
        except KeyError as e:
            raise DuLieuKhongHopLeError(f"Thiếu trường dữ liệu: {e.args[0]}") from None
        except TypeError:
            raise DuLieuKhongHopLeError("Bản ghi sinh viên không đúng định dạng.") from None

    def __str__(self):
        return (f"{self.ma_sv} | {self.ho_ten} | {self.lop} | "
                f"GPA: {self.gpa} | ĐRL: {self.diem_ren_luyen}")

    def __repr__(self):
        return f"SinhVien({self.ma_sv!r}, {self.ho_ten!r}, {self.lop!r}, {self.gpa}, {self.diem_ren_luyen})"

    def __eq__(self, other):
        return isinstance(other, SinhVien) and self.ma_sv == other.ma_sv

    def __hash__(self):
        return hash(self.ma_sv)
