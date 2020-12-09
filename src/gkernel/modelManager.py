from .dtype.geometric.primitive import Pnt


class ModelIterator:
    def __init__(self, shapes):
        self._shapes = shapes
        self._iter_idx = 0

    def __next__(self):
        # if self._iter_idx >= len(self._shapes):
        #     raise StopIteration
        # else:
        print('ddd')
        for s in self._shapes:
            print(s)
            yield s
            # shape = self._shapes[self._iter_idx]
            # self._iter_idx += 1
            # return shape

    def __iter__(self):
        return self


class Model:
    def __init__(self):
        self._shapes = []
        self._origin = Pnt()

    def append_shape(self, shape):
        self._shapes.append(shape)

    def iter(self):
        """
        iter all shapes in model
        :return:
        """
        for shape in self._shapes:
            if isinstance(shape, Model):    # if its a sub model iter it
                for child_shape in shape.iter():
                    yield child_shape
            else:
                yield shape

    def intersect(self, ray):
        """
        run intersection with all shapes in model
        :param ray: to intersect with
        :return:
        """



class Shape:
    def __init__(self):
        pass

    def intersect(self, ray):
        """
        shape is responsible for intersecting with ray
        :param ray: to intersect with
        :return:
        """
        raise NotImplementedError
