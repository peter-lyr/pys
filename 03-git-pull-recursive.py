import os
import re
import shutil
import time
from datetime import datetime
from multiprocessing import Pool
from traceback import format_exc

import b

test_txt = r"C:\Windows\Temp\23sxi.txt"


def p(text):
    try:
        for line in text.strip().replace("\r", "").split("\n"):
            line = line.strip()
            if line:
                with open(test_txt, "wb") as f:
                    f.write(line.encode("utf-8"))
                os.system(f"chcp 65001>nul & cat {test_txt} & echo.")
            else:
                os.system("chcp 65001>nul & echo.")
    except Exception as e:
        print(f"echo {text}", flush=True)
        print(e, "][]]]]]]]]]]]")


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


def git_pull(subrepo_clone_when_empty):
    subrepo, clone_when_empty = subrepo_clone_when_empty
    sub, repo, url = subrepo
    if os.path.exists(repo) and os.path.exists(rep(os.path.join(repo, ".git"))):
        os.chdir(repo)
        p(f" ==== pulling: {repo}")
        os.system("git pull")
    else:
        if not clone_when_empty:
            return
        p(f" ++++ cloning: {repo}")
        os.chdir(rep(sub))
        try:
            shutil.rmtree(repo)
        except:
            pass
        os.system(f"git clone {url} {repo} && git checkout main")


def rep(text):
    return text.replace("/", "\\")


if __name__ == "__main__":
    try:
        params = b.get_params()
        root = params[0]
        try:
            clone_when_empty = params[1]
        except:
            clone_when_empty = False
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
                    p(f"{repo}")
                    os.chdir(repo)
                    os.system(f"git checkout main")
                    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
                    os.system(f'git stash push -m "{dt}"')
                    os.chdir(repo)
                os.chdir(rep(temp))
                for repo, url in zip(repos, urls):
                    if repo not in Repos:
                        Repos.append(repo)
                        SubRepos.append(
                            [
                                [os.path.split(dotgitmodule)[0], repo, url],
                                clone_when_empty,
                            ]
                        )
        os.chdir(root)
        p(f" ==== pulling: {root}")
        os.system("git pull")
        if 0:
            for subrepo_clone_when_empty in SubRepos:
                git_pull(subrepo_clone_when_empty)
        else:
            with Pool() as pool:
                pool.map(git_pull, SubRepos)
    except:
        print("{{[[{{{xkdjsd3w}}}]]}}", format_exc(), flush=True)
