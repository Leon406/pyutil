import os

import requests
import json
import random
import urllib3

from common.Hash import b64, url_encode

# 不良林-交流群(https://t.me/bulianglin) 学习使用，转载请保留出处
# 主要用于学习使用，代码实现了无限DISCO刷注册，导出软件里的节点
# 订阅转换 https://sub.90.ms/

"""
实现过程：
1、通过抓包，获取软件的注册接口，注册就送200G，但是注册的时候提交POST数据是加密的，必须解密得到他提交了什么数据才能脱离软件实现程序自动注册
2、反编译获取了算法，通过解密POST数据发现这个数据没有和本机的唯一识别的信息绑定（比如IMEI串号），那么每次都提交这串加密数据就可以达到无限注册了（那么加密的意义何在？）
3、编写代码，实现重复注册，并导出节点列表，每个IP可以注册10次

其实这个也可以做无限刷邀请，不过刷一次才1G流量，还不如刷注册，通过之前的抓包教程抓取注册接口加入你的邀请码即可实现，你可以尝试实现一下当做练习
"""

rootdir = os.getcwd()
proxies = {'https': '127.0.0.1:10809', 'http': '127.0.0.1:10809'}

imeis = [
    3065285382274984,
]


def ssr():
    list = os.listdir(rootdir)
    print(list)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path) and len(list[i]) == 20:
            imei = list[i].replace(".txt", "")
            # print(imei)
            with open(path) as fp:
                r = json.load(fp)
                json2ssr(r, imei)


def json2ssr(js, imei):
    for node in js['data']:
        s = f"{node['ip']}:{node['port']}:{node['protocol']}:{node['method']}:{node['obfs']}:{b64(node['passwd'])}/?{b64(node['obfsparam'])}&protoparam={b64(node['protoparam'])}&remarks={b64(node['name'])}&group={b64('leon_' + imei)}"
        print(f"ssr://{b64(s)}")


def getNode(imei=None):
    global url, headers, data
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 隐藏警告信息，可以忽略
    url = "https://discovpn.com/api/v2/trial/"  # 注册接口，通过抓包可以获得
    if not imei:
        imei = str(random.randint(1214231512312314, 9865412514251321))  # 随机生成手机串号，加入到请求头中
    # imei = "1353244593106323"
    session = requests.session()
    # r = session.get("http://www.baidu.com", proxies=proxies)
    # print(r.text)
    headers = {
        "systemVersion": "9",
        "channel": "GW",
        "appVersion": "1.0.9",
        "platform": "android",
        "Accept": "application/json",
        "imei": imei,
        "User-Agent": "okhttp/3.14.1",
        "Content-Type": "application/text; charset=utf-8"
    }  # 注册接口提交的请求头，通过抓包可以获得
    post_data = "kIva131Z8nSWEtWLHUoxNqxe6Pban1Zxa7Dpd5H6B64="  # 这段数据用的是AES加密再通过BASE64编码，解密后的内容是：{"phoneModel":"OE106"}，加密手机型号？？什么骚操作，和手机串号没有关联，那么就没有做验证，填写固定值就行了，可能是BUG，估计会被修复，不过已经知道算法了，修复了也可以算出来
    req = session.post(url, post_data, headers=headers, #proxies=proxies,
                       verify=False)  # 向服务器发送post请求
    data = json.loads(req.text)  # 服务器返回的数据交给data
    if data['message'] == "登陆成功":  # 判断是否登陆成功，成功则表示注册成功
        print("获取成功！")
        print("ID：" + imei)
        print("总流量：" + data['data']['user']['flowTotal'])
        print("已使用：" + data['data']['user']['flowUsed'])
        print("剩余流量：" + data['data']['user']['flowRemaining'])
        print("获取SSR节点列表：")
        headers['Authorization'] = 'Token ' + data['data']['token']
        req_ssr = session.post("https://discovpn.com/api/v2/nodes/", "", headers=headers,
                               # proxies=proxies,
                               verify=False)
        print(req_ssr.text)
        if req_ssr.status_code != 200:
            print("错误")
            return

        # 将节点写入到文件
        filename = rootdir + "/" + imei + '.txt'
        with open(filename, 'w') as file_object:
            file_object.write(req_ssr.text)

    elif data['message'] == "IP注册超限":  # 如果返回IP限制，则需要更换IP再注册
        print("IP注册超限！更换IP再试！")
    else:
        print("未知错误！")
        # print(req.text)  #可以打印服务器返回的结果看看是什么原因导致的


if __name__ == '__main__':
    # getNode()
    # for i in imeis:
    #     # print(i)
    #     getNode()

    ssr()
