import os
import shutil
import re
import time
from datetime import datetime
from multiprocessing import Pool
from traceback import format_exc

import b

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


def git_pull(subrepo):
    sub, repo, url = subrepo
    if os.path.exists(repo) and os.path.exists(os.path.join(repo, '.git')):
        os.chdir(rep(repo))
        print(f'pulling: {rep(repo)}')
        os.system("git pull")
    else:
        print(f'cloning: {rep(repo)}')
        os.chdir(rep(sub))
        shutil.rmtree(rep(repo))
        os.system(f"git clone {url} {repo}")


def rep(text):
    return text.replace("/", "\\")


if __name__ == "__main__":
    try:
        root = b.get_params()[0]
        if not os.path.exists(root) or not os.path.exists(os.path.join(root, ".git")):
            os._exit(1)
        dotgitmodules = get_gitmodules(root)
        dotgitmodules_from_leaves_to_root = level_gitmodules(dotgitmodules)
        time.sleep(1)
        Repos = []
        SubRepos = []
        for dotgitmodules in dotgitmodules_from_leaves_to_root:
            for dotgitmodule in dotgitmodules:
                temp = os.getcwd()
                paths, urls = get_path_url(dotgitmodule)
                repo = os.path.dirname(dotgitmodule)
                os.chdir(rep(repo))
                repos = [os.path.join(repo, path) for path in paths]
                repos.append(repo)
                for repo in repos:
                    if repo in Repos:
                        continue
                    if not os.path.exists(repo):
                        continue
                    print(f"{repo}", flush=True)
                    os.chdir(rep(repo))
                    os.system(f"git checkout main")
                    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
                    os.system(f'git stash push -m "{dt}"')
                    os.chdir(rep(repo))
                os.chdir(rep(temp))
                for repo, url in zip(repos, urls):
                    if repo not in Repos:
                        Repos.append(repo)
                        SubRepos.append([os.path.split(dotgitmodule)[0], repo, url])
        if 1:
            for subrepo in SubRepos:
                git_pull(subrepo)
        else:
            with Pool() as pool:
                pool.map(git_pull, SubRepos)
    except:
        print("{{[[{{{xkdjsd3w}}}]]}}", format_exc(), flush=True)
