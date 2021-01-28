import numpy as np


dtype = np.dtype([('a', 'uint', 3), ('b', 'f', 2)])
print(dtype)
data = [ ((0,1,2), (0,2)), ((0,1,2), (2,2)) ]
arr = np.array(data, dtype=dtype)
print(arr)
print(arr['a'])


dtype = np.dtype([('a', 'uint', 3)])
print(dtype)
data = ((1,2,3),)
arr = np.array(data, dtype=dtype)
print(arr)
print(arr['a'], data, dtype)