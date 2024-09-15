import os
from multiprocessing import Pool

import funcs as f


def clone(cwd, name, repo):
    cmd = f'cd /d "{cwd}" && git clone --recursive git@github.com:{name}/{repo}'
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    params = f.get_params()
    try:
        root, name, repos = params[0], params[1], params[2:]
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)
        if len(repos) > 1:
            p = Pool(4)
            for repo in repos:
                p.apply_async(clone, args=(root, name, repo))
            p.close()
            p.join()
        else:
            clone(root, name, repos[0])
    except Exception as e:
        print(e)
    os.system("pause")
