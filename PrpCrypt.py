import base64

from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms

'''
AES/CBC/PKCS7Padding 加密解密
环境需求:
pip3 install pycryptodome
'''


class PrpCrypt:

    def __init__(self, key='1234567812345678'):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC
        self.iv = b'1234567812345678'
        self.decryptor = AES.new(self.key, self.mode, self.iv)
        self.encryptor = AES.new(self.key, self.mode, self.iv)
        # block_size 128位

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16但是不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        text = self.pkcs7_padding(text.encode('utf-8'))
        ciphertext = self.encryptor.encrypt(text)
        aes_base64 = base64.encodebytes(ciphertext)
        return str(aes_base64, "utf-8").strip()

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def decrypt(self, text):
        text = base64.decodebytes(text.encode('utf-8'))
        decrypted_text = str(self.decryptor.decrypt(text), 'utf-8').replace('\0', '') \
            .replace('\x01', '').replace('\x02', '').replace('\x03', '') \
            .replace('\x04', '').replace('\x05', '').replace('\x06', '') \
            .replace('\x07', '').replace('\x08', '').replace('\x09', '') \
            .replace('\x0a', '').replace('\x0b', '').replace('\x0c', '') \
            .replace('\x0d', '').replace('\x0e', '').replace('\x0f', '').replace('\x10', '')
        return decrypted_text


# 加解密
if __name__ == '__main__':
    pc = PrpCrypt()
    a = "感谢"
    print(pc.decrypt('/l2MHkUIJ+nUt2vd+A6soQ=='))
    print("加密前：%s" % a)
    b = pc.encrypt(a)
    print("解密后：%s" % b)

