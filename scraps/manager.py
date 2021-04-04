import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time


class SharedType:
    def __init__(self, custom_arg):
        self.count = 0
        self.custom_arg = custom_arg
        self.builtin_arg = []

    def accum(self):
        self.count += 1

    def get_count(self):
        return self.count

    def get_custom_arg(self):
        return self.custom_arg

    def put(self, i):
        return self.builtin_arg.append(i)

    def get(self):
        return self.builtin_arg

class CustomArg:
    def __init__(self):
        self.v = []

    def append(self, i):
        self.v.append(i)


class MyManager(BaseManager):
    pass


MyManager.register('SharedType', SharedType)


def count(obj, uid):
    print(uid, 'start')
    # record uid
    obj.get_custom_arg().append(uid)
    obj.put(uid)

    # do some work
    for _ in range(100_0000):
        obj.accum()
    return id


if __name__ == '__main__':
    print('run single process')
    st = time.time()
    c = 0
    for _ in range(10):
        for __ in range(100_000):
            c += 1
    print(c, f'elapse: {time.time() - st}')
    print()

    print('run multi process')
    st = time.time()
    pool = mp.Pool()
    with MyManager() as manager:
        shared_obj = manager.SharedType(CustomArg())
        # run
        ps = [pool.apply_async(count, args=(shared_obj, i)) for i in range(10)]
        print('waiting...')
        pool.close()
        pool.join()
        print(shared_obj.get_count(), f'elapse: {time.time() - st}')
        print(shared_obj.get_custom_arg().v, shared_obj.get())
