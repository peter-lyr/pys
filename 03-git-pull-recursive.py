import multiprocessing
import os

# import sys
import re
import shutil
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


def pp(txt):
    with multiprocessing.Lock():
        b.p(txt)


temp_dir = "C:\\Windows\\Temp\\git-pull-recursive\\"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)


def run_outside(cmd, py):
    py = re.sub(r"[^\w\d_]", "_", py)
    py = temp_dir + py + ".py"
    with open(py, "wb") as f:
        f.write(cmd.strip().encode("utf-8"))
    # os.system(f"""start cmd /c "{py} & pause" """)
    os.system(f"""start /min cmd /c "{py}" """)


def git_pull(subrepo_clone_when_empty):
    subrepo, clone_when_empty = subrepo_clone_when_empty
    sub, repo, url = subrepo

    pulling = 1 if os.path.exists(repo) else 0
    if pulling:
        pulling *= 1 if os.path.exists(rep(os.path.join(repo, ".git"))) else 0
    if pulling:
        files = os.listdir(repo)
        pulling *= 1 if len(files) >= 2 else 0
    if pulling:
        run_outside(
            f"""
import os
try:
    print(rf" ==== pulling: {repo}")
    os.chdir(r'''{repo}''')
    os.system(rf"git pull")
except Exception as e:
    print("==========================error==========================")
    print(e)
    print("==========================error end =====================")
            """,
            repo,
        )
    else:
        if not clone_when_empty:
            return
        pp(f" ++++ cloning: {repo}")
        run_outside(
            f"""
import os
import time
import shutil
os.chdir(r'''{sub}''')
if os.path.exists(r'''{repo}'''):
    for i in range(100):
        try:
            shutil.rmtree(r'''{repo}''')
            break
        except Exception as e:
            print("==========================error==========================")
            print(e)
            print("==========================error end =====================")
            time.sleep(0.1)
os.system(rf"git clone {url} {repo} && git checkout main")
            """,
            repo,
        )


def rep(text):
    return text.replace("/", "\\")


if __name__ == "__main__":
    try:
        params = b.get_params()
        root = params[0]
        clone_when_empty = 0 if params[1] == "no" else 1
        checkout = 0 if params[2] == "no" else 1
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
                if checkout:
                    for repo in repos:
                        if repo in Repos:
                            continue
                        if not os.path.exists(repo):
                            continue
                        b.p(f"{repo}")
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
        b.p(f" ==== pulling: {root}")
        os.system("git pull")
        if 0:
            for subrepo_clone_when_empty in SubRepos:
                git_pull(subrepo_clone_when_empty)
        else:
            with Pool(processes=(os.cpu_count() or 2) * 2) as pool:
                pool.map(git_pull, SubRepos)
    except:
        print("{{[[{{{xkdjsd3w}}}]]}}", format_exc(), flush=True)
