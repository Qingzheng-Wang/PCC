#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# ========================================================
# 名称:   LL.py
# 作者:   Qingzheng WANG
# 时间:   2023/5/21
# 描述:   使用LL分析法生成语法树
# ========================================================

from get_predict_table import create_predict_table
from lexer import word_list

predict_table = create_predict_table()

# 语法树节点
class Node:
    def __init__(self, Type, text=None):
        self.type = Type
        self.text = text
        self.child = list()
    # 将语法树对象字符化输出
    def __str__(self):
        children = list()
        for child in self.child:
            children.append(child.__str__())
        # 对于非终结符，type就是非终结符本身
        out = "<{type}, {text}>".format(type=self.type, text=self.text)
        for child in children:
            if child:
                for line in child.split("\n"):
                    out = out + "\n     " + line
        return out

    def __repr__(self):
        return self.__str__()

# 输出栈中节点的type
def stack_text(stack):
    ss = []
    for s in stack:
        ss.append(s.type)
    return ss

def analysis(word_table, show=False):
    stack = []
    root = Node("Program")
    End = Node("#")
    stack.append(End)
    stack.append(root)
    index = 0
    """
    分析预测表的三个状态
    1. cur = #  解析完成
    2. cur = w  输入的字符表与符号栈中节点匹配
    3. cur 为非终结符，继续生成子节点
    4. error
    """
    while len(stack) != 0:
        cur = stack.pop()
        # 状态 1 遇到结束符号，解析完成
        if cur.type == "#" and len(stack) == 0:
            print("\nComplete LL(1) analysis!")
            return [True, root]
        # 状态 2 遇到终结符，匹配
        # 匹配终结符需要判断type而不是word，因为产生式中都是id类似的形式，而匹配字符是具体的值
        elif cur.type == word_table[index]['type']:
            if show:
                print("\nSymbol Stack: ", stack_text(stack), "\nMatching Character: ", word_table[index]['word'])
            cur.text = word_table[index]['word']
            index += 1
        # 状态 3  遇到非终结符，继续生成子节点
        else:
            w = word_table[index]['type']
            if w in predict_table[cur.type]: # 判断该非终结符是否在预测表中
                if predict_table[cur.type][w] == "null":
                    continue
                next_pr = predict_table[cur.type][w].split()
                if show:
                    print("\nSymbol Stack: ", stack_text(stack), "\nProduction: ", cur.type,"->", predict_table[cur.type][w])
                node_list = []
                """
                产生式右部符号入栈
                子节点入栈
                注意：子节点入栈顺序应该与产生式符号相反
                """
                for np in next_pr:
                    node_list.append(Node(np))
                for nl in node_list:
                    cur.child.append(nl)
                node_list.reverse()
                for nl in node_list:
                    stack.append(nl)
            # 状态 4 错误
            else:
                print("Error in", stack, cur.type , word_table[index]['type'])
                return [False]

if __name__ == "__main__":
    w_list = word_list("./test/array.c")
    word_table = w_list.word_list
    root = analysis(word_table, True)
    if root[0]:
        print("\n\nInput 1 to print the grammar tree, or press any key to quit.")
        if input() == "1":
            print(root[1])
            print("\n\nComplete printing grammar tree!\n\n")
        # print(root[1])