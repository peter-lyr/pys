import os
import subprocess
import sys
import time

import b

dir = file = sys.argv[1]
git_fake_remote_dir = file = sys.argv[2]

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


dir_tail = os.path.split(dir)[-1]
os.chdir(git_fake_remote_dir)
remote = os.path.join(git_fake_remote_dir, dir_tail)
os.makedirs(remote, exist_ok=True)
os.chdir(remote)

process = subprocess.Popen(
    ["git", "init", "--bare"],
    universal_newlines=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    encoding="utf-8",
    errors="ignore",
)
stdout, stderr = process.communicate()
process.wait()
p(stdout)
if stderr:
    p(stderr)

cmd = [
    "git",
    "init",
    "&&",
    "git",
    "add",
    ".",
    "&&",
    "git",
    "commit",
    "-m",
    "first commit",
    "&&",
    "git",
    "remote",
    "add",
    "origin",
    remote,
    "&&",
    "git",
    "branch",
    "-M",
    "main",
    "&&",
    "git",
    "push",
    "-u",
    remote,
    "main",
]

p("wwwwwwwwww9")
p(str(cmd))

os.chdir(dir)
process = subprocess.Popen(
    cmd,
    universal_newlines=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    encoding="utf-8",
    errors="ignore",
)
stdout, stderr = process.communicate()
process.wait()
p(stdout)
if stderr:
    p(stderr)
