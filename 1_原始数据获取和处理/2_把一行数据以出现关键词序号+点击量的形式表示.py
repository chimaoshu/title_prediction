import copy
import json

# 读取数据
with open('1_原始数据获取和处理\\1_2020年新数据.json', 'r', encoding='utf-8') as f:
    _data = json.loads(f.read())

# rank
with open('1_原始数据获取和处理\\老编号.json', 'r', encoding='utf-8') as f:
    rank = json.loads(f.read())

# 存储2020年所有公文的信息
new_data_list = []

# 前面存储了出现在1534中的关键词的序号
# 最后一个位置存储公文点击量
a_row_of_info = []

for i in _data.keys():

    has_keyword_in_1534 = False

    keywords = _data[i]["keyword"]

    for keyword in keywords:

        if keyword in rank.keys():

            has_keyword_in_1534 = True
            a_row_of_info.append(rank[keyword])

    else:
        if has_keyword_in_1534:
           a_row_of_info.append(_data[i]["click_times"])

    if len(a_row_of_info) != 0:
        new_data_list.append(copy.deepcopy(a_row_of_info))
        a_row_of_info = []
        


# 写入数据
with open('1_原始数据获取和处理\\2_2020年新数据.json', 'a+', encoding='utf-8') as f:
    f.write(json.dumps(new_data_list, ensure_ascii=False))
