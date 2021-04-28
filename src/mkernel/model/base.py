from gkernel.tools.intersector import Intersector as intx
import gkernel.dtype.geometric as gt
import mkernel.shapes as st
import mkernel.renderers as rend
from mkernel.global_id_provider import GIDP
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
        User of threading has to take care of locking by himself
        :return: Lock,
        """
        return self.__Lock

    @property
    def plane(self):
        return self.__plane

    def add_shape(self, args, shape_type, renderer_type):
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
        shp = shape_type(*args, renderer)
        self.__shapes.setdefault(shape_type, set()).add(shp)
        return shp

    def remove_shape(self, shape):
        """
        remove geometry from the model

        Method does nothing if geometry is not in the model.
        :param shape:
        :return:
        """
        if shape in self.__shapes.get(shape.__class__, {}):
            self.__shapes[shape.__class__].remove(shape)
            shape.delete()

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

    def render(self):
        for r in self.__renderers.values():
            r.render()
