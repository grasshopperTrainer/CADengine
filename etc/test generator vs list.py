from time import time

s = time()
all(0 < i for i in range(1_000_000))
e = time()
print(e - s)

s = time()
all([0 < i for i in range(1_000_000)])
e = time()
print(e - s)
