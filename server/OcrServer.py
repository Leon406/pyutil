import ddddocr, time, json, threading, configparser, os
from flask import Flask, request
import platform
import requests

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
users = {}
restrict_users = {}
black_users = set()
SERVER_IP = "127.0.0.1"
RATE_TIME = 120
RATE_LIMIT = RATE_TIME / 10
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
    if SERVER_IP == ip:
        print(SERVER_IP, ip, SERVER_IP == ip)

    if ip in users:
        user = users[ip]
        print("current %s" % user)
        if ip in black_users:
            raise Exception("You request too much, and now in blacklist!!!")
        if time.time() - user["time"] < RATE_TIME:
            if user["count"] < RATE_LIMIT:
                user["count"] += 1
            else:
                print("black ip %s" % ip)
                if ip in restrict_users:
                    restrict_users[ip] = restrict_users[ip] + 1
                else:
                    restrict_users[ip] = 1
                print("black  %s" % restrict_users)
                if restrict_users[ip] > BLACK_OVER_LIMIT:
                    black_users.add(ip)
                raise Exception("request limit!!! Try again in %s min" % int(RATE_TIME / 60))
        else:
            reset_limit(ip)
    else:
        reset_limit(ip)


def reset_limit(ip):
    users[ip] = {
        "time": time.time(),
        "count": 1,
    }
    if ip in restrict_users:
        restrict_users.pop(ip)
    print("users %s %s" % (ip, users))


# 支持 参数 url, base64,file
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        ip = parse_ip(request)
        check_limit(ip)
        if "base64" in request.form:
            b64 = request.form['base64']
            b64 = b64[b64.find(',') + 1:]
            return classify(b64, ip)
        if "url" in request.form:
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
    print("unlock_ip", unlock_ip)
    ip = parse_ip(request)
    print("unlock black %s" % restrict_users)
    if ip in black_users:
        black_users.remove(ip)
    reset_limit(ip)
    print("after unlock black %s" % restrict_users)
    return json.dumps({'status': True, 'msg': "unlock success", 'ip': ip})


@app.route('/users', methods=['GET'])
def user():
    return json.dumps({'status': True,
                       'msg': "Success",
                       'user': users,
                       'restrict': restrict_users,
                       'black': list(black_users)})


def classify(content, ip):
    i = get_ddddocr()
    if i == -1:
        return json.dumps({'status': False, 'msg': '没有空闲的OCR线程'})
    print("已调度线程", i)
    start = time.time()
    data = ddddocr_list[i].classification(content)
    end = time.time()
    destroy_ddddocr(i)
    print("线程", i, "已释放")
    return json.dumps({'status': True, 'msg': 'SUCCESS', 'result': data, 'usage': end - start, 'ip': ip,
                       'remain': RATE_LIMIT - users[ip]["count"]})


def parse_ip(req):
    ip = request.remote_addr
    if "X-Forwarded-For" in request.headers:
        ip = request.headers.getlist("X-Forwarded-For")[0]
    return ip


if __name__ == '__main__':
    threading.Thread(target=init).start()
    app.run(host=service['listen'], port=service['port'], debug=True)
