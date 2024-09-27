import os
import subprocess
from traceback import format_exc

import funcs as f

if __name__ == "__main__":
    try:
        params = f.get_params()
        CommitFile = params[0]
        if not os.path.exists(CommitFile):
            os._exit(1)
        cmd = [
            "git",
            "add",
            ".",
            "&&",
            "git",
            "commit",
            "-F",
            CommitFile,
            "&&",
            "git",
            "push",
        ]
        with open(CommitFile, "rb") as file:
            CommitLines = [line.strip() for line in file.readlines()]
        if not CommitLines:
            os._exit(2)
        file = params[1]
        parent = file
        if os.path.isfile(parent):
            parent = os.path.split(file)[0]
        Dirs = []
        while 1:
            dot_git = os.path.join(parent, ".git")
            if os.path.exists(dot_git):
                Dirs.append(parent)
            temp = os.path.split(parent)[0]
            if temp == parent:
                break
            parent = temp
        last_commit_lines = []
        for i in range(len(Dirs)):
            dir = Dirs[i]
            print("-" * len(dir))
            print(dir, flush=True)
            os.chdir(dir)
            if dir == Dirs[0]:
                cur_commit_lines = CommitLines
            else:
                last = Dirs[i - 1]
                cur_commit_lines = [(last[len(dir) + 1 :] + "===>\n").encode("utf-8")] + last_commit_lines
                with open(CommitFile, "wb") as file:
                    file.writelines(cur_commit_lines)
            print("Commit info:\n", flush=True)
            for line in cur_commit_lines:
                print(line.rstrip().decode('utf-8'), flush=True)
            last_commit_lines = cur_commit_lines
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
            print(stdout, flush=True)
            print(stderr, flush=True)
    except:
        e = "wwwwwwwwwwwwwewwwwwwwwwww: " + format_exc()
        print("{{[[{{{1ww}}}]]}}", format_exc(), flush=True)
        f.write_err(e.split("\n"))
