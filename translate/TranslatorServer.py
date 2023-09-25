import configparser
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import translators as ts
from flask import Flask, render_template, request

debug = False
# 读取service.conf配置文件
config = configparser.ConfigParser()
config.read("service.conf", encoding="utf-8")
service = config["service"]
REQ_TIMEOUT = int(service["req_timeout"])

app = Flask(__name__)
pool = ThreadPoolExecutor(max_workers=int(service["worker_threads"]))
start_time = time.time()
# 按需调整翻译引擎, 已支持多线程,基本不影响整体加载速度
cn_translator = [
    # 无法正常翻译
    # "deepl",
    # "google",
    #  "bing",
    # "yeekit",
    # "volcEngine",
    # "niutrans",
    # "cloudYi",
    "youdao",
    "sogou",
    "bing",
    "baidu",
    "caiyun",
    "iflyrec",
    "iciba",
    "alibaba",
    # "qqFanyi"
]
# refer https://github.com/UlionTse/translators
TYPE_DICT = {
    "baidu": "百度翻译",
    "bing": "必应",
    "deepl": "Deepl",
    "youdao": "有道智云",
    "iciba": "金山词霸",
    "alibaba": "阿里翻译",
    "sogou": "搜狗翻译",
    "caiyun": "彩云小译",
    "google": "Google翻译",
    "iflyrec": "讯飞听见",
    "niutrans": "小牛翻译",
    "qqFanyi": "腾讯翻译君",
    "cloudYi": "云译",
    "volcEngine": "火山翻译",
    "yeekit": "Yeekit中译语通",
    "lingva": "lingva",
}

servers = [
    "https://st.alefvanoon.xyz",
    "https://simplytranslate.pussthecat.org",
    "https://simplytranslate.esmailelbob.xyz",
    "https://simplytranslate.leemoon.network",
    "https://st.odyssey346.dev",
]


okServers = [
    "https://st.alefvanoon.xyz",
    "https://simplytranslate.pussthecat.org",
    "https://simplytranslate.esmailelbob.xyz",
    "https://simplytranslate.leemoon.network",
    "https://st.odyssey346.dev",
]


def check_servers():
    for server in servers:
        try:
            r = requests.get(f"https://{server}", timeout=1)
            if r.status_code == 200:
                okServers.append(server)
            else:
                print("~~~~~~")
        except Exception as e:
            print("~~~~~~ ", e)
    print(okServers)


check_servers()


def google_mirror(text: str, src="en", target="zh-CN"):
    try:
        trans = requests.get(
            f"https://{okServers[-1]}/api/translate/",
            params={"engine": "google", "from": src, "to": target, "text": text},
            timeout=REQ_TIMEOUT,
        )

        return "google", trans.json()["translated-text"]
    except Exception as e:
        return "google", "错误"


def translators(
    text: str, translator: str = "bing", src: str = "zh", target: str = "en"
):
    try:
        translated_text = ts.translate_text(
            text,
            from_language=src,
            to_language=target,
            translator=translator,
            timeout=REQ_TIMEOUT,
        )
        return translator, translated_text
    except Exception as e:
        return translator, "错误"


@app.route("/")
def index():
    trans = []
    print(request.args)
    fromLanguage = request.args["from"] if "from" in request.args else "en"
    toLanguage = request.args["to"] if "to" in request.args else "zh-CN"
    originalText = (
        request.args["d"]
        if "d" in request.args
        else "Please input what you want to translate!"
    )

    print(f"{originalText} {fromLanguage} {toLanguage}")
    results = [
        pool.submit(translators, originalText, i, fromLanguage, toLanguage)
        for i in cn_translator
    ]
    results.insert(
        0, pool.submit(google_mirror, originalText, fromLanguage, toLanguage)
    )
    for r in results:
        t, translated = r.result()
        trans.append([TYPE_DICT[t], translated])
    return render_template("index.html", originalText=originalText, translators=trans)


if __name__ == "__main__":
    if debug:
        app.run(host=service["listen"], port=service["port"], debug=False)
    else:
        # 改用waitress WSGI
        from waitress import serve

        serve(app, host=service["listen"], port=int(service["port"]))
        app.run()
