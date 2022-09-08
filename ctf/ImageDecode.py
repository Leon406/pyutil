import math

from PIL import Image

# 二维码 固定大小 7*7的定位标志
mark = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]


def read(file="bin"):
    with open(file, "r") as f:
        lists = [list(i.strip()) for i in f.readlines()]
    datas = "".join('%s' % "".join(a) for a in lists)
    size = int(math.sqrt(len(datas)))
    return datas, size


def show_image(file="bin", fill_mark=False):
    (datas, size) = read(file)
    img = Image.new("1", (size, size))
    showSize = max(size * 2, 500)
    for i in range(size):
        for j in range(size):
            if fill_mark:
                # 左上角定位标志
                if i < 7 and j < 7:
                    img.putpixel((i, j), mark[i][j] ^ 1)
                # 左下角定位标志
                elif i > size - 8 and j < 7:
                    img.putpixel((i, j), mark[i - (size - 7)][j] ^ 1)
                # 右上角定位标志
                elif i < 7 and j > size - 8:
                    img.putpixel((i, j), mark[i][j - (size - 7)] ^ 1)
                else:
                    img.putpixel((i, j), int(datas[i * size + j]) ^ 1)
            else:
                img.putpixel((i, j), int(datas[i * size + j]) ^ 1)

    img.resize((showSize, showSize)).show()


if __name__ == '__main__':
    show_image("bin")
    show_image("1和0的故事.txt", True)
