import os
import re
import chardet

from pycparser import c_parser, c_ast
from graphviz import Digraph


def picturize_tree(ast, picture_path="../pictures/syntax_tree"):
    # 创建Graphviz图
    dot = Digraph(comment="C语言语法树")
    dot.node_attr['shape'] = 'box'

    # 辅助函数，递归遍历语法树节点，并将节点添加到Graphviz图中
    def traverse_ast(node):
        # 创建或更新该节点对应的Graphviz节点
        node_id = str(id(node))
        label = str(type(node).__name__)
        if isinstance(node, c_ast.IdentifierType):
            print(node.names)
            label += " (" + node.names[0] + ")"
        if isinstance(node, c_ast.Constant):
            label += " (" + str(node.value) + ")"
        dot.node(node_id, label=label)

        # 递归遍历该节点的子节点，并添加到Graphviz图中
        for _, child in node.children():
            child_id = str(id(child))
            dot.edge(node_id, child_id)
            traverse_ast(child)

    # 添加语法树根节点到Graphviz图中
    traverse_ast(ast)
    # 按照Graphviz DOT语言进行绘制
    dot.format = 'png'
    dot.render(picture_path, view=True)


def print_tree(ast):
    # 访问语法树的节点信息
    for node in ast.ext:
        print(node)


def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']


def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "  # note: a space and not an empty string
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


def parser_file(lines, render_picture=False, picture_path="../pictures/syntax_tree"):
    code = ""
    for line in lines:
        if not line.startswith("#"):
            code += line.strip() + "\n"
    code = comment_remover(code)
    code = code.replace("def", "")
    print(code)

    # 解析C语言代码
    parser = c_parser.CParser()
    ast = parser.parse(code)
    if render_picture is True:
        picturize_tree(ast, picture_path=picture_path)
    print_tree(ast)
    return ast


def tree_generate_test(path="../auto_grammar_inspect_tests/test1.c"):
    with open(path, "r", encoding=get_encoding(path)) as f:
        lines = f.readlines()

    parser_file(lines, render_picture=True)


def alg_test():
    filenames = os.listdir("../Tests")
    for filename in filenames[0:-1]:
        path = "../Tests/" + filename
        # 去除预处理器指令，只保留实际的C代码
        with open(path, "r", encoding=get_encoding(path)) as f:
            lines = f.readlines()
        parser_file(lines)


if __name__ == '__main__':
    # tree_generate_test(path="../Tests/test1.txt")
    alg_test()
