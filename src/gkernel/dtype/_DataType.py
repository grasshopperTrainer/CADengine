import numpy as np
from numbers import Number


class DataType:
    """
    Inharitable describing data type
    """
    def __init__(self, data):
        self._data = data

    @classmethod
    def from_row(cls, raw_data):
        """
        Return new instance of raw_data

        ! User has full responsibility providing correct raw data
        :param raw_data:
        :return:
        """
        ins = cls()
        ins._data = raw_data.copy()

        return ins


class MatrixLikeData(DataType):
    """
    Data is represented as a matrix
    """

    @property
    def shape(self):
        return self._data.shape

    def __neg__(self):
        """
        negate matrix
        :return:
        """
        ins = self.__class__()
        ins._data = -1 * self._data
        return ins

    def __truediv__(self, other):
        v = self.__class__()
        v._data = self._data / other
        print(self, other, v)
        return v
