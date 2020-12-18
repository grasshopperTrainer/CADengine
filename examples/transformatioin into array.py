from gkernel.dtype.nongeometric.matrix import EyeMat4, MoveMat, ScaleMat, RotXMat, RotYMat, StackedMat
from gkernel.dtype.geometric.primitive import Pnt, Vec
import numpy as np

# p = Pnt(1,1,1)
# mm = MoveMat(10,10,10)
# ss = ScaleMat(2, 2,2)
# # print(ss)
# # print(mm)
# tm = mm*ss
#
# print(mm*ss*p)
#
# v = Vec(10,0,0)
# print(p*v)
v = Vec(10, 0, 0)
k = v[:3, 0]
print(type(k))
print(k, k.shape)

k = np.array([1,2,3])
print(id(k))
k[:2] = 0, 1
print(id(k))
# print(k.arr)

# print(mm.string_mat())
# print(ss.shape)
# print(ss[:3, 0])
# print(mm)
# print(p*mm)
# a = ss*p
# print(a*mm)
# a = RotXMat(10)
# b = RotYMat(2)
# a*b
# b*a