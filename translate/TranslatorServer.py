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
PORT = int(service["port"])
WORKERS = int(service["worker_threads"])

app = Flask(__name__)
pool = ThreadPoolExecutor(max_workers=WORKERS)
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
    # "bing",
    "baidu",
    # "caiyun",
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
    "simplytranslate.org",
    "st.alefvanoon.xyz",
    "translate.josias.dev",
    "translate.namazso.eu",
    "translate.riverside.rocks",
    "st.manerakai.com",
    "translate.bus-hit.me",
    "simplytranslate.pussthecat.org",
    "translate.northboot.xyz",
    "translate.tiekoetter.com",
    "simplytranslate.esmailelbob.xyz",
    "translate.syncpundit.com",
    "tl.vern.cc",
    "translate.slipfox.xyz",
    "st.privacydev.net",
    "translate.leptons.xyz",
    "translate.catvibers.me",
    "t.opnxng.com",
    "simplytranslate.leemoon.network",
    "simplytranslate.manerakai.com",
    "st.odyssey346.dev",
    "st.tokhmi.xyz",
    "translate.priv.pw",
]

okServers = []


def is_server_ok(url: str, timeout: int = 3):
    try:
        r = requests.get(
            f"{url}/api/translate/",
            params={"engine": "google", "from": "auto", "to": "zh-CN", "text": "text"},
            timeout=timeout,
        )
        if r.status_code == 200:
            return "translated-text" in r.text, url
        else:
            print("~~~~~~")
            return False, url
    except Exception as e:
        print("~~~~~~ ", e)
        return False, url


def check_servers(domains):
    ok = []
    results = [pool.submit(is_server_ok, f"https://{server}", 3) for server in domains]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
    return ok


okServers.extend(check_servers(servers))

print(okServers)


def google_mirror(text: str, src="en", target="zh-CN"):
    try:
        trans = requests.get(
            f"{okServers[0]}/api/translate/",
            params={"engine": "google", "from": src, "to": target, "text": text},
            timeout=REQ_TIMEOUT,
        )

        return "google", trans.json()["translated-text"]
    except Exception as e:
        print(e)
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
        print(e)
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
        app.run(host=service["listen"], port=PORT, debug=False)
    else:
        # 改用waitress WSGI
        from waitress import serve

        serve(app, host=service["listen"], port=PORT)
        app.run()
