import json
from pathlib import Path
from models.sinh_vien import SinhVien
from service.quan_ly_sinh_vien import QuanLySinhVien
from models.hoc_bong import HocBong
from service.quan_ly_hoc_bong import QuanLyHocBong
from service.xet_duyet import XetDuyetHocBong
from models.ho_so_hoc_bong import HoSoHocBong
from models.thong_ke import ThongKe

DU_LIEU = Path(__file__).parent / "data" / "du_lieu.json"


def nhap_so(thong_bao, kieu=float):
    return kieu(input(thong_bao).strip())


def luu(ql_sv, ql_hb, ql_xet):
    DU_LIEU.parent.mkdir(parents=True, exist_ok=True)
    du_lieu = {
        "sinh_vien": [sv.to_dict() for sv in ql_sv.danh_sach.values()],
        "hoc_bong": [hb.to_dict() for hb in ql_hb.danh_sach.values()],
        "ho_so": [hs.to_dict() for hs in ql_xet.danh_sach_ho_so],
        "dem_ho_so": ql_xet.dem_ho_so,
    }
    DU_LIEU.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2), encoding="utf-8")


def tai(ql_sv, ql_hb, ql_xet):
    if not DU_LIEU.exists():
        return
    data = json.loads(DU_LIEU.read_text(encoding="utf-8"))
    for d in data.get("sinh_vien", []):
        ql_sv.them(SinhVien(**d))
    for d in data.get("hoc_bong", []):
        ql_hb.them(HocBong(**d))
    for d in data.get("ho_so", []):
        sv = ql_sv.danh_sach.get(d["ma_sv"])
        hb = ql_hb.tim_kiem(d["ma_hb"])
        if sv is None or hb is None:
            continue
        hs = HoSoHocBong(d["ma_ho_so"], sv, hb)
        hs.trang_thai = d["trang_thai"]
        hs.ly_do = d.get("ly_do", "")
        ql_xet.danh_sach_ho_so.append(hs)
    ql_xet.dem_ho_so = max(int(data.get("dem_ho_so", 0)),
                           *(int(h.ma_ho_so[2:]) for h in ql_xet.danh_sach_ho_so)) if ql_xet.danh_sach_ho_so else int(data.get("dem_ho_so", 0))


def menu():
    print("\n========== HE THONG QUAN LY HOC BONG ==========")
    print("1. Them sinh vien         2. Danh sach sinh vien")
    print("3. Tim sinh vien          4. Sua sinh vien")
    print("5. Xoa sinh vien          6. Them hoc bong")
    print("7. Danh sach hoc bong     8. Sua hoc bong")
    print("9. Xoa hoc bong          10. Dang ky hoc bong")
    print("11. Xet duyet hoc bong   12. Ket qua ho so")
    print("13. Thong ke              0. Luu va thoat")


