import b

try:
    import pyttsx3
except:
    import os

    os.system(
        "pip install pyttsx3 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host mirrors.aliyun.com"
    )
    import pyttsx3


if __name__ == "__main__":
    params = b.get_params()
    text = " ".join(params[:])
    b.p(text)
    if not text.strip():
        text = text.replace(" ", "空格").replace("\t", "制表符").replace("\n", "回车符")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
