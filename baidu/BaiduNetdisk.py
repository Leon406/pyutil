import json
import re
import time

import requests

SEARCH_KEY = "666java"
REGEXP = re.compile("【.+：666java .com】")
REG_DELETE = re.compile(r"\.url$")
REPLACE = r""

# 接口请求参数, 重命名可以不需要
BDSTOKEN = ""
# cookie信息
BDUSS_BFESS = ""
STOKEN = ""
PAGE = 3

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Mobile Safari/537.36",
    # BDUSS_BFESS STOKEN
    "Cookie": "BDUSS_BFESS=" + BDUSS_BFESS + "; STOKEN=" + STOKEN + ";"
}

API_SEARCH = "https://pan.baidu.com/api/search?app_id=250528&web=1&order=time&desc=1&num=1000&page=%s&recursion=1&key=%s"
API_RENAME = 'https://pan.baidu.com/api/filemanager'


def search(key, page=1):
    url = API_SEARCH % (page, key)
    print(url)
    response = requests.get(url, headers=headers)
    jsonStr = response.json()

    datas = jsonStr["list"]
    print(len(datas), jsonStr["has_more"])
    files = []
    dirs = []
    for data in datas:
        if data["isdir"] == 1:
            dirs.append({"id": data["fs_id"], "path": data["path"]})
        else:
            files.append({"id": data["fs_id"], "path": data["path"]})
    return jsonStr["has_more"], files, dirs


def rename(file_list):
    try_max = 5
    try_count = 0
    params = {
        'opera': 'rename',
        'async': '2',
        'onnest': 'fail',
        'bdstoken': BDSTOKEN,
        'web': '1',
        'app_id': '250528',
    }
    response = requests.post(API_RENAME, params=params, data=file_list, headers=headers)
    response.raise_for_status()
    errno = response.json()['errno']
    if errno == 0:
        print('[info] : rename successfully!')
    elif errno == 12:
        print('[warning]:批量处理错误，5s后重试 - 总数量:{}'.format(len(file_list)))
        try_count += 1
        if try_count <= try_max:
            time.sleep(5)
            rename(file_list)
        else:
            print('[error] : 批量处理错误且达到最大重试上限')
    else:
        print(response.json())
    pass


def delete(file_list):
    try_max = 3
    try_count = 0
    params = {
        'opera': 'delete',
        'async': '2',
        'onnest': 'fail',
        'bdstoken': BDSTOKEN,
        'web': '1',
        'clienttype': '0',
        'app_id': '250528',
    }
    print(file_list)
    response = requests.post(API_RENAME, params=params, data=file_list, headers=headers)
    response.raise_for_status()
    errno = response.json()['errno']
    if errno == 0:
        print('[info] : delete successfully!')
    elif errno == 12:
        print('[warning]:批量处理错误，5s后重试 - 总数量:{}'.format(len(file_list)))
        try_count += 1
        if try_count <= try_max:
            time.sleep(5)
            delete(file_list)
        else:
            print('[error] : 批量处理错误且达到最大重试上限')
    else:
        print(response.json())
    pass


if __name__ == '__main__':
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
        if REGEXP.search(file["path"]):
            name = file["path"][file["path"].rfind("/") + 1:]
            file["newname"] = REGEXP.sub(REPLACE, name)
            filelist.append(file)
        if REG_DELETE.search(file["path"]):
            deletelist.append(file["path"])

    print("=====> 重命名文件", len(filelist), filelist)
    print("=====> 删除文件", deletelist)

    if len(filelist) > 0:
        data = {"filelist": json.dumps(filelist, ensure_ascii=False)}
        rename(data)

    if len(deletelist) > 0:
        delete_data = {"filelist": json.dumps(deletelist, ensure_ascii=False)}
        delete(delete_data)
