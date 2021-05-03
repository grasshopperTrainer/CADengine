from mkernel.model.shapes.base import _MetaShape
import gkernel.dtype.geometric as gt


class Brep(_MetaShape):
    def __init__(self, geo: gt.Brep, model, renderer):
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
        shp = self.__model.add_geo_shape(pnt)
        self.__sub_shapes.setdefault(shp.__class__, set()).add(shp)
        return shp

    def add_lin(self):
        raise NotImplementedError

    def add_pgon(self):
        raise NotImplementedError

    def delete(self):
        raise
