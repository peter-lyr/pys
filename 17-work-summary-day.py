import os
import datetime
import pyperclip
import re
import subprocess
import sys
import time

import b

work_org = sys.argv[1]
day = sys.argv[2]
morning = sys.argv[3]

week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ptr_task = 0  # * 凯利诺，13X，PS4拔插3.5mm耳机会重新枚举一次
# ptr_list = 0  # 1. 耳机座4脚增加磁珠，缩短USB线，关闭所有audio寄存器，均未改善。
# ptr_line = 0

# b.p(work_org)
# b.p(day)


def search_task(lines):
    for line in lines:
        if not line:
            break
        res = re.findall(r"^\* (.+)", line)
        if res:
            # b.p(line)
            return res[0]


def search_lists(lines):
    # b.p("\n".join(lines))
    l = []
    for line in lines:
        res = re.findall(r"^\d+\. (.+)", line)
        if not res:
            return l
        # b.p(line)
        l.append(res[0])
    return l


if __name__ == "__main__":
    with open(work_org, "rb") as f:
        lines = [line.strip().decode("utf-8") for line in f.readlines()]
    # tasks = []
    tasks = {}
    y, m, d = [int(i) for i in day.split("-")]
    date_week = datetime.date(y, m, d).weekday()
    text = f"刘德培{day}-{week_list[date_week]}计划\n"
    task_cnt = 1
    for i, line in enumerate(lines):
        if re.findall(r"^\*\* " + day, line):
            # b.p(line.strip())
            # b.p(str(i) + "-----------")
            # tasks.append(search_task(lines[i::-1]))
            task = search_task(lines[i::-1])
            # b.p("task:")
            # b.p(task)
            if not task:
                continue
            lists = search_lists(lines[i + 1 : :])
            # b.p("lists:")
            # b.p("\n".join(lists))
            if not lists:
                tasks[task] = "未跟进"
                if morning == "morning":
                    text += f"{task_cnt}. {task}\n"
                else:
                    text += f"{task_cnt}. {task}->未跟进\n"
            else:
                t = "；".join([i.strip("。").strip("；") for i in lists])
                tasks[task] = t
                if morning == "morning":
                    text += f"{task_cnt}. {task}\n"
                else:
                    text += f"{task_cnt}. {task}->{t}\n"
            task_cnt += 1
    # b.p("tasks:")
    # b.p(str(tasks))
    pyperclip.copy(text.strip())
