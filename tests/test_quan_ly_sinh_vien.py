"""Test mục 2.3, 2.4, 2.5 và phần test nghiệp vụ (2.6): thêm, sửa, xóa, tìm, sắp xếp, lưu file."""
import json
import os
import unittest

from models.sinh_vien import DuLieuKhongHopLeError
from services.luu_tru_json import LoiFileError
from services.quan_ly_sinh_vien import QuanLySinhVien, bo_dau
from tests.helpers import ds_mau, file_tam, ql_mau


class TestThem(unittest.TestCase):
    def setUp(self):
        self.ql = ql_mau()

    def test_them_hop_le_va_ghi_file(self):
        self.ql.them("2044240999", "Võ Quốc Bảo", "dhkl16b", 3.1, 82)
        self.assertTrue(self.ql.ton_tai("2044240999"))
        self.assertEqual(self.ql.so_luong(), 4)
        # tải lại từ file: dữ liệu vẫn còn
        ql2 = QuanLySinhVien(self.ql._QuanLySinhVien__luu_tru.duong_dan)
        self.assertEqual(ql2.lay_theo_ma("2044240999").lop, "DHKL16B")

    def test_trung_ma(self):
        with self.assertRaises(DuLieuKhongHopLeError) as ctx:
            self.ql.them("2044240101", "Người Khác", "DHKL16A", 3.0, 80)
        self.assertIn("đã tồn tại", str(ctx.exception))
        self.assertEqual(self.ql.so_luong(), 3)  # không thêm rác

    def test_du_lieu_sai_khong_them(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.them("2044240999", "Võ Quốc Bảo", "DHKL16B", 5.0, 80)
        self.assertFalse(self.ql.ton_tai("2044240999"))

    def test_loi_ghi_file_hoan_tac(self):
        ql = ql_mau()
        duong_dan = ql._QuanLySinhVien__luu_tru.duong_dan
        # đặt đường dẫn vào thư mục không tồn tại và không tạo được -> lỗi ghi
        ql._QuanLySinhVien__luu_tru.duong_dan = os.path.join(duong_dan, "khong_ton_tai", "x.json")
        with self.assertRaises(LoiFileError):
            ql.them("2044240999", "Võ Quốc Bảo", "DHKL16B", 3.1, 82)
        self.assertFalse(ql.ton_tai("2044240999"))  # đã hoàn tác trong bộ nhớ


class TestSua(unittest.TestCase):
    def setUp(self):
        self.ql = ql_mau()

    def test_sua_giu_ma(self):
        moi = self.ql.sua("2044240101", "Trần Minh Anh", "DHKL16B", 3.5, 90)
        self.assertEqual(moi.ma_sv, "2044240101")
        self.assertEqual(moi.lop, "DHKL16B")
        self.assertEqual(self.ql.lay_theo_ma("2044240101").gpa, 3.5)

    def test_sua_sai_du_lieu_giu_nguyen(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.sua("2044240101", "Trần Minh Anh", "DHKL16B", 9, 90)
        self.assertEqual(self.ql.lay_theo_ma("2044240101").gpa, 3.82)

    def test_sua_ma_khong_ton_tai(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.sua("2044240000", "Trần Minh Anh", "DHKL16B", 3.5, 90)


class TestXoa(unittest.TestCase):
    def setUp(self):
        self.ql = ql_mau()

    def test_xoa_thanh_cong(self):
        self.ql.xoa("2044240102")
        self.assertFalse(self.ql.ton_tai("2044240102"))
        self.assertEqual(self.ql.so_luong(), 2)

    def test_xoa_bi_chan_khi_co_rang_buoc(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.xoa("2044240101", lambda ma: ma == "2044240101")
        self.assertTrue(self.ql.ton_tai("2044240101"))

    def test_xoa_khong_ton_tai(self):
        with self.assertRaises(DuLieuKhongHopLeError):
            self.ql.xoa("2044240000")


class TestTimKiem(unittest.TestCase):
    def setUp(self):
        self.ql = ql_mau()

    def ma(self, ds):
        return sorted(sv.ma_sv for sv in ds)

    def test_theo_ma(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("2044240102", "ma_sv")), ["2044240102"])

    def test_theo_ten_khong_dau(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("minh anh", "ho_ten")), ["2044240101"])

    def test_theo_ten_co_dau(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("Phạm Thu", "ho_ten")), ["2044240203"])

    def test_theo_lop_khong_phan_biet_hoa_thuong(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("dhkl16a", "lop")), ["2044240101", "2044240102"])

    def test_tat_ca_tieu_chi(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("2044240")), ["2044240101", "2044240102", "2044240203"])

    def test_khong_tim_thay(self):
        self.assertEqual(self.ql.tim_kiem("Không Có Ai"), [])

    def test_gan_dung(self):
        self.assertEqual(self.ma(self.ql.tim_kiem("tran minh anhh", "ho_ten", gan_dung=True)), ["2044240101"])
        self.assertEqual(self.ql.tim_kiem("tran minh anhh", "ho_ten", gan_dung=False), [])

    def test_tu_khoa_rong_tra_ve_tat_ca(self):
        self.assertEqual(len(self.ql.tim_kiem("   ")), 3)

    def test_tieu_chi_sai(self):
        with self.assertRaises(ValueError):
            self.ql.tim_kiem("x", "gpa")

    def test_bo_dau(self):
        self.assertEqual(bo_dau("Đặng Khánh"), "dang khanh")


