# RC梁の断面計算
# 基底クラス RCBase は RC関連の共通事項を定義したもの、その派生クラス RCBeam は
# RC梁の断面計算関連のものです
# RCBase は RC柱の断面計算を行う RCColumn でも基底クラスとして使用しています
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


class RCBeam(RCBase):
    # RC梁の計算を行う派生クラス
    def calc_beam(self, size="", bar="", st="", load=0, ql_method=1, qs_method=0, alpha=1):
        # 梁の許容曲げ・許容せん断力の計算
        # size:コンクリート断面をあらわす文字列, bar:主筋本数・径をあらわす文字列
        # st:スタラップ筋本数・間隔・径をあらわす文字列, load = 0:長期 1:短期
        # ql_method 長期許容せん断力の制御 0:ひび割れを許容しない, 1:ひび割れを許容する
        # qs_method 短期許容せん断力の制御 0:損傷制御, 1:大地震動に対する安全性確保
        # alpha:M/Qdによる割増係数
        section = self.get_section(size)
        if section is None:
            print("断面寸法の指定に誤りがある")
            return
        # bar_main[]
        # 0:引張1段筋本数, 1:引張2段筋本数, 2:圧縮1段筋本数, 3:圧縮2段筋本数, 4:主筋径
        bar_main = self.get_bar_main(bar)
        if bar_main is None:
            print("主筋本数指定に誤りがある")
            return
        # bar_st[] 0:ST本数, 1:ST間隔, 2:ST径
        bar_st = self.get_bar_st(st)
        if bar_st is None:
            print("スタラップ筋の指定に誤りがある")
            return

        # 許容曲げの計算
        # dt:コンクリート縁から引張鉄筋重心まで, dc:コンクリート縁から圧縮鉄筋重心まで
        dt = self.bar_dt(bar_main[0], bar_main[1], bar_main[4], bar_st[2])
        dc = self.bar_dt(bar_main[2], bar_main[3], bar_main[4], bar_st[2])
        if (dt + dc) > section[1]:
            print("断面の有効せいが確保できない")
            return
        # at:引張鉄筋の総断面積, ac:圧縮鉄筋の総断面積
        at = (bar_main[0] + bar_main[1]) * self.bar_area(bar_main[4])
        ac = (bar_main[2] + bar_main[3]) * self.bar_area(bar_main[4])
        # fc:コンクリートの許容圧縮応力度, ft:鉄筋の許容応力度
        fc = self.concrete_fc()
        ft = self.bar_ft_main(bar_main[4])
        # ma:許容曲げ
        ma = self.beam_ma(section[0], section[1], at, ac, dt, dc, ft[load], fc[load])

        # 許容せん断力の計算
        qa = 0  # 許容せん断力
        fs = self.concrete_fs()  # コンクリートの許容せん断応力度
        ft = self.bar_ft_shear()  # 鉄筋の許容応力度
        sd = section[1] - dt  # 有効せい
        pw = bar_st[0] * self.bar_area(bar_st[2]) / section[0] / bar_st[1]  # せん断補強筋比
        if load == 0:
            qa = self.beam_qal(section[0], sd, fs[0], ft[0], pw, ql_method, alpha)
        else:
            qa = self.beam_qas(section[0], sd, fs[1], ft[1], pw, qs_method, alpha)

        return (self.out_form(ma), self.out_form(qa))

    def get_section(self, s):
        # 文字列 s (幅 * せい) から部材寸法を取得
        section = []
        arr = s.split("*")
        try:
            for i in range(len(arr)):
                section.append(float(arr[i]))
        except ValueError:
            return
        if len(section) != 2:
            return
        else:
            return section

    def get_bar_main(self, s):
        # 文字列 s (引張1段筋/2段筋 - 圧縮1段筋/2段筋 - 鉄筋径) から主筋情報を取得
        # 戻り値 bar[]
        # 0:引張1段筋本数, 1:引張2段筋本数, 2:圧縮1段筋本数, 3:圧縮2段筋本数, 4:鉄筋径
        def bar_num(s):
            # 鉄筋本数文字列(1段筋/2段筋)を分解
            num = [0 for i in range(2)]
            try:
                if s.count("/") == 0:
                    num[0] = int(s)
                else:
                    arr = s.split("/")
                    if len(arr) != 2:
                        return
                    num[0] = int(arr[0])
                    num[1] = int(arr[1])
            except ValueError:
                return
            return num

        bar = []
        arr = s.split("-")
        if len(arr) != 3:
            return
        for i in range(2):
            num = bar_num(arr[i])
            if num is None:
                return
            bar.append(num[0])
            bar.append(num[1])
        if self.valid_bar_name(arr[2]):
            bar.append(arr[2])
            return bar
        else:
            return

    def get_bar_st(self, s):
        # 文字列 s (ST本数 - ST径 @ 鉄筋間隔) からスタラップ情報を取得
        # 戻り値 [] 0:ST本数, 1:ST間隔, 2:ST径
        n = 2  # ST本数
        pitch = 0  # ST間隔
        name = ""  # ST径
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

    def beam_ma(self, b, d, at, ac, dt, dc, ft, fc):
        # 許容曲げの計算
        # b:梁幅, d:梁せい, at:引張鉄筋の総断面積, ac:圧縮鉄筋の総断面積,
        # dt:コンクリート縁から引張鉄筋の重心位置, dc:コンクリート縁から圧縮鉄筋の重心位置
        # ft:鉄筋の許容応力度, fc:コンクリートの許容圧縮応力度
        # 戻り値　許容曲げ(kN.m)
        sd = d - dt  # 有効せい
        pt = at / (b * sd)  # 引張鉄筋比
        gam = ac / at  # 複筋比
        dc1 = dc / sd
        n = self.bar_concrete()  # ヤング係数比
        t1 = n * (1 + gam) - gam
        t2 = 2 * (n * (1 + gam * dc1) - gam * dc1) / pt
        t1 = math.sqrt(t1 * t1 + t2) - (n * (1 + gam) - gam)
        xn1 = pt * t1  # 中立軸比
        c0 = n * (1 - xn1) * (3 - xn1) - gam * (n - 1) * (xn1 - dc1) * (3 * dc1 - xn1)
        c1 = pt * fc * c0 / (3 * xn1)
        c2 = pt * ft * c0 / (3 * n * (1 - xn1))
        return min(c1, c2) * b * sd * sd / 1000000  # N.mm -> kN.m

    def beam_qal(self, b, sd, fs, ft, pw, method=1, alpha=1):
        # 長期許容せん断力
        # b:梁幅, sd:有効せい, fs:コンクリートの許容せん断応力度, ft:鉄筋の許容応力度
        # pw:せん断補強筋比, alpha:M/Qdによる割増係数
        # method = 0:ひび割れを許容しない, 1:ひび割れを許容する
        # 戻り値 長期許容せん断力(kN)
        alpha = min(alpha, 2)
        if method == 0:
            return b * 0.875 * sd * alpha * fs / 1000  # N -> kN
        else:
            ss = min(alpha, 2) * fs  # 許容せん断応力度
            pw = min(pw, 0.006)  # せん断補強筋比
            if pw > 0.002:
                ss += 0.5 * ft * (pw - 0.002)
            return b * 0.875 * sd * ss / 1000.0  # N -> kN

    def beam_qas(self, b, sd, fs, ft, pw, method=0, alpha=1):
        # 短期許容せん断力
        # b:梁幅, sd:有効せい, fs:コンクリートの許容せん断応力度, ft:鉄筋の許容応力度
        # pw:せん断補強筋比, alpha:M/Qdによる割増係数
        # method = 0:損傷制御, 1:大地震動に対する安全性確保
        # 戻り値 短期許容せん断力(kN)
        alpha = min(alpha, 2)
        if method == 0:
            ss = 2 * alpha * fs / 3  # 許容せん断応力度
            pw = min(pw, 0.012)  # せん断補強筋比
            if pw > 0.002:
                ss += 0.5 * ft * (pw - 0.002)
            return b * 0.875 * sd * ss / 1000.0  # N -> kN
        else:
            ss = alpha * fs  # 許容せん断応力度
            pw = min(pw, 0.012)  # せん断補強筋比
            if pw > 0.002:
                ss += 0.5 * ft * (pw - 0.002)
            return b * 0.875 * sd * ss / 1000.0  # N -> kN


# 以下は計算例
obj = RCBeam(fc=24)
(ma, qa) = obj.calc_beam(size="300*600", bar="3/2-3-D25", st="D13@200", load=1, qs_method=1)
print("Ma = " + str(ma) + ", Qa = " + str(qa))
