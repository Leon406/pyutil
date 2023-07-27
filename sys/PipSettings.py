import os
import platform
from subprocess import check_output, call


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


def upgrade_all():
    output = check_output(['pip', 'list'])
    # 处理输出
    libraries = output.decode().split('\n')
    installed_libraries = [lib.split() for lib in libraries
                           # if 'grequests' in lib
                           ]
    # 打印结果
    for library in installed_libraries:
        if len(library) > 1:
            print(library[0] + ' ' + library[1])
            call('pip install --user --upgrade ' + library[0], shell=True)


if __name__ == "__main__":
    # pip_source()
    upgrade_all()
