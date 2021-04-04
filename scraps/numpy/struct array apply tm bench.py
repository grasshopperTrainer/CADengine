import random
import time
import numpy as np
from gkernel.dtype.geometric.primitive import Pnt

"""
compare transformation matrix application

test 0, struct stores other array as an object
test 1, struct stores point in ndarray with vertical vector shape


is this true?
"""

# power self test
n = 10000
test_n = 10

ave = 0
dtype = np.dtype([('pnt', Pnt), ('color', 'f4', 3)])
# test 0
for _ in range(test_n):
    arr = []
    for _ in range(n):
        p = Pnt(*[random.random() for _ in range(3)])
        c = [random.random() for _ in range(3)]
        arr.append((p, c))

    a = np.array(arr, dtype=dtype)

    s = time.time()
    for i in range(n):
        a[i]['pnt'] = np.dot(np.ndarray((4, 4)), a[i]['pnt'])
    e = time.time()
    ave += e - s
print(ave/test_n)

# test 1
ave = 0
dtype = np.dtype([('pnt', 'f8', (4, 1)), ('color', 'f4', 3)])
for _ in range(test_n):
    arr = []
    for _ in range(n):
        p = [[i] for i in range(4)]
        p[3] = [1]
        c = [random.random() for _ in range(3)]
        arr.append((p, c))
    a = np.array(arr, dtype=dtype)

    s = time.time()
    s = time.time()
    for i in range(n):
        a[i]['pnt'] = np.dot(np.ndarray((4, 4)), a[i]['pnt'])
    e = time.time()
    ave += e - s
print(ave / test_n)
