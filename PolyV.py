#!/usr/bin/env python
# coding=utf8

import base64
import binascii
import hashlib
import json
import re

import requests
from Crypto.Cipher import AES

import sys

# =================================================================
# 下面两个参数是需要按需修改的
g_videoid = 'd06ae002cb4a0bed78fb912c874fdbb2_d'
# 如果你分析出网站怎么获取 playsafe 的，去修改 get_playsafe_token 函数, 有效期 3-5分钟
g_playsafe = 'f4056a55-33ad-4e05-ad4f-58533adc1396-e8nl4l2n3c4klc'
# =================================================================

BS = AES.block_size  # 这个等于16
mode = AES.MODE_CBC
pad = lambda s: s + (BS - len(s)) * '\0'  # 用于补全key
# 用于补全下面的text，上面两个网址就是用以下形式补全的
pad_txt = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-s[-1]]


def urlget(_url, _header={}):
    _response = requests.get(_url, headers=_header)
    return _response.content.decode('utf-8')


def urlpost(_url, _postdata, _header={}):
    _response = requests.post(_url, _postdata, headers=_header)
    return _response.content.decode('utf-8')


def hash_md5(_str):
    _hash = hashlib.md5()
    _hash.update(_str.encode('utf-8'))
    return _hash.hexdigest()


def get_playsafe_token(_vid):
    return g_playsafe


def videoinfo_decrypt(_vid, _body):
    # print("vid: " + _vid)
    _str = hash_md5(_vid)
    # print("vid md5: " + _str)
    _key = _str[0: 16]
    _iv = _str[16:]
    # print("key: " + _key + " iv: " + _iv)

    _body_raw = binascii.unhexlify(_body)

    _cryptor = AES.new(pad(_key).encode('utf-8'), mode, _iv.encode('utf-8'))
    _ret = base64.b64decode(unpad(_cryptor.decrypt(_body_raw))).decode('utf-8')
    print(_ret)
    return _ret


def decode_key(_seed_const, _key_enc):
    _aeskey = hash_md5(str(_seed_const))[0:16]
    _aesiv = b'\x01\x02\x03\x05\x07\x0B\x0D\x11\x13\x17\x1D\x07\x05\x03\x02\x01'
    # _aesiv = b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01'
    # _aesiv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    _cryptor = AES.new(pad(_aeskey).encode('utf-8'), mode, _aesiv)
    _key_paded = _cryptor.decrypt(_key_enc)
    return unpad(_key_paded)


def vidinfo(_vid):
    _url = 'https://player.polyv.net/secure/' + _vid + '.json'
    _content = urlget(_url).strip()
    if not _content:
        return None
    print(_content)
    _info_enc = json.loads(_content)
    if int(_info_enc["code"]) != 200:
        print(_info_enc)
        return None
    _body = _info_enc["body"]

    print(_body)
    _info = json.loads(videoinfo_decrypt(_vid, _body))

    return {"m3u8": _info["hls"][-1], "seed_const": _info["seed_const"]}


def main(argc, argv):
    vinfo = vidinfo(g_videoid)
    if not vinfo:
        print("get vid(%s) information error" % g_videoid)
        return 0

    m3u8content = urlget(vinfo["m3u8"])
    if not m3u8content:
        print("get m3u8(%s) error" % (vinfo["m3u8"]))
        return 0

    rem = re.search(r'URI="([^"]+)"', m3u8content, re.M | re.I)
    if not rem:
        print("m3u8 key url not found")
        return 0

    m3u8keyurl = rem.group(1).strip() + "?token=" + get_playsafe_token(g_videoid)
    print(m3u8keyurl)
    m3u8keyurl = re.sub(r'://([^/]+)/', r'://\1/playsafe/', m3u8keyurl, 1, re.I)

    r = requests.get(m3u8keyurl)
    m3u8key = r.content

    print("m3u8 key  %s" % m3u8key)

    keylen = len(m3u8key)
    print(m3u8keyurl + " key length is 32, decoding..." + r.text)
    if keylen == 32:
        with open('00.key', "wb") as f:
            print(m3u8key)
            f.write(m3u8key)
        print("key length is 32, decoding...")
        m3u8key = decode_key(vinfo["seed_const"], m3u8key)

    keyfile = g_videoid + ".key"
    with open(keyfile, "wb") as f:
        f.write(m3u8key)

    m3u8content = re.sub(r'URI="([^"]+)"', 'URI="%s"' % keyfile, m3u8content, 1, re.M | re.I)
    with open(g_videoid + ".m3u8", "wb") as f:
        f.write(m3u8content.encode('utf-8'))

    return 1


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
