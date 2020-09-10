import datetime
import json
import os
import re

import requests
from bs4 import BeautifulSoup


def getIpFromIpaddress(site):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/737.36(KHTML, like Gecke) Chrome/52.0.2743.82 Safari/537.36',
        'Host': 'ipaddress.com'}
    url = "https://ipaddress.com/search/" + site
    trueip = None
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", res.text)
        result = soup.find_all('div', class_="comma-separated")
        for c in result:
            if len(ip) != 0:
                trueip = ip[0]
    except Exception as e:
        print("查询" + site + " 时出现错误: " + str(e))
    return trueip


def getIpFromChinaz(site):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/737.36(KHTML, like Gecke) Chrome/52.0.2743.82 Safari/537.36',
        'Host': 'ip.tool.chinaz.com'}
    url = "http://ip.tool.chinaz.com/" + site
    trueip = None
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        result = soup.find_all('span', class_="Whwtdhalf w15-0")
        for c in result:
            ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", c.text)
            if len(ip) != 0:
                trueip = ip[0]
    except Exception as e:
        print("查询" + site + " 时出现错误: " + str(e))
    return trueip


def getIpFromWhatismyipaddress(site):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/737.36(KHTML, like Gecke) Chrome/52.0.2743.82 Safari/537.36',
        'Host': 'ip.tool.chinaz.com'}
    url = "https://whatismyipaddress.com/hostname-ip"
    data = {
        "DOMAINNAME": site,
        "Lookup IP Address": "Lookup IP Address"
    }
    trueip = None
    try:
        res = requests.post(url, headers=headers, data=data, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        result = soup.find_all('span', class_="Whwtdhalf w15-0")
        for c in result:
            ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", c.text)
            if len(ip) != 0:
                trueip = ip[0]
    except Exception as e:
        print("查询" + site + " 时出现错误: " + str(e))
    return trueip


def getIpFromipapi(site):
    """
    return trueip: None or ip
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/737.36(KHTML, like Gecke) Chrome/52.0.2743.82 Safari/537.36',
        'Host': 'ip-api.com'}
    url = "http://ip-api.com/json/%s?lang=zh-CN" % site
    trueip = None
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res = json.loads(res.text)
        if res["status"] == "success":
            trueip = res["query"]
    except Exception as e:
        print("查询" + site + " 时出现错误: " + str(e))
    return trueip


# 需要获取ip的网址
sites = [
    'assets-cdn.github.com',
    'avatars0.githubusercontent.com',
    'api.github.com',
    'codeload.github.com',
    'documentcloud.github.com',
    'github.global.ssl.fastly.net',
    'gist.github.com',
    'github.githubassets.com',
    'githubapp.com',
    'github.com',
    'github-production-release-asset-2e65be.s3.amazonaws.com',
    'github-cloud.s3.amazonaws.com',
    'github-com.s3.amazonaws.com',
    'live.github.com',
    'pages.github.com',
    'status.github.com',
    'training.github.com',
]

# 相同ip映射表,减少网络请求数量
gp = {
    # githubusercontent
    "avatars0.githubusercontent.com": ['avatars0.githubusercontent.com',
                                       'avatars1.githubusercontent.com',
                                       'avatars2.githubusercontent.com',
                                       'avatars3.githubusercontent.com',
                                       'avatars4.githubusercontent.com',
                                       'avatars5.githubusercontent.com',
                                       'avatars6.githubusercontent.com',
                                       'avatars7.githubusercontent.com',
                                       'avatars8.githubusercontent.com',
                                       'camo.githubusercontent.com',
                                       'user-images.githubusercontent.com',
                                       'gist.githubusercontent.com',
                                       'raw.github.com',
                                       'raw.githubusercontent.com',
                                       'cloud.githubusercontent.com',

                                       ],
    # amazonaws relese download
    "github-cloud.s3.amazonaws.com": ['github-cloud.s3.amazonaws.com',
                                      'github-production-user-asset-6210df.s3.amazonaws.com',
                                      ],
    "github-com.s3.amazonaws.com": ['github-com.s3.amazonaws.com',
                                    'github-production-repository-file-5c1aeb.s3.amazonaws.com',
                                    ],
    "codeload.github.com": ['codeload.github.com',
                            'nodeload.github.com',
                            ],
    "github.githubassets.com": ['github.githubassets.com',
                                'help.github.com',
                                ],
    "documentcloud.github.com": ['documentcloud.github.com',
                                 'customer-stories-feed.github.com',
                                 ],

}

addr2ip = {}
hostLocation = r"hosts"


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
    today = datetime.date.today()
    for site in sites:
        trueip = getIpFromChinaz(site)
        if trueip:
            if site in gp and gp[site]:
                for gsite in gp[site]:
                    addr2ip[gsite] = trueip
                    print(gsite + "dd\t" + trueip)
            else:
                addr2ip[site] = trueip
                print(site + "\t" + trueip)

    with open(hostLocation, "r") as f1:
        f1_lines = f1.readlines()
        with open("temphost", "w") as f2:
            f2.write("#*********************github " +
                     str(today) + " update********************\n")
            for line in f1_lines:  # 为了防止 host 越写用越长，需要删除之前更新的含有github相关内容
                if not dropDuplication(line):
                    f2.write(line)

            for key in addr2ip:
                f2.write(addr2ip[key] + "\t" + key + "\n")
    os.remove(hostLocation)
    os.rename("temphost", hostLocation)


if __name__ == '__main__':
    updateHost()
