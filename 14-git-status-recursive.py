import sys
import time

import b
import os

root = sys.argv[1]

# print(root)
repos = [root]
for R, D, F in os.walk(root):
    for d in D:
        d_full = os.path.join(R, d)
        dot_git = os.path.join(d_full, ".git")
        if os.path.exists(dot_git):
            repos.append(d_full)
for repo in repos:
    print("=" * len(repo))
    print(repo)
    os.chdir(repo)
    _, output = b.get_sta_output(["git", "status", "-s"])
# print(output)

# time.sleep(3)
