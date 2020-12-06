import numpy as np
from numbers import Number


class DataType:
    """
    Inharitable describing data type
    """
    def __init__(self, data):
        self._data = data

    @classmethod
    def new_from_raw(cls, raw_data):
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
        v = self.__class__()
        v._data = -1 * self._data
        return v

    def __truediv__(self, other):
        v = self.__class__()
        v._data = self._data / other
        return v
    #
    # def __mul__(self, other):
    #     if isinstance(other, Number):
    #         return self._data*np

    # def __sub__(self, other):
    #     raw = self._data - other._data
    #     return self.new_from_raw(raw)


class ColumnVectorLikeData(MatrixLikeData):
    def __mul__(self, other):
        if isinstance(other, MatrixLikeData):
            return np.dot(self._data.T, other._data)[0,0]
        elif isinstance(other, (float, int)):
            v = self.__class__()
            v._data = self._data*other
            return v
        else:
            raise NotImplementedError

    def __rmul__(self, other):
        if isinstance(other, MatrixLikeData):
            return self.__class__().new_from_raw(np.dot(other._data, self._data))
        elif isinstance(other, (float, int)):
            v = self.__class__()
            v._data = self._data*other
            return v
        else:
            raise NotImplementedError

    # def tolist(self):
    #     if self._data.shape[1] == 1:
    #         self._data.
