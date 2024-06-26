import configparser
import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import translators as ts
from flask import Flask, render_template, request

debug = True
# region 读service.conf配置文件
config = configparser.ConfigParser()
config.read("service.conf", encoding="utf-8")
service = config["service"]
REQ_TIMEOUT = int(service["req_timeout"])
HIDE_ERROR = int(service["hide_error"]) == 1
PORT = int(service["port"])
WORKERS = int(service["worker_threads"])
# endregion

ERROR_INFO = "Response Error 错误"

# 按需调整翻译引擎, 已支持多线程,基本不影响整体加载速度
# https://github.com/UlionTse/translators/blob/master/translators/server.py
cn_translator = [
    # 无法正常翻译 ,采用自实现镜像
    # "deepl",
    # "google",

    #  README状态 不可用
    # "yeekit",
    # "volcEngine",
    # "niutrans",

    "youdao",
    "bing",
    "sogou",
    "baidu",

    "qqTranSmart",
    "qqFanyi",
    "caiyun",
    "iflyrec",

    "hujiang",
    "iciba",
    "alibaba",

    "myMemory",
    "lingvanex",
    "modernMt",
    "sysTran",
    "argos",
]
# refer https://github.com/UlionTse/translators
TYPE_DICT = {
    "baidu": "百度",
    "bing": "必应",
    "deepl": "DeepL",
    "deeplx": "DeepLX（候选）",
    "youdao": "有道智云",
    "iciba": "金山词霸",
    "alibaba": "阿里",
    "sogou": "搜狗",
    "caiyun": "彩云小译",
    "google": "Google",
    "iflyrec": "讯飞听见",
    "niutrans": "小牛",
    "qqFanyi": "腾讯翻译君",
    "qqTranSmart": "腾讯交互翻译",
    "volcEngine": "火山",
    "yeekit": "Yeekit中译语通",
    "lingvanex": "Lingvanex",
    "hujiang": "沪江",
    "modernMt": "ModernMT",
    "myMemory": "MyMemory",
    "argos": "Argos",
    "sysTran": "Systran",
}

