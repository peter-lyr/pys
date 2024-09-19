import os

import funcs as f

submodule_pull_or_clone_py = "submodule-pull-or-clone.py"

def test(dir):
    print(dir)


if __name__ == "__main__":
    params = f.get_params()
    try:
        root = params[0]
        test(root)
    except Exception as e:
        print(e)
    os.system('pause')
