from concurrent.futures import ThreadPoolExecutor

import requests

pool = ThreadPoolExecutor(max_workers=16)


def is_server_ok(url: str, timeout: int = 1):
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
    results = [pool.submit(is_server_ok, f"https://{server}", 3) for server in domains]
    for r in results:
        state, url = r.result()
        if state:
            ok.append(url)
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

server = "https://api.deepl-pro.com"
auth = "2f8a0549-d214-4509-b880-98618419f562:dp"


def deepl_third(sentence: str, src="EN", target="ZH"):
    target = target.split("-")[0].upper()
    src = src.split("-")[0].upper()
    r = requests.post(f"{server}/v2/translate",
                      data={"text": sentence, "target_lang": target, "source_lang": src},
                      headers={
                          "Content-Type": "application/x-www-form-urlencoded",
                          "Authorization": f"DeepL-Auth-Key {auth}"})
    return r.json()["translations"][0]["text"]


def deepl_third_check():
    return requests.get(f"{server}/v2/referral_usage", headers={
        "Authorization": f"DeepL-Auth-Key {auth}"}).json()["referral_limit"]


if __name__ == '__main__':
    # print(check_servers(servers))
    print(deepl_third("Hello world!"))
    print(deepl_third_check())
