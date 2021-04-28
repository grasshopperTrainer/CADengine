from math import inf
from numbers import Number
from collections import deque
import bisect

import numpy as np
from global_tools.red_black_tree import RedBlackTree
from global_tools.enum import enum

from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV

from gkernel.color import Clr, ClrRGBA
import gkernel.dtype.geometric as gt
from gkernel.constants import ATOL

from mkernel.global_id_provider import GIDP
from .base import GeoShape


class Pgon(GeoShape):
    """
    Polygon shape
    """

    def __init__(self, geo: gt.Pgon, renderer, model):
        vertices, fill_indxs, edge_indxs = _Trapezoidator().gen_quad_strip(geo)

        self.__model = model

        self.__vrtx_block = renderer.vbo.cache.request_block(size=len(vertices))
        self.__vrtx_block['vtx'] = vertices
        self.__vrtx_block['oid'] = GIDP().register_entity(self).as_rgba_float()

        # add PRV at the end to draw separately
        offset = self.__vrtx_block.indices[0]  # min index
        self.__fill_indx_block = renderer.fill_ibo.cache.request_block(size=len(fill_indxs) + 1)
        self.__fill_indx_block['idx', :-1] = [offset + i if i != PRV else PRV for i in fill_indxs]
        self.__fill_indx_block['idx', -1] = PRV

        self.__edge_indx_block = renderer.edge_ibo.cache.request_block(size=len(edge_indxs) + 1)
        self.__edge_indx_block['idx', :-1] = [offset + i for i in edge_indxs]
        self.__edge_indx_block['idx', -1] = PRV

        self.__geo = None
        self.__thk = None
        self.__clr_edge = None
        self.__clr_fill = None

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

    def delete(self):
        self.__vrtx_block.release()
        self.__edge_indx_block.release()
        self.__fill_indx_block.release()

        GIDP.deregister(self)
        self.__model.remove(self)

        for k, v in self.__dict__.items():
            setattr(self, k, None)


class CAT(enum):
    MAX = 'MAX'
    MIN = 'MIN'
    HMAX = 'HMAX'
    HMIN = 'HMIN'
    HORI = 'HORI'
    INTR = 'INTR'


