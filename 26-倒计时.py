import tkinter as tk

class CountdownTimer:
    def __init__(self, root, total_seconds=10):
        self.root = root
        self.root.title("倒计时")
        self.root.geometry("300x200")
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")

        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.running = False

        # 创建时间显示标签
        self.time_label = tk.Label(root,
                                  text=self.format_time(self.remaining_seconds),
                                  font=(self.font_family[0], 48),
                                  fg="black")
        self.time_label.pack(expand=True)

        # 创建总时间显示标签
        self.total_time_label = tk.Label(root,
                                        text=f"总时间: {self.format_time(self.total_seconds)}",
                                        font=(self.font_family[0], 24),
                                        fg="gray")
        self.total_time_label.pack(pady=20)

        # 绑定ESC键退出程序
        self.root.bind("<Escape>", self.exit_program)

        # 开始倒计时
        self.start_countdown()

    def format_time(self, seconds):
        """将秒数格式化为时:分:秒"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def update_timer(self):
        """更新倒计时显示"""
        if self.remaining_seconds > 0 and self.running:
            self.time_label.config(text=self.format_time(self.remaining_seconds))
            self.remaining_seconds -= 1
            self.root.after(1000, self.update_timer)
        elif self.remaining_seconds == 0 and self.running:
            self.time_up()

    def start_countdown(self):
        """开始倒计时"""
        self.running = True
        self.update_timer()

    def time_up(self):
        """时间到了的处理"""
        self.running = False

        # 清除现有窗口内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 进入全屏模式
        self.root.attributes("-fullscreen", True)

        # 创建铺满整个窗口的"时间到了"标签
        time_up_label = tk.Label(self.root,
                                text="时间到了",
                                font=(self.font_family[0], 100, "bold"),
                                fg="red",
                                bg="white")
        time_up_label.pack(expand=True, fill=tk.BOTH)

        # 显示提示信息，告诉用户按ESC退出程序
        hint_label = tk.Label(self.root,
                            text="按ESC键退出程序",
                            font=(self.font_family[0], 12),
                            fg="gray",
                            bg="white")
        hint_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def exit_program(self, event=None):
        """退出整个程序"""
        self.root.destroy()

if __name__ == "__main__":
    # 可以修改这里的秒数来设置不同的倒计时时间
    countdown_seconds = 3  # 倒计时时间（秒）

    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds)
    root.mainloop()
