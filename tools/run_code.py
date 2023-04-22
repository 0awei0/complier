import tkinter
import tkinter as tk
import tkinter.simpledialog

from tools.generate_code import GenerateCode
from tools.ll1 import LL1
from tools.word_analyser import Lexer


class RunCode:
    def __init__(self, code, window):
        """

        :param code: 中间代码
        :param window: tk
        """
        super().__init__()
        self.res_info = ""
        self.code_str = ""
        self.variable = dict()
        self.code = code
        self.code2str()

        self.window = window
        self.text1 = tk.Text(self.window, undo=True, font=('consolas', 12))
        self.insert_code()
        self.text2 = tk.Text(self.window, undo=True, font=('consolas', 12))
        self.button = tk.Button(self.window, text="运行", command=lambda: self.run_it(code))

        self.text1.place(relx=0.05, rely=0.1, relheight=0.5, relwidth=0.4)
        self.text2.place(relx=0.55, rely=0.1, relheight=0.5, relwidth=0.4)
        self.button.place(relx=0.45, rely=0.8)

        self.window.mainloop()

    def insert_code(self):
        self.text1.insert("insert", self.code_str)

    def code2str(self):
        self.code_str = ''
        for j in range(len(self.code)):
            i = self.code[j]
            self.code_str += str(j) + '    (' + i[0] + ',' + i[1] + ',' + i[2] + ',' + i[3] + ')\n'

    def check_arg(self, code, i):
        if code[i][1] in self.variable:
            arg1 = self.variable[code[i][1]]
        else:
            arg1 = int(code[i][1])
        if code[i][2] in self.variable:
            arg2 = self.variable[code[i][2]]
        else:
            arg2 = int(code[i][2])
        return arg1, arg2

    def run_it(self, code):
        self.res_info = ''
        i = 0
        while i < len(code):
            if code[i][0] == '=':
                if code[i][3] in self.variable:
                    res = int(self.variable[code[i][3]])
                # 读取输入
                elif code[i][3] == 'read()':
                    res = tkinter.simpledialog.askinteger(title="输入", prompt='输入' + code[i][1] + '的值')
                    res = int(res)
                else:
                    res = int(code[i][3])
                self.variable[code[i][1]] = res
                i += 1

            elif code[i][0] == 'j':
                if code[i][3] == 'write()':
                    print(self.variable[code[i][2]])
                    self.res_info += str(self.variable[code[i][2]]) + '\n'
                    i += 1
                else:
                    i = int(code[i][3])

            elif code[i][0] == 'j>=':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])
                arg1, arg2 = self.check_arg(code, i)
                if arg1 >= arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j<=':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])
                arg1, arg2 = self.check_arg(code, i)
                if arg1 <= arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j==':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])

                arg1, arg2 = self.check_arg(code, i)
                if arg1 == arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == 'j<':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])

                arg1, arg2 = self.check_arg(code, i)
                if arg1 < arg2:
                    i = int(code[i][3])
                else:
                    i += 1

            elif code[i][0] == '+':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])
                #
                arg1, arg2 = self.check_arg(code, i)
                self.variable[code[i][3]] = arg1 + arg2
                i += 1

            elif code[i][0] == '*':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])

                arg1, arg2 = self.check_arg(code, i)
                self.variable[code[i][3]] = arg1 * arg2
                i += 1

            elif code[i][0] == '%':
                # if code[i][1] in self.variable:
                #     arg1 = self.variable[code[i][1]]
                # else:
                #     arg1 = int(code[i][1])
                # if code[i][2] in self.variable:
                #     arg2 = self.variable[code[i][2]]
                # else:
                #     arg2 = int(code[i][2])

                arg1, arg2 = self.check_arg(code, i)
                self.variable[code[i][3]] = arg1 % arg2
                i += 1
        print("res: ", self.res_info)
        self.text2.delete(1.0, "end")
        self.text2.insert("insert", self.res_info)


def alg_test():
    with open("../Tests/test1.txt", encoding="utf-8-sig") as f:
        content = f.readlines()
    lex = Lexer(content)
    result = lex.result

    ll1 = LL1(result)
    code = GenerateCode(ll1.ast.root, ll1.end).code
    root = tk.Tk()
    root.geometry('600x400')
    RunCode(code, root)


if __name__ == '__main__':
    alg_test()
