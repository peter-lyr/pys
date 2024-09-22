import os
import re
import subprocess
from datetime import datetime

import funcs as f
from xpinyin import Pinyin

if __name__ == "__main__":
    try:
        params = f.get_params()
        root = params[0]
        os.chdir(root)
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
            capture_output=True,
            text=True,
        )
        repos = result.stdout.replace('\r', '').split('\n')
        R = []
        for repo in repos:
            if re.match(r'^\d{3}[_-]', repo):
                R.append(repo)
        R.sort(reverse=True)
        for r in R:
            print(r)
    except Exception as e:
        print(e, flush=True)
