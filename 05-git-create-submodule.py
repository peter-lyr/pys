import os
import re
from datetime import datetime
from traceback import format_exc

from xpinyin import Pinyin

import b


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
        print(root, path, flush=True)
        if not os.path.exists(root):
            print(f"{root} not exists", flush=True)
            os._exit(1)
        repo = os.path.split(path)[1]
        p = Pinyin()
        temp = repo.replace("-", ":").replace("，", ",")
        xxx = p.get_initials(temp)
        # 026-富友昌
        temp_2 = "-".join(repo.split("-")[1:])
        if len(temp_2) <= 3:
            xxx = p.get_pinyin(temp)
        repo = xxx.replace("-", "").replace(":", "-").replace(",", "-").strip()
        repo = re.sub(r"\W+", "_", repo)
        os.chdir(root)
        dir = os.path.join(root, path)
        os.makedirs(dir, exist_ok=True)
        os.chdir(path)
        if os.path.exists(".git"):
            print(f".git exists in {path}", flush=True)
            os._exit(2)
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
        run_print_cmd(f"git submodule add -f git@github.com:{name}/{repo} {path}")
        run_print_cmd("git add .")
        run_print_cmd(f'git commit -m "{root_tail}/{path}"')
        run_print_cmd("git push")
    except:
        print("{{[[{{{xidcwii8}}}]]}}", format_exc(), flush=True)
