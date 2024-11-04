import os
import subprocess
import sys
from datetime import datetime
from traceback import format_exc

import win32clipboard
import win32con


def get_clipboard_data():
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        if data:
            data = data.replace("\r\n", "\n")
    except TypeError:
        data = None
    win32clipboard.CloseClipboard()
    return data


def get_params_from_file(file):
    with open(file, "rb") as f:
        lines = [line.decode("utf-8").strip() for line in f.readlines()]
    return lines


def get_params():
    params = []
    if len(sys.argv) > 1:
        params = sys.argv[1:]
        if len(params) == 1 and os.path.split(params[0])[1].split("-")[0] == "params":
            params = get_params_from_file(params[0])
    else:
        text = get_clipboard_data()
        if text != None:
            params = text.split("\n")
    return params


def write_err(lines):
    file = datetime.now().strftime("%Y%m%d-%H%M%S.txt")
    with open(os.path.join(r"C:\temp", file), "wb") as f:
        for line in lines:
            if type(line) != bytes:
                line = line.encode("utf-8")
            f.write(line + b"\n")


def get_sta_output(cmd_params):
    output = []
    sta = 1234
    try:
        process = subprocess.Popen(
            cmd_params,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        while True:
            res = process.stdout.readline()
            if res == "" and process.poll() is not None:
                break
            if res:
                print(res.strip())
                output.append(res.strip())
                sys.stdout.flush()
        sta = process.wait()
    except:
        sys.stdout.flush()
        e = format_exc()
        print(e, flush=True)
    return sta, output


# def run_cmd_and_get_output(command):
#     """
#     运行cmd命令并返回它的执行结果
#     """
#     output = ""
#     try:
#         result = subprocess.run(command, shell=True, capture_output=True, text=True)
#         p(command)
#         if result.returncode == 0:
#             if result.stdout:
#                 output = result.stdout.strip()
#         else:
#             if result.stderr:
#                 output = result.stderr.strip()
#     except Exception as e:
#         output = str(e) + "WWEWEWEWEWE"
#         return "-23238"
#     return output


test_txt = r"C:\Windows\Temp\23sxi.txt"


def p(text):
    try:
        for line in text.strip().replace("\r", "").split("\n"):
            line = line.strip()
            if line:
                with open(test_txt, "wb") as f:
                    f.write(line.encode("utf-8"))
                os.system(f"chcp 65001>nul & cat {test_txt} & echo.")
            else:
                os.system("chcp 65001>nul & echo.")
    except Exception as e:
        print(f"echo {text}", flush=True)
        print(e, "][]]]]]]]]]]]")


def get_untracked_file_size(dir=None):
    if not dir:
        return -1, []
    os.chdir(dir)
    _, untracked_files = get_sta_output(
        [
            "git",
            "ls-files",
            "--exclude-standard",
            "--no-ignored",
            "--others",
        ]
    )
    sizes = 0
    new_untracked_files = []
    for untracked_file in untracked_files:
        if os.path.isfile(untracked_file):
            # p("untracked " + untracked_file + "|")
            sizes += os.path.getsize(untracked_file)
            new_untracked_files.append(untracked_file)
        else:
            p("Is not a file: [" + untracked_file + "]")
    return sizes, new_untracked_files
