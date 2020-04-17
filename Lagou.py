import re
import requests
import json
from M3u8 import M3u8
import time

res = requests.session()

maps = {}


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


if __name__ == '__main__':
    start = time.time()  # 开始时间
    url = 'https://kaiwu.lagou.com/course/courseInfo.htm?courseId=67#/detail/pc?id=1585'

    # shi(url)
    maps = shi(url)
    print(maps)
    for k, v in maps.items():
        M3u8(v).download(k)

    print('共耗时: %s)' % (time.time() - start))
