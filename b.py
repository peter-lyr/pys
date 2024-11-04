import os
from os.path import isfile
import subprocess
import sys
from datetime import datetime

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
    with open(os.path.join(r'C:\temp', file), 'wb') as f:
        for line in lines:
            if type(line) != bytes:
                line = line.encode('utf-8')
            f.write(line + b'\n')

def run_cmd_and_get_output(command):
    """
    运行cmd命令并返回它的执行结果
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
        else:
            output = result.stderr.strip()
    except Exception as e:
        output = str(e)
    return output


def get_untracked_file_size(dir=None):
    if not dir:
        return -1
    untracked_files = run_cmd_and_get_output(
        f"cd {dir} & git ls-files --exclude-standard --no-ignored --others"
    )
    untracked_files = untracked_files.strip().replace("\r", "").split("\n")
    sizes = 0
    for untracked_file in untracked_files:
        if os.path.isfile(untracked_file):
            print(untracked_file)
            sizes += os.path.getsize(untracked_file)
    if sizes >= 500 * 1024 * 1024:
        print("error")
    return sizes
