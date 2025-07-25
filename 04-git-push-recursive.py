import os
import subprocess
import time
from traceback import format_exc

import b

single_file_max_size = 500 * 1024 * 1024
one_push_max_size = 500 * 1024 * 1024


if __name__ == "__main__":
    try:
        params = b.get_params()
        CommitFile = params[0]
        if not os.path.exists(CommitFile):
            os._exit(1)
        with open(CommitFile, "rb") as file:
            CommitLines = [line.strip() for line in file.readlines() if line.strip()]
        if not CommitLines:
            os._exit(2)
        file = params[1]
        opts = params[2:]
        cmd = []
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
        add_all = 1
        untracked_files = []
        sta = 0
        if Dirs:
            fsize, untracked_files = b.get_untracked_file_size(Dirs[0])
            for untracked_file in untracked_files:
                if os.path.getsize(untracked_file) > single_file_max_size:
                    b.split_big_file(untracked_file, single_file_max_size)
            fsize, untracked_files = b.get_untracked_file_size(Dirs[0])
            if fsize > 0:
                b.p(f"{fsize} untracked files size of:")
            if fsize > one_push_max_size:
                b.p(f"{Dirs[0]}\n Is more than {one_push_max_size/1024/1024}MB.")
                add_all = 0
                # os._exit(4)
        if add_all:
            if "add" in opts:
                temp = [
                    "git",
                    "add",
                    ".",
                    "&&",
                ]
                cmd = temp + cmd
        else:
            if "add" in opts:
                temp = [
                    "git",
                    "add",
                ]
                new_untracked_files = []
                for untracked_file in untracked_files:
                    if ".gitignore" == os.path.split(untracked_file)[-1].lower():
                        b.p(".gitignore: " + untracked_file)
                        temp = ["git", "add", untracked_file, "&&"] + temp
                        break
                size = 0
                for untracked_file in untracked_files:
                    size += os.path.getsize(untracked_file)
                    if size > one_push_max_size:
                        break
                    if untracked_file not in new_untracked_files:
                        new_untracked_files.append(untracked_file)
                temp += new_untracked_files
                for new_untracked_file in new_untracked_files:
                    b.p(new_untracked_file)
                temp += [
                    "&&",
                ]
                cmd = temp + cmd
                sta = 234
        cmd = ["chcp", "65001>nul", "&&"] + cmd
        for i in range(len(Dirs)):
            dir = Dirs[i]
            os.chdir(dir)
            _, output = b.get_sta_output(["git", "rev-list", "--all", "--count"], True)
            b.p(f"""{"-" * len(dir)} [{int(output[0])+1}] commits""")
            b.p(dir)
            temp_sss = 20
            for j in range(temp_sss):
                lock = os.path.join(dir, ".git", "index.lock")
                if os.path.exists(lock):
                    try:
                        os.remove(lock)
                    except:
                        pass
                    b.p(f"{temp_sss - j} .git/index.lock exist")
                    time.sleep(1)
                else:
                    break
            else:
                os._exit(3)
            if dir == Dirs[0]:
                cur_commit_lines = CommitLines
            else:
                last = Dirs[i - 1]
                cur_commit_lines = [
                    (f"[{last[len(dir) + 1 :]}]:\n").encode("utf-8")
                ] + last_commit_lines
                with open(CommitFile, "wb") as file:
                    file.writelines(cur_commit_lines)
            # if "commit" in opts:
            #     print(f"******* {i+1}. *******", flush=True)
            #     print("", flush=True)
            #     for line in cur_commit_lines:
            #         print(line.rstrip().decode("utf-8"), flush=True)
            #     print("", flush=True)
            #     print("******************", flush=True)
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
            b.p(stdout)
            if stderr:
                b.p(stderr)
        os._exit(sta)
    except:
        e = "wwwwwwwwwwwwwewwwwwwwwwww: " + format_exc()
        print("{{[[{{{1ww}}}]]}}", format_exc(), flush=True)
        b.write_err(e.split("\n"))
