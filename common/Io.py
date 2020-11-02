# import grequests
import time
import json


# 读取文档
def read_lines(path):
    with open(path, 'r', encoding="UTF-8") as f:
        txt = []
        for s in f.readlines():
            txt.append(s.strip())
    return txt


# 读取文档
def read(path):
    with open(path, 'r', encoding="UTF-8") as f:
        return f.readlines()


# 读取json
def read_json(path):
    with open(path, 'r', encoding="UTF-8") as f:
        return json.load(f)


# 清空文档
def truncate_file(path):
    with open(path, 'w', encoding='utf-8') as f:
        f.truncate()


# 写入文档
def write(path, text):
    with open(path, 'a', encoding='utf-8') as f:
        f.writelines(text)
        f.write('\n')


if __name__ == "__main__":
    print(str(read("Io.py")))
    start = time.time()
    # tasks = [
    #     grequests.get("http://baidu.com",
    #                   timeout=5) for d in range(1, 100)]
    # print(tasks)
    # res = grequests.map(tasks)
    # for i, r in enumerate(res):
    #     if r:
    #         if r.status_code == 200:
    #             print(r.text)

    print(time.time() - start)
