import numpy as np
from collections import namedtuple
import OpenGL.GL as opengl


class BufferObject:
    """
    Object holding OpenGL object id and other properties of bound data

    To store buffer properties such as size, stride of data.
    Handles deletion of OpenGL object.
    """

    @property
    def id(self):
        return self._id
    @property
    def kind(self):
        return self._kind

class VertexBufferObject(BufferObject):
    _kind = opengl.GL_ARRAY_BUFFER

    def __init__(self, id):
        self._id = id


class VertexArrayObject:
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id


class VertexAttribObject:
    """
    Numpy array value to be used pushed into buffer and used as vertex attribute
    """
    def __init__(self, value):
        if not isinstance(value, np.ndarray):
            raise TypeError

        self._value = value

    @property
    def bytesize(self):
        return self._value.size * self._value.itemsize

    @property
    def properties(self):
        nt = namedtuple('vao_properties', ('name', 'size', 'type', 'stride', 'offset'))
        nts = []
        stride = self._value.itemsize
        for k, v in self._value.dtype.fields.items():
            dtype, offset = v
            subdtype, size = dtype.subdtype
            size = size[0]
            nts.append(nt(k, size, subdtype, stride, offset))
        return nts

    @property
    def value(self):
        return self._value