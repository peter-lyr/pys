import os
import re
from datetime import datetime
from traceback import format_exc

from xpinyin import Pinyin

import b

filename = "06-git-repo-list-3digit-"
git_repo_list_3digit = __import__(filename)
max_num_index = git_repo_list_3digit.get_max_num_index()


def run_print_cmd(cmd):
    print(f"***** {cmd}", flush=True)
    os.system(cmd)


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
        temp = repo.replace("-", ":").replace("，", ",")
        xxx = p.get_initials(temp)
        temp_2 = "-".join(repo.split("-")[1:])
        if has_num_prefix and len(temp_2) <= 3:
            xxx = p.get_pinyin(temp)
        repo = xxx.replace("-", "").replace(":", "-").replace(",", "-").strip()
        repo = re.sub(r"\W+", "_", repo)
        repo_bak = repo
        if num_index_new and num_index != num_index_new:
            if has_num_prefix:
                repo = re.sub(num_index, num_index_new, repo, 1)
            else:
                repo = f"{num_index_new}_{repo}"
        os.chdir(root)
        dir = os.path.join(root, path)
        os.makedirs(dir, exist_ok=True)
        os.chdir(path)
        if os.path.exists(".git"):
            print(f".git exists in {path}", flush=True)
            os._exit(2)
        repos = git_repo_list_3digit.get_all_repos()
        repo_exists = 0
        for r in repos:
            res = re.findall(repo_bak, r)
            b.p(f"{repo_bak} {r}")
            if res:
                repo_exists = 1
                break
        # if repo_exists:  # 不存在仓库
        #     run_print_cmd("git init")
        #     file = datetime.now().strftime("0-%Y%m%d-%H%M%S.txt")
        #     with open(file, "wb") as f:
        #         f.write(b"")
        #     run_print_cmd("git add .")
        #     run_print_cmd('git commit -m "s1"')
        #     run_print_cmd(
        #         f'gh repo create {repo} --{public} --description "{root_tail}/{path}" --source=. --remote=origin'
        #     )
        #     run_print_cmd("git push -u origin main")
        # os.chdir(root)
        # run_print_cmd(f"git submodule add -f git@github.com:{name}/{repo} {path}")
        # run_print_cmd("git add .")
        # run_print_cmd(f'git commit -m "{root_tail}/{path}"')
        # run_print_cmd("git push")
    except:
        print("{{[[{{{xidcwii8}}}]]}}", format_exc(), flush=True)
