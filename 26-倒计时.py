import ctypes
import platform
import tkinter as tk
from ctypes import wintypes  # 用于Windows系统获取任务栏高度


class CountdownTimer:
    def __init__(self, root, total_seconds=10):
        self.root = root
        # 移除窗口标题栏和控制按钮
        self.root.overrideredirect(True)
        # 设置初始窗口大小
        self.root.geometry("300x200")

        # 设置窗口透明度为50%
        self.root.attributes("-alpha", 0.5)

        # 设置窗口不在任务栏显示（跨平台处理）
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", True)  # Windows系统不显示在任务栏
        elif platform.system() == "Darwin":  # macOS
            self.root.attributes("-type", "utility")
        else:  # Linux等其他系统
            self.root.attributes("-type", "toolbar")

        # 设置中文字体支持
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")

        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.running = False

        # 创建时间显示标签
        self.time_label = tk.Label(
            root,
            text=self.format_time(self.remaining_seconds),
            font=(self.font_family[0], 48),
            fg="black",
        )
        self.time_label.pack(expand=True)

        # 创建总时间显示标签
        self.total_time_label = tk.Label(
            root,
            text=f"总时间: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 24),
            fg="gray",
        )
        self.total_time_label.pack(pady=20)

        # 绑定ESC键退出程序
        self.root.bind("<Escape>", self.exit_program)

        # 允许拖动窗口（因为没有标题栏了）
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)

        # 将窗口放置在左下角（避开任务栏）
        self.position_window()

        # 开始倒计时
        self.start_countdown()

    def get_taskbar_height(self):
        """获取系统任务栏高度，处理不同操作系统"""
        if platform.system() == "Windows":
            try:
                # 正确获取Windows任务栏高度的方法
                user32 = ctypes.WinDLL("user32", use_last_error=True)

                # 定义RECT结构
                class RECT(ctypes.Structure):
                    _fields_ = [
                        ("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long),
                    ]

                # 查找任务栏窗口
                h_taskbar = user32.FindWindowW("Shell_TrayWnd", None)
                if not h_taskbar:
                    return 40  # 找不到任务栏时使用默认值

                # 获取任务栏位置和大小
                rect = RECT()
                user32.GetWindowRect(h_taskbar, ctypes.byref(rect))

                # 计算任务栏高度
                return rect.bottom - rect.top
            except:
                # 发生错误时使用默认高度
                return 40
        elif platform.system() == "Darwin":  # macOS
            # macOS Dock栏高度，通常约为50-60像素
            return 60
        else:  # Linux等其他系统
            # 通常任务栏高度约为40-50像素
            return 50

    def position_window(self):
        """将窗口放置在屏幕左下角（避开任务栏）"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 获取窗口尺寸
        window_width = 300
        window_height = 200

        # 获取任务栏高度
        taskbar_height = self.get_taskbar_height()

        # 计算左下角位置（留出10像素边距 + 任务栏高度）
        x = 10  # 左边距10像素
        # 底部位置 = 屏幕高度 - 窗口高度 - 边距 - 任务栏高度
        y = screen_height - window_height - 10 - taskbar_height

        # 确保y坐标不会为负数
        if y < 10:
            y = 10

        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

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

        # 禁用透明效果，让提示更醒目
        self.root.attributes("-alpha", 1.0)

        # 关闭任务栏隐藏属性，确保全屏正常显示
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", False)

        # 关键修复：先禁用overrideredirect，再设置全屏，确保全屏生效
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", True)
        # 重新绑定ESC键
        self.root.bind("<Escape>", self.exit_program)

        # 创建铺满整个窗口的"时间到了"标签
        time_up_label = tk.Label(
            self.root,
            text="时间到了",
            font=(self.font_family[0], 100, "bold"),
            fg="red",
            bg="white",
        )
        time_up_label.pack(expand=True, fill=tk.BOTH)

        # 显示提示信息，告诉用户按ESC退出程序
        hint_label = tk.Label(
            self.root,
            text="按ESC键退出程序",
            font=(self.font_family[0], 12),
            fg="gray",
            bg="white",
        )
        hint_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def exit_program(self, event=None):
        """退出整个程序"""
        self.root.destroy()

    # 以下两个方法用于实现窗口拖动功能
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    # 可以修改这里的秒数来设置不同的倒计时时间
    countdown_seconds = 8  # 倒计时时间（秒）

    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds)
    root.mainloop()
