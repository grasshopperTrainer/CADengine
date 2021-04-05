from mkernel.shapes.base import GeoShape
from gkernel.color import *
from mkernel.global_id_provider import GIDP
import gkernel.dtype.geometric as gt
# from gkernel.dtype.geometric.brep.topology import


class Brep(GeoShape):
    def __init__(self, geo: gt.Brep, renderer, model):
        self.__model = model

        self.__geo = geo
        self.__renderer = renderer

        self.__vrtx_cache = self.__renderer.vrtx_vbo.cache
        self.__pnt_cache = self.__renderer.pnt_vbo.cache
        self.__pnt_indx_cache = self.__renderer.pnt_ibo.cache

        self.__sub_shapes = {}

    @property
    def geo(self):
        return self.__geo

    def add_vrtx(self, vrtx):
        """
        add point of given coordinate into brep

        :param vrtx:
        :return:
        """
        # type check?
        pnt = vrtx.geo
        # add point shape
        shp = self.__model.add_geo(pnt)
        self.__sub_shapes.setdefault(shp.__class__, set()).add(shp)
        return shp

    def add_lin(self):
        raise NotImplementedError

    def add_pgon(self):
        raise NotImplementedError

    def delete(self):
        raise
