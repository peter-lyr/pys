import os
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
    with open(file, 'wb') as f:
        for line in lines:
            if type(line) != bytes:
                line = line.encode('utf-8')
            f.write(line + b'\n')
