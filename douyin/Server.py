import random
import urllib.parse

import execjs
import requests
from flask import Flask, request, jsonify
import re
import os

# 使用nvm安装 node
ENV_NODE_JS = os.environ.get('NVM_SYMLINK')

with open('X-Bogus.js', encoding="utf8") as fp:
    js_func = execjs.compile(fp.read(), cwd=ENV_NODE_JS + "\\node_modules")

app = Flask(__name__)


@app.route('/X-Bogus', methods=['POST'])
def generate_request_params():
    data = request.get_json()
    url = data.get('url')
    user_agent = data.get('user_agent')
    query = urllib.parse.urlparse(url).query
    xbogus = js_func.call('sign', query, user_agent)
    new_url = url + "&X-Bogus=" + xbogus
    response_data = {
        "param": new_url,
        "X-Bogus": xbogus,
        "msToken": generate_random_str(),
        "ttwid": ttwid(),
    }
    return jsonify(response_data)


def generate_random_str(randomlength=107):
    """
    根据传入长度产生随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
    length = len(base_str) - 1
    for _ in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def ttwid():
    json = {"region": "cn", "aid": 1768, "needFid": False, "service": "www.ixigua.com",
            "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": True}
    r = requests.post("https://ttwid.bytedance.com/ttwid/union/register/", json=json)
    print(r.text)
    cookie = r.headers['Set-Cookie']
    match = re.search("ttwid=([^;]+)", cookie)
    if match:
        result = match.group(1)
    else:
        result = ""
    print(result)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787)