class SWEEP(enum):
    LEFT = 'LEFT'
    NONE = 'NONE'
    RIGHT = 'RIGHT'
    BOTH = 'BOTH'


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
        four operations are executed within single loop
        1. remove horizontal vertices
        2. update far x
        3. record edge vertices

        trapezoidation first stage
        4. define vertex RBT
            1. determine vertex category
            2. determine sweep direction
            3. create edge list

        :param arr:
        :return:
        """
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
        far_x = -inf  # find far x for further research
        vertices = deque([gt.Pnt(*coord) for coord in arr[:3].T])
        edges, edge_vrtx = deque(), deque()
        while vertices:
            if not edges:
                a, b = vertices.popleft(), vertices[0]
                edges.append(self.__Edge(a, b))
                edge_vrtx.append(a)
                continue

            this_vrtx = vertices.popleft()
            vrtx_next = vertices[0] if vertices else edge_vrtx[0]
            edge_next = self.__Edge(this_vrtx, vrtx_next)

            # 1. ignore horizontal
            if gt.Vec.cross(edges[-1].geo.as_vec(), edge_next.geo.as_vec()) == 0:
                # determine which vertex should become high
                low, _, high = sorted((edges[-1].high, edges[-1].low, vrtx_next), key=lambda v: v.yx)
                edges[-1].low = low
                edges[-1].high = high
            else:
                edges.append(edge_next)
                edge_vrtx.append(this_vrtx)  # 3. record edge vertex
                far_x = max(far_x, this_vrtx.x + 100)  # 2. update far x

        # check last horizontal
        if gt.Vec.cross(edges[-1].geo.as_vec(), edges[0].geo.as_vec()) == 0:
            # determine which vertex should become high
            low, _, __, high = sorted((edges[-1].high, edges[-1].low, edges[0].high, edges[0].low), key=lambda v: v.yx)
            edges[0].low = low
            edges[0].high = high
            edges.pop()
            edge_vrtx.popleft()
            edge_vrtx.appendleft(edge_vrtx.pop())

        # 4. record trap vertex
        for i, v in enumerate(edge_vrtx):
            vrtx = self.__Vrtx(v)
            rb.insert(vrtx)
            pi, ni = i - 1, (i + 1) % len(edge_vrtx)
            vrtx.determine_cat_sweep(edge_vrtx[pi], v, edge_vrtx[ni], edges[pi], edges[i])

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
                if sbj.pnts_share_side(obj.high, far_pnt):
                    return 1
                else:
                    return -1
            elif is_same_side:  # else search right, +1
                return 1
            else:  # if side differs search left, -1
                return -1

        edges = RedBlackTree(__edge_comparator)
        # find trapezoids
        for i, vrtx in enumerate(vrtxs):
            print(vrtx)
            if edges:
                if vrtx.cat == CAT.MAX:
                    # weav peak
                    if vrtx.sweep_dir == SWEEP.NONE:
                        edges.uprint()
                        trapezoids.tryadd_right_left(edges, vrtx.ending_edges[0], vrtx.y)
                    elif vrtx.sweep_dir == SWEEP.BOTH:
                        trapezoids.tryadd_left_right(edges, vrtx.ending_edges[0], vrtx.y)
                        trapezoids.tryadd_right_left(edges, vrtx.ending_edges[1], vrtx.y)

                elif vrtx.sweep_dir == SWEEP.LEFT:
                    trapezoids.tryadd_left_right(edges, vrtx.ending_edges[0], vrtx.y)
                elif vrtx.sweep_dir == SWEEP.RIGHT:
                    trapezoids.tryadd_right_left(edges, vrtx.ending_edges[0], vrtx.y)
                elif vrtx.sweep_dir == SWEEP.BOTH:
                    trapezoids.tryadd_right_left(edges, vrtx.starting_edges[0], vrtx.y)
                elif vrtx.sweep_dir == SWEEP.NONE:
                    pass

            # update edges
            for e in vrtx.ending_edges:
                edges.delete_try(e)
            for e in vrtx.starting_edges:
                if not e.is_zero:
                    edges.insert_unique(e)

            for i in trapezoids.geos:
                print(i)
            edges.uprint()
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
            edge_indxs.append(vtx_idx[compared])  # edge vertex has to be always in vrtx_array

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

            self.__sweep = None
            self.__category = None

            self.__starting_edges = []
            self.__ending_edges = []

        def __str__(self):
            return f"<Vrtx {self.__geo},swp:{self.__sweep}, cat:{self.__category}>"

        def __repr__(self):
            return self.__str__()

        def determine_cat_sweep(self, prev_v, this_v, next_v, prev_e, next_e):
            self.__determine_cat(prev_v, this_v, next_v, prev_e, next_e)
            self.__determine_sweep(prev_v, this_v, next_v, prev_e, next_e)

        def __determine_cat(self, prev_v, this_v, next_v, prev_e, next_e):
            # determine category and edge connection
            if np.isclose(prev_v.y, this_v.y, atol=ATOL):  # left horizontal
                if np.isclose(next_v.y, this_v.y, atol=ATOL):  # right horizontal
                    raise  # this cant happen as horizontals are ignored
                elif this_v.y < next_v.y:  # right above
                    # consider as MIN
                    self.__category = CAT.HMIN
                    self.__append_ending_edge(prev_e)
                    self.__append_starting_edge(next_e)
                else:  # right below
                    # consider as MAX
                    self.__category = CAT.HMAX
                    self.__append_ending_edge(next_e)
                    # self.__starting_edges.append(prev_e)

            elif prev_v.y < this_v.y:  # left below
                if np.isclose(this_v.y, next_v.y, atol=ATOL):  # right horizontal
                    # consider as MAX
                    self.__category = CAT.HMAX
                    self.__append_ending_edge(prev_e)
                    # self.__starting_edges.append(next_e)
                elif this_v.y < next_v.y:  # right above
                    self.__category = CAT.INTR
                    self.__append_ending_edge(prev_e)
                    self.__append_starting_edge(next_e)
                else:  # right below current
                    self.__category = CAT.MAX
                    self.__append_ending_edge(next_e)
                    self.__append_ending_edge(prev_e)

            else:  # left above
                if np.isclose(this_v.y, next_v.y, atol=ATOL):  # right horizontal
                    # consider as MIN
                    self.__category = CAT.HMIN
                    self.__append_starting_edge(prev_e)
                    self.__append_ending_edge(next_e)
                elif this_v.y < next_v.y:  # right upper
                    self.__category = CAT.MIN
                    self.__append_starting_edge(prev_e)
                    self.__append_starting_edge(next_e)
                else:  # right below current
                    self.__category = CAT.INTR
                    self.__append_starting_edge(prev_e)
                    self.__append_ending_edge(next_e)

        def __determine_sweep(self, prev_v, this_v, next_v, prev_e, next_e):
            # find sweep direction
            xvec, yvec = next_v - this_v, prev_v - this_v
            norm = gt.Vec.dot(gt.ZVec(), gt.Vec.cross(xvec, yvec))
            if self.__category == CAT.MIN:
                if 0 < norm:
                    self.__sweep = SWEEP.NONE
                else:
                    self.__sweep = SWEEP.BOTH
            elif self.__category == CAT.HMIN:
                if 0 < norm:
                    self.__sweep = SWEEP.NONE
                    # if np.isclose(this_v.y, next_v.y, atol=ATOL):
                    #     self.__sweep = SWEEP.RIGHT
                    # else:
                    #     self.__sweep = SWEEP.LEFT
                else:
                    self.__sweep = SWEEP.BOTH
            elif self.__category == CAT.MAX:
                if 0 < norm:
                    self.__sweep = SWEEP.NONE
                else:
                    self.__sweep = SWEEP.BOTH
            elif self.__category == CAT.HMAX:
                if np.isclose(this_v.y, next_v.y, atol=ATOL):
                    self.__sweep = SWEEP.LEFT
                else:
                    self.__sweep = SWEEP.RIGHT
            elif self.__category == CAT.INTR:
                if prev_v.y < next_v.y:
                    self.__sweep = SWEEP.LEFT
                else:
                    self.__sweep = SWEEP.RIGHT
            else:
                raise Exception('contradiction')

        def __append_starting_edge(self, edge):
            if not self.__starting_edges:
                self.__starting_edges.append(edge)
            else:
                e = self.__starting_edges[0]
                far_x = max(e.low.x, e.high.x) + 100
                far_pnt = gt.Pnt(far_x, e.high.y, 0)
                if e.pnts_share_side(far_pnt, edge.high):
                    self.__starting_edges.append(edge)
                else:
                    self.__starting_edges.insert(0, edge)

        def __append_ending_edge(self, edge):
            if not self.__ending_edges:
                self.__ending_edges.append(edge)
            else:  # maintain order
                e = self.__ending_edges[0]
                far_x = max(e.low.x, e.high.x) + 100
                far_pnt = gt.Pnt(far_x, e.low.y, 0)
                if e.pnts_share_side(far_pnt, edge.low):
                    self.__ending_edges.append(edge)
                else:
                    self.__ending_edges.insert(0, edge)

        @property
        def y(self):
            return self.__geo.y

        @property
        def x(self):
            return self.__geo.x

        @property
        def sweep_dir(self):
            return self.__sweep

        @property
        def cat(self):
            return self.__category

        @property
        def starting_edges(self):
            return self.__starting_edges

        @property
        def ending_edges(self):
            return self.__ending_edges

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

        @low.setter
        def low(self, v):
            self.__low = v

        @property
        def high(self):
            return self.__high

        @high.setter
        def high(self, v):
            self.__high = v

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

        def intersect(self, y):
            # calculate intersection
            if np.isclose(self.__low.y, y, atol=ATOL):
                i = self.__low
            elif np.isclose(self.__high.y, y, atol=ATOL):
                i = self.__high
            else:
                x = self.__gradient * (y - self.__low.y) + self.__low.x
                i = gt.Pnt(x, y, 0)
            return i

        def set_low(self, pnt):
            """
            cut edge at given y and return edge below

            :param y:
            :return:
            """
            self.__low = pnt

        def set_high(self, high):
            """

            :param high:
            :return:
            """
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

        def tryadd_left_right(self, edges, e, y):
            left_edge = edges.search_lesser(e)
            if left_edge:
                right_edge = edges.search_greater(left_edge)
                if right_edge:
                    self.__try_cut_add(left_edge, right_edge, y)

        def tryadd_right_left(self, edges, e, y):
            right_edge = edges.search_greater(e)
            if right_edge:
                left_edge = edges.search_lesser(right_edge)
                if left_edge:
                    self.__try_cut_add(left_edge, right_edge, y)

        def __is_zero(self, a, b, c, d):
            if np.isclose(a.y, c.y, atol=ATOL) or np.isclose(b.y, d.y, atol=ATOL):
                return True
            # check width
            if np.isclose(a.x, b.x, atol=ATOL) and np.isclose(c.x, d.x, atol=ATOL):
                return True
            return False

        def __try_cut_add(self, left_edge, right_edge, y):
            a = left_edge.low
            b = right_edge.low
            c = left_edge.intersect(y)
            d = right_edge.intersect(y)
            if not self.__is_zero(a, b, c, d):
                left_edge.set_low(c)
                right_edge.set_low(d)
                self.__geos.insert((a.xyzw, b.xyzw, c.xyzw, d.xyzw))

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
