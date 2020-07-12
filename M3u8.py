import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import requests
from Crypto.Cipher import AES

# 拉勾通过cookies进行付费校验,必须要购买课程的
COOKIE = 'user_trace_token=20200225101518-22575ce0-8112-46ac-a704-038b9b96b89d; _ga=GA1.2.2069224394.1582596922; LGUID=20200225101519-20460062-7ff1-4746-9fff-ea885836dcec; LG_HAS_LOGIN=1; index_location_city=%E6%9D%AD%E5%B7%9E; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1590298113,1590823497,1590912149,1592307083; LG_LOGIN_USER_ID=bf2b02414504f9afa421d551576075debea8588b70b36529; privacyPolicyPopup=false; _putrc=FC755B67B4B1175F; login=true; unick=%E6%96%BD%E7%81%B5%E9%BE%99; sensorsdata2015session=%7B%7D; LGRID=20200712172852-8a836bfe-a00d-41ff-b682-2b1d871c5163; X_HTTP_TOKEN=7853a618605f1cdb63164549519344137bb1244aa1; JSESSIONID=ABAAAECABCAAACDBB0F68BFE0B41CFBB638401F2B0B0AB5; gate_login_token=ca5ca6a779a8eae4897e3be8c3491f628a6cc347b9e0384d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%228686565%22%2C%22%24device_id%22%3A%2216ddf03ac49303-0b8a475ad2b891-36664c08-2073600-16ddf03ac4a4ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24os%22%3A%22Windows%22%2C%22%24browser%22%3A%22Chrome%22%2C%22%24browser_version%22%3A%2278.0.3904.108%22%7D%2C%22first_id%22%3A%2217342cdd3d773-06ee9f6f48fb88-376b4502-2073600-17342cdd3d8af4%22%7D'


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
                    print(key_url)
                    if key_url in self.keys and self.keys[key_url]:
                        key = self.keys[key_url]
                        print("key from cache")
                        pass
                    else:
                        res = requests.get(key_url, headers=self.headers)
                        key = res.content  # 获取加密密钥
                        if key:
                            self.keys[key_url] = key
                            print("cache key ")
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
    url = 'http://1252043158.vod2.myqcloud.com/1d93b969vodtranscq1252043158/6167e9a85285890805041608626/drm/v.f240.m3u8'
    start = time.time()  # 开始时间
    d = M3u8(url)
    d.download("第32讲：解析动态权限适配遇到的问题")

    print('共耗时: %s)' % (time.time() - start))
