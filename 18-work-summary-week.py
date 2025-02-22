import datetime
import re
import sys

import pyperclip

work_md = sys.argv[1]
week_range = sys.argv[2]

week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def search_task(lines):
    for line in lines:
        if not line:
            break
        res = re.findall(r"^# (.+)", line)
        if res:
            return res[0]


def search_lists(lines):
    l = []
    for line in lines:
        res = re.findall(r"^\d+\. (.+)", line)
        if not res:
            return l
        res2 = re.findall(r"(.*\d+%，.+)", res[0])
        if res2:
            l.append(res2[0])
    return l


if __name__ == "__main__":
    with open(work_md, "rb") as f:
        lines = [line.strip().decode("utf-8") for line in f.readlines()]
    week_num = week_range.split(" ")[0]
    week_days = week_range.split(" ")[1]
    week_start = week_days.split("~")[0]
    week_end = week_days.split("~")[1]
    start_y, start_m, start_d = [int(i) for i in week_start.split("-")]
    end_y, end_m, end_d = [int(i) for i in week_end.split("-")]
    datetime_start = datetime.datetime(start_y, start_m, start_d)
    datetime_end = datetime.datetime(end_y, end_m, end_d)
    text = f"# 刘德培{week_num}周汇报\n"
    Tasks = {}
    for i in range((datetime_end - datetime_start).days + 1):
        day = datetime_start + datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        for i, line in enumerate(lines):
            if not re.findall(r"^## " + day_str, line):  # ## ~2024-12-19这种不汇报
                continue
            task = search_task(lines[i::-1])
            if not task:
                continue
            lists = search_lists(lines[i + 1 : :])
            if not lists:
                continue
            if task not in Tasks:
                Tasks[task] = []
            Tasks[task].append([f"{day_str}-{week_list[day.weekday()]}"] + lists)
    T = sorted(list(Tasks.keys()))
    for k in T:
        v = Tasks[k]
        if len(v) == 0:
            continue
        text += f"\n## {k}\n"
        text += f"=========={week_num}==========\n"
        for _, days in enumerate(v[::-1]):
            if len(days) <= 1:
                continue
            text += f"\n### {days[0]}\n"
            for j, line in enumerate(days[:0:-1]):
                text += f"{j+1}. {line}\n"
    pyperclip.copy(text.strip())
