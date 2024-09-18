import os

import funcs as f


def clone(cwd, name, repo, dir):
    cmd = f'cd /d "{cwd}" && git clone git@github.com:{name}/{repo} {dir}'
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    params = f.get_params()
    try:
        root, name, repo, dir = params[0], params[1], params[2], params[3]
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)
        clone(root, name, repo, dir)
    except Exception as e:
        print(e)
    os.system("pause")
