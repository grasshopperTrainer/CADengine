from numbers import Number
import numpy as np
import gkernel.dtype.geometric as gt
from gkernel.color.primitive import ClrRGBA, Clr
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
from mkernel.renderers.base import Renderer
from .base import SimpleGeoShape


class Ray(SimpleGeoShape):

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(SimpleGeoShape):

    def __init__(self, geo, renderer: Renderer, model):
        # request blocks
        vb = renderer.vbo.cache.request_block(size=1)
        oid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        # index block will be set at `frm` setter
        super().__init__(model, vb, None, oid)

        # enums
        self.__form_square = self.__Form(renderer.square_ibo, 'SQUARE')
        self.__form_circle = self.__Form(renderer.circle_ibo, 'CIRCLE')
        self.__form_tirangle = self.__Form(renderer.triangle_ibo, 'TRIANGLE')

        self.geo = geo
        self.clr = ClrRGBA(1, 1, 1, 1)
        self.__frm, self.frm = None, self.FORM_SQUARE
        self.__dia = self.dia = 5

    # form constants
    @property
    def FORM_SQUARE(self):
        return self.__form_square

    @property
    def FORM_CIRCLE(self):
        return self.__form_circle

    @property
    def FORM_TRIANGLE(self):
        return self.__form_tirangle

    @property
    def dia(self):
        return self.__dia

    @dia.setter
    def dia(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self._vrtx_block['dia'] = v
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
        # swapping index block
        # remove old
        if self._indx_block is not None:
            self._indx_block.release()

        # set new
        self._indx_block = v.ibo.cache.request_block(size=1)
        self._indx_block['idx'] = self._vrtx_block.indices
        self.__frm = v

    def __del__(self):
        print("shape Pnt gc")

    class __Form:
        def __init__(self, ibo, name):
            self.__ibo = ibo
            self.__name = name

        @property
        def ibo(self):
            return self.__ibo

        def __str__(self):
            return f"<ENUM {self.__name}>"


class Vec(SimpleGeoShape):
    pass


class Lin(SimpleGeoShape):
    def __init__(self, geo, renderer, model):
        # request blocks
        vb = renderer.vbo.cache.request_block(size=2)
        oid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        ib = renderer.ibo.cache.request_block(size=2)
        ib['idx'] = vb.indices
        super().__init__(model, vb, ib, oid)

        self.geo = geo
        self.clr = ClrRGBA(0, 0, 0, 1)
        self.__thk = self.thk = 1

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self._vrtx_block['thk'] = v
        self.__thk = v


class Plin(SimpleGeoShape):
    def __init__(self, geo, renderer, model):
        """

        :param vs: number of vertices coordinate that form polyline
        """
        # this will check input validity
        vb = renderer.vbo.cache.request_block(size=len(geo))
        oid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        # +1 for primitive restart value
        ib = renderer.ibo.cache.request_block(size=len(geo) + 1)
        ib['idx', :-1] = vb.indices
        ib['idx', -1] = PRV
        super().__init__(model, vb, ib, oid)

        self.geo = geo
        self.clr = ClrRGBA(0, 0, 0, 1)
        self.__thk = self.thk = 1

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self._vrtx_block['thk'] = v
        self.__thk = v


class Tgl(SimpleGeoShape):
    __is_render_edge = True

    def __init__(self, geo, renderer, model):
        vb = renderer.vbo.cache.request_block(size=3)
        oid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        ib = renderer.ibo.cache.request_block(size=3)
        ib['idx'] = vb.indices
        super().__init__(model, vb, ib, oid)

        # actual value assignment
        self.geo = geo
        self.__clr_fill = self.clr_fill = ClrRGBA(1, 1, 1, 1)
        self.__clr_edge = self.clr_edge = ClrRGBA(0, 0, 0, 1)
        self.__edge_thk = self.edge_thk = 0.5

    @property
    def clr(self):
        return self.__clr_fill, self.__clr_edge

    @clr.setter
    def clr(self, v):
        self.clr_fill = v
        self.clr_edge = v

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
        self._vrtx_block['fill_clr'] = v
        if self.__clr_fill is None:
            self.__clr_fill = v
        else:
            self.__clr_fill[:] = v

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
        self._vrtx_block['edge_clr'] = v
        if self.__clr_edge is None:
            self.__clr_edge = v
        else:
            self.__clr_edge[:] = v

    @property
    def edge_thk(self):
        return self.__edge_thk

    @edge_thk.setter
    def edge_thk(self, v):
        self._vrtx_block['edge_thk'] = v
        self.__edge_thk = v

    def intersect(self, ray):
        raise NotImplementedError

    @classmethod
    def set_render_edge(cls, b):
        if not isinstance(b, bool):
            raise TypeError
        cls.__render_edge = b
