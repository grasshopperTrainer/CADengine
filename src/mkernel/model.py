from gkernel.tools.intersector import Intersector as intx
import gkernel.dtype.geometric as gt
import mkernel.shapes as st
import mkernel.renderers as rend
from .global_id_provider import GIDP
import threading


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
        self.__shapes = {}
        self.__plane = gt.Pln()
        self.__renderers = {}
        self.__Lock = threading.Lock()

    @property
    def lock(self):
        """
        User of threading has to take care of locking used entity
        :return: Lock,
        """
        return self.__Lock

    @property
    def plane(self):
        return self.__plane

    def __add_geo_helper(self, geo, shape_type, renderer_type):
        """
        helper for adding geometric shapes like Point, Vector

        :param geo:
        :param shape_type:
        :param renderer_type:
        :return:
        """
        if shape_type not in self.__renderers:
            self.__renderers[shape_type] = renderer_type()
        renderer = self.__renderers[shape_type]
        shp = shape_type(geo, renderer, self)
        self.__shapes.setdefault(shape_type, set()).add(shp)
        return shp

    def __add_nongeo_helper(self, shape_type, renderer_type, args=()):
        """
        helper for nongeometric shapes like ground

        :param shape_type:
        :param renderer_type:
        :return:
        """
        if shape_type not in self.__renderers:
            self.__renderers[shape_type] = renderer_type()
        renderer = self.__renderers[shape_type]
        shp = shape_type(*args, **{'renderer': renderer, 'model': self})
        self.__shapes.setdefault(shape_type, set()).add(shp)
        return shp

    def add_geo(self, geo):
        """
        add given geometry

        :return:
        """
        if isinstance(geo, gt.Pnt):
            return self.__add_geo_helper(geo, shape_type=st.Pnt, renderer_type=rend.PointRenderer)
        elif isinstance(geo, gt.Lin):
            return self.__add_geo_helper(geo, shape_type=st.Lin, renderer_type=rend.LineRenderer)
        elif isinstance(geo, gt.Tgl):
            return self.__add_geo_helper(geo, shape_type=st.Tgl, renderer_type=rend.TriangleRenderer)
        elif isinstance(geo, gt.Pgon):
            return self.__add_geo_helper(geo, shape_type=st.Pgon, renderer_type=rend.PolygonRenderer)
        elif isinstance(geo, gt.Plin):
            return self.__add_geo_helper(geo, shape_type=st.Plin, renderer_type=rend.PolylineRenderer)
        elif isinstance(geo, gt.Brep):
            return self.__add_geo_helper(geo, shape_type=st.Brep, renderer_type=rend.BrepRenderer)
        elif isinstance(geo, gt.Pln):
            return self.__add_geo_helper(geo, shape_type=st.Pln, renderer_type=rend.PlaneRenderer)
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
        return self.__add_geo_helper(geo=gt.Pnt(x, y, z), shape_type=st.Pnt, renderer_type=rend.PointRenderer)

    def add_lin(self, start, end) -> st.Lin:
        """
        add line

        :param start: (x, y, z), vertex start
        :param end: (x, y, z), vertex end
        :return: Lin shape
        """
        return self.__add_geo_helper(geo=gt.Lin(start, end), shape_type=st.Lin, renderer_type=rend.LineRenderer)

    def add_tgl(self, v0, v1, v2) -> st.Tgl:
        """
        add triangle

        :param v0: (x, y, z), vertex 0
        :param v1: (x, y, z), vertex 1
        :param v2: (x, y, z), vertex 2
        :return:
        """
        return self.__add_geo_helper(geo=gt.Tgl(v0, v1, v2), shape_type=st.Tgl, renderer_type=rend.TriangleRenderer)

    def add_plin(self, *vs) -> st.Plin:
        """
        add polyline
        :param vs:
        :return:
        """
        return self.__add_geo_helper(geo=gt.Plin(*vs), shape_type=st.Plin, renderer_type=rend.PolylineRenderer)

    def add_pgon(self, *vs) -> st.Pgon:
        """
        add polygon

        :param vs: vertices
        :return:
        """
        return self.__add_geo_helper(geo=gt.Pgon(*vs), shape_type=st.Pgon, renderer_type=rend.PolygonRenderer)

    def add_brep(self):
        """

        :return:
        """
        return self.__add_geo_helper(geo=gt.Brep(), shape_type=st.Brep, renderer_type=rend.BrepRenderer)

    def add_pln(self, o, x, y, z):
        """

        coordinate values of:
        :param o: (x, y, z), origin
        :param x: (x, y, z), x axis
        :param y: (x, y, z), y axis
        :param z: (x, y, z), z axis
        :return:
        """
        return self.__add_geo_helper(geo=gt.Pln(o, x, y, z), shape_type=st.Pln, renderer_type=rend.PlaneRenderer)

    def add_ground(self, color):
        """

        :param color: (r, g, b, a)
        :return:
        """
        return self.__add_nongeo_helper(shape_type=st.Ground, renderer_type=rend.GroundRenderer, args=(color,))

    def add_axis(self) -> st.FlatAxis:
        return self.__add_nongeo_helper(shape_type=st.FlatAxis, renderer_type=rend.FlatAxisRenderer)

    def remove_shape(self, shape):
        """
        remove geometry from the model

        Method does nothing if geometry is not in the model.
        :param shape:
        :return:
        """
        if shape in self.__shapes.get(shape.__class__, {}):
            self.__shapes[shape.__class__].remove(shape)

    def iterator(self):
        """
        iter all shapes in model
        :return:
        """
        for shape in self.__shapes:
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

    def iter_shapes(self, typ=None):
        """
        iter all shapes
        :param typ: type, iter only given type if given
        :return:
        """
        if not typ:
            for shapes in self.__shapes.values():
                for s in shapes:
                    yield s
        else:
            for s in self.__shapes[typ]:
                yield s
