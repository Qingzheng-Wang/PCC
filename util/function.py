#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# ========================================================
# 名称:   function.py
# 作者:   Qingzheng WANG
# 时间:   2023/5/19
# 描述:   词法分析工具，包括读取单词，判断是否为变量名，判断变量
#         名是否存在，判断是否是数字，打印单词表和参数表
# ========================================================

import re
import tabulate

# 运算符表
op_list = {"+", "-", "*", "/", "<", "<=", ">", ">=", "=", "==", "!=", ",", "!"}
# 分隔符表
sp_list = {";", "(", ")", "[", "]", "{", "}", ".", ":", "\"", "#", "\'", "\\", "?"}
# 关键字表
k_list = {
    "if", "return", "while"
}
# 比较运算符
Cmp = ["<", ">", "==", "!=", ">=", "<="]

# 正则表达式判断是否为数字
def if_num(int_word):
    # 前半部分代表和类似3.14这样的小数匹配，后半部分代表和整数匹配
    if re.match("^([0-9]+[.][0-9]*)$", int_word) or re.match("^([0-9]+)$", int_word) is None:
        return False
    else:
        return True

# 判断是否为为变量名
def if_para(int_word):
    if re.match("[a-zA-Z_][a-zA-Z0-9_]*", int_word) is None: # 表示支持aSb, Abb__, 以及_aaB8__诸如此类的变量名
        return False
    else:
        return True

# 判断是否为终结符
# def END_STATE(int_word):
#     if 

# 判断变量名是否已存在
def have_para(para_list, para):
    for n in para_list:
        if para == n['para']:
            return True
    return False

def print_str(lists):
    table = [['line', 'type', 'word', 'id']]
    for l in lists:
        if len(l.items()) == 4:
            temp = [i[1] for i in l.items()]
            table.append(temp)
        else:
            t = list(l.items())
            temp = [i[1] for i in t]
            temp.append("None")
            table.append(temp)
    print(tabulate.tabulate(table, headers='firstrow'))

def print_para(lists):
    table = [['line', 'id', 'value', 'para', 'type']]
    for l in lists:
        temp = [i[1] for i in l.items()]
        table.append(temp)
    print(tabulate.tabulate(table, headers='firstrow'))

# 分割并获取文本单词
# 返回值为列表out_words
# 列表元素{'word':ws, 'line':line_num}分别对应单词与所在行号
def get_word(filename):
    global sp_list
    out_words = []
    f = open(filename,'r+',encoding='UTF-8')
    # 先逐行读取，并记录行号
    lines = f.readlines()
    line_num = 1
    # 判断是否含有注释块的标识
    pass_block = False
    for line in lines:
        words = list(line.split())
        for w in words:
            # 去除注释
            if '*/' in w:
                pass_block = False
                continue
            if '//' in w or pass_block:
                break
            if '/*' in w:
                pass_block = True
                break
            # 分析单词
            if w in Cmp:
                out_words.append({'word':w, 'line':line_num})
                continue
            ws = w
            for a in w:
                if a in sp_list or a in op_list:
                    # index为分隔符的位置，将被分隔符或运算符隔开的单词提取, 考虑例如main(){由多种类型组合的情况
                    index = ws.find(a)
                    if index != 0: # 分隔符不在行首
                        # 存储单词与该单词的所在行号，方便报错定位
                        out_words.append({'word':ws[0:index], 'line':line_num})
                    ws = ws[index+1:]
                    out_words.append({'word':a, 'line':line_num})
            if ws!='':
                out_words.append({'word':ws, 'line':line_num})
        line_num += 1
    return out_words