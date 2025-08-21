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

home = os.environ["USERPROFILE"]
dp = os.path.join(home, "Dp")
temp = os.path.join(dp, "temp")
# 确保temp目录存在
os.makedirs(temp, exist_ok=True)
kill_self_py_bat = os.path.join(temp, "26-倒计时-保存到微信收藏笔记.py.bat")
# 监测文件路径
MONITOR_FILE = os.path.join(temp, "countdown_monitor.txt")


class CountdownTimer:
    def __init__(self, root, countdown_seconds=1500, enable_wechat_save=0):
        """初始化倒计时器"""
        self.root = root
        self.start_datetime = datetime.now()
        self.total_seconds = countdown_seconds
        self.enable_wechat_save = enable_wechat_save
        self.is_fullscreen = False  # 标记是否处于全屏状态
        self.is_manual_done = False  # 标记是否手动结束
        self.running = False  # 提前初始化running属性，解决线程访问问题
        self.remaining_seconds = countdown_seconds  # 提前初始化

        # 创建监测文件
        with open(MONITOR_FILE, "w", encoding="utf-8") as f:
            f.write('')

        # 启动文件监测线程（此时running属性已初始化）
        self.monitor_thread = threading.Thread(target=self.monitor_file, daemon=True)
        self.monitor_thread.start()

        # 窗口基础设置
        self.root.overrideredirect(True)
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

        # 字体与其他变量
        self.font_family = ("SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial")
        self.allow_exit = False
        self.overtime_seconds = 0

        # 创建倒计时标签
        self.time_label = tk.Label(
            root,
            text=self._init_time_text(),
            font=(self.font_family[0], 20),
            fg="green",
            bg=self.bg_color,
        )
        self.time_label.pack(expand=True)

        self.total_time_label = tk.Label(
            root,
            text=f"Total time: {self.format_time(self.total_seconds)}",
            font=(self.font_family[0], 14),
            fg="gray",
            bg=self.bg_color,
        )
        self.total_time_label.pack(pady=2)

        # 添加手动结束提示
        self.manual_hint = tk.Label(
            root,
            text=f"Write 'manual done' to {MONITOR_FILE} to end early",
            font=(self.font_family[0], 10),
            fg="blue",
            bg=self.bg_color,
        )
        self.manual_hint.pack(pady=2)

        # 绑定退出与初始化
        self.root.bind("<Escape>", self.exit_program)
        self.position_window()
        self.set_mouse_transparent()
        self.start_countdown()  # 这里会设置self.running = True

    def monitor_file(self):
        """监测文件内容，检查是否需要手动结束"""
        while True:
            # 现在这些属性都已在初始化时定义
            if not self.running or self.remaining_seconds <= 0:
                continue

            try:
                if os.path.exists(MONITOR_FILE):
                    with open(MONITOR_FILE, "r", encoding="utf-8") as f:
                        content = f.read().strip().lower()
                        if content == "manual done":
                            self.is_manual_done = True
                            # 清空文件内容，避免重复触发
                            with open(MONITOR_FILE, "w", encoding="utf-8") as f_clear:
                                f_clear.write("")
                            # 提前结束倒计时
                            self.root.after(0, self.manual_end_countdown)
                            break
            except Exception as e:
                print(f"监测文件出错: {e}")

            time.sleep(1)  # 每秒检查一次

    def manual_end_countdown(self):
        """手动结束倒计时"""
        self.running = False
        self.time_up()

    def _init_time_text(self):
        """初始化时间显示文本"""
        elapsed_time = self.format_time(0)
        remaining_time = self.format_time(self.total_seconds)
        return f"{elapsed_time} / {remaining_time}"

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
        """窗口固定在右上角，铺满除任务栏外的屏幕"""
        if platform.system() == "Windows":
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
        else:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            taskbar_height = int(screen_height * 0.05)
            screen_height -= taskbar_height

        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

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
        """更新倒计时显示：同时显示已计时时间和剩余时间"""
        if self.remaining_seconds > 0 and self.running:
            elapsed_seconds = self.total_seconds - self.remaining_seconds
            elapsed_time = self.format_time(elapsed_seconds)
            remaining_time = self.format_time(self.remaining_seconds)
            self.time_label.config(text=f"{elapsed_time} / {remaining_time}")
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
        if hasattr(self, "hint_label") and self.hint_label is not None:
            self.allow_exit = True
            self.hint_label.config(text="Press ESC to exit")
            self.root.bind("<Escape>", self.delayed_exit)
        else:
            print("警告：hint_label未初始化，无法更新退出提示")

    def update_exit_countdown(self, remaining):
        """更新退出倒计时提示文字"""
        if remaining > 0:
            self.hint_label.config(text=f"Exit allowed in {remaining} seconds...")
            self.root.after(1000, self.update_exit_countdown, remaining - 1)
        else:
            self.hint_label.config(text="Exit allowed in 0 seconds...")
            self.enable_exit()  # 倒计时结束后允许退出

    def check_window_focus(self):
        """检查窗口是否获得焦点并调整透明度"""
        if self.is_fullscreen:  # 仅在全屏状态下调整
            try:
                # 获取当前活动窗口
                if platform.system() == "Windows":
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    active_title = ctypes.create_string_buffer(256)
                    ctypes.windll.user32.GetWindowTextA(hwnd, active_title, 256)
                    active_title = active_title.value.decode("utf-8", errors="ignore")
                    is_active = active_title == self.root.title()
                else:
                    active_window = gw.getActiveWindow()
                    is_active = (
                        active_window and self.root.title() in active_window.title
                    )

                # 根据是否活动设置透明度（60%活动，15%非活动）
                new_alpha = 0.6 if is_active else 0.15
                if abs(self.root.attributes("-alpha") - new_alpha) > 0.01:
                    self.root.attributes("-alpha", new_alpha)
            except Exception as e:
                print(f"检查窗口焦点时出错: {e}")

        # 继续定期检查
        self.root.after(20, self.check_window_focus)

    def calculate_font_sizes(self):
        """根据窗口大小计算合适的字体大小"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        base_width = 1920
        base_height = 1080
        scale = min(screen_width / base_width, screen_height / base_height)
        return {
            "title": int(120 * scale),
            "overtime": int(50 * scale),
            "info": int(36 * scale),
            "hint": int(18 * scale),
        }

    def time_up(self):
        """倒计时结束处理（包括正常结束和手动结束）"""
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

        # 窗口最大化设置 - 取消置顶
        self.is_fullscreen = True  # 标记为全屏状态
        self.root.attributes("-alpha", 0.15)
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.update_idletasks()

        # 设置窗口标题用于焦点检测
        self.root.title("Countdown Timer - Time's up")

        # 启动窗口焦点检查，动态调整透明度
        self.check_window_focus()

        # 创建铺满窗口的UI布局
        self.allow_exit = False
        self.overtime_seconds = 0
        start_time_str = self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        font_sizes = self.calculate_font_sizes()

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)  # 新增一行用于显示手动结束信息
        main_frame.grid_columnconfigure(0, weight=1)

        # 主标签（区分正常结束和手动结束）
        title_text = "Manual done!" if self.is_manual_done else "Time's up"
        tk.Label(
            main_frame,
            text=title_text,
            font=(self.font_family[0], font_sizes["title"], "bold"),
            fg="blue" if self.is_manual_done else "red",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # 超时时间标签（仅正常结束显示）
        if not self.is_manual_done:
            self.overtime_label = tk.Label(
                main_frame,
                text=f"Overtime: {self.format_time(0)}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="orange",
                bg="white",
                anchor="center",
                justify="center",
            )
            self.overtime_label.grid(row=1, column=0, sticky="nsew", pady=20)
        else:
            # 手动结束时显示已用时间和剩余时间
            elapsed_seconds = self.total_seconds - self.remaining_seconds
            remaining_seconds = self.remaining_seconds
            tk.Label(
                main_frame,
                text=f"Elapsed: {self.format_time(elapsed_seconds)}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="green",
                bg="white",
                anchor="center",
                justify="center",
            ).grid(row=1, column=0, sticky="nsew", pady=10)

            tk.Label(
                main_frame,
                text=f"Remaining: {self.format_time(remaining_seconds)}",
                font=(self.font_family[0], font_sizes["overtime"], "bold"),
                fg="orange",
                bg="white",
                anchor="center",
                justify="center",
            ).grid(row=2, column=0, sticky="nsew", pady=10)

        # 开始时间标签
        tk.Label(
            main_frame,
            text=f"Start time: {start_time_str}",
            font=(self.font_family[0], font_sizes["info"]),
            fg="green",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(row=3, column=0, sticky="nsew", pady=20)

        # 结束时间标签
        tk.Label(
            main_frame,
            text=f"End time: {end_time_str}",
            font=(self.font_family[0], font_sizes["info"]),
            fg="purple",
            bg="white",
            anchor="center",
            justify="center",
        ).grid(row=4, column=0, sticky="nsew", pady=20)

        # 退出提示标签
        self.hint_label = tk.Label(
            main_frame,
            text="",
            font=(self.font_family[0], font_sizes["hint"]),
            fg="orange",
            bg="white",
            anchor="center",
            justify="center",
        )
        self.hint_label.grid(row=5, column=0, sticky="nsew", pady=(20, 0))

        # 启动超时计时（仅正常结束）
        if not self.is_manual_done:
            self.update_overtime()

        # 绑定事件
        self.root.bind("<Escape>", self.delayed_exit)
        main_frame.bind("<Escape>", self.delayed_exit)

        # 根据控制变量决定是否启动微信保存线程
        if self.enable_wechat_save:
            wechat_thread = threading.Thread(target=self.record_to_wechat)
            wechat_thread.daemon = True
            wechat_thread.start()
        else:
            # 不执行微信保存时，启动退出倒计时
            self.update_exit_countdown(2)

    def record_to_wechat(self):
        """微信收藏保存（包含手动结束信息）"""
        if not self.enable_wechat_save:
            return

        start_time = self.start_datetime.strftime("%A %Y-%m-%d %H:%M:%S")
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration_actual = self.total_seconds - self.remaining_seconds
        duration_planned = self.total_seconds

        # 根据是否手动结束设置不同的内容
        if self.is_manual_done:
            content = (
                f"Manual done!\n"
                f"Planned duration: {self.format_time(duration_planned)}\n"
                f"Actual duration: {self.format_time(duration_actual)}\n"
                f"Remaining time: {self.format_time(self.remaining_seconds)}\n"
                f"From {start_time} to {end_time}\n"
            )
        else:
            content = (
                f"Time's up!\n"
                f"Duration: {self.format_time(duration_planned)}\n"
                f"From {start_time} to {end_time}\n"
            )

        pyperclip.copy(content)

        try:
            # 激活微信窗口
            wechat_windows = gw.getWindowsWithTitle("Weixin")
            if not wechat_windows:
                pyautogui.hotkey("ctrl", "alt", "w")
                time.sleep(0.3)
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

            # 检测微信窗口激活
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
            print("微信收藏保存成功")

        except Exception as e:
            print(f"微信保存失败: {str(e)}")

        finally:
            # 保存完成后启动退出倒计时
            self.root.after(0, lambda: self.update_exit_countdown(2))

    def _restore_focus_and_enable(self):
        """恢复主窗口焦点并允许退出"""
        self.root.focus_force()

    def delayed_exit(self, event=None):
        """延迟退出处理"""
        if self.allow_exit:
            self.exit_program()

    def exit_program(self, event=None):
        """退出程序"""
        # # 清理监测文件
        # if os.path.exists(MONITOR_FILE):
        #     try:
        #         os.remove(MONITOR_FILE)
        #     except:
        #         pass
        self.root.destroy()


if __name__ == "__main__":
    if os.path.exists(kill_self_py_bat):
        os.system(kill_self_py_bat)
    with open(kill_self_py_bat, "wb") as f:
        f.write(b"@echo off\n")
        f.write(f"taskkill /f /pid {os.getpid()}\n".encode("utf-8"))
        f.write(f"taskkill /f /pid {os.getppid()}\n".encode("utf-8"))

    # 处理命令行参数
    try:
        countdown_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
        if countdown_seconds <= 0:
            raise ValueError("时间必须为正数")
    except ValueError:
        countdown_seconds = 1500

    # 处理微信保存控制参数
    try:
        enable_wechat_save = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        enable_wechat_save = 1 if enable_wechat_save == 1 else 0
    except (IndexError, ValueError):
        enable_wechat_save = 0
    enable_wechat_save = 1

    root = tk.Tk()
    app = CountdownTimer(root, countdown_seconds, enable_wechat_save)
    root.mainloop()
