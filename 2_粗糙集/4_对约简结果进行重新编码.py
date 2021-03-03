import json

with open('3_分割数据\\最终结果.json', 'r', encoding='utf-8') as f:
    a = json.loads(f.read())

with open('3_分割数据\\老编号.json', 'r', encoding='utf-8') as f:
    rank = json.loads(f.read())

# 新编号
new_json = {}

# 编号
new_order = 1

# 关键词
keywords = list(rank.keys())

# 遍历约简出来的每一个编号
for old_order in list(a):
    # 通过编号拿到关键词
    keyword = keywords[old_order - 1]

    # 关键词--编号
    new_json[keyword] = new_order
    new_order += 1

with open('3_分割数据\\新编号.json', 'a+', encoding='utf-8') as f:
    f.write(json.dumps(new_json, ensure_ascii=False))
