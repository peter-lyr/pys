import os
from traceback import format_exc
import re
from datetime import datetime

from xpinyin import Pinyin

import b

if __name__ == "__main__":
    try:
        params = b.get_params()
        root = params[0]
        path = params[1]
        public = params[2]
        name = params[3]
        root_tail = os.path.split(root)[1]
        if public not in ["public", "private"]:
            print('public not in ["public", "private"]')
            os._exit(3)
        print(root, path)
        if not os.path.exists(root):
            print(f'{root} not exists')
            os._exit(1)
        repo = os.path.split(path)[1]
        p = Pinyin()
        temp = repo.replace("-", ":").replace("，", ",")
        xxx = p.get_initials(temp)
        # 026-富友昌
        temp_2 = '-'.join(repo.split('-')[1:])
        if len(temp_2) <= 3:
            xxx = p.get_pinyin(temp)
        repo = xxx.replace("-", "").replace(":", "-").replace(",", "-").strip()
        repo = re.sub(r"\W+", "_", repo)
        os.chdir(root)
        dir = os.path.join(root, path)
        os.makedirs(dir, exist_ok=True)
        os.chdir(path)
        if os.path.exists(".git"):
            print(f'.git exists in {path}')
            os._exit(2)
        os.system("git init")
        file = datetime.now().strftime("%Y%m%d-01-s1-%H%M%S.txt")
        with open(file, "wb") as f:
            f.write(b"")
        os.system("git add .")
        os.system('git commit -m "s1"')
        os.system(
            f'gh repo create {repo} --{public} --description "{root_tail}/{path}" --source=. --remote=origin'
        )
        os.system("git push -u origin main")
        os.chdir(root)
        os.system(f"git submodule add git@github.com:{name}/{repo} {path}")
        os.system("git add .")
        os.system(f'git commit -m "{root_tail}/{path}"')
        os.system("git push")
    except:
        print("{{[[{{{xidcwii8}}}]]}}", format_exc(), flush=True)
