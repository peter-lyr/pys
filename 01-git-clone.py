import os
import time

import funcs as f

submodule_pull_or_clone_py = "submodule-pull-or-clone.py"

def test(root):
    print('===============')
    print(root)
    print('===============')
    temp = os.path.join(root, submodule_pull_or_clone_py)
    if os.path.exists(temp):
        cmd = f'cd /d "{root}" && python {temp}'
        print("++++++++++++++++++++++")
        print(cmd)
        print("++++++++++++++++++++++")
        os.system(cmd)
    for i in range(4):
        print(f'sleep {4-i}s...')
        time.sleep(1)
    for dir in os.listdir(root):
        if dir not in ['.git']:
            temp = os.path.join(root, dir)
            if os.path.isdir(temp):
                test(temp)


def clone(cwd, name, repo, dir):
    cmd = f'cd /d "{cwd}" && git clone git@github.com:{name}/{repo} {dir}'
    print(cmd)
    os.system(cmd)
    test(os.path.join(cwd, dir))


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
