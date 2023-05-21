# from parser import Node,build_ast
from other.function import if_num 
from LL import analysis
import sys, os
sys.path.append(os.pardir)
from lexer import word_list

operator = {
    "+": lambda a, b: a+b,
    "-": lambda a, b: a-b,
    "*": lambda a, b: a*b,
    "/": lambda a, b: a/b
}

"""
四元式对象
成员：　op，arg1,arg2,result 分别对于操作数，两个变量，结果
特殊的自定义四元式语法：
    1.  (code_block, 0, 0, block1)   代码块开始标记
    2.  (j, 0, 0, , +2)              跳转语句，往后跳两行
    3.  (j<, a, b, block1)          条件跳转 if(a<b) then　jmp block1
    4.  (print, 0, 0, a)             打印变量ａ
"""
class MNode:
    def __init__(self, op="undefined", a1=None, a2=None, re=None):
        self.op = op
        self.arg1 = a1
        self.arg2 = a2
        self.re = re
    """字符化输出"""
    def __str__(self):
        return "({0},{1},{2},{3})".format(self.op, self.arg1, self.arg2, self.re)

    def __repr__(self):
        return self.__str__()

"""
两个全局 mid_result 存放四元式对象
tmp记录临时变量id
"""
mid_result = []
while_flag = []
arr = {}
tmp = 0
type_flag = ""

"""
递归遍历语法树
遇到相应非终结符做相应处理，遇到终结符返回终结符，其他字符递归处理其子节点
"""
def view_astree(root, ft=None):
    global type_flag
    if root.type == "type":
        type_flag = root.text
    if root == None or root.text == "(" or root.text == ")":
        return
    elif len(root.child) == 0 and root.text != None:
        return root.text
    if root.type == "L": # 这里的type和LL里语法树节点的type一致，如果是非终结符，则type是其本身
        math_op(root)
    elif root.type == "Pan": # "Pan"表示条件判断语句
        judge(root)
    elif root.type == "OUT":
        out(root)
    else: # 遇到其他非终结符则递归调用其子节点
        re = ""
        for c in root.child:
            cre = view_astree(c)
            if cre != None  and cre not in "[]}{)(\"'":
                re = cre
        return re

def math_op(root, ft=None):
    if root == None:
        return
    elif len(root.child) == 0 and root.text != None: # 对于非终结符则直接返回
        return root.text
    global mid_result
    global tmp
    global arr
    global type_flag
    """
    变量声明语句，两种情况
    1. 直接赋值
    2. 不赋值
    (=, a, 0, c)的含义是：c ::= a
    """
    if root.type == "L": # L -> M LM
        c1 = root.child[1] # c1是LM
        if len(c1.child) == 1: # 此时c1.child是null LM -> null
            mid_result.append(MNode("=", 0, 0, math_op(root.child[0].child[0]))) # root.child[0].child[0]是parameter，此时是声明语句，不赋值
        elif c1.child[0].type == "=": # LM -> = FE，遇到等号，就可以判断这是一个简单赋值语句，先生成四元式，然后四元式里的内容再递归处理
            mid_result.append(MNode("=", math_op(c1), 0, math_op(root.child[0].child[0])))
        else: # LM -> Size AM
            if len(c1.child[1].child) >1: # AM -> = E，该情况是数组赋值，类似s[1] = 1 + 2, 2
                cc1 = c1.child[1] # E
                mid_result.append(MNode("=", math_op(cc1), 0, math_op(root.child[0].child[0]) + "[]" + math_op(c1.child[0])))
            if math_op(root.child[0].child[0]) not in arr: # 将math_op(root.child[0].child[0])添加到数组表中
                arr[math_op(root.child[0].child[0])] = [math_op(c1.child[0]), type_flag]
                type_flag = ""
    elif root.type == "ET" or root.type == "TT":
        if len(root.child) > 1: # ET -> + T ET / ET -> - T ET
            op = MNode(math_op(root.child[0]))
            arg1 = math_op(root.child[1])
            if if_num(arg1) and if_num(ft):
                return str(operator[op](int(arg1), int(ft)))

            """
            临时变量Tn
            ft 为父节点传入的操作符左边部分临时id
            """
            t = "T" + str(tmp)
            tmp += 1
            mid_result.append(MNode(op, arg1, ft, t))
            ct = math_op(root.child[2], t)
            if ct != None:
                return ct
            return t

    elif root.type == "E" or root.type == "T":
        """
        赋值语句处理
        如果存在右递归，进行四则运算的解析
        不存在右递归的话直接赋值
        """
        if len(root.child[1].child) > 1: # 说明等号后有运算式，E下是加减运算式，例如int i = 1 + 2，T下是乘除运算式
            op = math_op(root.child[1].child[0]) # 这里递归遇到终结符（+ - * /）直接就返回符号
            arg1 = math_op(root.child[0]) # 计算参数1
            arg2 = math_op(root.child[1].child[1]) # 计算参数2
            """静态的计算提前算好"""
            if if_num(arg1) and if_num(arg2):
                return str(operator[op](int(arg1), int(arg2)))

            t = "T" + str(tmp)
            tmp += 1
            mid_result.append(MNode(op, arg1, arg2, t))
            ct = math_op(root.child[1].child[2], t)
            if ct != None:
                return ct
            return t
        else:
            return math_op(root.child[0])
    elif root.type == "F" and len(root.child) == 2:
        c = root.child
        if c[1].child != [] and c[1].child[0].type == "Size":
            return c[0].child[0].text + "[]" + math_op(c[1])
        else:
            return c[0].child[0].text

    else: # LM, FE
        re = ""
        for c in root.child:
            cre = math_op(c)
            if cre != None and cre not in "[]}{)(\"'":
                re = cre
        return re


