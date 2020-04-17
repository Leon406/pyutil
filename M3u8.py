import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import requests
from Crypto.Cipher import AES

# 拉勾通过cookies进行付费校验,必须要购买课程的
COOKIE = 'user_trace_token=20190902123641-ac7378f0-d4b5-453c-8aec-c7e3e51ddd71; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1567399004; _ga=GA1.2.179289398.1567399004; LGUID=20190902123642-43525383-cd3b-11e9-8e56-525400f775ce; LG_HAS_LOGIN=1; fromsite=www.baidu.com; utm_source=""; PRE_UTM=; PRE_HOST=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGSID=20200417141246-8f95230e-91a9-464f-8879-b53f0b530bd3; PRE_SITE=https%3A%2F%2Fwww.lagou.com; _gat=1; privacyPolicyPopup=false; LG_LOGIN_USER_ID=2361189333f00a6a31cadeca5c8a01256836e130f55ed958; _putrc=FC755B67B4B1175F; login=true; unick=%E6%96%BD%E7%81%B5%E9%BE%99; index_location_city=%E6%9D%AD%E5%B7%9E; LGRID=20200417141445-753dc1c0-80b0-4ce7-b1e4-5ede6ac90cda; kw_login_authToken="Mk/XefUuTgVSG92jp7xp2ux1kFTqeeOL8mssZ3//nAVlNIV3fpT7+owyBKNYZyfBNK6xNd0SnDvvCv55G9TFouqwWo8D1sKneBnNzSdkO4jc4jbs8qCMwBKGQ1xJrdYQyJ1bjgHjORv6bQ6CGrk3/uDqFfrePVCXVCCWnAaQKkx4rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; gate_login_token=1ff348fa41b26014b557788a39df1a099d56ac507a7d2ed0; X_HTTP_TOKEN=a8e7355c8992eba1390401785198f39497f22d8e7b'  # 这里需要抓个cookie


def md5(str1):
    h1 = hashlib.md5()
    h1.update(str1.encode('utf-8'))
    return h1.hexdigest()


class M3u8:

    def __init__(self, url, cookie=COOKIE, core=16):
        self.url = url
        self.base_url = url[:url.rfind('/') + 1]  # 如果需要拼接url,则启用 , +1 把 / 加上
        self.tmp = md5(url)
        self.cookie = cookie
        self.executor = ThreadPoolExecutor(core)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Cookie': self.cookie
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
                    method_pos = line.find("METHOD")
                    comma_pos = line.find(",")
                    method = line[method_pos:comma_pos].split('=')[1]  # 获取加密方式
                    print("Decode Method：", method)
                    uri_pos = line.find("URI")
                    quotation_mark_pos = line.rfind('"')
                    key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
                    key_url = key_path
                    res = requests.get(key_url, headers=self.headers)
                    key = res.content  # 获取加密密钥
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

    def _download2_(self, tsUrl, key, index):
        crypto = AES.new(key, AES.MODE_CBC, key)
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
        self.download_ts()
        self.merge(file_name)


if __name__ == '__main__':
    url = 'http://1252043158.vod2.myqcloud.com/1d93b969vodtranscq1252043158/5118f4575285890800411211515/drm/v.f240.m3u8'
    start = time.time()  # 开始时间
    d = M3u8(url)
    d.download("第01讲：程序运行时，内存到底是如何进行分配的？")

    print('共耗时: %s)' % (time.time() - start))