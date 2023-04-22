import tkinter as tk

from tools import automata
from tkinter import *
from PIL import ImageTk, Image


class AutomataWindow:
    def __init__(self, window, picture_path=r"../pictures/img.png", path="../pictures/"):
        """

        :param window: tk
        :param picture_path: 默认显示图片路径
        :param path: 默认生成图片保存文件夹路径
        """
        self.dfa = None
        self.minimal_dfa = None
        self.nfa = None
        self.regex = ""
        self.path = path

        self.window = window
        self.entry = tk.Entry(self.window)
        self.reg_nfa_button = tk.Button(self.window, command=self.reg_nfa, text="REG->NFA")
        self.nfa_dfa_button = tk.Button(self.window, command=self.nfa_dfa, text="NFA->DFA")
        self.minimize_dfa = tk.Button(self.window, command=self.minimize_dfa, text="minimize DFA")
        self.w_box = 640
        self.h_box = 420

        self.pil_image = Image.open(picture_path)  # 以一个PIL图像对象打开  【调整待转图片格式】
        self.pil_image_resized = self.resize(self.w_box, self.h_box, self.pil_image)

        self.photo = ImageTk.PhotoImage(self.pil_image_resized)
        print(self.photo, picture_path)
        self.picture_label = Label(self.window, image=self.photo)

        self.entry.place(relx=0.1, rely=0.1, relheight=0.07, relwidth=0.8)
        self.reg_nfa_button.place(relx=0.3, rely=0.2)
        self.nfa_dfa_button.place(relx=0.5, rely=0.2)
        self.minimize_dfa.place(relx=0.7, rely=0.2)

        self.picture_label.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.7)

        self.window.mainloop()

    @staticmethod
    def resize(w_box, h_box, pil_image):  # 参数是：要适应的窗口宽、高、Image.open后的图片
        w, h = pil_image.size  # 获取图像的原始大小
        if w > w_box or h > h_box:
            f1 = 1.0 * w_box / w
            f2 = 1.0 * h_box / h
            factor = min([f1, f2])
            width = int(w * factor)
            height = int(h * factor)
            return pil_image.resize((width, height), Image.ANTIALIAS)
        else:
            return pil_image

    def transform(self):
        self.regex = self.entry.get()
        print("reg: ", self.regex)
        self.nfa = automata.Regex2NFA(self.regex, self.path)
        self.dfa = automata.NFA2DFA(self.nfa, self.path)
        self.minimal_dfa = automata.DFA2MDFA(self.dfa, self.path)

    def reg_nfa(self):
        self.transform()
        self.pil_image = Image.open(self.path + 'nfa.png')  # 以一个PIL图像对象打开  【调整待转图片格式】
        self.pil_image_resized = self.resize(self.w_box, self.h_box,
                                             self.pil_image)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】

        self.photo = ImageTk.PhotoImage(self.pil_image_resized)
        self.picture_label.configure(image=self.photo)
        self.picture_label.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.7)

    def nfa_dfa(self):
        self.transform()
        self.pil_image = Image.open(self.path + 'dfa.png')  # 以一个PIL图像对象打开  【调整待转图片格式】
        self.pil_image_resized = self.resize(self.w_box, self.h_box,
                                             self.pil_image)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】
        self.photo = ImageTk.PhotoImage(self.pil_image_resized)

        self.picture_label.configure(image=self.photo)
        self.picture_label.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.7)

    def minimize_dfa(self):
        self.transform()
        self.pil_image = Image.open(self.path + 'mdfa.png')  # 以一个PIL图像对象打开  【调整待转图片格式】
        self.pil_image_resized = self.resize(self.w_box, self.h_box,
                                             self.pil_image)  # 缩放图像让它保持比例，同时限制在一个矩形框范围内  【调用函数，返回整改后的图片】
        self.photo = ImageTk.PhotoImage(self.pil_image_resized)

        self.picture_label.configure(image=self.photo)
        self.picture_label.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.7)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x600')

    AutomataWindow(root)
