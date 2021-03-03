import copy
import json
import time
import os

import numpy as np
from sklearn.ensemble import (AdaBoostClassifier, AdaBoostRegressor,
                              BaggingClassifier, BaggingRegressor,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def run(config: dict) -> None:
    try:
        if config["是否使用约简后的新数据"]:
            with open('4_新编码数据生成训练集\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
                gw_data = json.loads(f.read())

        else:
            with open('1_原始数据获取和处理\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
                gw_data = json.loads(f.read())
    
    # 如果直接在文件夹下运行
    except FileNotFoundError:

        if config["是否使用约简后的新数据"]:
            with open('..\\4_新编码数据生成训练集\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
                gw_data = json.loads(f.read())

        else:
            with open('..\\1_原始数据获取和处理\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
                gw_data = json.loads(f.read())

    # 条件属性
    x = []

    # 决策属性
    y = []

    # 每一行的数据
    a_row_of_info_x = []
    a_row_of_info_y = []

    for row in gw_data:

        # X数据，即条件属性
        #######################################################

        # 补0
        if config["是否使用约简后的新数据"]:
            for i in range(540):
                a_row_of_info_x.append(0)

        else:
            for i in range(1534):
                a_row_of_info_x.append(0)

        # 有关键词出现的地方补上1
        for keyword in row[0:-1]:
            a_row_of_info_x[keyword - 1] = 1

        #######################################################

        # Y数据，即决策属性
        #######################################################

        click_times: int = row[-1]

        if config["是否使用分类，否则回归"] or config["是否对数据进行离散化"]:

            interval = config["分类区间大小"]
            max_classification = config["分类个数"]

            a_row_of_info_y.append(min(click_times // interval, max_classification - 1))

        else:
            a_row_of_info_y.append(click_times)

        #######################################################

        x.append(copy.deepcopy(a_row_of_info_x))
        a_row_of_info_x.clear()

        y.append(copy.deepcopy(a_row_of_info_y))
        a_row_of_info_y.clear()

    # 转化为numpy
    x = np.array(x)
    y = np.array(y)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=config["测试数据占比"],
                                                        random_state=config["测试数据随机种子"],
                                                        shuffle=config["打乱测试数据"])

    base_estimator_type = config["决策者种类（1.KNN、2.SVM、3.DecisionTree）"]

    if base_estimator_type == 1:

        if config["是否使用分类，否则回归"]:
            base_estimator = KNeighborsClassifier(n_neighbors=config["KNN_K值"])

        else:
            base_estimator = KNeighborsRegressor(n_neighbors=config["KNN_K值"])

    elif base_estimator_type == 2:

        if config["是否使用分类，否则回归"]:
            base_estimator = SVC()

        else:
            base_estimator = SVR()

    elif base_estimator_type == 3:

        if config["是否使用分类，否则回归"]:
            base_estimator = DecisionTreeClassifier()

        else:
            base_estimator = DecisionTreeRegressor()

    else:
        raise NameError

    # 模型`
    learning_model = base_estimator

    if config["是否使用集成学习"]:

        integrated_learning_algorithm = config["集成学习算法（1.Adaboost、2.Bagging、3.RandomForest）"]

        if integrated_learning_algorithm == 1:

            if config["是否使用分类，否则回归"]:

                learning_model = AdaBoostClassifier(
                    base_estimator=base_estimator,
                    n_estimators=config["决策者数量"],
                    learning_rate=config["Adaboost学习率"],
                    algorithm='SAMME' if config["Adaboost算法（1.SAMME、2.SAMME.R）"] == 1 else 'SAMME.R',
                    random_state=config["测试数据随机种子"],
                )

            else:

                learning_model = AdaBoostRegressor(
                    base_estimator=base_estimator(),
                    n_estimators=config["决策者数量"],
                    learning_rate=config["Adaboost学习率"],
                    algorithm='SAMME' if config["Adaboost算法（1.SAMME、2.SAMME.R）"] == 1 else 'SAMME.R',
                    random_state=config["测试数据随机种子"],
                )

        elif integrated_learning_algorithm == 2:

            if config["是否使用分类，否则回归"]:

                learning_model = BaggingClassifier(
                    base_estimator=base_estimator,
                    n_estimators=config["决策者数量"],
                    random_state=config["测试数据随机种子"],
                    max_samples=config["取样率"]
                )

            else:

                learning_model = BaggingRegressor(
                    base_estimator=base_estimator,
                    n_estimators=config["决策者数量"],
                    random_state=config["测试数据随机种子"],
                    max_samples=config["取样率"]
                )

        elif integrated_learning_algorithm == 3:

            if config["是否使用分类，否则回归"]:

                learning_model = RandomForestClassifier(
                    n_estimators=config["决策者数量"],
                    random_state=config["测试数据随机种子"],
                    max_samples=config["取样率"]
                )

            else:

                learning_model = RandomForestRegressor(
                    n_estimators=config["决策者数量"],
                    random_state=config["测试数据随机种子"],
                    max_samples=config["取样率"]
                )
        else:
            raise NameError

    learning_model.fit(x_train, y_train.ravel())

    predict_y_value: np.ndarray = learning_model.predict(x_test)
    print("\n预测数据：", predict_y_value)

    real_y_value: np.ndarray = np.array([i[0] for i in y_test.tolist()])
    print("\n真实数据：", real_y_value)

    print("\n误差：", real_y_value - predict_y_value)
    print("\n平均误差(总误差除以总样本数)：", np.abs((real_y_value - predict_y_value)).sum() / real_y_value.size)
    print("\n准确率(分类)或拟合优度R^2(回归)：", learning_model.score(x_test, y_test), '\n')


if __name__ == '__main__':

    config = {
        "是否使用约简后的新数据": True,
        "是否使用分类，否则回归": True,
        "是否对数据进行离散化": True,
        "分类区间大小": 600,
        "分类个数": 2,
        "测试数据占比": 0.33,
        "测试数据随机种子": None,
        "打乱测试数据": True,
        "是否使用集成学习": True,
        "集成学习算法（1.Adaboost、2.Bagging、3.RandomForest）": 2,  # KNN不饿能搭配Adaboost
        "Adaboost学习率": 1,
        "Adaboost算法（1.SAMME、2.SAMME.R）": 1,  # SVM必须使用SAMME算法
        "决策者种类（1.KNN、2.SVM、3.DecisionTree）": 1,
        "KNN_K值": 5,
        "取样率": 0.8,
        "是否使用Bootstrap取样": True,
        "决策者数量": 5,
        "测试次数": 1
    }

    while True:
        os.system('cls')
        [print(i, '.', key, ":", config[key]) for i, key in enumerate(config.keys())]
        order = input("Input the order of the configuration to change, 'begin' to begin:")
        if order == 'begin': break
        config[list(config.keys())[int(order)]] = \
            eval(input("You would like to change config[%s] to:" % (list(config.keys())[int(order)])))

    for i in range(config["测试次数"]):
        start_time = time.time()
        print("\n\nThe %d time:\n\n" % (i + 1))
        run(config)
        end_time = time.time()
        print("耗时(秒)：", end_time - start_time)
