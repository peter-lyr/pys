import os
import re
import subprocess

import funcs as f

if __name__ == "__main__":
    try:
        params = f.get_params()
        root = params[0]
        os.chdir(root)
        bash_cmd = r"""gh repo list --limit 9999999 --json name,description --jq '.[] | "\(.name)\t\t\t\t\t\(.description)"'"""
        result = subprocess.run(
            ["bash.exe", "-c", bash_cmd],
            capture_output=True,
            text=True,
        )
        repos = result.stdout.replace("\r", "").split("\n")
        R = []
        for repo in repos:
            # if re.match(r"^\d{3}[_-]", repo):
                R.append(repo)
        R.sort(reverse=True)
        for r in R:
            print(r)
    except Exception as e:
        print(e, flush=True)
