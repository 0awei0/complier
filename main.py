import chardet
import tkinter as tk
import os
import idlelib.colorizer as idc
import idlelib.percolator as idp

from ttkbootstrap import Style
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tools.word_analyser import Lexer
from tools.lexer import get_all_tokens
from tools.ll1 import LL1
from tools.auto_grammar_inspect import parser_file
from tools.generate_code import GenerateCode
from tools.run_code import RunCode
from tools.automata_window import AutomataWindow
from tkinter.messagebox import showinfo


class BaseWindow:
    # 初始化窗口
    def __init__(self, window):
        self.window = window
        self.text1 = tk.Text(self.window, undo=True, font=('consolas', 12))
        self.text2 = tk.Text(self.window, undo=True, font=('consolas', 12))
        self.text3 = tk.Text(self.window, undo=True, font=('consolas', 12))

        self.scroll1 = tk.Scrollbar()
        self.scroll2 = tk.Scrollbar()
        self.scroll3 = tk.Scrollbar()

        self.highlight_keywords()
        self.setup_text_window()
        self.setup_menu()
        self.window.mainloop()

    # 调整滑动条位置
    @staticmethod
    def setup_scrolls(text, scroll, scroll_params, text_params):
        # 放到text1的右侧, 填充Y竖直方向
        scroll.place(relx=scroll_params[0], rely=scroll_params[1], relheight=scroll_params[2])
        # 两个控件关联
        scroll.config(command=text.yview)
        text.config(yscrollcommand=scroll.set)
        text.place(relx=text_params[0], rely=text_params[1], relheight=text_params[2], relwidth=text_params[3])

    # text1关键字高亮
    def highlight_keywords(self):
        idc.color_config(self.text1)
        self.text1.focus_set()
        p = idp.Percolator(self.text1)
        d = idc.ColorDelegator()
        p.insertfilter(d)

    # 建立文本框
    def setup_text_window(self):
        # 滑动条的x, y, height
        scroll_params = [[0.6, 0, 0.95], [0.95, 0, 0.45], [0.95, 0.5, 0.45]]
        # 文本框的x, y, height, width
        text_params = [[0, 0, 0.95, 0.6], [0.65, 0, 0.45, 0.3], [0.65, 0.5, 0.45, 0.3]]
        texts = [self.text1, self.text2, self.text3]
        scrolls = [self.scroll1, self.scroll2, self.scroll3]

        # 设置三个文本框及滑动条的位置
        for idx, scroll_params in enumerate(scroll_params):
            self.setup_scrolls(texts[idx], scrolls[idx], scroll_params, text_params[idx])

        self.text1.bind("<Button-3>", lambda x: self.right_key(x, self.text1))  # 绑定右键鼠标事件
        self.text2.bind("<Button-3>", lambda x: self.right_key(x, self.text2))  # 绑定右键鼠标事件
        self.text3.bind("<Button-3>", lambda x: self.right_key(x, self.text3))  # 绑定右键鼠标事件

    # 建立主菜单
    def setup_menu(self):
        main_menu = Menu(self.window)
        # 文件选项
        menu_file = Menu(main_menu)  # 菜单分组 menuFile
        main_menu.add_cascade(label="文件", menu=menu_file)
        menu_file.add_command(label="新建", accelerator='Ctrl+N', command=lambda: self.new_file("new file"))
        menu_file.add_command(label="打开", accelerator='Ctrl+O', command=lambda: self.open_file("open file"))
        menu_file.add_command(label="保存", accelerator='Ctrl+S', command=lambda: self.save_file("save file"))
        menu_file.add_separator()  # 分割线
        menu_file.add_command(label="退出", command=self.window.destroy)

        # 词法分析
        menu_edit = Menu(main_menu)  # 菜单分组 menuEdit
        main_menu.add_cascade(label="词法分析", menu=menu_edit)
        menu_edit.add_command(label="状态转换图", command=self.word_analysis)
        menu_edit.add_command(label="自动", command=self.re_match)
        menu_edit.add_command(label="NFA->DFA", command=self.automata)

        # 语法分析
        menu_edit = Menu(main_menu)  # 菜单分组 menuEdit
        main_menu.add_cascade(label="语法分析", menu=menu_edit)
        menu_edit.add_command(label="ll1预测分析", command=lambda: self.ll1_grammar_analysis())
        menu_edit.add_command(label="自动", command=lambda: self.auto_grammar_analysis())

        # 中间代码
        menu_edit = Menu(main_menu)  # 菜单分组 menuEdit
        main_menu.add_cascade(label="中间代码", menu=menu_edit)
        menu_edit.add_command(label="生成", command=lambda: self.generate_code())

        # 目标代码生成
        menu_edit = Menu(main_menu)  # 菜单分组 menuEdit
        main_menu.add_cascade(label="运行代码", menu=menu_edit)
        menu_edit.add_command(label="解释器运行", command=lambda: self.run_code())

        # 帮助
        menu_edit = Menu(main_menu)  # 菜单分组 menuEdit
        main_menu.add_cascade(label="帮助", menu=menu_edit)
        menu_edit.add_command(label="查看使用文档", command=lambda: self.help())

        self.window.config(menu=main_menu)
        root.bind("<Control-N>", self.new_file)
        root.bind("<Control-O>", self.open_file)
        root.bind("<Control-S>", self.save_file)

    def help(self):
        with open("help.txt", encoding=self.get_encoding("help.txt")) as f:
            content = f.read()
        showinfo(title="编译器使用帮助", message=content)

    @staticmethod
    def automata():
        automata_win = tk.Toplevel()
        automata_win.geometry('800x600')
        automata_win.title("NFA->DFA转化")
        icon = tk.PhotoImage(file="pictures/logo.gif")
        automata_win.tk.call("wm", "iconphoto", automata_win._w, icon)
        AutomataWindow(automata_win, r"pictures/img.png", path="pictures/")

    def run_code(self):
        content = self.text1.get(0.0, tk.END).splitlines()
        content = [i + "\n" for i in content]

        result = Lexer(content).result
        ll1 = LL1(result, grammar_path="tools/grammar.txt")

        code = GenerateCode(ll1.ast.root, ll1.end).code
        run_win = tk.Toplevel()
        run_win.geometry('600x400')
        run_win.title("解释器运行")
        icon = tk.PhotoImage(file="pictures/logo.gif")
        run_win.tk.call("wm", "iconphoto", run_win._w, icon)
        RunCode(code, run_win)

    def get_lexer_result(self):
        content = self.text1.get(0.0, tk.END).splitlines()
        content = [i + "\n" for i in content]

        result = Lexer(content).result
        ll1 = LL1(result)

        return ll1

    def generate_code(self):
        self.clean()
        content = self.text1.get(0.0, tk.END).splitlines()
        content = [i + "\n" for i in content]

        result = Lexer(content).result
        ll1 = LL1(result, grammar_path="tools/grammar.txt")

        code = GenerateCode(ll1.ast.root, ll1.end)

        error = ""
        code_str = ""
        if len(code.warn) != 0:
            print("存在语义错误")
            for i in code.warn:
                error += i + '\n'
        else:
            for i in range(len(code.code) - 1):
                code_str += code.code[i][0] + "\t" + code.code[i][1] + "\t" + code.code[i][2] + "\t"
                # print(code.code[i][0], code.code[i][1], code.code[i][2])
                if isinstance(code.code[i][3], int):
                    code_str += str(int(code.code[i][3]) + 1) + "\n"
                    # print(str(int(code.code[i][3]) + 1))
                else:
                    code_str += code.code[i][3] + "\n"
                    # print(code.code[i][3])
        self.text2.insert("insert", code_str)
        self.text3.insert("insert", error)
        print("*" * 20)
        print(code.code)

    def clean(self):
        self.text2.delete(1.0, END)
        self.text3.delete(1.0, "end")

    def ll1_grammar_analysis(self):
        self.clean()
        content = self.text1.get(0.0, tk.END).splitlines()
        content = [i + "\n" for i in content]
        print(content)

        lexer = Lexer(content)
        result = lexer.result
        ll1 = LL1(result, render_tree=True, grammar_path="tools/grammar.txt", picture_path="pictures/ast_tree")
        if ll1.welldone == 1:
            print("success")
        else:
            print("failed")

    def auto_grammar_analysis(self):
        self.clean()
        content = self.text1.get(0.0, tk.END).splitlines()
        lines = [i + "\n" for i in content]
        ast = parser_file(lines, render_picture=True, picture_path="pictures/syntax_tree")
        # tree = ""
        # for node in ast.ext:
        #     tree += node.__str__()
        # self.text2.insert("insert", tree)

    # 词法分析
    def word_analysis(self):
        self.clean()

        content = self.text1.get(0.0, tk.END).splitlines()
        content = [i + "\n" for i in content]
        print(content)

        lexer = Lexer(content)
        tokens = lexer.tokens

        self.text2.insert("insert", "type\t\t" + "value\t\t" + "code   \n")
        self.text2.insert("insert", "-" * 40 + "\n")
        for token in tokens:
            item = "{}\t\t{}\t\t{}\n".format(token.type, token.value, token.code)
            self.text2.insert("insert", item)

        warning = lexer.warnings
        self.text3.insert("insert", warning)

    def re_match(self):
        self.clean()

        content = self.text1.get(0.0, tk.END)
        tokens, warning_info = get_all_tokens(content)
        self.text2.insert("insert", "type\t\t" + "value\n")
        self.text2.insert("insert", "-" * 20 + "\n")

        for token in tokens:
            item = "{}\t\t{}\n".format(token.type, token.value)
            self.text2.insert("insert", item)
        self.text3.insert("insert", warning_info)

    def new_file(self, event):
        self.text1.delete(1.0, END)

    # 获取文件编码类型
    @staticmethod
    def get_encoding(file):
        # 二进制方式读取，获取字节数据，检测类型
        with open(file, 'rb') as f:
            return chardet.detect(f.read())['encoding']

    # 打开指定文件并显示到文本框中
    def open_file(self, event):
        file_path = askopenfilename(title="选择一个txt文件", initialdir="")
        print("encoding: ", self.get_encoding(file_path))
        with open(file_path, encoding=self.get_encoding(file_path)) as f:
            content = f.read()

        self.text1.delete(1.0, END)
        self.text1.insert('insert', content)

    def save_file(self, event):
        filename = tk.filedialog.asksaveasfilename()
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(self.text1.get(0.0, tk.END))
            basename = os.path.basename(filename)
            save_succeed = messagebox.showinfo(title='message', message='%s保存成功' % basename)
            print("文件另存为：", save_succeed)

    @staticmethod
    def cut(editor, event=None):
        editor.event_generate("<<Cut>>")

    @staticmethod
    def copy(editor, event=None):
        editor.event_generate("<<Copy>>")

    @staticmethod
    def paste(editor, event=None):
        editor.event_generate('<<Paste>>')

    # 右键事件
    def right_key(self, event, editor):
        menubar = Menu(root, tearoff=False)  # 创建一个菜单
        menubar.delete(0, END)
        menubar.add_command(label='剪切', command=lambda: self.cut(editor))
        menubar.add_command(label='复制', command=lambda: self.copy(editor))
        menubar.add_command(label='粘贴', command=lambda: self.paste(editor))
        menubar.post(event.x_root, event.y_root)


if __name__ == '__main__':
    style = Style(theme='minty')
    # 想要切换主题，修改theme值即可，有以下这么多的主题，自己尝试吧：
    # ['vista', 'classic', 'cyborg', 'journal', 'darkly', 'flatly', 'clam',
    # 'alt', 'solar', 'minty', 'litera', 'united', 'xpnative', 'pulse', 'cosmo',
    # 'lumen', 'yeti', 'superhero', 'winnative', 'sandstone', 'default']
    root = style.master
    # 这两行代码在自己原基础的代码上加入即可，放在代码的最开端部分，也就是在窗口创建代码之前
    # 设置图标
    icon = tk.PhotoImage(file="pictures/logo.gif")
    root.tk.call("wm", "iconphoto", root._w, icon)

    # root = Tk()
    root.title('Compiler')
    root.geometry('800x600')
    BaseWindow(root)
