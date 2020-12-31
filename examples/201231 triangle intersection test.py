from gkernel.tools import Intersector as intx
from gkernel.dtype.geometric.primitive import *


def no_culling_tester(tgl, ray):
    result = intx.intx(tgl, ray)
    print('result', result)
    print('culling disabling works', result == intx.intx(tgl.copy().reverse(), ray))
    print()


print('SIMPLE 2D TEST:')

tgl = Tgl([0, 0, 0], [10, 0, 0], [0, 10, 0])
print("test : from above")
no_culling_tester(tgl, Ray(o=[5, 5, 5], v=[0, -0.5, -1]))
print("test : from below")
no_culling_tester(tgl, Ray(o=[5, 5, -5], v=[0, -0.5, 1]))
print("test : not intersecting")
no_culling_tester(tgl, Ray(o=[5, 5, -5], v=[0, 0.5, 1]))
no_culling_tester(tgl, Ray(o=[5, 5, 5], v=[0, 0.5, 1]))
print()

print('TEST IN CUBE')
d = 10
tgl = Tgl([d, 0, 0], [0, d, 0], [0, 0, d])
no_culling_tester(tgl, Ray(o=[d, d, d], v=[-d, -d, -d]))
no_culling_tester(tgl, Ray(o=[d, d, d], v=[-1, 0, 0]))
no_culling_tester(tgl, Ray(o=[d, d, d], v=[-1, 0, -1]))
print()

print('TEST RAY STARTING FROM ON THE TRIANGLE')
no_culling_tester(tgl, Ray(o=[d/2, d/2, 0], v=[0, 0, 1]))
no_culling_tester(tgl, Ray(o=(Pnt(d/2, d/2, 0) + Vec.from_pnts(Pnt(0,0,d), Pnt(d/2,d/2, 0)).amplify(10)).xyz, v=[0, 0, 1]))
