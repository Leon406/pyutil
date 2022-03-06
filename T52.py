import json
import os
import re
import time
import requests

sess = requests.session()
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Mobile Safari/537.36"
}
# 可输入链接：https://v.douyin.com/dMAhh44/
# inputUrl = input('粘贴分享链接：')
shorts = ["https://v.douyin.com/dMAhh44/", "https://v.douyin.com/dMAhh44/"]

for inputUrl in shorts:

    shortUrl = re.findall('[a-z]+://[\\S]+', inputUrl, re.I | re.M)[0]
    print(shortUrl)

    startPage = sess.get(shortUrl, headers=headers, allow_redirects=False)
    location = startPage.headers['location']
    sec_uid = re.findall('(?<=sec_uid=)[\\w -]+', location, re.M | re.I)[0]
    name = sess.get('https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={}'.format(sec_uid),
                    headers=headers).text
    userinfo = json.loads(name)
    name = userinfo['user_info']['nickname']
    print(name)

    saveFileDir = name

    if not os.path.exists(saveFileDir):
        os.mkdir(saveFileDir)
    else:
        print('directory exist')
    # os.chdir(saveFileDir)

    year = ('2018', '2019', '2020', '2021')
    month = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
    timepool = [x + '-' + y + '-01 00:00:00' for x in year for y in month]
    print(timepool)

    k = len(timepool)
    for i in range(k):
        if i < k - 1:
            # print('begintime=' + timepool[i])
            # print('endtime=' + timepool[i + 1])
            beginarray = time.strptime(timepool[i], "%Y-%m-%d %H:%M:%S")
            endarray = time.strptime(timepool[i + 1], "%Y-%m-%d %H:%M:%S")
            t1 = int(time.mktime(beginarray) * 1000)
            t2 = int(time.mktime(endarray) * 1000)
            # print(t1, t2)

            params = {
                'sec_uid': sec_uid,
                'count': 200,
                'min_cursor': t1,
                'max_cursor': t2,
                'aid': 1128,
                '_signature': 'PtCNCgAAXljWCq93QOKsFT7QjR'
            }
            awemeurl = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
            awemehtml = sess.get(url=awemeurl, params=params, headers=headers).text
            data = json.loads(awemehtml)
            for item in data['aweme_list']:
                # videotitle = re.sub(r"[^\w]", "", item['desc'])
                # 想保留什么在中括号里加,保留逗号  r"[^\w，]"
                videotitle = re.sub(r"[^\w，]", "", item['desc'])
                videourl = item['video']['play_addr']['url_list'][0]
                start = time.time()
                print('{} ===>downloading'.format(videotitle))
                with open(saveFileDir+"/"+videotitle + '.mp4', 'wb') as v:
                    try:
                        v.write(requests.get(url=videourl, headers=headers).content)
                        end = time.time()
                        cost = end - start
                        print('{} ===>downloaded ===>cost {}s'.format(videotitle, cost))
                    except Exception as e:
                        print('download error')
