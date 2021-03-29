import numpy as np
from numbers import Number

from ..array_like import ArrayLikeData
from ..constants import DTYPE
from global_tools.lazy import lazyProp


class Clr(ArrayLikeData):

    @staticmethod
    def is_num_complike(num):
        return isinstance(num, Number) and 0 <= num <= 1


    @lazyProp
    def as_byte(self):
        return (self*255).astype(np.uint8).tolist()

    def __setattr__(self, key, value):
        super(Clr, self).__setattr__(key, value)
        self.__class__.as_byte.reset(self)

    def __str__(self):
        return f"<{self.__class__.__name__}: {[round(v, 3) for v in self.view(np.ndarray)]}>"


class ClrRGB(Clr):

    def __new__(cls, r=1, g=1, b=1):
        """
        rgb in range (0, 1)
        :param r: red
        :param g: green
        :param b: blue
        """
        if not all([cls.is_num_complike(n) for n in (r, g, b)]):
            raise TypeError
        obj = super().__new__(cls, shape=3, dtype=DTYPE)
        obj[:] = r, g, b
        return obj

    @property
    def shape_std(self):
        return (3, )


class ClrRGBA(Clr):
    def __new__(cls, r=1, g=1, b=1, a=1):
        """
        rgb in range (0, 1)
        :param r: red
        :param g: green
        :param b: blue
        :param a: alpha(transparency)
        """
        if not all([cls.is_num_complike(n) for n in (r, g, b, a)]):
            raise TypeError
        obj = super().__new__(cls, shape=4, dtype=DTYPE)
        obj[:] = r, g, b, a
        return obj

    __rgba_idx = {'r':0, 'g':1, 'b':2, 'a':3}
    def __getattr__(self, item):
        vs = []
        if not (set(item) - set('rgba')):
            for c in item:
                vs.append(self[self.__rgba_idx[c]])
        return vs

    @property
    def shape_std(self):
        return (4, )

    @classmethod
    def from_raw_float(cls, r, g, b, a):
        ins = cls()
        ins[:] = r, g, b, a
        return ins