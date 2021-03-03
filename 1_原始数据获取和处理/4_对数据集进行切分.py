import copy
import json
import csv

# 读取数据
with open('1_原始数据获取和处理\\2_2020年新数据.json', 'r', encoding='utf-8') as f:
    _data = json.loads(f.read())

# rank
with open('1_原始数据获取和处理\\老编号.json', 'r', encoding='utf-8') as f:
    rank = json.loads(f.read())

# 所有row的集合
rows = []

# 前面存储了出现在1534中的关键词的序号
# 最后一个位置存储公文点击量
a_row_of_info = []

# 第几个切分的文件
index_of_file: int = 1

header = rank.keys()

for row in _data:

    # data
    #######################################################

    if 1:

        # 1534个0
        for i in range(1534):
            a_row_of_info.append(0)

        # 有关键词出现的地方补上1
        for keyword in row[0:-1]:
            a_row_of_info[keyword - 1] = 1

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

    if 1:
        click_times: int = row[-1]

        if click_times < 200:
            a_row_of_info.append(1)

        elif click_times < 400:
            a_row_of_info.append(2)

        elif click_times < 600:
            a_row_of_info.append(3)

        elif click_times < 800:
            a_row_of_info.append(4)

        elif click_times < 1000:
            a_row_of_info.append(5)

        else:
            a_row_of_info.append(6)

    #######################################################

    rows.append(copy.deepcopy(a_row_of_info))
    a_row_of_info.clear()

    if len(rows) >= 100:
        # 写入数据
        with open('3_分割数据\\%d_分割数据.data' % (index_of_file), 'a+', encoding='utf-8', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(header)
            f_csv.writerows(rows)
            rows.clear()

            index_of_file += 1

else:
    # 写入数据
    with open('3_分割数据\\%d_分割数据.data' % (index_of_file), 'a+', encoding='utf-8', newline='') as f:

        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(rows)
        rows.clear()

        index_of_file += 1
