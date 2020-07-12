import requests
import json


def download_from_url(down_url, dst):
    req = requests.get(down_url)
    if req.status_code == 302:
        print()
    print(req)
    with(open(dst, 'wb')) as f:
        print("write")
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


if __name__ == "__main__":
    with open(r"E:\file\pyutil\c.json", 'r', encoding="utf-8") as f:
        s1 = json.load(f)
        print(s1['content']['courseSectionList'])

        for item in s1['content']['courseSectionList']:
            # print(item['courseLessons'])
            for course in item['courseLessons']:
                if (course["videoMediaDTO"]):
                    print(course["theme"], course["videoMediaDTO"]["fileUrl"])
                else:
                    print(course["theme"], "未更新")