def main():
    ql_sv, ql_hb, ql_xet = QuanLySinhVien(), QuanLyHocBong(), XetDuyetHocBong()
    try:
        tai(ql_sv, ql_hb, ql_xet)
    except (ValueError, KeyError, json.JSONDecodeError, OSError) as e:
        print("Khong doc duoc du lieu cu:", e)
        return
    while True:
        menu()
        chon = input("Chon chuc nang: ").strip()
        try:
            if chon == "1":
                sv = SinhVien(input("Ma SV: "), input("Ho ten: "), input("Lop: "),
                              nhap_so("GPA (0-4): "), nhap_so("Diem ren luyen (0-100): ", int))
                ql_sv.them(sv)
                print("Da them sinh vien")
            elif chon == "2":
                ql_sv.hien_thi_tat_ca()
            elif chon == "3":
                ket_qua = ql_sv.tim_kiem(input("Nhap ma/ten can tim: "))
                for sv in ket_qua: sv.hien_thi_thong_tin()
                if not ket_qua: print("Khong tim thay")
            elif chon == "4":
                ma = input("Ma SV can sua: ").strip()
                sv = ql_sv.danh_sach.get(ma)
                if sv is None: raise ValueError("Khong tim thay sinh vien")
                print("Nhan Enter de giu nguyen gia tri cu")
                ten = input(f"Ho ten [{sv.ho_ten}]: ").strip()
                lop = input(f"Lop [{sv.lop}]: ").strip()
                gpa = input(f"GPA [{sv.gpa}]: ").strip()
                drl = input(f"DRL [{sv.diem_ren_luyen}]: ").strip()
                ql_sv.sua(ma, ho_ten=ten or sv.ho_ten, lop=lop or sv.lop,
                          gpa=float(gpa) if gpa else sv.gpa,
                          diem_ren_luyen=int(drl) if drl else sv.diem_ren_luyen)
                print("Da sua")
            elif chon == "5":
                ma = input("Ma SV can xoa: ").strip()
                if any(h.sinh_vien.ma_sv == ma for h in ql_xet.danh_sach_ho_so):
                    raise ValueError("SV co ho so; khong the xoa")
                print("Da xoa" if ql_sv.xoa(ma) else "Khong tim thay")
            elif chon == "6":
                hb = HocBong(input("Ma HB: "), input("Ten HB: "),
                             nhap_so("Gia tri (VND): ", int), nhap_so("GPA toi thieu: "),
                             nhap_so("DRL toi thieu: ", int), nhap_so("So suat: ", int))
                ql_hb.them(hb)
                print("Da them hoc bong")
            elif chon == "7":
                ql_hb.hien_thi_tat_ca()
            elif chon == "8":
                ma = input("Ma HB can sua: ").strip()
                hb = ql_hb.tim_kiem(ma)
                if hb is None: raise ValueError("Khong tim thay hoc bong")
                print("Nhan Enter de giu nguyen gia tri cu")
                ten = input(f"Ten [{hb.ten_hb}]: ").strip()
                tien = input(f"Gia tri [{hb.gia_tri}]: ").strip()
                gpa = input(f"GPA [{hb.gpa_toi_thieu}]: ").strip()
                drl = input(f"DRL [{hb.ren_luyen_toi_thieu}]: ").strip()
                suat = input(f"So suat [{hb.so_luong}]: ").strip()
                ql_hb.sua(ma, ten_hb=ten or hb.ten_hb,
                          gia_tri=int(tien) if tien else hb.gia_tri,
                          gpa_toi_thieu=float(gpa) if gpa else hb.gpa_toi_thieu,
                          ren_luyen_toi_thieu=int(drl) if drl else hb.ren_luyen_toi_thieu,
                          so_luong=int(suat) if suat else hb.so_luong)
                print("Da sua (neu da xet duyet, hay xet lai)")
            elif chon == "9":
                ma = input("Ma HB can xoa: ").strip()
                if any(h.hoc_bong.ma_hb == ma for h in ql_xet.danh_sach_ho_so):
                    raise ValueError("HB co ho so; khong the xoa")
                print("Da xoa" if ql_hb.xoa(ma) else "Khong tim thay")
            elif chon == "10":
                sv = ql_sv.danh_sach.get(input("Ma SV: ").strip())
                hb = ql_hb.tim_kiem(input("Ma HB: ").strip())
                if sv is None or hb is None: raise ValueError("Ma SV hoac HB khong ton tai")
                hs = ql_xet.tao_ho_so(sv, hb)
                print("Da tao ho so:", hs.ma_ho_so)
            elif chon == "11":
                hb = ql_hb.tim_kiem(input("Ma HB can xet: ").strip())
                if hb is None: raise ValueError("Khong tim thay hoc bong")
                ket_qua = ql_xet.xet_duyet(hb)
                print(f"Da xet {len(ket_qua)} ho so")
            elif chon == "12":
                ql_xet.hien_thi_ket_qua()
            elif chon == "13":
                ThongKe.hien_thi(ql_xet.danh_sach_ho_so)
            elif chon == "0":
                luu(ql_sv, ql_hb, ql_xet)
                print("Da luu du lieu. Tam biet!")
                break
            else:
                print("Lua chon khong hop le")
            # Luu sau moi thao tac de han che mat du lieu.
            luu(ql_sv, ql_hb, ql_xet)
        except (ValueError, TypeError, OSError) as e:
            print("Loi:", e)

if __name__ == "__main__":
    main()
