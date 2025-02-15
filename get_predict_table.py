#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# ========================================================
# 名称:   get_predict_table.py
# 作者:   Qingzheng WANG
# 时间:   2023/5/20
# 描述:   生成预测分析表，计算非终结符的first集和follow集
# ========================================================

# 使用自上而下的语法分析
import sys, os, re
sys.path.append(os.pardir)

grammars = {
    "Program":["type M C Pro"],

    "C":["( cc )"],
    "cc":["null"],

    "Pro":["{ Pr }"], # 大括号
    "Pr":["P Pr", "null"],
    "P":["type L ;", "L ;", "printf OUT ;", "Pan"],

    "L":["M LM"], # 赋值语句
    "LM":["= FE", "Size AM","null"],
    "FE":["E", "string", "character"],
    "M":["parameter"],

    "E":["T ET"],
    "ET":["+ T ET", "- T ET", "null"],
    "T":["F TT"],
    "TT":["* F TT", "/ F TT", "null"],
    "F":["number", "BRA", "M MS"],
    "MS":["Size", "null"],
    "BRA": ["( E )"],

    "Pan":["Ptype P_block Pro"],
    "Ptype":["if", "while"],
    "P_block":["( Pbc )"],
    "Pbc":["E PM"],
    "PM":["Cmp E", "null"],

    "Size":["[ E ]"],
    "AM":["= E", "null"]
}

first_table = {}
follow_table = {}
predict_table = {}
observer = {} # observer里面，key是产生式左部，value是产生式右部的最后一位，follow(key)更新，则follow(value)也要同步更新

"""
初始化订阅者
订阅者： 用于求follow集合的过程中特殊情况：
    非终结符的后继非终结符的first集合可能存在null
    eg： A -> B C     C -> D | null   D -> (A) | i
    那么在一次遍历过程中，需要将follow（A）加入follow（B），因为C -> null
    （重点）但是！此时的follow（A），并不是完整的，它可能在后续的遍历中会继续更新自身的follow集合
    所以此时会出现遗漏的follow
    所以我在这里用到一个订阅者模式
    订阅者为一个字典，字典键值为产生式左部，字典内容为产生式右部
"""
def init_observer():
    for k in grammars: # k是grammar里的键值，也就是产生式的左部
        follow_table[k] = []
        observer[k] = []
        for next_grammar in grammars[k]: # next_grammar是产生式的右部
            last_k = next_grammar.split()[-1]
            if last_k in grammars and last_k != k:
                observer[k].append(last_k)


"""
刷新订阅
检测到某个follow集合更新时，对其订阅的所有产生式左部的follow集合进行更新
简而言之：follow（A）发生了更新，那么曾经将follow（A）加入自身的B，C也更新其follow
并且，这是一个递归过程
"""
def refresh(k):
    for lk in observer[k]:
        new = U(follow_table[k], follow_table[lk]) # k是左部，lk是右部最后一位
        if new != follow_table[lk]:
            follow_table[lk] = new
            refresh(lk)

"""
合并两个list并且去重
"""
def U(A,B):
    return list(set(A+B))

"""
查找指定非终结符的first集合
"""
def find_first(key):
    if key not in grammars: # key不是grammar的左部，说明key是非终结符，递归结束，直接返回key
        return [key]
    l = []
    for next_grammar in grammars[key]: 
        next_k = next_grammar.split()[0]
        l.extend(find_first(next_k)) # 递归调用，寻找右式第一个终结符或非终结符的first集
    return l

"""
查找所有非终结符follow集合
"""
def find_follow():
    init_observer()
    follow_table["Program"] = ["#"] # Program作为入口非终结符
    for k in grammars:
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()
            
            for i in range(0,len(next_k)-1):
                if next_k[i] in grammars:
                    if next_k[i+1] not in grammars:
                        """
                        如果后继字符是终结符，加入follow集
                        """
                        new_follow = U([next_k[i+1]], follow_table[next_k[i]])
                        if new_follow != follow_table[next_k[i]]: # 判断new_follow是否较原来有更新
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
                    else:
                        new_follow = U(first_table[next_k[i+1]], follow_table[next_k[i]])
                        """
                        如果后继字符的first集合中含有null，通知所有订阅者更新follow集合
                        """
                        if "null" in first_table[next_k[i+1]]:
                            new_follow = U(follow_table[k], new_follow)
                            observer[k].append(next_k[i])
                        if new_follow != follow_table[next_k[i]]:
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
            """
            产生式左部的follow集合加入最后一个非终结符的follow集合
            """
            if next_k[-1] in grammars:
                if next_k[-1] not in follow_table:
                    follow_table[next_k[-1]] = []
                if next_k[-1] != k:
                    follow_table[next_k[-1]] = U(follow_table[next_k[-1]], follow_table[k])

    for k in follow_table:
        if "null" in follow_table[k]:
            follow_table[k].remove("null")

"""
获取所有非终结符的first集合
在此同时直接将first集合加入predict表中
"""
def get_first_table():
    for k in grammars:
        predict_table[k] = {}
        first_table[k] = []
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()[0]
            kl = find_first(next_k)
            first_table[k].extend(kl)
            for kk in kl: # first集中有的非终结符，如果不为空，则直接加入预测表
                if kk != "null":
                    predict_table[k][kk] = next_grammar

"""
将follow集合中的部分内容加入predict表中
"""
def get_predict_table():
    for k in grammars:
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()[0]
            if next_k in grammars and "null" in first_table[next_k] or next_k == "null":
                for fk in follow_table[k]:
                    predict_table[k][fk] = next_grammar


def create_predict_table():
    get_first_table()
    find_follow()
    get_predict_table()
    return predict_table

def show_tables():
    get_first_table()
    find_follow()
    get_predict_table()
    print("\nfirst集合如下\n")
    for k in first_table:
        print(k, first_table[k])
    print("\nfollow集合如下\n")
    for k in follow_table:
        print(k, follow_table[k])
    # print(first_table)
    print("\n预测表如下\n")
    for k in predict_table:
        print(k, predict_table[k])

if __name__ == "__main__":
    show_tables()