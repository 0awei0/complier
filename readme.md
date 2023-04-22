本项目实现了一个支持C语言部分语法的编译器，安装好依赖后，直接运行`main.py`文件，菜单如下

![image-20230422192734662](readme.assets/image-20230422192734662.png)

请先打开一个文件，打开文件后可进行词法分析，语法分析，中间代码生成，运行代码等操作。

使用graphviz前添加如下代码
os.environ["path"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

