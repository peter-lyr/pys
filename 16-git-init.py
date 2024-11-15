import os
import subprocess
import sys
import time

import b

dir = file = sys.argv[1]
git_fake_remote_dir = file = sys.argv[2]

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
b.p(stdout)
if stderr:
    b.p(stderr)

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

# b.p("wwwwwwwwww9")
# b.p(str(cmd))

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
b.p(stdout)
if stderr:
    b.p(stderr)
