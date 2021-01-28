from gkernel.dtype.geometric.primitive import Vec

a = Vec(10, 20, 3)
print(a.normalize())
print(a.amplify(10))
# import numpy as np
# a = np.array([0, 1, 2])
a[:] = 10
print(a)