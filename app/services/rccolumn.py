# RC柱の断面計算
# 基底クラス RCBase は RC関連の共通事項を定義したもの、その派生クラス RCColumn は
# RC柱の断面計算関連のものです
# RCBase は RC梁の断面計算を行う RCBeam でも基底クラスとして使用しています
# 配布の便宜上2つのクラスを1ファイルにまとめていますが、通常は基底クラスを別ファイルにしてください
# 例題は本ファイルの末尾にあります

import math


class RCBase:
    # RC関連共通の基底クラス
    def __init__(self, fc=21, bar_main="SD345", bar_shear="SD295", bar_cv=40, num_form=2):
        # fc:コンクリートの設計強度(N/mm2), bar_main:主筋材料, bar_shear:せん断補強筋材料
        # bar_cv:せん断補強筋のかぶり厚
        # num_form: 出力時の小数以下の桁数(-1の場合は四捨五入しない)
        self.fc = fc
        if self.valid_bar_mat(bar_main):
            self.bar_mat_main = bar_main  # 主筋材料
        else:
            self.bar_mat_main = "SD345"
        if self.valid_bar_mat(bar_shear):
            self.bar_mat_shear = bar_shear  # せん断補強筋材料
        else:
            self.bar_mat_shear = "SD295"
        self.bar_cv = bar_cv
        self.num_form = num_form

    def concrete_fc(self):
        # コンクリートの許容圧縮応力度
        # 戻り値 [] 0:長期許容圧縮応力度, 1:短期許容圧縮応力度(N/mm2)
        return [self.fc / 3, self.fc * 2 / 3]

    def concrete_fs(self):
        # コンクリートの許容せん断応力度
        # 戻り値 [] 0:長期許容せん断応力度, 1:短期許容せん断応力度(N/mm2)
        fs = min(self.fc / 30, 0.49 + 0.01 * self.fc)
        return [fs, 1.5 * fs]

    def bar_concrete(self):
        # コンクリートに対する鉄筋のヤング係数比
        # 戻り値 ヤング係数比
        if self.fc <= 27:
            return 15
        elif self.fc <= 36:
            return 13
        elif self.fc <= 48:
            return 11
        else:
            return 9

    def valid_bar_name(self, bar_name):
        # 鉄筋径名称 bar_name の検証
        # 戻り値 0:鉄筋径名称が不正
        #       1:D25以下の鉄筋, 2:D29以上の鉄筋
        name = ["D10", "D13", "D16", "D19", "D22", "D25", "D29", "D32", "D35", "D38", "D41"]
        try:
            pos = name.index(bar_name)
            if pos < 6:
                return 1
            else:
                return 2
        except ValueError:
            return 0

    def valid_bar_mat(self, bar_mat):
        # 鉄筋材料名称 bar_mat の検証
        # 戻り値 0:鉄筋材料名称が不正
        name = ("SD295", "SD345", "SD390", "SD490")
        if bar_mat in name:
            return 1
        else:
            return 0

    def bar_area(self, bar_name):
        # 戻り値 鉄筋径名称 bar_name の断面積(mm2)
        area = {
            "D10": 71,
            "D13": 127,
            "D16": 199,
            "D19": 287,
            "D22": 387,
            "D25": 507,
            "D29": 642,
            "D32": 794,
            "D35": 957,
            "D38": 1140,
            "D41": 1340,
        }
        return area[bar_name]

    def bar_ft_main(self, bar_name):
        # 主筋の許容応力度
        # bar_name: 鉄筋径の名称
        # 戻り値 [] 0:長期許容応力度, 1:短期許容応力度(N/mm2)
        ft = {"SD295": [195, 295], "SD345": [215, 345], "SD390": [215, 390], "SD490": [215, 490]}
        if self.valid_bar_name(bar_name) == 2:  # D29以上
            ft[self.bar_mat_main][0] = 195
        return ft[self.bar_mat_main]

    def bar_ft_shear(self):
        # せん断補強筋の許容応力度
        # 戻り値 [] 0:長期許容応力度, 1:短期許容応力度(N/mm2)
        ft = {"SD295": [195, 295], "SD345": [195, 345], "SD390": [195, 390], "SD490": [195, 490]}
        return ft[self.bar_mat_shear]

    def bar_dt(self, n1, n2, bar_main, bar_st):
        # n1:1段筋の本数, n2:2段筋の本数, bar_main:主筋の名称, bar_st:せん断補強筋の名称
        # 戻り値 コンクリート縁から鉄筋重心までの距離(mm)
        # dm1:鉄筋の外径
        dm = {
            "D10": 11,
            "D13": 14,
            "D16": 18,
            "D19": 21,
            "D22": 25,
            "D25": 28,
            "D29": 33,
            "D32": 36,
            "D35": 40,
            "D38": 43,
            "D41": 47,
        }
        # d1:コンクリート縁から1段筋重心まで
        d1 = self.bar_cv + dm[bar_st] + 0.5 * dm[bar_main]
        if n2 > 0:
            # d2:1段筋/2段筋間のあき
            d2 = int(bar_main[1:])
            d2 = max(1.5 * d2, 31.25)  # 31.25 = 25*1.25 (骨材寸法 25mm)
            # d2 -> コンクリート縁から2段筋重心まで
            d2 = d1 + d2 + dm[bar_main]
            return (n1 * d1 + n2 * d2) / (n1 + n2)
        else:
            return d1

    def out_form(self, val):
        # 値 val を出力用の値に整形
        if self.num_form < 0:
            return val
        else:
            return round((10**self.num_form) * val) / (10**self.num_form)


