import numpy as np


a = np.eye(4)
a[0][3] = 10
b = np.array([1,0,10, 1])
# b = b.reshape((4,1))
print(a.dot(b))
# print(a*b)
a = np.array([1,2,3,4])
b = np.array([4,5,6,7])
print(a.dot(b))

a = [[1,0,0,10],
     [0,1,0,0],
     [0,0,1,0],
     [0,0,0,1]]
b = [[0,0,0,1],
     [1,0,0,0],
     [0,1,0,0],
     [0,0,1,0]]
a = np.array(a)
b = np.array(b)
print(b.T)
print(b.T.dot(a))