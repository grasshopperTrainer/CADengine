from numbers import Number
from math import inf

import numpy as np

from gkernel.array_like import ArrayLikeData
from gkernel.constants import DTYPE, DUNIT
from global_tools.singleton import Singleton
from global_tools.red_black_tree import RedBlackTree

from .primitive import Pnt, Vec, Pln, Lin, ZVec


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


class Pgon(ArrayLikeData):
    """
    Polygon
    """

    def __new__(cls, *vs):
        """

        :param vs: vertices
        """
        if len(vs) < 3:
            raise ValueError('at least 3 vertex needed')
        # ? should provide coupling end vertex or not?
        if not cls.validate_3d_coordinate(*vs):
            raise ValueError
        obj = super().__new__(cls, shape=(4, len(vs)), dtype=DTYPE)
        for i, v in enumerate(vs):
            obj[:3, i] = v
            obj[3, i] = 1

        obj.__plane = None
        obj.__normalized = None
        obj.__normalize()
        return obj

    def __str__(self):
        return f"<Pgon,{len(self)}>"

    @property
    def plane(self):
        return self.__plane

    @property
    def TM(self):
        return self.__plane.TM

    @property
    def normalized(self):
        """
        normalized geometry is a special representative of this geometry of:
        * first vertex lying on WCS origin(0, 0, 0) and
        * first edge lying on WCS X axis

        :return:
        """
        return self.__normalized

    @staticmethod
    def validate_array(cls, arr):
        """
        check array validity

        :param cls:
        :param arr:
        :return:
        """
        raise NotImplementedError

    def __normalize(self):
        """
        store normalized

        :return:
        """
        if not (self[:3, 0] == self[:3, -1]).all:
            raise ValueError('first and last vertex has to be identical')
        # find plane
        first = Pnt(*self[:3, 0])
        second = Pnt(*self[:3, 1])
        third = Pnt(*self[:3, 2])

        pln = Pln.from_lin_pnt(line=Lin.from_pnts(s=first, e=second), point=third, axis_of='x')
        self.__plane = pln
        self.__normalized = pln.TM.I * self
        if not self.__test_planarity():
            raise ValueError('given vertices not planar')

    def __test_planarity(self):
        """
        mytest is polygon is planner

        :return:
        """
        if self.__normalized is None:
            raise Exception('object not normalized')
        return (self.__normalized[3] == 0).all

    def __test_intersection(self):
        raise NotImplementedError('shamos-Hoey algorithm needed')

# this should be subclass of polygon
# class Rect(ArrayLikeData):
#     """
#     rectangle
#     """
#     def __new__(cls, a, b, c, d):
#         if not cls.validate_3d_coordinate(a, b, c, d):
#             raise TypeError
#         obj = super().__new__(cls, shape=(4, 4), dtype=DTYPE)
#         for i, v in enumerate(a, b, c, d):
#             obj[:3, i] = v
#             obj[3, i] = 1
#         return obj
