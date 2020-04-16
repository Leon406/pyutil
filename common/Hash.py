import base64
import hashlib


def md5(str1):
    h1 = hashlib.md5()
    h1.update(str1.encode('utf-8'))
    return h1.hexdigest()


def b64(s):
    return str(base64.b64encode(s.encode('utf-8')), 'utf-8')


def b64_decode(s):
    return str(base64.b64decode(s), 'utf-8')


if __name__ == "__main_":


    pass
