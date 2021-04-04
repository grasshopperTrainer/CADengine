import random
import time
import numpy as np
from gkernel.dtype.geometric.primitive import Pnt
from gkernel.dtype.nongeometric.matrix.primitive import MoveMat
"""
what is the correct struct?

1. applying transformation matrix
2. weaving into struct
3. manipulating single object

"""

# found! use this pattern
mm = MoveMat(10, 10, 10)
dtype = np.dtype([('pnt', 'f4', 4), ('clr', 'f4', (3,))])
n = 6
interleaved = []
for _ in range(n):
    interleaved.append(((1, 11, 111, 1), (0, 0, 0)))
interleaved = np.array(interleaved, dtype)

print('this is interleaved buffer:')
print(interleaved)
print()
print('this is linear geometric data:')

# pnts = interleaved['pnt'].T.view(np.ndarray)
# print(interleaved['pnt'].shape)
print(interleaved['pnt'].shape)
pnts = interleaved[[1, 2, 3]]
print(pnts)
# pnts[:] = np.dot(pnts, mm.T)
# pnts[:] = pnts.dot(mm.T)
# print(pnts[0,0])
print(pnts[0])
pnts['pnt'] = 100
print()
print(pnts)
print(pnts.base)
k = interleaved['pnt'][..., (0, 3)]
k[:] = 100
print()
print(interleaved)
# print()
# print(interleaved['pnt'].T)
# print(interleaved['pnt'][:, :, (0, 1)])
# print(interleaved['pnt'].T.shape)
# print(pnts)
# p = interleaved['pnt'][0].view(Pnt)
# print(b)
# p[0] = 10
# print(b)
#
# print()
# b[:] = mm * b
# print(interleaved)
# p[0] = 50
# print(interleaved)
# print(b)
# # print()
# # c = np.apply_along_axis(lambda x: mm * x, axis=1, arr=b)
# # print(c)
# # print(p)