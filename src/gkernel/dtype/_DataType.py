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
        v = self.__class__()
        v._data = -1 * self._data
        return v

    def __truediv__(self, other):
        v = self.__class__()
        v._data = self._data / other
        return v

class VectorLikeData(MatrixLikeData):
    # def __mul__(self, other):
    #     if isinstance(other, MatrixLikeData):
    #         return np.dot(self._data.T, other._data)[0,0]
    #     elif isinstance(other, (float, int)):
    #         v = self.__class__()
    #         v._data = self._data*other
    #         return v
    #     else:
    #         raise NotImplementedError
    #
    # def __rmul__(self, other):
    #     if isinstance(other, MatrixLikeData):
    #         return self.__class__().from_row(np.dot(other._data, self._data))
    #     elif isinstance(other, (float, int)):
    #         v = self.__class__()
    #         v._data = self._data*other
    #         return v
    #     else:
    #         raise NotImplementedError
    pass
    # def tolist(self):
    #     if self._data.shape[1] == 1:
    #         self._data.
