# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:24:42 2019
@author: BHN
"""
import pandas as pd
import itertools
def Deal_data():

#    pandas分为Series和DataFrame两种数据形式。Series可以视为一维数组，DataFrame与array
#    的区别是其数据类型可以是不相同的

    df=pd.read_csv('watermelon.csv', encoding='utf-8')
    # print(df.columns)#打印pandas的标签

#    df.drop(df.columns[0],axis=1,inplace=True)#删除某一列

    answer = {}

    # 0 '色泽'
    for class_num,a in enumerate(list(df.columns[1:-1])): #删除第一列的序数和最后一列的决策属性

        # ['浅白', '青绿', '乌黑']
        wtf = df[a].values
        one_class_label = list(set(wtf))#DataFrame对应转成numpy的是to_numpy()

#        这行的功能是查看这一个属性中有几种独立的label
        single_class_conditional_attribute_set = []

        # 浅白
        for b in one_class_label:
            test2 = df[df[a] == b]
            test3 = test2.ID
            test4 = test3.values
            test1 = set(test4)
            single_class_conditional_attribute_set.append(test1)
            
        answer[str(class_num)]=single_class_conditional_attribute_set
    
    answer_decision = {}
    one_class_label = list(set(df[df.columns[-1]].values))
    single_class_conditional_attribute_set = []
    for b in one_class_label:
        single_class_conditional_attribute_set.append(set(df[df[df.columns[-1]] == b].ID.values))
    answer_decision['0']=single_class_conditional_attribute_set
    return answer,answer_decision
        
def liang_zu_guan_xi_de_deng_jia_lei(list_a,list_b):
    answer = []
    for A in list_a:
        for B in list_b:
            tmp = A&B
            if tmp != set():
                answer.append(tmp)
    return answer
def Pos_2_attributes(C,D):
    answer = []
    for A in C:
        for B in D:
            if A.issubset(B):
                answer.append(A)
    if answer != []:
        union = answer[0]
        for a in answer:
            union = union|a
    else:
        union = set()
    return union
        
    
if __name__ =='__main__':
    conditional_attribute_set,decision_attribute_set = Deal_data()
    equivalence_class_count = len(conditional_attribute_set)
    for level in range(2,equivalence_class_count+2):#因为是二元关系，所以二元关系对的层数是总数减一
#        如果leve为2代表U/{a,b},如果level为3代表U/{a,b,c}
        for class_combination in itertools.combinations(range(equivalence_class_count), level):
#            枚举不重复的等价类组合。例如：('A', 'B') ('A', 'C') ('A', 'D') ('B', 'C') ('B', 'D') ('C', 'D')
            combination_id = "".join([str(o) for o in class_combination])
            previous_equivalence_class_id = combination_id[:-1]
            latter_equivalence_class_id = combination_id[-1]
            conditional_attribute_set[combination_id] = \
            liang_zu_guan_xi_de_deng_jia_lei(\
                                             conditional_attribute_set[previous_equivalence_class_id],\
                                             conditional_attribute_set[latter_equivalence_class_id])
    print(conditional_attribute_set)
    for key in conditional_attribute_set:
#        验证每一个商集是否与所有条件属性的商集相同
        if len(conditional_attribute_set[key]) == len(conditional_attribute_set["".join([str(o) for o in range(equivalence_class_count)])]):
            set_equ_flag = True
            for a in conditional_attribute_set[key]:
                if a not in conditional_attribute_set["".join([str(o) for o in range(equivalence_class_count)])]:
                    set_equ_flag = False
                    break
            for a in conditional_attribute_set["".join([str(o) for o in range(equivalence_class_count)])]:
                if a not in conditional_attribute_set[key]:
                    set_equ_flag = False
                    break
            if set_equ_flag:
                print(key)