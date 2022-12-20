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


# 支持 参数 url, base64,file
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        if "base64" in request.form:
            b64 = request.form['base64']
            b64 = b64[b64.find(',') + 1:]
            return classify(b64)
        if "url" in request.form:
            return classify(requests.get(request.form['url']).content)
        file = request.files['file']
        if file:
            filename = file.filename
            # 判断是不是图片
            if filename.split('.')[-1].lower() not in ['jpg', 'png', 'jpeg']:
                return json.dumps({'code': False, 'msg': '这不是有效的图片'})
        else:
            return json.dumps({'code': False, 'msg': '服务器错误'})

        return classify(file.read())
    except Exception as e:
        print(e)
        return json.dumps({'status': False, 'msg': str(e)})


def classify(content):
    i = get_ddddocr()
    if i == -1:
        return json.dumps({'status': False, 'msg': '没有空闲的OCR线程'})
    print("已调度线程", i)
    start = time.time()
    data = ddddocr_list[i].classification(content)
    end = time.time()
    destroy_ddddocr(i)
    print("线程", i, "已释放")
    return json.dumps({'status': True, 'msg': 'SUCCESS', 'result': data, 'usage': end - start})


if __name__ == '__main__':
    threading.Thread(target=init).start()
    app.run(host=service['listen'], port=service['port'], debug=False)
