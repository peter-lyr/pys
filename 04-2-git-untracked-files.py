import subprocess
import os


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


untracked_files = run_cmd_and_get_output(
    "git ls-files --exclude-standard --no-ignored --others"
)
untracked_files = untracked_files.strip().replace("\r", "").split("\n")
for untracked_file in untracked_files:
    print(untracked_file)

os.system("pause")
