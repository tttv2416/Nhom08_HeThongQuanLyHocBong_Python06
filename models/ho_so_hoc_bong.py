class HoSoHocBong:
    """Lưu thông tin hồ sơ đăng ký học bổng của một sinh viên."""

    def __init__(
        self,
        ma_ho_so,
        sinh_vien,
        hoc_bong,
        gpa,
        diem_ren_luyen,
        ly_do="",
        trang_thai="Chờ xét duyệt",
    ):
        self.ma_ho_so = str(ma_ho_so).strip()
        self.sinh_vien = sinh_vien
        self.hoc_bong = hoc_bong
        self.gpa = float(gpa)
        self.diem_ren_luyen = int(diem_ren_luyen)
        self.ly_do = ly_do
        self.trang_thai = trang_thai
        self.ghi_chu = ""

        if not self.ma_ho_so:
            raise ValueError("Mã hồ sơ không được để trống.")
        if not 0 <= self.gpa <= 4:
            raise ValueError("GPA phải nằm trong khoảng từ 0 đến 4.")
        if not 0 <= self.diem_ren_luyen <= 100:
            raise ValueError("Điểm rèn luyện phải nằm trong khoảng từ 0 đến 100.")

    def duyet(self, ghi_chu=""):
        """Chuyển hồ sơ sang trạng thái đã duyệt."""
        self.trang_thai = "Đã duyệt"
        self.ghi_chu = ghi_chu

    def tu_choi(self, ly_do_tu_choi=""):
        """Từ chối hồ sơ và lưu lý do."""
        self.trang_thai = "Từ chối"
        self.ghi_chu = ly_do_tu_choi

    @staticmethod
    def _lay_thuoc_tinh(obj, *ten_thuoc_tinh, mac_dinh="Chưa có"):
        for ten in ten_thuoc_tinh:
            if hasattr(obj, ten):
                return getattr(obj, ten)
        return mac_dinh

    def hien_thi(self):
        """In thông tin hồ sơ ra màn hình."""
        ten_sinh_vien = self._lay_thuoc_tinh(
            self.sinh_vien, "ho_ten", "ten", "name", "ten_sinh_vien"
        )
        ma_sinh_vien = self._lay_thuoc_tinh(
            self.sinh_vien, "ma_sinh_vien", "ma_sv", "ma", "student_id"
        )
        ten_hoc_bong = self._lay_thuoc_tinh(
            self.hoc_bong, "ten_hoc_bong", "ten", "name"
        )
        ma_hoc_bong = self._lay_thuoc_tinh(
            self.hoc_bong, "ma_hoc_bong", "ma_hb", "ma", "scholarship_id"
        )

        print("-" * 45)
        print(f"Mã hồ sơ: {self.ma_ho_so}")
        print(f"Sinh viên: {ten_sinh_vien} (Mã: {ma_sinh_vien})")
        print(f"Học bổng: {ten_hoc_bong} (Mã: {ma_hoc_bong})")
        print(f"GPA: {self.gpa:.2f}/4.0")
        print(f"Điểm rèn luyện: {self.diem_ren_luyen}/100")
        print(f"Lý do đăng ký: {self.ly_do}")
        print(f"Trạng thái: {self.trang_thai}")
        if self.ghi_chu:
            print(f"Ghi chú: {self.ghi_chu}")
        print("-" * 45)
