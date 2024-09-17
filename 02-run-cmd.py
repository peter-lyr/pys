import multiprocessing
import os
import subprocess
import sys


def get_sta_output(cmd_params):
    process = subprocess.Popen(
        cmd_params,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    output = []
    sta = 1234
    try:
        while True:
            res = process.stdout.readline()
            if res == "" and process.poll() is not None:
                break
            if res:
                print(res.strip())
                output.append(res.strip())
                sys.stdout.flush()
        sta = process.wait()
    except Exception as e:
        print(e)
    return sta, output


def run(cmd_params_file, i, outputs):
    if not os.path.exists(cmd_params_file):
        sys.exit(2)
    with open(cmd_params_file, "rb") as f:
        cmd_params = [
            line.strip().decode("utf-8") for line in f.readlines() if line.strip()
        ]
    pause = False
    if cmd_params[-2] == "&&" and cmd_params[-1] == "pause":
        pause = True
        cmd_params = cmd_params[:-2]
    sta, output = get_sta_output(cmd_params)
    outputs[i] = [sta, output]
    if pause:
        os.system("pause")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    pool = multiprocessing.Pool(4)
    manager = multiprocessing.Manager()
    outputs = manager.dict()
    cmd_params_files = sys.argv[1:]
    for i in range(len(cmd_params_files)):
        cmd_params_file = cmd_params_files[i]
        pool.apply_async(func=run, args=(cmd_params_file, i, outputs))
    pool.close()
    pool.join()
    # for i, output in outputs.items():
    #     sta, output = output
    #     print(i, sta)
    #     print("+++++++++++++++++++")
    #     print(output)
    #     print("+++++++++++++++++++")
    # os.system("pause")
