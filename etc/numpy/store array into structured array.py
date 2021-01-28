import numpy as np


mat = np.eye(4)
mat2 = np.eye(3)

dtype = np.dtype([('a', np.ndarray)])
print(dtype)
arr = np.zeros(1, dtype)
arr[0] = (mat,)
# print(arr)
# print('ddddddddd')
# print(arr[0])
# arr2 = np.array((mat2,), dtype)
# print(arr, type(arr))
# print(type(arr['a']))
# print(arr['a'],)
# print(np.array(2))
# print(arr[0])
# k = np.vstack((arr, arr2))
# print(k.shape, arr.shape)
# print(k['a'][0])