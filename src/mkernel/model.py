from gkernel.tools.intersector import Intersector as intx
import mkernel.gkernel_wrapper as gw
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

    def append_shape(self, shape):
        self._shapes.append(shape)

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
        """
        redner all shaped inside model

        call all renderer defined in shaped inside gkernel_wrapper
        :return:
        """
        for k, v in gw.__dict__.items():
            if isinstance(v, type) and issubclass(v, Shape):    # find shape class
                v.get_cls_renderer().run()

    def test_render(self):
        gw.Tgl.get_cls_renderer().render()