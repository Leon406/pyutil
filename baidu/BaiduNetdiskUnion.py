import re
import json
import time
import requests

# 需要接入百度网盘SDK https://pan.baidu.com/union/doc/Jl0j9pza3
ACCESS_TOKEN = ""
SEARCH_KEY = "学习"
DIR = "/"
API_SEARCH = (f"http://pan.baidu.com/rest/2.0/xpan/file?dir={DIR}&access_token={ACCESS_TOKEN}"
              f"&recursion=1&page=%s&method=search&key=%s")
PAGE = 3

# REGEXP = re.compile("_?【瑞客论坛 www\.ruike1\.com】|(瑞客论坛 www.ruike1.com)?\[瑞客论坛 www.ruike1.com]|\[瑞客论坛 www\.ruike1\.com]")
REGEXP = re.compile("\[瑞客论坛 www.ruike1.com]")
REPLACE = r""
REG_DELETE = re.compile(r"\.url$")
headers = {
    'User-Agent': 'pan.baidu.com'
}

API_FILE_MANAGER = f'http://pan.baidu.com/rest/2.0/xpan/file?method=filemanager&access_token={ACCESS_TOKEN}&opera=%s'
API_RENAME = API_FILE_MANAGER % "rename"
API_DELETE = API_FILE_MANAGER % "delete"


def search(key, page=1):
    url = API_SEARCH % (page, key)
    # print(url)
    response = requests.get(url, headers=headers)
    jsonStr = response.json()
    print(jsonStr)
    if 'has_more' not in jsonStr:
        return 0, [], []

    datas = jsonStr["list"]
    print(len(datas), jsonStr["has_more"])
    files = []
    dirs = []
    for data in datas:
        print(data)
        if data["isdir"] == 1:
            dirs.append({"id": data["fs_id"], "path": data["path"]})
        else:
            files.append({"id": data["fs_id"], "path": data["path"]})
    return jsonStr["has_more"], files, dirs


def rename(file_list):
    try_max = 5
    try_count = 0
    params = {
        'async': '2',
        'ondup': 'fail',
        'filelist': json.dumps(file_list, ensure_ascii=False),
    }
    response = requests.post(API_RENAME,data=params, headers=headers)
    response.raise_for_status()
    errno = response.json()['errno']
    if errno == 0:
        print('[info] : rename successfully!')
    elif errno == 12:
        print(response.json())
        print('[warning]:批量处理错误，5s后重试 - 总数量:{}'.format(len(file_list)))
        try_count += 1
        if try_count <= try_max:
            time.sleep(5)
            rename(file_list)
        else:
            print('[error] : 批量处理错误且达到最大重试上限')
    else:
        print(response.json())


def delete(file_list):
    try_max = 3
    try_count = 0
    params = {
        'async': '2',
        'ondup': 'fail',
        'filelist': json.dumps(file_list, ensure_ascii=False),
    }
    print(file_list)
    response = requests.post(API_DELETE, data=params, headers=headers)
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
        print(filelist)
        rename(filelist)
    #
    if len(deletelist) > 0:
        delete_data = {"filelist": json.dumps(deletelist, ensure_ascii=False)}
        delete(deletelist)
