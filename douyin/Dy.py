import subprocess
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
import requests
from urllib.parse import urlencode

with open('getXBoGust.js', encoding="utf8") as fp:
    js_func = execjs.compile(fp.read(), cwd="E:\\Lily5\\Scoop\\persist\\nvm\\nodejs\\v16.17.1\\node_modules")

headers = {
    "cookie": "strategyABtestKey=%221672340505.13%22;",
    "referer": "https://www.douyin.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}
params = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "aweme_id": "7166234565919477005",
    "cursor": "0",
    "count": "20",
    "item_type": "0",
    "insert_ids": "",
    "rcFT": "",
    "pc_client_type": "1",
    "version_code": "170400",
    "version_name": "17.4.0",
    "cookie_enabled": "true",
    "screen_width": "1536",
    "screen_height": "864",
    "browser_language": "zh-CN",
    "browser_platform": "Win32",
    "browser_name": "Chrome",
    "browser_version": "104.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "104.0.0.0",
    "os_name": "Windows",
    "os_version": "10",
    "cpu_core_num": "8",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "10",
    "effective_type": "4g",
    "round_trip_time": "100",
    "webid": "7182571494127535616",
    # "msToken": "BAsHVO5ryQtHyUqtVIOpdhHNHTr4LpedaPHBWiERWgaPcuCNnhIUR1JzxW3ND6-0nQ7bfXM6gzZ_XNzxQHKFtdN3bRYBwZtYkSZ-76bSvYPnxyOk8okq"
}
url_path = urlencode(params, safe='=')
print(url_path)
params["X-Bogus"] = js_func.call("getXBoGust", url_path)
response = requests.get("https://www.douyin.com/aweme/v1/web/comment/list/?" + urlencode(params, safe='='),
                        headers=headers)
print(response.text)
