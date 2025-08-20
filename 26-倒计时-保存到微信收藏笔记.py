import ctypes
import os
import platform
import threading
import time
import tkinter as tk
from datetime import datetime

import pyautogui
import pygetwindow as gw
import pyperclip


class CountdownTimer:
    def __init__(self, root, total_seconds=10):
        """初始化倒计时器"""
        self.root = root
        self.start_datetime = datetime.now()
        self.total_seconds = total_seconds

        # 窗口基础设置
        self.root.overrideredirect(True)
        self.root.geometry("148x68")
        self.root.attributes("-alpha", 0.2)
        self.root.attributes("-topmost", True)

        # 透明背景与任务栏设置
        self.bg_color = self.get_transparent_color()
        self.root.configure(bg=self.bg_color)
        if platform.system() == "Windows":
            self.root.attributes("-toolwindow", True)
        elif platform.system() == "Darwin":
            self.root.attributes("-type", "utility")
        else:
            self.root.attributes("-type", "toolbar")

        # 字体与计时变量
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")
        self.remaining_seconds = total_seconds
        self.running = False
        self.allow_exit = False
        self.overtime_seconds = 0

        # 创建倒计时标签
        self.time_label = tk.Label(
            root,
            text=self.format_time(self.remaining_seconds),
            font=(self.font_family[0], 24),
            fg="green",
            bg=self.bg_color,
        )
        self.time_label.pack(expand=True)

        self.total_time_label = tk.Label(
            root,
            text=f"{self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 14),
            fg="gray",
            bg=self.bg_color,
        )
        self.total_time_label.pack(pady=2)

        # 绑定退出与初始化
        self.root.bind("<Escape>", self.exit_program)
        self.position_window()
        self.set_mouse_transparent()
        self.start_countdown()

    def get_transparent_color(self):
        """获取系统支持的透明色"""
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
        """窗口固定在左上角"""
        self.root.geometry("148x68+0+0")

    def set_mouse_transparent(self):
        """设置鼠标穿透效果"""
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
        """格式化时间为时分秒"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return (
            f"{hours:02d}:{minutes:02d}:{secs:02d}"
            if hours > 0
            else f"{minutes:02d}:{secs:02d}"
        )

    def update_timer(self):
        """更新倒计时显示"""
        if self.remaining_seconds > 0 and self.running:
            self.time_label.config(text=self.format_time(self.remaining_seconds))
            self.remaining_seconds -= 1
            self.root.after(1000, self.update_timer)
        elif self.remaining_seconds == 0 and self.running:
            self.time_up()

    def update_overtime(self):
        """更新超时时间（每秒）"""
        self.overtime_seconds += 1
        self.overtime_label.config(
            text=f"Overtime: {self.format_time(self.overtime_seconds)}"
        )
        self.root.after(1000, self.update_overtime)

    def start_countdown(self):
        """启动倒计时"""
        self.running = True
        self.update_timer()

    def enable_exit(self):
        """允许退出（确保在主线程中更新UI）"""
        self.root.after(0, lambda: self._enable_exit_ui())

    def _enable_exit_ui(self):
        """实际更新UI的方法（在主线程执行）"""
        # 检查hint_label是否存在
        if hasattr(self, "hint_label") and self.hint_label is not None:
            self.allow_exit = True
            self.hint_label.config(text="Press any key or click to exit")
            # 重新绑定事件确保响应
            self.root.bind("<Key>", self.delayed_exit)
            self.root.bind("<Button-1>", self.delayed_exit)
        else:
            print("警告：hint_label未初始化，无法更新退出提示")

    def calculate_font_sizes(self):
        """根据窗口大小计算合适的字体大小"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 根据屏幕尺寸按比例计算字体大小（确保在不同分辨率下适配）
        base_width = 1920  # 基准宽度（1080p）
        base_height = 1080  # 基准高度

        # 计算缩放比例（取宽高比例中的较小值，避免文字溢出）
        scale = min(screen_width / base_width, screen_height / base_height)

        # 基于缩放比例计算各元素字体大小（增大比例确保铺满窗口）
        return {
            "title": int(120 * scale),  # 主标题（增大字号）
            "overtime": int(50 * scale),  # 超时时间（增大字号）
            "info": int(36 * scale),  # 开始时间和时长（增大字号）
            "hint": int(18 * scale),  # 退出提示（增大字号）
        }

    def time_up(self):
        """倒计时结束处理（确保内容铺满窗口）"""
        self.running = False
        for widget in self.root.winfo_children():
            widget.destroy()

        # 恢复窗口交互
        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style & ~0x20)
        elif platform.system() == "Darwin":
            self.root.attributes("-ignoremouseevents", False)

        # 1. 窗口最大化设置
        self.root.attributes("-alpha", 0.15)
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.focus_force()  # 确保窗口获得焦点

        # 确保获取正确的屏幕尺寸（等待窗口最大化完成）
        self.root.update_idletasks()

        # 2. 创建铺满窗口的UI布局
        self.allow_exit = False
        self.overtime_seconds = 0
        start_time_str = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # 计算适合当前屏幕的字体大小
        font_sizes = self.calculate_font_sizes()

        # 主容器：填充整个窗口
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)  # 保留少量边距

        # 使用网格布局实现垂直均匀分布
        main_frame.grid_rowconfigure(0, weight=1)  # 标题行权重
        main_frame.grid_rowconfigure(1, weight=1)  # 超时时间行权重
        main_frame.grid_rowconfigure(2, weight=1)  # 开始时间行权重
        main_frame.grid_rowconfigure(3, weight=1)  # 时长行权重
        main_frame.grid_rowconfigure(4, weight=1)  # 提示行权重
        main_frame.grid_columnconfigure(0, weight=1)  # 列权重

        # "Time's up"主标签（居中，占满行高）
        tk.Label(
            main_frame,
            text="Time's up",
            font=(self.font_family[0], font_sizes["title"], "bold"),
            fg="red",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(
            row=0, column=0, sticky="nsew", pady=(0, 20)
        )  # 粘性布局充满单元格

        # 超时时间标签（居中，占满行高）
        self.overtime_label = tk.Label(
            main_frame,
            text=f"Overtime: {self.format_time(0)}",
            font=(self.font_family[0], font_sizes["overtime"], "bold"),
            fg="orange",
            bg="white",
            anchor="center",
            justify="center",
        )
        self.overtime_label.grid(row=1, column=0, sticky="nsew", pady=20)  # 粘性布局

        # 开始时间标签（居中，占满行高）
        tk.Label(
            main_frame,
            text=f"Start time: {start_time_str}",
            font=(self.font_family[0], font_sizes["info"]),
            fg="blue",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(
            row=2, column=0, sticky="nsew", pady=20
        )  # 粘性布局

        # 时长标签（居中，占满行高）
        tk.Label(
            main_frame,
            text=f"Duration: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], font_sizes["info"]),
            fg="purple",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(
            row=3, column=0, sticky="nsew", pady=20
        )  # 粘性布局

        # 退出提示标签（居中，占满行高）
        self.hint_label = tk.Label(
            main_frame,
            text="Saving to WeChat...",
            font=(self.font_family[0], font_sizes["hint"]),
            fg="orange",
            bg="white",
            anchor="center",
            justify="center",
        )
        self.hint_label.grid(row=4, column=0, sticky="nsew", pady=(20, 0))  # 粘性布局

        # 3. 启动超时计时
        self.update_overtime()

        # 4. 绑定事件
        self.root.bind("<Key>", self.delayed_exit)
        self.root.bind("<Button-1>", self.delayed_exit)
        main_frame.bind("<Key>", self.delayed_exit)
        main_frame.bind("<Button-1>", self.delayed_exit)

        # 5. 启动线程执行微信保存操作
        wechat_thread = threading.Thread(target=self.record_to_wechat)
        wechat_thread.daemon = True
        wechat_thread.start()

    def record_to_wechat(self):
        """微信收藏保存（在子线程中执行，优化窗口激活检测）"""
        start_time = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        duration = self.format_time(self.total_seconds)
        content = f"倒计时记录\n开始时间: {start_time}\n时长: {duration}"
        pyperclip.copy(content)

        try:
            # 激活微信窗口
            wechat_windows = gw.getWindowsWithTitle("Weixin")
            if not wechat_windows:
                print("未找到微信窗口，尝试启动...")
                wechat_path = r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
                if os.path.exists(wechat_path):
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "open", wechat_path, None, None, 1
                    )
                    time.sleep(20)
                    wechat_windows = gw.getWindowsWithTitle("Weixin")
                else:
                    raise Exception("未找到微信路径")

            wechat_window = wechat_windows[0]
            wechat_window.minimize()
            wechat_window.restore()

            # 优化：循环检测微信窗口是否激活，最多等待1秒
            timeout = 1.0  # 总超时时间（秒）
            interval = 0.1  # 检测间隔（秒）
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

            # 打开收藏并保存
            pyautogui.hotkey("ctrl", "alt", "d")

            # 等待收藏窗口
            timeout = 5
            interval = 0.5
            target_title_keywords = ["Note", "笔记"]
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

            # 粘贴并保存
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)
            pyautogui.press("esc")
            print("微信收藏保存成功")

        except Exception as e:
            print(f"微信保存失败: {str(e)}")

        finally:
            # 保存完成后切回主窗口并允许退出
            self.root.after(0, lambda: self._restore_focus_and_enable())

    def _restore_focus_and_enable(self):
        """恢复主窗口焦点并允许退出"""
        self.root.focus_force()  # 强制将焦点切回倒计时窗口
        self.enable_exit()

    def delayed_exit(self, event=None):
        """延迟退出处理"""
        if self.allow_exit:
            self.exit_program()

    def exit_program(self, event=None):
        """退出程序"""
        self.root.destroy()


if __name__ == "__main__":
    countdown_seconds = 1  # 测试用1秒
    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds)
    root.mainloop()
