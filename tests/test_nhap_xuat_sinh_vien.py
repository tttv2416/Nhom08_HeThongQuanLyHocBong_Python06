"""Kiểm thử nhập/xuất sinh viên từ file CSV, JSON (hợp lệ, sai, trùng mã, file lỗi).

Chạy từ thư mục gốc project:  python -m unittest discover -s tests -t . -v
"""

import csv
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from config import DATA_DIR
from services.luu_tru_json import LoiFileError
from services.nhap_xuat_sinh_vien import doc_file, xuat_file
from services.quan_ly_sinh_vien import QuanLySinhVien
from tests.test_sinh_vien import tao_file_mau
from ui.menu_sinh_vien import MenuSinhVien

CSV_MAU = os.path.join(DATA_DIR, "sinh_vien_nhap_mau.csv")
JSON_MAU = os.path.join(DATA_DIR, "sinh_vien_nhap_mau.json")


class TestNhapXuat(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.duong_dan = tao_file_mau(self.thu_muc)
        self.ql = QuanLySinhVien(self.duong_dan)

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    def ghi(self, ten, noi_dung, ma_hoa="utf-8"):
        dd = os.path.join(self.thu_muc, ten)
        with open(dd, "wb") as f:
            f.write(noi_dung.encode(ma_hoa) if isinstance(noi_dung, str) else noi_dung)
        return dd

    # ----- đọc file mẫu của project -----
    def test_nhap_csv_mau(self):
        ket_qua = self.ql.nhap_hang_loat(doc_file(CSV_MAU))
        self.assertEqual(ket_qua.them, 5)           # 5 dòng hợp lệ
        self.assertEqual(len(ket_qua.bo_qua), 3)    # trùng mã, mã sai, GPA sai
        self.assertIn("đã tồn tại", "\n".join(ket_qua.bo_qua))
        self.assertIn("10 chữ số", "\n".join(ket_qua.bo_qua))
        self.assertIn("0 đến 4.0", "\n".join(ket_qua.bo_qua))
        self.assertEqual(QuanLySinhVien(self.duong_dan).so_luong(), 13)  # đã ghi file

    def test_nhap_json_mau(self):
        ket_qua = self.ql.nhap_hang_loat(doc_file(JSON_MAU))
        self.assertEqual(ket_qua.them, 3)
        self.assertEqual(len(ket_qua.bo_qua), 1)
        self.assertIn("Thiếu trường", ket_qua.bo_qua[0])

    # ----- ghi đè khi trùng -----
    def test_ghi_de_cap_nhat_thay_vi_bo_qua(self):
        dd = self.ghi("a.csv", "ma_sv,ho_ten,lop,gpa,diem_ren_luyen\n2044240275,Nguyễn Thị Đông Phương,DHKL16B,3.9,99\n")
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd), ghi_de=True)
        self.assertEqual((ket_qua.them, ket_qua.cap_nhat, len(ket_qua.bo_qua)), (0, 1, 0))
        self.assertEqual(self.ql.lay_theo_ma("2044240275").gpa, 3.9)
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd), ghi_de=False)
        self.assertEqual((ket_qua.them, ket_qua.cap_nhat, len(ket_qua.bo_qua)), (0, 0, 1))

    # ----- định dạng CSV -----
    def test_csv_cham_phay_bom_va_ten_cot_khac(self):
        # Excel Việt Nam: dấu chấm phẩy, có BOM, tên cột kiểu MSSV/ĐRL, GPA dùng dấu phẩy thập phân
        noi_dung = "MSSV;Họ và tên;Lớp;GPA;ĐRL\n2044240601;Lê Văn Tám;DHKL16F;3,45;88\n"
        dd = self.ghi("b.csv", noi_dung, "utf-8-sig")
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd))
        self.assertEqual(ket_qua.them, 1)
        self.assertEqual(self.ql.lay_theo_ma("2044240601").gpa, 3.45)

    def test_csv_bo_dong_trong_va_bao_dung_so_dong(self):
        noi_dung = ("ma_sv,ho_ten,lop,gpa,diem_ren_luyen\n"
                    "2044240601,Lê Văn Tám,DHKL16F,3.4,88\n"
                    ",,,,\n\n"
                    "abc,Lê Văn Bảy,DHKL16F,3.4,88\n")
        ket_qua = self.ql.nhap_hang_loat(doc_file(self.ghi("c.csv", noi_dung)))
        self.assertEqual(ket_qua.them, 1)
        self.assertTrue(ket_qua.bo_qua[0].startswith("Dòng 5:"))

    def test_csv_thieu_cot(self):
        dd = self.ghi("d.csv", "ma_sv,ho_ten,lop\n2044240601,Lê Văn Tám,DHKL16F\n")
        with self.assertRaises(LoiFileError) as ctx:
            doc_file(dd)
        self.assertIn("thiếu cột", str(ctx.exception))

    def test_csv_dong_thieu_o(self):
        dd = self.ghi("e.csv", "ma_sv,ho_ten,lop,gpa,diem_ren_luyen\n2044240601,Lê Văn Tám,DHKL16F\n")
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd))
        self.assertEqual(ket_qua.them, 0)
        self.assertEqual(len(ket_qua.bo_qua), 1)

    # ----- file lỗi -----
    def test_file_loi(self):
        sai = [
            os.path.join(self.thu_muc, "khong_co.csv"),                    # không tồn tại
            self.ghi("f.csv", ""),                                         # rỗng
            self.ghi("g.json", "{bad"),                                    # JSON hỏng
            self.ghi("h.json", '{"a": 1}'),                                # không phải danh sách
            self.ghi("i.csv", b"\xff\xfe\x00ma_sv\n"),                     # không phải UTF-8
            self.ghi("j.txt", "abc"),                                      # sai đuôi
            self.thu_muc,                                                  # là thư mục
        ]
        for dd in sai:
            with self.subTest(dd=os.path.basename(dd)):
                with self.assertRaises(LoiFileError):
                    doc_file(dd)

    def test_json_dang_bao_boc_va_ban_ghi_khong_phai_dict(self):
        dd = self.ghi("k.json", json.dumps({"sinh_vien": [
            {"Mã SV": "2044240701", "Họ tên": "Ngô Văn Chín", "Lớp": "DHKL16G", "GPA": 3.1, "ĐRL": 80}, 5]}))
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd))
        self.assertEqual(ket_qua.them, 1)
        self.assertEqual(len(ket_qua.bo_qua), 1)

    def test_nhap_file_rong_khong_ghi_file_du_lieu(self):
        dd = self.ghi("l.json", "[]")
        thoi_gian = os.path.getmtime(self.duong_dan)
        ket_qua = self.ql.nhap_hang_loat(doc_file(dd))
        self.assertEqual((ket_qua.them, ket_qua.cap_nhat), (0, 0))
        self.assertEqual(os.path.getmtime(self.duong_dan), thoi_gian)

    def test_hoan_tac_khi_ghi_file_loi(self):
        with patch.object(QuanLySinhVien, "luu", side_effect=LoiFileError("lỗi ghi")):
            with self.assertRaises(LoiFileError):
                self.ql.nhap_hang_loat(doc_file(CSV_MAU))
        self.assertEqual(self.ql.so_luong(), 8)  # không thêm sót bản ghi nào

    # ----- xuất file -----
    def test_xuat_csv_va_doc_lai(self):
        dd = os.path.join(self.thu_muc, "ra", "ds.csv")  # thư mục "ra" chưa có -> tự tạo
        xuat_file(self.ql.sap_xep("ma_sv"), dd)
        with open(dd, "rb") as f:
            self.assertTrue(f.read().startswith(b"\xef\xbb\xbf"))  # BOM cho Excel
        with open(dd, encoding="utf-8-sig", newline="") as f:
            hang = list(csv.reader(f))
        self.assertEqual(hang[0][0], "Mã sinh viên")
        self.assertEqual(len(hang), 9)
        ql2 = QuanLySinhVien(os.path.join(self.thu_muc, "moi.json"))
        ket_qua = ql2.nhap_hang_loat(doc_file(dd))   # xuất rồi nhập lại phải khớp
        self.assertEqual(ket_qua.them, 8)
        self.assertEqual(ql2.lay_theo_ma("2044240275").ho_ten, "Nguyễn Thị Đông Phương")

    def test_xuat_json_va_doc_lai(self):
        dd = os.path.join(self.thu_muc, "ds.json")
        xuat_file(self.ql.danh_sach(), dd)
        ql2 = QuanLySinhVien(os.path.join(self.thu_muc, "moi.json"))
        self.assertEqual(ql2.nhap_hang_loat(doc_file(dd)).them, 8)

    def test_xuat_sai_duoi_hoac_khong_ghi_duoc(self):
        with self.assertRaises(LoiFileError):
            xuat_file(self.ql.danh_sach(), os.path.join(self.thu_muc, "ds.xlsx"))
        with self.assertRaises(LoiFileError):
            # đường dẫn đi qua một file (không phải thư mục) -> không ghi được
            xuat_file(self.ql.danh_sach(), os.path.join(self.duong_dan, "ds.csv"))


