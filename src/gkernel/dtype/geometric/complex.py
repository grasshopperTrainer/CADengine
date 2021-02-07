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


from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from ckernel.constants import RENDER_DEFAULT_FLOAT as RDF


@Singleton
class Trapezoidator:
    MAX, MIN, HMAX, HMIN, HORI, INTR = range(6)
    LEFT, NONE, RIGHT, BOTH = range(-1, 3)

    def run(self, arr):
        vrtxs, far_x = self.__stage_one(arr)
        trapezoids = self.__stage_two(vrtxs, far_x)
        vertices, indices = self.__stage_three(trapezoids)
        print(vertices)
        print(indices)
        print(len(vertices), len(indices))

    def __stage_one(self, arr):
        """
        first stage
        1. determine vertex category
        2. determine sweep direction
        3. create edge list
        :param arr:
        :return:
        """

        def __vertex_comparator(obj, sbj):
            ok, sk = obj.sort_key, sbj.sort_key
            if ok == sk:
                return 0
            if ok < sk:
                return -1
            else:
                return 1

        rb = RedBlackTree(comparator=__vertex_comparator)  # sort by y,x
        # prepare for the first
        prev_v = Pnt(*arr[:3, -1])
        this_v = Pnt(*arr[:3, 0])
        prev_e = self.__Edge(this_v, prev_v)

        # to maintain membership test through hash?
        last_v = prev_v
        first_v = this_v
        last_e = prev_e

        # find far x for further research
        far_x = -inf

        for i in range(len(arr)):
            next_v = Pnt(*arr[:3, (i + 1) % len(arr)])
            # maintain y incremental edge
            next_e = self.__Edge(this_v, next_v)
            # to maintain membership test through hash?
            if i == len(arr) - 2:
                next_v = last_v
            elif i == len(arr) - 1:
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
                    vrtx.append_ending_edge(next_e)  # order matters?
                    vrtx.append_ending_edge(prev_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HMAX)
                    vrtx.append_ending_edge(prev_e)
                    # not adding horizontal
                else:  # right above
                    vrtx.set_category(self.INTR)
                    vrtx.append_starting_edge(next_e)
                    vrtx.append_ending_edge(prev_e)
            elif prev_v.y == this_v.y:  # left horizontal
                if next_v.y < this_v.y:  # right below current
                    vrtx.set_category(self.HMAX)
                    vrtx.append_ending_edge(next_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HORI)
                    # not adding horizontal
                else:  # right upper
                    vrtx.set_category(self.HMIN)
                    vrtx.append_starting_edge(next_e)
            else:  # left upper current
                if next_v.y < this_v.y:  # right below current
                    vrtx.set_category(self.INTR)
                    vrtx.append_starting_edge(prev_e)
                    vrtx.append_ending_edge(next_e)
                elif next_v.y == this_v.y:  # right horizontal
                    vrtx.set_category(self.HMIN)
                    vrtx.append_starting_edge(prev_e)
                    # not adding horizontal
                else:  # right upper
                    vrtx.set_category(self.MIN)
                    vrtx.append_starting_edge(prev_e)
                    vrtx.append_starting_edge(next_e)

            # find sweep direction
            xvec, yvec = next_v - this_v, prev_v - this_v
            norm = Vec.cross(xvec, yvec)
            if vrtx.cat == self.HORI:
                vrtx.set_sweep_dir(self.NONE)
            elif vrtx.cat == self.HMIN:
                vrtx.set_sweep_dir(self.BOTH)   # for basin case
            elif vrtx.cat == self.HMAX:
                vrtx.set_sweep_dir(self.BOTH)   # for basin case
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
        return rb, far_x

    def __stage_two(self, vrtxs, far_x):
        trapezoids = self.__Trapezoids()

        def __edge_comparator(obj, sbj):
            # check side for inserting edge's vertex and far_x
            if obj is sbj:
                return 0

            is_same_side = sbj.pnts_share_side(obj.low_vertex, Pnt(far_x, obj.low_vertex.y, 0))
            if is_same_side is None:
                if obj.low_vertex.yx == sbj.low_vertex.yx:
                    if obj.hight_vertex.x < sbj.hight_vertex.x:
                        return -1
                    else:  # go right has equal
                        return 1
                elif obj.low_vertex.yx < sbj.low_vertex.yx:
                    return -1
                else:
                    return 1
            if is_same_side:  # else search right, +1
                return 1
            else:  # if side differs search left, -1
                return -1

        edges = RedBlackTree(__edge_comparator)
        # intersect
        for i, vrtx in enumerate(vrtxs):
            if edges:
                if vrtx.sweep_dir == self.NONE:
                    if len(vrtx.ending_edges) == 2:  # summit trapezoid, simply join two endings
                        trapezoids.add(vrtx.ending_edges[0].geo, vrtx.ending_edges[1].geo)
                    else:
                        raise Exception('unknown')

                elif vrtx.sweep_dir == self.LEFT:
                    left_edge = edges.search_lesser(vrtx.ending_edges[0])
                    left_seg = left_edge.cut(vrtx.y)
                    right_seg = vrtx.ending_edges[0].geo
                    trapezoids.add(left_seg, right_seg)

                elif vrtx.sweep_dir == self.RIGHT:
                    right_edge = edges.search_greater(vrtx.ending_edges[0])
                    right_seg = right_edge.cut(vrtx.y)
                    left_seg = vrtx.ending_edges[0].geo
                    trapezoids.add(left_seg, right_seg)

                elif vrtx.sweep_dir == self.BOTH:
                    # find left right intersection edges
                    if vrtx.cat == self.MIN:
                        left_edge = edges.search_lesser(vrtx.starting_edges[0])
                        right_edge = edges.search_greater(vrtx.starting_edges[1])
                    elif vrtx.cat == self.MAX:
                        left_edge = edges.search_lesser(vrtx.starting_edges[0])
                        right_edge = edges.search_greater(vrtx.starting_edges[1])
                    elif vrtx.cat == self.HMIN:
                        left_edge = edges.search_lesser(vrtx.starting_edges[0])
                        right_edge = edges.search_greater(vrtx.starting_edges[0])
                    elif vrtx.cat == self.HMAX:
                        left_edge = edges.search_lesser(vrtx.ending_edges[0])
                        right_edge = edges.search_greater(vrtx.ending_edges[0])

                    # find segments
                    if left_edge:
                        left_seg = left_edge.cut(vrtx.y)
                    else:
                        left_seg = Lin.from_pnts(vrtx.geo, vrtx.geo)  # 0 line
                    if right_edge:
                        right_seg = right_edge.cut(vrtx.y)
                    else:
                        right_seg = Lin.from_pnts(vrtx.geo, vrtx.geo)  # 0 line

                    if left_seg.length != 0 or right_seg.length != 0:
                        trapezoids.add(left_seg, right_seg)

            for e in vrtx.ending_edges:
                edges.delete(e)
            for e in vrtx.starting_edges:
                edges.insert_unique(e)

        return trapezoids

    def __stage_three(self, trapezoids):
        """
        array compaction into QUAD_STRIP

        :param trapezoids:
        :return:
        """
        return trapezoids.generate_array()

    class __Vrtx:
        """
        helper
        """

        def __init__(self, geo):
            self.__geo = geo

            self.__sweep_dir = None
            self.__category = None

            self.__starting_edges = []
            self.__ending_edges = []

        def __str__(self):
            return f"<Vrtx {self.__geo},{self.__sweep_dir},{self.__category}>"

        def append_starting_edge(self, edge):
            self.__starting_edges.append(edge)

        def append_ending_edge(self, edge):
            if not self.__ending_edges:
                self.__ending_edges.append(edge)
            else:
                if self.__ending_edges[0].low_vertex.x < edge.low_vertex.x:
                    self.__ending_edges.append(edge)
                else:
                    self.__ending_edges.insert(0, edge)

        def set_sweep_dir(self, dir):
            self.__sweep_dir = dir

        def set_category(self, cat):
            self.__category = cat

        @property
        def sort_key(self):
            return self.__geo.y, self.__geo.x

        @property
        def sweep_dir(self):
            return self.__sweep_dir

        @property
        def cat(self):
            return self.__category

        @property
        def starting_edges(self):
            return self.__starting_edges

        @property
        def ending_edges(self):
            return self.__ending_edges

        @property
        def x(self):
            return self.__geo.x

        @property
        def y(self):
            return self.__geo.y

        @property
        def geo(self):
            return self.__geo

    class __Edge:
        """
        line wrapper
        as line can be shortened during trapezoidation

        functions:
        1. normalize so that two vertex is defined as having smaller and bigger x,y
        2. provide shortening
        """

        def __init__(self, a, b):
            """

            :param a:
            :param b:
            """
            if a.yx < b.yx:
                self.__small = a
                self.__big = b
            elif a.yx > b.yx:
                self.__small = b
                self.__big = a
            else:
                raise ValueError('contradiction')
            # need for point side checking
            self.__line = Lin.from_pnts(self.__small, self.__big)
            if self.__big.y - self.__small.y == 0:
                self.__gradient = 0
            else:
                self.__gradient = (self.__big.x - self.__small.x) / (self.__big.y - self.__small.y)

        def __str__(self):
            return f"<Edge {self.__small} {self.__big}>"

        def __repr__(self):
            return self.__str__()

        @property
        def vec(self):
            return self.__vec

        @property
        def low_vertex(self):
            return self.__small

        @property
        def hight_vertex(self):
            return self.__big

        @property
        def geo(self):
            """
            dont return cached, it doesnt reflect updated small

            :return:
            """
            return Lin.from_pnts(self.__small, self.__big)

        def pnts_share_side(self, v0, v_max):
            return self.__line.pnts_share_side(v0, v_max)

        def cut(self, y):
            """
            cut edge at given y and return edge below

            :param y:
            :return:
            """
            # calculate intersection
            x = self.__gradient * (y - self.__small.y) + self.__small.x
            inter_p = Pnt(x, y, 0)
            # form edge below
            edge_below = Lin.from_pnts(self.__small, inter_p)
            # erase bolow
            self.__small = inter_p
            self.__line = Lin.from_pnts(self.__small, self.__big)
            return edge_below

    class __Trapezoids:
        def __init__(self):
            self.__geos = RedBlackTree(comparator=self.__comparator)

        @staticmethod
        def __comparator(obj, sbj):
            if obj[0] == sbj[0] and obj[1] == sbj[1]:
                return 0
            # compare lower left's y value
            if obj[0][1] < sbj[0][1]:
                return -1
            elif obj[0][1] > sbj[0][1]:
                return 1
            else:  # then compare x
                if obj[0][0] < sbj[0][0]:
                    return -1
                elif obj[0][0] >= sbj[0][0]:
                    return 1

        def add(self, left, right):
            (a, c), (b, d) = (v.xyzw for v in left.vertices), (v.xyzw for v in right.vertices)
            self.__geos.insert((a, b, c, d))

        def generate_array(self):
            """
            generate vertex array and indices for GL_QUAD_STRIP

            :return:
            """
            if not self.__geos:
                raise ValueError

            vertices = []
            indices = []
            unique_vrtx = {}  # for extra compaction

            # init
            vs = self.__geos.popleft()
            for v in vs:
                indices.append(len(vertices))
                vertices.append(v)
            last_sweep = vs[2:]

            while self.__geos:
                if self.__geos.has_value(last_sweep):  # stripable
                    vs = self.__geos.pop_value(last_sweep)
                    for v in vs[2:]:
                        if v not in unique_vrtx:
                            unique_vrtx.setdefault(v, len(vertices))
                            indices.append(len(vertices))
                            vertices.append(v)
                        else:
                            indices.append(unique_vrtx[v])
                else:  # none stripable
                    # restart primitive and record all vertices
                    indices.append(PRV)
                    vs = self.__geos.popleft()
                    for v in vs:
                        if v not in unique_vrtx:
                            unique_vrtx.setdefault(v, len(vertices))
                            indices.append(len(vertices))
                            vertices.append(v)
                        else:
                            indices.append(unique_vrtx[v])
                # new sweep
                last_sweep = tuple(vs[2:])

            return np.array(vertices, dtype=RDF), np.array(indices, dtype=np.uint)

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
