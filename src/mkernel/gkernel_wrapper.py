import numpy as np
from numbers import Number

import gkernel.dtype.geometric.primitive as rg
from gkernel.color.primitive import ClrRGBA
import mkernel.shape as shp
from .primitive_renderer import *
from global_tools.singleton import Singleton
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV

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
        # set vertex attributes
        self.__vrtx_block = PointRenderer().vbo.cache.request_block(size=1)
        # set index buffer
        self.__indx_block = PointRenderer().square_ibo.cache.request_block(size=1)
        self.__indx_block['idx'] = self.__vrtx_block.indices

        self.__frm = self.FORM_SQUARE
        self.__geo = rg.Pnt()
        self.__clr = ClrRGBA()
        self.__dia = 5

        self.geo = rg.Pnt(x, y, z)
        self.clr = ClrRGBA(1, 1, 1, 1)
        self.dia = 5


    # form constants
    @property
    def FORM_SQUARE(self):
        return self.__SquareForm()

    @property
    def FORM_CIRCLE(self):
        return self.__CircleForm()

    @property
    def FORM_TRIANGLE(self):
        return self.__TriangleForm()

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, (tuple, list, rg.Pnt)):
            raise TypeError
        self.__vrtx_block['vtx'] = v.T
        self.__geo = v


    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (tuple, list, np.ndarray)):
            raise TypeError
        self.__vrtx_block['clr'] = v
        self.__clr[:] = v

    @property
    def dia(self):
        return self.__dia

    @dia.setter
    def dia(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self.__vrtx_block['dia'] = v
        self.__dia = v

    @property
    def frm(self):
        return self.__frm

    @frm.setter
    def frm(self, v):
        """
        register at corresponding index buffer

        :param v:
        :return:
        """
        if not isinstance(v, self.__Form):
            raise TypeError
        # ignore if setting is redundant
        if self.__frm == v:
            return
        # swap
        self.__indx_block.release(PRV)
        self.__indx_block = v.ibo.cache.request_block(size=1)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        self.__frm = v

    @classmethod
    def render(cls):
        PointRenderer().render()

    class __Form:
        @property
        def ibo(self):
            return getattr(self, f"_{self.__class__.__name__.replace('_', '')}__ibo")

    @Singleton
    class __CircleForm(__Form):
        def __init__(self):
            self.__ibo = PointRenderer().circle_ibo

    @Singleton
    class __SquareForm(__Form):
        def __init__(self):
            self.__ibo = PointRenderer().square_ibo

    @Singleton
    class __TriangleForm(__Form):
        def __init__(self):
            self.__ibo = PointRenderer().triangle_ibo


class Vec(rg.Vec, shp.Shape):
    pass


class Lin(shp.Shape):

    def __init__(self, s=(0, 0, 0), e=(0, 1, 0)):
        self.__vrtx_block = LineRenderer().vbo.cache.request_block(size=2)

        self.__geo = rg.Lin()
        self.__clr = ClrRGBA()
        self.__thk = 2
        self.geo = rg.Lin(s, e)
        self.clr = ClrRGBA(0, 0, 0, 1)
        # set index
        self.__indx_block = LineRenderer().ibo.cache.request_block(size=2)
        self.__indx_block['idx'] = self.__vrtx_block.indices

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, rg.Lin):
            raise TypeError
        self.__vrtx_block['vtx'] = v.T
        self.__geo[:] = v

    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self.__vrtx_block['clr'] = v  # to accept as much as possible
        self.__clr[:] = v

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self.__vrtx_block['thk'] = v
        self.__thk = v

    @classmethod
    def render(cls):
        """
        passer
        :return:
        """
        LineRenderer().render()


class Plin(shp.Shape):
    pass


class Pln(rg.Pln, shp.Shape):
    pass


class Tgl(shp.Shape):
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
        self.__vrtx_block = TriangleRenderer().vbo.cache.request_block(size=3)
        # registering at ibo
        self.__indx_block = TriangleRenderer().ibo.cache.request_block(size=3)
        self.__indx_block['idx'] = self.__vrtx_block.indices
        # just filling correct placeholder
        self.__geo = rg.Tgl()
        self.__fill_clr = ClrRGBA()
        self.__edge_clr = ClrRGBA()
        self.__edge_thk = 1
        # actual value assignment
        self.geo = rg.Tgl(v0, v1, v2)
        self.clr_fill = ClrRGBA(1, 1, 1, 1)
        self.edge_clr = ClrRGBA(0, 0, 0, 1)

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, value):
        if not isinstance(value, rg.Tgl):
            raise TypeError
        self.__vrtx_block['vtx'] = value.T
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
        self.__vrtx_block['fill_clr'] = v
        self.__fill_clr[:] = v

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
        self.__vrtx_block['edge_clr'] = v
        self.__fill_clr[:] = v

    @property
    def edge_thk(self):
        return self.__edge_thk

    @edge_thk.setter
    def edge_thk(self, v):
        self.__vrtx_block['edge_thk'] = v
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
        TriangleRenderer().vbo.get_entity().push_cache()
        TriangleRenderer().render(cls.__is_render_edge)
