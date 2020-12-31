from gkernel.tools import Intersector
from gkernel.dtype.geometric.primitive import *

i = Intersector()
pln = Pln()
ray = Ray()

print(i.intx(pln, ray))


