import math


class SteelBox:
    # プロパティ: 角形鋼管の寸法 (mm)
    # dx: x方向の辺長, dy: y方向の辺長, t: 板厚, r: 端部のアール
    def __init__(self, dx=0, dy=0, t=0, r=0):
        self.dx = dx
        self.dy = dy
        self.t = t
        self.r = r

    def valid_size(self):
        # 寸法のチェック
        # 戻り値 False: 寸法に誤りがある, True: 正常
        if (self.dx < 10.0) or (self.dy < 10.0) or (self.t < 0.1) or (self.r < -0.1):
            return False
        elif (self.dx < 2 * self.t) or (self.dy < 2 * self.t):
            return False
        elif (self.dx < 2 * self.r) or (self.dy < 2 * self.r):
            return False
        else:
            return True

    @property
    def area(self):
        # 戻り値: 断面積 (cm2)
        if self.valid_size():
            dx = 0.1 * self.dx  # mm -> cm
            dy = 0.1 * self.dy
            t = 0.1 * self.t
            r = 0.1 * self.r
            if r < 0.001:
                return dx * dy - (dx - 2.0 * t) * (dy - 2.0 * t)
            else:
                return 2.0 * (dx + dy - 4.0 * r) * t + (2 * r * t - t * t) * math.pi
        else:
            return 0

    @property
    def ix(self):
        # 戻り値: x軸回りの断面2次モーメント (cm4)
        if self.valid_size():
            b = 0.1 * self.dx  # mm -> cm
            d = 0.1 * self.dy
            t = 0.1 * self.t
            r = 0.1 * self.r
            b1 = b - 2.0 * t
            d1 = d - 2.0 * t
            if r < 0.001:
                return (b * d**3 - b1 * d1**3) / 12.0
            else:
                b2 = b - 2.0 * r
                d2 = d - 2.0 * r
                r1 = r - t
                c1 = (4.0 * (r**2 + r1 * r + r1**2)) / (3.0 * math.pi * (r1 + r)) + d2 / 2.0
                return (b2 * (d**3 - d1**3) + 2.0 * t * d2**3) / 12.0 + math.pi * (r**2 - r1**2) * c1 * c1
        else:
            return 0

    @property
    def iy(self):
        # 戻り値: y軸回りの断面2次モーメント (cm4)
        if self.valid_size():
            b = 0.1 * self.dy  # mm -> cm
            d = 0.1 * self.dx
            t = 0.1 * self.t
            r = 0.1 * self.r
            b1 = b - 2.0 * t
            d1 = d - 2.0 * t
            if r < 0.001:
                return (b * d**3 - b1 * d1**3) / 12.0
            else:
                b2 = b - 2.0 * r
                d2 = d - 2.0 * r
                r1 = r - t
                c1 = (4.0 * (r**2 + r1 * r + r1**2)) / (3.0 * math.pi * (r1 + r)) + d2 / 2.0
                return (b2 * (d**3 - d1**3) + 2.0 * t * d2**3) / 12.0 + math.pi * (r**2 - r1**2) * c1 * c1
        else:
            return 0

    @property
    def zx(self):
        # 戻り値: 強軸回りの断面係数 (cm3)
        if self.valid_size():
            return self.ix / (0.1 * (self.dy / 2.0))
        else:
            return 0

    @property
    def zy(self):
        # 戻り値: 弱軸回りの断面係数 (cm3)
        if self.valid_size():
            return self.iy / (0.1 * (self.dx / 2.0))
        else:
            return 0

    def get_fc(self, lkx=0.0, lky=0.0, f=235):
        # 長期許容圧縮応力度の計算
        # lkx: x軸回りの座屈長さ (m), lky: y軸回りの座屈長さ (m), f: F値 (N/mm2)
        # 戻り値: 長期許容圧縮応力度 (N/mm2)
        if (not self.valid_size()) or (f < 0.1):
            return 0
        elif lkx < 0.1:
            return f / 1.5  # 座屈を考慮しない
        elif lky < 0.1:
            lky = lkx  # lky が省略された場合は lky = lkx

        ramda = math.sqrt(2023265.5 / (0.6 * f))  # 限界細長比 Λ (E = 205000)
        ix = math.sqrt(self.ix / self.area)  # x軸回り断面2次半径
        iy = math.sqrt(self.iy / self.area)  # y軸回り断面2次半径
        ramda1 = 100.0 * lkx / ix  # 細長比 λ
        if (lky / iy) > (lkx / ix):
            ramda1 = 100.0 * lky / iy

        ramda2 = (ramda1 / ramda) ** 2  # (λ / Λ) ^ 2
        if ramda1 < ramda:
            return f * (1.0 - 0.4 * ramda2) / (1.5 + 0.667 * ramda2)
        else:
            return 0.277 * f / ramda2

    def get_na(self, lkx=0.0, lky=0.0, f=235):
        # 長期軸耐力の計算
        # lkx: x軸回りの座屈長さ (m), lky: y軸回りの座屈長さ (m), f: F値 (N/mm2)
        # 戻り値: 長期軸耐力 (kN)
        return 0.1 * self.area * self.get_fc(lkx, lky, f)  # N -> kN

    def get_max(self, f=235):
        # x軸回りの曲げ耐力の計算
        # 戻り値: 長期曲げ耐力 (kN.m)
        return 0.001 * self.zx * f / 1.5  # N.cm -> kN.m

    def get_may(self, f=235):
        # y軸回りの曲げ耐力の計算
        # 戻り値: 長期曲げ耐力 (kN.m)
        return 0.001 * self.zy * f / 1.5  # N.cm -> kN.m
