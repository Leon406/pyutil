"""
欧几里得算法又称辗转相除法
"""

import math


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


"""
最小公倍数等于两数之积除以最大公约数
"""


def lcm(a, b):
    return a * b // gcd(a, b)


def countPrimes(n):
    """
     统计质数数量
    """
    if n <= 2:
        return 0
    prime = [0] * n  # 这个是类似状态组的东西
    l = int(n ** 0.5)  # 最大遍历上限为√n
    for i in range(2, l + 1):
        if prime[i]:  # 合数直接过
            continue
        prime[i * i:n:i] = [1] * len(prime[i * i:n:i])  # 如果是质数，质数平方开始到n之间步距为i的每个位置存1
    return len(prime) - sum(prime) - 2  # 输出总数字与合数的差（-2是去除0 和1）


if __name__ == "__main__":
    x = int(
        '1c7bb1ae67670f7e6769b515c174414278e16c27e95b43a789099a1c7d55c717b2f0a0442a7d49503ee09552588ed9bb6eda4af738a02fb31576d78ff72b2499b347e49fef1028182f158182a0ba504902996ea161311fe62b86e6ccb02a9307d932f7fa94cde410619927677f94c571ea39c7f4105fae00415dd7d',
        16)
    y = int(
        '2710e45014ed7d2550aac9887cc18b6858b978c2409e86f80bad4b59ebcbd90ed18790fc56f53ffabc0e4a021da2e906072404a8b3c5555f64f279a21ebb60655e4d61f4a18be9ad389d8ff05b994bb4c194d8803537ac6cd9f708e0dd12d1857554e41c9cbef98f61c5751b796e5b37d338f5d9b3ec3202b37a32f',
        16)
    print(math.gcd(x, y))
    print(lcm(x, y))
    print(gcd(x, y))
    print("__________")
    print(countPrimes(250000000))
