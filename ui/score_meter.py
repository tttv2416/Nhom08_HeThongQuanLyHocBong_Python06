"""Module ui/score_meter.py
Người phụ trách: Nguyễn Thị Đông Phương - 2044240275

ScoreMeter: widget tự vẽ bằng Canvas (Custom Widget) hiển thị điểm dạng thanh đo,
đổi màu theo mức: đỏ (thấp) - vàng (trung bình) - xanh (tốt).

Ví dụ:
    meter = ScoreMeter(khung, toi_da=4.0)      # thang GPA
    meter.dat_gia_tri(3.45)                    # vẽ lại, tự đổi màu
    meter.dat_gia_tri(None)                    # xóa (chưa chọn)

Mốc màu mặc định tính theo tỷ lệ so với giá trị tối đa:
    < 50%  -> đỏ     (GPA < 2.0,  điểm rèn luyện < 50)
    < 80%  -> vàng   (GPA < 3.2,  điểm rèn luyện < 80)
    còn lại -> xanh
Các mốc này trùng với ranh giới xếp loại trong SinhVien.
"""

import tkinter as tk

from ui.theme import MAU_NEN, kich_thuoc_canvas

MAU_DO = "#d64545"
MAU_VANG = "#e8a317"
MAU_XANH = "#2e9e5b"
MOC_MAC_DINH = ((0.5, MAU_DO), (0.8, MAU_VANG), (1.0, MAU_XANH))

MAU_RANH = "#d6dce6"
MAU_VIEN = "#b8c1cf"


class ScoreMeter(tk.Canvas):
    """Thanh đo điểm tự vẽ, đổi màu theo mức điểm."""

    def __init__(self, master, toi_da=100.0, cac_moc=MOC_MAC_DINH, nen=MAU_NEN,
                 width=200, height=18, **kwargs):
        super().__init__(master, width=width, height=height, bg=nen,
                         highlightthickness=0, **kwargs)
        if float(toi_da) <= 0:
            raise ValueError("Giá trị tối đa của ScoreMeter phải lớn hơn 0.")
        self.toi_da = float(toi_da)
        self.cac_moc = tuple(cac_moc)
        self.gia_tri = None
        self.bind("<Configure>", lambda _e: self.ve())
        self.ve()

    def dat_gia_tri(self, gia_tri):
        """Đặt giá trị mới (None = chưa có giá trị) rồi vẽ lại."""
        if gia_tri is None:
            self.gia_tri = None
        else:
            self.gia_tri = max(0.0, min(float(gia_tri), self.toi_da))
        self.ve()

    def mau_hien_tai(self):
        """Màu của thanh theo giá trị hiện tại (None nếu chưa có giá trị)."""
        if self.gia_tri is None:
            return None
        ti_le = self.gia_tri / self.toi_da
        for nguong, mau in self.cac_moc[:-1]:
            if ti_le < nguong:
                return mau
        return self.cac_moc[-1][1]

    def ve(self):
        self.delete("all")
        rong, cao = kich_thuoc_canvas(self)
        x0, x1 = 1, rong - 1
        y0, y1 = 2, cao - 2
        if x1 <= x0 or y1 <= y0:
            return
        # rãnh nền
        self.create_rectangle(x0, y0, x1, y1, fill=MAU_RANH, outline=MAU_VIEN)
        # phần đã đạt
        if self.gia_tri is not None and self.gia_tri > 0:
            do_dai = max(3, (x1 - x0) * self.gia_tri / self.toi_da)
            self.create_rectangle(x0, y0, x0 + do_dai, y1, fill=self.mau_hien_tai(), outline="")
        # vạch chia mốc màu
        for nguong, _ in self.cac_moc[:-1]:
            x = x0 + (x1 - x0) * nguong
            self.create_line(x, y0, x, y1, fill="white", width=2)
