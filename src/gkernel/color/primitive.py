import numpy as np
from numbers import Number

from ..array_like import ArrayLikeData
from ..constants import DTYPE
from global_tools.lazy import lazyProp


class Clr(ArrayLikeData):

    def as_ubyte(self):
        return (self * 255).astype(np.uint8)

    def __str__(self):
        return f"<{self.__class__.__name__}: {[round(v, 3) for v in self.view(np.ndarray)]}>"


class ClrRGB(Clr):

    def __new__(cls, r=1., g=1., b=1.):
        """
        rgb in range (0, 1)
        :param r: red
        :param g: green
        :param b: blue
        """
        obj = super().__new__(cls, shape=3, dtype=DTYPE)
        obj[:] = r, g, b
        return obj


class ClrRGBA(Clr):

    def __new__(cls, r=1., g=1., b=1., a=1.):
        """
        rgb in range (0, 1)
        :param r: red
        :param g: green
        :param b: blue
        :param a: alpha(transparency)
        """
        obj = super().__new__(cls, shape=4, dtype=DTYPE)
        obj[:] = r, g, b, a
        return obj

    __rgba_idx = {'r': 0, 'g': 1, 'b': 2, 'a': 3}

    def __getattr__(self, item):
        vs = []
        if not (set(item) - set('rgba')):
            for c in item:
                vs.append(self[self.__rgba_idx[c]])
        return tuple(vs)
