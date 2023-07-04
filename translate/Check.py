from concurrent.futures import ThreadPoolExecutor

import requests

pool = ThreadPoolExecutor(max_workers=16)


def is_server_ok(url: str, timeout: int = 1):
    try:
        # r = requests.get(url, timeout=timeout)
        r = requests.get(f"{url}/api/translate/",
                         params={"engine": "google",
                                 "from": "auto",
                                 "to": "zh-CN",
                                 "text": "text"
                                 }, timeout=timeout)
        if r.status_code == 200:
            print(url)
            print(r.text)
            return True, url
        else:
            print("~~~~~~")
            return False, url
    except Exception as e:
        print("~~~~~~ ", e)
        return False, url


def check_servers(domains):
    ok = []
    results = [pool.submit(is_server_ok, f"https://{server}", 1) for server in domains]
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

if __name__ == '__main__':
    print(check_servers(servers))
