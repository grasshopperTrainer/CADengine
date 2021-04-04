from numbers import Number
import numpy as np
import gkernel.dtype.geometric as gt
from gkernel.color.primitive import ClrRGBA, Clr
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
from mkernel.renderers.base import Renderer
from .base import SimpleShape


class Ray(SimpleShape):

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(SimpleShape):

    def __init__(self, geo, renderer: Renderer, model):
        # request blocks
        vb = renderer.vbo.cache.request_block(size=1)
        vb['cid'] = GIDP().register_entity(self).as_rgb_float()
        # index block will be set at `frm` setter
        super().__init__(model, vb, None)

        # enums
        self.__form_square = self.__Form(renderer.square_ibo, 'SQUARE')
        self.__form_circle = self.__Form(renderer.circle_ibo, 'CIRCLE')
        self.__form_tirangle = self.__Form(renderer.triangle_ibo, 'TRIANGLE')

        self.__frm = None
        self.__geo = None
        self.__clr = None
        self.__dia = None

        self.frm = self.FORM_SQUARE
        self.geo = geo
        self.clr = ClrRGBA(1, 1, 1, 1)
        self.dia = 5

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
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, (tuple, list, gt.Pnt)):
            raise TypeError
        self._vrtx_block['vtx'] = v.T
        if self.__geo is None:
            self.__geo = v
        else:
            self.__geo[:] = v

    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (tuple, list, np.ndarray)):
            raise TypeError
        self._vrtx_block['clr'] = v
        if self.__clr is None:
            self.__clr = v
        else:
            self.__clr[:] = v

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


class Vec(SimpleShape):
    pass


class Lin(SimpleShape):
    def __init__(self, geo, renderer, model):
        # request blocks
        vb = renderer.vbo.cache.request_block(size=2)
        vb['cid'] = GIDP().register_entity(self).as_rgb_float()
        ib = renderer.ibo.cache.request_block(size=2)
        ib['idx'] = vb.indices
        super().__init__(model, vb, ib)

        self.__geo = None
        self.__clr = None
        self.__thk = None

        self.geo = geo
        self.clr = ClrRGBA(0, 0, 0, 1)
        self.thk = 1

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Lin):
            raise TypeError
        self._vrtx_block['vtx'] = v.T
        if self.__geo is None:
            self.__geo = v
        else:
            self.__geo[:] = v

    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self._vrtx_block['clr'] = v
        if self.__clr is None:
            self.__clr = v
        else:
            self.__clr[:] = v

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self._vrtx_block['thk'] = v
        self.__thk = v


class Plin(SimpleShape):
    def __init__(self, geo, renderer, model):
        """

        :param vs: number of vertices coordinate that form polyline
        """
        # this will check input validity
        vb = renderer.vbo.cache.request_block(size=len(geo))
        vb['cid'] = GIDP().register_entity(self).as_rgb_float()
        # +1 for primitive restart value
        ib = renderer.ibo.cache.request_block(size=len(geo) + 1)
        ib['idx', :-1] = vb.indices
        ib['idx', -1] = PRV
        super().__init__(model, vb, ib)

        self.__geo = geo
        self.__clr = ClrRGBA()
        self.__thk = 1

        self.geo = geo
        self.clr = ClrRGBA(0, 0, 0, 1)
        self.thk = 1

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Plin):
            raise TypeError
        self._vrtx_block['vtx'] = v.T
        self.__geo[:] = v

    @property
    def clr(self):
        return self.__clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (tuple, list, Clr)):
            raise TypeError
        self._vrtx_block['clr'] = v
        self.__clr[:] = v

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, v):
        if not isinstance(v, Number):
            raise TypeError
        self._vrtx_block['thk'] = v
        self.__thk = v


class Tgl(SimpleShape):
    __is_render_edge = True

    def __init__(self, geo, renderer, model):
        vb = renderer.vbo.cache.request_block(size=3)
        vb['cid'] = GIDP().register_entity(self).as_rgb_float()
        ib = renderer.ibo.cache.request_block(size=3)
        ib['idx'] = vb.indices
        super().__init__(model, vb, ib)

        # just filling correct placeholder
        self.__geo = None
        self.__fill_clr = None
        self.__edge_clr = None
        self.__edge_thk = None
        # actual value assignment
        self.geo = geo
        self.clr_fill = ClrRGBA(1, 1, 1, 1)
        self.edge_clr = ClrRGBA(0, 0, 0, 1)
        self.edge_thk = 0.5

    @property
    def geo(self):
        return self.__geo

    @geo.setter
    def geo(self, v):
        if not isinstance(v, gt.Tgl):
            raise TypeError
        self._vrtx_block['vtx'] = v.T
        if self.__geo is None:
            self.__geo = v
        else:
            self.__geo[:] = v

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
        self._vrtx_block['fill_clr'] = v
        if self.__fill_clr is None:
            self.__fill_clr = v
        else:
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
        self._vrtx_block['edge_clr'] = v
        if self.__edge_clr is None:
            self.__edge_clr = v
        else:
            self.__edge_clr[:] = v

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
