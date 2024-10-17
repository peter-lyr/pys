import re
import sys

import matplotlib.pyplot as plt

P = {
    "num": re.compile("\b([0-9]+)\b"),
    "0xXX": re.compile(r"\b(0x[0-9a-fA-F]{2})\b"),  # 0xXX
    "XX": re.compile(r"\b([0-9a-fA-F]{2})\b"),  # XX
}

N = "0xXX"


def get_num(text):
    if "0x" not in N and "XX" in N:
        num = eval("0x" + text)
    else:
        num = eval(text)
    return num


def get_number(t):
    m = P[N].findall(t)
    if not m:
        return
    try:
        num = get_num(m[0])
        return num
    except Exception as e:
        print(e)
    return


def get_nums_list_from_file(file):
    with open(file, "rb") as f:
        lines = f.readlines()
    numbers = []
    for t in lines:
        temp = get_number(t.decode('utf-8'))
        if temp:
            numbers.append(temp)
    return numbers


def main():
    if len(sys.argv) > 1:
        y = get_nums_list_from_file(sys.argv[1])
        if not y:
            return
    else:
        return
    x = [i for i in range(len(y))]
    plt.plot(x, y)
    plt.scatter(x, y)
    plt.show()


if __name__ == "__main__":
    main()
