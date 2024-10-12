import os
import time
import subprocess
from traceback import format_exc

import b

if __name__ == "__main__":
    try:
        params = b.get_params()
        CommitFile = params[0]
        if not os.path.exists(CommitFile):
            os._exit(1)
        with open(CommitFile, "rb") as file:
            CommitLines = [
                line.strip().decode("utf-8")
                for line in file.readlines()
                if line.strip()
            ]
        if not CommitLines:
            os._exit(2)
        file = params[1]
        opts = params[2:]
        cmd = []
        if "add" in opts:
            cmd += [
                "git",
                "add",
                ".",
                "&&",
            ]
        if "commit" in opts:
            cmd += [
                "git",
                "commit",
                "-F",
                CommitFile,
                "&&",
            ]
        if "push" in opts:
            cmd += [
                "git",
                "push",
                "&&",
            ]
        if cmd and cmd[-1] == "&&":
            cmd = cmd[:-1]
        if not cmd:
            cmd = [
                "git",
                "push",
            ]
        # cmd = ["chcp", "&&", "chcp", "65001", "&&"] + cmd
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
            temp_sss = 3
            for j in range(temp_sss):
                if os.path.exists(os.path.join(dir, ".git", "index.lock")):
                    print(f"{temp_sss - j}...", flush=True)
                    time.sleep(1)
                else:
                    break
            else:
                os._exit(3)
            if dir == Dirs[0]:
                cur_commit_lines = CommitLines
            else:
                last = Dirs[i - 1]
                try:
                    cur_commit_lines = [
                        (f"[{last[len(dir) + 1 :]}]:\n")
                    ] + last_commit_lines
                except:
                    cur_commit_lines = [
                        (f"[{last[len(dir) + 1 :]}]:\n")
                    ] + last_commit_lines
                with open(CommitFile, "w") as file:
                    file.writelines(cur_commit_lines)
            # if "commit" in opts:
            #     print(f"******* {i+1}. *******", flush=True)
            #     print("", flush=True)
            #     for line in cur_commit_lines:
            #         print(line.rstrip(), flush=True)
            #     print("", flush=True)
            #     print("******************", flush=True)
            last_commit_lines = cur_commit_lines
            process = subprocess.Popen(
                cmd,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                encoding="gbk",
                errors="ignore",
            )
            stdout, stderr = process.communicate()
            process.wait()
            print(stdout, flush=True)
            print(stderr, flush=True)
    except:
        e = "wwwwwwwwwwwwwewwwwwwwwww: " + format_exc()
        print("{{[[{{{1ww}}}]]}}", format_exc(), flush=True)
        b.write_err(e.split("\n"))
