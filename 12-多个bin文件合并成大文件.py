import os
import sys

dp = os.path.dirname(os.path.abspath(__file__))
print(dp)

try:
    bins_dir_full = sys.argv[1]
    if not os.path.isdir(bins_dir_full):
        os._exit(2)
except:
    os._exit(1)
bins_dir_root, bins_dir = os.path.split(bins_dir_full)
print(bins_dir_root)
print(bins_dir)

out_file = "-bin".join(bins_dir.split("-bin")[:-1])
print(out_file)

temp = out_file.split(".")
out_file = ".".join(temp[:-1])
out_ext = temp[-1]

out_file = out_file + "-out." + out_ext
print(out_file)

bins = os.listdir(bins_dir_full)
bins.sort()
print("bins:")
with open(os.path.join(bins_dir_root, out_file), 'wb') as outf:
    for bin in bins:
        with open(os.path.join(bins_dir_full, bin), 'rb') as inf:
            buffer = inf.read()
            outf.write(buffer)

os.system("pause")
