import abc
from numbers import Number

import numpy as np

from gkernel.constants import ATOL


class ArrayLikeData(np.ndarray, metaclass=abc.ABCMeta):
    """
    Data is represented as a matrix
    """

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

    # not working
    @classmethod
    @abc.abstractmethod
    def is_array_like(cls, arr):
        pass

    @property
    def arr(self):
        """
        pretty print raw array for debugging
        :return: array elements rounded in decimal 5
        """

        def foo(x):
            if x is None:
                return
            return round(x, 5)

        return np.vectorize(foo)(self.view(np.ndarray)).__str__()

    def __getitem__(self, item):
        """
        do not cast into self's type as self has strict array property

        :param item:
        :return:
        """
        return self.view(np.ndarray)[item]

    def __eq__(self, other):
        """
        logical equation within absolute tolerance

        :param other: of ArrayLikeData
        :return: bool
        """
        if isinstance(other, Number):
            return (np.isclose(self[:3].view(np.ndarray), other, atol=ATOL)).all()
        elif isinstance(other, np.ndarray):
            if self.shape != other.shape:
                return False
            return np.isclose(self.view(np.ndarray), other.view(np.ndarray), atol=ATOL).all()
        else:
            raise TypeError
