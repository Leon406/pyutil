import subprocess
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs
import requests
from urllib.parse import urlencode
import os

# 使用nvm安装 node
ENV_NODE_JS = os.environ.get('NVM_SYMLINK')

# UA必须跟获取cookie的浏览器一致
UA = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edg/120.0.0.0"

session = requests.session()

with open('X-Bogus.js', encoding="utf8") as fp:
    js_func = execjs.compile(fp.read(), cwd=ENV_NODE_JS + "\\node_modules")

headers = {
    #  2023/03/17 后台加入cookie校验  s_v_web_id必须先过验证
    "cookie": "ttwid=1%7COtR5WXtMgJiC7pmdAtIhiZPIEflB-wn6uFgjYO0zffk%7C1690424153%7Caf85812ecbaed24088a0adf8b37bb4fc7b4fd46228f50600f984a4d2946f51f0; ",
    "referer": "https://www.douyin.com/user",
    "user-agent": UA
}


def comment_list():
    # 可以删除凑数的参数
    params = _common_params()
    params["cursor"] = "0"
    params["count"] = "20"
    params["aweme_id"] = "7166234565919477005"
    _add_xbogus2(params, UA)
    print(params["X-Bogus"])

    response = session.get("https://www.douyin.com/aweme/v1/web/comment/list/?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)


def _add_xbogus2(params, user_agent):
    url_path = urlencode(params, safe='=')
    print(url_path, user_agent)
    params["X-Bogus"] = js_func.call("sign", url_path, user_agent)
    print( params["X-Bogus"])


def _common_params():
    return {
        "device_platform":"webapp",
        "aid":"6383",
        "channel":"channel_pc_web",
        # "sec_user_id":"MS4wLjABAAAAHBzaYq41eZhmDn9cOTQya8X3-YxoAYTOLm1BM947R_A",
        "max_cursor":"0",
        "locate_query":"false",
        "show_live_replay_strategy":"1",
        "need_time_list":"1",
        "time_list_query":"0",
        "whale_cut_token":"",
        "cut_version":"1",
        # "count":"18",
        "publish_video_strategy_type":"2",
        "pc_client_type":"1",
        "version_code":"170400",
        "version_name":"17.4.0",
        "cookie_enabled":"true",
        "screen_width":"354",
        "screen_height":"852",
        "browser_language":"zh-CN",
        "browser_platform":"Win32",
        "browser_name":"Edge",
        "browser_version":"120.0.0.0",
        "browser_online":"true",
        "engine_name":"Blink",
        "engine_version":"120.0.0.0",
        "os_name":"Android",
        "os_version":"6.0",
        "cpu_core_num":"12",
        "device_memory":"8",
        "platform":"Android",
        "downlink":"10",
        "effective_type":"4g",
        "round_trip_time":"250",
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
                        "ttwid=1%7COtR5WXtMgJiC7pmdAtIhiZPIEflB-wn6uFgjYO0zffk%7C1690424153%7Caf85812ecbaed24088a0adf8b37bb4fc7b4fd46228f50600f984a4d2946f51f0; "

    params = _common_params()
    # params["publish_video_strategy_type"] = "2"
    params["sec_user_id"] = "MS4wLjABAAAAQf9alelOm8_s-ODwrxGOtZUAl6g8Yss2oHlrQZi8_EA"
    _add_xbogus2(params, UA)
    response = session.get("https://www.douyin.com/aweme/v1/web/user/profile/other/?" + urlencode(params, safe='='),
                           headers=headers)
    print(response.text)
    print(response.json()["user"]["nickname"])


def videos():
    """主页视频"""
    params = _common_params()
    params["sec_user_id"] = "MS4wLjABAAAAHBzaYq41eZhmDn9cOTQya8X3-YxoAYTOLm1BM947R_A"
    # params["max_cursor"] = 1667207880000
    # params["locate_query"] = False
    params["count"] = 18
    # params["show_live_replay_strategy"] = 1
    # params["publish_video_strategy_type"] = 2
    _add_xbogus2(params, UA)
    print(urlencode(params, safe='='))
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

    # ttwid可用通过Server.py 获取
    # 必须更换 UA/Cookie 2024年1月24日09:08:01 测试可用
    videos()
