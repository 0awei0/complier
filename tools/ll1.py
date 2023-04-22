import copy
import graphviz
import os

from tools.word_analyser import Lexer

os.environ["path"] += os.pathsep + r"C:\Program Files\Graphviz\bin"


class NODE:
    """
        语法树节点定义
    """
    def __init__(self, element):
        self.ele = element
        self.children = []


class ASTTree:
    """
        语法树定义
    """
    def __init__(self):
        self.root = NODE('#')
        self.p = self.root
        self.stack = [self.root]

    def add_node(self, element):
        node = NODE(element)
        self.p.children.append(node)
        self.stack.append(node)

    def pop_node(self):
        self.p = self.stack.pop()


class LL1:
    def __init__(self, line=None, render_tree=False, grammar_path="grammar.txt", picture_path='../pictures/ast_tree'):
        """

        :param line: 词法分析的结果，token列表
        :param render_tree: 是否生成语法树图片
        :param grammar_path:  文法路径
        """
        self.processed_right = None
        self.follow = None
        self.table = None
        self.welldone = None
        self.first_from = None
        self.first = None
        self.processed_left = None
        self.processed = None
        self.ast = None
        self.picture_path = picture_path

        fp = open(grammar_path, 'r', encoding='utf-8')
        self.data = fp.read()
        self.symbols = set()
        self.not_end = set()
        self.end = set()
        self.start = ''
        self.n = 1
        self.process_data()
        self.get_first()
        self.get_follow()
        self.create_table()
        self.analyse(line)
        if self.welldone == 1 and render_tree is True:
            self.print_ast_tree()

    def process_data(self):
        self.processed = []
        self.processed_left = []
        self.processed_right = []

        # 将输入的文本data按照换行符分割成一个字符串列表，并去掉空行以及以#开头的注释行。
        self.data = self.data.split('\n')
        temp = [i for i in self.data if len(i) > 0]
        temp_2 = [i for i in temp if i[0] != '#']
        self.data = temp_2
        del temp
        del temp_2

        self.start = self.data[0].split('->')[0]  # 获得文法的开始符号
        # 使用箭头符号->来分割产生式的左右部分，并将左部加入not_end集合，并将左,右部加入symbols集合（后者用于记录文法的所有符号）。
        for i in self.data:
            key, value = i.split('->')  # key: value:
            self.not_end.add(key)
            self.symbols.add(key)

            # 如果右部包含竖杠符号 | ，则将它拆成多个产生式，并逐个加入到data数组中。
            if '|' in value:
                value = value.split('|')
                for j in value:
                    self.data.append(key + '->' + j)
                continue

            # 否则，代码将右部按空格分割，并将符号都加入到symbols集合中。
            value = value.split()
            for j in value:
                self.symbols.add(j)

            temp = [key, value]
            self.processed.append(temp)
            self.processed_left.append(key)
            self.processed_right.append(value)

        # 函数遍历symbols集合，并将不在not_end集合中的符号加入到end集合中，以记录所有的终结符。
        for i in self.symbols:
            if i not in self.not_end:
                self.end.add(i)

    # 计算文法的FIRST集合。
    def get_first(self):
        # 首先，代码初始化了两个变量left和 right，这两个变量是处理后的产生式的左部和右部。
        left = self.processed_left
        right = self.processed_right

        # 初始化一个空字典 self.first和一个空字典列表self.first_from，并为每一个非终结符号构建了一个空的集合。
        self.first = dict()
        self.first_from = dict()
        for i in self.not_end:
            self.first[i] = set()
            self.first_from[i] = dict()

        # 然后，代码遍历所有产生式，对于右部的首个符号是终结符号的产生式，将这个终结符号加入到左部对应的FIRST集合中。
        for i in range(len(right)):
            if right[i][0] in self.end:
                self.first_from[left[i]][right[i][0]] = right[i]
                self.first[left[i]].add(right[i][0])

        for dist in self.not_end:
            left_temp = [dist]
            left_temp_minus = []
            road = dict()
            change_flag = 1
            # 进入一个 while 循环，循环中使用左部的非终结符号 dist 初始化一个列表 left_temp，和一个空列表 left_temp_minus。
            # left_temp 中存储了可以直接推导出 dist 的符号，left_temp_minus 中存储了已经使用过的可空的符号。
            while change_flag == 1:
                temp_first = copy.deepcopy(self.first)
                change_flag = 0

                # 遍历所有的产生式
                for i in range(len(right)):
                    temp = right[i][0]

                    # 对于左部在left_temp或left_temp_minus的产生式，进行以下操作：
                    # 1.如果右部的首个符号是终结符号，则将它加入到self.first集合和self.first_from字典中；
                    # 2.如果右部的首个符号是非终结符号，则在left_temp中添加这个非终结符号，如果这个非终结符号可以推导出空串，
                    #   则将它加入到left_temp_minus中，并记录变量road来记录这个产生式的来源；
                    # 3.如果右部的所有符号都可以推导出空串，则将空串加入到 self.first集合和self.first_from字典中。
                    # 4.如果有符号被加入到self.first集合或self.first_from字典中，则将change_flag置为1，
                    #   继续执行while 循环。循环结束后，self.first 字典即为所求的 FIRST 集合。
                    if left[i] in left_temp or left[i] in left_temp_minus:

                        # 如果右部的首个符号是终结符号，则将它加入到self.first集合和self.first_from字典中；
                        if temp in self.end:
                            if left[i] in left_temp_minus:
                                if temp == 'e':
                                    continue
                            if left[i] == dist:
                                self.first_from[dist][temp] = right[i]
                            else:
                                self.first_from[dist][temp] = road[left[i]]
                            self.first[dist].add(temp)

                        # 如果右部的首个符号是非终结符号，则在left_temp中添加这个非终结符号
                        elif temp not in self.end:
                            flag = 0
                            for j in right[i]:
                                if j in self.end:
                                    if left[i] == dist:
                                        self.first_from[dist][j] = right[i]
                                    else:
                                        self.first_from[dist][j] = road[left[i]]
                                    self.first[dist].add(j)
                                    break
                                elif j in left_temp:
                                    flag = 1
                                    break
                                # 如果这个非终结符号可以推导出空串，则将它加入到left_temp_minus中，并记录变量road来记录这个产生式的来源；
                                elif 'e' in self.first[j]:
                                    flag = 1
                                    # for k in self.first[j]:
                                    #     if k != 'e':
                                    #         if left[i] == dist:
                                    #             self.first_from[dist][k] = right[i]
                                    #         else:
                                    #             self.first_from[dist][k] = road[left[i]]
                                    #         self.first[dist].add(k)
                                    if j not in left_temp_minus:
                                        left_temp_minus.append(j)
                                        if left[i] != dist:
                                            road[j] = road[left[i]]
                                        else:
                                            road[j] = right[i]
                                        change_flag = 1
                                else:
                                    # 如果有符号被加入到self.first集合或self.first_from字典中，则将change_flag置为1，
                                    # 继续执行while 循环。循环结束后，self.first 字典即为所求的 FIRST 集合。
                                    flag = 1
                                    left_temp.append(j)
                                    if left[i] != dist:
                                        road[j] = road[left[i]]
                                    else:
                                        road[j] = right[i]
                                    change_flag = 1
                                    break

                            # 如果右部的所有符号都可以推导出空串，则将空串加入到 self.first集合和self.first_from字典中。
                            if flag == 0:
                                if left[i] == dist:
                                    self.first_from[dist]['e'] = right[i]
                                else:
                                    self.first_from[dist]['e'] = road[left[i]]
                                self.first[dist].add('e')
                if temp_first != self.first:
                    change_flag = 1
        print('FIRST')
        # for i in self.not_end:
        #     print(i, end='->')
        #     for j in self.first[i]:
        #         print(j, end=' ')
        #     print()

    # 求文法的follow集合
    def get_follow(self):
        # 变量left和right分别表示处理后的产生式的左部和右部。接着，代码初始化了一个空字典self.follow和一个空集合，
        # 其中字典中为每一个非终结符号构建了一个空set集合，最开始将起始符号（self.start）的FOLLOW集合加入了一个#号。
        left = self.processed_left
        right = self.processed_right

        self.follow = dict()
        for i in self.not_end:
            self.follow[i] = set()
        self.follow[self.start].add('#')

        # 代码进入一个循环，循环遍历每一个非终结符号。代码使用变量change_flag来记录FOLLOW集合是否有变化，如果有变化则继续执行while循环。
        for dist_2 in self.not_end:
            change_flag = 1
            left_temp = [dist_2]
            # 在while循环中，代码使用变量left_temp来记录可以直接推导出非终结符号dist_2的符号，
            # 并初始化变量temp_follow来存储当前的FOLLOW集合。
            while change_flag == 1:
                change_flag = 0
                temp_follow = copy.deepcopy(self.follow)

                for i in range(len(right)):
                    temp = right[i]
                    # 代码遍历所有的产生式，对于右部包含dist_2的产生式，进行以下操作：
                    for dist in left_temp:
                        # 如果dist_2在产生式右部的末尾，则将产生式左部的FOLLOW集合加入到dist_2的FOLLOW集合中，
                        # 如果左部非终结符号不在left_temp中，则加入到left_temp中，并将change_flag置为1
                        if left[i] != dist and dist in temp:
                            index_dist = temp.index(dist)
                            if index_dist == len(temp) - 1:
                                if left[i] not in left_temp:
                                    left_temp.append(left[i])
                                    change_flag = 1
                            else:
                                add_flag = 1
                                for j in range(index_dist + 1, len(temp)):
                                    # 如果dist_2在产生式右部的中间，则将后续的符号temp[j]的FIRST集合加入到dist_2的FOLLOW集合中
                                    if temp[j] in self.end:
                                        self.follow[dist] |= set(temp[j])
                                        add_flag = 0
                                        break
                                    # 如果这些符号能够推导出空串，则继续往后加，否则停止添加；
                                    elif 'e' in self.first[temp[j]]:
                                        self.follow[dist] |= self.first[temp[j]]
                                        self.follow[dist] -= set('e')
                                        continue
                                    else:
                                        self.follow[dist] |= self.first[temp[j]]
                                        self.follow[dist] -= set('e')
                                        add_flag = 0
                                # 如果已经到达产生式右部的末尾还没有停止添加，则将产生式左部的FOLLOW集合加入到dist_2的FOLLOW集合中。
                                if add_flag == 1:
                                    if left[i] not in left_temp:
                                        left_temp.append(left[i])
                                        change_flag = 1
                if temp_follow != self.follow:
                    change_flag = 1
            # 循环结束后，将 left_temp中的所有符号的FOLLOW集合添加到 dist_2 的FOLLOW集合中。
            # 最终得到的 self.follow字典即为所求的FOLLOW集合。
            for i in left_temp:
                self.follow[dist_2] |= self.follow[i]
        print('FOLLOW')
        # for i in self.not_end:
        #     print(i, end='->')
        #     for j in self.follow[i]:
        #         print(j, end=' ')
        #     print()
        # print()

    # 创建ll1预测分析表
    def create_table(self):
        # 在代码开始，初始化了一个空字典self.table，该字典的key为非终结符号，value为另一个字典，
        # 用于对应该非终结符号下的终结符号和动作。
        self.table = dict()
        for i in self.not_end:
            self.table[i] = dict()
        # 代码使用两个循环分别初始化每个非终结符号下的表格，在第一个循环中，
        # 由于我们只需要在非终结符号下记录END的内容，因此使用j in self.end 来限定循环语句。
        for i in self.not_end:
            for j in self.end:
                if j == 'e':
                    continue
                self.table[i][j] = 'ERROR'
            self.table[i]['#'] = 'ERROR'

        # 在第二个循环中，代码使用self.first[i]来访问所有可能的FIRST集合，并根据其中的终结符号为非终结符号添加对应的操作。
        # 如果 FIRST集合中包含空字符，则继续用循环将FOLLOW集合中对应的终结符号也加入操作中。
        for i in self.not_end:
            for j in self.first[i]:
                if j == 'e':
                    for k in self.follow[i]:
                        self.table[i][k] = ['e']
                    continue
                self.table[i][j] = self.first_from[i][j]

    # 对代码进行分析
    def analyse(self, line):
        self.ast = ASTTree()
        # 分析栈的初始元素为#和文法的起始符号 self.start，表示句子的开始和结束。
        stack = ['#', self.start]
        # 为输入符号串添加结束标记
        line.append(['', '#'])
        # 定义一个变量p表示当前读入到输入符号串的第几个字符，以及一个变量top存储栈顶的字符，将变量record初始化为空字符串，
        # 存储分析过程的记录，cur_char为当前读入的字符。
        p = 0
        top = stack.pop()
        record = ''
        cur_char = line[p][1]

        while top != '#':
            # 判断栈顶元素 top 是否等于 cur_char，若相等，则表示当前字符匹配成功，将其从栈顶元素 stack
            # 中弹出，并更新 cur_char 和 p 的值，同时在语法分析树中添加相应的节点；
            if top in self.end and top == cur_char:
                record += str(stack) + ' ' + cur_char + '匹配成功\n'
                # print(str(stack) + ' ' + cur_char + '匹配成功')
                if cur_char in ['identifier', 'number']:
                    cur_id = line[p][0]
                    self.ast.p.ele = [self.ast.p.ele]
                    self.ast.p.ele.append(cur_id)
                p += 1
                cur_char = line[p][1]

            # 若top是非终结符并且当前字符在其对应的文法分析表中即不在表中为ERROR，则将文法的推导过程进行记录，
            # 并将栈元素弹出，将推导后的符号（若不为空）进行逆序压入栈中，同时在语法分析树中添加相应的节点；
            elif top in self.not_end and cur_char in self.table[top] and self.table[top][cur_char] != 'ERROR':
                record += str(stack) + ' ' + top + '->' + \
                          str(self.table[top][cur_char]) + '\n'
                # print(str(stack) + ' ' + top + '->' +
                #       str(self.table[top][cur_char]))
                temp = self.table[top][cur_char]
                for char in reversed(temp):
                    if char != 'e':
                        self.ast.add_node(char)
                        stack.append(char)
            # 若以上两种情况均不满足，则说明输入的符号串与文法不匹配，直接退出循环。
            else:
                break

            self.ast.pop_node()
            top = stack.pop()

        # 判断栈顶元素 top是否与当前字符 cur_char相等，若相等，则表示语法匹配成功，
        if top == cur_char:
            record += '接受\n'
            print('接受')
            self.welldone = 1
        else:
            record += '匹配失败\n'
            print('匹配失败')
            self.welldone = 0
        # print(record)

    # 用递归的方式输出语法分析树，
    def print_tree(self, f, ast_node, father):
        if len(ast_node.children) == 0:
            return
        else:
            for i in reversed(ast_node.children):
                if isinstance(i.ele, list):
                    f.node(str(self.n), fontname='Microsoft YaHei', label=i.ele[0] + ':' + i.ele[1])
                else:
                    f.node(str(self.n), fontname='Microsoft YaHei', label=i.ele)
                f.edge(str(father), str(self.n))
                self.n += 1
                self.print_tree(f, i, self.n - 1)

    # 函数 `print_ast_tree(self)` 创建一个新的图 `Digraph` 对象 `f`，初始化根节点，
    # 调用 `self.print_tree()` 递归输出语法分析树，并将结果保存为图片文件（默认格式为 png），并在系统默认的图片查看器中打开图片。
    def print_ast_tree(self):
        f = graphviz.Digraph('NFA', format='png', filename=self.picture_path)
        f.node(str(0), fontname='Microsoft YaHei', label='#')
        self.print_tree(f, self.ast.root, 0)
        f.render(view=True)


def alg_test():
    with open("../Tests/test6.txt", encoding="utf-8-sig") as f:
        content = f.readlines()
    lex = Lexer(content)
    result = lex.result

    ll1 = LL1(result, render_tree=True)
    if ll1.welldone == 1:
        print("success")
    else:
        print("failed")


def test_all():
    filenames = os.listdir("../Tests")
    fail = 0

    for filename in filenames:
        with open("../Tests/" + filename, encoding="utf-8-sig") as f:
            content = f.readlines()
        lex = Lexer(content)
        result = lex.result

        ll1 = LL1(result)
        if ll1.welldone == 1:
            print("success")
        else:
            fail += 1
            print("failed", filename)
    print("all fail count: ", fail)


if __name__ == '__main__':
    alg_test()
    # test_all()