class TestSapXepVaDanhSach(unittest.TestCase):
    def setUp(self):
        self.ql = ql_mau()

    def test_sap_theo_gpa_giam_dan(self):
        ds = self.ql.sap_xep("gpa", giam_dan=True)
        self.assertEqual([sv.ma_sv for sv in ds], ["2044240101", "2044240203", "2044240102"])

    def test_sap_theo_ten_theo_ten_cuoi(self):
        ds = self.ql.sap_xep("ho_ten")
        # sắp theo từ cuối của tên: Anh < Hà < Nam
        self.assertEqual([sv.ho_ten for sv in ds], ["Trần Minh Anh", "Phạm Thu Hà", "Lê Hoàng Nam"])

    def test_truong_sai(self):
        with self.assertRaises(ValueError):
            self.ql.sap_xep("mat_khau")

    def test_loc(self):
        ds = self.ql.loc(lop="dhkl16a", gpa_min=3.0)
        self.assertEqual([sv.ma_sv for sv in ds], ["2044240101"])


class TestLuuTru(unittest.TestCase):
    def test_file_chua_ton_tai_la_danh_sach_rong(self):
        ql = QuanLySinhVien(file_tam())
        self.assertEqual(ql.so_luong(), 0)

    def test_file_rong(self):
        ql = QuanLySinhVien(file_tam(""))
        self.assertEqual(ql.so_luong(), 0)

    def test_file_sai_cu_phap_bao_loi(self):
        with self.assertRaises(LoiFileError):
            QuanLySinhVien(file_tam("[{ma_sv: }"))

    def test_file_khong_phai_list(self):
        with self.assertRaises(LoiFileError):
            QuanLySinhVien(file_tam('{"ma_sv": "2044240101"}'))

    def test_ban_ghi_loi_bi_bo_qua_va_canh_bao(self):
        du_lieu = ds_mau() + [
            {"ma_sv": "2044240101", "ho_ten": "Trùng Mã", "lop": "DHKL16A", "gpa": 3, "diem_ren_luyen": 80},
            {"ma_sv": "2044240500", "ho_ten": "Sai GPA", "lop": "DHKL16A", "gpa": 9, "diem_ren_luyen": 80},
            {"ma_sv": "2044240600"},
        ]
        ql = QuanLySinhVien(file_tam(du_lieu))
        self.assertEqual(ql.so_luong(), 3)
        self.assertEqual(len(ql.loi_khi_tai), 3)

    def test_tao_file_bak_khi_ghi(self):
        path = file_tam(ds_mau())
        ql = QuanLySinhVien(path)
        ql.them("2044240999", "Võ Quốc Bảo", "DHKL16B", 3.1, 82)
        self.assertTrue(os.path.exists(path + ".bak"))
        with open(path, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)), 4)


if __name__ == "__main__":
    unittest.main()