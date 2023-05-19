import re
# 一些判断函数和字符分割函数放在同级文件function.py中
import sys, os
sys.path.append(os.pardir)  # 为了导入父目录的文件而进行的设定
from other.function import if_num, if_para, have_para, print_str, get_word, print_para

# 运算符表
op_list = {"+", "-", "*", "/", "<", "<=", ">", ">=", "=", "==", "!=", "^", ",", "&", "&&", "|", "||", "%", "~", "<<", ">>", "!"}
# 分隔符表
sp_list = {";", "(", ")", "[", "]", "{", "}", ".", ":", "\"", "#", "\'", "\\", "?"}
# 关键字表
k_list = {
    "auto", "break", "case", "const", "continue","default", "do",  "else", "enum", "extern",
    "for", "goto", "if", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union",  "volatile", "while", "printf"
}

Cmp = ["<", ">", "==", "!=", ">=", "<="]

Type = {"int","float","char","double","void","long","unsigned","string"}
type_flag = ""
# 括号配对判断
kuo_cp = {'{':'}', '[':']', '(':')'}

# 词法分析器输出对象
# 成员变量：输出的单词表，源代码中的分隔符表,运算符表,变量表,关键字表
# 一个方法，将源代码字符切割并存入对应表中
# 对象创建实例需要传入filename参数，默认为test.c
class word_list():
    def __init__(self, filename='test.c'):
        self.word_list = []          # 输出单词列表
        self.separator_list = []     # 分隔符
        self.operator_list = []      # 运算符
        self.para_list = []          # 变量
        self.key_word_table = []     # 关键字
        self.string_list = []
        self.flag = True             # 源代码是否正确标识
        
        # get_word函数将源代码切割
        self.creat_table(get_word(filename))

    # 创建各个表
    def creat_table(self, in_words):
        global type_flag
        para_id = 0
        kuo_list = []           # 存储括号并判断是否完整匹配
        char_flag = False
        str_flag = False
        strings = ""
        chars = ""
        for word in in_words:
            w = word['word']
            line = word['line']
            if w == '"':
                # 引号开头，判断为string类型
                if not str_flag: # 说明是开头的引号
                    str_flag = True
                else: # 说明是结束的引号
                    str_flag = False # 结束的引号后面没有字符串，置False
                    self.word_list.append({'line':line, 'type':'string', 'word':strings})
                    self.string_list.append(strings)
                    strings = "" # strings被重置为空
                # self.word_list.append({'line':line, 'type':w, 'word':w})
                continue
            # 判断是否为字符串
            if str_flag:
                strings += w
                continue
            if w == "'": # 单引号的处理和双引号类似
                if not char_flag:
                    char_flag = True
                else:
                    char_flag = False
                    self.word_list.append({'line':line, 'type':'character', 'word':chars})
                    chars = ""
                continue
            if char_flag:
                chars += w
                continue
            # 判断为关键字
            if w in k_list:
                self.key_word_table.append({'line':line, 'type':w, 'word':w})
                self.word_list.append({'line':line, 'type':w, 'word':w})
            elif w in Cmp:
                self.word_list.append({'line':line, 'type':'Cmp', 'word':w})
            # 判断为参数
            elif w in Type:
                type_flag = w
                self.key_word_table.append({'line':line, 'type':'type', 'word':w})
                self.word_list.append({'line':line, 'type':'type', 'word':w})
            # 判断为运算符
            elif w in op_list:
                self.operator_list.append({'line':line, 'type':w, 'word':w})
                self.word_list.append({'line':line, 'type':w, 'word':w})
            # 判断为分隔符
            elif w in sp_list:
                if w in kuo_cp.values() or w in kuo_cp.keys(): # key是左括号，value是右括号
                    # 左括号入栈
                    if w in kuo_cp.keys():
                        kuo_list.append({'kuo':w, 'line':line})
                    # 右括号判断是否匹配并出栈
                    elif w == kuo_cp[kuo_list[-1]['kuo']]:
                        kuo_list.pop()
                    else:
                        print("Error in line " + str(line) + ": missing bracket.")
                        self.flag = False
                        return
                self.separator_list.append({'line':line, 'type':w, 'word':w})
                self.word_list.append({'line':line, 'type':w, 'word':w}) # 这里type必须用w，而不是' separator '，因为后续LL分析时要用w
            # 其他字符处理
            else:
                if if_num(w):
                    self.word_list.append({'line':line, 'type':'number', 'word':w})
                # 如果是变量名要判断是否已经存在
                elif if_para(w): # 这里会把函数名和变量名都视为para·
                    if have_para(self.para_list, w):
                        self.word_list.append({'line':line, 'type':'parameter', 'word':w, 'id':para_id})
                    else:
                        self.para_list.append({'line':line, 'id':para_id, 'value':0.0, 'para':w, 'type':type_flag})
                        self.word_list.append({'line':line, 'type':'parameter', 'word':w, 'id':para_id})
                        para_id += 1
                else:
                    print("Error in line " + str(line) + ": " + w + " cannot be recognized.")
                    self.flag = False
                    return
        if kuo_list: # 当kuo_list不为空时
            print("Error in line" + str(kuo_list[0]['line']) + ": " + kuo_list[0]['kuo'] + " cannot be matched.")
            self.flag = False
            return
 
if __name__ == '__main__':

    # 写了三个测试的c语言文件在同级目录
    # 其中test.c是正常的代码
    # error1.c和error2.c是错误的测试代码

    filename = input("File path: ")
    if filename == '':
        filename = 'test/test.c'
    w_list = word_list(filename)
    if w_list.flag:
        print("\nWord Table:\n")
        print_str(w_list.word_list)
        print("\n\nParameter Table:\n")
        print_para(w_list.para_list)