import numpy as np
from collections import namedtuple
import OpenGL.GL as opengl
from .primitive import NamedData


class OpenglObject:
    """
    Something that has id.
    """
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

class BufferObject(OpenglObject):
    """
    Object holding OpenGL object id and other properties of bound data

    To store buffer properties such as size, stride of data.
    Handles deletion of OpenGL object.
    """
    def __init__(self, id, kind):
        super().__init__(id)
        self._kind = kind

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


class PrgrmObj(OpenglObject):
    pass


class ShdrObj(OpenglObject):
    _kind = None
    def __init__(self, id):
        super().__init__(id)

    @property
    def kind(self):
        return self._kind

class VrtxShdrObj(ShdrObj):
    pass

class FrgmtShdrObj(ShdrObj):
    pass


class DataBufferObject(VertexBufferObject, NamedData):
    """
    Buffer storing vertex attribute data
    """
    def __init__(self, bffr, name_data):
        if hasattr(bffr, 'isinstance') and hasattr(name_data, 'isinstance'):
            if not (bffr.isinstance(BufferObject) and name_data.isinstance(NamedData)):
                raise TypeError
        else:
            if not (isinstance(bffr, BufferObject) and isinstance(name_data, NamedData)):
                raise TypeError

        self._bffr = bffr
        self._data = name_data

    @property
    def bffr(self):
        return self._bffr

    @property
    def data(self):
        return self._data
