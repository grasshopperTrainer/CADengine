from gkernel.dtype.geometric.primitive import *

#
# v = Vec(10, 10, 10)
#
# p0 = Pnt(10, 10, 10)
# p1 = Pnt(5, 5, 5)
#
# zv = ZeroVec()
#
# print('point to vector')
# print(p0 - p1)
#
# print('move point')
# print(p0 + v)
# print(p0 - v)
#
# print('named to common Vec')
# print(zv + v)
# print(v + zv)
# print(zv + p0)
# print(p0 + zv)
#
# print('scalar math')
# print(zv * 3)
# print(zv - v / 3)
# print((zv + v) / 3)
#
# print()
# print('named vs named test')
# xvec = XVec()
# t = zv
# zv += v
# print(zv, t, t == zv)
# print(t + xvec)
# print(-xvec)
a = ZeroVec()
a[:] = a * 10
# print(a * 10)
print(a.normalize())
print(a.as_vec())
