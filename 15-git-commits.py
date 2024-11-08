import sys
import time

import b
import os

dir = file = sys.argv[1]

if not os.path.exists(file):
    os._exit(1)
elif os.path.isfile(file):
    dir = os.path.dirname(file)
    while 1:
        if os.path.exists(os.path.join(dir, ".git")):
            print(dir)
            os.chdir(dir)
            _, output = b.get_sta_output(["git", "rev-list", "--all", "--count"], True)
            print(output[0])
        bak = dir
        dir = os.path.dirname(dir)
        if bak == dir:
            break
elif os.path.isdir(file):
    # print(dir)
    dot_git = os.path.join(dir, ".git")
    repos = []
    if os.path.exists(dot_git):
        repos = [dir]
    for R, D, F in os.walk(dir):
        for d in D:
            d_full = os.path.join(R, d)
            dot_git = os.path.join(d_full, ".git")
            if os.path.exists(dot_git):
                repos.append(d_full)
    l = len(repos)
    for i, repo in enumerate(repos):
        os.chdir(repo)
        _, output = b.get_sta_output(["git", "rev-list", "--all", "--count"], True)
        if output:
            b.p(repo)
            b.p("-> " + output[0])

# time.sleep(3)
