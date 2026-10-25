
"""Mô hình học bổng – hỗ trợ kế thừa, đa hình và lưu trữ dữ liệu."""

from .base import BaseEntity
import config


class HocBong(BaseEntity):
    """Lớp cơ sở mô tả thông tin và nghiệp vụ học bổng."""

    def __init__(
        self,
        ma_hb: str = "",
        ten_hb: str = "",
        loai_hb: str = "Học tập",
        gia_tri: int = 0,
        so_suat: int = 1,
        don_vi: str = "",
        gpa_min: float = 0.0,
        drl_min: int = 0,
        nam_hoc: str = "",
        hoc_ky: str = "",
        trong_so_gpa: float = None,
        trong_so_drl: float = None,
    ):
        super().__init__(ma_hb)

        self.ma_hb = str(ma_hb).strip()
        self.ten_hb = str(ten_hb).strip()
        self.loai_hb = str(loai_hb).strip() or "Học tập"
        self.gia_tri = int(gia_tri) if gia_tri is not None else 0
        self.so_suat = int(so_suat) if so_suat is not None else 1
        self.don_vi = str(don_vi).strip()
        self.gpa_min = float(gpa_min) if gpa_min is not None else 0.0
        self.drl_min = int(drl_min) if drl_min is not None else 0
        self.nam_hoc = str(nam_hoc).strip()
        self.hoc_ky = str(hoc_ky).strip()

        self.trong_so_gpa = (
            float(trong_so_gpa)
            if trong_so_gpa is not None
            else float(config.DEFAULT_GPA_WEIGHT)
        )

        self.trong_so_drl = (
            float(trong_so_drl)
            if trong_so_drl is not None
            else float(config.DEFAULT_DRL_WEIGHT)
        )

    # =====================================================
    # CHUYỂN ĐỔI DỮ LIỆU
    # =====================================================

    def to_dict(self) -> dict:
        """Chuyển đối tượng học bổng thành dictionary để lưu JSON."""
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
            "created_at": self._created_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Khôi phục đúng lớp học bổng từ dictionary."""
        class_map = {
            "HocBong": HocBong,
            "HocBongHocTap": HocBongHocTap,
            "HocBongHoanCanh": HocBongHoanCanh,

            # Hỗ trợ dữ liệu JSON đã lưu bằng tên lớp cũ.
            "Scholarship": HocBong,
            "AcademicScholarship": HocBongHocTap,
            "HardshipScholarship": HocBongHoanCanh,
        }

        class_type = data.get("class_type", "HocBong")
        model_class = class_map.get(class_type, HocBong)

        return model_class._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict):
        """Khôi phục đối tượng từ dictionary."""
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
            trong_so_drl=data.get("trong_so_drl"),
        )

        if data.get("created_at") is not None:
            obj._created_at = data["created_at"]

        return obj

    # =====================================================
    # KIỂM TRA DỮ LIỆU
    # =====================================================

    def validate(self) -> tuple[bool, str]:
        """Kiểm tra dữ liệu học bổng có hợp lệ hay không."""

        if not self.ma_hb:
            return False, "Mã học bổng bắt buộc."

        if not self.ten_hb:
            return False, "Tên học bổng bắt buộc."

        if self.gia_tri < 0:
            return False, "Giá trị học bổng không được âm."

        if self.so_suat < 1:
            return False, "Số suất học bổng phải lớn hơn hoặc bằng 1."

        if not 0 <= self.gpa_min <= config.GPA_SCALE:
            return False, (
                f"GPA tối thiểu phải nằm trong khoảng "
                f"0 – {config.GPA_SCALE}."
            )

        if not 0 <= self.drl_min <= config.DRL_MAX:
            return False, (
                f"Điểm rèn luyện tối thiểu phải nằm trong khoảng "
                f"0 – {config.DRL_MAX}."
            )

        if self.trong_so_gpa < 0 or self.trong_so_drl < 0:
            return False, "Trọng số GPA và ĐRL không được âm."

        if self.trong_so_gpa + self.trong_so_drl <= 0:
            return False, "Tổng trọng số GPA và ĐRL phải lớn hơn 0."

        return True, ""

    # =====================================================
    # NGHIỆP VỤ HỌC BỔNG
    # =====================================================

    def du_dieu_kien(self, gpa: float, drl: int) -> bool:
        """Kiểm tra sinh viên có đạt điều kiện học bổng hay không."""

        return (
            0 <= gpa <= config.GPA_SCALE
            and 0 <= drl <= config.DRL_MAX
            and gpa >= self.gpa_min
            and drl >= self.drl_min
        )

    def tinh_diem(
        self,
        gpa: float,
        drl: int,
        hoan_canh: str = "",
    ) -> float:
        """Tính điểm xét học bổng theo trọng số GPA và điểm rèn luyện."""

        if not 0 <= gpa <= config.GPA_SCALE:
            raise ValueError(
                f"GPA phải nằm trong khoảng 0 – {config.GPA_SCALE}."
            )

        if not 0 <= drl <= config.DRL_MAX:
            raise ValueError(
                f"Điểm rèn luyện phải nằm trong khoảng 0 – {config.DRL_MAX}."
            )

        diem = (
            (gpa / config.GPA_SCALE)
            * self.trong_so_gpa
            * 100
            + (drl / config.DRL_MAX)
            * self.trong_so_drl
            * 100
        )

        return round(diem, 2)

    def hien_thi(self) -> None:
        """Hiển thị thông tin học bổng."""

        print("-" * 60)
        print(f"Mã học bổng       : {self.ma_hb}")
        print(f"Tên học bổng      : {self.ten_hb}")
        print(f"Loại học bổng     : {self.loai_hb}")
        print(f"Giá trị           : {self.gia_tri:,.0f} VNĐ")
        print(f"Số suất           : {self.so_suat}")
        print(f"Đơn vị cấp        : {self.don_vi}")
        print(f"GPA tối thiểu     : {self.gpa_min}")
        print(f"Điểm RL tối thiểu : {self.drl_min}")
        print(f"Năm học           : {self.nam_hoc}")
        print(f"Học kỳ            : {self.hoc_ky}")
        print("-" * 60)


class HocBongHocTap(HocBong):
    """Học bổng học tập – ưu tiên thành tích GPA."""

    def __init__(self, **kwargs):
        kwargs.setdefault("loai_hb", "Học tập")
        kwargs.setdefault("trong_so_gpa", 0.8)
        kwargs.setdefault("trong_so_drl", 0.2)
        super().__init__(**kwargs)

    def tinh_diem(
        self,
        gpa: float,
        drl: int,
        hoan_canh: str = "",
    ) -> float:
        """Ghi đè phương thức tính điểm để thể hiện tính đa hình."""
        return super().tinh_diem(gpa, drl, hoan_canh)


class HocBongHoanCanh(HocBong):
    """Học bổng dành cho sinh viên có hoàn cảnh khó khăn."""

    DIEM_UU_TIEN = 15

    def __init__(self, **kwargs):
        kwargs.setdefault("loai_hb", "Hoàn cảnh")
        kwargs.setdefault("trong_so_gpa", 0.5)
        kwargs.setdefault("trong_so_drl", 0.3)
        super().__init__(**kwargs)

    def tinh_diem(
        self,
        gpa: float,
        drl: int,
        hoan_canh: str = "",
    ) -> float:
        """Cộng điểm ưu tiên khi có thông tin hoàn cảnh khó khăn."""
        diem = super().tinh_diem(gpa, drl, hoan_canh)

        if hoan_canh and hoan_canh.strip():
            diem += self.DIEM_UU_TIEN

        return round(min(diem, 100), 2)
