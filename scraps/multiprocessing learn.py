import multiprocessing as mp
import threading
import time


def f(answer):
    for i in range(10_000_000):
        pass
    return answer


if __name__ == '__main__':
    s = time.time()
    p = mp.Pool(processes=32)
    r = p.map(func=f, iterable=[i for i in range(32)])
    e = time.time()
    print(e - s)

    s = time.time()
    ts = [threading.Thread(target=f, args=(i, )) for i in range(32)]
    for t in ts:
        t.start()
    e = time.time()
    print(e-s)

    s = time.time()
    for i in range(32):
        f(i)
    e = time.time()
    print(e-s)