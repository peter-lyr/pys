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
            print("=====================")
            dir = Dirs[i]
            print(dir, flush=True)
            os.chdir(dir)
            if dir == Dirs[0]:
                commit = Commit
            else:
                last = Dirs[i-1]
                commit = last[len(dir)+1:]
            process = subprocess.Popen(
                [
                    "git",
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
                shell=True,
                text=True,
            )
            process.wait()
    except Exception as e:
        print(e, flush=True)
