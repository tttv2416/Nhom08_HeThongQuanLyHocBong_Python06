
"""
Lớp học bổng - kế thừa và đa hình phương thức tính điểm.
Hỗ trợ học bổng học tập và học bổng hoàn cảnh khó khăn.
"""

# =============================================================
# 1. IMPORT THƯ VIỆN VÀ THIẾT LẬP ĐƯỜNG DẪN
# =============================================================

import sys
from pathlib import Path


# Hỗ trợ chạy file trực tiếp trong Spyder hoặc import từ main.py
if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent

    if current_dir.name == "models":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # base.py cần nằm trong thư mục models/
    from models.base import BaseEntity

    # config.py cần nằm trong thư mục gốc dự án
    import config

else:
    # Khi import theo package models
    from .base import BaseEntity
    import config


# =============================================================
# 2. LỚP CƠ SỞ SCHOLARSHIP
# =============================================================

class Scholarship(BaseEntity):
    """Lớp cơ sở quản lý thông tin học bổng."""

    def __init__(
        self,
        ma_hb="",
        ten_hb="",
        loai_hb="Học tập",
        gia_tri=0,
        so_suat=1,
        don_vi="",
        gpa_min=0.0,
        drl_min=0,
        nam_hoc="",
        hoc_ky="",
        trong_so_gpa=None,
        trong_so_drl=None
    ):
        super().__init__(ma_hb)

        self.ma_hb = ma_hb
        self.ten_hb = ten_hb
        self.loai_hb = loai_hb

        self.gia_tri = int(gia_tri)
        self.so_suat = int(so_suat)

        self.don_vi = don_vi
        self.gpa_min = float(gpa_min)
        self.drl_min = int(drl_min)

        self.nam_hoc = nam_hoc
        self.hoc_ky = hoc_ky

        # Lấy trọng số mặc định từ config.py nếu không truyền vào
        self.trong_so_gpa = float(
            config.DEFAULT_GPA_WEIGHT
            if trong_so_gpa is None
            else trong_so_gpa
        )

        self.trong_so_drl = float(
            config.DEFAULT_DRL_WEIGHT
            if trong_so_drl is None
            else trong_so_drl
        )

    # =========================================================
    # 3. CHUYỂN ĐỐI TƯỢNG THÀNH DICTIONARY
    # =========================================================

    def to_dict(self):
        """Chuyển thông tin học bổng thành dictionary."""

        return {
            "ma_hb": self.ma_hb,
            "ten_hb": self.ten_hb,
            "loai_hb": self.loai_hb,
            "gia_tri": self.gia_tri,
            "so_suat": self.so_suat,
            "don_vi": self.don_vi,
            "gpa_min": self.gpa_min,
            "drl_min": self.drl_min,
            "nam_hoc": self.nam_hoc,
            "hoc_ky": self.hoc_ky,
            "trong_so_gpa": self.trong_so_gpa,
            "trong_so_drl": self.trong_so_drl,
            "class_type": self.__class__.__name__,
            "created_at": getattr(self, "_created_at", None)
        }

    # =========================================================
    # 4. KHÔI PHỤC ĐỐI TƯỢNG TỪ DICTIONARY
    # =========================================================

    @classmethod
    def from_dict(cls, data):
        """Khôi phục đúng lớp học bổng từ dictionary."""

        if not isinstance(data, dict):
            raise TypeError("Dữ liệu khôi phục phải là dictionary.")

        class_type = data.get("class_type", cls.__name__)

        class_map = {
            "Scholarship": Scholarship,
            "AcademicScholarship": AcademicScholarship,
            "HardshipScholarship": HardshipScholarship
        }

        target_class = class_map.get(class_type, cls)

        return target_class._from_dict(data)

    @classmethod
    def _from_dict(cls, data):
        """Tạo đối tượng từ dictionary."""

        obj = cls(
            ma_hb=data.get("ma_hb", ""),
            ten_hb=data.get("ten_hb", ""),
            loai_hb=data.get("loai_hb", "Học tập"),
            gia_tri=data.get("gia_tri", 0),
            so_suat=data.get("so_suat", 1),
            don_vi=data.get("don_vi", ""),
            gpa_min=data.get("gpa_min", 0.0),
            drl_min=data.get("drl_min", 0),
            nam_hoc=data.get("nam_hoc", ""),
            hoc_ky=data.get("hoc_ky", ""),
            trong_so_gpa=data.get("trong_so_gpa"),
            trong_so_drl=data.get("trong_so_drl")
        )

        # Khôi phục thời điểm tạo nếu BaseEntity có thuộc tính này
        if data.get("created_at") is not None:
            obj._created_at = data["created_at"]

        return obj

    # =========================================================
    # 5. KIỂM TRA TÍNH HỢP LỆ
    # =========================================================

    def validate(self):
        """
        Trả về (True, "") nếu hợp lệ.
        Trả về (False, thông báo lỗi) nếu không hợp lệ.
        """

        if not isinstance(self.ma_hb, str) or not self.ma_hb.strip():
            return False, "Mã học bổng bắt buộc."

        if not isinstance(self.ten_hb, str) or not self.ten_hb.strip():
            return False, "Tên học bổng bắt buộc."

        if self.gia_tri < 0:
            return False, "Giá trị học bổng không được âm."

        if self.so_suat < 1:
            return False, "Số suất học bổng phải từ 1 trở lên."

        if not 0 <= self.gpa_min <= config.GPA_SCALE:
            return (
                False,
                f"GPA tối thiểu phải từ 0 đến {config.GPA_SCALE}."
            )

        if not 0 <= self.drl_min <= config.DRL_MAX:
            return (
                False,
                f"Điểm rèn luyện tối thiểu phải từ 0 đến "
                f"{config.DRL_MAX}."
            )

        if self.trong_so_gpa < 0:
            return False, "Trọng số GPA không được âm."

        if self.trong_so_drl < 0:
            return False, "Trọng số điểm rèn luyện không được âm."

        return True, ""

    # =========================================================
    # 6. KIỂM TRA ĐIỀU KIỆN NHẬN HỌC BỔNG
    # =========================================================

    def du_dieu_kien(self, gpa, drl):
        """Kiểm tra GPA và điểm rèn luyện có đạt yêu cầu không."""

        try:
            gpa = float(gpa)
            drl = float(drl)
        except (TypeError, ValueError):
            return False

        if not 0 <= gpa <= config.GPA_SCALE:
            return False

        if not 0 <= drl <= config.DRL_MAX:
            return False

        return (
            gpa >= self.gpa_min
            and drl >= self.drl_min
        )

    def kiem_tra_dieu_kien(self, gpa, drl):
        """Phương thức tương thích với tên gọi trong chương trình."""

        return self.du_dieu_kien(gpa, drl)

    # =========================================================
    # 7. TÍNH ĐIỂM XÉT HỌC BỔNG
    # =========================================================

    def tinh_diem(self, gpa, drl, hoan_canh=""):
        """
        Tính điểm theo trọng số GPA và điểm rèn luyện.

        Công thức:
        Điểm GPA = GPA / GPA_SCALE * trọng số GPA * 100
        Điểm ĐRL = ĐRL / DRL_MAX * trọng số ĐRL * 100
        Tổng điểm không vượt quá 100.
        """

        try:
            gpa = float(gpa)
            drl = float(drl)
        except (TypeError, ValueError):
            raise ValueError(
                "GPA và điểm rèn luyện phải là số."
            )

        if not 0 <= gpa <= config.GPA_SCALE:
            raise ValueError(
                f"GPA phải từ 0 đến {config.GPA_SCALE}."
            )

        if not 0 <= drl <= config.DRL_MAX:
            raise ValueError(
                f"Điểm rèn luyện phải từ 0 đến {config.DRL_MAX}."
            )

        if config.GPA_SCALE <= 0 or config.DRL_MAX <= 0:
            raise ValueError(
                "GPA_SCALE và DRL_MAX trong config.py phải lớn hơn 0."
            )

        diem_gpa = (
            gpa / config.GPA_SCALE
        ) * self.trong_so_gpa * 100

        diem_drl = (
            drl / config.DRL_MAX
        ) * self.trong_so_drl * 100

        tong_diem = diem_gpa + diem_drl

        return round(min(tong_diem, 100), 2)

    # =========================================================
    # 8. HIỂN THỊ THÔNG TIN HỌC BỔNG
    # =========================================================

    def hien_thi(self):
        """In thông tin học bổng ra màn hình."""

        print("-" * 55)
        print(f"Mã học bổng   : {self.ma_hb}")
        print(f"Tên học bổng  : {self.ten_hb}")
        print(f"Loại học bổng : {self.loai_hb}")
        print(f"Giá trị       : {self.gia_tri:,.0f} VNĐ")
        print(f"Số suất       : {self.so_suat}")
        print(f"Đơn vị cấp    : {self.don_vi}")
        print(f"GPA tối thiểu : {self.gpa_min}")
        print(f"ĐRL tối thiểu : {self.drl_min}")
        print(f"Năm học       : {self.nam_hoc}")
        print(f"Học kỳ        : {self.hoc_ky}")
        print("-" * 55)


