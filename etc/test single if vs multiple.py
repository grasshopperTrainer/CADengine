from time import time

s = time()
for i in range(100_000_000):
    if 0 < i:
        if i < 5_000_000:
            if i % 2 == 0:
                pass
e = time()
print(e - s)

s = time()
for i in range(100_000_000):
    if 0 < i < 5_000_000 and i % 2 == 0:
        pass
e = time()
print(e - s)
