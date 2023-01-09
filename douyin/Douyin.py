import json
import os
import re
import time
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from douyin.browser_cookie3 import load


def write(path, text):
    with open(path, 'a', encoding='utf-8') as f:
        f.writelines(text)
        f.write('\n')


sess = requests.session()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76",
    "referer": "https://www.douyin.com/user/"
}


def get_cookie_from_browser(site='https://www.douyin.com'):
    """直接读取浏览器的 cookie 数据库，优先返回 Firefox cookie，最后为 Chrome
    """
    cookie = {}
    domain = re.match(r".*://([^/]+)/?", site)
    domain = domain.groups()[0]
    domain = domain.split(".")
    domain = ".".join(domain[-2:])
    cookies = load(domain_name=domain)
    for c in cookies:
        if c.domain in site:
            cookie[c.name] = c.value
    return cookie


cookie_jar = get_cookie_from_browser("https://www.douyin.com")
print(cookie_jar)
msToken = cookie_jar["msToken"]
print("msToken", msToken)

# 可输入链接：https://v.douyin.com/dMAhh44/
# inputUrl = input('粘贴分享链接：')
shorts = ["https://v.douyin.com/dMAhh44/"]
pubdateUrl = "https://www.douyin.com/video/%s?secUid=%s"


def download(to_date=None, from_date=None, need_cover=False):
    if not to_date:
        end_date = datetime.today()
    else:
        if len(to_date) == 10:
            end_date = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        elif len(to_date) == 7:
            end_date = datetime.strptime(to_date, "%Y-%m").replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")

    if not from_date:
        stop_date = datetime.strptime("2016-09-20", "%Y-%m-%d")
    else:
        if len(from_date) == 10:
            stop_date = datetime.strptime(from_date, "%Y-%m-%d")
        elif len(from_date) == 7:
            stop_date = datetime.strptime(from_date, "%Y-%m")
        else:
            stop_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")

    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    count = 0
    print('=====爬取时间范围====>', datetime.strftime(stop_date, "%Y-%m-%d %H:%M:%S"),
          datetime.strftime(end_date, "%Y-%m-%d %H:%M:%S"))

    while start_date >= stop_date:
        params = {
            'sec_uid': sec_uid,
            'count': 200,
            'min_cursor': int(start_date.timestamp() * 1000),
            'max_cursor': int(end_date.timestamp() * 1000),
        }
        awemeurl = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
        awemehtml = sess.get(url=awemeurl, params=params, headers=headers, cookies=cookie_jar).text
        if not awemehtml:
            continue
        data = json.loads(awemehtml)
        print(start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'))
        count += len(data['aweme_list'])

        for item in data['aweme_list']:
            video_url = item['video']['play_addr']['url_list'][0]
            video_id = item['aweme_id']
            proper_title = re.sub(r"[@#][^ ]+ *", "", item['desc'])
            proper_title = re.sub("[\n/?|<>]", "", proper_title) \
                .replace(":", "：")
            print(f'\t===>downloading {proper_title}  {video_id}')
            download_video(video_url, proper_title)

            if need_cover:
                videoCoverurl = item['video']['origin_cover']['url_list'][0]
                download_video(videoCoverurl, proper_title, '.jpeg')

        end_date = start_date
        start_date = start_date - relativedelta(months=1)
        if end_date > stop_date and start_date < stop_date:
            start_date = stop_date

    print(f"\ncount= {count}")


def download_video(url, name, ext='.mp4'):
    start = time.time()
    file_name = name + ext
    path = saveFileDir + "/" + file_name
    if not os.path.exists(path):
        with open(path, 'wb') as v:
            try:
                v.write(requests.get(url=url, headers=headers).content)
                cost = int((time.time() - start) * 1000)
                print(f'\t\t>>>downloaded {file_name} ===>cost {cost} ms')
            except Exception as e:
                print('\tdownload error', e)
    else:
        print(f'\t\t!!!exist {file_name}')


for inputUrl in shorts:
    shortUrl = re.findall('[a-z]+://[\\S]+', inputUrl, re.I | re.M)[0]
    print(shortUrl)

    startPage = sess.get(shortUrl, headers=headers, allow_redirects=False)
    location = startPage.headers['location']
    print("location", location)
    sec_uid = re.findall('(?<=sec_uid=)[\\w -]+', location, re.M | re.I)[0]
    print("sec_uid",sec_uid)
    req_url = 'https://www.douyin.com/aweme/v1/web/social/count?' \
              'device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1' \
              '&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1603' \
              '&screen_height=902&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge' \
              '&browser_version=108.0.1462.76&browser_online=true&engine_name=Blink&engine_version=108.0.0.0' \
              '&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10' \
              '&effective_type=4g&round_trip_time=50&webid=7186641719562339895' \
              '&msToken={}&X-Bogus=DFSzswVOMgUANVEgSDNWXQppgiFE'.format(sec_uid, msToken)
    print(req_url)
    name = sess.get(req_url,
                    headers=headers, cookies=cookie_jar).text
    print(name)
    userinfo =name and json.loads(name)
    name = userinfo and userinfo['user_info']['nickname'] or "dy"
    print(name)

    saveFileDir = name

    if not os.path.exists(saveFileDir):
        os.mkdir(saveFileDir)
    else:
        print('directory exist')

    download("2022-01", "2021-01-30 12:58:23")
