import os
import numpy as np

import gkernel.dtype.geometric.primitive as pg
from gkernel.color.primitive import ClrRGBA
import mkernel.shape as shp
import ckernel.render_context.opengl_context.ogl_factories as ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ckernel.render_context.opengl_context.uniform_pusher import UniformPusher
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from .primitive_renderer import *


class Ray(pg.Ray, shp.Shape):

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(pg.Pnt, shp.Shape):

    def __init__(self, x, y, z):
        """

        :param x: Number, coordinate value x
        :param y: Number, coordinate value y
        :param z: Number, coordinate value z
        """
        pass


class Vec(pg.Vec, shp.Shape):
    pass


class Lin(pg.Lin, shp.Shape):
    pass


class Pln(pg.Pln, shp.Shape):
    pass


class Tgl(shp.Shape):
    # array buffer and vao
    __dtype = [('vtx', 'f4', 4), ('clr_edge', 'f4', 4), ('clr_fill', 'f4', 4)]
    __vrtx_bffr = ogl.ArryBffrFactory(attr_desc=__dtype, attr_loc=(0, 1, 2))
    __vrtx_cache = BffrCache(dtype=__dtype, size=32)
    __vao = ogl.VrtxArryFactory(__vrtx_bffr)

    def __init__(self, v0, v1, v2):
        """

        :param v0:
        :param v1:
        :param v2:

        :param __block: this is merely a container for block location in raw array
                        used when shape is deleted thus has to free space in raw array
                        ! need to be updated when local value is updated
        :param __geo: exposed geometric data
                      ! always a copy of __block to prevent undesired value contamination
        """
        self.__block = self.__vrtx_cache.request_vacant(3)
        self.__geo = pg.Tgl()
        self.__clr_fill = ClrRGBA(1, 1, 1, 1)
        self.__clr_edge = ClrRGBA(0, 0, 0, 1)

        self.geo = pg.Tgl(v0, v1, v2)
        self.clr_fill = ClrRGBA(1, 1, 1, 1)

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, value):
        if not isinstance(value, pg.Tgl):
            raise TypeError
        self.__block['vtx'][:] = value.T
        self.__geo[:] = value

    @property
    def clr_fill(self):
        return self.__clr_fill

    @clr_fill.setter
    def clr_fill(self, v):
        """
        set fill color

        currently all vertex has color value and are all the same
        :param v: color value, in default color format is RGBA
        :return:
        """
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__block['clr_fill'][..., :len(v)] = v
        self.__clr_fill[:len(v)] = v

    @property
    def clr_edge(self):
        return self.__clr_edge

    @clr_edge.setter
    def clr_edge(self, v):
        """
        set edge color

        :return:
        """
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__block['clr_edge'][..., :len(v)] = v
        self.__clr_fill[:len(v)] = v

    def intersect(self, ray):
        raise NotImplementedError

    @classmethod
    def render_face(cls):
        cls.__vrtx_bffr.push_all(cls.__vrtx_cache)
        TriangleRenderer.render(vao=cls.__vao, vrtx_count=cls.__vrtx_cache.count_used_vrtx)

    @classmethod
    def render_line(cls):
        cls.__vrtx_bffr.push_all(cls.__vrtx_cache)
        LineRenderer.render(vao=cls.__vao, vrtx_count=cls.__vrtx_cache.count_used_vrtx)

    @classmethod
    def render_point(cls):
        raise NotImplementedError

    @classmethod
    def render_default(cls):
        cls.render_face()
        cls.render_line()
