"""Module ui/menu_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Menu console cho chức năng sinh viên: xem danh sách, thêm, sửa, xóa, tìm kiếm,
xem chi tiết, sắp xếp. Chạy độc lập:  python -m ui.menu_sinh_vien
Hoặc gọi từ main.py:                  MenuSinhVien().chay()
"""

import functools

from services.luu_tru_json import LoiFileError
from services.quan_ly_sinh_vien import QuanLySinhVien
from services.rang_buoc_ho_so import sinh_vien_co_ho_so
from models.sinh_vien import (
    DuLieuKhongHopLeError,
    kiem_tra_ma_sv,
    kiem_tra_ho_ten,
    kiem_tra_lop,
    kiem_tra_gpa,
    kiem_tra_diem_ren_luyen,
)


class HuyThaoTac(Exception):
    """Người dùng gõ 'huy' để dừng thao tác đang nhập."""


# ---------------------------------------------------------------------------
# Decorator: gom xử lý hủy thao tác và lỗi để chương trình không bị dừng đột ngột
# ---------------------------------------------------------------------------
def _an_toan(ham):
    @functools.wraps(ham)
    def boc(self, *args, **kwargs):
        try:
            return ham(self, *args, **kwargs)
        except HuyThaoTac:
            print("Đã hủy thao tác.")
        except DuLieuKhongHopLeError as e:
            print(f"Lỗi: {e}")
        except LoiFileError as e:
            print(f"Lỗi file dữ liệu: {e}")
    return boc


# ---------------------------------------------------------------------------
# Hiển thị bảng
# ---------------------------------------------------------------------------
def _cat(chuoi, do_dai):
    chuoi = str(chuoi)
    return chuoi if len(chuoi) <= do_dai else chuoi[:do_dai - 1] + "."


def in_bang(ds, tieu_de=""):
    """In danh sách sinh viên dạng bảng."""
    if tieu_de:
        print(f"\n{tieu_de}")
    if not ds:
        print("(Không có sinh viên nào.)")
        return
    ke = "-" * 93
    print(ke)
    print(f"{'STT':<4} {'Mã SV':<11} {'Họ và tên':<26} {'Lớp':<10} {'GPA':>5} {'ĐRL':>6}  "
          f"{'Học lực':<11} {'Rèn luyện':<10}")
    print(ke)
    for i, sv in enumerate(ds, start=1):
        print(f"{i:<4} {sv.ma_sv:<11} {_cat(sv.ho_ten, 26):<26} {sv.lop:<10} "
              f"{sv.gpa:>5.2f} {sv.diem_ren_luyen:>6.1f}  "
              f"{sv.xep_loai_hoc_luc():<11} {sv.xep_loai_ren_luyen():<10}")
    print(ke)
    print(f"Tổng: {len(ds)} sinh viên")


