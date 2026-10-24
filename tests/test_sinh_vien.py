"""Kiểm thử lớp SinhVien và QuanLySinhVien (hợp lệ, không hợp lệ, biên, lỗi file).

Chạy từ thư mục gốc project:  python -m unittest discover -s tests -t . -v
"""
import unittest

from models.sinh_vien import (
    DuLieuKhongHopLeError, SinhVien,
    kiem_tra_diem_ren_luyen, kiem_tra_gpa, kiem_tra_ho_ten, kiem_tra_lop, kiem_tra_ma_sv,
)


class TestKiemTraMaSV(unittest.TestCase):
    def test_hop_le(self):
        self.assertEqual(kiem_tra_ma_sv("2044240275"), "2044240275")

    def test_bo_khoang_trang_thua(self):
        self.assertEqual(kiem_tra_ma_sv("  2044240275 "), "2044240275")

    def test_rong(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_ma_sv("   ")

    def test_sai_do_dai(self):
        for ma in ("12345", "20442402751", "204424027a"):
            with self.subTest(ma=ma), self.assertRaises(DuLieuKhongHopLeError):
                kiem_tra_ma_sv(ma)


class TestKiemTraHoTen(unittest.TestCase):
    def test_chuan_hoa(self):
        self.assertEqual(kiem_tra_ho_ten("  nguyễn   thị  hoa "), "Nguyễn Thị Hoa")

    def test_mot_tu_bi_loi(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_ho_ten("Hoa")

    def test_co_so_bi_loi(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_ho_ten("Nguyen Van 1")

    def test_ky_tu_dac_biet_bi_loi(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_ho_ten("Nguyen @ Van")


class TestKiemTraLop(unittest.TestCase):
    def test_viet_hoa_tu_dong(self):
        self.assertEqual(kiem_tra_lop("dhkl16a"), "DHKL16A")

    def test_rong_va_qua_dai(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_lop("")
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_lop("A" * 21)

    def test_ky_tu_la(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_lop("DH KL")


class TestKiemTraGPA(unittest.TestCase):
    def test_bien(self):
        self.assertEqual(kiem_tra_gpa("0"), 0.0)
        self.assertEqual(kiem_tra_gpa("4.0"), 4.0)

    def test_dau_phay_thap_phan(self):
        self.assertEqual(kiem_tra_gpa("3,25"), 3.25)

    def test_ngoai_khoang(self):
        for gia_tri in ("-0.01", "4.01", "4.5"):
            with self.subTest(gia_tri=gia_tri), self.assertRaises(DuLieuKhongHopLeError):
                kiem_tra_gpa(gia_tri)

    def test_khong_phai_so(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            kiem_tra_gpa("gioi")


class TestKiemTraDRL(unittest.TestCase):
    def test_bien(self):
        self.assertEqual(kiem_tra_diem_ren_luyen("0"), 0.0)
        self.assertEqual(kiem_tra_diem_ren_luyen("100"), 100.0)

    def test_ngoai_khoang(self):
        for gia_tri in ("-1", "100.1", "101"):
            with self.subTest(gia_tri=gia_tri), self.assertRaises(DuLieuKhongHopLeError):
                kiem_tra_diem_ren_luyen(gia_tri)


class TestSinhVien(unittest.TestCase):
    def test_tao_hop_le_va_xep_loai(self):
        sv = SinhVien("2044240101", "Trần Minh Anh", "dhkl16a", 3.82, 95)
        self.assertEqual(sv.lop, "DHKL16A")
        self.assertEqual(sv.xep_loai_hoc_luc(), "Xuất sắc")
        self.assertEqual(sv.xep_loai_ren_luyen(), "Xuất sắc")

    def test_sai_du_lieu_khong_tao_duoc(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            SinhVien("123", "Trần Minh Anh", "DHKL16A", 3.0, 80)

    def test_from_dict_thieu_truong(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            SinhVien.from_dict({"ma_sv": "2044240101"})

    def test_bang_gpa_xep_loai(self):
        cac_muc = [(3.6, "Xuất sắc"), (3.2, "Giỏi"), (2.5, "Khá"), (2.0, "Trung bình"), (1.99, "Yếu")]
        for gpa, ket_qua in cac_muc:
            with self.subTest(gpa=gpa):
                self.assertEqual(SinhVien("2044240101", "Trần Minh Anh", "DHKL16A", gpa, 80).xep_loai_hoc_luc(),
                                 ket_qua)

    def test_bang_drl_xep_loai(self):
        cac_muc = [(90, "Xuất sắc"), (80, "Tốt"), (65, "Khá"), (50, "Trung bình"), (35, "Yếu"), (34, "Kém")]
        for drl, ket_qua in cac_muc:
            with self.subTest(drl=drl):
                self.assertEqual(SinhVien("2044240101", "Trần Minh Anh", "DHKL16A", 3.0, drl).xep_loai_ren_luyen(),
                                 ket_qua)

    def test_bang_theo_ma(self):
        a = SinhVien("2044240101", "Trần Minh Anh", "DHKL16A", 3.0, 80)
        b = SinhVien("2044240101", "Nguyễn Khác", "DHKL16B", 2.0, 60)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