# =============================================================
# 9. LỚP CON: HỌC BỔNG HỌC TẬP
# =============================================================

class AcademicScholarship(Scholarship):
    """Học bổng học tập, ưu tiên kết quả GPA."""

    def __init__(self, **kwargs):
        kwargs.setdefault("loai_hb", "Học tập")
        kwargs.setdefault("trong_so_gpa", 0.8)
        kwargs.setdefault("trong_so_drl", 0.2)

        super().__init__(**kwargs)

    def tinh_diem(self, gpa, drl, hoan_canh=""):
        """Ghi đè phương thức tính điểm của lớp cha."""

        return super().tinh_diem(gpa, drl, hoan_canh)


# =============================================================
# 10. LỚP CON: HỌC BỔNG HOÀN CẢNH KHÓ KHĂN
# =============================================================

class HardshipScholarship(Scholarship):
    """Học bổng ưu tiên sinh viên có hoàn cảnh khó khăn."""

    DIEM_UU_TIEN_HOAN_CANH = 15.0

    def __init__(self, **kwargs):
        kwargs.setdefault("loai_hb", "Hoàn cảnh")
        kwargs.setdefault("trong_so_gpa", 0.5)
        kwargs.setdefault("trong_so_drl", 0.3)

        super().__init__(**kwargs)

    def tinh_diem(self, gpa, drl, hoan_canh=""):
        """Cộng điểm ưu tiên nếu sinh viên khai báo hoàn cảnh."""

        diem_co_ban = super().tinh_diem(gpa, drl, hoan_canh)

        if isinstance(hoan_canh, str) and hoan_canh.strip():
            diem_co_ban += self.DIEM_UU_TIEN_HOAN_CANH

        return round(min(diem_co_ban, 100), 2)


