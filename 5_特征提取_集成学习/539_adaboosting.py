import copy
import json

import numpy as np
from sklearn import datasets
from sklearn.ensemble import (AdaBoostClassifier, BaggingClassifier,
                              RandomForestClassifier)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.utils import shuffle

# 读取数据
with open('4_新编码数据生成训练集\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
    _data = json.loads(f.read())

# rank
with open('3_分割数据\\新编号.json', 'r', encoding='utf-8') as f:
    rank = json.loads(f.read())

# 所有row的集合
x = []
y = []

# 前面存储了出现在540中的关键词的序号
# 最后一个位置存储公文点击量
a_row_of_info_x = []
a_row_of_info_y = []

limit = 0

for row in _data:

    # limit += 1

    # if limit > 10:
    #     break

    # data
    #######################################################

    # 540个0
    for i in range(540):
        a_row_of_info_x.append(0)

    # 有关键词出现的地方补上1
    for keyword in row[0:-1]:
        a_row_of_info_x[keyword - 1] = 1

    #######################################################

    # target
    #######################################################

    click_times: int = row[-1]

    # 分类区间间隔
    INTERVAL = 300

    # 几分类？
    MAX_CLASSIFICATION = 3
    a_row_of_info_y.append(min(click_times // INTERVAL, MAX_CLASSIFICATION - 1))

    #######################################################

    x.append(copy.deepcopy(a_row_of_info_x))
    a_row_of_info_x.clear()

    y.append(copy.deepcopy(a_row_of_info_y))
    a_row_of_info_y.clear()

# header = rank.keys()


all_X = np.array(x)
all_Y = np.array(y)

x_train, x_test, y_train, y_test = train_test_split(all_X, all_Y, test_size=0.20, random_state=None, shuffle=True)

adaboost = AdaBoostClassifier(
    base_estimator=SVC(),
    n_estimators=2,
    learning_rate=1,
    algorithm='SAMME'
).fit(x_train, y_train.ravel())

scores = cross_val_score(adaboost, x_train, y_train.ravel())
scores.mean()

print(adaboost.predict(x_test))
print("准确率：", adaboost.score(x_test, y_test))