class RCColumn(RCBase):
    # RC柱の計算を行う派生クラス
    def calc_column(self, size="", bar="", hoop="", force=0, load=0, qs_method=0, alpha=1):
        # 柱の許容曲げ・許容せん断力の計算
        # size:コンクリート断面をあらわす文字列, bar:主筋本数・径をあらわす文字列
        # hoop:HOOP筋本数・間隔・径をあらわす文字列, force:軸力(kN), load = 0:長期 1:短期
        # qs_method 短期許容せん断力の制御 0:損傷制御, 1:大地震動に対する安全性確保
        # alpha:M/Qdによる割増係数
        section = self.get_section(size)
        if section is None:
            print("断面寸法の指定に誤りがある")
            return
        # bar_main[]
        # 0:鉄筋本数, 1:主筋径
        bar_main = self.get_bar_main(bar)
        if bar_main is None:
            print("主筋本数の指定に誤りがある")
            return
        # bar_hoop[] 0:HOOP本数, 1:HOOP間隔, 2:HOOP径
        bar_hoop = self.get_bar_hoop(hoop)
        if bar_hoop is None:
            print("フープ筋の指定に誤りがある")
            return

        # 許容曲げの計算
        ma = 0  # 許容曲げ
        # dt:コンクリート縁から引張鉄筋重心まで
        dt = self.bar_dt(bar_main[0], 0, bar_main[1], bar_hoop[2])
        # at:引張鉄筋の総断面積
        at = bar_main[0] * self.bar_area(bar_main[1])
        # fc:コンクリートの許容圧縮応力度, ft:鉄筋の許容応力度
        fc = self.concrete_fc()
        ft = self.bar_ft_main(bar_main[1])
        if len(section) == 2:
            # 長方形
            if dt > section[1]:
                print("断面の有効せいが確保できない")
                return
            ma = self.col_ma_rect(section[0], section[1], at, dt, ft[load], fc[load], force)
        else:
            # 円形
            if 2 * dt > section[0]:
                print("断面の有効せいが確保できない")
                return
            ma = self.col_ma_round(section[0], at, dt, ft[load], fc[load], force)

        # 許容せん断力の計算
        b = section[0]
        if len(section) == 1:
            # 円形断面は等価な正方形に置き換える
            d = math.sqrt(math.pi * b * b / 4)
            b = d
        else:
            d = section[1]
        qa = 0  # 許容せん断力
        fs = self.concrete_fs()  # コンクリートの許容せん断応力度
        ft = self.bar_ft_shear()  # 鉄筋の許容応力度
        pw = bar_hoop[0] * self.bar_area(bar_hoop[2]) / b / bar_hoop[1]  # せん断補強筋比
        sd = d - dt  # 有効せい
        if load == 0:
            qa = self.col_qal(b, sd, fs[0], ft[0], pw, alpha)
        else:
            qa = self.col_qas(b, sd, fs[1], ft[1], pw, qs_method, alpha)

        return (self.out_form(ma), self.out_form(qa))

    def get_section(self, s):
        # 文字列 s (幅 * せい) または (直径) から部材寸法を取得
        section = []
        if isinstance(s, int):
            section.append(s)
        else:
            try:
                if s.count("*") == 0:
                    section.append(int(s))
                else:
                    arr = s.split("*")
                    for i in range(len(arr)):
                        section.append(int(arr[i]))
                    if len(section) != 2:
                        return
            except ValueError:
                return
        return section

    def get_bar_main(self, s):
        # 文字列 s (鉄筋本数 - 鉄筋径) から主筋情報を取得
        # 戻り値 bar[]
        # 0:鉄筋本数, 1:鉄筋径
        bar = []
        arr = s.split("-")
        if len(arr) != 2:
            return
        try:
            bar.append(int(arr[0]))
        except ValueError:
            return
        if self.valid_bar_name(arr[1]):
            bar.append(arr[1])
            return bar
        else:
            return

    def get_bar_hoop(self, s):
        # 文字列 s (HOOP本数 - HOOP径 @ 鉄筋間隔) からスタラップ情報を取得
        # 戻り値 [] 0:HOOP本数, 1:HOOP間隔, 2:ST径
        n = 2  # HOOP本数
        pitch = 0  # HOOP間隔
        name = ""  # HOOP径
        arr = s.split("@")
        if len(arr) != 2:
            return
        try:
            if arr[0].count("-"):
                ar1 = arr[0].split("-")
                n = int(ar1[0])
                name = ar1[1]
            else:
                name = arr[0]
            pitch = int(arr[1])
        except ValueError:
            return
        if (n < 1) or (pitch < 10):
            return
        elif self.valid_bar_name(name):
            bar = []
            bar.append(n)
            bar.append(pitch)
            bar.append(name)
            return bar

    def col_ma_rect(self, b, d, at, dt, ft, fc, force):
        # 長方形柱の許容曲げ
        # b:幅, d:せい, at:引張鉄筋の総断面積, dt:コンクリート縁から引張鉄筋の重心位置,
        # ft:鉄筋の許容応力度, fc:コンクリートの許容圧縮応力度, force:軸力(kN)
        # 戻り値　許容曲げ(kN.m)
        n = self.bar_concrete()  # ヤング係数比
        bd = b * d
        pt = at / bd  # 引張鉄筋比
        ae = bd * (2 * n * pt + 1)  # 等価断面積
        rnc = min(ae * fc, ae * ft / n)  # 限界圧縮力
        rnt = -2 * ft * bd * pt  # 限界引張力
        rd1 = dt / d  # dt/d = dc/d
        xn1b = (1 - rd1) * n * fc / (ft + n * fc)  # 釣り合い中立軸比
        # 中立軸比 xn1 の値に対応する軸力
        # bn1: xn1 = 1.0
        # bn2: xn1 = xn1b
        # bn3: xn1 = 0
        bn1 = fc * bd * (0.5 + n * pt)
        bn2 = fc * bd * (0.5 * xn1b * xn1b + n * pt * (2 * xn1b - 1)) / xn1b
        bn3 = -ft * pt * bd / (1 - rd1)
        bd2 = b * d * d
        dn1 = 1000 * force  # kN -> N
        rma = 0  # 許容曲げ
        xn1 = 0  # 中立軸比
        if dn1 > rnc:
            print("設計軸力が限界圧縮力を上回る")
        elif dn1 < rnt:
            print("設計軸力が限界引張力を下回る")
        elif dn1 > bn1:
            xn1 = (0.5 + n * pt) / (1 + 2 * n * pt - dn1 / (bd * fc))
            rma = (
                fc
                * bd2
                * (xn1 * xn1 - xn1 + 0.33 + (2 * xn1 * xn1 - 2 * xn1 + 2 * rd1 * rd1 - 2 * rd1 + 1) * n * pt)
                / xn1
            )
            rma = rma + (0.5 - xn1) * dn1 * d
        elif dn1 > bn2:
            r1 = 2 * n * pt - dn1 / (bd * fc)
            r1 = max(r1 * r1 + 2 * n * pt, 0.001)
            xn1 = dn1 / (bd * fc) - 2 * n * pt + math.sqrt(r1)
            rma = (
                fc
                * bd2
                * (0.33 * xn1 * xn1 * xn1 + (2 * xn1 * xn1 - 2 * xn1 + 2 * rd1 * rd1 - 2 * rd1 + 1) * n * pt)
                / xn1
            )
            rma += (0.5 - xn1) * dn1 * d
        elif dn1 > bn3:
            r1 = 2 * n * pt + n * dn1 / (bd * ft)
            r1 = max(r1 * r1 + 2 * (n * pt + 0.9 * n * dn1 / (bd * ft)), 0.001)
            xn1 = -n * dn1 / (bd * ft) - 2 * n * pt + math.sqrt(r1)
            rma = (
                ft
                * bd2
                * (0.33 * xn1 * xn1 * xn1 + (2 * xn1 * xn1 - 2 * xn1 + 2 * rd1 * rd1 - 2 * rd1 + 1) * n * pt)
            )
            rma /= n * (1 - xn1 - rd1)
            rma += (0.5 - xn1) * dn1 * d
        else:
            rma = (1 - 2 * rd1) * bd2 * (pt * ft + 0.5 * dn1 / bd)

        return rma / 1000000  # N.mm -> kN.m

    def col_ma_round(self, d, ag, dt, ft, fc, force):
        # 円形柱の許容曲げ
        # d:直径, ag:鉄筋の総断面積, dt:コンクリート縁から引張鉄筋の重心位置,
        # ft:鉄筋の許容応力度, fc:コンクリートの許容圧縮応力度, force:軸力(kN)
        # 戻り値　許容曲げ(kN.m)
        n = self.bar_concrete()  # ヤング係数比
        sr = d / 2  # 半径
        ar = math.pi * sr * sr  # 断面積
        pg = ag / ar  # 鉄筋比
        rd1 = (sr - dt) / sr  # 鉄筋位置の半径 / 半径
        rnc = ar * (fc + pg * ft)  # 限界圧縮力
        rnt = -ar * pg * ft  # 限界引張力
        sx = sr - (1.0 - dt / d) * n * fc * d / (ft + n * fc)
        sy = math.sqrt(sr * sr - sx * sx)
        ttb = 0  # 釣合い中立軸の角度
        if sx > 0.0:
            ttb = math.atan(sy / sx)
        else:
            ttb = math.atan(-sy / sx) + math.pi / 2
        cs = math.cos(ttb)
        sn = math.sin(ttb)
        # 中立軸の角度θに対応する軸力
        # bn1: θ = π
        # bn2: θ = ttb
        # bn3: θ = 0
        bn1 = 0.5 * fc * ar * (n * pg + 1)
        bn2 = (fc * sr * sr / (1 - cs)) * (0.33 * sn * (2 + cs * cs) - ttb * cs - n * pg * math.pi * cs)
        bn3 = -ar * ft * pg / (rd1 + 1)
        dn1 = 1000 * force  # kN -> N
        rma = 0  # 許容曲げ
        if dn1 > rnc:
            print("設計軸力が限界圧縮力を上回る")
        elif dn1 < rnt:
            print("設計軸力が限界引張力を下回る")
        elif dn1 > bn1:
            xn1 = -(1.0 + n * pg) / (dn1 / (fc * math.pi * sr * sr) - n * pg - 1)
            rma = (fc * sr * sr * sr / xn1) * (
                0.25 * math.pi * (1 + 2 * n * pg * rd1 * rd1)
                + math.pi * (1 + n * pg) * (xn1 - 1.0) * (xn1 - 1.0)
            )
            rma = rma - sr * dn1 * (xn1 - 1)
        elif dn1 > bn2:
            tt1 = ttb
            tt2 = math.pi
            # ttbとπの間にある中立軸の角度を反復計算(1/2分割法)により求める
            while True:
                tt = (tt1 + tt2) / 2
                cs = math.cos(tt)
                sn = math.sin(tt)
                cs2 = cs * cs
                an = (fc * sr * sr / (1 - cs)) * (0.33 * sn * (2 + cs2) - tt * cs - n * pg * math.pi * cs)
                if ((dn1 - an) > 100.0) and ((tt2 - tt1) > 0.00001):
                    tt1 = tt
                elif ((dn1 - an) < -100.0) and ((tt2 - tt1) > 0.00001):
                    tt2 = tt
                else:
                    rma = (fc * sr * sr * sr / (1.0 - cs)) * (
                        tt * (0.25 + cs2)
                        - sn * cs * (1.08 + 0.17 * cs2)
                        + n * math.pi * pg * (0.5 * rd1 * rd1 + cs2)
                    )
                    rma += dn1 * sr * cs
                    break
        elif dn1 > bn3:
            tt1 = 0
            tt2 = ttb
            # ttbと0の間にある中立軸の角度を反復計算(1/2分割法)により求める
            while True:
                tt = (tt1 + tt2) / 2
                cs = math.cos(tt)
                sn = math.sin(tt)
                cs2 = cs * cs
                an = (ft * sr * sr / (n * (rd1 + cs))) * (
                    0.33 * sn * (2 + cs2) - tt * cs - n * pg * math.pi * cs
                )
                if (dn1 - an) > 100.0:
                    tt1 = tt
                elif (dn1 - an) < -100.0:
                    tt2 = tt
                else:
                    rma = (ft * sr * sr * sr / (n * (rd1 + cs))) * (
                        tt * (0.25 + cs2)
                        - sn * cs * (1.08 + 0.17 * cs2)
                        + n * math.pi * pg * (0.5 * rd1 * rd1 + cs2)
                    )
                    rma += dn1 * sr * cs
                    break
        else:
            rma = 0.5 * ar * sr * rd1 * (ft * pg + dn1 / ar)

        return rma / 1000000  # N.mm -> kN.m

    def col_qal(self, b, sd, fs, ft, pw, alpha=1):
        # 長期許容せん断力
        # b:幅, sd:有効せい, fs:コンクリートの許容せん断応力度, ft:鉄筋の許容応力度
        # pw:せん断補強筋比, alpha:M/Qdによる割増係数
        # method = 0:ひび割れを許容しない, 1:ひび割れを許容する
        # 戻り値 長期許容せん断力(kN)
        alpha = min(alpha, 1.5)
        return b * 0.875 * sd * alpha * fs / 1000  # N -> kN

    def col_qas(self, b, sd, fs, ft, pw, method=0, alpha=1):
        # 短期許容せん断力
        # b:幅, sd:有効せい, fs:コンクリートの許容せん断応力度, ft:鉄筋の許容応力度
        # pw:せん断補強筋比, alpha:M/Qdによる割増係数
        # method = 0:損傷制御, 1:大地震動に対する安全性確保
        # 戻り値 短期許容せん断力(kN)
        ss = 0  # 鉄筋による許容せん断力
        pw = min(pw, 0.012)  # せん断補強筋比
        if pw > 0.002:
            ss = 0.5 * ft * (pw - 0.002)
        if method == 0:
            alpha = min(alpha, 2)
            ss += 2 * alpha * fs / 3  # 許容せん断応力度
        else:
            ss += fs
        return b * 0.875 * sd * ss / 1000.0  # N -> kN


# 以下は計算例
obj = RCColumn()
(ma, qa) = obj.calc_column(size="600*600", bar="4-D22", hoop="D13@100", force=1350, load=1, qs_method=1)
print("Ma = " + str(ma) + ", Qa = " + str(qa))
