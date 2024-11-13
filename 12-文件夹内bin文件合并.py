import os
import sys
import b


# 已收录到b.py
def merge_bins_file(bins_dir_full):
    bins_dir_root, bins_dir = os.path.split(bins_dir_full)

    out_file = "-bin".join(bins_dir.split("-bin")[:-1])
    if not out_file:
        os._exit(4)

    out_file_name = out_file

    temp = out_file.split(".")
    out_file_true = ".".join(temp[:-1])
    out_ext = temp[-1]

    out_file_true = out_file_true + "." + out_ext

    b.add_ignore_files(bins_dir_root, [out_file_true])

    bins = os.listdir(bins_dir_full)
    bins.sort()
    new_bins = []
    for bin in bins:
        if out_file_name in bin:
            new_bins.append(bin)
    if not new_bins:
        os._exit(3)
    with open(os.path.join(bins_dir_root, out_file_true), "wb") as outf:
        for bin in new_bins:
            if out_file_name not in bin:
                continue
            print(bin)
            with open(os.path.join(bins_dir_full, bin), "rb") as inf:
                buffer = inf.read()
                outf.write(buffer)


if __name__ == "__main__":
    try:
        bins_dir_full = sys.argv[1]
        if not os.path.isdir(bins_dir_full):
            os._exit(2)
    except:
        os._exit(1)
    merge_bins_file(bins_dir_full)

# os.system("pause")
