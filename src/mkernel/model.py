from gkernel.tools.intersector import Intersector as intx
import mkernel.gkernel_wrapper as gw
import gkernel.dtype.geometric as gt
import mkernel.gkernel_wrapper as st
import mkernel.primitive_renderer as pr

from .shape import Shape


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

    def add_geo(self, geo):
        """
        add given geometry

        :return:
        """
        if isinstance(geo, gt.Pnt):
            renderer = self.__renderers.setdefault('pnt', pr.PointRenderer())
            shp = st.Pnt(geo, renderer)
            self._shapes.setdefault(gt.Pnt, []).append(shp)
            return shp
        elif isinstance(geo, gt.Lin):
            pass
        elif isinstance(geo, gt.Tgl):
            pass
        else:
            raise NotImplementedError

    def add_pnt(self, x, y, z):
        """
        add point

        :param x: Number, coordinate x
        :param y: Number, coordinate y
        :param z: Number, coordinate z
        :return: Pnt shape
        """
        geo = gt.Pnt(x, y, z)
        renderer = self.__renderers.setdefault('pnt', pr.PointRenderer())
        shp = st.Pnt(geo, renderer)
        self._shapes.setdefault(gt.Pnt, []).append(shp)
        return shp

    def add_lin(self, vs, ve):
        """
        add line

        :param vs: (x, y, z), vertex start
        :param ve: (x, y, z), vertex end
        :return: Lin shape
        """
        geo = gt.Lin(vs, ve)
        renderer = self.__renderers.setdefault('lin', pr.LineRenderer())
        shp = st.Lin(geo, renderer)
        self._shapes.setdefault(gt.Lin, []).append(shp)
        return shp

    def add_tgl(self, v0, v1, v2):
        """
        add triangle

        :param v0: (x, y, z), vertex 0
        :param v1: (x, y, z), vertex 1
        :param v2: (x, y, z), vertex 2
        :return:
        """
        geo = gt.Tgl(v0, v1, v2)
        renderer = self.__renderers.setdefault('tgl', pr.TriangleRenderer())
        shp = st.Tgl(geo, renderer)
        self._shapes.setdefault(gt.Tgl, []).append(shp)
        return shp

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

