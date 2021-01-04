from gkernel.dtype.geometric.primitive import Pln
from gkernel.tools.intersector import Intersector as intx

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
        self._plane = Pln()

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
        for shape in self.iterator():
            print(intx.intx(shape, ray))

    def render(self):
        """
        redner all shaped inside model

        :return:
        """
