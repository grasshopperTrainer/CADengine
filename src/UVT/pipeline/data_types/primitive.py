from numbers import Number
import numpy as np


class PrimitiveDataType:
    pass


class Bound(PrimitiveDataType):

    def __init__(self, start=0, end=1):
        if not (isinstance(start, Number) and isinstance(end, Number)):
            raise TypeError
        self._start, self._end = start, end

    # def __len__(self):
    #     return self._end - self._start

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def len(self):
        return self._end - self._start


class Vector:

    def __init__(self, array: np.ndarray):
        if not isinstance(array, np.ndarray):
            raise TypeError
        self._data = array

    @property
    def bytesize(self):
        if self._data is None:
            return 0
        return self._data.itemsize * self._data.size

    @property
    def itemsize(self):
        return self._data.itemsize

    @property
    def size(self):
        return self._data.size

    @property
    def data(self):
        return self._data


class FloatVector(Vector):
    _dtype = 'f'
