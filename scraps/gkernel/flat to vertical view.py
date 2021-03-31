from gkernel.dtype.geometric.primitive import Pnt
import numpy as np


p = np.array([0, 1, 2, 3]).view(Pnt)
print(p.raw)