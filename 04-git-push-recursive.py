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
        with open(CommitFile, 'rb') as f:
            Commit = f.read().decode('utf-8').strip()
        if not Commit:
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
        lastcommit = ''
        for i in range(len(Dirs)):
            dir = Dirs[i]
            print("-" * len(dir))
            print(dir, flush=True)
            os.chdir(dir)
            if dir == Dirs[0]:
                commit = Commit
            else:
                last = Dirs[i - 1]
                commit = last[len(dir) + 1 :] + '->' + lastcommit
            lastcommit = commit
            print("Commit info:", commit, flush=True)
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
        e = 'wwwwwwwwwwwwwewwwwwwwwwww: ' + format_exc()
        print('{{[[{{{1ww}}}]]}}', format_exc(), flush=True)
        f.write_err(e.split('\n'))
