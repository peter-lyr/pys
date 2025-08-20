import time
L = 60*8
for i in range(L):
    time.sleep(1)
    print(f'\r{i}s/{L} {i/60:.3f}m/{int(L/60)}', end='')

import tkinter as tk
# from tkinter import messagebox
window = tk.Tk()
window.title('主窗口标题')
window.geometry('3840x1080')
# def display_messagebox():
#     messagebox.showinfo('弹窗标题', '这是弹窗显示的信息\n这是弹窗显示的信息\n')
# tk.Button(window, text='显示弹窗', command=display_messagebox).pack()
window.mainloop()
