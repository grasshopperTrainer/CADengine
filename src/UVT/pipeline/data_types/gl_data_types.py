import numpy as np
from collections import namedtuple
import OpenGL.GL as opengl
from ..components.mess_toolbox import np_gl_type_convert

class BufferObject:
    """
    Object holding OpenGL object id and other properties of bound data

    To store buffer properties such as size, stride of data.
    Handles deletion of OpenGL object.
    """

    def __init__(self, id, kind):
        self._id = id
        self._kind = kind

    @property
    def id(self):
        return self._id
    @property
    def kind(self):
        return self._kind


class VertexBufferObject(BufferObject):
    def __init__(self, id):
        super().__init__(id, opengl.GL_ARRAY_BUFFER)

class IndexBufferObject(BufferObject):
    def __init__(self, id):
        super().__init__(id, opengl.GL_ELEMENT_ARRAY_BUFFER)


class VertexArrayObject:
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id


class NamedData:
    """
    Numpy array value to be used pushed into buffer and used as vertex attribute
    """
    def __init__(self, data):
        if not isinstance(data, np.ndarray):
            raise TypeError

        self._data = data

    @property
    def bytesize(self):
        return self._data.size * self._data.itemsize

    @property
    def properties(self):
        nt = namedtuple('named_data', ('name', 'size', 'type', 'stride', 'offset'))
        nts = []
        stride = self._data.itemsize
        for k, v in self._data.dtype.fields.items():
            dtype, offset = v
            dtype, size = dtype.subdtype
            dtype = np_gl_type_convert(dtype)             # convert into OpenGL type
            size = size[0]
            offset = None if offset == 0 else offset
            nts.append(nt(k, size, dtype, stride, offset))
        return nts

    @property
    def data(self):
        return self._data


class DataBufferObject(VertexBufferObject, NamedData):
    """
    Buffer storing vertex attribute data
    """
    def __init__(self, bffr, attr):
        if hasattr(bffr, 'isinstance') and hasattr(attr, 'isinstance'):
            if not (bffr.isinstance(BufferObject) and attr.isinstance(NamedData)):
                raise TypeError
        else:
            if not (isinstance(bffr, BufferObject) and isinstance(attr, NamedData)):
                raise TypeError

        self._bffr = bffr
        self._attr = attr

        self._id = self._bffr.id
        self._kind = self._bffr.kind
        self._data = self._attr.data
