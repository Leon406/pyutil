import base64
import re

from Crypto.Cipher import AES

from common import Hash

patter = re.compile("METHOD=(?P<method>.+),URI=\"(?P<uri>.+)\"(,IV=(?P<iv>.+))?")
if __name__ == "__main__":
    # s = '#EXT-X-KEY:METHOD=AES-128,URI="https://hls.videocc.net/d1977c4d68/2/d1977c4d684446cbb2d691241d558922_3.key"'
    # match = re.search(patter, s)
    # if match:
    #     result = match.group("method") + match.group("uri") +( match.group("iv") if match.group("iv") else "")
    # else:
    #     result = ""
    # print(result)

    key = "1234567812345678".encode()
    iv = "1234567812345678".encode()
    d = "/l2MHkUIJ+nUt2vd+A6soQ=="
    s = "hello"
    pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    crypto = AES.new(key, AES.MODE_CBC, iv)
    # print(crypto.decrypt(d))
    s = pad(s)
    print(base64.b64encode(crypto.encrypt(s.encode())))
    crypto2 = AES.new(key, AES.MODE_CBC, iv)
    str()
    print(crypto2.decrypt(base64.decodebytes(b'vkYbld7ogr5nNi/bRp6XMA==')))

    b = Hash.b64("leon")
    assert b == 'bGVvbg=='
    assert Hash.b64_decode(b) == "leon"
    assert Hash.md5("leon") == "5c443b2003676fa5e8966030ce3a86ea"
