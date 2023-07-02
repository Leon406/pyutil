import asyncio
import time


async def func1():
    print(1)
    # 网络 IO 请求
    await asyncio.sleep(2)  # 遇到 IO 耗时操作，自动切换
    print(2)


async def func2():
    print(3)
    # 网络 IO 请求
    await asyncio.sleep(2)  # 遇到 IO 耗时操作，自动切换
    print(4)


def func2_block():
    print(3)
    # 网络 IO 请求
    time.sleep(2)
    print(4)


async def func():
    print("你好")
    await asyncio.sleep(2)
    print("Hello")
    return 2


async def func2():
    print("函数开始执行")
    resp = await func()  # 添加协程对象
    print(f"{time.ctime()}：", resp)


async def main():
    tasks = [asyncio.create_task(func2()) for i in range(3)]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    asyncio.run(main())  # 传入协程对象
    # func2_block()
    # func2_block()
    # func2_block()
    print("end")
