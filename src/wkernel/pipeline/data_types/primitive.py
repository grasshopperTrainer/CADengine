from numbers import Number
import numpy as np
from collections import namedtuple
from .mess_toolbox import np_gl_type_convert


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


class NamedData:
    """
    Numpy array value to be used pushed into buffer and used as vertex attribute
    """
    def __init__(self, data):
        if not isinstance(data, np.ndarray):
            raise TypeError

        self._data = data

    @property
    def properties(self):
        nt = namedtuple('named_data', ('name', 'size', 'type', 'stride', 'offset', 'sub_data'))
        nts = []
        stride = self._data.itemsize

        for k, v in self._data.dtype.fields.items():
            dtype, offset = v
            if dtype == 'object':
                sample = self._data[k][0]
                dtype = sample.dtype
                size = sample.size
            else:
                dtype, size = dtype.subdtype
                size = size[0]

            dtype = np_gl_type_convert(dtype)             # convert into OpenGL type
            offset = None if offset == 0 else offset
            sub_data = self._data[k]
            nts.append(nt(k, size, dtype, stride, offset, sub_data))

        return nts

    @property
    def data(self):
        return self._data

    @property
    def bytesize(self):
        return self._data.size * self._data.itemsize

    @property
    def shape(self):
        return self._data.shape
