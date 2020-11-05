import base64
import hashlib
import urllib.parse


def md5(str1):
    h1 = hashlib.md5()
    h1.update(str1.encode('utf-8'))
    return h1.hexdigest()


def b64(s):
    return str(base64.b64encode(s.encode('utf-8')), 'utf-8')


def b64_decode(s):
    return str(base64.b64decode(s), 'utf-8')


def url_encode(s):
    return urllib.parse.quote(s)


def url_decode(s):
    return urllib.parse.unquote(s)


if __name__ == "__main__":
    print(b64("Leon"))
    print(url_encode("中国"))
    print(url_decode("%E4%B8%AD%E5%9B%BD"))
