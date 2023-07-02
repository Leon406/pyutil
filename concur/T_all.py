import asyncio


async def func():
    print("你好")
    await asyncio.sleep(2)
    print("Hello")
    return 2


async def func2():
    print("函数开始执行")
    resp = await func()  # 添加协程对象
    print(resp)


asyncio.run(func2())  # 传入协程对象
