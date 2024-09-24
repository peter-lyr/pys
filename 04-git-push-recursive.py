import os
import subprocess

import funcs as f

if __name__ == "__main__":
    try:
        params = f.get_params()
        Commit = params[0]
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
        for i in range(len(Dirs)):
            dir = Dirs[i]
            print("-" * len(dir))
            print("Commit info:", dir, flush=True)
            os.chdir(dir)
            if dir == Dirs[0]:
                commit = Commit
            else:
                last = Dirs[i - 1]
                commit = last[len(dir) + 1 :]
            print(commit, flush=True)
            process = subprocess.Popen(
                [
                    "cd",
                    "/d",
                    dir,
                    "&&" "git",
                    "add",
                    ".",
                    "&&",
                    "git",
                    "commit",
                    "-m",
                    commit,
                    "&&",
                    "git",
                    "push",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                encoding="utf-8",
            )
            stdout, stderr = process.communicate()
            process.wait()
            print(stdout, flush=True)
            print(stderr, flush=True)
    except Exception as e:
        print(e, flush=True)
