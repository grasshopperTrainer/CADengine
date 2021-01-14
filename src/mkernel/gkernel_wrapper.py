import os
import numpy as np

import gkernel.dtype.geometric.primitive as pg
from gkernel.color.primitive import ClrRGBA
import mkernel.shape as shp
import ckernel.render_context.opengl_context.ogl_factories as ogl
import ckernel.render_context.opengl_context.opengl_hooker as gl


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
    # below is creation of entities for rendering
    # path of shaders relative to current dir
    __vrtx_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_vrtx_shdr.glsl')
    __frgm_shdr_path = os.path.join(os.path.dirname(__file__), 'tgl_frgm_shdr.glsl')

    # use same dtype to push data cpu -> gpu
    __dtype = [('vtx', 'f4', 4), ('clr', 'f4', 4)]
    __vrtx_bffr = ogl.OGLArryBffrFactory(attr_desc=__dtype, is_descriptor=True)
    __arry_bffr = ogl.CPUBffrFactory(dtype=__dtype, is_descriptor=False).get_entity()
    # create vao and program
    __vao = ogl.OGLVrtxArryFactory(__vrtx_bffr, is_descriptor=True)
    __gpu_prgrm = ogl.OGLPrgrmFactory(vrtx_path=__vrtx_shdr_path, frgm_path=__frgm_shdr_path, is_descriptor=True)
    # use dtype for uniform array
    __dtype = [('MM', 'f4', (4, 4)), ('VM', 'f4', (4, 4)), ('PM', 'f4', (4, 4))]
    __ufrm_bffr = ogl.CPUBffrFactory(dtype=__dtype, is_descriptor=False).get_entity()
    __ufrm_pshr = ogl.OGLUniformPusherFactory(dtype=__dtype, prgrm_fct=__gpu_prgrm, is_descriptor=False).get_entity()

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
        self.__block = self.__arry_bffr.request_block_vacant(3)
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

    def intersect(self, ray):
        raise NotImplementedError

    @classmethod
    def render_all(cls):
        """
        render all triangles

        :return:
        """
        cls.__vrtx_bffr.push_all(cls.__arry_bffr)
        cls.__vao.bind()
        cls.__gpu_prgrm.bind()
        # need uniform pusher...
        # need camera stack and view stack?...

        gl.glDrawArrays(gl.GL_TRIANGLES,
                        0,
                        cls.__arry_bffr.num_vertex_inuse)
