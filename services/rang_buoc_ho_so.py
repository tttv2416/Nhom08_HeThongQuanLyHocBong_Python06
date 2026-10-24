"""Ràng buộc dữ liệu: sinh viên đã có hồ sơ học bổng thì không được xóa.

Dùng chung cho menu console và giao diện Tkinter.
"""

from config import DUONG_DAN_HO_SO
from services.luu_tru_json import LuuTruJSON


def _ma_sv_cua_ho_so(ho_so):
    """Lấy mã sinh viên từ một bản ghi hồ sơ (chấp nhận vài cách đặt tên khóa)."""
    if not isinstance(ho_so, dict):
        return ""
    sv = ho_so.get("sinh_vien")
    if isinstance(sv, str):
        return sv.strip()
    nguon = sv if isinstance(sv, dict) else ho_so
    for khoa in ("ma_sv", "ma_sinh_vien"):
        if khoa in nguon:
            return str(nguon[khoa]).strip()
    return ""


def sinh_vien_co_ho_so(ma_sv, duong_dan=DUONG_DAN_HO_SO):
    """True nếu sinh viên đang có hồ sơ trong file ho_so.json.
    File hồ sơ chưa có/rỗng -> False. File hỏng -> LoiFileError (chặn xóa cho an toàn)."""
    ds = LuuTruJSON(duong_dan).doc()
    return any(_ma_sv_cua_ho_so(h) == str(ma_sv).strip() for h in ds)
