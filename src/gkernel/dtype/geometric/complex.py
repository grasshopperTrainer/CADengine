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

        obj.__tessellation_trapezoid = Trapezoidator().run(obj)
        return obj

    def __str__(self):
        return f"<Pgon,{len(self)}>"

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
        # find plane
        first = Pnt(*self[:3, 0])
        second = Pnt(*self[:3, 1])
        last = Pnt(*self[:3, -1])
        pln = Pln.from_lin_pnt(line=Lin.from_pnts(s=first, e=second), point=last, axis_of='x')
        self.__plane = pln
        self.__normalized = pln.TM.I * self
        if not self.__test_planarity():
            raise ValueError('given vertices not planar')

    def __test_planarity(self):
        """
        test is polygon is planner

        :return:
        """
        if self.__normalized is None:
            raise Exception('object not normalized')
        return (self.__normalized[3] == 0).all


@Singleton
class Trapezoidator:
    MAX, MIN, HMAX, HMIN, HORI, INTR = range(6)
    LEFT, NONE, RIGHT, BOTH = range(-1, 3)

    def run(self, arr):
        vrtxs, far_x = self.__stage_one(arr)
        self.__stage_two(vrtxs, far_x)

    @staticmethod
    def __vertex_comparator(obj, sbj):
        ok, sk = obj.sort_key, sbj.sort_key
        if ok == sk:
            return 0
        if ok < sk:
            return -1
        else:
            return 1

    def __stage_one(self, arr):
        """
        first stage
        1. determine vertex category
        2. determine sweep direction
        3. create edge list
        :param arr:
        :return:
        """

        rb = RedBlackTree(comparator=self.__vertex_comparator)  # sort by y,x
        # prepare for the first
        prev_v = Pnt(*arr[:3, -1])
        this_v = Pnt(*arr[:3, 0])
        prev_e = Lin.from_pnts(this_v, prev_v) if this_v.y < prev_v.y else Lin.from_pnts(prev_v, this_v)

        # to maintain membership test through hash?
        last_v = prev_v
        first_v = this_v
        last_e = prev_e

        # find far x for further research
        far_x = -inf

        for i in range(len(arr)):
            next_v = Pnt(*arr[:3, (i + 1) % len(arr)])
            # maintain y incremental edge
            next_e = Lin.from_pnts(this_v, next_v) if this_v.y < next_v.y else Lin.from_pnts(next_v, this_v)
            # to maintain membership test through hash?
            if i == len(arr)-2:
                next_v = last_v
            elif i == len(arr)-1:
                this_v = last_v
                next_v = first_v
                next_e = last_e

            # update far x
            if far_x < this_v.x + 100:
                far_x = this_v.x + 100

            vrtx = self.__Vrtx(this_v)
            # determine category and edge connection
            if prev_v.y < this_v.y:  # left below current
                if next_v.y < this_v.y:  # right below current
                    vrtx.set_category(self.MAX)
                    vrtx.add_ending_edge(prev_e)
                    vrtx.add_ending_edge(next_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HMAX)
                    vrtx.add_ending_edge(prev_e)
                    # not adding horizontal
                else:  # right above
                    vrtx.set_category(self.INTR)
                    vrtx.add_starting_edge(next_e)
                    vrtx.add_ending_edge(prev_e)
            elif prev_v.y == this_v.y:  # left horizontal
                if next_v.y < this_v.y:  # right below current
                    vrtx.set_category(self.HMAX)
                    vrtx.add_ending_edge(next_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HORI)
                    # not adding horizontal
                else:  # right upper
                    vrtx.set_category(self.HMIN)
                    vrtx.add_starting_edge(next_e)
            else:  # left upper current
                if next_v.y < this_v.y:  # right below current
                    vrtx.set_category(self.INTR)
                    vrtx.add_starting_edge(prev_e)
                    vrtx.add_ending_edge(next_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HMIN)
                    vrtx.add_starting_edge(prev_e)
                    # not adding horizontal
                else:  # right upper
                    vrtx.set_category(self.MIN)
                    vrtx.add_starting_edge(prev_e)
                    vrtx.add_starting_edge(next_e)

            # find sweep direction
            xvec, yvec = next_v - this_v, prev_v - this_v
            norm = Vec.cross(xvec, yvec)
            if vrtx.cat == self.HORI:
                vrtx.set_sweep_dir(self.NONE)
            elif vrtx.cat == self.HMIN:
                if prev_v.y == this_v.y:
                    vrtx.set_sweep_dir(self.LEFT)
                else:
                    vrtx.set_sweep_dir(self.RIGHT)
            elif vrtx.cat == self.HMAX:
                if prev_v.y == this_v.y:
                    vrtx.set_sweep_dir(self.RIGHT)
                else:
                    vrtx.set_sweep_dir(self.LEFT)
            elif vrtx.cat in (self.MIN, self.MAX):
                if 0 < Vec.dot(ZVec(), norm):
                    vrtx.set_sweep_dir(self.NONE)
                else:
                    vrtx.set_sweep_dir(self.BOTH)
            elif vrtx.cat == self.INTR:
                if prev_v.y < next_v.y:
                    vrtx.set_sweep_dir(self.LEFT)
                else:
                    vrtx.set_sweep_dir(self.RIGHT)

            # update for next vertex
            prev_v, this_v, prev_e = this_v, next_v, next_e

            # record point
            rb.insert(vrtx)
        return rb, Pnt(x=far_x, y=0, z=0)

    def __stage_two(self, vrtxs, far_x):

        # def comparator(obj, sbj):
        #     # check side for inserting edge's vertex and far_x
        #
        #     # if side differs search left, -1
        #
        #     # else search right, +1
        #
        #     # 0 cant occur


        edges = RedBlackTree()
        # first vertex of normalized is always [0, 0, 0]
        # first edge of normalized is always [x, 0, 0]
        # prepare fisrt edge
        # there are 3 initial cases
        for v in vrtxs:
            # discreet searching needed
            # update edges
            for e in v.ending_edges:
                edges.delete(e)
            for e in v.starting_edges:
                edges.insert()
            print(v)
            print(v.starting_edges)
            print(v.ending_edges)

        #     raise
        # raise NotImplementedError

    class __Vrtx:
        """
        helper
        """

        def __init__(self, geo):
            self.__geo = geo

            self.__sweep_dir = None
            self.__category = None

            self.__starting_edges = set()
            self.__ending_edges = set()

        def __str__(self):
            return f"<Vrtx {self.__geo},{self.__sweep_dir},{self.__category}>"

        def add_starting_edge(self, edge):
            self.__starting_edges.add(edge)

        def add_ending_edge(self, edge):
            self.__ending_edges.add(edge)

        def set_sweep_dir(self, dir):
            self.__sweep_dir = dir

        def set_category(self, cat):
            self.__category = cat

        @property
        def sort_key(self):
            return self.__geo.y, self.__geo.x

        @property
        def cat(self):
            return self.__category

        @property
        def starting_edges(self):
            return self.__starting_edges
        @property
        def ending_edges(self):
            return self.__ending_edges