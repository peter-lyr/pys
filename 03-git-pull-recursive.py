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
                F.append(rep(os.path.join(r, file)))
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
    global clone_when_empty
    sub, repo, url = subrepo
    if os.path.exists(repo) and os.path.exists(rep(os.path.join(repo, '.git'))):
        os.chdir(repo)
        print(f'pulling: {repo}', flush=True)
        os.system("git pull")
    else:
        if not clone_when_empty:
            return
        print(f'cloning: {repo}', flush=True)
        os.chdir(rep(sub))
        try:
            shutil.rmtree(repo)
        except:
            pass
        os.system(f"git clone {url} {repo} && git checkout main")


def rep(text):
    return text.replace("/", "\\")


if __name__ == "__main__":
    global clone_when_empty
    try:
        params = b.get_params()
        root = params[0]
        clone_when_empty = params[1]
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
                repo = rep(os.path.dirname(dotgitmodule))
                os.chdir(repo)
                repos = [rep(os.path.join(repo, path)) for path in paths]
                repos.append(repo)
                for repo in repos:
                    if repo in Repos:
                        continue
                    if not os.path.exists(repo):
                        continue
                    print(f"{repo}", flush=True)
                    os.chdir(repo)
                    os.system(f"git checkout main")
                    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
                    os.system(f'git stash push -m "{dt}"')
                    os.chdir(repo)
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
