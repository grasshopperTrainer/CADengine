import numpy as np



a = np.array([[1,2],[3,4]])
print(a)
b = a[:,0]
print(b)
b[0] = 10
print(a)