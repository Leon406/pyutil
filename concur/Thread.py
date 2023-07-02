from concurrent.futures import ThreadPoolExecutor
from time import sleep


def func(val):
    sleep(1)
    return val


pool = ThreadPoolExecutor(max_workers=10)

results = [pool.submit(func, i) for i in range(10)]
# pool.shutdown()
for r in results:
    print(r.result())
