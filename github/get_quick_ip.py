import datetime
import os
import time
import platform
import requests

DOHs = ["https://dns.alidns.com/resolve",
        "https://rubyfish.cn/dns-query",
        # cloudflare-dns.com 国内被墙, 换ip可以正常访问
        "https://1.1.1.1/dns-query",
        "https://doh.360.cn/query",
        "https://doh.pub/dns-query",
        # 国内被墙
        # "https://dns.google/resolve"
        ]

doh_header = {
    "user-source": "360se",
    "accept": "application/dns-json",
    "user-identity": "12345678901234567890123456789012345678901234",
}

sess = requests.session()


def get_ip_from_doh(site, dohIndex=2):
    res = sess.get("%s?name=%s&type=1" % (DOHs[dohIndex], site), headers=doh_header, timeout=30)
    print(DOHs[dohIndex])
    for i in res.json()['Answer']:
        if i['type'] == 1:
            # print(i['data'])
            trueip = i['data']
            if check_ping(trueip):
                print("ok %s" % trueip)
            else:
                print("fail %s" % trueip)
                dohIndex = dohIndex + 1
                return get_ip_from_doh(site, dohIndex % len(DOHs))

            return i['data']


def get_ip(site):
    return addr2ip[site] if site in addr2ip else get_ip_from_doh(site)


def check_ping(server):
    print(platform.system())
    if platform.system() == "Windows":
        response = os.system("ping -n 1 %s" % server)
    else:
        response = os.system("ping -c 1 %s" % server)
    # print("result: ", response)
    return response == 0


# 需要获取ip的网址
sites = [
    'avatars.githubusercontent.com',
    'codeload.github.com',
    'github-cloud.s3.amazonaws.com',
    'github-com.s3.amazonaws.com',
    'github.githubassets.com',
    # 国内DNS已被污染严重,无法正常解析
    'github.global.ssl.fastly.net',
    'gist.github.com',
    'assets-cdn.github.com',
    'api.github.com',
    'githubapp.com',
    'live.github.com',
    'status.github.com',
    'collector.githubapp.com',
    'github.blog',
    'central.github.com',
    'desktop.githubusercontent.com',
    'i.imgur.com',
]

# 相同ip映射表,减少网络请求数量
gp = {
    # githubusercontent
    "avatars.githubusercontent.com": ['avatars.githubusercontent.com',
                                      'camo.githubusercontent.com',
                                      'user-images.githubusercontent.com',
                                      'gist.githubusercontent.com',
                                      'raw.github.com',
                                      'raw.githubusercontent.com',
                                      'cloud.githubusercontent.com',
                                      'media.githubusercontent.com',
                                      'github.map.fastly.net',
                                      ],

    "github-cloud.s3.amazonaws.com": ['github-cloud.s3.amazonaws.com',
                                      'github-production-release-asset-2e65be.s3.amazonaws.com',
                                      'github-production-user-asset-6210df.s3.amazonaws.com'
                                      ],
    "gist.github.com": ['gist.github.com',
                        'github.com',
                        'www.github.com'],
    "github-com.s3.amazonaws.com": ['github-com.s3.amazonaws.com',
                                    'github-production-repository-file-5c1aeb.s3.amazonaws.com',
                                    ],
    "codeload.github.com": ['codeload.github.com',
                            'nodeload.github.com',
                            ],
    "github.githubassets.com": ['github.githubassets.com',
                                'help.github.com',
                                ],
    "collector.githubapp.com": ['collector.githubapp.com'],
    "live.github.com": ['live.github.com', 'alive.github.com'],
    "assets-cdn.github.com": ['assets-cdn.github.com', 'pages.github.com', 'training.github.com', 'github.io',
                              'githubstatus.com', 'documentcloud.github.com',
                              'customer-stories-feed.github.com', ]

}

addr2ip = {}
# hostLocation = r"./github/hosts"
hostLocation = r"hosts" if platform.system() == "Windows" else r"./github/hosts"


def dropDuplication(line):
    flag = False
    if "#*********************github" in line:
        return True
    for site in sites:
        if site in gp and gp[site]:
            for gsite in gp[site]:
                if gsite in line:
                    flag = flag or True
                else:
                    flag = flag or False
        else:
            flag = flag or site in line
    return flag


# 更新host, 并刷新本地DNS
def updateHost():
    print(sorted(sites, key=lambda i: i[0]))
    fail_ips = []
    ok = []
    while len(ok) != len(sites):
        a = [i for i in sites if i not in ok]
        print(a)
        for site in a:
            trueip = get_ip(site)
            if trueip:
                if site in gp and gp[site]:
                    for gsite in gp[site]:
                        addr2ip[gsite] = trueip
                    # print(str(gp[site]) + "\t" + trueip)
                else:
                    addr2ip[site] = trueip
                    # print(site + "\t" + trueip)
                ok.append(site)
                print("进度 %d / %d" % (len(ok), len(sites)))
            else:
                fail_ips.append(site)
            # print("剩余 %d / %d" % (len(ok), len(sites)))
        time.sleep(3)
    write_hosts(hostLocation)


def write_hosts(path):
    today = datetime.date.today()
    with open(path, "r") as f1:
        f1_lines = f1.readlines()
        with open("temphost", "w") as f2:
            f2.write("#*********************github " +
                     str(today) + " update********************\n")
            for line in f1_lines:  # 为了防止 host 越写用越长，需要删除之前更新的含有github相关内容
                if not dropDuplication(line):
                    f2.write(line)

            for key in addr2ip:
                f2.write(addr2ip[key] + "\t" + key + "\n")
    os.remove(path)
    os.rename("temphost", path)


if __name__ == '__main__':
    okIps = []
    failDomains = []
    with open(hostLocation, "r") as f1:
        f1_lines = f1.readlines()
        for i in f1_lines:
            l = i.replace("\n", "").split('\t')
            if len(l) > 1:
                print(l)
                addr2ip[l[1]] = l[0]
                if l[0] not in okIps:
                    if check_ping(l[0]):
                        okIps.append(l[0])
                    else:
                        print("fail _________", l[0], l[1])
                        failDomains.append(l[1])
        print(addr2ip)
        print(failDomains)
    updateHost()
    # check_ping("192.168.10.1")
    # getIpFromDoH("github.global.ssl.fastly.net", 4)
