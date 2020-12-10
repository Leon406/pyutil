import hashlib
import os
import os.path
import re
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import requests
from Crypto.Cipher import AES

# 拉勾通过cookies进行付费校验,必须要购买课程的
COOKIE = 'user_trace_token=20201008114240-e5eb483e-259c-471f-98d0-972759067854; LGUID=20201008114240-8ab68cbf-5ce1-474a-8fe5-6db15997e83b; _ga=GA1.2.1060024075.1602128562; LG_LOGIN_USER_ID=93d8bc8949775963477a4b5279adc64a00917ba8876659b7; LG_HAS_LOGIN=1; _putrc=FC755B67B4B1175F; login=true; unick=%E6%96%BD%E7%81%B5%E9%BE%99; privacyPolicyPopup=false; index_location_city=%E6%9D%AD%E5%B7%9E; gate_login_token=c08d65506a14efd8336554e28bc61dd7e715a6753c1b5536; PRE_UTM=; PRE_HOST=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGSID=20201008123152-3aed06a2-a093-4ae9-bb21-e3194cca62f5; PRE_SITE=https%3A%2F%2Fwww.lagou.com; LGRID=20201008123152-9693a202-1e27-49dc-a46b-1233f745f413; _gat=1; X_HTTP_TOKEN=f9cc62e35a90c00671513120613d0475f7ed28a585'
PATTERN = re.compile("MEA?THOD=(?P<method>.+),URI=\"(?P<uri>.+)\"(,IV=(?P<iv>.+))?")

POLYV = 'hls.videocc.net'
POLYV_SAFE = '0b888fc8-dbed-4957-b143-ab5b4642df50-t8nl45lc755k10'


def md5(str1):
    h1 = hashlib.md5()
    h1.update(str1.encode('utf-8'))
    return h1.hexdigest()


class M3u8:

    def __init__(self, url, cookie=COOKIE, core=16):
        self.url = url
        self.base_url = url[:url.rfind('/') + 1]  # 如果需要拼接url,则启用 , +1 把 / 加上
        self.tmp = md5(url)
        self.keys = {}
        self.cookie = cookie
        self.executor = ThreadPoolExecutor(core)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4195.1 Safari/537.36',
            'Cookie': self.cookie,
            'Referer': 'https://kaiwu.lagou.com/course/courseInfo.htm?courseId=500'
        }

    def download_ts(self):

        rs = requests.get(self.url, headers=self.headers).text
        list_content = rs.split('\n')
        player_list = []

        if not os.path.exists(self.tmp):
            os.system('mkdir ' + self.tmp)
        key = ''
        for index, line in enumerate(list_content):
            # 判断视频是否经过AES-128加密
            if "#EXT-X-KEY" in line:
                if not key:
                    match = re.search(PATTERN, line)
                    if match:
                        result = match.group("method") + match.group("uri") + (
                            match.group("iv") if match.group("iv") else "")
                    else:
                        result = ""
                    print(result)
                    print("Decode Method：", match.group("method"))
                    key_url = match.group("uri")
                    print(key_url)
                    if "http" not in key_url:
                        key_url = self.url[:self.url.rfind('/') + 1] + key_url
                        print(key_url)
                    if key_url in self.keys and self.keys[key_url]:
                        key = self.keys[key_url]
                        print("key from cache")
                    else:
                        if POLYV in key_url:
                            key_url = '%s?token=%s' % (
                            key_url.replace('hls.videocc.net/', 'hls.videocc.net/playsafe/'), POLYV_SAFE)
                            print("polyV url " + key_url)
                        res = requests.get(key_url, headers=self.headers)
                        key = res.content  # 获取加密密钥
                        with open('m.key', "wb") as f:
                            f.write(key)
                        print(res.text)
                        if key:
                            self.keys[key_url] = key
                            print("cache key ")
                        else:
                            print("错误码: %s" % res.status_code)
                    print("key：", key)
            # 以下拼接方式可能会根据自己的需求进行改动
            if '#EXTINF' in line:
                # href = ''
                # 如果加密，直接提取每一级的.ts文件链接地址
                if 'http' in list_content[index + 1]:
                    href = list_content[index + 1]
                    player_list.append(href)
                # 如果没有加密，构造出url链接
                elif 'ad0.ts' not in list_content[index + 1]:
                    href = self.base_url + list_content[index + 1]
                    player_list.append(href)
        if len(key):
            print('此视频经过加密')
            print(player_list)  # 打印ts地址列表

            tasks = [self.executor.submit(self._download2_, tsUrl, key, i) for i, tsUrl in enumerate(player_list)]
            wait(tasks, return_when=ALL_COMPLETED)

            print('下载完成')

        else:
            print('此视频未加密')
            print(player_list)  # 打印ts地址列表
            tasks = [self.executor.submit(self._download_, tsUrl, i) for i, tsUrl in enumerate(player_list)]
            wait(tasks, return_when=ALL_COMPLETED)
            print('下载完成')

    def _download_(self, tsUrl, index):
        res = requests.get(tsUrl, headers=self.headers)
        with open(self.tmp + '/' + str(index + 1) + '.ts', 'wb') as file:
            file.write(res.content)
            print('正在写入第{}个文件'.format(index + 1))

    def _download2_(self, tsUrl, key, index, iv=None):
        if not iv:
            iv = key

        crypto = AES.new(key, AES.MODE_CBC, iv)
        res = requests.get(tsUrl, headers=self.headers)
        with open(self.tmp + '/' + str(index + 1) + '.ts', 'wb') as file:
            file.write(crypto.decrypt(res.content))  # 将解密后的视频写入文件
            print('正在写入第{}个文件'.format(index + 1))

    def merge(self, file_name):
        c = os.listdir(self.tmp)
        with open('%s.mp4' % file_name, 'wb+') as f:
            for i in range(len(c)):
                x = open(self.tmp + '/' + str(i + 1) + '.ts', 'rb').read()
                f.write(x)

        print('合并完成')
        os.system('rd /s/q ' + self.tmp)  # 这里如果试Linux 把rm -tf改成rm -rf

    def download(self, file_name):
        if os.path.exists(file_name + ".mp4"):
            print(file_name, "已存在")
            return

        self.download_ts()
        self.merge(file_name)


if __name__ == '__main__':
    url = 'https://vod.lagou.com/b595ca64be404e02aa83afcefa3ce342/81f06756dbbbf061cf46bf087044e1f5-hd-encrypt-stream.m3u8'
    url = 'https://vod.lagou.com/55d71556af874cb1a5450eeb309110da/34e1e259a2155b1daea5905b49bd122f-sd-encrypt-stream.m3u8'
    url = 'https://1252524126.vod2.myqcloud.com/9764a7a5vodtransgzp1252524126/47fccaa55285890784299740979/drm/v.f230.m3u8'
    url = 'https://hls.videocc.net/d06ae002cb/2/d06ae002cb4a0bed78fb912c874fdbb2_2.m3u8?pid=1604812797069X1989802&device=desktop'
    url = 'http://1252524126.vod2.myqcloud.com/9764a7a5vodtransgzp1252524126/e3def9065285890783868358884/drm/v.f230.m3u8'

    start = time.time()  # 开始时间
    d = M3u8(url)
    d.download("课程")

    print('共耗时: %s' % (time.time() - start))
