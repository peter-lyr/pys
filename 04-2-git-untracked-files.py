import subprocess
import os

# 已收录get_untracked_file_size
import b


def run_cmd_and_get_output(command):
    """
    运行cmd命令并返回它的执行结果
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
        else:
            output = result.stderr.strip()
    except Exception as e:
        output = str(e)
    return output


def get_untracked_file_size(dir=None):
    if not dir:
        return
    untracked_files = run_cmd_and_get_output(
        f"cd {dir} & git ls-files --exclude-standard --no-ignored --others"
    )
    untracked_files = untracked_files.strip().replace("\r", "").split("\n")
    sizes = 0
    for untracked_file in untracked_files:
        print(untracked_file)
        sizes += os.path.getsize(untracked_file)
    if sizes >= 500 * 1024 * 1024:
        print("error")


if __name__ == "__main__":
    b.get_untracked_file_size()
    os.system("pause")
