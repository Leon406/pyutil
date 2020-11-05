import requests
from sys import stdout
import os

#  gdown --id 1jtyEOcDpG1IU2aqBPwStoUkoyJrMJDTt
# youtube-dl https://drive.google.com/open?id=1jtyEOcDpG1IU2aqBPwStoUkoyJrMJDTt


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    print(response.headers)
    filesize = 1000000000
    times = int(filesize) // CHUNK_SIZE
    show = 1 / times
    show2 = 1 / times
    start = 1
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
            if start <= times:
                stdout.write(f"\r下载进度: {show:.2%}")
                start += 1
                show += show2
            else:
                stdout.write("\r下载进度: 100%")
            # print("\n结束下载")


if __name__ == "__main__":
    file_id = '1jtyEOcDpG1IU2aqBPwStoUkoyJrMJDTt'
    destination = '1.mp4'
    download_file_from_google_drive(file_id, destination)