"""
控制语句的程序块处理
可处理语句：
    １. if语句
    ２. while语句
    ３. if和while的相互嵌套语句
"""
def judge(root):
    if root == None:
        return
    elif len(root.child) == 0 and root.text != None:
        return root.text
    if root.type == "Ptype":
        if root.child[0].text == "if":
            while_flag.append([False])
        else:
            """
            对whilie语句进行代码块标记，方便跳转
            """
            cur = len(mid_result)
            while_flag.append([True,cur])
            mid_result.append(MNode("code_block", 0, 0, "W" + str(cur)))
    if root.type == "Pbc":
        """
        判断语句括号中的的两种情况
        1. (E)
        2. (E1 cmp E2)
        """
        Pm = root.child[1].child
        if len(Pm) == 1: # 此时括号里面就是一个数，如果这个数等于1，就跳转到下一条指令，下一条指令即是if条件满足时执行的操作
            mid_result.append(MNode("j=", 1, math_op(root.child[0]), "code" + str(len(mid_result) + 1)))
        else: # PM -> Cmp E 否则就递归计算两个参数
            mid_result.append(MNode("j" + judge(Pm[0]), math_op(root.child[0]), math_op(Pm[1]), "code" + str(len(mid_result) + 1)))
        return
    if root.type == "Pro":
        """
        控制语句的代码块前后做标记
        判断标记
        跳转->结束标记
        {
            code
        }
        while跳转->判断标记
        结束标记
        """
        w = while_flag.pop()
        code_block = len(mid_result)
        code = "block" + str(code_block)
        mid_result.append(MNode("j", 0, 0, code))
        mid_result.append(MNode("code_block", 0, 0, "code" + str(code_block)))
        view_astree(root)
        if w[0] == True:
            mid_result.append(MNode("j", 0, 0, "W" + str(w[1])))
        mid_result.append(MNode("code_block", 0, 0, code))
        code_block += 1
        return
    else:
        re = ""
        for c in root.child:
            cre = judge(c)
            if cre != None and cre not in "[]}{)(\"'":
                re = cre
        return re


"""
输出处理
可处理语句：printf(a,b) 该语法：在括号内只能传入变量参数
"""
def out(root):
    if root == None:
        return
    elif root.type == "V":
        if len(root.child) <= 1:
            mid_result.append(MNode("print", '-1', '-1', '-1'))
            return
        else:
            name = [math_op(root.child[1])]
            V = root.child[2]
            while len(V.child) > 1:
                name.append(math_op(V.child[1]))
                V = V.child[2]
            name.extend(['-1','-1','-1'])
            mid_result.append(MNode("print", name[0], name[1], name[2]))
    else:
        for c in root.child:
            out(c)

def creat_mcode(filename):
    global tmp
    global mid_result
    global arr
    arr = {}
    tmp = 0
    mid_result = []
    w_list = word_list(filename)
    word_table = w_list.word_list
    string_list = w_list.string_list
    root = analysis(word_table)[1] # 生成语法树
    view_astree(root)

    return {"name_list":w_list.para_list, "mid_code":mid_result, "tmp":tmp, "strings":string_list, "arrs":arr}
        
if __name__ == "__main__":
    filename = 'test/judge.c'
    creat_mcode(filename)
    for r in mid_result:
        print(r)
