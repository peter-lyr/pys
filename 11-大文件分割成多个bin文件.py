import os
import b
import sys


def split_big_file(bin_file_full):
    bin_file_full_dir = os.path.split(bin_file_full)[0]
    bin_file = os.path.split(bin_file_full)[-1]

    bin_size = os.path.getsize(bin_file_full)
    bin_sub_size = 10 * 1024 * 1024
    if bin_size < bin_sub_size:
        os._exit(3)
    bin_sub_nums = int(bin_size / bin_sub_size)

    bin_dir = f"{bin_file_full}-bins"
    os.makedirs(bin_dir, exist_ok=True)

    b.add_ignore_files(bin_file_full_dir, [bin_file])

    with open(bin_file_full, "rb") as infile:
        for i in range(bin_sub_nums + 1):
            part_name = f"{bin_dir}/{bin_file}_{(i + 1):0>4}.bin"
            with open(part_name, "wb") as outfile:
                buffer = infile.read(bin_sub_size)
                outfile.write(buffer)


if __name__ == "__main__":
    try:
        bin_file_full = sys.argv[1]
        if not os.path.isfile(bin_file_full):
            os._exit(2)
    except:
        os._exit(1)
    split_big_file(bin_file_full)

os.system("pause")
