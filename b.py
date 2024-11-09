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


def get_sta_output(cmd_params, silent=False):
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
                res = res.strip()
                output.append(res)
                if not silent:
                    print(res)
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


def add_ignore_files(dir, files):
    lines = []
    gitignore = os.path.join(dir, ".gitignore")
    if os.path.exists(gitignore):
        with open(gitignore, "rb") as f:
            for line in f.readlines():
                line = line.strip()
                if line not in lines:
                    lines.append(line)
    for file in files:
        if file.encode("utf-8") not in lines:
            lines.append(file.encode("utf-8"))
    with open(gitignore, "wb") as f:
        for line in lines:
            f.write(line + b"\n")


def merge_bins_file(bins_dir_full):
    bins_dir_root, bins_dir = os.path.split(bins_dir_full)

    out_file = "-bin".join(bins_dir.split("-bin")[:-1])
    if not out_file:
        os._exit(4)

    out_file_name = out_file

    temp = out_file.split(".")
    out_file_true = ".".join(temp[:-1])
    out_ext = temp[-1]

    out_file_true = out_file_true + "." + out_ext

    bins = os.listdir(bins_dir_full)
    bins.sort()
    new_bins = []
    for bin in bins:
        if out_file_name in bin:
            new_bins.append(bin)
    if not new_bins:
        os._exit(3)
    with open(os.path.join(bins_dir_root, out_file_true), "wb") as outf:
        for bin in new_bins:
            if out_file_name not in bin:
                continue
            print(bin)
            with open(os.path.join(bins_dir_full, bin), "rb") as inf:
                buffer = inf.read()
                outf.write(buffer)


def split_big_file(bin_file_full, bin_sub_size=10 * 1024 * 1024):
    bin_file_full_dir = os.path.split(bin_file_full)[0]
    bin_file = os.path.split(bin_file_full)[-1]

    bin_size = os.path.getsize(bin_file_full)
    if bin_size < bin_sub_size:
        os._exit(3)
    bin_sub_nums = int(bin_size / bin_sub_size)

    bin_dir = f"{bin_file_full}-bins"
    os.makedirs(bin_dir, exist_ok=True)

    add_ignore_files(bin_file_full_dir, [bin_file])

    with open(bin_file_full, "rb") as infile:
        for i in range(bin_sub_nums + 1):
            part_name = f"{bin_dir}/{bin_file}_{(i + 1):0>4}.bin"
            with open(part_name, "wb") as outfile:
                buffer = infile.read(bin_sub_size)
                outfile.write(buffer)
