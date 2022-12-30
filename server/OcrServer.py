import configparser
import json
import os
import platform
import re
import threading
import time

import ddddocr
import requests
from flask import Flask, request

# ImportError: libGL.so 解决方案  https://www.cnblogs.com/mrneojeep/p/16252044.html
# ubuntu
# apt-get update && apt-get install libgl1
#  CentOS、RHEL、Fedora 或其他使用 的 linux 发行版yum
# yum install mesa-libGL -y

# 读取service.conf配置文件
config = configparser.ConfigParser()
config.read('service.conf', encoding='utf-8')
service = config['service']

app = Flask(__name__)

ddddocr_list = []
ddddocr_state = []
USERS = {}
RESTRICT_USERS = {}
black_users = set()
SERVER_IP = "127.0.0.1"
black_users.add(SERVER_IP)
RATE_TIME = 3600
global RATE_LIMIT
global BLACK_OVER_LIMIT
RATE_LIMIT = int(RATE_TIME / 60)
BLACK_OVER_LIMIT = RATE_LIMIT


def init():
    t = service['worker_threads']
    t = int(t)
    for i in range(t):
        ddddocr_list.append(ddddocr.DdddOcr())
        ddddocr_state.append(0)
        os.system('cls' if "window" in platform.platform().lower() else "clear")

    print("init success")


def get_ddddocr():
    for i in range(len(ddddocr_state)):
        if ddddocr_state[i] == 0:
            ddddocr_state[i] = 1
            return i
    return -1


def destroy_ddddocr(i):
    ddddocr_state[i] = 0
    return 0


def check_limit(ip):
    if ip in USERS and SERVER_IP != ip:
        current_user = USERS[ip]
        print("current %s" % current_user)
        if ip in black_users:
            raise Exception("You request too much, and now in blacklist!!!")
        if time.time() - current_user["time"] < RATE_TIME:
            if current_user["count"] < RATE_LIMIT:
                current_user["count"] += 1
            else:
                print("black ip %s" % ip)
                if ip in RESTRICT_USERS:
                    RESTRICT_USERS[ip] = RESTRICT_USERS[ip] + 1
                else:
                    RESTRICT_USERS[ip] = 1
                print("black  %s" % RESTRICT_USERS)
                if RESTRICT_USERS[ip] > BLACK_OVER_LIMIT:
                    black_users.add(ip)
                raise Exception("request limit!!! Try again in %s min" % int(RATE_TIME / 60))
        else:
            reset_limit(ip)
    else:
        reset_limit(ip)


def reset_limit(ip):
    USERS[ip] = {
        "time": time.time(),
        "count": 0,
    }
    if ip in RESTRICT_USERS:
        RESTRICT_USERS.pop(ip)
    print("users %s %s" % (ip, USERS))


# 支持 参数 url, base64,file
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        if "x-requested-with" not in request.headers and "X-Requested-With" not in request.headers:
            return json.dumps({'code': False, 'msg': '请求错误'})
        xrw = request.headers.getlist("x-requested-with") or request.headers.getlist("X-Requested-With")
        if xrw[0] != "XMLHttpRequest":
            return json.dumps({'code': False, 'msg': 'error'})
        ip = parse_ip(request)
        check_limit(ip)
        if "base64" in request.form:
            b64 = request.form['base64']
            b64 = b64[b64.find(',') + 1:]
            return classify(b64, ip)
        if "url" in request.form:
            pre_request = requests.head(request.form['url'])
            length = 0
            if "Content-Length" in pre_request.headers:
                length = pre_request.headers["Content-Length"]
            elif "content-length" in pre_request.headers:
                length = pre_request.headers["content-length"]

            # 校验图片大小
            if length:
                if int(length) < 64 * 1024:
                    return classify(requests.get(request.form['url']).content, ip)
                else:
                    return json.dumps({'code': False, 'msg': '文件大于64k'})
            else:
                return classify(requests.get(request.form['url']).content, ip)

        file = request.files['file']
        if file:
            filename = file.filename
            # 判断是不是图片
            if filename.split('.')[-1].lower() not in ['jpg', 'png', 'jpeg']:
                return json.dumps({'code': False, 'msg': '这不是有效的图片'})
        else:
            return json.dumps({'code': False, 'msg': '服务器错误'})

        return classify(file.read(), ip)
    except Exception as e:
        print(e)
        return json.dumps({'status': False, 'msg': str(e)})


@app.route('/unlock/<unlock_ip>', methods=['PUT'])
def unlock(unlock_ip):
    print(f"unlock_ip {unlock_ip}")
    ip = parse_ip(request)
    print("unlock", ip == SERVER_IP, unlock_ip in black_users)
    if ip == SERVER_IP and unlock_ip in black_users:
        black_users.remove(unlock_ip)
        reset_limit(unlock_ip)
        print("after unlock black %s" % RESTRICT_USERS)
        return json.dumps({'status': True, 'msg': "unlock success", 'ip': ip})
    else:
        return json.dumps({'status': False, 'msg': "Server Error!", 'ip': ip})


@app.route('/rate/<rate_count>', methods=['PUT'])
def rate(rate_count):
    ip = parse_ip(request)
    rate_count = int(rate_count)
    if rate_count < 0:
        return json.dumps({'status': False, 'msg': "wrong rate", 'ip': ip})
    else:
        global RATE_LIMIT
        # 不限制,
        if rate_count == 0:
            rate_count = RATE_TIME * 10
        if ip == SERVER_IP and rate_count != RATE_LIMIT:
            print(f"old= {RATE_LIMIT}, new= {rate_count}")
            RATE_LIMIT = rate_count
            return json.dumps({'status': True, 'msg': "success", 'ip': ip, 'rate': RATE_LIMIT})
        else:
            return json.dumps({'status': False, 'msg': "sever error", 'ip': ip, 'rate': RATE_LIMIT})


@app.route('/users', methods=['GET'])
def user():
    return json.dumps({'status': True,
                       'msg': "Success",
                       'user': USERS,
                       'restrict': RESTRICT_USERS,
                       'black': list(black_users)})


def classify(content, ip):
    i = get_ddddocr()
    if i == -1:
        return json.dumps({'status': False, 'msg': '没有空闲的OCR线程'})
    if i != 0:
        print("已调度线程", i)
    start = time.time()
    data = post_process(ddddocr_list[i].classification(content))
    print("reco====>", data)
    end = time.time()
    destroy_ddddocr(i)
    if i != 0:
        print("线程", i, "已释放")
    return json.dumps({'status': True, 'msg': 'SUCCESS', 'result': data, 't': round(end - start, 3), 'ip': ip,
                       'remain': RATE_LIMIT - USERS[ip]["count"]})


def parse_ip(req):
    ip = req.remote_addr
    if "X-Forwarded-For" in req.headers:
        ip = req.headers.getlist("X-Forwarded-For")[0]
    return ip


regex_chinese = re.compile("[\u4e00-\u9fa5]+")
regex_line = re.compile("""^[-)(/一_>=<+,]|[-)(/一_>=<+,]$""")


def post_process(data: str) -> str:
    """处理识别后的字符串,干扰线"""
    after = regex_line.sub("", data)
    chinese = regex_chinese.findall(data)
    if chinese:
        count = 0
        for i in chinese:
            count += len(i)
        #  不支持中英混合, 比例小于1/4删除
        if count / len(data) < 0.26:
            after = regex_chinese.sub("", after)

    if after != data:
        print(f"process {data} ==> {after} ")
    return after


if __name__ == '__main__':
    threading.Thread(target=init).start()
    app.run(host=service['listen'], port=service['port'], debug=True)
