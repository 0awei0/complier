import ply.lex as lex

error_info = ''

reserved_keywords = {
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'goto': 'GOTO',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'unsigned': 'UNSIGNED',
    'int': 'INT',
    'char': 'CHAR',
    'float': 'FLOAT',
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'return': 'RETURN',
    'void': 'VOID',
    'main': 'MAIN',
}

tokens = [
             "NOT",  # !
             'PLUS',  # +
             'PLUS1',  # ++
             'MINUS',  # -
             'MINUS1',  # --
             'TIMES',  # *
             'TIMES_EQUAL',  # *=
             'DIVIDE',  # /
             'DIVIDE_EQUAL',  # /=
             'GT',  # >
             'LT',  # <
             'GE',  # >=
             'LE',  # <=
             'EQUAL',  # ==
             'NEQUAL',  # !=
             'SEMI',  # ;
             'COMMA',  # ,
             'ASSIGN',  # =
             'LPAREN',  # (
             'RPAREN',  # )
             'LBRACKET',  # [
             'RBRACKET',  # ]
             'LBRACE',  # {
             'RBRACE',  # }
             'SHARP',  #
             'AND',  # &
             'OR',  # |
             'POINT',  # .
             'REM',  # %
             'ID',  # 标识符
             'NUM',  # 整数
             'HEX',  # 十六进制
             'OCT',  # 八进制
             'STR',  # 字符串
             'IEEE754',  # 浮点数
             'FNUM',  # 10进制数
             'LITERALCHAR',  # 单个字符
         ] + list(reserved_keywords.values())

# 定义每种左括号对应的右括号
brackets = {'(': ')', '{': '}', '[': ']'}

# 定义一个栈，用来存储遇到的左括号
stack = []


