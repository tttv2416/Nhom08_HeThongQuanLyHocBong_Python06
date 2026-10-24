"""Lớp xử lý file JSON dùng chung cho cả nhóm: đọc, ghi an toàn, sao lưu."""

import json
import os
import shutil


class LoiFileError(Exception):
    """Lỗi khi đọc/ghi file dữ liệu."""


class LuuTruJSON:
    """Đọc/ghi một file JSON chứa danh sách bản ghi (list các dict)."""

    def __init__(self, duong_dan):
        self.duong_dan = duong_dan

    def doc(self):
        """Trả về list các dict. File chưa có hoặc rỗng -> []."""
        if not os.path.exists(self.duong_dan):
            return []
        try:
            with open(self.duong_dan, "r", encoding="utf-8") as f:
                noi_dung = f.read().strip()
            if not noi_dung:
                return []
            data = json.loads(noi_dung)
        except json.JSONDecodeError as e:
            raise LoiFileError(
                f"File '{self.duong_dan}' sai định dạng JSON (dòng {e.lineno}). "
                f"Hãy sửa file hoặc khôi phục từ file .bak.") from e
        except PermissionError as e:
            raise LoiFileError(f"Không có quyền đọc file '{self.duong_dan}'.") from e
        except OSError as e:
            raise LoiFileError(f"Không thể đọc file '{self.duong_dan}': {e}") from e
        if not isinstance(data, list):
            raise LoiFileError("Dữ liệu trong file phải là một danh sách (list) bản ghi.")
        return data

    def sao_luu(self):
        """Tạo file .bak trước khi ghi đè."""
        if os.path.exists(self.duong_dan):
            try:
                shutil.copy2(self.duong_dan, self.duong_dan + ".bak")
            except OSError as e:
                raise LoiFileError(f"Không thể tạo file sao lưu: {e}") from e

    def ghi(self, data):
        """Ghi an toàn: sao lưu -> ghi file tạm -> thay thế file chính."""
        self.sao_luu()
        tam = self.duong_dan + ".tmp"
        try:
            thu_muc = os.path.dirname(self.duong_dan)
            if thu_muc:
                os.makedirs(thu_muc, exist_ok=True)
            with open(tam, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(tam, self.duong_dan)
        except PermissionError as e:
            raise LoiFileError(f"Không có quyền ghi file '{self.duong_dan}'.") from e
        except OSError as e:
            raise LoiFileError(f"Không thể ghi file '{self.duong_dan}': {e}") from e
