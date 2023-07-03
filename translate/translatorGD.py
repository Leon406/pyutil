import io
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

import requests
import translators as ts

import sys

arg_size = len(sys.argv)
originalText = "Please input what you want to translate!"
fromLanguage = "en"
toLanguage = "zh-CN"

debug = False

# 可以手动指定翻译参数,默认英译中, 中译英可参考如下
# python translatorGD.py "text to translate" zh-CN en

if arg_size > 1:
    originalText = sys.argv[1]
if arg_size > 2:
    fromLanguage = sys.argv[2]
if arg_size > 3:
    toLanguage = sys.argv[3]

pool = ThreadPoolExecutor(max_workers=16)
start_time = time.time()
# 按需调整翻译引擎, 已支持多线程,基本不影响整体加载速度
cn_translator = [
    # 无法正常翻译
    # "google",
    # "bing",
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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

css = """<style type="text/css">
    .engine {
      font-family: "MiSansVF";
      font-size: 18px;
      color: #578bc5;
    }
    .originalText {
        font-size: 120%;
        font-family: "MiSansVF";
        font-weight: 600;
        display: inline-block;
        margin: 0rem 0rem 0rem 0rem;
        color: #2a5598;
        margin-bottom: 0.6rem;
    }
    .frame {
        margin: 1rem 0.5rem 0.5rem 0;
        padding: 0.7rem 0.5rem 0.5rem 0;
        border-top: 3px dashed #eaeef6;
    }
    definition {
        font-family: "MiSansVF";
        color: #2a5598;
        height: 120px;
        padding: 0.05em;
        font-weight: 500;
        font-size: 16px;
    }
    </style>"""


def html():
    print(css)
    print('<div class="originalText">' + originalText + '</div>')
    print('<br><br>')


servers = [
    "st.tokhmi.xyz",
    "translate.riverside.rocks",
    "simplytranslate.manerakai.com",
    "simplytranslate.pussthecat.org",
    "translate.tiekoetter.com",
    "simplytranslate.esmailelbob.xyz",
    "tl.vern.cc",
    "translate.slipfox.xyz",
    "st.privacydev.net",
    "translate.beparanoid.de",
]
okServers = ["st.tokhmi.xyz"]


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
    # print(okServers)


def google_mirror(text: str, src="en", target="zh-CN"):
    try:
        trans = requests.get(f"https://{okServers[0]}/api/translate/",
                             params={"engine": "google",
                                     "from": src,
                                     "to": target,
                                     "text": text
                                     }, timeout=3.0)

        return "google", trans.json()["translated-text"]
    except Exception as e:
        if debug:
            print(e)
        return "google", "错误"


# https://github.com/CopyTranslator/CopyTranslator/blob/master/src/common/translate/lingva.ts
def lingva(text, src="en", target="zh"):
    try:
        resp = requests.get(
            f"https://lingva.ml/api/v1/{src.replace('-CN', '')}/{target.replace('-CN', '')}/{quote(text)}", timeout=3.0)
        return "lingva", resp.json()["translation"]
    except Exception as e:
        if debug:
            print(e)
        return "lingva", "错误"


def _output(engine: str, definition: str):
    print('<span class="engine">' + engine + "</span>")
    print('<div class="frame">')
    print('<definition>' + definition + '</definition>')
    print("</div>")
    print("<br>")


def translators(text: str, translator: str = "bing", src: str = "zh", target: str = "en"):
    try:
        translated_text = ts.translate_text(text, from_language=src, to_language=target, translator=translator,
                                            timeout=3.0)
        return translator, translated_text
    except Exception as e:
        if debug:
            print(e)
        return translator, "错误"


results = [pool.submit(translators, originalText, i, fromLanguage, toLanguage) for i in cn_translator]
results.insert(0, pool.submit(google_mirror, originalText, fromLanguage, toLanguage))
results.insert(4, pool.submit(lingva, originalText, fromLanguage, toLanguage))

html()
for r in results:
    t, translated = r.result()
    _output(TYPE_DICT[t], translated)

print(f"It takes {(time.time() - start_time):.2f} seconds")
