import os
import subprocess
import sys
from traceback import format_exc


def get_sta_output(cmd_params, cmd_params_file, opts):
    output = []
    sta = 1234
    try:
        process = subprocess.Popen(
            cmd_params,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if "no_output" not in opts:
            while True:
                res = process.stdout.readline()
                if res == "" and process.poll() is not None:
                    break
                if res:
                    print(res.strip())
                    output.append(res.strip())
                    sys.stdout.flush()
        sta = process.wait()
    except:
        e = format_exc()
        print(e, flush=True)
        with open(get_outerr_file(cmd_params_file), "wb") as f:
            f.write(str(e).encode("utf-8"))
    return sta, output


def get_outmsg_file(cmd_params_file):
    head, tail = os.path.split(cmd_params_file)
    return os.path.join(head, tail.replace("params", "out-msg"))


def get_outsta_file(cmd_params_file):
    head, tail = os.path.split(cmd_params_file)
    return os.path.join(head, tail.replace("params", "out-sta"))


def get_outerr_file(cmd_params_file):
    head, tail = os.path.split(cmd_params_file)
    return os.path.join(head, tail.replace("params", "out-err"))


def run(cmd_params_file, opts):
    try:
        if not os.path.exists(cmd_params_file):
            sys.exit(2)
        with open(cmd_params_file, "rb") as f:
            cmd_params = [
                line.strip().decode("utf-8") for line in f.readlines() if line.strip()
            ]
        pause = False
        try:
            if cmd_params[-2] == "&&" and cmd_params[-1] == "pause":
                pause = True
                cmd_params = cmd_params[:-2]
        except:
            pass
        sta, output = get_sta_output(cmd_params, cmd_params_file, opts)
        with open(get_outmsg_file(cmd_params_file), "wb") as f:
            if output:
                for line in output:
                    f.write(line.encode("utf-8").strip() + b"\n")
            else:
                f.write(b"000")
        with open(get_outsta_file(cmd_params_file), "wb") as f:
            f.write(b"1")
        if pause:
            os.system("pause")
    except:
        e = format_exc()
        print("wioe", e, flush=True)
        with open(get_outerr_file(cmd_params_file), "wb") as f:
            f.write(str(e).encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    run(sys.argv[1], sys.argv[2:])
