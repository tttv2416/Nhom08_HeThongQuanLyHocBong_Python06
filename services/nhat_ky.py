"""Module services/nhat_ky.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Nhật ký thao tác: ghi lại ai đã thêm/sửa/xóa/nhập file sinh viên, vào lúc nào.
Mỗi thao tác là một dòng trong file data/nhat_ky.log, các cột cách nhau bằng " | ":

    2026-10-25 13:05:12 | admin | THEM | 2044240888 | Nguyễn Văn An - DHKL16A - GPA 3.50 - ĐRL 88.0

Ghi nhật ký bị lỗi (ví dụ file bị khóa) không được làm hỏng thao tác chính,
nên ghi() không ném ngoại lệ mà chỉ trả về False.
"""

import os
from datetime import datetime

from services.luu_tru_json import LoiFileError

DINH_DANG_THOI_GIAN = "%Y-%m-%d %H:%M:%S"
CAC_COT = ("thoi_gian", "nguoi_dung", "hanh_dong", "ma_sv", "chi_tiet")
NHAN_HANH_DONG = {
    "THEM": "Thêm",
    "SUA": "Sửa",
    "XOA": "Xóa",
    "NHAP_FILE": "Nhập file",
}


def _lam_sach(text):
    """Bỏ ký tự xuống dòng và dấu '|' để mỗi thao tác luôn nằm trên đúng một dòng."""
    return " ".join(str(text).replace("|", "/").split())


class NhatKy:
    """Ghi và đọc file nhật ký thao tác."""

    def __init__(self, duong_dan):
        self.duong_dan = duong_dan

    def ghi(self, nguoi_dung, hanh_dong, ma_sv="-", chi_tiet=""):
        """Thêm một dòng vào cuối file nhật ký. Trả về True nếu ghi được."""
        dong = " | ".join((
            datetime.now().strftime(DINH_DANG_THOI_GIAN),
            _lam_sach(nguoi_dung) or "?",
            _lam_sach(hanh_dong) or "?",
            _lam_sach(ma_sv) or "-",
            _lam_sach(chi_tiet),
        ))
        try:
            thu_muc = os.path.dirname(self.duong_dan)
            if thu_muc:
                os.makedirs(thu_muc, exist_ok=True)
            with open(self.duong_dan, "a", encoding="utf-8") as f:
                f.write(dong + "\n")
            return True
        except OSError:
            return False

    def doc_gan_day(self, so_dong=200):
        """Trả về tối đa so_dong thao tác gần nhất (mới nhất đứng đầu), mỗi phần tử là dict
        có các khóa: thoi_gian, nguoi_dung, hanh_dong, ma_sv, chi_tiet. File chưa có -> []."""
        if not os.path.exists(self.duong_dan):
            return []
        try:
            with open(self.duong_dan, "r", encoding="utf-8", errors="replace") as f:
                cac_dong = f.read().splitlines()
        except PermissionError:
            raise LoiFileError(f"Không có quyền đọc file nhật ký '{self.duong_dan}'.") from None
        except OSError as e:
            raise LoiFileError(f"Không thể đọc file nhật ký '{self.duong_dan}': {e}") from e

        ket_qua = []
        for dong in reversed(cac_dong):
            if not dong.strip():
                continue
            phan = dong.split(" | ", 4)
            phan += [""] * (len(CAC_COT) - len(phan))  # dòng thiếu cột vẫn hiển thị được
            ket_qua.append(dict(zip(CAC_COT, phan)))
            if len(ket_qua) >= so_dong:
                break
        return ket_qua
