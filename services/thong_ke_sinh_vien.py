"""Module services/thong_ke_sinh_vien.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

Các hàm thống kê thuần (không phụ thuộc giao diện) cho danh sách SinhVien:
dùng để vẽ biểu đồ và dễ kiểm thử.
"""

THU_TU_HOC_LUC = ("Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu")


def dem_theo_lop(ds):
    """[(lớp, số sinh viên), ...] sắp theo tên lớp."""
    dem = {}
    for sv in ds:
        dem[sv.lop] = dem.get(sv.lop, 0) + 1
    return sorted(dem.items())


def dem_theo_hoc_luc(ds):
    """[(học lực, số sinh viên), ...] đủ 5 mức theo thứ tự, mức không có ai vẫn là 0."""
    dem = dict.fromkeys(THU_TU_HOC_LUC, 0)
    for sv in ds:
        dem[sv.xep_loai_hoc_luc()] += 1
    return list(dem.items())


def tong_quan(ds):
    """Số liệu tổng hợp: tổng sinh viên, số lớp, GPA và điểm rèn luyện trung bình, sinh viên GPA cao nhất."""
    ds = list(ds)
    if not ds:
        return {"tong": 0, "so_lop": 0, "gpa_tb": 0.0, "drl_tb": 0.0, "gpa_cao_nhat": None}
    return {
        "tong": len(ds),
        "so_lop": len({sv.lop for sv in ds}),
        "gpa_tb": sum(sv.gpa for sv in ds) / len(ds),
        "drl_tb": sum(sv.diem_ren_luyen for sv in ds) / len(ds),
        "gpa_cao_nhat": max(ds, key=lambda sv: sv.gpa),
    }