def in_chi_tiet(sv):
    print("\n" + "=" * 40)
    print("THÔNG TIN SINH VIÊN")
    print("=" * 40)
    print(f"Mã sinh viên   : {sv.ma_sv}")
    print(f"Họ và tên      : {sv.ho_ten}")
    print(f"Lớp            : {sv.lop}")
    print(f"GPA (thang 4)  : {sv.gpa:.2f}  ({sv.xep_loai_hoc_luc()})")
    print(f"Điểm rèn luyện : {sv.diem_ren_luyen:.1f}  ({sv.xep_loai_ren_luyen()})")
    print("=" * 40)


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
class MenuSinhVien:
    """Giao diện menu console cho chức năng sinh viên."""

    TIEU_DE_MENU = """
========== QUẢN LÝ SINH VIÊN ==========
 1. Xem danh sách sinh viên
 2. Thêm sinh viên
 3. Sửa thông tin sinh viên
 4. Xóa sinh viên
 5. Tìm kiếm sinh viên
 6. Xem thông tin chi tiết
 7. Sắp xếp danh sách
 0. Quay lại / Thoát
=======================================
(Khi đang nhập, gõ 'huy' để hủy thao tác)"""

    def __init__(self, ql=None, kiem_tra_rang_buoc=None):
        self.ql = ql if ql is not None else QuanLySinhVien()
        self.kiem_tra_rang_buoc = kiem_tra_rang_buoc or sinh_vien_co_ho_so

    # ---------- nhập liệu ----------
    @staticmethod
    def _nhap(nhan, kiem_tra=None, mac_dinh=None):
        """Nhập một trường, lặp lại cho đến khi hợp lệ. 'huy' để hủy.
        mac_dinh: nếu có, nhấn Enter sẽ giữ giá trị cũ."""
        while True:
            goi_y = f" [{mac_dinh}]" if mac_dinh is not None else ""
            s = input(f"{nhan}{goi_y}: ").strip()
            if s.lower() == "huy":
                raise HuyThaoTac()
            if s == "" and mac_dinh is not None:
                s = str(mac_dinh)
            if kiem_tra is None:
                return s
            try:
                return kiem_tra(s)
            except DuLieuKhongHopLeError as e:
                print(f"  Lỗi: {e} Mời nhập lại (hoặc gõ 'huy' để hủy).")

    @staticmethod
    def _xac_nhan(cau_hoi):
        """Hỏi có/không (tương đương hộp thoại xác nhận). Mặc định là không."""
        while True:
            s = input(f"{cau_hoi} (y/n): ").strip().lower()
            if s in ("y", "yes", "c", "co", "có"):
                return True
            if s in ("n", "no", "k", "khong", "không", ""):
                return False
            print("  Vui lòng nhập y (đồng ý) hoặc n (không).")

    def _ma_ton_tai(self, s):
        ma = kiem_tra_ma_sv(s)
        if self.ql.ton_tai(ma):
            raise DuLieuKhongHopLeError(f"Mã sinh viên {ma} đã tồn tại.")
        return ma

    # ---------- 1. Xem danh sách ----------
    @_an_toan
    def xem_danh_sach(self):
        self.ql.tai_du_lieu()  # làm mới từ file
        if self.ql.so_luong() == 0:
            print("Danh sách sinh viên đang trống.")
            return
        in_bang(self.ql.sap_xep("ma_sv"), "DANH SÁCH SINH VIÊN")

    # ---------- 2. Thêm ----------
    @_an_toan
    def them_sinh_vien(self):
        print("\n--- THÊM SINH VIÊN ---")
        ma = self._nhap("Mã sinh viên (10 chữ số)", self._ma_ton_tai)
        ten = self._nhap("Họ và tên", kiem_tra_ho_ten)
        lop = self._nhap("Lớp (vd: DHKL16A)", kiem_tra_lop)
        gpa = self._nhap("GPA (0 - 4.0)", kiem_tra_gpa)
        drl = self._nhap("Điểm rèn luyện (0 - 100)", kiem_tra_diem_ren_luyen)
        sv = self.ql.them(ma, ten, lop, gpa, drl)
        print(f"Đã thêm sinh viên {sv.ma_sv} - {sv.ho_ten}.")

    # ---------- 3. Sửa ----------
    @_an_toan
    def sua_sinh_vien(self):
        print("\n--- SỬA THÔNG TIN SINH VIÊN ---")
        ma = self._nhap("Nhập mã sinh viên cần sửa", kiem_tra_ma_sv)
        sv = self.ql.lay_theo_ma(ma)
        if sv is None:
            print(f"Không tìm thấy sinh viên có mã {ma}.")
            return
        in_chi_tiet(sv)
        print("Nhấn Enter để giữ nguyên giá trị hiện tại (mã sinh viên không đổi được).")
        ten = self._nhap("Họ và tên", kiem_tra_ho_ten, sv.ho_ten)
        lop = self._nhap("Lớp", kiem_tra_lop, sv.lop)
        gpa = self._nhap("GPA (0 - 4.0)", kiem_tra_gpa, sv.gpa)
        drl = self._nhap("Điểm rèn luyện (0 - 100)", kiem_tra_diem_ren_luyen, sv.diem_ren_luyen)
        moi = self.ql.sua(ma, ten, lop, gpa, drl)
        print(f"Đã cập nhật sinh viên {moi.ma_sv}.")

    # ---------- 4. Xóa ----------
    @_an_toan
    def xoa_sinh_vien(self):
        print("\n--- XÓA SINH VIÊN ---")
        ma = self._nhap("Nhập mã sinh viên cần xóa", kiem_tra_ma_sv)
        sv = self.ql.lay_theo_ma(ma)
        if sv is None:
            print(f"Không tìm thấy sinh viên có mã {ma}.")
            return
        in_chi_tiet(sv)
        if self.kiem_tra_rang_buoc(ma):
            print(f"Không thể xóa: sinh viên {ma} đang có hồ sơ học bổng. "
                  f"Hãy xóa hồ sơ học bổng của sinh viên này trước.")
            return
        if not self._xac_nhan(f"Bạn chắc chắn muốn xóa sinh viên {sv.ho_ten}?"):
            print("Đã hủy xóa.")
            return
        self.ql.xoa(ma, self.kiem_tra_rang_buoc)
        print(f"Đã xóa sinh viên {ma}.")

    # ---------- 5. Tìm kiếm ----------
    @_an_toan
    def tim_kiem_sinh_vien(self):
        print("\n--- TÌM KIẾM SINH VIÊN ---")
        print(" 1. Tất cả (mã, họ tên, lớp)")
        print(" 2. Theo mã sinh viên")
        print(" 3. Theo họ tên")
        print(" 4. Theo lớp")
        tieu_chi = {"1": "tat_ca", "2": "ma_sv", "3": "ho_ten", "4": "lop"}.get(
            input("Chọn tiêu chí: ").strip())
        if tieu_chi is None:
            print("Lựa chọn không hợp lệ, hãy nhập số từ 1 đến 4.")
            return
        tu_khoa = ""
        while not tu_khoa:
            tu_khoa = self._nhap("Từ khóa")
            if not tu_khoa:
                print("  Lỗi: Từ khóa không được để trống.")
        gan_dung = self._xac_nhan("Tìm gần đúng (chấp nhận gõ sai nhẹ)?")
        ket_qua = self.ql.tim_kiem(tu_khoa, tieu_chi, gan_dung)
        if not ket_qua:
            print(f"Không tìm thấy sinh viên nào phù hợp với '{tu_khoa}'.")
            return
        in_bang(self.ql.sap_xep("ma_sv", ds=ket_qua), f"KẾT QUẢ TÌM KIẾM '{tu_khoa}'")

    # ---------- 6. Xem chi tiết ----------
    @_an_toan
    def xem_chi_tiet(self):
        print("\n--- XEM THÔNG TIN SINH VIÊN ---")
        ma = self._nhap("Nhập mã sinh viên", kiem_tra_ma_sv)
        sv = self.ql.lay_theo_ma(ma)
        if sv is None:
            print(f"Không tìm thấy sinh viên có mã {ma}.")
            return
        in_chi_tiet(sv)

    # ---------- 7. Sắp xếp ----------
    @_an_toan
    def sap_xep_danh_sach(self):
        print("\n--- SẮP XẾP DANH SÁCH ---")
        print(" 1. Mã sinh viên   2. Họ tên   3. Lớp   4. GPA   5. Điểm rèn luyện")
        truong = {"1": "ma_sv", "2": "ho_ten", "3": "lop", "4": "gpa", "5": "diem_ren_luyen"}.get(
            input("Sắp xếp theo: ").strip())
        if truong is None:
            print("Lựa chọn không hợp lệ, hãy nhập số từ 1 đến 5.")
            return
        thu_tu = input("Thứ tự (1 = tăng dần, 2 = giảm dần): ").strip()
        if thu_tu not in ("1", "2"):
            print("Lựa chọn không hợp lệ, hãy nhập 1 hoặc 2.")
            return
        in_bang(self.ql.sap_xep(truong, giam_dan=(thu_tu == "2")), "DANH SÁCH ĐÃ SẮP XẾP")

    # ---------- vòng lặp menu ----------
    def chay(self):
        for canh_bao in self.ql.loi_khi_tai:
            print(f"Cảnh báo khi đọc dữ liệu - {canh_bao}")
        hanh_dong = {
            "1": self.xem_danh_sach,
            "2": self.them_sinh_vien,
            "3": self.sua_sinh_vien,
            "4": self.xoa_sinh_vien,
            "5": self.tim_kiem_sinh_vien,
            "6": self.xem_chi_tiet,
            "7": self.sap_xep_danh_sach,
        }
        while True:
            print(self.TIEU_DE_MENU)
            try:
                chon = input("Chọn chức năng: ").strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nĐã thoát menu sinh viên.")
                break
            if chon == "0":
                break
            ham = hanh_dong.get(chon)
            if ham is None:
                print("Lựa chọn không hợp lệ, hãy nhập số từ 0 đến 7.")
                continue
            try:
                ham()
            except KeyboardInterrupt:
                print("\nĐã hủy thao tác.")
            except EOFError:
                break


if __name__ == "__main__":
    MenuSinhVien().chay()
