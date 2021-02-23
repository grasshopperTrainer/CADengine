from gkernel.tools.intersector import Intersector as intx
import mkernel.shapes.primitive_wrapper as gw
import gkernel.dtype.geometric as gt
import mkernel.shapes as st
import mkernel.renderers as rend
from .color_registry import GlobalColorRegistry


class ModelIterator:
    def __init__(self, shapes):
        self._shapes = shapes
        self._iter_idx = 0

    def __next__(self):
        for s in self._shapes:
            yield s

    def __iter__(self):
        return self


class Model:
    def __init__(self):
        self._shapes = {}
        self._plane = gw.Pln()
        self.__renderers = {}

    def __add_geo_helper(self, geo, geo_wrapper, renderer_type):
        if geo_wrapper not in self.__renderers:
            self.__renderers[geo_wrapper] = renderer_type()
        renderer = self.__renderers[geo_wrapper]
        shp = geo_wrapper(geo, renderer)
        self._shapes.setdefault(geo_wrapper, []).append(shp)
        return shp

    def add_geo(self, geo):
        """
        add given geometry

        :return:
        """
        if isinstance(geo, gt.Pnt):
            return self.__add_geo_helper(geo, geo_wrapper=st.Pnt, renderer_type=rend.PointRenderer)
        elif isinstance(geo, gt.Lin):
            return self.__add_geo_helper(geo, geo_wrapper=st.Lin, renderer_type=rend.LineRenderer)
        elif isinstance(geo, gt.Tgl):
            return self.__add_geo_helper(geo, geo_wrapper=st.Tgl, renderer_type=rend.TriangleRenderer)
        elif isinstance(geo, gt.Pgon):
            return self.__add_geo_helper(geo, geo_wrapper=st.Pgon, renderer_type=rend.PolygonRenderer)
        elif isinstance(geo, gt.Plin):
            return self.__add_geo_helper(geo, geo_wrapper=st.Plin, renderer_type=rend.PolylineRenderer)
        elif isinstance(geo, gt.Brep):
            return self.__add_geo_helper(geo, geo_wrapper=st.Brep, renderer_type=rend.BrepRenderer)
        else:
            raise NotImplementedError

    def add_pnt(self, x, y, z) -> st.Pnt:
        """
        add point

        :param x: Number, coordinate x
        :param y: Number, coordinate y
        :param z: Number, coordinate z
        :return: Pnt shape
        """
        return self.__add_geo_helper(geo=gt.Pnt(x, y, z), geo_wrapper=st.Pnt, renderer_type=rend.PointRenderer)

    def add_lin(self, vs, ve) -> st.Lin:
        """
        add line

        :param vs: (x, y, z), vertex start
        :param ve: (x, y, z), vertex end
        :return: Lin shape
        """
        return self.__add_geo_helper(geo=gt.Lin(vs, ve), geo_wrapper=st.Lin, renderer_type=rend.LineRenderer)

    def add_tgl(self, v0, v1, v2) -> st.Tgl:
        """
        add triangle

        :param v0: (x, y, z), vertex 0
        :param v1: (x, y, z), vertex 1
        :param v2: (x, y, z), vertex 2
        :return:
        """
        return self.__add_geo_helper(geo=gt.Tgl(v0, v1, v2), geo_wrapper=st.Tgl, renderer_type=rend.TriangleRenderer)

    def add_plin(self, *vs) -> st.Plin:
        """
        add polyline
        :param vs:
        :return:
        """
        return self.__add_geo_helper(geo=gt.Plin(*vs), geo_wrapper=st.Plin, renderer_type=rend.PolylineRenderer)

    def add_pgon(self, *vs) -> st.Pgon:
        """
        add polygon

        :param vs: vertices
        :return:
        """
        return self.__add_geo_helper(geo=gt.Pgon(*vs), geo_wrapper=st.Pgon, renderer_type=rend.PolygonRenderer)

    def add_brep(self):
        """

        :return:
        """
        return self.__add_geo_helper(geo=gt.Brep(), geo_wrapper=st.Brep, renderer_type=rend.BrepRenderer)

    def iterator(self):
        """
        iter all shapes in model
        :return:
        """
        for shape in self._shapes:
            if isinstance(shape, Model):  # if its a sub model iter it
                for child_shape in shape.iterator():
                    yield child_shape
            else:
                yield shape

    def intersect(self, ray):
        """
        run intersection with all shapes in model
        :param ray: to intersect with
        :return:
        """
        for i, shape in enumerate(self.iterator()):
            x = intx.intx(shape, ray)
            if x is not None:
                print(i, x)

    def render(self):
        for r in self.__renderers.values():
            r.render()

