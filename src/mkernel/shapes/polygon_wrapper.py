from math import inf
from numbers import Number

import numpy as np
from global_tools.red_black_tree import RedBlackTree
from global_tools.singleton import Singleton

from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from ckernel.constants import RENDER_DEFAULT_FLOAT as RDF

from gkernel.dtype.geometric.primitive import Pnt, Vec, Lin, ZVec
from gkernel.color import Clr, ClrRGBA
import gkernel.dtype.geometric as gt

from .base import Shape


class Pgon(Shape):
    """
    Polygon shape
    """

    def __init__(self, geo: gt.Pgon, renderer):
        self.__geo = None
        self.__thk = None
        self.__clr_edge = None
        self.__clr_fill = None
        # _Trapezoidator supports normalized array and returns normalized trapezoid
        # vertices are in normalized position so apply plane TM
        vertices, fill_indxs, edge_indxs = _Trapezoidator().gen_quad_strip(geo)
        print(edge_indxs)
        self.__renderer = renderer
        self.__vrtx_block = renderer.vbo.cache.request_block(size=len(vertices))
        self.__vrtx_block['vtx'] = vertices
        self.__fill_indx_block = renderer.fill_ibo.cache.request_block(size=len(fill_indxs))
        self.__fill_indx_block['idx'] = fill_indxs
        self.__edge_indx_block = renderer.edge_ibo.cache.request_block(size=len(edge_indxs) + 1)
        self.__edge_indx_block['idx', :-1] = edge_indxs
        self.__edge_indx_block['idx', -1] = PRV

        self.__geo = geo
        self.thk = 0.5
        self.clr_edge = ClrRGBA(0, 0, 0, 1)
        self.clr_fill = ClrRGBA(1, 1, 1, 1)

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Pgon):
            raise
        if len(v) != len(self.__vrtx_block):
            self.__vrtx_block.resize(size=len(v))
        else:
            self.__vrtx_block['vtx'] = v
            self.__geo[:] = v

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self.__vrtx_block['edge_thk'] = v
        self.__thk = v

    @property
    def clr(self):
        return self.__clr_edge, self.__clr_fill

    @clr.setter
    def clr(self, v):
        if isinstance(v, Clr):
            edge, fill = v
        elif isinstance(v, (tuple, list)) and len(v) == 2:
            edge, fill = v
        else:
            raise TypeError
        self.clr_edge = edge
        self.clr_fill = fill

    @property
    def clr_edge(self):
        return self.__clr_edge

    @clr_edge.setter
    def clr_edge(self, v):
        if not isinstance(v, Clr):
            raise TypeError
        self.__vrtx_block['clr_edge'] = v
        if self.__clr_edge is not None:
            self.__clr_edge[:] = v
        else:
            self.__clr_edge = v

    @property
    def clr_fill(self):
        return self.__clr_fill

    @clr_fill.setter
    def clr_fill(self, v):
        if not isinstance(v, Clr):
            raise TypeError
        self.__vrtx_block['clr_fill'] = v
        if self.__clr_fill is not None:
            self.__clr_fill[:] = v
        else:
            self.__clr_fill = v


@Singleton
class _Trapezoidator:
    MAX, MIN, HMAX, HMIN, HORI, INTR = range(6)
    LEFT, NONE, RIGHT, BOTH = range(-1, 3)

    def gen_quad_strip(self, pgon: Pgon):
        """
        ! array should be normalized on WCS origin plane
        :param pgon:
        :return:
        """
        if not isinstance(pgon, gt.Pgon):
            raise TypeError
        vrtxs, far_x = self.__stage_one(pgon.normalized)
        trapezoids = self.__stage_two(vrtxs, far_x)

        return self.__stage_three(pgon, trapezoids)

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
        prev_v = Pnt(*arr[:3, -2])  # not to consider last
        this_v = Pnt(*arr[:3, 0])
        prev_e = self.__Edge(this_v, prev_v)

        # to maintain membership mytest through hash?
        last_v = prev_v
        first_v = this_v
        last_e = prev_e

        # find far x for further research
        far_x = -inf

        for i in range(len(arr) - 1):  # not to consider last
            next_v = Pnt(*arr[:3, (i + 1) % len(arr)])
            next_e = self.__Edge(this_v, next_v)

            # this is not really needed
            if i == len(arr) - 2:
                next_v = last_v
            elif i == len(arr) - 1:
                this_v = last_v
                next_v = first_v
                next_e = last_e

            # update far x, +100 not to mytest with overlapping vertex
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

            if vrtx.cat == self.HORI:
                vrtx.set_sweep_dir(self.NONE)
            elif vrtx.cat == self.HMIN:
                vrtx.set_sweep_dir(self.BOTH)  # for basin case
            elif vrtx.cat == self.HMAX:
                vrtx.set_sweep_dir(self.BOTH)  # for basin case
            elif vrtx.cat in (self.MIN, self.MAX):
                xvec, yvec = next_v - this_v, prev_v - this_v
                norm = Vec.cross(xvec, yvec)
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

            far_pnt = Pnt(far_x, obj.low_vertex.y, 0)
            is_same_side = sbj.pnts_share_side(obj.low_vertex, far_pnt)
            # object edge's vertex touches subject edge
            if is_same_side is None:
                if obj.low_vertex.yx == sbj.low_vertex.yx:
                    if obj.hight_vertex.x < sbj.hight_vertex.x:
                        return -1
                    else:  # go right includes equal
                        return 1
                elif obj.low_vertex.yx < sbj.low_vertex.yx:
                    return -1
                else:  # go right includes equal
                    return 1
            if is_same_side:  # else search right, +1
                return 1
            else:  # if side differs search left, -1
                return -1

        edges = RedBlackTree(__edge_comparator)
        # find trapezoids
        for i, vrtx in enumerate(vrtxs):
            if edges:
                if vrtx.sweep_dir == self.NONE:
                    if len(vrtx.ending_edges) == 2:  # summit trapezoid, simply join two endings
                        trapezoids.add(vrtx.ending_edges[0].geo, vrtx.ending_edges[1].geo)
                    else:
                        raise Exception('unknown')
                # LEFT RIGHT is for category INTR
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
                    else:
                        raise
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

            # update edges
            for e in vrtx.ending_edges:
                edges.delete(e)
            for e in vrtx.starting_edges:
                edges.insert_unique(e)

        return trapezoids

    def __stage_three(self, pgon, trapezoids):
        """
        array compaction into QUAD_STRIP
        and denormalize

        :param trapezoids:
        :return:
        """
        vs, fill_indxs, vi_dict = trapezoids.generate_array()
        vs = (pgon.TM * np.array(vs).T).T

        # form edge index for GL_LINE_STRIP_ADJACENCY
        edge_indxs = []
        edge_indxs.append(vi_dict[tuple(pgon.normalized[:, -2])])  # form adjacency
        for i in range(len(pgon)):
            v = tuple(pgon.normalized[:, i])
            edge_indxs.append(vi_dict[v])
        edge_indxs.append(edge_indxs[2])  # form adjacency

        return vs, fill_indxs, edge_indxs

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
            # maintain y incremental edge
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
            # needed for finding intersection point
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
                if v not in unique_vrtx:
                    unique_vrtx.setdefault(v, len(vertices))
                    indices.append(len(vertices))
                    vertices.append(v)
                else:
                    indices.append(unique_vrtx[v])
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

            return vertices, indices, unique_vrtx
