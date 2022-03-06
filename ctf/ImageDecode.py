from PIL import Image

with open("1和0的故事.txt", "r") as f:
    data = [list(i.strip()) for i in f.readlines()]

# 固定大小 7*7的定位标志
flag = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]
# 二维码一共有40个尺寸 公式是：(V-1)*4 + 21（V是版本号） 最高Version 40，(40-1)*4+21 = 177 77 x 177 的正方形
size = 25
img = Image.new("1", (size, size))
for i in range(len(data)):
    for j in range(len(data[1])):
        # 左上角定位标志
        if i < 7 and j < 7:
            img.putpixel((i, j), flag[i][j] ^ 1)
        # 左下角定位标志
        elif i > size-8 and j < 7:
            img.putpixel((i, j), flag[i-(size-7)][j] ^ 1)
        # 右上角定位标志
        elif i < 7 and j > size-8:
            img.putpixel((i, j), flag[i][j-(size-7)] ^ 1)
        else:
            img.putpixel((i, j), int(data[i][j]) ^ 1)

img.resize((500, 500)).show()
