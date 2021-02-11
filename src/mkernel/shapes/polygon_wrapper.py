from math import inf
from numbers import Number
from warnings import warn
import bisect

import numpy as np
from global_tools.red_black_tree import RedBlackTree
from global_tools.singleton import Singleton

from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV

from gkernel.color import Clr, ClrRGBA
import gkernel.dtype.geometric as gt
from gkernel.constants import ATOL

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
        # try:
        vertices, fill_indxs, edge_indxs = _Trapezoidator().gen_quad_strip(geo)
        self.__renderer = renderer
        self.__vrtx_block = renderer.vbo.cache.request_block(size=len(vertices))
        self.__vrtx_block['vtx'] = vertices
        # add PRV at the end to draw separately
        offset = self.__vrtx_block.indices[0]  # min index
        self.__fill_indx_block = renderer.fill_ibo.cache.request_block(size=len(fill_indxs) + 1)
        self.__fill_indx_block['idx', :-1] = [offset + i if i != PRV else PRV for i in fill_indxs]
        self.__fill_indx_block['idx', -1] = PRV

        self.__edge_indx_block = renderer.edge_ibo.cache.request_block(size=len(edge_indxs) + 1)
        self.__edge_indx_block['idx', :-1] = [offset + i for i in edge_indxs]
        self.__edge_indx_block['idx', -1] = PRV
        # except Exception as e:
        #     warn('trapezoidation fail')
        #     self.__vrtx_block = renderer.vbo.cache.request_block(size=1)

        self.__geo = geo
        self.thk = 0.5
        self.clr_edge = ClrRGBA(0, 0, 0, 1)
        self.clr_fill = ClrRGBA(1, 1, 1, 1)

    def __str__(self):
        return f"<Pgon >"

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Pgon):
            raise
        vertices, fill_indxs, edge_indxs = _Trapezoidator().gen_quad_strip(v)
        if len(vertices) != len(self.__vrtx_block):
            self.__vrtx_block.resize(size=len(v))
        else:
            self.__vrtx_block['vtx'] = vertices
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
    MAX, MIN, HMAX, HMIN, HORI, INTR = 'MAX', 'MIN', 'HMAX', 'HMIN', 'HORI', 'INTR'
    LEFT, NONE, RIGHT, BOTH = 'LEFT', 'NONE', 'RIGHT', 'BOTH'

    def gen_quad_strip(self, pgon: Pgon):
        """
        ! array should be normalized on WCS origin plane
        :param pgon:
        :return:
        """
        if not isinstance(pgon, gt.Pgon):
            raise TypeError
        vrtxs, far_x, edge_vrtx = self.__stage_one(pgon.normalized)
        trapezoids = self.__stage_two(vrtxs, far_x)
        return self.__stage_three(pgon, edge_vrtx, trapezoids)

    def __stage_one(self, arr):
        """
        first stage
        1. determine vertex category
        2. determine sweep direction
        3. create edge list
        :param arr:
        :return:
        """
        edge_vrtx = []
        arr = arr[:, :-1]

        def __vertex_comparator(obj, sbj):
            if np.isclose(obj.y, sbj.y, atol=ATOL):
                if np.isclose(obj.x, sbj.x, atol=ATOL):
                    return 0
                elif obj.x < sbj.x:
                    return -1
                else:
                    return 1
            elif obj.y < sbj.y:
                return -1
            else:
                return 1

        rb = RedBlackTree(comparator=__vertex_comparator)  # sort by y,x
        # prepare for the first
        prev_v = gt.Pnt(*arr[:3, -1])  # not to consider last
        this_v = gt.Pnt(*arr[:3, 0])

        prev_e = self.__Edge(this_v, prev_v)
        # to maintain membership mytest through hash?
        last_v = prev_v
        first_v = this_v
        last_e = prev_e

        # find far x for further research
        far_x = -inf
        num_v = arr.shape[1]
        for i in range(num_v):  # not to consider last
            if i == num_v - 2:
                this_v = gt.Pnt(*arr[:3, i])
                next_v = last_v
                next_e = self.__Edge(this_v, next_v)
            elif i == num_v - 1:
                this_v = last_v
                next_v = first_v
                next_e = last_e
            else:
                this_v = gt.Pnt(*arr[:3, i])
                next_v = gt.Pnt(*arr[:3, (i + 1) % num_v])
                next_e = self.__Edge(this_v, next_v)
            # update far x, +100 not to mytest with overlapping vertex
            if far_x < this_v.x + 100:
                far_x = this_v.x + 100

            vrtx = self.__Vrtx(this_v)
            # ignoring horizontal
            if gt.Vec.cross(prev_e.geo.as_vec(), next_e.geo.as_vec()) == 0:
                e, s = sorted((prev_e, next_e), key=lambda x: x.low.y)
                e.extand(s.high)
                prev_v, this_v, prev_e = prev_v, next_v, prev_e
            else:
                # determine category and edge connection
                if np.isclose(prev_v.y, this_v.y, atol=ATOL):  # left horizontal
                    if next_v.y < this_v.y:  # right below current
                        vrtx.set_category(self.HMAX)
                        vrtx.append_ending_edge(next_e)
                    elif np.isclose(next_v.y, this_v.y, atol=ATOL):  # right horizontal
                        raise  # this cant happen as horizontals are ignored
                        # vrtx.set_category(self.HORI)
                        # not adding horizontal
                    else:  # right upper
                        vrtx.set_category(self.HMIN)
                        vrtx.append_starting_edge(next_e)
                elif prev_v.y < this_v.y:  # left below current
                    if np.isclose(next_v.y, this_v.y, atol=ATOL):  # right horizontal
                        vrtx.set_category(self.HMAX)
                        vrtx.append_ending_edge(prev_e)
                        # not adding horizontal
                    elif next_v.y < this_v.y:  # right below current
                        vrtx.set_category(self.MAX)
                        vrtx.append_ending_edge(next_e)  # order matters?
                        vrtx.append_ending_edge(prev_e)
                    else:  # right above
                        vrtx.set_category(self.INTR)
                        vrtx.append_starting_edge(next_e)
                        vrtx.append_ending_edge(prev_e)

                else:  # left upper current
                    if np.isclose(next_v.y, this_v.y, atol=ATOL):  # right horizontal
                        vrtx.set_category(self.HMIN)
                        vrtx.append_starting_edge(prev_e)
                        # not adding horizontal
                    elif next_v.y < this_v.y:  # right below current
                        vrtx.set_category(self.INTR)
                        vrtx.append_starting_edge(prev_e)
                        vrtx.append_ending_edge(next_e)
                    else:  # right upper
                        vrtx.set_category(self.MIN)
                        vrtx.append_starting_edge(prev_e)
                        vrtx.append_starting_edge(next_e)

                # find sweep direction
                xvec, yvec = next_v - this_v, prev_v - this_v
                norm = gt.Vec.dot(gt.ZVec(), gt.Vec.cross(xvec, yvec))

                if vrtx.cat == self.HORI:
                    vrtx.set_sweep_dir(self.NONE)
                elif vrtx.cat == self.HMIN:
                    if 0 < norm:
                        vrtx.set_sweep_dir(self.NONE)
                    else:
                        vrtx.set_sweep_dir(self.BOTH)
                    # elif np.isclose(next_v.y, this_v.y, atol=ATOL):
                    #     vrtx.set_sweep_dir(self.RIGHT)
                    # else:
                    #     vrtx.set_sweep_dir(self.LEFT)
                elif vrtx.cat == self.HMAX:
                    # vrtx.set_sweep_dir(self.BOTH)
                    if np.isclose(next_v.y, this_v.y, atol=ATOL):
                        vrtx.set_sweep_dir(self.LEFT)
                    else:
                        vrtx.set_sweep_dir(self.RIGHT)
                elif vrtx.cat in (self.MIN, self.MAX):
                    # vrtx.set_sweep_dir(self.BOTH)
                    if 0 < norm:
                        vrtx.set_sweep_dir(self.NONE)
                    else:
                        vrtx.set_sweep_dir(self.BOTH)
                elif vrtx.cat == self.INTR:
                    if prev_v.y < next_v.y:
                        vrtx.set_sweep_dir(self.LEFT)
                    else:
                        vrtx.set_sweep_dir(self.RIGHT)

                # record point
                rb.insert(vrtx)
                edge_vrtx.append(this_v)
                # update for next vertex
                prev_v, this_v, prev_e = this_v, next_v, next_e
        return rb, far_x, edge_vrtx

    def __stage_two(self, vrtxs, far_x):
        trapezoids = self.__Trapezoids()

        def __edge_comparator(obj, sbj):
            # check side for inserting edge's vertex and far_x
            if obj is sbj:
                return 0
            if obj.low == sbj.low and obj.high == sbj.high:
                return 0

            far_pnt = gt.Pnt(far_x, obj.low.y, 0)
            is_same_side = sbj.pnts_share_side(obj.low, far_pnt)
            # object edge's vertex touches subject edge
            if is_same_side is None:
                if np.isclose(obj.low.x, obj.low.x, atol=ATOL):
                    # for v shape, need to determine which is left
                    # by gradiant
                    if np.isclose(obj.gradient, sbj.gradient, atol=ATOL):
                        if np.isclose(obj.high.y, sbj.high.y, atol=ATOL):  # exactly same
                            return 0
                        elif obj.high.y < sbj.high.y:
                            return -1
                        else:
                            return 1
                    elif obj.gradient < sbj.gradient:
                        return -1
                    else:
                        return 1
                elif obj.low.x < sbj.low.x:
                    return -1
                else:  # go right includes equal
                    return 1
            elif is_same_side:  # else search right, +1
                return 1
            else:  # if side differs search left, -1
                return -1

        edges = RedBlackTree(__edge_comparator)
        # find trapezoids
        for i, vrtx in enumerate(vrtxs):
            print(vrtx)
            if edges:
                left_edge = None
                right_edge = None
                if vrtx.sweep_dir == self.NONE:
                    if len(vrtx.ending_edges) == 2:  # summit trapezoid, simply join two endings
                        trapezoids.add(vrtx.ending_edges[0].geo, vrtx.ending_edges[1].geo)
                    else:
                        pass
                        # raise Exception('unknown')
                # LEFT RIGHT is for category INTR
                elif vrtx.sweep_dir == self.LEFT:
                    if vrtx.ending_edges:
                        left_edge = edges.search_lesser(vrtx.ending_edges[0])
                        if left_edge:
                            left_seg = left_edge.cut(vrtx.y)
                            right_seg = vrtx.ending_edges[0].geo
                            trapezoids.add(left_seg, right_seg)

                elif vrtx.sweep_dir == self.RIGHT:
                    if vrtx.ending_edges:
                        right_edge = edges.search_greater(vrtx.ending_edges[0])
                        if right_edge:
                            right_seg = right_edge.cut(vrtx.y)
                            left_seg = vrtx.ending_edges[0].geo
                            trapezoids.add(left_seg, right_seg)

                elif vrtx.sweep_dir == self.BOTH:
                    left_edge = None
                    right_edge = None
                    # find left right intersection edges
                    if vrtx.cat == self.MAX:
                        # there are two separate trapezoids
                        # first
                        left_edge = edges.search_lesser(vrtx.ending_edges[0])
                        right_edge = edges.search_greater(left_edge)
                        trapezoids.add(left_edge.cut(vrtx.y), right_edge.cut(vrtx.y))
                        # second
                        right_edge = edges.search_greater(vrtx.ending_edges[1])
                        left_edge = edges.search_lesser(right_edge)
                        trapezoids.add(left_edge.cut(vrtx.y), right_edge.cut(vrtx.y))

                    else:
                        if vrtx.cat == self.MIN:
                            left_edge = edges.search_lesser(vrtx.starting_edges[0])
                            right_edge = edges.search_greater(left_edge)

                        elif vrtx.cat == self.HMIN:
                            e = vrtx.starting_edges[0]
                            if not e.is_zero:
                                left_edge = edges.search_lesser(e)
                                if left_edge is not None:
                                    right_edge = edges.search_greater(left_edge)
                        elif vrtx.cat == self.HMAX:
                            e = vrtx.ending_edges[0]
                            if not e.is_zero and e in edges:
                                right_edge = edges.search_greater(e)
                                if right_edge:
                                    left_edge = e
                                else:
                                    right_edge = e
                                    left_edge = edges.search_lesser(e)
                        # find segments
                        if left_edge:
                            left_seg = left_edge.cut(vrtx.y)
                        else:
                            left_seg = gt.Lin.from_pnts(vrtx.geo, vrtx.geo)  # 0 line
                        if right_edge:
                            right_seg = right_edge.cut(vrtx.y)
                        else:
                            right_seg = gt.Lin.from_pnts(vrtx.geo, vrtx.geo)  # 0 line

                        if left_seg.length != 0 or right_seg.length != 0:
                            trapezoids.add(left_seg, right_seg)

            # update edges
            for e in vrtx.ending_edges:
                edges.delete_try(e)
            for e in vrtx.starting_edges:
                if not e.is_zero:
                    edges.insert_unique(e)
            # if vrtx.sweep_dir != self.NONE:
            for g in trapezoids.geos:
                print(g)
            # edges.uprint()
        return trapezoids

    def __stage_three(self, pgon, edge_vrtx, trapezoids):
        """
        array compaction into QUAD_STRIP
        and denormalize

        :param trapezoids:
        :return:
        """
        vrtx_array, fill_indxs = trapezoids.generate_array()

        # going to find nearest by bisect to mark correct edge vertex position with tolerance
        sorted_vs = sorted(vrtx_array)
        vtx_idx = {v: i for i, v in enumerate(vrtx_array)}

        # form edge index for GL_LINE_STRIP_ADJACENCY
        edge_indxs = []
        for ev in map(lambda x: tuple(x.xyzw), edge_vrtx):
            # for each edge vertex find closest
            i = bisect.bisect_right(sorted_vs, ev)
            compared = sorted_vs[i - 1]
            edge_indxs.append(vtx_idx[compared])    # edge vertex has to be always in vrtx_array

        # form adjacency
        if edge_indxs[-1] != edge_indxs[0]:  # for first vertex being omitted
            edge_indxs.append(edge_indxs[0])
        edge_indxs.append(edge_indxs[1])
        edge_indxs.append(edge_indxs[2])

        # return denormalized? not sure
        vrtx_array = (pgon.TM * np.array(vrtx_array).T).T
        return vrtx_array, fill_indxs, edge_indxs

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
            return f"<Vrtx {self.__geo},swp:{self.__sweep_dir}, cat:{self.__category}>"

        def __repr__(self):
            return self.__str__()

        def append_starting_edge(self, edge):
            self.__starting_edges.append(edge)

        def append_ending_edge(self, edge):
            if not self.__ending_edges:
                self.__ending_edges.append(edge)
            else:
                # special case for max vertex
                # check gradient
                v0 = self.__ending_edges[0].geo.as_vec()
                v1 = edge.geo.as_vec()
                g0 = v0.x / v0.y
                g1 = v1.x / v1.y
                if g0 < g1:
                    self.__ending_edges.insert(0, edge)
                else:
                    self.__ending_edges.append(edge)

        def set_sweep_dir(self, dir):
            self.__sweep_dir = dir

        def set_category(self, cat):
            self.__category = cat

        @property
        def y(self):
            return self.__geo.y

        @property
        def x(self):
            return self.__geo.x

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
                self.__low = a
                self.__high = b
            elif a.yx > b.yx:
                self.__low = b
                self.__high = a
            else:
                raise ValueError('contradiction')

            # need for point side checking, even if line becomes length 0
            self.__line = gt.Lin.from_pnts(self.__low, self.__high)
            # needed for finding intersection point
            if self.__high.y - self.__low.y == 0:
                self.__gradient = 0
            else:
                self.__gradient = (self.__high.x - self.__low.x) / (self.__high.y - self.__low.y)

        def __str__(self):
            return f"<Edge {self.__low} {self.__high}>"

        def __repr__(self):
            return self.__str__()

        @property
        def low(self):
            return self.__low

        @property
        def high(self):
            return self.__high

        @property
        def gradient(self):
            return self.__gradient

        @property
        def is_zero(self):
            return self.__low == self.__high

        @property
        def geo(self):
            """
            dont return cached, it doesnt reflect updated small

            :return:
            """
            return gt.Lin.from_pnts(self.__low, self.__high)

        def pnts_share_side(self, v0, v_max):
            return self.__line.pnts_share_side(v0, v_max)

        def cut(self, y):
            """
            cut edge at given y and return edge below

            :param y:
            :return:
            """
            # calculate intersection
            if np.isclose(self.__low.y, y, atol=ATOL):
                inter_p = self.__low
            elif np.isclose(self.__high.y, y, atol=ATOL):
                inter_p = self.__high
            else:
                x = self.__gradient * (y - self.__low.y) + self.__low.x
                inter_p = gt.Pnt(x, y, 0)
            # form edge below
            edge_below = gt.Lin.from_pnts(self.__low, inter_p)
            # erase bolow
            self.__low = inter_p
            return edge_below

        def extand(self, high):
            self.__high = high

    class __Trapezoids:
        def __init__(self):
            self.__geos = RedBlackTree(comparator=self.__comparator)

        def __len__(self):
            return len(self.__geos)

        @property
        def geos(self):
            return self.__geos

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
            return vertices, indices
