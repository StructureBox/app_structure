# 各種公式による荷重項の計算
# 最初にクラス Cmq の定義があります
# これを使用した例題は本ファイルの末尾にあります
# 例題の詳細は cmq.pdf の2ページ目にあります

import numpy


class Cmq:
    def __init__(self, q_fix=0):
        # q_fix = 0: 両端ピンのせん断力, 1: 両端固定のせん断力
        self.q_fix = q_fix

    def cmq_divide(self, al=0, p=0, count=1):
        # 等間隔に作用する集中荷重による荷重項
        # al: 部材長, p: 集中荷重, count: 荷重の個数
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        cmq = self.init_cmq()
        err = ""
        if al < 0.01:
            err = "部材長に誤りがある"
        elif (abs(p) < 0.01) or (count < 1):
            err = "荷重の値または個数に誤りがある"
        if err:
            print(err)
            return cmq
        w = al / (count + 1)
        a = 0
        for i in range(count):
            a += w
            cmq += self.type_point(al, p, a)
        return cmq

    def cmq_points(self, al=0, *arg):
        # 任意位置に作用する集中荷重による荷重項
        # al: 部材長, arg: 荷重1, 距離1, 荷重2, 距離2 ...
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        cmq = self.init_cmq()
        err = ""
        if al < 0.01:
            err = "部材長に誤りがある"
        elif len(arg) < 2:
            err = "荷重の個数に誤りがある"
        if err:
            print(err)
            return cmq
        for i in range(len(arg) // 2):
            cmq += self.type_point(al, arg[i * 2], arg[i * 2 + 1])
        if self.q_fix > 0:
            # 両端固定梁のせん断力に変換
            self.q0_to_qf(al, cmq)
        return cmq

    def cmq_zone(self, al=0, w=0, *arg):
        # 等分布荷重による荷重項
        # al: 部材長, w: 等分布荷重
        # arg: 分割点の座標 x座標1, y座標1, x座標2, y座標2 ...
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        cmq = self.init_cmq()
        err = ""
        if al < 0.01:
            err = "部材長に誤りがある"
        elif abs(w) < 0.01:
            err = "荷重の値に誤りがある"
        elif len(arg) < 2:
            err = "座標値の個数に誤りがある"
        if err:
            print(err)
            return cmq
        # pos[i][j] 分割点iの座標 j = 0:X, 1:Y
        pos = []
        pos.append([0, 0])  # 部材左端
        for i in range(len(arg) // 2):
            x = arg[i * 2]
            y = arg[i * 2 + 1]
            if (x < -0.01) or (y < -0.01) or ((x - al) > 0.01):
                print("座標値の指定に誤りがある")
                return cmq
            pos.append([x, y])
        pos.append([al, 0])  # 部材右端
        for i in range(len(pos) - 1):
            x1 = pos[i][0]
            y1 = pos[i][1]
            x2 = pos[i + 1][0]
            y2 = pos[i + 1][1]
            if (abs(x2 - x1) < 0.01) or (abs(y1 + y2) < 0.01):
                continue
            cmq += self.type_zone(al, x1, x2 - x1, w, y1, y2)
        if self.q_fix > 0:
            # 両端固定梁のせん断力に変換
            self.q0_to_qf(al, cmq)
        return cmq

    def type_point(self, al, p, a):
        # 集中荷重による荷重項
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        # al: 部材長
        #              p|
        #               V
        #           +===*=========+
        #             a
        #           +---+

        res = self.init_cmq()
        if a > al:
            return res
        b = al - a
        res[0] = -p * a * b * b / al / al
        res[1] = p * a * a * b / al / al
        res[3] = p * b / al
        res[4] = p * a / al
        if a < 0.5 * al:
            res[2] = 0.5 * p * a
        else:
            res[2] = 0.5 * p * b
        return res

    def type_zone(self, al, a, b, w, awl, bwl):
        # 等分布荷重による荷重項
        # al: 部材長, a: 始端から荷重開始位置まで, b: 荷重の作用長さ
        # w: 等分布荷重, awl: 荷重左端の高さ, bwl: 荷重右端の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        res = self.init_cmq()
        if b < 0.01:
            return res
        elif (awl < 0.01) and (bwl < 0.01):
            return res
        c = al - a - b
        if (a < 0.01) and (c < 0.01):
            # 全長にわたる荷重
            if (awl > 0.01) and (bwl > 0.01):
                # 台形荷重
                if abs(awl - bwl) < 0.01:
                    # 等分布
                    res = self.type_rect_full(al, w, awl)
                elif bwl > awl:
                    # 右上がりの等変分布
                    res = self.type_rect_full(al, w, awl)
                    res += self.type_tri_right_full(al, w, bwl - awl)
                else:
                    # 左上がりの等変分布
                    res = self.type_rect_full(al, w, bwl)
                    res += self.type_tri_left_full(al, w, awl - bwl)
            elif bwl > 0.01:
                # 右上がりの三角形荷重
                res = self.type_tri_right_full(al, w, bwl)
            else:
                # 左上がりの三角形荷重
                res = self.type_tri_left_full(al, w, awl)
        else:
            # 部材中間の荷重
            if (awl > 0.01) and (bwl > 0.01):
                # 台形荷重
                if abs(awl - bwl) < 0.01:
                    # 等分布
                    res = self.type_rect_part(al, a, b, w, awl)
                elif bwl > awl:
                    # 右上がりの等変分布
                    res = self.type_rect_part(al, a, b, w, awl)
                    res += self.type_tri_right_part(al, a, b, w, bwl - awl)
                else:
                    # 左上がりの等変分布
                    res = self.type_rect_part(al, a, b, w, bwl)
                    res += self.type_tri_left_part(al, a, b, w, awl - bwl)
            elif bwl > 0.01:
                # 右上がりの三角形荷重
                res = self.type_tri_right_part(al, a, b, w, bwl)
            else:
                # 左上がりの三角形荷重
                res = self.type_tri_left_part(al, a, b, w, awl)

        return res

    def type_rect_full(self, al, w, wl):
        # 部材全長に等分布荷重がある場合
        # al: 部材長, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        res = self.init_cmq()
        wa = w * wl * al  # 全荷重
        res[0] = -0.08333 * wa * al
        res[1] = -res[0]
        res[2] = 0.125 * wa * al
        res[3] = 0.5 * wa
        res[4] = res[3]
        return res

    def type_rect_part(self, al, a, b, w, wl):
        # 部材中間に等分布荷重がある場合
        # al: 部材長, a, b: 寸法, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        #
        #         +     *-----*
        #      wl |     |  w  |
        #         + +=============+
        #             a    b
        #           +---+-----+
        res = self.init_cmq()
        wa = w * wl * b  # 全荷重
        r1 = a / al
        r2 = b / al
        p1 = 2 * r1 + r2
        p2 = 3 * (r1**2) + 3 * r1 * r2 + (r2**2)
        p3 = 4 * (r1**3) + 6 * r2 * (r1**2) + 4 * r1 * (r2**2) + (r2**3)
        res[0] = -0.08333 * (6 * p1 - 8 * p2 + 3 * p3) * wa * al
        res[1] = 0.08333 * (4 * p2 - 3 * p3) * wa * al
        res[3] = 0.5 * (2 - p1) * wa
        res[4] = 0.5 * p1 * wa
        if (r1 + r2) < 0.5:
            res[2] = 0.25 * p1 * wa * al
        elif r1 > 0.5:
            res[2] = 0.25 * (2 - p1) * wa * al
        else:
            p4 = (1 - 2 * r1) ** 2 / (2 * r2)
            res[2] = 0.25 * (2 - p1 - p4) * wa * al
        return res

    def type_tri_right_full(self, al, w, wl):
        # 部材全長に右上がりの直角三角荷重がある場合
        # al: 部材長, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        res = self.init_cmq()
        wa = 0.5 * w * wl * al  # 全荷重
        res[0] = -0.06667 * wa * al
        res[1] = 0.1 * wa * al
        res[2] = 0.125 * wa * al
        res[3] = 0.3333 * wa
        res[4] = 0.6667 * wa
        return res

    def type_tri_left_full(self, al, w, wl):
        # 部材全長に左上がりの直角三角荷重がある場合
        # al: 部材長, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        res = self.init_cmq()
        wa = 0.5 * w * wl * al  # 全荷重
        res[0] = -0.1 * wa * al
        res[1] = 0.06667 * wa * al
        res[2] = 0.125 * wa * al
        res[3] = 0.6667 * wa
        res[4] = 0.3333 * wa
        return res

    def type_tri_right_part(self, al, a, b, w, wl):
        # 部材中間に右上がりの直角三角荷重がある場合
        # al: 部材長, a, b: 寸法, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        #
        #         +          *
        #         |        * |
        #      wl |      * w |
        #         + +===+====+===+
        #             a    b
        #           +---+----+

        res = self.init_cmq()
        wa = 0.5 * w * wl * b  # 全荷重
        r1 = a / al
        r2 = b / al
        p1 = 3 * r1 + 2 * r2
        p2 = 6 * (r1**2) + 8 * r1 * r2 + 3 * (r2**2)
        p3 = 10 * (r1**3) + 20 * r2 * (r1**2) + 15 * r1 * (r2**2) + 4 * (r2**3)
        res[0] = -0.03333 * (10 * p1 - 10 * p2 + 3 * p3) * wa * al
        res[1] = 0.03333 * (5 * p2 - 3 * p3) * wa * al
        res[3] = 0.3333 * (3 - p1) * wa
        res[4] = 0.3333 * p1 * wa
        if (r1 + r2) < 0.5:
            res[2] = 0.1667 * p1 * wa * al
        elif r1 > 0.5:
            res[2] = 0.1667 * (3 - p1) * wa * al
        else:
            p4 = (1 - 2 * r1) ** 3 / (4 * (r2**2))
            res[2] = 0.1667 * (3 - p1 - p4) * wa * al
        return res

    def type_tri_left_part(self, al, a, b, w, wl):
        # 部材中間に左上がりの直角三角荷重がある場合
        # al: 部材長, a, b: 寸法, w: 等分布荷重, wl: 荷重の高さ
        # 戻り値 (Ci, Cj, M0, Qi, Qj)
        #
        #         +     *
        #         |     | *
        #      wl |     | w *
        #         + +===+====+===+
        #             a    b
        #           +---+----+

        res = self.init_cmq()
        wa = 0.5 * w * wl * b  # 全荷重
        r1 = a / al
        r2 = b / al
        p1 = 3 * r1 + r2
        p2 = 6 * (r1**2) + 4 * r1 * r2 + (r2**2)
        p3 = 10 * (r1**3) + 10 * r2 * (r1**2) + 5 * r1 * (r2**2) + (r2**3)
        res[0] = -0.03333 * (10 * p1 - 10 * p2 + 3 * p3) * wa * al
        res[1] = 0.03333 * (5 * p2 - 3 * p3) * wa * al
        res[3] = 0.3333 * (3 - p1) * wa
        res[4] = 0.3333 * p1 * wa
        if (r1 + r2) < 0.5:
            res[2] = 0.1667 * p1 * wa * al
        elif r1 > 0.5:
            res[2] = 0.1667 * (3 - p1) * wa * al
        else:
            p4 = 1.5 * ((1 - 2 * r1) ** 2) / r2
            p5 = (1 - 2 * r1) ** 3 / (4 * (r2**2))
            res[2] = 0.1667 * (3 - p1 - p4 + p5) * wa * al
        return res

    def q0_to_qf(self, al, cmq):
        # 単純梁のせん断力 Q0 を両端固定梁の値に変換
        # al: 部材長
        cmq[3] -= (cmq[0] + cmq[1]) / al
        cmq[4] += (cmq[0] + cmq[1]) / al

    def init_cmq(self):
        # CMQ用の配列の初期化
        return numpy.zeros(5)

    def cmq_form(self, arr, n=2):
        # 出力用に値を整形
        # n: 小数以下の桁数
        if n < 0:
            return arr
        for i in range(len(arr)):
            v = round((10**n) * abs(arr[i])) / (10**n)
            if arr[i] < 0:
                arr[i] = -v
            else:
                arr[i] = v
        return arr


# 以下は荷重項計算の例題です
# 詳細については cmq.pdf の2ページ目をご覧ください

if __name__ == "__main__":
    obj = Cmq()
    cmq = obj.cmq_zone(6, 10, 1.5, 1.5, 3, 0, 4.5, 1.5)
    cmq += obj.cmq_divide(6, 67.5)
    print(obj.cmq_form(cmq, 1))
