import copy
import csv
import json

import numpy as np
from sklearn import datasets
from sklearn.ensemble import (BaggingClassifier, RandomForestClassifier,
                              RandomForestRegressor)
from sklearn.model_selection import train_test_split
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

    # 最后加上点击量，6个等级：
    # x < 200:1
    # 200 <= x < 400:2
    # 400 <= x < 600:3
    # 600 <= x < 800:4
    # 800 <= x < 1000:5
    # x >= 1000:6

    click_times :int = row[-1]

    # 分类区间间隔
    # INTERVAL = 300

    # 几分类？
    # MAX_CLASSIFICATION = 3
    # a_row_of_info_y.append(min(click_times // INTERVAL, MAX_CLASSIFICATION - 1))
    a_row_of_info_y.append(click_times)

    #######################################################

    x.append(copy.deepcopy(a_row_of_info_x))
    a_row_of_info_x.clear()

    y.append(copy.deepcopy(a_row_of_info_y))
    a_row_of_info_y.clear()
        
# header = rank.keys()

# 把东西直接喂给KNN学习

iris_X=np.array(x)
iris_y=np.array(y)

X_train,X_test,y_train,y_test=train_test_split(iris_X,iris_y,test_size=0.20,random_state=None, shuffle=True)


forest = RandomForestClassifier(
    n_estimators=100,
    random_state=None,
    max_samples=0.8    #每个样本取这么多数据进行学习
).fit(X_train, y_train.ravel())

print(forest.predict(X_test))
print(y_test)
print("准确率：", forest.score(X_test, y_test))
