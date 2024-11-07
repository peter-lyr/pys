import sys
import time

import b
import os

root = sys.argv[1]

# print(root)
dot_git = os.path.join(root, ".git")
dot_gitmodules = os.path.join(root, ".gitmodules")
repos = []
if os.path.exists(dot_git) and not os.path.exists(dot_gitmodules):
    repos = [root]
for R, D, F in os.walk(root):
    for d in D:
        d_full = os.path.join(R, d)
        dot_git = os.path.join(d_full, ".git")
        dot_gitmodules = os.path.join(d_full, ".gitmodules")
        if os.path.exists(dot_git) and not os.path.exists(dot_gitmodules):
            # print(dot_gitmodules)
            repos.append(d_full)
l = len(repos)
for i, repo in enumerate(repos):
    os.chdir(repo)
    _, output = b.get_sta_output(["git", "status", "-s"], True)
    if output:
        b.p(str(i + 1) + ".")
        b.p(repo)
        for line in output:
            b.p(line)
        b.p("-" * len(repo))

# time.sleep(3)
