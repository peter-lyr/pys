import ctypes
import platform
import tkinter as tk


class CountdownTimer:
    def __init__(self, root, total_seconds=10):
        self.root = root
        # 移除窗口标题栏和控制按钮
        self.root.overrideredirect(True)
        # 设置窗口尺寸为148x68
        self.root.geometry("148x68")

        # 设置倒计时阶段窗口透明度为20%
        self.root.attributes("-alpha", 0.2)

        # 设置窗口置顶
        self.root.attributes("-topmost", True)

        # 设置透明背景方案
        self.bg_color = self.get_transparent_color()
        self.root.configure(bg=self.bg_color)

        # 设置窗口不在任务栏显示
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", True)
        elif platform.system() == "Darwin":  # macOS
            self.root.attributes("-type", "utility")
        else:  # Linux
            self.root.attributes("-type", "toolbar")

        # 设置中文字体支持
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")

        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.running = False
        self.allow_exit = False  # 控制是否允许退出的标志

        # 创建时间显示标签
        self.time_label = tk.Label(
            root,
            text=self.format_time(self.remaining_seconds),
            font=(self.font_family[0], 24),
            fg="green",
            bg=self.bg_color,
        )
        self.time_label.pack(expand=True)

        # 创建总时间显示标签
        self.total_time_label = tk.Label(
            root,
            text=f"Total time: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 12),
            fg="gray",
            bg=self.bg_color,
        )
        self.total_time_label.pack(pady=2)

        # 绑定ESC键退出程序（倒计时阶段）
        self.root.bind("<Escape>", self.exit_program)

        # 将窗口放置在左上角（无边缘间距）
        self.position_window()

        # 设置鼠标穿透效果
        self.set_mouse_transparent()

        # 开始倒计时
        self.start_countdown()

    def get_transparent_color(self):
        """获取系统支持的透明色或替代方案"""
        try:
            self.root.attributes("-transparentcolor", "white")
            return "white"
        except:
            try:
                self.root.attributes("-transparentcolor", "#000000")
                return "#000000"
            except:
                return "white"

    def position_window(self):
        """将窗口放置在屏幕左上角（无边缘间距）"""
        window_width = 148
        window_height = 68
        self.root.geometry(f"{window_width}x{window_height}+0+0")

    def set_mouse_transparent(self):
        """设置窗口鼠标穿透效果"""
        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        elif platform.system() == "Darwin":
            self.root.attributes("-level", "floating")
            self.root.attributes("-ignorezoom", True)
            self.root.attributes("-ignoremouseevents", True)
        else:
            self.root.attributes("-type", "dock")
            self.root.attributes("-acceptfocus", False)

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

    def enable_exit(self):
        """2秒后允许退出"""
        self.allow_exit = True
        # 隐藏倒计时提示，显示退出提示
        self.countdown_label.destroy()
        self.hint_label.config(text="Press any key or click to exit")

    def time_up(self):
        """时间到了的处理 - 全屏置顶，前2秒不可退出"""
        self.running = False

        # 清除现有窗口内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 恢复窗口正常交互（取消鼠标穿透）
        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style & ~0x20)
        elif platform.system() == "Darwin":
            self.root.attributes("-ignoremouseevents", False)

        # 设置全屏窗口透明度为15%
        self.root.attributes("-alpha", 0.15)

        # 进入全屏模式并强制置顶
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)  # 保持置顶

        # 初始化退出权限为False
        self.allow_exit = False

        # 创建铺满整个窗口的"Time's up"标签
        time_up_label = tk.Label(
            self.root,
            text="Time's up",
            font=(self.font_family[0], 100, "bold"),
            fg="red",
            bg="white",
        )
        time_up_label.pack(expand=True, fill=tk.BOTH)

        # 显示倒计时提示（2秒后可退出）
        self.countdown_label = tk.Label(
            self.root,
            text="Exit allowed in 2 seconds...",
            font=(self.font_family[0], 12),
            fg="orange",
            bg="white",
        )
        self.countdown_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # 2秒后允许退出
        self.root.after(2000, self.enable_exit)

        # 创建退出提示标签（初始隐藏，由enable_exit显示）
        self.hint_label = tk.Label(
            self.root,
            text="",
            font=(self.font_family[0], 12),
            fg="gray",
            bg="white",
        )
        self.hint_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # 绑定任意键和鼠标点击事件
        self.root.bind("<Key>", self.delayed_exit)
        self.root.bind("<Button>", self.delayed_exit)

    def delayed_exit(self, event=None):
        """延迟退出处理 - 只有在允许退出后才生效"""
        if self.allow_exit:
            self.exit_program()

    def exit_program(self, event=None):
        """退出整个程序"""
        self.root.destroy()


if __name__ == "__main__":
    countdown_seconds = 3  # 倒计时时间（秒）
    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds)
    root.mainloop()
