import datetime
import pyperclip
import re
import sys

work_org = sys.argv[1]
day = sys.argv[2]
morning = sys.argv[3]

week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def search_task(lines):
    for line in lines:
        if not line:
            break
        res = re.findall(r"^\* (.+)", line)
        if res:
            # b.p(line)
            return res[0]


def search_lists(lines):
    l = []
    percentage = ""
    for line in lines:
        res = re.findall(r"^\d+\. (.+)", line)
        # 1. #50%，trim一下芯片，微信去电未听见杂音，给到华哥测试
        if not res:
            if percentage:
                return [percentage] + l
            return l
        t = res[0]
        report = re.findall(r"^\d+\. #", line)  # 汇报该行
        if not report:
            continue
        res = re.findall(r"([^，]+)，(.+)", t)
        if res:
            res = res[0]
            l.append(res[1])
            percentage = res[0].strip("#")
        else:
            l.append(t)
    if percentage:
        return [percentage] + l
    return l


if __name__ == "__main__":
    with open(work_org, "rb") as f:
        lines = [line.strip().decode("utf-8") for line in f.readlines()]
    tasks = {}
    y, m, d = [int(i) for i in day.split("-")]
    date_week = datetime.date(y, m, d).weekday()
    text = f"** 刘德培{day}-{week_list[date_week]}进度\n"
    task_cnt = 1
    for i, line in enumerate(lines):
        if re.findall(r"^\*\* " + day, line):  # ** ~2024-12-19这种不汇报
            task = search_task(lines[i::-1])
            if not task:
                continue
            task = task.replace(" ", "》")
            lists = search_lists(lines[i + 1 : :])
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
    pyperclip.copy(text.strip())
