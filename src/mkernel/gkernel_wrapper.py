import gkernel.dtype.geometric.primitive as pg
from gkernel.dtype.nongeometric.matrix.primitive import MoveMat
from gkernel.color.primitive import Clr, ClrRGBA

import mkernel.shape as shp
import ckernel.render_context.opengl_context.buffer_syncer as bs
import ckernel.render_context.opengl_context.entity_template as ogl
# from .linear_buffer import LinearBuffer
from ckernel.tools.compound_array import CompoundArray
import os
import numpy as np


class Ray(pg.Ray, shp.Shape):

    @classmethod
    def get_cls_renderer(cls):
        return None


class Pnt(pg.Pnt, shp.Shape):
    pass


class Vec(pg.Vec, shp.Shape):
    pass


class Lin(pg.Lin, shp.Shape):
    pass


class Pln(pg.Pln, shp.Shape):
    pass


class Tgl(shp.Shape):
    # path of shaders relative to current dir
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_frgm_shdr.glsl')

    # program... but program is per meta context, so this has to happen per context
    __master_array = CompoundArray([('vtx', 'f4', 4), ('clr', 'f4', 4)])
    __buffer = ogl.OGLArryBffrTemp()
    __prgrm = ogl.OGLPrgrmTemp(vrtx_path=__vrtx_shdr_path, frgm_path=__frgm_shdr_path)
    __renderer = shp.ShapeRenderer(__buffer, __prgrm)

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
        self.__block = self.__master_array.request_block_vacant(3)
        self.__geo = pg.Tgl()
        self.__clr_fill = ClrRGBA()
        self.__clr_stroke = None

        self.geo = pg.Tgl(v0, v1, v2)
        self.clr_fill = ClrRGBA(1, 1, 1)

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
        self.__block['clr'][..., :len(v)] = v
        self.__clr_fill[:len(v)] = v

    @property
    def clr_stroke(self):
        raise NotImplementedError

    @classmethod
    def get_cls_renderer(cls):
        return cls.__renderer

    def intersect(self, ray):
        raise NotImplementedError