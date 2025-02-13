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
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
