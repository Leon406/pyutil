import subprocess
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
import requests
from urllib.parse import urlencode
import os

# 使用nvm安装 node
ENV_NODE_JS = os.environ.get('NVM_SYMLINK')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"

session = requests.session()

with open('getXBoGust.js', encoding="utf8") as fp:
    js_func = execjs.compile(fp.read(), cwd=ENV_NODE_JS + "\\node_modules")

headers = {
    "cookie": "strategyABtestKey=%221672340505.13%22;",
    "referer": "https://www.douyin.com/user",
    "user-agent": UA
}


def comment_list():
    # 可以删除凑数的参数
    params = _common_params()
    params["cursor"] = "0"
    params["count"] = "20"
    params["aweme_id"] = "7166234565919477005"
    _add_xbogus(params)
    print(params["X-Bogus"])

    response = session.get("https://www.douyin.com/aweme/v1/web/comment/list/?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)


def _add_xbogus(params):
    url_path = urlencode(params, safe='=')
    print(url_path)
    params["X-Bogus"] = js_func.call("getXBoGust", url_path)


def _common_params():
    return {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "pc_client_type": "1",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "108.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "108.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": "12",
        "device_memory": "8",
        "platform": "PC",
        "downlink": "10",
        "effective_type": "4g",
        "round_trip_time": "100",
        "webid": "7186820922069665295",
    }


def social_count():
    """没有校验"""
    params = _common_params()
    response = session.get("https://www.douyin.com/aweme/v1/web/social/count?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)


def user():
    """用户信息"""
    headers["cookie"] = headers["cookie"] + \
                        "ttwid=1%7CmKYQriuiDg_yUyQYU8SsO0BLRWWHot8TjPqs3zUWUsU%7C1673312168%7Cd2898f5fb30808177f883755ee3e61cf955726cc599aaef1c2574ae264160302; "

    params = _common_params()
    # params["publish_video_strategy_type"] = "2"
    params["sec_user_id"] = "MS4wLjABAAAAQf9alelOm8_s-ODwrxGOtZUAl6g8Yss2oHlrQZi8_EA"
    _add_xbogus(params)
    response = session.get("https://www.douyin.com/aweme/v1/web/user/profile/other/?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)
    print(response.json()["user"]["nickname"])


def videos():
    """主页视频"""
    headers["cookie"] = headers["cookie"] \
                        + ";" + "ttwid=1%7CmKYQriuiDg_yUyQYU8SsO0BLRWWHot8TjPqs3zUWUsU%7C1673312168%7Cd2898f5fb30808177f883755ee3e61cf955726cc599aaef1c2574ae264160302; "

    params = _common_params()
    params["sec_user_id"] = "MS4wLjABAAAAQf9alelOm8_s-ODwrxGOtZUAl6g8Yss2oHlrQZi8_EA"
    params["max_cursor"] = 1667207880000
    params["locate_query"] = False
    params["count"] = 10
    params["show_live_replay_strategy"] = 1
    params["publish_video_strategy_type"] = 2
    _add_xbogus(params)
    response = session.get("https://www.douyin.com/aweme/v1/web/aweme/post/?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)
    if response.text:
        aweme_list = response.json()["aweme_list"]

        for item in aweme_list:
            # item["duration"]
            video_info = item["video"]
            print(item["aweme_id"], item["desc"], video_info)
            print(video_info["cover"]["url_list"][0], video_info["play_addr"]["url_list"][0])


if __name__ == '__main__':
    # comment_list()
    # social_count()
    # user()
    # 不再编写完整爬取代码,请自行参考Douyin.py改写
    videos()
