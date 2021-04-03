import threading
import time
import random

class A:
    def __init__(self):
        self.arr = []

    def add_a(self, lock):
        with lock:
            for _ in range(5):
                self.arr.append('a')
                time.sleep(random.uniform(0, 0.1))

    def add_b(self, lock):
        with lock:
            for _ in range(5):
                self.arr.append('b')

a = A()
lock0 = threading.Lock()
lock1 = threading.Lock()

t0 = threading.Thread(target=a.add_a, args=(lock0,))
t1 = threading.Thread(target=a.add_b, args=(lock1,))
t0.start()
t1.start()

t0.join()
t1.join()
print(a.arr)