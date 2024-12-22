import os
import re
import subprocess
from traceback import format_exc

import b


def purify(lines, no_print=False):
    A = []
    B = []
    for line in lines:
        temp = line.split("\t\t\t\t\t")
        if len(temp) >= 2:
            A.append(temp[0])
            B.append(temp[1])
        else:
            A.append(temp[0])
    AA = []
    if len(A) == len(B):
        m = max([len(n) for n in A])
        t = f"{{:<{m}}} {{}}"
        L = []
        for a, b in zip(A, B):
            L.append(t.format(a, b))
        for l in L:
            if not no_print:
                print(l)
            AA.append(l)
    else:
        m = max([len(n) for n in A])
        t = f"{{:<{m}}}"
        L = []
        for a in A:
            L.append(t.format(a))
        for l in L:
            if not no_print:
                print(l)
            AA.append(l)
    return AA


def get_repos(root):
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
    return repos


def get_all_repos():
    try:
        params = b.get_params()
        root = params[0]
        show_what = params[1]
        repos = get_repos(root)
        R = []
        patt = r"^\d{3}[_-]"  # main
        if show_what == "temp":
            patt = r"^t\d{3}[_-]"
        for repo in repos:
            if re.match(patt, repo):
                R.append(repo)
        if R:
            R.sort(reverse=True)
            AA = purify(R, True)
            return AA
        return []
    except:
        print("{{[[{{{owi2ww}}}]]}}", format_exc(), flush=True)
        return []


def get_max_num_index():
    try:
        return get_all_repos()[0].split("-")[0].split("_")[0]
    except:
        return "0"


def main():
    try:
        params = b.get_params()
        root = params[0]
        show_what = params[1]
        repos = get_repos(root)
        R = []
        L = []
        patt = r"^\d{3}[_-]"  # main
        if show_what == "temp":
            patt = r"^t\d{3}[_-]"
        for repo in repos:
            if re.match(patt, repo):
                R.append(repo)
            else:
                L.append(repo)
        if R:
            R.sort(reverse=True)
            purify(R)
        # for r in R:
        #     print(r)
        print("-----------------")
        # for l in L:
        #     print(l)
        if L:
            purify(L)
    except:
        print("{{[[{{{owi2ww}}}]]}}", format_exc(), flush=True)


if __name__ == "__main__":
    main()
    # print(get_max_num_index())