def ply_lexer():
    digit = r'([0-9])'  # 匹配数字
    letter = r'([_A-Za-z])'  # 匹配字母和下划线
    identifier = r'(' + letter + r'(' + digit + r'|' + letter + r')*)'  # 标识符的正则表达式
    number = r' 0 | [1-9]\d* '  # 数字的正则表达式

    # 一些符号的正则表达式
    t_NOT = r'\!'
    t_PLUS = r'\+'
    t_PLUS1 = r'\+\+'
    t_MINUS = r'-'
    t_MINUS1 = r'--'
    t_TIMES = r'\*'
    t_TIMES_EQUAL = r'\*\='
    t_DIVIDE = r'/'
    t_DIVIDE_EQUAL = r'/\='
    t_LT = r'\<'
    t_LE = r'\<\='
    t_GT = r'\>'
    t_GE = r'\>\='
    t_EQUAL = r'\=\='
    t_NEQUAL = r'\!\='
    t_ASSIGN = r'\='
    t_SEMI = r';'
    t_COMMA = r','
    t_SHARP = r'\#'
    t_REM = r'%'
    t_AND = r'&'
    t_OR = r'\|'
    t_POINT = r'\.'

    # t_STR = r'(\' .* \') | (\" .* \")'
    t_STR = r'(\" .* \")'
    t_LITERALCHAR = r"'([^\"?\\\\\\n\\r]|\\\\[0-7xuUa-fA-F]+)'"

    # 定义一个函数，用来检查每个标记是否是有效的括号，并在遇到不匹配或者未闭合的情况下输出错误信息
    def check_bracket(t):
        global stack, error_info
        if t.value in brackets.keys():  # 如果是左括号，就入栈
            stack.append(t)
        elif t.value in brackets.values():  # 如果是右括号，就和栈顶元素比较
            if stack and brackets[stack[-1].value] == t.value:  # 如果匹配，就出栈
                stack.pop()
            else:  # 如果不匹配，就报错
                print(f"Error: unmatched bracket {t.value} at line {t.lineno}")
                error_info += f"不匹配的括号 {t.value} 在 {t.lineno} 行\n"
        # 定义正则表达式规则来匹配各种括号，并调用上面定义的函数来检查它们

    def t_LPAREN(t):
        r"""\("""
        check_bracket(t)
        return t

    def t_RPAREN(t):
        r"""\)"""
        check_bracket(t)
        return t

    def t_LBRACE(t):
        r"""\{"""
        check_bracket(t)
        return t

    def t_RBRACE(t):
        r"""\}"""
        check_bracket(t)
        return t

    def t_LBRACKET(t):
        r"""\["""
        check_bracket(t)
        return t

    def t_RBRACKET(t):
        r"""\]"""
        check_bracket(t)
        return t

    # 定义识别未闭合STRING的正则表达式
    def t_STR_ERROR(t):
        r""" "([^"\;] | (\.))*; """
        global error_info
        if t.value[-1] != '"':
            print('Error string {} at row {} '.format(t.value, t.lexer.lineno))
            error_info += '非法的字符串 {} 在 {} 行 \n'.format(t.value, t.lexer.lineno)
            t.lexer.skip(1)  # 跳过非法字符
        else:
            t.value = t.value[1:-1]  # 去掉引号

    # 定义识别未闭合单个字符的正则表达式
    def t_LITERALCHAR_ERROR(t):
        r""" '([^'\;] | (\.))*; """
        global error_info
        if t.value[-1] != "'":
            print('Error char {} at row {} '.format(t.value, t.lexer.lineno))
            error_info += '非法的单个字符 {} 在 {} 行\n'.format(t.value, t.lexer.lineno)
            t.lexer.skip(1)  # 跳过非法字符
        else:
            t.value = t.value[1:-1]  # 去掉引号

    # 匹配浮点数
    def t_IEEE754(t):
        r"""([1-9] \d* . \d+ [Ee] \d* [+-] \d+) | ([1-9] \d* [Ee] ( (\d+) | ([+-] \d+)) )"""
        return t

    # 运算符错误
    def t_OPERATOR_ERROR(t):
        r""" (\!\+) | (>==)"""
        print('Error operator {} at row {} '.format(t.value, t.lexer.lineno))
        global error_info
        error_info += '非法的运算符 {} 在 {} 行'.format(t.value, t.lexer.lineno) + '\n'

    # 匹配标识符错误
    def t_ID_ERROR(t):
        r"""[1-9]+ [a-zA-Z]+"""
        print('Error ID {} at row {}'.format(t.value, t.lexer.lineno))
        global error_info
        error_info += '非法的标识符 {} 在 {} 行'.format(t.value, t.lexer.lineno) + '\n'

    # 匹配十进制数错误
    def t_FNUM_ERROR(t):
        r"""([1-9] \d* \. \d+ \. \d*)"""
        print('Error NUM {} at row {}'.format(t.value, t.lexer.lineno))
        global error_info
        error_info += '非法的数字 {} 在 {} 行'.format(t.value, t.lexer.lineno) + '\n'

    # 匹配十进制数
    def t_FNUM(t):
        r"""[1-9] \d* \. \d+"""
        return t

    # 匹配8进制数错误
    def t_OCT_ERROR(t):
        r"""(0 [0-7]* [8-9]+ [0-7]*) | (0 0+ [0-7]*) """
        print('Error OCT {} at row {}'.format(t.value, t.lexer.lineno))
        global error_info
        error_info += '非法的八进制数 {} 在 {} 行'.format(t.value, t.lexer.lineno) + '\n'

    # 匹配8进制数
    def t_OCT(t):
        r"""0 [0-7]+"""
        return t

    # 匹配16进制数错误
    def t_HEX_ERROR(t):
        r"""0 [xX] [0-9]* [g-zG-Z]+ [0-9]* """
        print('Error HEX {} at row {}'.format(t.value, t.lexer.lineno))
        global error_info
        error_info += '非法16进制数 {} 在 {} 行'.format(t.value, t.lexer.lineno) + '\n'

    # 匹配16进制数
    def t_HEX(t):
        r"""0 [xX] ([0-9] | [A-Fa-f])+ """
        return t

    def t_NUM(t):
        t.value = int(t.value)
        return t

    t_NUM.__doc__ = number

    def t_ID(t):
        t.type = reserved_keywords.get(t.value, 'ID')  # Check for reserved words
        # Look up symbol table information and return a tuple
        # t.value = (t.value, symbol_lookup(t.value))
        return t

    t_ID.__doc__ = identifier

    # 匹配/**/注释
    def t_comment(t):
        r""" (/\*(.|\n)*?\*/) | (/\*.*) """
        t.lexer.lineno += t.value.count('\n')

    # 匹配//注释
    def t_cpp_comment(t):
        r"""//.*\n"""
        t.lexer.lineno += 1

    # 记录行号
    def t_newline(t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    # 忽略空格及tab
    t_ignore = ' \t'

    # 处理不能识别的字符错误
    def t_error(t):
        global error_info
        print("Illegal character {} at row {}".format(t.value[0], t.lexer.lineno))
        error_info += "非法字符 {} 在 {} 行".format(t.value[0], t.lexer.lineno) + '\n'
        t.lexer.skip(1)

    # 在词法分析器结束后，检查栈是否为空，如果不为空，说明有未闭合的左括号存在，也要报错。
    def t_eof(t):
        global stack, error_info
        while stack:
            top = stack.pop()
            print(f"Error: unclosed bracket {top.value} at line {top.lineno}")
            error_info += f"未闭合的括号 {top.value} 在 {top.lineno} 行\n"

    # Build the lexer
    lexer = lex.lex()
    return lexer


def get_all_tokens(text):
    global error_info
    error_info = ""
    lexer = ply_lexer()

    all_tokens = []
    lexer.input(text)

    while True:
        token = lexer.token()
        if not token:
            break
        all_tokens.append(token)
        # print(str(token.value) + '\t\t' + token.type + '\t\t' + str(token.lineno))
    return all_tokens, error_info


def main():
    lexer = ply_lexer()
    data = open('../Tests/词法分析用例.txt', 'r', encoding='utf-8-sig').read()
    lexer.input(data)

    while True:
        token = lexer.token()
        if not token:
            break
        # print(str(token.value) + '\t\t' + token.type + '\t\t' + str(token.lineno))
    # print(error_info)


if __name__ == '__main__':
    main()
