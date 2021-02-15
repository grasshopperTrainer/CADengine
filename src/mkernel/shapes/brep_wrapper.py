import random
import weakref as wr

import numpy as np
from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from mkernel.shapes.base import Shape
import gkernel.dtype.geometric as gt
from mkernel.renderers.brep_renderer import BrepRenderer
from gkernel.color import *


class Brep(Shape):
    def __init__(self, geo, renderer):
        self.__geo = geo
        self.__renderer = renderer

        self.__vrtx_cache = self.__renderer.vrtx_vbo.cache
        self.__pnt_cache = self.__renderer.pnt_vbo.cache
        self.__pnt_indx_cache = self.__renderer.pnt_ibo.cache

        # self.__crv_cache = BffrCache(dtype=np.dtype([('clr', 'f4', 4), ('thk', 'f4')]), locs=(0, 1), size=16)
        # self.__srf_cache =
        self.__points = set()

        self.__entity_registry = EntityRegistry()

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
        self.__entity_registry.getset_entity_cid(point)
        self.__points.add(point)
        return vrtx

    def add_lin(self):
        raise NotImplementedError

    def add_pgon(self):
        raise NotImplementedError


class EntityRegistry:

    def __init__(self):
        self.__record = wr.WeakKeyDictionary()

        self.__color_comp_bitsize = 8
        self.__color_comp_bitmask = [0 for i in range(3)]

    def getset_entity_cid(self, entity):
        """
        get, set color id for the entity

        :param entity:
        :return:
        """
        if entity in self.__record:
            return self.__record[entity]
        else:
            while True:
                color_comps = tuple(random.getrandbits(self.__color_comp_bitsize) for _ in range(3))
                # check for reserved 0
                if any([cc == 0 for cc in color_comps]):
                    continue

                masked_count = 0
                for bm, cc in zip(self.__color_comp_bitmask, color_comps):
                    if bm & (1 << cc):
                        masked_count += 1
                # color is already occupied
                if masked_count == 3:
                    continue
                else:   # mask
                    for i in range(3):
                        self.__color_comp_bitmask[i] |= color_comps[i]
                    break
            self.__record[entity] = color_comps
            return color_comps

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
