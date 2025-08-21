import ctypes
import os
import platform
import sys
import threading
import time
import tkinter as tk
from datetime import datetime

import pyautogui
import pygetwindow as gw
import pyperclip

# 初始化路径变量
home = os.environ["USERPROFILE"]  # 获取用户主目录
dp = os.path.join(home, "Dp")  # 主工作目录
temp = os.path.join(dp, "temp")  # 临时文件目录
os.makedirs(temp, exist_ok=True)  # 确保临时目录存在
# 进程终止脚本路径（用于程序退出时清理自身进程）
kill_self_py_bat = os.path.join(temp, "26-倒计时-保存到微信收藏笔记.py.bat")
# 监测文件路径（用于外部控制倒计时器，如手动结束）
MONITOR_FILE = os.path.join(temp, "countdown_monitor.txt")


class CountdownTimer:
    """倒计时器类，支持定时提醒、手动控制和微信收藏功能"""

    def __init__(self, root, countdown_seconds=1500, enable_wechat_save=0):
        """
        初始化倒计时器实例

        参数:
            root: Tkinter主窗口对象
            countdown_seconds: 倒计时总秒数，默认25分钟(1500秒)
            enable_wechat_save: 是否启用微信收藏保存功能，1启用，0禁用
        """
        # 基础配置
        self.root = root  # Tkinter主窗口
        self.start_datetime = datetime.now()  # 倒计时开始时间
        self.total_seconds = countdown_seconds  # 总倒计时时长（秒）
        self.enable_wechat_save = enable_wechat_save  # 微信保存开关

        # 状态管理
        self.status = 0  # 状态标记：0-等待手动结束；1-等待退出；≥2-计时器模式
        self.is_fullscreen = False  # 是否处于全屏模式
        self.is_manual_done = False  # 是否手动结束倒计时
        self.running = False  # 倒计时是否正在运行
        self.remaining_seconds = countdown_seconds  # 剩余秒数
        self.timer_mode = False  # 是否处于计时器模式

        # 初始化监测文件（清空内容）
        with open(MONITOR_FILE, "w", encoding="utf-8") as f:
            f.write("")

        # 启动文件监测线程（用于检测外部控制指令）
        self.monitor_thread = threading.Thread(target=self.monitor_file, daemon=True)
        self.monitor_thread.start()

        # 窗口基础配置（无边框、透明度、置顶）
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes("-alpha", 0.2)  # 透明度20%
        self.root.attributes("-topmost", True)  # 窗口置顶

        # 根据系统设置窗口透明背景和类型
        self.bg_color = self.get_transparent_color()
        self.root.configure(bg=self.bg_color)
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", True)  # Windows工具窗口
        elif platform.system() == "Darwin":
            self.root.attributes("-type", "utility")  # macOS工具窗口
        else:
            self.root.attributes("-type", "toolbar")  # 其他系统工具栏窗口

        # 字体配置与计时相关变量
        self.font_family = (
            "SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"
        )  # 支持多系统中文字体
        self.allow_exit = False  # 是否允许退出
        self.overtime_seconds = 0  # 超时秒数（自动结束后）
        self.manual_elapsed_seconds = 0  # 手动结束后经过的秒数
        self.auto_elapsed_seconds = 0  # 自动结束后经过的秒数
        self.current_elapsed_label = None  # 计时器模式的计时标签

        # 创建UI组件
        self._create_widgets()

        # 绑定退出事件（ESC键）
        self.root.bind("<Escape>", self.exit_program)
        # 定位窗口并设置鼠标穿透
        self.position_window()
        self.set_mouse_transparent()
        # 启动倒计时
        self.start_countdown()

    def _create_widgets(self):
        """创建初始界面组件"""
        # 倒计时显示标签（已用时间/剩余时间）
        self.time_label = tk.Label(
            self.root,
            text=self._init_time_text(),
            font=(self.font_family[0], 20),
            fg="green",
            bg=self.bg_color,
        )
        self.time_label.pack(expand=True)

        # 总时长显示标签
        self.total_time_label = tk.Label(
            self.root,
            text=f"Total time: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 14),
            fg="gray",
            bg=self.bg_color,
        )
        self.total_time_label.pack(pady=2)

        # 手动结束提示标签
        self.manual_hint = tk.Label(
            self.root,
            text=f"Write 'manual done' to {MONITOR_FILE} to end early",
            font=(self.font_family[0], 10),
            fg="blue",
            bg=self.bg_color,
        )
        self.manual_hint.pack(pady=2)

    def monitor_file(self):
        """
        监测控制文件内容变化，响应外部指令

        支持的指令:
            "step_forward": 状态0→手动结束；状态1→退出；状态≥2→退出
            "for_timer": 状态0→同step_forward；状态1→进入计时器模式；状态≥2→响应但不退出
        """
        while True:
            try:
                # 若监测文件不存在则退出循环
                if not os.path.exists(MONITOR_FILE):
                    break

                # 读取文件内容并判断指令
                with open(MONITOR_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip().lower()

                # 指令为空则跳过
                if not content:
                    continue

                # 清空文件内容（避免重复触发）
                with open(MONITOR_FILE, "w", encoding="utf-8") as f_clear:
                    f_clear.write("")

                # 处理"step_forward"指令
                if content == "step_forward":
                    if self.status == 0:
                        # 状态0：手动结束倒计时，状态转为1
                        self.is_manual_done = True
                        self.root.after(0, self.manual_end_countdown)
                        self.status = 1
                    else:
                        # 状态≥2：退出程序
                        self.root.after(0, self.exit_program)

                # 处理"for_timer"指令
                elif content == "for_timer":
                    if self.status == 0:
                        # 状态0：同step_forward，手动结束倒计时，状态转为1
                        self.is_manual_done = True
                        self.root.after(0, self.manual_end_countdown)
                        self.status = 1
                    else:
                        self.auto_elapsed_seconds = 0
                        self.manual_elapsed_seconds = 0
                        self.end_time_str = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )  # 格式化结束时间
                        self.root.after(0, self.enter_timer_mode)

            except Exception as e:
                print(f"监测文件出错: {e}")

            time.sleep(1)  # 每秒检查一次

    def enter_timer_mode(self):
        """进入计时器模式：调整UI显示，包含三行内容并铺满屏幕"""
        self.timer_mode = True  # 标记为计时器模式

        # 清除所有现有组件
        for widget in self.root.winfo_children():
            widget.destroy()

        # 计算自适应字体大小
        font_sizes = self.calculate_font_sizes()

        # 创建主框架并设置网格布局
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 设置三行均等权重，确保铺满屏幕
        for i in range(3):
            main_frame.grid_rowconfigure(i, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # 1. 主标题行
        tk.Label(
            main_frame,
            text="Timer",
            font=(self.font_family[0], font_sizes["title"], "bold"),
            fg="purple",
            bg="white",
            anchor="center",
            justify="center"
        ).grid(row=0, column=0, sticky="nsew", pady=10)

        # 2. 计时信息行
        self.current_elapsed_label = tk.Label(
            main_frame,
            text=f"{self.format_time(0)} from {self.end_time_str}",
            font=(self.font_family[0], font_sizes["overtime"], "bold"),
            fg="purple",
            bg="white",
            anchor="center",
            justify="center"
        )
        self.current_elapsed_label.grid(row=1, column=0, sticky="nsew", pady=10)

        # 3. 退出提示行
        tk.Label(
            main_frame,
            text="Press ESC to exit",
            font=(self.font_family[0], font_sizes["hint"], "bold"),
            fg="orange",
            bg="white",
            anchor="center",
            justify="center"
        ).grid(row=2, column=0, sticky="nsew", pady=10)

        # 复制当前超时信息到剪贴板
        self.update_timer_clipboard()

    def update_timer_clipboard(self):
        """更新计时器模式下的剪贴板内容"""
        if self.is_manual_done:
            content = f"timeout {self.format_time(self.manual_elapsed_seconds)} from {self.end_time_str}\n"
        else:
            content = f"timeout {self.format_time(self.auto_elapsed_seconds)} from {self.end_time_str}"
        pyperclip.copy(content)

    def manual_end_countdown(self):
        """手动结束倒计时（设置状态并触发结束处理）"""
        self.running = False  # 停止倒计时
        self.time_up()  # 执行结束逻辑

    def _init_time_text(self):
        """初始化时间显示文本（00:00 / 总时长）"""
        elapsed_time = self.format_time(0)
        remaining_time = self.format_time(self.total_seconds)
        return f"{elapsed_time} / {remaining_time}"

    def get_transparent_color(self):
        """获取系统支持的透明背景色（兼容不同系统）"""
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
        """将窗口定位到屏幕右上角，铺满除任务栏外的区域"""
        if platform.system() == "Windows":
            # Windows系统通过系统API获取屏幕尺寸
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
        else:
            # 其他系统通过Tkinter获取屏幕尺寸
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            taskbar_height = int(screen_height * 0.05)  # 估算任务栏高度（5%）
            screen_height -= taskbar_height  # 减去任务栏高度

        # 设置窗口尺寸和位置（全屏，左上角坐标(0,0)）
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

    def set_mouse_transparent(self):
        """设置鼠标穿透效果（窗口不响应鼠标事件）"""
        if platform.system() == "Windows":
            # Windows通过修改窗口样式实现穿透
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            # 添加WS_EX_LAYERED(0x80000)和WS_EX_TRANSPARENT(0x20)样式
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        elif platform.system() == "Darwin":
            # macOS通过属性设置穿透
            self.root.attributes("-level", "floating")
            self.root.attributes("-ignorezoom", True)
            self.root.attributes("-ignoremouseevents", True)
        else:
            # 其他Linux系统设置
            self.root.attributes("-type", "dock")
            self.root.attributes("-acceptfocus", False)

    def format_time(self, seconds, show_hour=None):
        """
        格式化秒数为时分秒字符串

        参数:
            seconds: 待格式化的秒数
            show_hour: 是否强制显示小时（None则自动判断）
        返回:
            格式化后的字符串（如"01:23:45"或"23:45"）
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        # 若小时数>0或强制显示小时，则显示时分秒，否则显示分秒
        return (
            f"{hours:02d}:{minutes:02d}:{secs:02d}"
            if (hours > 0 or show_hour)
            else f"{minutes:02d}:{secs:02d}"
        )

    def update_timer(self):
        """更新倒计时显示（每秒执行一次）"""
        if self.remaining_seconds > 0 and self.running:
            # 计算已用时间和剩余时间
            elapsed_seconds = self.total_seconds - self.remaining_seconds
            elapsed_time = self.format_time(elapsed_seconds)
            remaining_time = self.format_time(self.remaining_seconds)
            # 更新显示
            self.time_label.config(text=f"{elapsed_time} / {remaining_time}")
            # 减少剩余秒数并预约下次更新
            self.remaining_seconds -= 1
            self.root.after(1000, self.update_timer)
        elif self.remaining_seconds == 0 and self.running:
            # 倒计时结束，执行结束逻辑
            self.time_up()
            self.status = 1

    def update_manual_elapsed(self):
        """更新手动结束后的经过时间（每秒更新）"""
        self.manual_elapsed_seconds += 1
        # 显示内容（根据模式调整标签）
        if self.timer_mode and self.current_elapsed_label:
            # 计时器模式：更新专用标签
            self.current_elapsed_label.config(
                text=f"{self.format_time(self.manual_elapsed_seconds)} from {self.end_time_str}"
            )
        else:
            # 普通模式：更新原有标签
            self.manual_elapsed_label.config(
                text=f"{self.format_time(self.manual_elapsed_seconds)} from {self.end_time_str}"
            )
        self.root.after(1000, self.update_manual_elapsed)

    def update_auto_elapsed(self):
        """更新自动结束后的经过时间（每秒更新）"""
        self.auto_elapsed_seconds += 1
        # 显示内容（根据模式调整标签）
        if self.timer_mode and self.current_elapsed_label:
            # 计时器模式：更新专用标签
            self.current_elapsed_label.config(
                text=f"{self.format_time(self.auto_elapsed_seconds)} from {self.start_time_str}"
            )
        else:
            # 普通模式：更新原有标签
            self.auto_elapsed_label.config(
                text=f"{self.format_time(self.auto_elapsed_seconds)} from {self.start_time_str}"
            )
        self.root.after(1000, self.update_auto_elapsed)

    def start_countdown(self):
        """启动倒计时（设置运行状态并开始更新）"""
        self.running = True
        self.update_timer()

    def enable_exit(self):
        """允许退出程序（在主线程中更新UI）"""
        self.root.after(0, lambda: self._enable_exit_ui())

    def _enable_exit_ui(self):
        """实际更新退出提示UI（确保在主线程执行）"""
        if hasattr(self, "hint_label") and self.hint_label is not None:
            self.allow_exit = True  # 允许退出
            self.hint_label.config(text="Press ESC to exit")  # 更新提示文字
            self.root.bind("<Escape>", self.delayed_exit)  # 绑定退出事件
        else:
            print("警告：hint_label未初始化，无法更新退出提示")

    def update_exit_countdown(self, remaining):
        """更新退出倒计时提示（显示剩余多少秒后允许退出）"""
        if remaining > 0:
            self.hint_label.config(text=f"Exit allowed in {remaining} seconds...")
            self.root.after(1000, self.update_exit_countdown, remaining - 1)
        else:
            self.hint_label.config(text="Exit allowed in 0 seconds...")
            self.enable_exit()  # 倒计时结束，允许退出

    def check_window_focus(self):
        """检查窗口是否获得焦点，并动态调整透明度"""
        if self.is_fullscreen:  # 仅在全屏模式下调整
            try:
                # 判断当前活动窗口是否为倒计时窗口
                if platform.system() == "Windows":
                    # Windows通过系统API获取活动窗口标题
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    active_title = ctypes.create_string_buffer(256)
                    ctypes.windll.user32.GetWindowTextA(hwnd, active_title, 256)
                    active_title = active_title.value.decode("utf-8", errors="ignore")
                    is_active = active_title == self.root.title()
                else:
                    # 其他系统通过pygetwindow获取活动窗口
                    active_window = gw.getActiveWindow()
                    is_active = (
                        active_window and self.root.title() in active_window.title
                    )

                # 根据是否活动调整透明度（活动60%，非活动15%）
                new_alpha = 0.6 if is_active else 0.15
                if abs(self.root.attributes("-alpha") - new_alpha) > 0.01:
                    self.root.attributes("-alpha", new_alpha)
            except Exception as e:
                print(f"检查窗口焦点时出错: {e}")

        # 每20毫秒检查一次
        self.root.after(20, self.check_window_focus)

    def calculate_font_sizes(self):
        """根据屏幕尺寸计算自适应字体大小（基于1920x1080基准缩放）"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        base_width = 1920
        base_height = 1080
        # 计算缩放比例（取宽高缩放中的较小值）
        scale = min(screen_width / base_width, screen_height / base_height)
        return {
            "title": int(120 * scale),  # 主标题字体大小
            "overtime": int(50 * scale),  # 超时时间字体大小
            "info": int(36 * scale),  # 信息文字字体大小
            "hint": int(18 * scale),  # 提示文字字体大小
        }

    def time_up(self):
        """
        倒计时结束处理（包括自动结束和手动结束）

        主要流程:
            1. 切换到全屏模式并恢复窗口交互
            2. 根据结束类型（自动/手动）显示不同内容
            3. 启动结束后的计时更新
            4. 准备微信收藏内容并触发保存（若启用）
        """
        self.running = False  # 停止倒计时

        # 清除原有窗口组件
        for widget in self.root.winfo_children():
            widget.destroy()

        # 恢复窗口交互能力（关闭鼠标穿透）
        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, -20, style & ~0x20
            )  # 移除透明样式
        elif platform.system() == "Darwin":
            self.root.attributes("-ignoremouseevents", False)  # 允许鼠标事件

        # 切换到全屏模式
        self.is_fullscreen = True
        self.root.attributes("-alpha", 0.15)  # 初始透明度15%
        self.root.overrideredirect(False)  # 恢复窗口边框
        self.root.attributes("-fullscreen", True)  # 全屏显示
        self.root.attributes("-topmost", True)  # 保持置顶
        self.root.focus_force()  # 获取焦点
        self.root.update_idletasks()  # 更新UI

        # 设置窗口标题（用于焦点检测）
        self.root.title("Countdown Timer - Time's up")
        # 启动窗口焦点检测（动态调整透明度）
        self.check_window_focus()

        # 初始化结束后的变量
        self.allow_exit = False
        self.auto_elapsed_seconds = 0
        self.manual_elapsed_seconds = 0
        self.start_time_str = self.start_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化开始时间
        self.end_time_str = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化结束时间
        font_sizes = self.calculate_font_sizes()  # 计算字体大小

        # 创建主布局框架
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

        # 根据结束类型设置不同行数（手动结束5行，自动结束4行）
        row_count = 5 if self.is_manual_done else 4
        for i in range(row_count):
            main_frame.grid_rowconfigure(i, weight=1)  # 行权重平均分配
        main_frame.grid_columnconfigure(0, weight=1)  # 列权重为1

        # 1. 主标题（手动结束/自动结束区分显示）
        title_text = "Manual done!" if self.is_manual_done else "Time's up"
        tk.Label(
            main_frame,
            text=title_text,
            font=(self.font_family[0], font_sizes["title"], "bold"),
            fg="blue" if self.is_manual_done else "red",  # 手动蓝色，自动红色
            bg="white",
            anchor="center",
            justify="center",
        ).grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # 计算时间值（已用、剩余、总时长）
        elapsed = self.format_time(self.total_seconds - self.remaining_seconds)
        remaining = self.format_time(self.remaining_seconds)
        total_time = self.format_time(self.total_seconds)

        # 手动结束特有行 - 2. 已用时间/剩余时间（仅手动结束显示）
        if self.is_manual_done:
            tk.Label(
                main_frame,
                text=f"{elapsed} / {remaining}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="green",
                bg="white",
                anchor="center",
                justify="center",
            ).grid(row=1, column=0, sticky="nsew", pady=10)

        # 3. 结束后经过的时间（两种结束方式都有，行号根据类型调整）
        elapsed_row = 2 if self.is_manual_done else 1  # 手动第2行，自动第1行
        if self.is_manual_done:
            self.manual_elapsed_label = tk.Label(
                main_frame,
                text=f"{self.format_time(0)} from {self.end_time_str}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="blue",
                bg="white",
                anchor="center",
                justify="center",
            )
            self.manual_elapsed_label.grid(
                row=elapsed_row, column=0, sticky="nsew", pady=10
            )
            self.update_manual_elapsed()  # 启动手动计时更新
        else:
            self.auto_elapsed_label = tk.Label(
                main_frame,
                text=f"{self.format_time(0)} from {self.start_time_str}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="red",
                bg="white",
                anchor="center",
                justify="center",
            )
            self.auto_elapsed_label.grid(
                row=elapsed_row, column=0, sticky="nsew", pady=10
            )
            self.update_auto_elapsed()  # 启动自动计时更新

        # 4. 总时长和开始时间（两种结束方式都有，行号根据类型调整）
        info_row = 3 if self.is_manual_done else 2  # 手动第3行，自动第2行
        tk.Label(
            main_frame,
            text=f"{total_time} from {self.start_time_str}",
            font=(self.font_family[0], font_sizes["info"]),
            fg="gray",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(row=info_row, column=0, sticky="nsew", pady=20)

        # 退出提示标签（不算在内容行内）
        hint_row = 4 if self.is_manual_done else 3  # 手动第4行，自动第3行
        self.hint_label = tk.Label(
            main_frame,
            text="",
            font=(self.font_family[0], font_sizes["hint"]),
            fg="orange",
            bg="white",
            anchor="center",
            justify="center",
        )
        self.hint_label.grid(row=hint_row, column=0, sticky="nsew", pady=(20, 0))

        # 绑定退出事件
        self.root.bind("<Escape>", self.delayed_exit)
        main_frame.bind("<Escape>", self.delayed_exit)

        # 准备微信收藏内容
        start_time = self.start_datetime.strftime("%A %Y-%m-%d %H:%M:%S")
        duration_actual = self.total_seconds - self.remaining_seconds
        duration_planned = self.total_seconds

        if self.is_manual_done:
            content = f"{self.format_time(duration_actual)}/{self.format_time(duration_planned)} from {start_time}\n"
        else:
            content = f"{self.format_time(duration_planned)} from {start_time}\n"

        # 启动微信保存线程或直接开始退出倒计时
        if self.enable_wechat_save:
            content = content.strip() + "\n"
            wechat_thread = threading.Thread(target=self.record_to_wechat)
            wechat_thread.daemon = True
            wechat_thread.start()
        else:
            self.update_exit_countdown(1)  # 1秒后允许退出

        # 复制内容到剪贴板
        pyperclip.copy(content)

    def record_to_wechat(self):
        """
        将倒计时信息保存到微信收藏

        操作流程:
            1. 尝试激活或启动微信应用
            2. 打开微信收藏窗口（使用快捷键Ctrl+Alt+D）
            3. 粘贴预准备的内容并完成保存
        """
        if not self.enable_wechat_save:
            return

        try:
            # 获取微信窗口（尝试激活）
            wechat_windows = gw.getWindowsWithTitle("Weixin")
            if not wechat_windows:
                # 尝试通过快捷键唤醒微信
                pyautogui.hotkey("ctrl", "alt", "w")
                time.sleep(0.3)
                wechat_windows = gw.getWindowsWithTitle("Weixin")

            # 若仍无微信窗口，则尝试启动微信
            if not wechat_windows:
                print("未找到微信窗口，尝试启动...")
                wechat_path = r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
                if os.path.exists(wechat_path):
                    # 启动微信
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "open", wechat_path, None, None, 1
                    )
                    time.sleep(20)  # 等待微信启动
                    wechat_windows = gw.getWindowsWithTitle("Weixin")
                else:
                    raise Exception("未找到微信路径")

            # 激活微信窗口
            wechat_window = wechat_windows[0]
            wechat_window.minimize()  # 先最小化
            wechat_window.restore()  # 再恢复（激活窗口）

            # 检查微信窗口是否激活成功
            timeout = 1.0
            interval = 0.1
            max_attempts = int(timeout / interval)
            wechat_activated = False

            for attempt in range(max_attempts):
                active_window = gw.getActiveWindow()
                if active_window and "Weixin" in active_window.title:
                    wechat_activated = True
                    print(f"微信窗口已激活（第{attempt+1}次尝试）")
                    break
                time.sleep(interval)

            if not wechat_activated:
                raise Exception(f"微信窗口激活超时（{timeout}秒内未激活）")

            # 打开微信收藏（快捷键Ctrl+Alt+D）
            pyautogui.hotkey("ctrl", "alt", "d")

            # 等待收藏窗口激活
            timeout = 5
            interval = 0.5
            target_title_keywords = ["Note", "笔记"]  # 匹配收藏窗口标题
            note_window_activated = False

            for _ in range(int(timeout / interval)):
                active_window = gw.getActiveWindow()
                if active_window and any(
                    keyword in active_window.title for keyword in target_title_keywords
                ):
                    note_window_activated = True
                    break
                time.sleep(interval)

            if not note_window_activated:
                raise Exception(f"收藏窗口激活超时（{timeout}秒内未激活）")

            # 粘贴内容（剪贴板中已准备好）
            pyautogui.hotkey("ctrl", "v")
            print("微信收藏保存成功")

        except Exception as e:
            print(f"微信保存失败: {str(e)}")

        finally:
            # 无论成功与否，启动退出倒计时
            self.root.after(0, lambda: self.update_exit_countdown(2))

    def delayed_exit(self, event=None):
        """延迟退出处理（仅当允许退出时执行）"""
        if self.allow_exit:
            self.exit_program()

    def exit_program(self, event=None):
        """
        退出程序

        退出前将超时信息复制到剪贴板
        """
        # 准备超时信息并复制到剪贴板
        if self.is_manual_done:
            content = f"timeout {self.format_time(self.manual_elapsed_seconds)} from {self.end_time_str}\n"
        else:
            content = f"timeout {self.format_time(self.auto_elapsed_seconds)} from {self.end_time_str}"
        pyperclip.copy(content)

        # 销毁窗口，结束程序
        self.root.destroy()


if __name__ == "__main__":
    # 清理旧的进程终止脚本并创建新脚本
    if os.path.exists(kill_self_py_bat):
        os.system(kill_self_py_bat)
    with open(kill_self_py_bat, "wb") as f:
        f.write(b"@echo off\n")
        f.write(f"taskkill /f /pid {os.getpid()}\n".encode("utf-8"))  # 终止当前进程

    # 处理命令行参数（倒计时秒数）
    try:
        countdown_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
        if countdown_seconds <= 0:
            raise ValueError("时间必须为正数")
    except ValueError:
        countdown_seconds = 1500  # 默认25分钟

    # 处理微信保存控制参数
    try:
        enable_wechat_save = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        enable_wechat_save = 1 if enable_wechat_save == 1 else 0
    except (IndexError, ValueError):
        enable_wechat_save = 0  # 默认禁用

    # 启动主窗口和倒计时器
    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds, enable_wechat_save)
    root.mainloop()
