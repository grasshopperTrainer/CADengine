from gkernel.dtype.geometric.primitive import Pln
from gkernel.dtype.nongeometric.matrix import MoveMat

# print('test 0: correct standardization')
a = Pln([100, 50, 30], x=(5, 5, 3))
# print(a.arr)
# print(a.trnsf_mat.arr)
# print('test 1: copy')
# print(a.copy().arr)
print('test 2: check TM after calculation')
m = MoveMat(10, 10, 5)
b = m * a
print(b.interleaved, type(b))
print(b.TM.interleaved)

# print(np.array([[1,2,3,4], [5,6,7,8], [10,11,12,13], [14,15,16,17]]).view(Pln))
