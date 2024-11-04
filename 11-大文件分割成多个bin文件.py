import os
import sys

# dp = os.path.dirname(os.path.abspath(__file__))
# print(dp)

# bin_file = "3.midi资料.zip"
# bin_file_full = os.path.join(dp, bin_file)
# print(bin_file_full)

try:
    bin_file_full = sys.argv[1]
    if not os.path.isfile(bin_file_full):
        os._exit(2)
except:
    os._exit(1)
bin_file = os.path.split(bin_file_full)[-1]
# print(bin_file_full)
# print(bin_file)

bin_size = os.path.getsize(bin_file_full)
bin_sub_size = 5 * 1024 * 1024
bin_sub_nums = int(bin_size / bin_sub_size)

bin_dir = f"{bin_file_full}-bins"
os.makedirs(bin_dir, exist_ok=True)

with open(bin_file_full, "rb") as infile:
    for i in range(bin_sub_nums + 1):
        part_name = f"{bin_dir}/{bin_file}_{(i + 1):0>4}.bin"
        print(part_name)
        with open(part_name, "wb") as outfile:
            buffer = infile.read(bin_sub_size)
            outfile.write(buffer)

# os.system("pause")