# region 镜像服务器
google_mirror_servers = [
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

# https://github.com/CaoYunzhou/cf-free-deeplx
# https://github.com/xiaozhou26/serch_deeplx/blob/main/success.txt
deeplx_servers = [
    "https://deepx.dumpit.top",
    "https://deepl.tr1ck.cn",
    "https://deeplx.keyrotate.com",
    "https://dlx.bitjss.com",
    "https://deepl.yuwentian.com",
    "https://deepl.wuyongx.uk",
    "https://deeplx.he-sb.top",
    # "https://deepl.aimoyu.tech",
    "http://107.150.100.170:8880",
    "https://deeplx.ychinfo.com",
    "http://deepl.wuyongx.uk",
    "https://api.deeplx.org",
    # "https://deeplx.vercel.app",
    "https://dx-api.nosec.link",
    "https://deepl.zhaosaipo.com",
    "https://deeplx.papercar.top",
    "http://20.89.253.28",
    "https://deepl.mukapp.top",
    "https://deepl.degbug.top",
    "https://deepl.coloo.org",
]
# endregion

# 自行注册无需信用卡,免费20W/月  https://deepl-pro.com/#/translate
# 使用邀请链接可以多获取20W/月  https://deepl-pro.com/#/translate?referral_code=Bw9Ic9czPM
DEEPL_THIRD_SERVER = "https://api.deepl-pro.com"
auth = "2f8a0549-d214-4509-b880-98618419f562:dp"

deepl_auth_keys = [auth]


# region 第三方镜像及服务筛选
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
            # print("~~~~~~")
            return False, url
    except Exception as e:
        # print("~~~~~~ ", e)
        return False, url


def check_servers(domains):
    ok = []
    results = [pool.submit(is_server_ok, f"https://{server}", REQ_TIMEOUT) for server in domains]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
    return ok


def is_deeplx_server_ok(url: str, timeout: int = 1):
    try:
        data = {"text": "Hello Leon", "target_lang": "ZH", "source_lang": "EN"}
        r = requests.post(f"{url}/translate", json=data, timeout=timeout)
        if r.status_code == 200:
            return "data" in r.json(), url
        else:
            print("~~~~~~", url, r.text)
            return False, url
    except Exception as e:
        print("~~~~~~ ", url, e)
        return False, url


def check_deeplx_servers(urls):
    ok = []
    results = [pool.submit(is_deeplx_server_ok, url, REQ_TIMEOUT) for url in urls]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
    return ok


# endregion

# region 第三方翻译
def google_mirror(text: str, src="en", target="zh-CN"):
    try:
        trans = requests.get(
            f"{google_mirror_servers[0]}/api/translate/",
            params={"engine": "google", "from": src, "to": target, "text": text},
            timeout=REQ_TIMEOUT,
        )

        return "google", trans.json()["translated-text"]
    except Exception as e:
        print(e)
        return "google", ERROR_INFO


def deepl_third(sentence: str, src="EN", target="ZH"):
    target = target.split("-")[0].upper()
    src = src.split("-")[0].upper()

    r = requests.post(f"{DEEPL_THIRD_SERVER}/v2/translate",
                      data={"text": sentence, "target_lang": target, "source_lang": src},
                      headers={
                          "Content-Type": "application/x-www-form-urlencoded",
                          "Authorization": f"DeepL-Auth-Key {deepl_auth_keys[-1]}"}, timeout=REQ_TIMEOUT)
    print(r.json())
    try:
        if "msg" in r.json():
            return "deepl", r.json()["msg"]
        return "deepl", r.json()["translations"][0]["text"]
    except Exception as e:
        print(e)
        return "deepl", ERROR_INFO


def deepl_third_check(auth=deepl_auth_keys[-1]):
    jsonData = requests.get(f"{DEEPL_THIRD_SERVER}/v2/usage", headers={
        "Authorization": f"DeepL-Auth-Key {auth}"}, timeout=REQ_TIMEOUT).json()
    return f"{jsonData['character_count']}/{jsonData['character_limit']}"


def deepl_third_referral(auth=deepl_auth_keys[-1]):
    return requests.get(f"{DEEPL_THIRD_SERVER}/v2/referral_usage", headers={
        "Authorization": f"DeepL-Auth-Key {auth}"}, timeout=REQ_TIMEOUT).json()["referral_limit"]


def deeplx_free(sentence: str, src="EN", target="ZH"):
    """主翻译 + 3个候选"""
    target = target.split("-")[0].upper()
    src = src.split("-")[0].upper()

    data = {"text": sentence, "target_lang": target, "source_lang": src}

    try:
        r = requests.post(f"{random.choice(deeplx_servers)}/translate", json=data, timeout=REQ_TIMEOUT)
        json_str = r.json()
        return "deeplx", json_str["data"] + (
            ("<br/>" + "<br/>".join(json_str["alternatives"])) if json_str["alternatives"] else "")
    except Exception as e:
        print(e)
        return "deeplx", ERROR_INFO


# endregion


def translators(
        text: str, translator: str = "bing", src: str = "zh", target: str = "en"
):
    try:
        print(f" translator {translator} ")
        translated_text = ts.translate_text(
            text,
            from_language=src,
            to_language=target,
            translator=translator,
            timeout=REQ_TIMEOUT,
        )
        return translator, translated_text
    except Exception as e:
        print(f"\t\t error: translator {translator} {e}")
        return translator, ERROR_INFO


# region 对外服务
app = Flask(__name__)


@app.route("/")
def index():
    start_time = time.time()
    trans = []
    print(request.args)
    fromLanguage = request.args["from"] if "from" in request.args else "en"
    toLanguage = request.args["to"] if "to" in request.args else "zh-CN"
    hideError = int(request.args["hide"]) == 1 if "hide" in request.args else HIDE_ERROR
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
        0, pool.submit(deepl_third, originalText, fromLanguage, toLanguage)
    )
    results.insert(
        1, pool.submit(deeplx_free, originalText, fromLanguage, toLanguage)
    )
    results.insert(
        2, pool.submit(google_mirror, originalText, fromLanguage, toLanguage)
    )
    for r in results:
        t, translated = r.result()
        print(f" type {t} {translated}")
        t_ = TYPE_DICT[t] if t in TYPE_DICT else t

        # 错误数据 空结果,无翻译，仅标点过滤
        if hideError and (
                translated == ERROR_INFO or not translated.strip() or translated == "。" or translated == originalText):
            continue
        trans.append([t_, translated])

    combined = {}
    for (t, tr) in trans:
        print(f"-- {tr}  --{t}")
        if tr not in combined:
            combined[tr] = t
        else:
            combined[tr] = combined[tr] + " · " + t
    trans = zip(combined.values(), combined.keys())
    info = f"It takes {(time.time() - start_time):.2f} seconds"
    print(info)
    return render_template("index.html", originalText=originalText, translators=trans, info=info)


@app.route("/add_deepl_auth")
def deepl_add():
    if request.args["auth"]:
        deepl_auth_keys.append(request.args["auth"])
    return deepl_auth_keys


@app.route("/delete_deepl_auth")
def deepl_remove():
    if request.args["auth"]:
        deepl_auth_keys.remove(request.args["auth"])
    return deepl_auth_keys


@app.route("/deepl_query")
def deepl_query():
    auth = request.args["auth"] if "auth" in request.args else deepl_auth_keys[-1]
    count = deepl_third_check(auth)
    return {"auth": auth, "quota": count}


# endregion

pool = ThreadPoolExecutor(max_workers=WORKERS)

print("==>筛选 google镜像")
google_mirror_servers = check_servers(google_mirror_servers)
print("==>筛选 deeplx 镜像")
deeplx_servers = check_deeplx_servers(deeplx_servers)
print("\t<==筛选 deeplx 镜像")
if __name__ == "__main__":
    if debug:
        print("------- Flask starting!!!")
        app.run(host=service["listen"], port=PORT, debug=False)
    else:
        # 改用waitress WSGI
        from waitress import serve

        print("------- waitress starting!!!")
        serve(app, host=service["listen"], port=PORT, threads=4)
        app.run()
