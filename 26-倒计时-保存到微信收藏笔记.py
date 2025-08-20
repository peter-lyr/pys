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
            text=f"Total time: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 12),
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

    def time_up(self):
        """倒计时结束处理（修复hint_label初始化问题）"""
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

        # 2. 创建居中布局的全屏UI
        self.allow_exit = False
        self.overtime_seconds = 0
        start_time_str = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # 主容器：使用grid布局，确保内容垂直和水平居中
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill=tk.BOTH)  # 填充整个窗口
        main_frame.grid_rowconfigure(0, weight=1)  # 允许行扩展
        main_frame.grid_columnconfigure(0, weight=1)  # 允许列扩展

        # 内容容器：所有元素放在这里，实现整体居中
        content_frame = tk.Frame(main_frame, bg="black")
        content_frame.grid(row=0, column=0, sticky="nsew")  # 居中对齐

        # "Time's up"主标签（居中显示）
        tk.Label(
            content_frame,
            text="Time's up",
            font=(self.font_family[0], 100, "bold"),
            fg="red",
            bg="white",
            anchor="center",  # 文本自身居中
        ).pack(pady=(0, 40))

        # 超时时间标签（居中显示）
        self.overtime_label = tk.Label(
            content_frame,
            text=f"Overtime: {self.format_time(0)}",
            font=(self.font_family[0], 36, "bold"),
            fg="orange",
            bg="white",
            anchor="center",
        )
        self.overtime_label.pack(pady=20)

        # 开始时间标签（居中显示）
        tk.Label(
            content_frame,
            text=f"Start time: {start_time_str}",
            font=(self.font_family[0], 24),
            fg="blue",
            bg="white",
            anchor="center",
        ).pack(pady=10)

        # 时长标签（居中显示）
        tk.Label(
            content_frame,
            text=f"Duration: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 24),
            fg="purple",
            bg="white",
            anchor="center",
        ).pack(pady=10)

        # 退出提示标签（关键修复：显式赋值给self.hint_label，不使用链式调用）
        self.hint_label = tk.Label(
            content_frame,
            text="Saving to WeChat...",
            font=(self.font_family[0], 12),
            fg="orange",
            bg="white",
            anchor="center",
        )
        self.hint_label.pack(pady=(40, 0))  # 分开调用pack，确保赋值成功

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
        """微信收藏保存（在子线程中执行）"""
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
            time.sleep(1)

            # 打开收藏并保存
            pyautogui.hotkey("ctrl", "alt", "d")

            # 等待收藏窗口
            timeout = 5
            interval = 0.5
            target_title_keywords = ["Note", "笔记"]

            for _ in range(int(timeout / interval)):
                active_window = gw.getActiveWindow()
                if active_window and any(
                    keyword in active_window.title for keyword in target_title_keywords
                ):
                    break
                time.sleep(interval)

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
