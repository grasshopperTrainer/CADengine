import numpy as np
from numbers import Number

import gkernel.dtype.geometric.primitive as rg
from gkernel.color.primitive import ClrRGBA
import mkernel.shape as shp
from .primitive_renderer import *
import ckernel.render_context.opengl_context.factories as ogl


class Ray(rg.Ray, shp.Shape):

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(rg.Pnt, shp.Shape):

    def __init__(self, x, y, z):
        """

        :param x: Number, coordinate value x
        :param y: Number, coordinate value y
        :param z: Number, coordinate value z
        """
        pass


class Vec(rg.Vec, shp.Shape):
    pass


class Lin(shp.Shape):
    __dtype = [('vtx', 'f4', 4), ('thk', 'f4', (1, )), ('clr', 'f4', 4)]
    __vrtx_bffr = ogl.ArryBffrFactory(attr_desc=__dtype, attr_loc=(0, 1, 2))
    __vrtx_cache = BffrCache(dtype=__dtype, size=32)
    __vao = ogl.VrtxArryFactory(__vrtx_bffr)

    def __init__(self, s=(0, 0, 0), e=(0, 1, 0)):
        self.__block = self.__vrtx_cache.request_vacant(2)
        self.__geo = rg.Lin(s, e)
        self.geo = rg.Lin(s, e)

        self.__clr = ClrRGBA()
        self.clr = ClrRGBA(0, 0, 0, 1)
        self.__thk = 2

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__block['vtx'][:] = v.T
        self.__geo[:] = v

    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__block['clr'][..., :len(v)] = v   # to accept as much as possible
        self.__clr[:] = v

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self.__block['thk'][...] = v
        self.__thk = v

    @classmethod
    def render(cls):
        """

        :return:
        """
        with cls.__vao:
            cls.__vrtx_bffr.push_all(cls.__vrtx_cache)
            LineRenderer.render(cls.__vrtx_cache.num_used_vrtx)


class Plin(shp.Shape):
    pass


class Pln(rg.Pln, shp.Shape):
    pass


class Tgl(shp.Shape):
    # array buffer and vao
    __dtype = [('vtx', 'f4', 4), ('edge_thk', 'f4', 1), ('edge_clr', 'f4', 4), ('fill_clr', 'f4', 4)]
    __vrtx_bffr = ogl.ArryBffrFactory(attr_desc=__dtype, attr_loc=(0, 1, 2, 3))
    __vrtx_cache = BffrCache(dtype=__dtype, size=32)
    __vao = ogl.VrtxArryFactory(__vrtx_bffr)

    # global settin
    __is_render_edge = True

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
        self.__geo = rg.Tgl()
        self.__fill_clr = ClrRGBA(1, 1, 1, 1)
        self.__edge_clr = ClrRGBA(0, 0, 0, 1)
        self.__edge_thk = 1

        self.geo = rg.Tgl(v0, v1, v2)
        self.clr_fill = ClrRGBA(1, 1, 1, 1)

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, value):
        if not isinstance(value, rg.Tgl):
            raise TypeError
        self.__block['vtx'][:] = value.T
        self.__geo[:] = value

    @property
    def clr_fill(self):
        return self.__fill_clr

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
        self.__block['fill_clr'][..., :len(v)] = v
        self.__fill_clr[:len(v)] = v

    @property
    def edge_clr(self):
        return self.__edge_clr

    @edge_clr.setter
    def edge_clr(self, v):
        """
        set edge color

        :return:
        """
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__block['edge_clr'][..., :len(v)] = v
        self.__fill_clr[:len(v)] = v

    @property
    def edge_thk(self):
        return self.__edge_thk

    @edge_thk.setter
    def edge_thk(self, v):
        self.__block['edge_thk'][:] = v
        self.__edge_thk = v

    def intersect(self, ray):
        raise NotImplementedError

    @classmethod
    def set_render_edge(cls, b):
        if not isinstance(b, bool):
            raise TypeError
        cls.__render_edge = b

    @classmethod
    def render(cls):
        with cls.__vao:
            cls.__vrtx_bffr.push_all(cls.__vrtx_cache)
            TriangleRenderer.render(vrtx_count=cls.__vrtx_cache.num_used_vrtx)
            if cls.__is_render_edge:
                TriangleEdgeRenderer.render(vrtx_count=cls.__vrtx_cache.num_used_vrtx)
