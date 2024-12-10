import random
from concurrent.futures import ThreadPoolExecutor

import requests

pool = ThreadPoolExecutor(max_workers=16)


def is_google_server_ok(url: str, timeout: int = 1):
    try:
        r = requests.get(f"{url}/api/translate/",
                         params={"engine": "google",
                                 "from": "auto",
                                 "to": "zh-CN",
                                 "text": "text"
                                 }, timeout=timeout)
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
    results = [pool.submit(is_google_server_ok, f"https://{server}", 3) for server in domains]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
    return ok


def check_deepx_servers(urls):
    print(len(urls))
    ok = []
    results = [pool.submit(is_deeplx_server_ok, url, 3) for url in urls]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
    print(len(ok))
    return ok


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

# https://github.com/CaoYunzhou/cf-free-deeplx
# https://github.com/xiaozhou26/serch_deeplx/blob/main/success.txt
deeplx_servers = [
    'http://132.226.232.50:1188', 'http://165.154.203.71:1188', 'http://82.157.49.14:1188', 'http://123.56.13.17:1188', 'http://121.43.134.47:1188', 'http://138.2.11.53:1188', 'http://124.223.85.170:1188', 'http://116.62.112.61:1188', 'http://42.193.219.103:1188', 'http://47.76.48.116:1188', 'http://168.138.161.222:1188', 'http://141.11.90.131:1188', 'https://deeplx.qninq.cn', 'https://deeplx.qiud.org', 'http://106.14.155.58:18019', 'https://deepl.kevinzhang.cn', 'http://23.94.25.208:1188', 'http://deeplx.qninq.cn']

server = "https://api.deepl-pro.com"
serverx = "https://deepx.dumpit.top"
auth = "2f8a0549-d214-4509-b880-98618419f562:dp"


def deepl_third(sentence: str, src="EN", target="ZH"):
    target = target.split("-")[0].upper()
    src = src.split("-")[0].upper()
    r = requests.post(f"{server}/translate",
                      data={"text": sentence, "target_lang": target, "source_lang": src},
                      timeout= 5,
                      headers={
                          "Content-Type": "application/x-www-form-urlencoded",
                          "Authorization": f"DeepL-Auth-Key {auth}"})
    js = r.json()
    if "translations" not in js:
        print(js)
        return
    return js["translations"][0]["text"]


def is_deeplx_server_ok(url: str, timeout: int = 1):
    try:
        data = {"text": "Hello Leon", "target_lang": "ZH", "source_lang": "EN"}
        r = requests.post(f"{url}/translate", json=data)
        if r.status_code == 200:
            return "data" in r.json(), url
        else:
            print("~~~~~~", url, r.text)
            return False, url
    except Exception as e:
        print("~~~~~~ ", url, e)
        return False, url


def deeplx_free(sentence: str, src="EN", target="ZH"):
    target = target.split("-")[0].upper()
    src = src.split("-")[0].upper()

    data = {"text": sentence, "target_lang": target, "source_lang": src}
    r = requests.post(f"{random.choice(deeplx_servers)}/translate", json=data)
    json_str = r.json()
    print(json_str)
    if "data" not in json_str:
        print(json_str)
        return
    return json_str["data"] + (("\r\n" + "\r\n".join(json_str["alternatives"])) if json_str["alternatives"] else "")


def deepl_third_check():
    return requests.get(f"{server}/v2/referral_usage", headers={
        "Authorization": f"DeepL-Auth-Key {auth}"}).json()["referral_limit"]


def tr():
    import translators as ts
    translated_text = ts.translate_text(
        "hello leon",
        from_language="en",
        to_language="zh",
        translator="baidu",
        timeout=3,
    )
    print(translated_text)


if __name__ == '__main__':
    # print(check_servers(servers))
    deeplx_servers = check_deepx_servers(deeplx_servers)
    print(deeplx_servers)

    # # tr()
    # print(deeplx_free(
    #     "Cecil Scott Forester (1899-1966) an English writer, best known for his historical novels about life in the Royal Navy. He created the famous character Horatio Hornblower, and wrote 12 novels about his adventures at sea during the Napoleonic Wars."))
    # # print(deepl_third_check())
