from common.Io import read_lines, write, truncate_file
from gevent import monkey

monkey.patch_all()
import grequests
import multiprocessing

# http://free.proxypool.cc/ip.txt
# http://amp.tsddos.cc/1001/proxy4.txt
PROXY_PATH = "proxy/pool"
PROXY_OK_PATH = "proxy_ok.txt"
API = "https://www.baidu.com?c="
head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


def proxies(ip):
    return {"https": ip, "http": ip}


def exception_handler(request, exception):
    print("Request failed " + request.url + str(exception))


def gCheck():
    lines = read_lines(PROXY_PATH)

    size = multiprocessing.cpu_count()
    r = grequests.imap((grequests.get(API + u, timeout=5, proxies=proxies(u)) for u in lines),
                       size=size * 2,
                       exception_handler=exception_handler)
    # print(r)
    for i in r:
        print(i.url[25:])
        print(i.text)
        write(PROXY_OK_PATH, i.url[25:])


if __name__ == "__main__":
    gCheck()
    # lines = read_lines(PROXY_PATH)
    # print(lines)
    # ss = requests.session()
    # for ip in lines:
    #     try:
    #         r = ss.get(API, proxies=proxies(ip), timeout=2)
    #         if r.status_code == 200:
    #             print(ip)
    #             write(PROXY_OK_PATH, ip)
    #     except Exception as e:
    #         print(str(e))
