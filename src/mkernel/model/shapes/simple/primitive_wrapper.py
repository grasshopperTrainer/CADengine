from numbers import Number
import numpy as np
from gkernel.color.primitive import ClrRGBA
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
from mkernel.view.sub_renderer import Renderer
from .base import GeoShape


class Ray(GeoShape):
    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(GeoShape):

    def __init__(self, geo):
        super().__init__(geo, clr=(1, 1, 1, 1))
        self._frm = self.frm = 's'
        self._dia = self.dia = 10

    @property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, val):
        self.model.update_viewer_cache(self, 'dia', val)

    @property
    def frm(self):
        return self._frm

    @frm.setter
    def frm(self, val):
        self.model.update_viewer_cache(self, 'frm', val)

    def __del__(self):
        print("shape Pnt gc")


class Vec(GeoShape):
    pass


class Lin(GeoShape):
    def __init__(self, geo, renderer):
        # request blocks
        vb = renderer.vbo.cache.request_block(size=2)
        goid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        ib = renderer.ibo.cache.request_block(size=2)
        ib['idx'] = vb.indices
        super().__init__(goid, (vb, ), (ib, ))

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
        self.vrtx_block['thk'] = v
        self.__thk = v


class Plin(GeoShape):
    def __init__(self, geo, renderer):
        """

        :param vs: number of vertices coordinate that form polyline
        """
        # this will check input validity
        vb = renderer.vbo.cache.request_block(size=len(geo))
        goid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        # +1 for primitive restart value
        ib = renderer.ibo.cache.request_block(size=len(geo) + 1)
        ib['idx', :-1] = vb.indices
        ib['idx', -1] = PRV
        super().__init__(goid, (vb, ), (ib, ))

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
        self.vrtx_block['thk'] = v
        self.__thk = v


class Tgl(GeoShape):
    __is_render_edge = True

    def __init__(self, geo, renderer):
        vb = renderer.vbo.cache.request_block(size=3)
        goid = vb['oid'] = GIDP().register_entity(self).as_rgba_float()
        ib = renderer.ibo.cache.request_block(size=3)
        ib['idx'] = vb.indices
        super().__init__(goid, (vb, ), (ib, ))

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
        self.vrtx_block['fill_clr'] = v
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
        self.vrtx_block['edge_clr'] = v
        if self.__clr_edge is None:
            self.__clr_edge = v
        else:
            self.__clr_edge[:] = v

    @property
    def edge_thk(self):
        return self.__edge_thk

    @edge_thk.setter
    def edge_thk(self, v):
        self.vrtx_block['edge_thk'] = v
        self.__edge_thk = v

    def intersect(self, ray):
        raise NotImplementedError

    @classmethod
    def set_render_edge(cls, b):
        if not isinstance(b, bool):
            raise TypeError
        cls.__render_edge = b
