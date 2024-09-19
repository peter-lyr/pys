import os
import time

import funcs as f

submodule_pull_or_clone_py = "submodule-pull-or-clone.py"

D = []

# def submodules(dir):
#     if dir in D:
#         return
#     print("===== START ======")
#     print(dir)
#     dirs = [os.path.join(dir, d) for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
#     dirs.append(dir)
#     for d in dirs:
#         print(d)
#     print("===== END ======")
#     for d in dirs:
#         # t = os.path.join(dir, d)
#         # if os.path.isdir(t):
#         #     submodules(t)
#         temp = os.path.join(d, submodule_pull_or_clone_py)
#         if os.path.exists(temp) and d not in D:
#             D.append(d)
#             cmd = f'cd /d "{d}" && {submodule_pull_or_clone_py}'
#             print(cmd)
#             os.system(cmd)
#             for i in os.listdir(d):
#                 submodules(os.path.join(d, i))
#         submodules(os.path.join(dir, d))

D = []
T = []

def test(dir):
    if dir in T:
        return
    T.append(dir)
    dirs = []
    for d in os.listdir(dir):
        d = os.path.join(dir, d)
        if os.path.isdir(d):
            dirs.append(d)
    dirs.append(dir)
    for d in dirs:
        print(d)
        temp = os.path.join(d, submodule_pull_or_clone_py)
        if os.path.exists(temp) and d not in D:
            D.append(d)
            cmd = f'cd /d "{d}" && {submodule_pull_or_clone_py}'
            print("++++++++++++++++++++++++++")
            print(cmd)
            os.system(cmd)
            time.sleep(0.5)
            for _d in os.listdir(d):
                _d = os.path.join(dir, _d)
                if os.path.isdir(_d):
                    print(_d)
                    test(_d)
            print("++++++++++++++++++++++++++")
        test(d)
        # T.append(d)


def clone(cwd, name, repo, dir):
    cmd = f'cd /d "{cwd}" && git clone git@github.com:{name}/{repo} {dir}'
    print(cmd)
    os.system(cmd)
    # submodules(os.path.join(cwd, dir))
    # test(os.path.join(cwd, dir))
    # print(fr"python C:\Users\llydr\AppData\Local\nvim\pys\01-2-git-submodules.py {os.path.join(cwd, dir)}")
    os.system(fr"python C:\Users\llydr\AppData\Local\nvim\pys\01-2-git-submodules.py {os.path.join(cwd, dir)}")


if __name__ == "__main__":
    params = f.get_params()
    try:
        root, name, repo, dir = params[0], params[1], params[2], params[3]
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)
        clone(root, name, repo, dir)
    except Exception as e:
        print(e)
    os.system('pause')
