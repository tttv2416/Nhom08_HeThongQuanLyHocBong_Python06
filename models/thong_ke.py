from ho_so_hoc_bong import HoSoHocBong

class ThongKe:
    @staticmethod
    def tong_hop(danh_sach_ho_so):
        duyet = [h for h in danh_sach_ho_so if h.trang_thai == HoSoHocBong.DA_DUYET]
        tu_choi = [h for h in danh_sach_ho_so if h.trang_thai == HoSoHocBong.TU_CHOI]
        return {"tong_ho_so": len(danh_sach_ho_so),
                "cho_duyet": len(danh_sach_ho_so) - len(duyet) - len(tu_choi),
                "da_duyet": len(duyet), "tu_choi": len(tu_choi),
                "tong_tien": sum(h.hoc_bong.gia_tri for h in duyet)}

    @staticmethod
    def hien_thi(danh_sach_ho_so):
        kq = ThongKe.tong_hop(danh_sach_ho_so)
        print("\n===== THONG KE HOC BONG =====")
        print(f"Tong ho so: {kq['tong_ho_so']}")
        print(f"Cho duyet: {kq['cho_duyet']}")
        print(f"Da duyet: {kq['da_duyet']}")
        print(f"Tu choi: {kq['tu_choi']}")
        print(f"Tong kinh phi: {kq['tong_tien']:,} VND")