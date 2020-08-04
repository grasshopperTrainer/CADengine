import numpy as np


class GeomDataType:
    @classmethod
    def new_from_raw(cls, value):
        ins = cls()
        ins._data = value
        return ins
