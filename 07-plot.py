import os
import re
import sys

import matplotlib.pyplot as plt

P = {
    "num": [0, re.compile("\b([0-9]+)\b")],
    "XX": [1, re.compile(r"\b([0-9a-fA-F]{2})\b")],
    "XX": [1, re.compile(r"\b([0-9a-fA-F]{4})\b")],
    "0xXX": [1, re.compile(r"\b(0[xX][0-9a-fA-F]{2})\b")],
    "0xXXXX": [2, re.compile(r"\b(0[xX][0-9a-fA-F]{4})\b")],
}

N = "0xXX"


def get_num(text):
    if "0x" not in N and "XX" in N:
        num = eval("0x" + text)
    else:
        num = eval(text)
    return num


def get_number(t):
    if "Error" in t:
        return None
    m = P[N][1].findall(t)
    if not m:
        return None
    try:
        num = get_num(m[0])
        return num
    except Exception as e:
        print(e, "OPOOERROR")
    return None


def get_nums_list_from_file(file):
    with open(file, "rb") as f:
        lines = f.readlines()
    numbers = []
    for t in lines:
        t = t.strip().decode("utf-8")
        temp = get_number(t)
        if temp is not None:
            numbers.append(temp)
        else:
            print(t)
    return numbers


def main():
    file = ""
    if len(sys.argv) > 1:
        file = sys.argv[1]
        y = get_nums_list_from_file(file)
        if not y:
            return
    else:
        return
    if file:
        with open(file + ".pcm", "wb") as f:
            for i in y:
                f.write(i.to_bytes(P[N][0], "little"))
    # x = [i for i in range(len(y))]
    # plt.plot(x, y)
    # plt.scatter(x, y)
    # plt.show()


if __name__ == "__main__":
    main()
