
"""
QUAN LY HOC BONG
File: quan_ly_hoc_bong.py

Chuc nang:
- Them hoc bong
- Sua thong tin hoc bong
- Xoa hoc bong
- Tim kiem hoc bong theo ma
- Tim kiem hoc bong theo tu khoa
- Hien thi danh sach hoc bong
- Thong ke hoc bong
"""

from hoc_bong import HocBong


class QuanLyHocBong:
    """Lop quan ly danh sach hoc bong."""

    def __init__(self):
        # Luu hoc bong theo ma hoc bong.
        # Cau truc: {"HB001": doi_tuong_hoc_bong}
        self.danh_sach = {}

    # =====================================================
    # 1. THEM HOC BONG
    # =====================================================

    def them(self, hoc_bong):
        """Them mot hoc bong vao danh sach."""

        if not isinstance(hoc_bong, HocBong):
            raise TypeError(
                "Doi tuong them vao phai la HocBong."
            )

        ma_hb = hoc_bong.ma_hb.strip()

        if not ma_hb:
            print("Loi: Ma hoc bong khong duoc de trong.")
            return False

        if ma_hb in self.danh_sach:
            print(
                f"Loi: Ma hoc bong {ma_hb} da ton tai."
            )
            return False

        hop_le, thong_bao = hoc_bong.validate()

        if not hop_le:
            print(f"Khong the them hoc bong: {thong_bao}")
            return False

        self.danh_sach[ma_hb] = hoc_bong

        print(
            f"Them hoc bong '{hoc_bong.ten_hb}' thanh cong."
        )
        return True

    # =====================================================
    # 2. TIM KIEM HOC BONG THEO MA
    # =====================================================

    def tim_kiem(self, ma_hb):
        """
        Tim hoc bong theo ma.
        Tra ve doi tuong HocBong neu tim thay.
        Tra ve None neu khong tim thay.
        """

        if ma_hb is None:
            return None

        ma_hb = str(ma_hb).strip()

        return self.danh_sach.get(ma_hb)

    # =====================================================
    # 3. SUA THONG TIN HOC BONG
    # =====================================================

    def sua(self, ma_hb, **kwargs):
        """
        Sua thong tin hoc bong theo ma.

        Vi du:
        ql_hb.sua(
            "HB001",
            ten_hb="Hoc bong khuyen hoc",
            gia_tri=2000000,
            gpa_toi_thieu=3.2
        )
        """

        hoc_bong = self.tim_kiem(ma_hb)

        if hoc_bong is None:
            print(
                f"Khong tim thay hoc bong co ma '{ma_hb}'."
            )
            return False

        truong_duoc_sua = {
            "ten_hb",
            "gia_tri",
            "gpa_toi_thieu",
            "ren_luyen_toi_thieu",
            "so_luong",
            "loai_hb",
            "don_vi",
            "nam_hoc",
            "hoc_ky",
            "trong_so_gpa",
            "trong_so_drl",
        }

        truong_khong_hop_le = (
            set(kwargs.keys()) - truong_duoc_sua
        )

        if truong_khong_hop_le:
            print(
                "Truong khong duoc phep sua: "
                + ", ".join(sorted(truong_khong_hop_le))
            )
            return False

        if not kwargs:
            print("Khong co thong tin nao duoc cap nhat.")
            return False

        # Sao luu du lieu cu de khoi phuc neu loi.
        du_lieu_cu = {
            ten: getattr(hoc_bong, ten)
            for ten in kwargs
        }

        try:
            for ten, gia_tri in kwargs.items():

                if ten == "ten_hb":
                    gia_tri = str(gia_tri).strip()

                elif ten == "gia_tri":
                    gia_tri = int(gia_tri)

                elif ten == "gpa_toi_thieu":
                    gia_tri = float(gia_tri)

                elif ten == "ren_luyen_toi_thieu":
                    gia_tri = int(gia_tri)

                elif ten == "so_luong":
                    gia_tri = int(gia_tri)

                elif ten in {
                    "trong_so_gpa",
                    "trong_so_drl"
                }:
                    gia_tri = float(gia_tri)

                setattr(hoc_bong, ten, gia_tri)

            hop_le, thong_bao = hoc_bong.validate()

            if not hop_le:
                raise ValueError(thong_bao)

        except (TypeError, ValueError, OverflowError) as loi:

            # Khoi phuc du lieu cu neu cap nhat that bai.
            for ten, gia_tri_cu in du_lieu_cu.items():
                setattr(hoc_bong, ten, gia_tri_cu)

            print(f"Khong the sua hoc bong: {loi}")
            return False

        print(
            f"Cap nhat hoc bong '{ma_hb}' thanh cong."
        )
        return True

    # =====================================================
    # 4. XOA HOC BONG
    # =====================================================

    def xoa(self, ma_hb):
        """Xoa hoc bong theo ma."""

        if ma_hb is None:
            print("Ma hoc bong khong duoc de trong.")
            return False

        ma_hb = str(ma_hb).strip()

        if ma_hb not in self.danh_sach:
            print(
                f"Khong tim thay hoc bong co ma '{ma_hb}'."
            )
            return False

        del self.danh_sach[ma_hb]

        print(f"Xoa hoc bong '{ma_hb}' thanh cong.")
        return True

    # =====================================================
    # 5. HIEN THI TAT CA HOC BONG
    # =====================================================

    def hien_thi_tat_ca(self):
        """Hien thi danh sach hoc bong."""

        if not self.danh_sach:
            print("Danh sach hoc bong hien dang trong.")
            return

        print("\n" + "=" * 65)
        print("DANH SACH HOC BONG")
        print("=" * 65)

        for stt, hoc_bong in enumerate(
            self.danh_sach.values(),
            start=1
        ):
            print(f"\nHoc bong thu {stt}:")
            hoc_bong.hien_thi()

        print(
            f"\nTong so hoc bong: {len(self.danh_sach)}"
        )

    # =====================================================
    # 6. TIM KIEM THEO TU KHOA
    # =====================================================

    def tim_kiem_tu_khoa(self, tu_khoa):
        """
        Tim theo ma, ten, loai hoc bong,
        don vi cap hoac nam hoc.
        Tra ve danh sach cac hoc bong phu hop.
        """

        if tu_khoa is None:
            return []

        tu_khoa = str(tu_khoa).strip().casefold()

        if not tu_khoa:
            return []

        ket_qua = []

        for hoc_bong in self.danh_sach.values():

            thong_tin = [
                hoc_bong.ma_hb,
                hoc_bong.ten_hb,
                hoc_bong.loai_hb,
                hoc_bong.don_vi,
                hoc_bong.nam_hoc,
            ]

            if any(
                tu_khoa in str(gia_tri).casefold()
                for gia_tri in thong_tin
            ):
                ket_qua.append(hoc_bong)

        return ket_qua

    # =====================================================
    # 7. THONG KE HOC BONG
    # =====================================================

    def dem_so_luong(self):
        """Dem tong so hoc bong."""

        return len(self.danh_sach)

    def tong_gia_tri(self):
        """Tinh tong gia tri cac hoc bong."""

        return sum(
            hb.gia_tri
            for hb in self.danh_sach.values()
        )

    def tong_so_suat(self):
        """Tinh tong so suat hoc bong."""

        return sum(
            hb.so_luong
            for hb in self.danh_sach.values()
        )


