import os
import time
import shutil
import itertools
import re
from datetime import datetime
from traceback import format_exc

from xpinyin import Pinyin

import b

filename = "06-git-repo-list-3digit-"
git_repo_list_3digit = __import__(filename)
max_num_index = git_repo_list_3digit.get_max_num_index()


def run_print_cmd(cmd):
    b.p(f"***** {cmd}")
    # print(f"***** {cmd}")
    os.system(cmd)


def get_permutations(arr):
    result = []
    for perm in itertools.permutations(arr):
        result.append(perm)
    return result


def get_multi_repo(repo):
    # 8936T，内部，fot单备份升级
    # 返回
    # 内部，8936T，fot单备份升级
    # 内部，fot单备份升级，8936T
    # 等等
    temp_l = repo.split("，")
    temp_a = get_permutations(temp_l)
    # b.p(str(temp_a))
    if not temp_a:
        return []
    temp_a = list(temp_a)
    temp_b = []
    for i in temp_a:
        # b.p(str(i) + "=-=========" + repo)
        if i != repo:
            temp_b.append(i)
    return ["，".join(i) for i in list(temp_b)]


def get_w_repo(repo):
    temp = repo.replace("-", ":").replace("，", ",")
    xxx = p.get_initials(temp)
    temp_2 = "-".join(repo.split("-")[1:])
    if has_num_prefix and len(temp_2) <= 3:
        xxx = p.get_pinyin(temp)
    repo = xxx.replace("-", "").replace(":", "-").replace(",", "-").strip()
    repo = re.sub(r"\W+", "_", repo)
    return repo


def get_repo_pinyin(repo, num_index_new, num_index, has_num_prefix):
    if num_index_new and num_index != num_index_new:
        if has_num_prefix:
            repo = re.sub(num_index, num_index_new, repo, 1)
        else:
            repo = f"{num_index_new}_{repo}"
        return repo
    return None


if __name__ == "__main__":
    try:
        params = b.get_params()
        root = params[0]
        path = params[1]
        public = params[2]
        name = params[3]
        root_tail = os.path.split(root)[1]
        if public not in ["public", "private"]:
            print('public not in ["public", "private"]', flush=True)
            os._exit(3)
        if not os.path.exists(root):
            print(f"{root} not exists", flush=True)
            os._exit(1)
        repo = os.path.split(path)[1]
        num_index = repo.split("_")[0].split("-")[0]
        has_num_prefix = 0
        try:
            temp_index = int(num_index)
            if temp_index < int(max_num_index):
                temp_index = int(max_num_index) + 1
            num_index_new = str(temp_index)
            has_num_prefix = 1
        except Exception as e:
            # print(e)
            temp_index = int(max_num_index) + 1
            num_index_new = str(temp_index)
        p = Pinyin()
        repo_bak_ori = repo
        repo = get_w_repo(repo)
        repo_bak = repo
        temp__ = get_repo_pinyin(repo, num_index_new, num_index, has_num_prefix)
        if temp__:
            repo = temp__
        os.chdir(root)
        repo_dir_path = os.path.join(root, path)
        os.makedirs(repo_dir_path, exist_ok=True)
        os.chdir(repo_dir_path)
        if os.path.exists(".git"):
            b.p(f".git exists in {path}")
            os._exit(2)
        repos = git_repo_list_3digit.get_all_repos()
        repo_exists = 0
        for r in repos:
            res = re.findall(repo_bak, r)
            # b.p(f"{repo_bak} {r}")
            if res:
                repo_exists = 1
                repo = r
                b.p("++++++++++++++++")
                break
        if not repo_exists:  # 不存在仓库
            multi_repo_names = get_multi_repo(repo_bak_ori)
            # b.p(str(multi_repo_names))
            to_break = 0
            for r in repos:
                # b.p(f"{r}==")
                for bak in multi_repo_names:
                    bak = get_w_repo(bak)
                    res = re.findall(bak, r)
                    # b.p(f"{bak} {r}")
                    if res:
                        repo_exists = 1
                        repo = r
                        b.p("################")
                        to_break = 1
                        break
                if to_break:
                    break
        if not repo_exists:  # 不存在仓库
            os.chdir(repo_dir_path)
            run_print_cmd("git init")
            file = datetime.now().strftime("0-%Y%m%d-%H%M%S.txt")
            with open(file, "wb") as f:
                f.write(b"")
            run_print_cmd("git add .")
            run_print_cmd('git commit -m "s1"')
            run_print_cmd(
                f'gh repo create {repo} --{public} --description "{root_tail}/{path}" --source=. --remote=origin'
            )
            run_print_cmd("git push -u origin main")
        os.chdir(root)
        temp_e = os.path.join(root, path)
        for i in range(20):
            # b.p(os.path.join(root, path) + ":" + str(i) + "--------------")
            shutil.rmtree(temp_e)
            if not os.path.exists(temp_e):
                break
            time.sleep(1)
        run_print_cmd(f"git submodule add -f git@github.com:{name}/{repo} {path}")
        if repo_exists:
            os.chdir(root)
        run_print_cmd("pwd")
        run_print_cmd("git add .")
        run_print_cmd(f'git commit -m "{root_tail}/{path}"')
        run_print_cmd("git push")
    except:
        print("{{[[{{{xidcwii8}}}]]}}", format_exc(), flush=True)
