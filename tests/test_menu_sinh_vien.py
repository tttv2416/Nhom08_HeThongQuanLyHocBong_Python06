"""Kiểm thử menu console sinh viên: nhập sai, trùng mã, không tìm thấy, hủy, ràng buộc.

Chạy từ thư mục gốc project:  python -m unittest discover -s tests -t . -v
"""

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ui.menu_sinh_vien import MenuSinhVien, sinh_vien_co_ho_so
from services.quan_ly_sinh_vien import QuanLySinhVien
from tests.test_sinh_vien import DU_LIEU_MAU, tao_file_mau

MA_CO_HO_SO = "2044240101"  # giả lập: sinh viên này đã có hồ sơ học bổng


class TestMenuSinhVien(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.duong_dan = tao_file_mau(self.thu_muc)
        self.ql = QuanLySinhVien(self.duong_dan)
        self.menu = MenuSinhVien(self.ql, kiem_tra_rang_buoc=lambda ma: ma == MA_CO_HO_SO)

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    def chay(self, ham, *nhap):
        """Chạy một chức năng với các dòng nhập giả lập, trả về nội dung in ra."""
        with patch("builtins.input", side_effect=list(nhap)), redirect_stdout(io.StringIO()) as out:
            ham()
        return out.getvalue()

    # ----- Thêm -----
    def test_them_nhap_sai_roi_nhap_dung(self):
        out = self.chay(
            self.menu.them_sinh_vien,
            "123",                  # mã sai độ dài
            "2044240275",           # mã trùng
            "2044240888",           # mã đúng
            "A",                    # họ tên 1 từ
            "Lê Văn Cường",
            "",                     # lớp rỗng
            "DHKL16A",
            "5",                    # GPA ngoài khoảng
            "abc",                  # GPA không phải số
            "3.4",
            "101",                  # ĐRL ngoài khoảng
            "80",
        )
        self.assertIn("10 chữ số", out)
        self.assertIn("đã tồn tại", out)
        self.assertIn("ít nhất 2 từ", out)
        self.assertIn("không được để trống", out)
        self.assertIn("0 đến 4.0", out)
        self.assertIn("phải là một số", out)
        self.assertIn("0 đến 100", out)
        sv = self.ql.lay_theo_ma("2044240888")
        self.assertIsNotNone(sv)
        self.assertEqual((sv.ho_ten, sv.lop, sv.gpa, sv.diem_ren_luyen), ("Lê Văn Cường", "DHKL16A", 3.4, 80.0))
        self.assertEqual(QuanLySinhVien(self.duong_dan).so_luong(), 9)  # đã ghi vào file

    def test_them_huy_giua_chung(self):
        out = self.chay(self.menu.them_sinh_vien, "2044240888", "huy")
        self.assertIn("Đã hủy thao tác", out)
        self.assertFalse(self.ql.ton_tai("2044240888"))

    # ----- Sửa -----
    def test_sua_khong_tim_thay(self):
        out = self.chay(self.menu.sua_sinh_vien, "2044249999")
        self.assertIn("Không tìm thấy", out)

    def test_sua_ma_sai_dinh_dang_roi_nhap_lai(self):
        out = self.chay(self.menu.sua_sinh_vien, "abc", "2044249999")
        self.assertIn("10 chữ số", out)
        self.assertIn("Không tìm thấy", out)

    def test_sua_thanh_cong_giu_nguyen_khi_bam_enter(self):
        out = self.chay(self.menu.sua_sinh_vien, "2044240102", "", "", "3.3", "")
        self.assertIn("Đã cập nhật", out)
        sv = QuanLySinhVien(self.duong_dan).lay_theo_ma("2044240102")
        self.assertEqual(sv.gpa, 3.3)
        self.assertEqual(sv.ho_ten, "Lê Hoàng Nam")      # giữ nguyên
        self.assertEqual(sv.diem_ren_luyen, 78.0)         # giữ nguyên

    def test_sua_nhap_sai_phai_nhap_lai(self):
        out = self.chay(self.menu.sua_sinh_vien, "2044240102", "", "", "9", "3.1", "")
        self.assertIn("0 đến 4.0", out)
        self.assertEqual(self.ql.lay_theo_ma("2044240102").gpa, 3.1)

    # ----- Xóa -----
    def test_xoa_khong_tim_thay(self):
        out = self.chay(self.menu.xoa_sinh_vien, "2044249999")
        self.assertIn("Không tìm thấy", out)
        self.assertEqual(self.ql.so_luong(), 8)

    def test_xoa_khong_dong_y(self):
        out = self.chay(self.menu.xoa_sinh_vien, "2044240102", "n")
        self.assertIn("Đã hủy xóa", out)
        self.assertTrue(self.ql.ton_tai("2044240102"))

    def test_xoa_dong_y(self):
        out = self.chay(self.menu.xoa_sinh_vien, "2044240102", "y")
        self.assertIn("Đã xóa", out)
        self.assertFalse(QuanLySinhVien(self.duong_dan).ton_tai("2044240102"))

    def test_xoa_nhap_xac_nhan_sai_phai_hoi_lai(self):
        out = self.chay(self.menu.xoa_sinh_vien, "2044240102", "abc", "y")
        self.assertIn("y (đồng ý) hoặc n", out)
        self.assertFalse(self.ql.ton_tai("2044240102"))

    def test_xoa_bi_chan_vi_con_ho_so(self):
        out = self.chay(self.menu.xoa_sinh_vien, MA_CO_HO_SO)
        self.assertIn("hồ sơ học bổng", out)
        self.assertTrue(self.ql.ton_tai(MA_CO_HO_SO))

    # ----- Tìm kiếm -----
    def test_tim_khong_thay(self):
        out = self.chay(self.menu.tim_kiem_sinh_vien, "2", "9999999999", "n")
        self.assertIn("Không tìm thấy", out)

    def test_tim_theo_lop_va_ten(self):
        out = self.chay(self.menu.tim_kiem_sinh_vien, "4", "dhkl16c", "n")
        self.assertIn("Đặng Khánh Linh", out)
        self.assertIn("Tổng: 3 sinh viên", out)
        out = self.chay(self.menu.tim_kiem_sinh_vien, "3", "phuong", "n")   # không dấu
        self.assertIn("Nguyễn Thị Đông Phương", out)

    def test_tim_gan_dung(self):
        out = self.chay(self.menu.tim_kiem_sinh_vien, "3", "Nguyen Thi Dong Phuog", "y")
        self.assertIn("Nguyễn Thị Đông Phương", out)

    def test_tim_tu_khoa_rong_bi_tu_choi(self):
        out = self.chay(self.menu.tim_kiem_sinh_vien, "2", "", "2044240275", "n")
        self.assertIn("Từ khóa không được để trống", out)
        self.assertIn("2044240275", out)

    def test_tim_tieu_chi_sai(self):
        out = self.chay(self.menu.tim_kiem_sinh_vien, "9")
        self.assertIn("không hợp lệ", out)

    # ----- Hiển thị -----
    def test_xem_danh_sach_va_chi_tiet(self):
        out = self.chay(self.menu.xem_danh_sach)
        self.assertIn("Tổng: 8 sinh viên", out)
        out = self.chay(self.menu.xem_chi_tiet, "2044240275")
        self.assertIn("Nguyễn Thị Đông Phương", out)
        out = self.chay(self.menu.xem_chi_tiet, "2044249999")
        self.assertIn("Không tìm thấy", out)

    def test_danh_sach_trong(self):
        ql = QuanLySinhVien(os.path.join(self.thu_muc, "rong.json"))
        out = self.chay(MenuSinhVien(ql, kiem_tra_rang_buoc=lambda ma: False).xem_danh_sach)
        self.assertIn("đang trống", out)

    def test_sap_xep(self):
        out = self.chay(self.menu.sap_xep_danh_sach, "4", "2")
        self.assertLess(out.index("Trần Minh Anh"), out.index("Võ Quốc Bảo"))  # GPA giảm dần
        out = self.chay(self.menu.sap_xep_danh_sach, "9")
        self.assertIn("không hợp lệ", out)

    # ----- Vòng lặp menu -----
    def test_menu_chon_sai_roi_thoat(self):
        out = self.chay(self.menu.chay, "9", "abc", "0")
        self.assertEqual(out.count("không hợp lệ"), 2)


class TestRangBuocHoSo(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    def ghi(self, noi_dung, ten="ho_so.json"):
        duong_dan = os.path.join(self.thu_muc, ten)
        with open(duong_dan, "w", encoding="utf-8") as f:
            f.write(noi_dung if isinstance(noi_dung, str) else json.dumps(noi_dung))
        return duong_dan

    def test_co_ho_so_cac_dang_khoa(self):
        dd = self.ghi([{"ma_sv": "2044240101"}, {"ma_sinh_vien": "2044240203"},
                       {"sinh_vien": {"ma_sv": "2044240305"}}, {"sinh_vien": "2044240306"}])
        for ma in ("2044240101", "2044240203", "2044240305", "2044240306"):
            self.assertTrue(sinh_vien_co_ho_so(ma, dd), ma)
        self.assertFalse(sinh_vien_co_ho_so("2044240999", dd))

    def test_file_chua_co_hoac_rong(self):
        self.assertFalse(sinh_vien_co_ho_so("2044240101", os.path.join(self.thu_muc, "khong_co.json")))
        self.assertFalse(sinh_vien_co_ho_so("2044240101", self.ghi("")))


if __name__ == "__main__":
    unittest.main()
