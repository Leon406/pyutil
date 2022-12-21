import base64
import muggle_ocr
import json
import time
import requests
from flask import Flask, request

sdk_Captcha = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
# sdk_OCR = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)

app = Flask(__name__)


# 支持 参数 url, base64,file
@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        ip = request.remote_addr
        if "X-Forwarded-For" in request.headers:
            ip = request.headers.getlist("X-Forwarded-For")[0]
        if "base64" in request.form:
            b64 = request.form['base64']
            b64 = b64[b64.find(',') + 1:]
            return classify( base64.b64decode(b64), ip)
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


def classify(bytes, ip):
    start = time.time()
    data = sdk_Captcha.predict(bytes)
    end = time.time()
    return json.dumps({'status': True, 'msg': 'SUCCESS', 'result': data, 'usage': end - start, 'ip': ip})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
