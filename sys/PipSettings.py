import platform
import os
from pip._internal.utils.misc import get_installed_distributions
from subprocess import call

# requestments.txt  pipreqs --debug  --pypi-server http://pypi.douban.com/simple ./ --encoding=utf-8


def pip_source():
    os_type = platform.system()
    if "Linux" == os_type:
        fileDirPath = "%s/.pip" % os.path.expanduser('~')
        filePath = "%s/pip.conf" % fileDirPath
        if not os.path.isdir(fileDirPath):
            os.mkdir(fileDirPath)
        fo = open(filePath, "w")
        fo.write(
            "[global]\nindex-url=https://pypi.tuna.tsinghua.edu.cn/simple/\n[install]\ntrusted-host=pypi.tuna.tsinghua.edu.cn\n")
        fo.close()
        print("Configuration is complete")
    elif "Windows" == os_type:
        fileDirPath = "%s\\pip" % os.path.expanduser('~')
        filePath = "%s\\pip.ini" % fileDirPath
        if not os.path.isdir(fileDirPath):
            os.mkdir(fileDirPath)

        print(filePath)
        fo = open(filePath, "w")
        fo.write(
            "[global]\nindex-url=https://pypi.tuna.tsinghua.edu.cn/simple/\n[install]\ntrusted-host=pypi.tuna.tsinghua.edu.cn\n")
        fo.close()
        print("Configuration is complete")
    else:
        exit("Your platform is unknow!")


def pipUpdateAll():
    for dist in get_installed_distributions():
        call('pip install --user --upgrade ' + dist.project_name, shell=True)


if __name__ == "__main__":
    # pip_source()
    pipUpdateAll()
