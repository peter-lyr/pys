import os
import re
import subprocess
from traceback import format_exc

import b

if __name__ == "__main__":
    try:
        params = b.get_params()
        root = params[0]
        os.chdir(root)
        bash_cmd = r"""gh repo list --limit 9999999 --json name,description --jq '.[] | "\(.name)\t\t\t\t\t\(.description)"'"""
        result = subprocess.run(
            ["bash.exe", "-c", bash_cmd],
            capture_output=True,
            text=True,
        )
        try:
            repos = result.stdout.replace("\r", "").split("\n")
        except:
            result = subprocess.run(
                [
                    "gh",
                    "repo",
                    "list",
                    "--limit",
                    "9999999",
                    "--source",
                    "--json",
                    "name",
                    "--jq",
                    ".[] | select(.name) | .name",
                ],
                universal_newlines=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        repos = result.stdout.replace("\r", "").split("\n")
        R = []
        L = []
        for repo in repos:
            if re.match(r"^\d{3}[_-]", repo):
                R.append(repo)
            else:
                L.append(repo)
        R.sort(reverse=True)
        for r in R:
            print(r)
        print("-----------------")
        for l in L:
            print(l)
    except:
        print("{{[[{{{owi2ww}}}]]}}", format_exc(), flush=True)