class TestMenuNhapXuat(unittest.TestCase):
    def setUp(self):
        self.thu_muc = tempfile.mkdtemp()
        self.ql = QuanLySinhVien(tao_file_mau(self.thu_muc))
        self.menu = MenuSinhVien(self.ql, kiem_tra_rang_buoc=lambda ma: False)

    def tearDown(self):
        shutil.rmtree(self.thu_muc, ignore_errors=True)

    def chay(self, ham, *nhap):
        with patch("builtins.input", side_effect=list(nhap)), redirect_stdout(io.StringIO()) as out:
            ham()
        return out.getvalue()

    def test_nhap_tu_file(self):
        out = self.chay(self.menu.nhap_tu_file, f'"{CSV_MAU}"', "n")
        self.assertIn("Đã thêm: 5", out)
        self.assertIn("Bỏ qua: 3", out)
        self.assertEqual(self.ql.so_luong(), 13)

    def test_nhap_file_khong_ton_tai_va_sai_duoi(self):
        self.assertIn("Không tìm thấy file", self.chay(self.menu.nhap_tu_file, "khong_co.csv"))
        self.assertIn("Chỉ hỗ trợ", self.chay(self.menu.nhap_tu_file, "a.txt"))
        self.assertEqual(self.ql.so_luong(), 8)

    def test_xuat_ra_file(self):
        dd = os.path.join(self.thu_muc, "ra.csv")
        out = self.chay(self.menu.xuat_ra_file, dd)
        self.assertIn("Đã xuất 8 sinh viên", out)
        self.assertTrue(os.path.exists(dd))
        self.assertIn("Chỉ hỗ trợ", self.chay(self.menu.xuat_ra_file, os.path.join(self.thu_muc, "ra.xlsx")))


if __name__ == "__main__":
    unittest.main()
