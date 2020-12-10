from gevent import monkey

monkey.patch_all(select=False)
from common.Io import read_lines

import grequests
import time
import multiprocessing

API = "https://www.chinapyg.com/forum.php?mod=ajax&inajax=yes&infloat=register&handlekey=register&ajaxmenu=1&action=checkinvitecode&invitecode="
head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

isResume = True


def exception_handler(request, exception):
    print("Request failed " + request.url)


if __name__ == "__main__":
    size = multiprocessing.cpu_count()
    start = time.time_ns()
    r = grequests.imap((grequests.get(API + u, timeout=5) for u in read_lines("code.txt")),
                       size=size * 2,
                       exception_handler=exception_handler)
    print(r)
    for i in r:
        print(i.url + i.text)

    print(f"grequests imap 耗时{(time.time_ns() - start) / 1000_000} ms")
    start = time.time_ns()
    mapR = grequests.map((grequests.get(API + u, timeout=5) for u in read_lines("code.txt")),
                         size=size * 2,
                         exception_handler=exception_handler)
    print(mapR)
    for i in mapR:
        print(i.url + i.text)
    print(f"grequests map 耗时{(time.time_ns() - start) / 1000_000} ms")

    # start = time.time_ns()
    # # 单线程
    # for param in read_lines("code.txt"):
    #     if param == "16121174":
    #         isResume = True
    #
    #     if not isResume:
    #         continue
    #
    #     r = requests.get(API + param, headers=head)
    #     if "抱歉，邀请码错误" in r.text:
    #         print("不可用")
    #     else:
    #         print("可用")
    #         # write("ok.txt", l)
    #
    # print(f"正常单线程 耗时{(time.time_ns() - start) / 1000_000} ms")
