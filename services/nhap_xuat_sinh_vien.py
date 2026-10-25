"""Module services/nhap_xuat_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Đọc danh sách sinh viên từ file CSV/JSON (để nhập hàng loạt) và xuất danh sách ra CSV/JSON.

- CSV: UTF-8 (có hoặc không BOM), phân tách bằng dấu phẩy hoặc chấm phẩy (Excel Việt Nam),
  dòng đầu là tiêu đề: Mã sinh viên, Họ và tên, Lớp, GPA, Điểm rèn luyện
  (cũng nhận tên cột kiểu ma_sv, ho_ten, lop, gpa, diem_ren_luyen, MSSV, ĐRL...).
- JSON: danh sách các đối tượng [{"ma_sv": ..., "ho_ten": ..., ...}, ...].
"""

import csv
import io
import json
import os

from services.luu_tru_json import LoiFileError
from services.quan_ly_sinh_vien import bo_dau

CAC_COT = ("ma_sv", "ho_ten", "lop", "gpa", "diem_ren_luyen")
TIEU_DE_XUAT = ("Mã sinh viên", "Họ và tên", "Lớp", "GPA", "Điểm rèn luyện")

# tên cột đã chuẩn hóa (bỏ dấu, chữ thường, bỏ khoảng trắng/ký tự đặc biệt) -> cột chuẩn
BI_DANH = {
    "ma_sv": {"masv", "masinhvien", "mssv", "ma"},
    "ho_ten": {"hoten", "hovaten", "tensinhvien", "hotensinhvien", "ten"},
    "lop": {"lop", "tenlop", "malop"},
    "gpa": {"gpa", "diemgpa", "diemtichluy"},
    "diem_ren_luyen": {"diemrenluyen", "drl", "diemrl", "renluyen"},
}
HUONG_DAN_COT = "Cần có các cột: Mã sinh viên, Họ và tên, Lớp, GPA, Điểm rèn luyện."


def _chuan_khoa(ten):
    return "".join(c for c in bo_dau(ten) if c.isalnum())


def _cot_chuan(ten):
    """Đổi tên cột bất kỳ về tên cột chuẩn; không nhận ra -> None."""
    khoa = _chuan_khoa(ten)
    for chuan, bi_danh in BI_DANH.items():
        if khoa == _chuan_khoa(chuan) or khoa in bi_danh:
            return chuan
    return None


def _doc_noi_dung(duong_dan, kieu):
    """Đọc toàn bộ file văn bản UTF-8, đổi mọi lỗi hệ thống thành LoiFileError dễ hiểu."""
    try:
        with open(duong_dan, "r", encoding="utf-8-sig", newline="") as f:
            return f.read()
    except FileNotFoundError:
        raise LoiFileError(f"Không tìm thấy file '{duong_dan}'.") from None
    except PermissionError:
        raise LoiFileError(f"Không có quyền đọc file '{duong_dan}'.") from None
    except IsADirectoryError:
        raise LoiFileError(f"'{duong_dan}' là thư mục, hãy chọn một file {kieu}.") from None
    except UnicodeDecodeError:
        raise LoiFileError(
            f"File {kieu} phải lưu bằng mã hóa UTF-8 "
            f"(trong Excel: Save As -> CSV UTF-8).") from None
    except OSError as e:
        raise LoiFileError(f"Không thể đọc file '{duong_dan}': {e}") from e


def _doc_csv(duong_dan):
    noi_dung = _doc_noi_dung(duong_dan, "CSV")
    if not noi_dung.strip():
        raise LoiFileError("File CSV rỗng. " + HUONG_DAN_COT)
    dong_dau = noi_dung.splitlines()[0]
    dau_phan_cach = ";" if dong_dau.count(";") > dong_dau.count(",") else ","
    try:
        cac_hang = list(csv.reader(io.StringIO(noi_dung), delimiter=dau_phan_cach))
    except csv.Error as e:
        raise LoiFileError(f"File CSV sai định dạng: {e}") from e

    vi_tri = {}
    for i, ten in enumerate(cac_hang[0]):
        chuan = _cot_chuan(ten)
        if chuan and chuan not in vi_tri:
            vi_tri[chuan] = i
    thieu = [c for c in CAC_COT if c not in vi_tri]
    if thieu:
        raise LoiFileError(f"File CSV thiếu cột: {', '.join(thieu)}. " + HUONG_DAN_COT)

    ket_qua = []
    for so_dong, hang in enumerate(cac_hang[1:], start=2):
        if not any(o.strip() for o in hang):
            continue  # bỏ dòng trống
        ban_ghi = {c: (hang[vi_tri[c]].strip() if vi_tri[c] < len(hang) else "") for c in CAC_COT}
        ban_ghi["_dong"] = so_dong
        ket_qua.append(ban_ghi)
    return ket_qua


