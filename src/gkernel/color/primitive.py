import numpy as np
from numbers import Number

from ..array_like import ArrayLikeData
from ..constants import DTYPE


class Clr(ArrayLikeData):

    @staticmethod
    def is_num_complike(num):
        return isinstance(num, Number) and 0 <= num <= 1

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

    @property
    def shape_std(self):
        return (4, )
