from gevent import monkey

monkey.patch_all(select=False)
from common.Io import read_lines, write

import grequests


API = "https://www.chinapyg.com/forum.php?mod=ajax&inajax=yes&infloat=register&handlekey=register&ajaxmenu=1&action=checkinvitecode&invitecode="
head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

isResume = True

def exception_handler(request, exception):
    print("Request failed " + request.url)

if __name__ == "__main__":
    r = grequests.imap((grequests.get(API + u, timeout=5) for u in read_lines("code.txt")), size=32,
                       exception_handler=exception_handler)
    print(r)
    for i in r:
        print(i.url + i.text)


    #单线程

    # for l in read_lines("code.txt"):
    #
    #     print("%s" % l)
    #     if l == "16121174":
    #         isResume = True
    #
    #     if not isResume:
    #         continue
    #
    #     r = requests.get(API + l, headers=head)
    #     print(API+l)
    #     if "抱歉，邀请码错误" in r.text:
    #         print("不可用")
    #     else:
    #         print("可用")
    #         write("ok.txt", l)
