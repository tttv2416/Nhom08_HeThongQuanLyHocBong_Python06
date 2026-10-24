"""Kiểm thử giao diện Tkinter sinh viên (cần có màn hình; tự bỏ qua nếu không có Tkinter/display).

Chạy từ thư mục gốc project:  python -m unittest discover -s tests -t . -v
(Trên Linux không màn hình: xvfb-run -a python -m unittest discover -s tests -t . -v)
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from services.quan_ly_sinh_vien import QuanLySinhVien
from tests.test_sinh_vien import tao_file_mau

try:
    import tkinter as tk
    from ui import giao_dien_sinh_vien as gd
    _goc = tk.Tk()
    _goc.destroy()
    CO_MAN_HINH = True
except Exception:  # không có tkinter hoặc không có display
    CO_MAN_HINH = False

MA_CO_HO_SO = "2044240101"


@unittest.skipUnless(CO_MAN_HINH, "Không có Tkinter hoặc màn hình hiển thị")
class TestGiaoDienSinhVien(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.duong_dan = tao_file_mau(self.thu_muc)
        self.goc = tk.Tk()
        self.goc.withdraw()
        self.ql = QuanLySinhVien(self.duong_dan)
        self.khung = gd.SinhVienFrame(self.goc, self.ql, kiem_tra_rang_buoc=lambda ma: ma == MA_CO_HO_SO)
        self.khung.grid()
        self.mb = patch.object(gd, "messagebox").start()
        self.mb.askyesno.return_value = True

    def tearDown(self):
        patch.stopall()
        self.goc.destroy()
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    # --- tiện ích ---
    def dien(self, ma="", ten="", lop="", gpa="", drl=""):
        for khoa, gia_tri in zip(("ma_sv", "ho_ten", "lop", "gpa", "drl"), (ma, ten, lop, gpa, drl)):
            self.khung.bien[khoa].set(gia_tri)

    def chon(self, ma):
        self.khung.bang.selection_set(ma)
        self.khung._chon_dong()

    def so_dong(self):
        return len(self.khung.bang.get_children())

    def dong_dau(self):
        return self.khung.bang.get_children()[0]

    # --- hiển thị ---
    def test_hien_thi_khi_khoi_dong(self):
        self.assertEqual(self.so_dong(), 8)
        self.assertIn("8 / 8", self.khung.var_trang_thai.get())
        self.assertIn("DHKL16A", self.khung.cb_loc_lop["values"])

    def test_chon_dong_do_form_va_progressbar(self):
        self.chon("2044240275")
        self.assertEqual(self.khung.bien["ho_ten"].get(), "Nguyễn Thị Đông Phương")
        self.assertEqual(str(self.khung.o_nhap["ma_sv"].cget("state")), "readonly")
        self.assertAlmostEqual(float(self.khung.pb_gpa["value"]), 3.45)
        self.assertAlmostEqual(float(self.khung.pb_drl["value"]), 88.0)
        self.assertTrue(self.khung.nut_sua.instate(["!disabled"]))
        self.assertTrue(self.khung.nut_them.instate(["disabled"]))

    def test_lam_moi_form(self):
        self.chon("2044240275")
        self.khung.lam_moi_form()
        self.assertEqual(self.khung.bien["ma_sv"].get(), "")
        self.assertEqual(str(self.khung.o_nhap["ma_sv"].cget("state")), "normal")
        self.assertTrue(self.khung.nut_them.instate(["!disabled"]))
        self.assertTrue(self.khung.nut_xoa.instate(["disabled"]))

    # --- thêm ---
    def test_them_hop_le(self):
        self.dien("2044240888", "lê văn cường", "dhkl16a", "3.4", "80")
        self.khung.them()
        self.mb.showinfo.assert_called()
        self.assertEqual(self.so_dong(), 9)
        self.assertEqual(QuanLySinhVien(self.duong_dan).so_luong(), 9)

    def test_them_nhap_sai(self):
        sai = [("123", "An Bình", "L1", "3", "80"), ("2044240888", "An", "L1", "3", "80"),
               ("2044240888", "An Bình", "", "3", "80"), ("2044240888", "An Bình", "L1", "5", "80"),
               ("2044240888", "An Bình", "L1", "abc", "80"), ("2044240888", "An Bình", "L1", "3", "101")]
        for gia_tri in sai:
            with self.subTest(gia_tri=gia_tri):
                self.mb.showerror.reset_mock()
                self.dien(*gia_tri)
                self.khung.them()
                self.mb.showerror.assert_called_once()
                self.assertEqual(self.so_dong(), 8)

    def test_them_trung_ma(self):
        self.dien("2044240275", "An Bình", "L1", "3", "80")
        self.khung.them()
        self.assertIn("đã tồn tại", self.mb.showerror.call_args[0][1])
        self.assertEqual(self.so_dong(), 8)

    # --- sửa ---
    def test_cap_nhat_thanh_cong(self):
        self.chon("2044240102")
        self.khung.bien["gpa"].set("3.3")
        self.khung.cap_nhat()
        self.mb.showinfo.assert_called()
        self.assertEqual(QuanLySinhVien(self.duong_dan).lay_theo_ma("2044240102").gpa, 3.3)

    def test_cap_nhat_chua_chon(self):
        self.khung.cap_nhat()
        self.mb.showwarning.assert_called_once()

    def test_cap_nhat_du_lieu_sai(self):
        self.chon("2044240102")
        self.khung.bien["gpa"].set("9")
        self.khung.cap_nhat()
        self.mb.showerror.assert_called_once()
        self.assertEqual(QuanLySinhVien(self.duong_dan).lay_theo_ma("2044240102").gpa, 2.9)

    # --- xóa ---
    def test_xoa_chua_chon(self):
        self.khung.xoa()
        self.mb.showwarning.assert_called_once()
        self.mb.askyesno.assert_not_called()

    def test_xoa_dong_y(self):
        self.chon("2044240102")
        self.khung.xoa()
        self.mb.askyesno.assert_called_once()
        self.assertEqual(self.so_dong(), 7)
        self.assertFalse(QuanLySinhVien(self.duong_dan).ton_tai("2044240102"))

    def test_xoa_khong_dong_y(self):
        self.mb.askyesno.return_value = False
        self.chon("2044240102")
        self.khung.xoa()
        self.assertEqual(self.so_dong(), 8)

    def test_xoa_bi_chan_boi_rang_buoc(self):
        self.chon(MA_CO_HO_SO)
        self.khung.xoa()
        self.mb.showwarning.assert_called_once()
        self.mb.askyesno.assert_not_called()
        self.assertEqual(self.so_dong(), 8)

    # --- tìm kiếm / lọc / sắp xếp ---
    def test_tim_kiem(self):
        self.khung.var_tu_khoa.set("phuong")
        self.khung.tim_kiem()
        self.assertEqual(self.so_dong(), 1)
        self.mb.showinfo.assert_not_called()

    def test_tim_theo_tieu_chi_lop(self):
        self.khung.var_tieu_chi.set("Lớp")
        self.khung.var_tu_khoa.set("DHKL16C")
        self.khung.tim_kiem()
        self.assertEqual(self.so_dong(), 3)

    def test_tim_khong_thay(self):
        self.khung.var_tu_khoa.set("zzzz")
        self.khung.tim_kiem()
        self.assertEqual(self.so_dong(), 0)
        self.mb.showinfo.assert_called_once()

    def test_tim_gan_dung(self):
        self.khung.var_tieu_chi.set("Họ tên")
        self.khung.var_tu_khoa.set("Nguyen Thi Dong Phuog")
        self.khung.var_gan_dung.set(True)
        self.khung.tim_kiem()
        self.assertEqual(self.so_dong(), 1)

    def test_loc_lop_va_hien_tat_ca(self):
        self.khung.var_loc_lop.set("DHKL16B")
        self.khung.hien_thi()
        self.assertEqual(self.so_dong(), 2)
        self.khung.hien_tat_ca()
        self.assertEqual(self.so_dong(), 8)

    def test_sap_xep_bam_tieu_de(self):
        self.khung.sap_xep_theo_cot("gpa")
        self.assertEqual(self.dong_dau(), "2044240204")  # GPA thấp nhất
        self.assertIn("▲", self.khung.bang.heading("gpa", "text"))
        self.khung.sap_xep_theo_cot("gpa")
        self.assertEqual(self.dong_dau(), "2044240101")  # GPA cao nhất
        self.assertIn("▼", self.khung.bang.heading("gpa", "text"))
        self.assertNotIn("▲", self.khung.bang.heading("ma_sv", "text"))

    # --- phân quyền ---
    def test_nguoi_dung_thuong_khong_duoc_sua(self):
        self.khung.dat_quyen_chinh_sua(False)
        self.assertTrue(self.khung.nut_them.instate(["disabled"]))
        self.dien("2044240888", "An Bình", "L1", "3", "80")
        self.khung.them()
        self.mb.showwarning.assert_called_once()
        self.assertEqual(self.so_dong(), 8)
        self.khung.dat_quyen_chinh_sua(True)
        self.assertTrue(self.khung.nut_them.instate(["!disabled"]))

    # --- file ---
    def test_tai_lai_khi_file_hong_giu_du_lieu_cu(self):
        with open(self.duong_dan, "w", encoding="utf-8") as f:
            f.write("{bad")
        self.khung.lam_moi_du_lieu()
        self.mb.showerror.assert_called_once()
        self.assertEqual(self.ql.so_luong(), 8)
        self.assertEqual(self.so_dong(), 8)

    def test_khong_tron_pack_va_grid(self):
        duong_dan = os.path.join(os.path.dirname(gd.__file__), "giao_dien_sinh_vien.py")
        with open(duong_dan, encoding="utf-8") as f:
            ma_nguon = f.read()
        self.assertNotIn(".pack(", ma_nguon)


if __name__ == "__main__":
    unittest.main()
