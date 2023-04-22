import time


class Token(object):
    """
        定义的Token类，用于储存词法分析的结果，可以自己添加信息
    """

    def __init__(self, typ, value, code: int, pos: tuple = None):
        """

        :param typ:   单词的类型: int
        :param value: 单词的值:   1
        :param pos:   单词的位置: (1, 1) 第一行第一列
        """
        self.type = str(typ)
        self.value = str(value)
        self.code = code
        self.pos = pos

    def __str__(self):
        return "type: {} value: {} code: {} position: (row {}, col {})".format(self.type, self.value,
                                                                               self.code, self.pos[0], self.pos[1])


class Lexer:
    operator = None
    plus_num = None
    e_num = None
    dot_num = None
    brackets = None
    flag_eof = None

    def __init__(self, text):

        self.text = text
        self.line = 0
        self.col = 0
        self.status = 'a'

        self.cur = None
        self.temp = ''
        self.result = []
        self.tokens = []
        self.warnings = ''

        self.keyword_list = {'auto', 'double', 'int', 'struct', 'break', 'else', 'long', 'switch', 'case', 'enum',
                             'register', 'typedef', 'char', 'extern', 'return', 'union', 'const', 'float', 'short',
                             'unsigned', 'continue', 'for', 'signed', 'void', 'default', 'goto', 'sizeof', 'volatile',
                             'do', 'if', 'while', 'static', 'func', "include", "bool", "def"}
        self.delimiters = [";", ",", "{", "}", "#"]  # 界符
        self.operators = ['(', ')', '[', ']', '!', '*', '/', '%', '+', '-', '<', '<=',
                          '>', '>=', '==', '!=', '&&', '||', '=', '.', "++", "+="]  # 运算符

        # 单词--种别码表
        self.category2id = {
            "char": 101,
            "int": 102,
            "float": 103,
            "break": 104,
            "const": 105,
            "return": 106,
            "void": 107,
            "continue": 108,
            "do": 109,
            "while": 110,
            "if": 111,
            "else": 112,
            "for": 113,
            "main": 114,
            "printf": 115,
            "include": 116,
            "bool": 117,
            "def": 118,

            "identifier": 700,
            "number": 400,
            "oct num": 401,
            "hex num": 402,
            "string": 600,

            "{": 301,
            "}": 302,
            ";": 303,
            ",": 304,

            "(": 201,
            ")": 202,
            "[": 203,
            "]": 204,
            "!": 205,
            "*": 206,
            "/": 207,
            "%": 208,
            "+": 209,
            "-": 210,
            "<": 211,
            "<=": 212,
            ">": 213,
            ">=": 214,
            "==": 215,
            "!=": 216,
            "&&": 217,
            "||": 218,
            "=": 219,
            ".": 220,
            "#": 221,
            "++": 222
        }

        self.board_char_list = {';', ',', '.'}
        self.brackets_list = {'{', '}', '[', ']', '(', ')'}
        self.recognize()
        # for token in self.tokens:
        #     print(token)
        # for i in self.result:
        #     print(i)
        # print(self.warnings)

    def is_letter(self):
        return self.cur.isalpha()

    def is_number(self):
        return self.cur.isdigit()

    def is_keyword(self):
        return self.temp in self.keyword_list

    def is_board(self):
        return self.cur in self.board_char_list

    def is_brackets(self):
        return self.cur in self.brackets_list

    def is_left_brackets(self):
        if self.cur == '{' or self.cur == '[' or self.cur == '(':
            return True
        else:
            return False

    # 判断空白符
    def is_empty(self):
        if self.cur == ' ' or self.cur == '\n' or self.cur == '\t':
            return True
        else:
            return False

    # 判断括号是否闭合
    def is_close(self):
        if self.brackets[len(self.brackets) - 1][0] == '{':
            if self.cur == '}':
                return True
            else:
                return False
        elif self.brackets[len(self.brackets) - 1][0] == '[':
            if self.cur == ']':
                return True
            else:
                return False
        elif self.brackets[len(self.brackets) - 1][0] == '(':
            if self.cur == ')':
                return True
            else:
                return False

    # 获得当前字符
    def getchar(self):
        if self.col == len(self.text[self.line]):
            if self.line + 1 == len(self.text):
                self.cur = 'EOF'
                return
            else:
                self.line += 1
                self.col = 0
        self.cur = self.text[self.line][self.col]
        self.col += 1
        self.temp += self.cur

    # 回退
    def backward(self):
        if not self.flag_eof:
            self.temp = self.temp[:-1]
            self.col -= 2
            self.cur = self.text[self.line][self.col]
            self.col += 1

    # 保存当前识别的token，并将状态置为a，重新开始识别
    def save(self, category):
        if category == 'self':
            category = self.temp.lower()

        temp_result = ['', '', '', '']
        temp_result[0] = self.temp  # 单词本身
        temp_result[1] = category  # 单词类别
        temp_result[2] = str(self.line + 1)  # 行
        temp_result[3] = str(self.col - len(self.temp) + 1)  # 列

        if category != 'note':
            self.result.append(temp_result.copy())

            if self.temp in self.delimiters:
                category = "delimiters"
                code = self.category2id.get(self.temp)

            elif self.temp in self.operators:
                category = "operators"
                code = self.category2id.get(self.temp)

            elif self.temp in self.keyword_list:
                category = "keyword"
                code = self.category2id.get(self.temp)

            else:
                code = self.category2id.get(category)
            self.tokens.append(Token(category, temp_result[0], code, (temp_result[2], temp_result[3])))

        self.status = 'a'
        self.temp = ''

    # 输出错误信息
    def warning(self, category):
        # self.warnings += time.strftime("[%H:%M:%S]  ")
        self.warnings += "Error\t"
        self.warnings += (self.temp + ' at row ' +
                          str(self.line + 1) + ' col ' + str(self.col - len(self.temp)))

        if category == 0:
            self.warnings += ': failed recognizing char\n'
        elif category in [2, 3]:
            self.warnings += ': brackets not close\n'
        elif category == 4:
            self.warnings += ': no left bracket\n'
        elif category == 5:
            self.warnings += ': illegal identifier\n'
        elif category == 6:
            self.warnings += ': note not close\n'
        elif category == 7:
            self.warnings += ': illegal octal number\n'
        elif category == 8:
            self.warnings += ': illegal hex number\n'
        elif category == 9:
            self.warnings += ': illegal number char\n'
        elif category == 10:
            self.warnings += ": illegal operator\n"
        self.status = 'a'
        self.temp = ''

    # 初态a
    def status_a(self):
        # 标识符
        if self.is_letter() or self.cur == '_':
            self.status = 'b'

        elif self.is_number():
            # 判断数字的进制
            if self.cur == '0':
                self.getchar()
                if self.cur in ['x', 'X']:
                    self.status = 'c16'  # 16进制
                    return
                elif self.is_number():
                    self.backward()
                    self.status = 'c8'  # 8进制
                elif self.cur == '.':
                    self.dot_num += 1
                    self.status = 'c'  # 小数
                else:
                    self.backward()
                    self.save('number')
            else:
                self.status = 'c'  # 整数

        # 判断单双引号(识别字符和字符串常量)
        elif self.cur in ['\'', '\"']:
            temp_quote = self.cur
            self.getchar()
            while self.cur != temp_quote:
                self.getchar()

                if self.cur == ";":
                    self.warning(2)
                    return

                if self.cur == 'EOF':
                    self.warning(2)
                    self.flag_eof = True
                    return

            if self.cur == temp_quote:
                self.save('string')

        # 判断界符 {';', ',', '.'}
        elif self.is_board():
            self.save('self')

        # 识别括号 {'{', '}', '[', ']', '(', ')'}
        elif self.is_brackets():
            # 栈中括号不为空
            if self.brackets:
                # 是左括号则入栈
                if self.is_left_brackets():
                    self.save('self')
                    temp = [self.cur, self.line, self.col]
                    self.brackets.append(temp)
                # 若括号闭合，则保存括号且将括号出栈
                elif self.is_close():
                    self.save('self')
                    self.brackets.pop()
                # 否则警告
                else:
                    self.warning(4)
            else:  # 栈中无括号
                self.save('self')
                temp = [self.cur, self.line, self.col]
                self.brackets.append(temp)
        # 识别注释
        elif self.cur == '/':
            self.status = 'd'

        elif self.cur == "!":
            self.getchar()
            if self.cur == "+":
                self.temp = "!+"
                self.warning(10)

            # if self.cur == "=":
            #     self.getchar()
            #     if self.cur == "=":
            #         self.temp = ">=="
            #         self.warning(10)
            #     else:
            #         self.temp = ">="
            #         self.backward()

        elif self.cur in ['\\', '#', ':', '!', '?', '~', '^']:
            self.save(self.cur)
        # 识别运算符
        elif self.cur in ['+', '-', '*', '=', '%', '&', '|', '<', '>']:
            self.status = 'op'
            self.operator = self.cur
        # 跳过空白符
        elif self.is_empty():
            self.temp = self.temp[:-1]
        # 输出警告，不能识别字符
        else:
            self.warning(0)

    def status_b(self):
        if self.is_letter() or self.is_number() or self.cur == '_':
            return
        else:
            self.backward()
            if self.is_keyword():
                self.save('self')
            else:
                self.save('identifier')

    # 识别浮点数
    def status_c(self):
        if self.is_number():
            return

        elif self.cur in ['e', 'E']:
            if self.e_num >= 1:
                self.warning(9)
            else:
                self.e_num += 1

        elif self.cur == '+':
            if self.plus_num >= 1:
                self.warning(9)
            else:
                self.plus_num += 1

        elif self.cur == '.':
            if self.dot_num >= 1:
                self.warning(9)
            else:
                self.dot_num += 1

        elif self.is_letter() or self.cur == '_':
            self.warning(5)

        else:
            self.backward()
            self.save('number')
            self.dot_num = 0
            self.e_num = 0
            self.plus_num = 0

    def status_c8(self):
        if self.is_number():
            if '0' <= self.cur <= '7':
                return
            else:
                self.warning(7)
        else:
            self.backward()
            self.save('oct num')

    def status_c16(self):
        if self.is_number():
            return
        if self.is_letter():
            if 'a' <= self.cur <= 'f':
                return
            elif 'A' <= self.cur <= 'F':
                return
            else:
                self.warning(8)
        else:
            self.backward()
            self.save('hex num')

    def status_op(self):
        if self.cur in ['=', self.operator]:
            self.save('self')
        else:
            self.backward()
            self.save('self')

    # 识别注释
    def status_d(self):
        if self.cur == '=':
            self.save('double op')
        elif self.cur == '/':
            while self.cur not in ['EOF', '\n']:
                self.getchar()
            self.save('note')
        elif self.cur == '*':
            while True:
                self.getchar()
                if self.cur == '*':
                    self.getchar()
                    if self.cur == '/':
                        self.save('note')
                        break
                elif self.cur == 'EOF':
                    self.warning(6)
                    break
        else:
            self.backward()
            self.save('op')

    # 识别
    def recognize(self):
        self.flag_eof = False
        self.brackets = []
        self.dot_num = 0  # 浮点数记录.个数，大于一则报错
        self.e_num = 0  # 浮点数记录e个数，大于一则报错
        self.plus_num = 0  # 浮点数记录+个数，大于一则报错

        while True:
            # 如果字符已读完，且栈中还有界符，证明界符未闭合
            if self.flag_eof:
                while self.brackets:  # 若栈中括号不为空
                    temp = self.brackets.pop()
                    self.cur = temp[0]
                    self.line = temp[1]
                    self.col = temp[2]
                    self.warning(2)
                break

            self.getchar()
            if self.cur == 'EOF':
                self.cur = ' '
                self.flag_eof = True
            if self.status == 'a':  # 初态
                self.status_a()
            elif self.status == 'b':  # 标识符
                self.status_b()
            elif self.status == 'c':  # 10进制数字
                self.status_c()
            elif self.status == 'd':  # 运算符或注释
                self.status_d()
            elif self.status == 'c8':  # 8进制数
                self.status_c8()
            elif self.status == 'c16':  # 16进制数
                self.status_c16()
            elif self.status == 'op':  # 运算符
                self.status_op()


if __name__ == '__main__':
    with open("../Tests/test6.txt", encoding="utf-8-sig") as f:
        content = f.readlines()
    # print(content)
    a = Lexer(content)
    print(a.result)
