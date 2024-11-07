import base64
import hashlib
import hmac
import json
import os
import sqlite3
import struct
import zlib
from binascii import hexlify
from binascii import unhexlify
from io import BytesIO

from Crypto.Cipher import AES


# 需要keydata.json 和相关db, 放到同级目录，之后运行即可

def decrypt_and_decompress_db(db_name, key_hex):
    db_file = f'{db_name}.db'
    if not os.path.exists(db_file):
        return

    decrypted_db_file = f'{db_name}_decrypt.db'
    if os.path.exists(decrypted_db_file):
        os.remove(decrypted_db_file)

    key = unhexlify(key_hex)
    cipher = AES.new(key, AES.MODE_ECB)
    
    def decrypt_aes_ecb(data):
        if len(data) % 16 != 0:
            print("Data length should be multiple of 16.")
            return None
        return cipher.decrypt(data)
    
    def decompress_data(data):
        try:
            return zlib.decompress(data)
        except zlib.error:
            return decompress_corrupted(data)
    def decompress_corrupted(data):
        d = zlib.decompressobj(zlib.MAX_WBITS | 32)
        f = BytesIO(data)
        result_str = b''
        buffer = f.read(1)
        try:
            while buffer:
                result_str += d.decompress(buffer)
                buffer = f.read(1)
        except zlib.error:
            pass
        return result_str
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    
    decrypted_conn = sqlite3.connect(decrypted_db_file)
    decrypted_cursor = decrypted_conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cursor.fetchall()
    if not tables:
        return
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        
        create_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        create_statement += ", ".join([f"{col[1]} {col[2]}" for col in columns_info])
        create_statement += ");"
        
        decrypted_cursor.execute(create_statement)
        
        columns = [col[1] for col in columns_info]
        insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"
        
        body_index = None
        for idx, col in enumerate(columns_info):
            if col[1] == 'body' or col[1] == "data":
                body_index = idx
                break
        
        if body_index is not None:
            print(f"Decrypting and decompressing 'body' column in '{table_name}' table.")
             
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            for row in rows:
                row = list(row)
                if row[body_index] is not None:
                    decrypted_body = decrypt_aes_ecb(row[body_index])
                    decompressed_body = decompress_data(decrypted_body)
                    row[body_index] = decompressed_body
                decrypted_cursor.execute(insert_statement, row)
    
    decrypted_conn.commit()
    
    conn.close()
    decrypted_conn.close()
    print(f"All data has been decrypted, decompressed and saved to '{decrypted_db_file}'.")

def generate_hex_representation(secret_key, data_to_sign, base64_encoded_iArr,is_big=False):
    hmac_signature = hmac.new(secret_key.encode(), data_to_sign.encode(), hashlib.sha256).digest()
    decoded_bytes = base64.b64decode(base64_encoded_iArr)
    iArr = list(struct.unpack('<' + 'I' * (len(decoded_bytes) // 4), decoded_bytes))
    iArr2 = list(struct.unpack('<' + 'I' * (len(hmac_signature) // 4), hmac_signature))
    
    limit = len(iArr)
    iArr3 = [0] * limit
    for i8 in range(limit):
        iArr3[i8] = iArr[i8] ^ iArr2[i8] ^ iArr2[i8 + 4]
    if is_big:
        bytes_data = struct.pack('>' + 'I' * len(iArr3), *iArr3)
        hex_representation = hexlify(bytes_data).decode('ascii')
    else:
        bytes_data = struct.pack('<' + 'I' * len(iArr3), *iArr3)
        hex_representation = hexlify(bytes_data).decode('ascii')
    
    return hex_representation


secret_key = base64.b32decode('KNKUYMLWHBLE26LBNJQW43DKKZXGSZTDJE2GQUTVKR4W2R2ENVKE4VTZLFHTQQSZ').decode()


if __name__ == '__main__':
    keydata = json.loads(open("keydata.json").read())
    for single_key in keydata["keys"]:
        base64_encoded_iArr = keydata["keys"][single_key]["code"]
        data_to_sign = str(keydata["keys"][single_key]["expires"]) + keydata["iid"]
        if single_key == "audio":
            db_key = generate_hex_representation(secret_key,data_to_sign,base64_encoded_iArr,is_big=True)
            decrypt_and_decompress_db("haudio",db_key)
        else:
            db_key = generate_hex_representation(secret_key,data_to_sign,base64_encoded_iArr)
            decrypt_and_decompress_db(single_key,db_key)