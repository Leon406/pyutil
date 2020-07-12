import re
import requests
import json
from M3u8 import M3u8
import time

res = requests.session()

maps = {}
# 拉勾通过cookies进行付费校验,必须要购买课程的
COOKIE = 'user_trace_token=20200225101518-22575ce0-8112-46ac-a704-038b9b96b89d; _ga=GA1.2.2069224394.1582596922; LGUID=20200225101519-20460062-7ff1-4746-9fff-ea885836dcec; LG_HAS_LOGIN=1; index_location_city=%E6%9D%AD%E5%B7%9E; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1590298113,1590823497,1590912149,1592307083; LG_LOGIN_USER_ID=bf2b02414504f9afa421d551576075debea8588b70b36529; privacyPolicyPopup=false; _putrc=FC755B67B4B1175F; login=true; unick=%E6%96%BD%E7%81%B5%E9%BE%99; sensorsdata2015session=%7B%7D; LGRID=20200712172852-8a836bfe-a00d-41ff-b682-2b1d871c5163; X_HTTP_TOKEN=7853a618605f1cdb63164549519344137bb1244aa1; gate_login_token=ca5ca6a779a8eae4897e3be8c3491f628a6cc347b9e0384d; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%228686565%22%2C%22%24device_id%22%3A%2216ddf03ac49303-0b8a475ad2b891-36664c08-2073600-16ddf03ac4a4ce%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24os%22%3A%22Windows%22%2C%22%24browser%22%3A%22Chrome%22%2C%22%24browser_version%22%3A%2278.0.3904.108%22%7D%2C%22first_id%22%3A%2217342cdd3d773-06ee9f6f48fb88-376b4502-2073600-17342cdd3d8af4%22%7D'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Cookie': COOKIE,
    'referer':'https://kaiwu.lagou.com/course/courseInfo.htm?courseId=67'
}

def shi(url):
    print(url)
    ss = res.get(url).text
    r = re.findall("window.courseInfo = (.+);", ss)[0]
    print(r)
    b = json.loads(r)
    print(b["courseSections"])

    for item in b["courseSections"]:

        for lesson in item["courseLessons"]:
            if "videoMedia" in lesson:
                maps[lesson["theme"]] = lesson["videoMedia"]["fileUrl"]
                print(item["sectionName"], lesson["theme"], lesson["videoMedia"]["fileUrl"])
            else:
                print(item["sectionName"], lesson["theme"], "not update")

    print(maps)
    return maps


course = "https://gate.lagou.com/v1/neirong/kaiwu/getCourseLessons?courseId=%s"


def get_course(course_id):
    ss = res.get(course % course_id,headers = headers).text
    print(ss)


if __name__ == '__main__':
    start = time.time()  # 开始时间
    url = 'https://kaiwu.lagou.com/course/courseInfo.htm?courseId=67#/detail/pc?id=1585'


    get_course(67)
    # shi(url)
    # maps = shi(url)
    # print(maps)
    # for k, v in maps.items():
    #     M3u8(v).download(k)

    print('共耗时: %s)' % (time.time() - start))
