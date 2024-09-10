import math


class SteelPipe:
    # プロパティ: 円形鋼管の寸法 (mm)
    # d: 直径, t: 板厚
    def __init__(self, d=0, t=0):
        self.d = d
        self.t = t

    def valid_size(self):
        # 寸法のチェック
        # 戻り値 False: 寸法に誤りがある, True: 正常
        if (self.d < 10.0) or (self.t < 0.1) or (self.d < 2 * self.t):
            return False
        else:
            return True

    @property
    def area(self):
        # 戻り値: 断面積 (cm2)
        if self.valid_size():
            t = 0.1 * self.t  # mm -> cm
            r1 = 0.1 * self.d  # 外径
            r2 = r1 - 2.0 * t  # 内径
            return (r1**2 - r2**2) * math.pi / 4.0
        else:
            return 0

    @property
    def ixy(self):
        # 戻り値: 断面2次モーメント (cm4)
        if self.valid_size():
            t = 0.1 * self.t  # mm -> cm
            r1 = 0.1 * self.d  # 外径
            r2 = r1 - 2.0 * t  # 内径
            return (r1**4 - r2**4) * math.pi / 64.0
        else:
            return 0

    @property
    def zxy(self):
        # 戻り値: 断面係数 (cm3)
        if self.valid_size():
            return self.ixy / (0.1 * (self.d / 2.0))
        else:
            return 0

    def get_fc(self, lk=0.0, f=235):
        # 長期許容圧縮応力度の計算
        # lk: 座屈長さ (m), f: F値 (N/mm2)
        # 戻り値: 長期許容圧縮応力度 (N/mm2)
        if (not self.valid_size()) or (f < 0.1):
            return 0
        elif lk < 0.1:
            return f / 1.5  # 座屈を考慮しない

        ramda = math.sqrt(2023265.5 / (0.6 * f))  # 限界細長比 Λ (E = 205000)
        ixy = math.sqrt(self.ixy / self.area)  # 断面2次半径
        ramda1 = 100.0 * lk / ixy  # 細長比 λ
        ramda2 = (ramda1 / ramda) ** 2  # (λ / Λ) ^ 2
        if ramda1 < ramda:
            return f * (1.0 - 0.4 * ramda2) / (1.5 + 0.667 * ramda2)
        else:
            return 0.277 * f / ramda2

    def get_na(self, lk=0.0, f=235):
        # 長期軸耐力の計算
        # lk: 座屈長さ (m), f: F値 (N/mm2)
        # 戻り値: 長期軸耐力 (kN)
        return 0.1 * self.area * self.get_fc(lk, f)  # N -> kN

    def get_ma(self, f=235):
        # 曲げ耐力の計算
        # 戻り値: 長期曲げ耐力 (kN.m)
        return 0.001 * self.zxy * f / 1.5  # N.cm -> kN.m
