#!/usr/bin/env python
# -*- coding: utf-8 -*- #
# ==================================================
# File Name:        busslog.py
# Author:           Qingzheng WANG
# Time:             2023/6/13 20:53
# Description:      业务逻辑
# Function List:    
# ===================================================

from main_window import Ui_MainWindow
from PyQt5 import QtWidgets
from util.function import print_str, print_para, print_mid_code
from generate import creat_mcode

class MainWindowUi(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def save_code(self):
        txt = self.textEditCode.toPlainText()
        # 让windows保存文件窗口跳出，命名，保存文件为.c文件
        fileName, ok = QtWidgets.QFileDialog.getSaveFileName(self, "文件保存", "D:\\2023大三下\\PCC\\test", "C Files (*.c)")
        if ok:
            with open(fileName, 'w', encoding="utf-8") as f:
                f.write(txt)
                f.close()
        return fileName

class BussLog():
    def __init__(self):
        self.main_window = MainWindowUi()
        self.save_flag = False
        self.file_name = ""
        self.main_window.pushButtonC.clicked.connect(self.on_click_compile)
        self.main_window.pushButtonS.clicked.connect(self.on_click_save)

    def on_click_compile(self):
        if not self.save_flag:
            self.file_name = self.main_window.save_code()
        d = creat_mcode(self.file_name)
        print(0)
        # 判断d的长度，如果为1，说明编译失败，否则编译成功
        if len(d) == 1:
            print(0.1)
            self.main_window.textBrowserTable.clear()
            self.main_window.textBrowserMCode.clear()
            self.main_window.textBrowserMCode.setText("编译失败")
            self.main_window.textBrowserTable.setText(d['error_info'])
            return
        print(1)
        para_list = d['name_list']
        print(1.1)
        mid_code = d['mid_code']
        print(1.2)
        string_list = d['strings']
        print(1.3)
        table = "参数表\n" + print_para(para_list) + "\n" + "单词表\n" + print_str(string_list)
        print(1.4)
        mid_code = "中间代码\n" + print_mid_code(mid_code)
        print(2)
        self.main_window.textBrowserTable.clear()
        self.main_window.textBrowserMCode.clear()
        print(3)
        self.main_window.textBrowserTable.setText(table)
        self.main_window.textBrowserMCode.setText(mid_code)

    def on_click_save(self):
        self.file_name = self.main_window.save_code()
        self.save_flag = True

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = BussLog()
    ui.main_window.show()
    sys.exit(app.exec_())