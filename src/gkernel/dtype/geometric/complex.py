from numbers import Number

import numpy as np

from gkernel.array_like import ArrayLikeData
from gkernel.constants import DTYPE, DUNIT
from .primitive import Pnt


class Plin(ArrayLikeData):

    def __new__(cls, *vs):
        """

        :param vs: ([x, y, z], [x, y, z], ...) more then two vertices of polyline
        """
        if not vs:  # default
            vs = ([0, 0, 0], [DUNIT, 0, 0], [0, 0, DUNIT])
        if len(vs) < 2:
            raise ValueError('at lease 2 vertices needed to from a polyline')
        if not all([len(v) == 3 and all(isinstance(c, Number) for c in v) for v in vs]):
            raise ValueError('vertex values cant be interpreted as coordinates')

        obj = super().__new__(cls, shape=(4, len(vs)), dtype=DTYPE)
        obj[:-1] = np.array(vs).T
        obj[-1] = 1
        return obj

    def __len__(self):
        """
        number of vertices
        :return:
        """
        return self.shape[1]

    def vertices(self):
        """
        generator of polyline vertices

        :return:
        """
        for i in range(self.shape[1]):
            yield Pnt(x=self[0, i], y=self[1, i], z=self[2, i])

    def length(self):
        raise NotImplementedError

l = Plin([0, 1, 2], [3, 4, 5], [6, 7, 8])
