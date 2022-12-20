import json
import os
import re
import time
import requests


def write(path, text):
    with open(path, 'a', encoding='utf-8') as f:
        f.writelines(text)
        f.write('\n')


sess = requests.session()
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Mobile Safari/537.36"
}

cookieHeader = {
    "cookie": "ttwid=1%7CgJ88Stv_G9XBVobEtBIglIdKnhaED8AJHdorw8fpjRc%7C1658801882%7C5c8122de28bfe6035ecc81c774ff59f5b7f6083b8354df948f5e27e108a3f93f; s_v_web_id=verify_l61jt9vh_Cj3rJtyh_lM2e_4hYW_BIYQ_BvAvj8s61YSV; passport_csrf_token=08dd53df16d6d731308551a256a42aca; passport_csrf_token_default=08dd53df16d6d731308551a256a42aca; douyin.com; odin_tt=8c104948316aadeccc316f50632c739e29a3cf87965ef58a1aea0be7c7cbc48eb7e0deb89f760243f8bd1dc4998180ddc16f6643c9f2de9e4942911ca95d367e; _tea_utm_cache_1243=undefined; MONITOR_WEB_ID=b1a13eee-10b3-4405-b17f-bf52bd0e028a; _tea_utm_cache_2018=undefined; download_guide=%223%2F20220817%22; IS_HIDE_THEME_CHANGE=%221%22; THEME_STAY_TIME=%22299739%22; strategyABtestKey=1661139548.537; __ac_nonce=063032fe4009d1dba7897; __ac_signature=_02B4Z6wo00f01FVg.oQAAIDDndw3mCj4BYhVQPoAAHZiYRMjEgEsPH0kWWTJVeoX83-gThd-MYoqL9VesTplQ07.Ps2lR-A9GRTM5DHuZTGxR8FM4ZQWwZjvlY7XE5qOVOSWlKGcQIMfjxWpd3; tt_scid=bhgVQ-oEnPScYZQLpvlhlu1uwy1Kp8Gq1fGRGznJHRCyhgYjF.vgJVVfpsGNOJbff3f7; msToken=2eOkmWiEF1Jjw7dHYxXGxja-UbQUBY-8C4sjfV-_fCALx_71vsdHyspmUzvFkHWI587UpQfzQxzgg-fU57dH13wxC2xbMs6M7c0nC-sY6OJ-fSC9u0ChZJpAgsfA-wtcweA=; msToken=HRdDjqETOyLic_Z_cmLRErv3uIA5_8dMKHwpLy4KKO2lQH7hgDKsI1Mx8P-vUMxcx1OkIRPClVCy8OkrnTdlJJTmygc__7uwYFnoEXCtPRt9PdGMpIUTRGL_NSAFjbPz7U4=; home_can_add_dy_2_desktop=%221%22"
}
# 可输入链接：https://v.douyin.com/dMAhh44/
# inputUrl = input('粘贴分享链接：')
# shorts = ["https://v.douyin.com/dMAhh44/"]
shorts = ["https://v.douyin.com/jf66Np3/"]
pubdateUrl = "https://www.douyin.com/video/%s?secUid=%s"

for inputUrl in shorts:

    shortUrl = re.findall('[a-z]+://[\\S]+', inputUrl, re.I | re.M)[0]
    print(shortUrl)

    startPage = sess.get(shortUrl, headers=headers, allow_redirects=False)
    location = startPage.headers['location']
    print(location)
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

    year = ('2018', '2019', '2020', '2021', '2022')
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
            print(t1, t2)

            params = {
                'sec_uid': sec_uid,
                'count': 200,
                'min_cursor': t1,
                'max_cursor': t2,
            }
            awemeurl = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
            awemehtml = sess.get(url=awemeurl, params=params, headers=headers).text
            data = json.loads(awemehtml)
            # print(awemehtml)
            for item in data['aweme_list']:
                # videotitle = re.sub(r"[^\w]", "", item['desc'])
                # 想保留什么在中括号里加,保留逗号  r"[^\w，]"
                # videotitle = re.sub(r"[^\w，]", "", item['desc'])
                videourl = item['video']['play_addr']['url_list'][0]
                videoCoverurl = item['video']['origin_cover']['url_list'][0]
                videoId = item['aweme_id']
                videotitle = videoId
                start = time.time()
                print('{} ===>downloading'.format(videotitle))
                saveFile = saveFileDir + "/" + videoId + '.mp4'
                metaFile = saveFileDir + "/meta.csv"

                properTitle = re.sub(r"[@#][^ ]+ *", "", item['desc'])
                url = pubdateUrl % (item['aweme_id'], sec_uid)
                html = requests.get(url=url, headers=cookieHeader).text
                # date = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', html, re.I | re.M)[0]
                date = ""
                print("%s,%s,%s" % (videoId, properTitle, date))
                # if not os.path.exists(saveFile):
                #     write(metaFile, "%s,%s,%s" % (item['aweme_id'], properTitle, date))
                #     with open(saveFile, 'wb') as v:
                #         try:
                #             v.write(requests.get(url=videourl, headers=headers).content)
                #             end = time.time()
                #             cost = end - start
                #             print('{} ===>downloaded ===>cost {}s'.format(videoId, cost))
                #         except Exception as e:
                #             print('download error')
                # else:
                #     print('%s exist ' % saveFile)

                # saveFile = saveFileDir + "/" + videoId + '.jpeg'
                # if not os.path.exists(saveFile):
                #     with open(saveFile, 'wb') as v:
                #         try:
                #             v.write(requests.get(url=videoCoverurl, headers=headers).content)
                #             end = time.time()
                #             cost = end - start
                #             print('{} ===>downloaded image ===>cost {}s'.format(videoId, cost))
                #         except Exception as e:
                #             print('download error')
                # else:
                #     print('%s exist ' % saveFile)
