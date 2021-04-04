from gkernel.dtype.geometric.primitive import Pln

a = 1
p = Pln([100, 100, 100], [-a, a, 0], [-a, -a, a], [a, a, a])
p[:] = 10
print(p)
print(p.raw)
