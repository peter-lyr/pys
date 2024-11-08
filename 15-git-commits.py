import sys
import time

import b
import os

dir = file = sys.argv[1]

if os.path.isfile(file):
    dir = os.path.dirname(file)
while 1:
    if os.path.exists(os.path.join(dir, ".git")):
        print(dir)
    bak = dir
    dir = os.path.dirname(dir)
    if bak == dir:
        break

# time.sleep(3)
