import os
import re
import time
from multiprocessing import Pool

import funcs as f


def get_gitmodules(root):
    F = []
    for r, _, files in os.walk(root):
        for file in files:
            ## if file == "submodule-pull-or-clone.py":
            if file == ".gitmodules":
                F.append(os.path.join(r, file))
    return F


def level_gitmodules(dotgitmodules):
    new = {}
    for gitmodule in dotgitmodules:
        level = len(gitmodule.replace("/", "\\").split("\\"))
        if level not in new:
            new[level] = []
        new[level].append(gitmodule)
    levels = new.keys()
    dotgitmodules_from_leaves_to_root = []
    for level in sorted(levels, reverse=True):
        dotgitmodules_from_leaves_to_root.append(new[level])
    return dotgitmodules_from_leaves_to_root


def get_path_url(dotgitmodules):
    with open(dotgitmodules, "rb") as f:
        lines = f.readlines()
    paths = []
    urls = []
    for line in lines:
        line = line.strip()
        res = re.findall(b"path = (.+)", line)
        if res:
            res = res[0]
            paths.append(res.decode("utf-8"))
        else:
            res = re.findall(b"url = (.+)", line)
            if res:
                res = res[0]
                urls.append(res.decode("utf-8"))
    return paths, urls


def git_pull(repo):
    print(repo, flush=True)
    os.chdir(repo)
    os.system("git pull")


if __name__ == "__main__":
    try:
        root = f.get_params()[0]
        if not os.path.exists(root) or not os.path.exists(os.path.join(root, ".git")):
            os._exit(1)
        dotgitmodules = get_gitmodules(root)
        dotgitmodules_from_leaves_to_root = level_gitmodules(dotgitmodules)
        time.sleep(1)
        Repos = []
        for dotgitmodules in dotgitmodules_from_leaves_to_root:
            for dotgitmodule in dotgitmodules:
                temp = os.getcwd()
                paths, urls = get_path_url(dotgitmodule)
                repo = os.path.dirname(dotgitmodule)
                os.chdir(repo)
                repos = [os.path.join(repo, path) for path in paths]
                repos.append(repo)
                for repo in repos:
                    if repo in Repos:
                        continue
                    print(f"\033[1;32m{repo}\033[0m", flush=True)
                    os.chdir(repo)
                    os.system(f"git checkout main")
                    os.chdir(repo)
                os.chdir(temp)
                for repo in repos:
                    if repo not in Repos:
                        Repos.append(repo)
        if 0:
            for repo in Repos:
                git_pull(repo)
        else:
            with Pool() as pool:
                pool.map(git_pull, Repos)
    except Exception as e:
        print(e, flush=True)