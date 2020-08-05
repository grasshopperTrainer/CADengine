from .._DataType import *


class GeomDataType(DataType):

    @classmethod
    def new_from_raw(cls, value):
        ins = cls()
        ins._data = value
        return ins