def _doc_json(duong_dan):
    noi_dung = _doc_noi_dung(duong_dan, "JSON")
    try:
        du_lieu = json.loads(noi_dung)
    except json.JSONDecodeError as e:
        raise LoiFileError(f"File JSON sai định dạng (dòng {e.lineno}): {e.msg}.") from e
    if isinstance(du_lieu, dict) and isinstance(du_lieu.get("sinh_vien"), list):
        du_lieu = du_lieu["sinh_vien"]
    if not isinstance(du_lieu, list):
        raise LoiFileError('File JSON phải chứa một danh sách sinh viên: [ {...}, {...} ].')

    ket_qua = []
    for i, d in enumerate(du_lieu, start=1):
        if isinstance(d, dict):
            ban_ghi = {}
            for khoa, gia_tri in d.items():
                ban_ghi[_cot_chuan(khoa) or khoa] = gia_tri
            ban_ghi["_dong"] = i
            ket_qua.append(ban_ghi)
        else:
            ket_qua.append(d)  # sẽ được báo lỗi ở bước nhập
    return ket_qua


def doc_file(duong_dan):
    """Đọc file .csv hoặc .json thành list các dict (có khóa '_dong' = số dòng/thứ tự trong file)."""
    duong_dan = str(duong_dan).strip().strip('"')
    duoi = os.path.splitext(duong_dan)[1].lower()
    if duoi == ".csv":
        return _doc_csv(duong_dan)
    if duoi == ".json":
        return _doc_json(duong_dan)
    raise LoiFileError("Chỉ hỗ trợ file .csv hoặc .json.")


# ---------------------------------------------------------------------------
# Xuất file
# ---------------------------------------------------------------------------
def _tao_thu_muc(duong_dan):
    thu_muc = os.path.dirname(duong_dan)
    if thu_muc:
        os.makedirs(thu_muc, exist_ok=True)


def xuat_csv(ds, duong_dan):
    """Xuất danh sách SinhVien ra CSV UTF-8 (có BOM để Excel mở đúng tiếng Việt)."""
    try:
        _tao_thu_muc(duong_dan)
        with open(duong_dan, "w", encoding="utf-8-sig", newline="") as f:
            ghi = csv.writer(f)
            ghi.writerow(TIEU_DE_XUAT)
            for sv in ds:
                ghi.writerow([sv.ma_sv, sv.ho_ten, sv.lop, f"{sv.gpa:.2f}", f"{sv.diem_ren_luyen:.1f}"])
    except PermissionError:
        raise LoiFileError(f"Không có quyền ghi file '{duong_dan}'. Có thể file đang mở trong Excel.") from None
    except OSError as e:
        raise LoiFileError(f"Không thể ghi file '{duong_dan}': {e}") from e


def xuat_json(ds, duong_dan):
    """Xuất danh sách SinhVien ra JSON UTF-8."""
    try:
        _tao_thu_muc(duong_dan)
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump([sv.to_dict() for sv in ds], f, ensure_ascii=False, indent=4)
    except PermissionError:
        raise LoiFileError(f"Không có quyền ghi file '{duong_dan}'.") from None
    except OSError as e:
        raise LoiFileError(f"Không thể ghi file '{duong_dan}': {e}") from e


def xuat_file(ds, duong_dan):
    """Xuất theo đuôi file: .csv hoặc .json."""
    duong_dan = str(duong_dan).strip().strip('"')
    duoi = os.path.splitext(duong_dan)[1].lower()
    if duoi == ".csv":
        xuat_csv(ds, duong_dan)
    elif duoi == ".json":
        xuat_json(ds, duong_dan)
    else:
        raise LoiFileError("Chỉ hỗ trợ xuất ra file .csv hoặc .json.")
