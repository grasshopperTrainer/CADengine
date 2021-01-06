from gkernel.dtype.geometric.primitive import *
from numpy import inf

a = Vec(10, 10, 5)
a = a*inf
print(a)
print(10*inf == 3*inf)