from ho_so_hoc_bong import HoSoHocBong


class XetDuyetHocBong:
    """Tạo, quản lý và xét duyệt hồ sơ học bổng."""

    def __init__(self):
        self.danh_sach_ho_so = []
        self.ket_qua = {}

    def tao_ho_so(
        self,
        ma_ho_so,
        sinh_vien,
        hoc_bong,
        gpa,
        diem_ren_luyen,
        ly_do="",
    ):
        """Tạo hồ sơ mới; mã hồ sơ phải duy nhất."""
        ma_ho_so = str(ma_ho_so).strip()
        if not ma_ho_so:
            print("Không thể tạo hồ sơ: mã hồ sơ không được để trống.")
            return None

        for ho_so in self.danh_sach_ho_so:
            if ho_so.ma_ho_so == ma_ho_so:
                print(f"Mã hồ sơ {ma_ho_so} đã tồn tại.")
                return None

        try:
            ho_so = HoSoHocBong(
                ma_ho_so,
                sinh_vien,
                hoc_bong,
                gpa,
                diem_ren_luyen,
                ly_do,
            )
        except (TypeError, ValueError) as loi:
            print(f"Không thể tạo hồ sơ: {loi}")
            return None

        self.danh_sach_ho_so.append(ho_so)
        print(f"Đã tạo hồ sơ {ma_ho_so}.")
        return ho_so

    @staticmethod
    def _lay_gia_tri(obj, *ten_thuoc_tinh, mac_dinh=None):
        for ten in ten_thuoc_tinh:
            if hasattr(obj, ten):
                return getattr(obj, ten)
        return mac_dinh

    def _kiem_tra_dieu_kien(self, ho_so):
        """Kiểm tra điều kiện theo thông tin của học bổng nếu có."""
        hoc_bong = ho_so.hoc_bong
        gpa_toi_thieu = self._lay_gia_tri(
            hoc_bong, "gpa_toi_thieu", "diem_gpa_toi_thieu", "min_gpa",
            mac_dinh=0
        )
        ren_luyen_toi_thieu = self._lay_gia_tri(
            hoc_bong, "diem_ren_luyen_toi_thieu",
            "ren_luyen_toi_thieu", "min_diem_ren_luyen",
            mac_dinh=0
        )

        try:
            gpa_toi_thieu = float(gpa_toi_thieu)
            ren_luyen_toi_thieu = int(ren_luyen_toi_thieu)
        except (TypeError, ValueError):
            gpa_toi_thieu = 0
            ren_luyen_toi_thieu = 0

        ly_do = []
        if ho_so.gpa < gpa_toi_thieu:
            ly_do.append(f"GPA chưa đạt mức tối thiểu {gpa_toi_thieu:g}")
        if ho_so.diem_ren_luyen < ren_luyen_toi_thieu:
            ly_do.append(
                f"Điểm rèn luyện chưa đạt mức tối thiểu {ren_luyen_toi_thieu}"
            )
        return len(ly_do) == 0, "; ".join(ly_do)

    def xet_duyet(self, ma_ho_so, chap_nhan=None, ghi_chu=""):
        """
        Xét duyệt một hồ sơ.
        - chap_nhan=True: duyệt nếu đạt điều kiện.
        - chap_nhan=False: từ chối.
        - chap_nhan=None: tự xét điều kiện học bổng.
        """
        ho_so = next(
            (hs for hs in self.danh_sach_ho_so
             if hs.ma_ho_so == str(ma_ho_so).strip()),
            None,
        )
        if ho_so is None:
            print(f"Không tìm thấy hồ sơ {ma_ho_so}.")
            return False

        if chap_nhan is False:
            ho_so.tu_choi(ghi_chu or "Không được chấp nhận.")
            self.ket_qua[ho_so.ma_ho_so] = ho_so.trang_thai
            return False

        dat_dieu_kien, ly_do = self._kiem_tra_dieu_kien(ho_so)
        if chap_nhan is True and not dat_dieu_kien:
            ho_so.tu_choi(ghi_chu or ly_do)
            self.ket_qua[ho_so.ma_ho_so] = ho_so.trang_thai
            return False

        if dat_dieu_kien:
            ho_so.duyet(ghi_chu or "Đạt điều kiện học bổng.")
            self.ket_qua[ho_so.ma_ho_so] = ho_so.trang_thai
            return True

        ho_so.tu_choi(ghi_chu or ly_do)
        self.ket_qua[ho_so.ma_ho_so] = ho_so.trang_thai
        return False

    def hien_thi_ket_qua(self):
        """Hiển thị danh sách hồ sơ và kết quả xét duyệt."""
        if not self.danh_sach_ho_so:
            print("Chưa có hồ sơ học bổng nào.")
            return

        print("\n===== KẾT QUẢ XÉT DUYỆT HỌC BỔNG =====")
        for ho_so in self.danh_sach_ho_so:
            ho_so.hien_thi()
