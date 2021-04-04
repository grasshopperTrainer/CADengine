from mkernel.shapes.base import Shape
from gkernel.color import *
from mkernel.global_id_provider import GIDP


class Brep(Shape):
    def __init__(self, geo, renderer, model):
        self.__model = model

        self.__geo = geo
        self.__renderer = renderer

        self.__vrtx_cache = self.__renderer.vrtx_vbo.cache
        self.__pnt_cache = self.__renderer.pnt_vbo.cache
        self.__pnt_indx_cache = self.__renderer.pnt_ibo.cache

        # self.__crv_cache = BffrCache(dtype=np.dtype([('clr', 'f4', 4), ('thk', 'f4')]), locs=(0, 1), size=16)
        # self.__srf_cache =
        self.__points = set()

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
        vrtx = self.__geo.addget_vrtx(x, y, z)
        vrtx_block = self.__vrtx_cache.request_block(size=1)
        point_vrtx_block = self.__pnt_cache.request_block(size=1)
        point_indx_block = self.__pnt_indx_cache.request_block(size=1)

        point = PointRenderEntity(vrtx, vrtx_block, point_vrtx_block, point_indx_block)
        GIDP().register_entity(point)
        self.__points.add(point)
        return vrtx

    def add_lin(self):
        raise NotImplementedError

    def add_pgon(self):
        raise NotImplementedError

    def delete(self):
        raise


class RenderEntity:
    pass


class PointRenderEntity(RenderEntity):
    def __init__(self, vrtx, coord_block, vrtx_block, indx_block):
        """
        gonna render given vertex

        :param vrtx:
        """
        self.__vrtx = vrtx
        self.__coord_block = coord_block
        self.__vrtx_block = vrtx_block
        self.__indx_block = indx_block

        self.__coord_block['coord'] = vrtx.point.T
        self.__vrtx_block['clr'] = ClrRGBA(1, 1, 1, 1)
        self.__vrtx_block['dia'] = 10
        self.__indx_block['idx'] = self.__coord_block.indices