# =========================================================
# 8. KIEM TRA DOC LAP
# =========================================================

if __name__ == "__main__":

    ql_hb = QuanLyHocBong()

    hb = HocBong(
        "HB001",
        "Hoc bong khuyen hoc",
        1000000,
        3.0,
        80,
        5
    )

    print("\n--- THEM HOC BONG ---")
    ql_hb.them(hb)

    print("\n--- HIEN THI DANH SACH ---")
    ql_hb.hien_thi_tat_ca()

    print("\n--- TIM KIEM HOC BONG ---")
    ket_qua = ql_hb.tim_kiem("HB001")

    if ket_qua:
        print("Ma hoc bong:", ket_qua.ma_hb)
        print("Ten hoc bong:", ket_qua.ten_hb)
    else:
        print("Khong tim thay hoc bong.")

    print("\n--- SUA HOC BONG ---")
    ql_hb.sua(
        "HB001",
        gia_tri=2000000,
        gpa_toi_thieu=3.2
    )

    print("\n--- THONG KE ---")
    print("So hoc bong:", ql_hb.dem_so_luong())
    print("Tong gia tri:", ql_hb.tong_gia_tri())
    print("Tong so suat:", ql_hb.tong_so_suat())

    print("\n--- HOAN TAT KIEM TRA ---")
