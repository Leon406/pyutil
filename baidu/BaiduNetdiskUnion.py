import json
import re
import time

import requests

# 需要接入百度网盘SDK https://pan.baidu.com/union/doc/Jl0j9pza3
ACCESS_TOKEN = ""

SEARCH_KEY = "瑞客论坛"
DIR = "/ALIST/02. java/2023-黑马java V13.0"
API_SEARCH = (
    f"http://pan.baidu.com/rest/2.0/xpan/file?dir={DIR}&access_token={ACCESS_TOKEN}"
    f"&recursion=1&page=%s&method=search&key=%s"
)
PAGE = 20

REGEXP = re.compile(
    "_?【瑞客论坛 www\.ruike1\.com】|(瑞客论坛 www.ruike1.com)?\[瑞客论坛 www.ruike1.com]|\[瑞客论坛 www\.ruike1\.com]"
)
# REGEXP = re.compile("\[瑞客论坛 www.ruike1.com]")
# 自定义水印
REPLACE = r""
# REG_DELETE = re.compile(r"\.url$")
REG_DELETE = re.compile(r"/target/(?:test-classes|maven-status|classes)")
headers = {"User-Agent": "pan.baidu.com"}

API_FILE_MANAGER = f"http://pan.baidu.com/rest/2.0/xpan/file?method=filemanager&access_token={ACCESS_TOKEN}&opera=%s"
API_RENAME = API_FILE_MANAGER % "rename"
API_DELETE = API_FILE_MANAGER % "delete"


def search(key, page=1):
    url = API_SEARCH % (page, key)
    response = requests.get(url, headers=headers)
    jsonStr = response.json()
    # print(jsonStr)
    if "has_more" not in jsonStr:
        return 0, [], []

    datas = jsonStr["list"]
    print(len(datas), jsonStr["has_more"])
    files = []
    dirs = []
    for data in datas:
        # print(data)
        if data["isdir"] == 1:
            dirs.append({"id": data["fs_id"], "path": data["path"]})
        else:
            files.append({"id": data["fs_id"], "path": data["path"]})
    return int(jsonStr["has_more"]), files, dirs


def rename(file_list):
    """
    https://pan.baidu.com/union/doc/mksg0s9l4
    """
    try_max = 5
    try_count = 0
    params = {
        # async 0 同步，1 自适应，2 异步
        "async": 0,
        "ondup": "fail",
        "filelist": json.dumps(file_list, ensure_ascii=False),
    }
    response = requests.post(API_RENAME, data=params, headers=headers)
    response.raise_for_status()
    errno = response.json()["errno"]
    # print(response.json())
    if errno == 0:
        print(f"[info] : rename successfully! {len(file_list)}")
    elif errno == 12:
        needRetry = False
        for item in response.json()["info"]:
            # -9	文件不存在 -7	文件名非法 111	有其他异步任务正在执行
            if item["errno"] not in [-9, 111]:
                needRetry = True
            else:
                pass
                # print(item["errno"])
        if not needRetry:
            return

        print("[warning]:批量处理错误，5s后重试 - 总数量:{}".format(len(file_list)))
        try_count += 1
        if try_count <= try_max:
            time.sleep(5)
            rename(file_list)
        else:
            print("[error] : 批量处理错误且达到最大重试上限")
    else:
        print(response.json())


def delete(file_list):
    try_max = 3
    try_count = 0
    params = {
        "async": 0,
        "ondup": "fail",
        "filelist": json.dumps(file_list, ensure_ascii=False),
    }
    # print(file_list)
    response = requests.post(API_DELETE, data=params, headers=headers)
    response.raise_for_status()
    errno = response.json()["errno"]
    if errno == 0:
        print(f"[info] : delete successfully! {len(file_list)}")
    elif errno == 12:
        needRetry = False
        for item in response.json()["info"]:
            # -9	文件不存在 -7	文件名非法 111	有其他异步任务正在执行
            if item["errno"] not in [-9, 111]:
                needRetry = True
            else:
                pass
                # print(item)
        if not needRetry:
            return

        print("[warning]:批量处理错误，5s后重试 - 总数量:{}".format(len(file_list)))
        try_count += 1
        if try_count <= try_max:
            time.sleep(5)
            rename(file_list)
        else:
            print("[error] : 批量处理错误且达到最大重试上限")
    else:
        print(response.json())
    pass


def check():
    page = 1
    has_more, files, dirs = search(SEARCH_KEY, page)
    print(files)
    filelist = []
    deletelist = []
    while has_more == 1 and page < PAGE:
        page += 1
        print(f"=========>{page}")
        has_more, tmp_files, tmp_dirs = search(SEARCH_KEY, page)
        print(f"=========> has_more{has_more}")
        files.extend(tmp_files)
        dirs.extend(tmp_dirs)
    print("=====> 匹配文件", len(files))
    print("=====> 匹配文件夹", len(dirs))
    for file in files:
        if REG_DELETE.search(file["path"]):
            deletelist.append(file["path"])
        elif REGEXP.search(file["path"]):
            name = file["path"][file["path"].rfind("/") + 1:]
            file["newname"] = REGEXP.sub(REPLACE, name)
            filelist.append(file)
    fileListLen = len(filelist)
    print("=====> 重命名文件", fileListLen, filelist)
    print("=====> 删除文件", deletelist)
    if fileListLen > 0:
        # print(filelist)
        iteration = (fileListLen // 1000) + 1
        for i in range(0, iteration):
            fr = 1000 * i
            end = 1000 * (i + 1)
            print(f"{fr} -> {end} {i}")
            rename(filelist[fr: end])
    #
    if len(deletelist) > 0:
        delete(deletelist)



if __name__ == "__main__":
    for i in range(1, 100):
        check()
        time.sleep(60)
