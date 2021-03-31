from numbers import Number
from collections import Counter
import numpy as np

from gkernel.array_like import ArrayLikeData
from gkernel.constants import DTYPE, DUNIT
from global_tools.singleton import Singleton
from global_tools.red_black_tree import RedBlackTree

from .primitive import Pnt, Vec, Pln, Lin, ZVec, ZeroVec


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
        if len(vs) < 4:
            raise ValueError('at least 4 vertex with overlapping first, last, needed')
        if not(vs[0] == vs[-1]):
            raise ValueError('first last vertices has to overlap')
        if len(set(map(tuple, vs))) != len(vs) - 1:
            raise ValueError('no overlapping vertices allowed')

        # ? should provide coupling end vertex or not?
        if not cls.validate_3d_coordinate(*vs):
            raise ValueError
        obj = super().__new__(cls, shape=(4, len(vs)), dtype=DTYPE)
        for i, v in enumerate(vs):
            obj[:3, i] = v
            obj[3, i] = 1

        # obj.__plane = None
        # obj.__normalized = None
        # obj.__normalize()
        return obj

    def __str__(self):
        return f"<Pgon,{len(self)}>"

    def __array_finalize__(self, obj):
        self.__plane = None
        self.__normalized = None

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
        self.__normalize()
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

    def __calc_normal(self):
        """
        calculate normal vector

        ref: https://stackoverflow.com/questions/22838071/robust-polygon-normal-calculation
        :return:
        """
        norm = ZeroVec()
        for a, b in zip(self[:3, :-1].T, self[:3, 1:].T):
            norm += Vec.cross(Pnt(*a), Pnt(*b))
        return norm.normalize()

    def __normalize(self):
        """
        store normalized

        :return:
        """
        if not (self[:3, 0] == self[:3, -1]).all:
            raise ValueError('first and last vertex has to be identical')
        # find z
        axis_z = self.__calc_normal()

        # find plane
        origin = Pnt(*self[:3, 0])
        axis_x = Vec(*(self[:3, 1] - self[:3, 0]))
        axis_y = Vec.cross(axis_z, axis_x)
        pln = Pln.from_ori_axies(origin, axis_x, axis_y, axis_z)

        self.__plane = pln
        self.__normalized = pln.TM.I * self.view(np.ndarray)
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
