import os
import re

from datetime import datetime

from xpinyin import Pinyin

import funcs as f

if __name__ == "__main__":
    try:
        params = f.get_params()
        root = params[0]
        path = params[1]
        public = params[2]
        name = params[3]
        if public not in ['public', 'private']:
            os._exit(3)
        print(root, path)
        if not os.path.exists(root):
            os._exit(1)
        repo = os.path.split(path)[1]
        repo = (
            Pinyin().get_initials(repo.replace("-", ":").replace("，", ","))
            .replace("-", "")
            .replace(":", "-")
            .replace(",", "-")
            .strip()
        )
        repo = re.sub(r"\W+", "_", repo)
        os.chdir(root)
        dir = os.path.join(root, path)
        os.makedirs(dir, exist_ok=True)
        os.chdir(path)
        if os.path.exists('.git'):
            os._exit(2)
        os.system('git init')
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(f'01-初次提交-{timestamp}.txt', 'wb') as f:
            f.write(b'')
        os.system('git add .')
        os.system('git commit -m "s1"')
        os.system(f'gh repo create {repo} --{public} --source=. --remote=origin')
        os.system('git push -u origin main')
        os.chdir(root)
        os.system(f'git submodule add git@github.com:{name}/{repo} {path}')
        os.system('git add .')
        os.system(f'git commit -m "{path}"')
        os.system('git push')
    except Exception as e:
        print(e, flush=True)
