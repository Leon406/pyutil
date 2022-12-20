import math
import random

from Crypto.Util.number import long_to_bytes

p = 0

# 设置模数
def GF(a):
    global p
    p = a


# 乘法取模
def g(a, b):
    global p
    return pow(a, b, p)


def AMM(x, e, p):
    GF(p)
    y = random.randint(1, p - 1)
    while g(y, (p - 1) // e) == 1:
        y = random.randint(1, p - 1)
        print(y)
    print("find")
    # p-1 = e^t*s
    t = 1
    while p % e == 0:
        t += 1
        print(t)
    s = p // (e ** t)
    print('e', e)
    print('p', p)
    print('s', s)
    print('t', t)
    # s|ralpha-1
    k = 1
    while (s * k + 1) % e != 0:
        k += 1
    print('k', k)
    alpha = (s * k + 1) // e
    # 计算a = y^s b = x^s h =1
    # h为e次非剩余部分的积
    t_s = e ** (t - 1) * s
    print("bigInteger",t_s)
    a = g(y, t_s)
    b = g(x, e * alpha - 1)
    c = g(y, s)
    h = 1

    print('alpha', alpha)
    print('a', a)
    print('b', b)
    print('c', c)
    #
    for i in range(1, t - 1):
        print("___________")
        d = g(b, e ** (t - 1 - i))
        if d == 1:
            j = 0
        else:
            j = -math.log(d, a)
        b = b * (g(g(c, e), j))
        h = h * g(c, j)
        c = g(c, e)
    # return (g(x, alpha * h)) % p
    root = g(x, alpha * h)
    roots = set()
    for i in range(e):
        mp2 = root * g(a, i) % p
        assert (g(mp2, e) == x)
        roots.add(mp2)
    return roots


def check(m):
    if 'flag' in m:
        print(m)
        return True
    else:
        return False


e = 1801
c = 821562155714228494350968286343241874202753771452745916900616612053610190986294297934462409534126095213198464996196364868528238538372119009517541428785632007137206972918081643841690069171088425923887930051635578719252415693144672179185417101210954906623326286804995637775062840407550493095027500638719998
p = 19897846550210846565807788524492364050901480736489979129040638436463635149815428186161001280958415730930156556581274966745574164608778242980049611665461488306439665507971670397595035647317930606555771720849158745264269952668944940061576328219674721623208805067371087817766416300084129945316973502412996143
mps = AMM(c, e, p)
for mpp in mps:
    solution = str(long_to_bytes(mpp))
    if check(solution):
        print(solution)
