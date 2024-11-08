import os
import sys

# dp = os.path.dirname(os.path.abspath(__file__))
# print(dp)

try:
    bins_dir_full = sys.argv[1]
    if not os.path.isdir(bins_dir_full):
        os._exit(2)
except:
    os._exit(1)
bins_dir_root, bins_dir = os.path.split(bins_dir_full)
# print(bins_dir_root)
# print(bins_dir)

out_file = "-bin".join(bins_dir.split("-bin")[:-1])
if not out_file:
    os._exit(4)

out_file_name = out_file
# print(out_file)

temp = out_file.split(".")
out_file_true = ".".join(temp[:-1])
out_ext = temp[-1]

# out_file_true = out_file_true + "-out." + out_ext
out_file_true = out_file_true + out_ext
# print(out_file_true)

# 去重
lines = []
gitignore = os.path.join(bins_dir_root, ".gitignore")
with open(gitignore, "rb") as f:
    for line in f.readlines():
        line = line.strip()
        if line not in lines:
            lines.append(line)
if out_file_true.encode("utf-8") not in lines:
    lines.append(out_file_true.encode("utf-8"))
with open(gitignore, "wb") as f:
    for line in lines:
        f.write(line + b"\n")

bins = os.listdir(bins_dir_full)
bins.sort()
# print("bins:")
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

# # print(out_file_name)
# for bin in bins:
#     print(bin)
#     # with open(os.path.join(bins_dir_full, bin), "rb") as inf:
#     #     buffer = inf.read()
#     #     outf.write(buffer)

# os.system("pause")
