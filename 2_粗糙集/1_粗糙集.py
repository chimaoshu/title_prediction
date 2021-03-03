import numpy as np
import pandas as pd
import time
import copy


class RoughSet:
    """粗糙集"""

    # 二维表
    table: pd.DataFrame

    def __init__(self, csv_path: str) -> None:

        self.table = pd.read_csv(csv_path, encoding='utf-8')
        print(self.table)

    def Ind(self, B: list) -> dict:
        """
        求不可辩关系
        输入：
            B: 列序号构成的list，以给定列序号划分等价类

        返回数据格式：
            左边是可能取值构成的list，右边是集合构成的list，左右下标相对应：
            ['好瓜', '坏瓜'], [{0, 1, 2, 3, 4, 5, 6, 7}, {8, 9, 10, 11, 12, 13, 14, 15, 16}]

        算法：根据取值划分等价类
        """

        df = self.table

        # 给定的多个属性构成的复合列
        columns = df.columns[B]

        # 决策属性的所有取值，可重复
        decision_attributes_values = df[columns].values

        # 决策属性的所有可能取值，去重
        decision_attributes_posible_values = []

        # 进行去重操作，此处无法用set，因为多维列表不能哈希
        for i in decision_attributes_values.tolist():
            if not i in decision_attributes_posible_values:
                decision_attributes_posible_values.append(i)

        # 商集
        Ind_B = []

        # 商集初始化
        for i in range(len(decision_attributes_posible_values)):
            Ind_B.append(set())

        # 遍历每一行，创建Ind(B)
        for row_order, decision_attribute_value in list(enumerate(decision_attributes_values)):
            # 找到决策属性对应的下标
            index: int = decision_attributes_posible_values.index(decision_attribute_value.tolist())

            # 再对应集合中添加行序号
            Ind_B[index].add(row_order)

        # return decision_attributes_posible_values, Ind_B
        return Ind_B

    def B_lower_approximation(self, B: list, X: set) -> set:
        """
        求下近似B(X)
        传入：
            条件属性B--列序号组成的list
            决策属性X--一个由数据帧中行号构成的集合(一般是关于决策属性划分后的等价类)
        返回：
            B(X)下近似--一个由数据帧中行号构成的集合

        算法：遍历关于B划分后的所有等价类，若某个等价类完全包含于X，则把该等价类添加到结果中
        """

        # B(X)
        B_X = set()

        # 获取B的等价类们
        equivalence_classes = self.Ind(B)

        # 遍历每一个等价类
        for equivalence_class in equivalence_classes:

            # 如果是X的子集
            if equivalence_class.issubset(X):
                # 取并集
                B_X = B_X | equivalence_class

        return B_X

    def test_B_lower_approximation(self) -> None:
        """
        测试下近似：作业题中B=a1，计算下近似：B(d1) B(d2) B(d3) B(d)
        B(d1)=∅
        B(d2)={x2,x7,x10}
        B(d3)={x5,x6,x8}
        B(d)=U
        """
        Ind_d = self.Ind([-1])

        # 全集
        d = set()

        print("下近似测试：")
        for i in Ind_d:
            d = d | i
            print(self.B_lower_approximation(B=[1], X=i))

        print(self.B_lower_approximation(B=[1], X=d))

    def POS(self, C: list, D: list) -> set:
        """
        positive domain
        传入条件属性C和决策属性D，求正域POSc(D)
        传入：
            C:condition attribute 条件属性的列序号组成的list
            D:decision attribute 决策属性的列序号组成的list
        
        算法：遍历关于决策属性D划分的等价类Yi，加入条件属性C关于该等价类的下近似B(Yi)，其中B为条件属性C
        """

        POS_C_D = set()

        # 获得关于D划分的等价类
        Ind_D = self.Ind(D)

        # 遍历关于决策属性D划分的等价类Yi
        # 加入条件属性C关于该等价类的下近似B(Yi)
        # 其中B为条件属性C
        for Yi in Ind_D:
            POS_C_D = POS_C_D | self.B_lower_approximation(B=C, X=Yi)

        return POS_C_D

    def test_POS(self) -> None:
        """
        正域测试，作业中的习题
        POSa1(d)={x2,x5,x6,x7,x8,x10}
        POSa2(d)={x2,x4,x7,x10}
        POSa3(d)={x2,x5,x6,x7,x8,x10}
        """
        print("正域测试：")
        print(self.POS([1], 4))
        print(self.POS([2], 4))
        print(self.POS([3], 4))

    def Redundancy(self, C: list, D: list) -> list:
        """
        计算条件属性C的冗余
        传入：
            C:条件属性构成的list
            D:决策属性构成的list
        返回：
            条件属性的冗余，若无冗余返回空

        算法：遍历C的每一个元素，尝试将其去掉，检查正域是否发生变化
        """

        # 一个属性，不用算了
        if len(C) == 1:
            return []

        # 冗余属性
        redundancy_attribute = []

        for element in C:

            C_copy = copy.deepcopy(C)
            C_copy.remove(element)

            # 判断是否为冗余
            if len(self.POS(C_copy, D)) == len(self.POS(C, D)):
                redundancy_attribute.append(element)

        return redundancy_attribute

    def Core(self, C: list, D: list) -> list:
        """
        计算条件属性C的核属性
        传入：
            C:条件属性构成的list
            D:决策属性构成的list
        返回：
            条件属性的核属性，若无核返回空

        算法：遍历C的每一个元素，尝试将其去掉，检查正域是否发生变化
        """

        # 一个属性，不用算了
        if len(C) == 1:
            return C

        # 核属性
        Core_C = []

        for element in C:

            C_copy = copy.deepcopy(C)
            C_copy.remove(element)

            # 判断是否为核
            if len(self.POS(C_copy, D)) != len(self.POS(C, D)):
                Core_C.append(element)

        return Core_C

    def test_Core(self) -> None:
        """
        维度约简测试，作业中的题：
        Core({a1,a2,a3}) = a2
        """
        print("核属性：", self.Core([1, 2, 3], -1))

    def Red(self, C: list, D: list) -> list:
        """
        计算条件属性C的一个约简
        传入：
            C:条件属性构成的list
            D:决策属性构成的list
        返回：
            条件属性的约简，若无约简返回本身

        算法：遍历C的每一个元素，尝试将其去掉，检查正域是否发生变化，不变则可约简
        """

        # 一个属性，不用算了
        if len(C) == 1:
            return C

        has_reduction = False

        # 约简
        Red_C = copy.deepcopy(C)

        while (True):

            for element in list(Red_C):

                # Red_C_copy = copy.deepcopy(Red_C)
                # Red_C_copy.remove(element)

                old_POS_length = len(self.POS(Red_C, D))

                Red_C.remove(element)
                new_POS_length = len(self.POS(Red_C, D))

                # 判断是否存在冗余
                if old_POS_length == new_POS_length:
                    has_reduction = True
                    break
                else:
                    Red_C.append(element)

            #  如果进行了约简，则再次循环继续寻找进一步的约简
            if has_reduction:
                has_reduction = False
                continue

            # 如果无冗余，即无法继续约简，则退出
            else:
                break

        return Red_C

    def test_Red(self) -> None:
        """
        维度约简测试，作业中的题：
        Red({a1,a2,a3}) = {a1, a2} 或 {a2, a3}
        """ 
        print("约简：", self.Red([1, 2, 3], -1))

    def auto_reduction(self) -> list:
        """
        自动对条件属性进行约简操作，返回约简后的列表
        """

        df = self.table

        # 最后一列为决策属性，其他全部是条件属性
        result = self.Red(list(range(len(df.columns) - 1)), [-1])

        print("\n该粗糙集所有条件属性的一个约简为：\n", result)

        print("\n对应的关键词为：")
        for i in df.columns[result]:
            print(i, end=' ')

        print('\n')
        return result


if __name__ == "__main__":
    csv_path = "2_粗糙集\\watermelon.csv"
    # csv_path = "作业题.csv"
    # csv_path = "gwt.csv"
    # csv_path = "3_2020年新数据.data_and_target"

    start_time = time.time()

    a = RoughSet(csv_path)
    # a.test_B_lower_approximation()
    # a.test_Core()
    # a.test_POS()
    # a.test_Red()
    a.auto_reduction()

    end_time = time.time()
    print("\n耗时：", end_time - start_time, "秒")