# =============================================================
# 11. CHƯƠNG TRÌNH KIỂM TRA
# =============================================================

def kiem_tra_chuong_trinh():
    """Kiểm tra khởi tạo, tính điểm, điều kiện và chuyển đổi dữ liệu."""

    print("=" * 60)
    print("KIỂM TRA LỚP SCHOLARSHIP")
    print("=" * 60)

    # Kiểm tra học bổng học tập
    hoc_bong = AcademicScholarship(
        ma_hb="HB001",
        ten_hb="Học bổng học tập",
        gia_tri=1000000,
        so_suat=5,
        don_vi="Nhà trường",
        gpa_min=3.0,
        drl_min=80,
        nam_hoc="2026-2027",
        hoc_ky="Học kỳ 1"
    )

    hop_le, thong_bao = hoc_bong.validate()

    print("\n[1] Kiểm tra dữ liệu")

    if hop_le:
        print("PASS: Dữ liệu học bổng hợp lệ.")
    else:
        print("FAIL:", thong_bao)

    print("\n[2] Thông tin học bổng")
    hoc_bong.hien_thi()

    print("\n[3] Kiểm tra điều kiện")

    du_dieu_kien = hoc_bong.du_dieu_kien(
        gpa=3.5,
        drl=90
    )

    print("Kết quả:", "Đủ điều kiện" if du_dieu_kien else "Không đủ điều kiện")

    print("\n[4] Tính điểm học bổng")

    diem = hoc_bong.tinh_diem(
        gpa=3.5,
        drl=90
    )

    print(f"Điểm xét học bổng: {diem}/100")

    print("\n[5] Kiểm tra chuyển đổi dictionary")

    du_lieu = hoc_bong.to_dict()
    hoc_bong_khoi_phuc = Scholarship.from_dict(du_lieu)

    print("Mã ban đầu:", hoc_bong.ma_hb)
    print("Mã khôi phục:", hoc_bong_khoi_phuc.ma_hb)
    print("Loại lớp khôi phục:", type(hoc_bong_khoi_phuc).__name__)

    if (
        hoc_bong_khoi_phuc.ma_hb == hoc_bong.ma_hb
        and type(hoc_bong_khoi_phuc) is type(hoc_bong)
    ):
        print("PASS: Chuyển đổi dictionary thành công.")
    else:
        print("FAIL: Dữ liệu khôi phục chưa chính xác.")

    print("\n[6] Kiểm tra đa hình")

    hoc_bong_hoan_canh = HardshipScholarship(
        ma_hb="HB002",
        ten_hb="Học bổng hoàn cảnh khó khăn",
        gia_tri=2000000,
        so_suat=3,
        don_vi="Nhà trường",
        gpa_min=2.5,
        drl_min=70
    )

    diem_hoc_tap = hoc_bong.tinh_diem(3.5, 90)
    diem_hoan_canh = hoc_bong_hoan_canh.tinh_diem(
        3.5,
        90,
        "Gia đình khó khăn"
    )

    print(f"Điểm học bổng học tập: {diem_hoc_tap}")
    print(f"Điểm học bổng hoàn cảnh: {diem_hoan_canh}")

    print("\n" + "=" * 60)
    print("ĐÃ HOÀN THÀNH KIỂM TRA.")
    print("=" * 60)


if __name__ == "__main__":
    kiem_tra_chuong_trinh()
