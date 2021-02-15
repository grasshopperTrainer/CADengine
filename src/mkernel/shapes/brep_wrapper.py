import numpy as np
from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from mkernel.shapes.base import Shape
import gkernel.dtype.geometric as gt
from mkernel.renderers.brep_renderer import BrepRenderer


class Brep(Shape):
    def __init__(self, geo, renderer):
        self.__geo = geo
        self.__renderer = renderer

        self.__vrtx_cache = self.__renderer.vrtx_vbo.cache
        self.__pnt_cache = self.__renderer.pnt_vbo.cache
        self.__pnt_indx_cache = self.__renderer.pnt_ibo.cache

        # self.__crv_cache = BffrCache(dtype=np.dtype([('clr', 'f4', 4), ('thk', 'f4')]), locs=(0, 1), size=16)
        # self.__srf_cache =
        self.__vrtx_blocks = {}

    @property
    def geo(self):
        return self.__geo

    def add_vrtx(self, x, y, z):
        """
        add point of given coordinate into brep

        1. adds point into brep
        2. bind point with block
        :param x:
        :param y:
        :param z:
        :return:
        """
        v, p = self.__geo.addget_vrtx(x, y, z)
        block = self.__vrtx_cache.request_block(size=1)
        block['coord'] = p.T
        bb = self.__pnt_cache.request_block(size=1)
        bb['dia'] = 5
        bb['clr'] = 1, 1, 1, 1
        bbb = self.__pnt_indx_cache.request_block(size=1)
        bbb['idx'] = block.indices
        self.__vrtx_blocks[v] = block
        return v

    def add_lin(self):
        raise NotImplementedError

    def add_pgon(self):
        raise NotImplementedError

class RenderEntity:
    pass


class PointRenderEntity(RenderEntity):
    def __init__(self, vrtx):
        pass
