import subprocess
import sys
import b

def run(cmd):
    if cmd and cmd[-1] == "&&":
        cmd = cmd[:-1]
    if cmd and cmd[-1] == "&":
        cmd = cmd[:-1]
    if cmd and cmd[-1] == "&&":
        cmd = cmd[:-1]
    if cmd and cmd[-1] == "&":
        cmd = cmd[:-1]
    process = subprocess.Popen(
        cmd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        encoding="utf-8",
        errors="ignore",
    )
    stdout, stderr = process.communicate()
    process.wait()
    b.p(stdout)
    if stderr:
        b.p('stderr:' + stderr)

if __name__ == "__main__":
    submodule_root = sys.argv[1]
    submodule_old_name = sys.argv[2]
    submodule_new_name = sys.argv[3]
    submodule_remote_url = sys.argv[4]

    cmd = []
    cmd += [
      "cd", "/d", f'''"{submodule_root}"''', "&",
    ]
    cmd += [
        "rm", "-rf", f".git/modules/{submodule_old_name}", "&",
    ]
    cmd += [
      "git", "submodule", "deinit", "-f", submodule_old_name, "&",
    ]
    cmd += [
      "git", "rm", "-f", submodule_old_name, "&",
    ]
    run(cmd)

    cmd = []
    cmd += [
      "git", "submodule", "add", "-f", submodule_remote_url, submodule_new_name, "&&",
    ]
    cmd += [
      "git", "add", ".", "&&",
    ]
    cmd += [
      "git", "commit", "-m", f'''"{submodule_old_name} renamed to {submodule_new_name}"''', "&&",
    ]
    cmd += [
      "git", "push", "&&",
    ]
    run(cmd)
