import ctypes
import os
import platform
import time
import tkinter as tk
from datetime import datetime

import psutil  # 用于进程管理和窗口所属进程检测
import pyautogui  # 用于模拟鼠标键盘操作
import pygetwindow as gw  # 用于窗口管理和激活
import pyperclip  # 用于操作系统剪贴板


class CountdownTimer:
    def __init__(self, root, total_seconds=10):
        """初始化倒计时器

        Args:
            root: Tkinter主窗口实例
            total_seconds: 倒计时总时长（秒），默认10秒
        """
        self.root = root
        self.start_datetime = datetime.now()  # 记录倒计时开始时间
        self.total_seconds = total_seconds    # 记录总倒计时时长

        # 窗口基础设置 - 无边框、固定尺寸、半透明且置顶
        self.root.overrideredirect(True)       # 移除窗口标题栏和边框
        self.root.geometry("148x68")           # 设置窗口尺寸为148x68像素
        self.root.attributes("-alpha", 0.2)    # 窗口透明度20%
        self.root.attributes("-topmost", True) # 窗口始终置顶

        # 透明背景与任务栏显示设置
        self.bg_color = self.get_transparent_color()  # 获取系统支持的透明色
        self.root.configure(bg=self.bg_color)
        # 根据操作系统设置窗口在任务栏的显示方式
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", True)  # Windows系统：工具窗口样式（不显示在任务栏）
        elif platform.system() == "Darwin":  # macOS系统
            self.root.attributes("-type", "utility")
        else:  # Linux系统
            self.root.attributes("-type", "toolbar")

        # 字体与计时相关变量
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")  # 中文字体支持
        self.remaining_seconds = total_seconds  # 剩余秒数
        self.running = False                     # 倒计时运行状态标记
        self.allow_exit = False                  # 控制是否允许退出的标志
        self.overtime_seconds = 0                # 超时秒数记录

        # 创建倒计时显示标签
        self.time_label = tk.Label(
            root,
            text=self.format_time(self.remaining_seconds),  # 格式化显示时间
            font=(self.font_family[0], 24),                 # 字体大小24
            fg="green",                                     # 文字颜色绿色
            bg=self.bg_color,                               # 背景色与窗口一致
        )
        self.time_label.pack(expand=True)  # 居中显示

        # 创建总时间显示标签
        self.total_time_label = tk.Label(
            root,
            text=f"Total time: {self.format_time(self.total_seconds)}",  # 显示总时长
            font=(self.font_family[0], 12),                              # 字体大小12
            fg="gray",                                                   # 文字颜色灰色
            bg=self.bg_color,
        )
        self.total_time_label.pack(pady=2)  # 底部留出2像素间距

        # 绑定ESC键退出程序（仅在倒计时阶段有效）
        self.root.bind("<Escape>", self.exit_program)
        self.position_window()             # 定位窗口到左上角
        self.set_mouse_transparent()       # 设置鼠标穿透效果
        self.start_countdown()             # 开始倒计时

    def get_transparent_color(self):
        """获取系统支持的透明色方案

        尝试设置白色或黑色为透明色，若都失败则返回白色
        """
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
        """将窗口固定在屏幕左上角（无边缘间距）"""
        self.root.geometry("148x68+0+0")  # 尺寸148x68，位置(0,0)

    def set_mouse_transparent(self):
        """设置窗口鼠标穿透效果（鼠标可穿过窗口操作下方内容）

        不同操作系统实现方式不同：
        - Windows：通过修改窗口样式实现
        - macOS：通过设置窗口属性实现
        - Linux：通过设置窗口类型实现
        """
        if platform.system() == "Windows":
            # 获取窗口句柄并修改样式
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            # WS_EX_LAYERED(0x80000) | WS_EX_TRANSPARENT(0x20) 实现分层透明和鼠标穿透
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        elif platform.system() == "Darwin":
            self.root.attributes("-level", "floating")       # 浮动窗口级别
            self.root.attributes("-ignorezoom", True)        # 忽略缩放
            self.root.attributes("-ignoremouseevents", True)  # 忽略鼠标事件
        else:
            self.root.attributes("-type", "dock")            # 停靠栏类型
            self.root.attributes("-acceptfocus", False)      # 不接受焦点

    def format_time(self, seconds):
        """将秒数格式化为易读的时间字符串

        格式为：
        - 若小时数>0：时:分:秒（例如 01:23:45）
        - 否则：分:秒（例如 23:45）

        Args:
            seconds: 要格式化的秒数

        Returns:
            格式化后的时间字符串
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return (
            f"{hours:02d}:{minutes:02d}:{secs:02d}"
            if hours > 0
            else f"{minutes:02d}:{secs:02d}"
        )

    def update_timer(self):
        """每秒更新倒计时显示

        若倒计时未结束，更新显示并继续计时；
        若倒计时结束，触发时间到处理逻辑
        """
        if self.remaining_seconds > 0 and self.running:
            self.time_label.config(text=self.format_time(self.remaining_seconds))
            self.remaining_seconds -= 1
            self.root.after(1000, self.update_timer)  # 1秒后再次调用
        elif self.remaining_seconds == 0 and self.running:
            self.time_up()  # 时间到处理

    def update_overtime(self):
        """每秒更新超时时间显示"""
        self.overtime_seconds += 1
        self.overtime_label.config(
            text=f"Overtime: {self.format_time(self.overtime_seconds)}"
        )
        self.root.after(1000, self.update_overtime)  # 1秒后再次调用

    def start_countdown(self):
        """启动倒计时"""
        self.running = True
        self.update_timer()  # 开始更新计时

    def enable_exit(self):
        """2秒后允许退出程序"""
        self.allow_exit = True
        self.hint_label.config(text="Press any key or click to exit")  # 更新提示信息

    def time_up(self):
        """倒计时结束处理逻辑

        1. 停止倒计时
        2. 清除原有窗口内容
        3. 恢复窗口交互能力（取消鼠标穿透）
        4. 切换到全屏提示模式
        5. 记录信息到微信收藏
        6. 显示超时信息和退出提示
        """
        self.running = False  # 停止倒计时

        # 清除现有窗口内容
        for widget in self.root.winfo_children():
            widget.destroy()

        # 恢复窗口正常交互（取消鼠标穿透）
        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style & ~0x20)  # 移除穿透标志
        elif platform.system() == "Darwin":
            self.root.attributes("-ignoremouseevents", False)  # 允许鼠标事件

        # 全屏设置 - 半透明且强制置顶
        self.root.attributes("-alpha", 0.15)         # 透明度15%
        self.root.overrideredirect(False)           # 恢复窗口边框
        self.root.attributes("-fullscreen", True)   # 全屏显示
        self.root.attributes("-topmost", True)      # 保持置顶

        # 记录信息到微信收藏
        self.record_to_wechat()

        # 全屏界面布局
        self.allow_exit = False                     # 初始不允许退出
        self.overtime_seconds = 0                   # 超时时间清零
        start_time_str = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")  # 格式化开始时间

        # 创建主容器，用于布局所有元素
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

        # "Time's up"主标签（醒目提示）
        tk.Label(
            main_frame,
            text="Time's up",
            font=(self.font_family[0], 100, "bold"),  # 大号粗体
            fg="red",                                 # 红色文字
            bg="white",
        ).grid(row=0, column=0, pady=(0, 40))

        # 超时时间显示标签
        self.overtime_label = tk.Label(
            main_frame,
            text=f"Overtime: {self.format_time(0)}",
            font=(self.font_family[0], 36, "bold"),  # 中号粗体
            fg="orange",                             # 橙色文字
            bg="white",
        )
        self.overtime_label.grid(row=1, column=0, pady=20)

        # 开始时间显示
        tk.Label(
            main_frame,
            text=f"Start time: {start_time_str}",
            font=(self.font_family[0], 24),  # 常规大小
            fg="blue",                       # 蓝色文字
            bg="white",
        ).grid(row=2, column=0, pady=10)

        # 倒计时时长显示
        tk.Label(
            main_frame,
            text=f"Duration: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 24),  # 常规大小
            fg="purple",                     # 紫色文字
            bg="white",
        ).grid(row=3, column=0, pady=10)

        # 退出提示标签
        self.hint_label = tk.Label(
            main_frame,
            text="Exit allowed in 2 seconds...",  # 初始提示
            font=(self.font_family[0], 12),       # 小号字体
            fg="orange",                          # 橙色文字
            bg="white",
        )
        self.hint_label.grid(row=4, column=0, pady=(40, 0))

        # 开始更新超时时间
        self.update_overtime()
        # 2秒后允许退出
        self.root.after(2000, self.enable_exit)
        # 绑定任意键和鼠标点击事件用于退出
        self.root.bind("<Key>", self.delayed_exit)
        self.root.bind("<Button>", self.delayed_exit)

    def record_to_wechat(self):
        """自动将倒计时记录保存到微信收藏

        流程：
        1. 准备记录内容并复制到剪贴板
        2. 激活微信窗口（若未找到则尝试启动）
        3. 使用快捷键Ctrl+Alt+D打开微信收藏新建笔记
        4. 等待收藏窗口激活
        5. 粘贴内容并保存

        容错机制：即使窗口检测失败，仍尝试执行粘贴操作
        """
        # 1. 准备内容并复制到剪贴板
        start_time = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")  # 格式化开始时间
        duration = self.format_time(self.total_seconds)                  # 格式化总时长
        content = f"倒计时记录\n开始时间: {start_time}\n时长: {duration}"  # 拼接记录内容
        pyperclip.copy(content)  # 将内容复制到系统剪贴板

        try:
            # 2. 激活微信窗口（标题为"Weixin"）
            wechat_windows = gw.getWindowsWithTitle("Weixin")  # 查找标题包含"Weixin"的窗口
            if not wechat_windows:
                print("未找到微信窗口，尝试启动微信...")
                # 微信默认安装路径（可根据实际情况修改）
                wechat_path = r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
                if os.path.exists(wechat_path):
                    # 启动微信
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "open", wechat_path, None, None, 1
                    )
                    time.sleep(8)  # 等待微信启动（包含登录时间）
                    wechat_windows = gw.getWindowsWithTitle("Weixin")
                else:
                    raise Exception("未找到微信安装路径")

            # 获取微信窗口并激活
            wechat_window = wechat_windows[0]
            # 强制将微信窗口置于最前（先最小化再恢复，解决单纯activate()可能失效的问题）
            wechat_window.minimize()
            wechat_window.restore()
            time.sleep(2)  # 等待窗口激活

            # 3. 按Ctrl-Alt-D打开新建收藏笔记（微信快捷键）
            pyautogui.hotkey("ctrl", "alt", "d")
            time.sleep(1.5)  # 延长等待时间，确保快捷键生效

            # 4. 等待微信收藏窗口激活
            timeout = 3       # 超时时间（秒）
            interval = 0.5    # 检查间隔（秒）
            activated = False # 激活状态标记
            # 微信收藏窗口可能的标题关键词（根据实际版本调整）
            target_title_keywords = ["Note", "笔记"]

            # 循环检查窗口激活状态
            for _ in range(int(timeout / interval)):
                # 处理getActiveWindow()可能返回None的情况
                active_window = gw.getActiveWindow()
                if active_window is None:
                    time.sleep(interval)
                    continue

                # 检查活动窗口标题是否包含目标关键词
                active_title = active_window.title
                print("当前活动窗口标题:", active_title)  # 调试信息
                if any(keyword in active_title for keyword in target_title_keywords):
                    # 进一步确认窗口所属进程为微信收藏进程（WeChatAppEx.exe）
                    try:
                        # 通过窗口句柄获取进程ID
                        hwnd = active_window._hWnd
                        pid = ctypes.c_ulong()
                        ctypes.windll.user32.GetWindowThreadProcessId(
                            hwnd, ctypes.byref(pid)
                        )
                        process = psutil.Process(pid.value)
                        # 确认进程名称为微信收藏进程
                        if process.name() == "WeChatAppEx.exe":
                            activated = True
                            break
                    except Exception as e:
                        print("进程检测异常:", e)  # 打印异常信息
                        pass  # 进程检测失败时，仍以标题匹配为准

                time.sleep(interval)

            if not activated:
                # 未检测到窗口激活时的容错处理
                print("未明确检测到窗口激活，尝试直接粘贴...")
                activated = True  # 强制继续，尝试执行操作

            # 5. 粘贴内容并保存（无论是否检测到激活，都尝试操作）
            pyautogui.hotkey("ctrl", "v")  # 粘贴剪贴板内容
            time.sleep(0.5)
            # pyautogui.hotkey("ctrl", "s")  # 保存笔记（根据实际情况决定是否启用）
            pyautogui.press("esc")  # 退出编辑界面
            print("操作完成（已尝试粘贴并保存）")

        except Exception as e:
            # 捕获所有异常并提示手动记录
            print(f"自动记录失败: {str(e)}")
            print("\n请手动记录以下信息到微信收藏：")
            print(f"开始时间: {start_time}")
            print(f"时长: {duration}")

    def delayed_exit(self, event=None):
        """延迟退出处理

        只有在允许退出（allow_exit为True）时才执行退出操作
        """
        if self.allow_exit:
            self.exit_program()

    def exit_program(self, event=None):
        """退出整个程序"""
        self.root.destroy()


if __name__ == "__main__":
    # 安装依赖：pip install pyautogui pygetwindow pyperclip psutil
    countdown_seconds = 1  # 倒计时时长（秒），测试时可设为1秒快速验证
    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds)
    root.mainloop()
