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
        self._shapes = []
        self._plane = gw.Pln()
        self.__renderers = {}

    def add_pnt(self, x, y, z):
        geo = gt.Pnt(x, y, z)
        renderer = self.__renderers.setdefault('pnt', pr.PointRenderer())
        shp = st.Pnt(geo, renderer)
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

    def test_render(self):
        gw.Tgl.render()
        gw.Lin.render()
        gw.Pnt.render()
