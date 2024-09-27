import re
import sys

import matplotlib.pyplot as plt

P = {
    "empty_hex": re.compile("[0-9a-fA-F]+"),  # '2d'
    "hex": re.compile("[0-9a-fA-F]+"),  # '0x2d2d2d'
    "hex2": re.compile("[0-9a-fA-F]{2}"),  # '0x2d'
    "num": re.compile("[0-9]+"),
}

N = "num"


def get_num(text):
    if "empty" in N and "hex" in N:
        num = eval("0x" + text)
    else:
        num = eval(text)
    return num


def get_number(t):
    m = P[N].match(t)
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
        content = f.read().decode("utf-8")
    numbers = []
    temp = content.split()
    for t in temp:
        temp = get_number(t)
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
