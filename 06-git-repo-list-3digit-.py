import os
import re
import subprocess
from traceback import format_exc

import b


def purify(lines):
    A = []
    B = []
    for line in lines:
        temp = line.split("\t\t\t\t\t")
        # print(temp, len(temp))
        if len(temp) >= 2:
            A.append(temp[0])
            B.append(temp[1])
    m = max([len(n) for n in A])
    t = f"{{:<{m}}} {{}}"
    L = []
    for a, b in zip(A, B):
        L.append(t.format(a, b))
    for l in L:
        print(l)


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
        purify(R)
        # for r in R:
        #     print(r)
        print("-----------------")
        # for l in L:
        #     print(l)
        purify(L)
    except:
        print("{{[[{{{owi2ww}}}]]}}", format_exc(), flush=True)
