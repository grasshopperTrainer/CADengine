import abc
from numbers import Number

import numpy as np

from gkernel.constants import ATOL


class ArrayLikeData(np.ndarray, metaclass=abc.ABCMeta):
    """
    Data is represented as a matrix
    """

    def __getitem__(self, item):
        """
        do not cast into self's type as self has strict array property

        :param item:
        :return:
        """
        return self.view(np.ndarray)[item]

    def __len__(self):
        return self.shape[1]

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

    def __hash__(self):
        """
        may be bad but leave it for now
        :return:
        """
        return hash(self.tostring())

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def validate_3d_coordinate(*vs):
        """
        check if given iterables represent 3D coordinate values

        :return:
        """
        for v in vs:
            if not (isinstance(v, (list, tuple)) and len(v) == 3 and all(isinstance(c, Number) for c in v)):
                return False
        return True

    @staticmethod
    def validate_2d_coordinate(*vs):
        """
        check if given iterables represent 2D coordinate values

        :return:
        """
        for v in vs:
            if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(c, Number) for c in v)):
                return False
        return True

    # not working
    @staticmethod
    @abc.abstractmethod
    def validate_array(cls, arr):
        """
        check if given np.array can represent the shape

        :param cls:
        :param arr:
        :return:
        """
        pass

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



    @property
    @abc.abstractmethod
    def shape_std(self):
        """
        return standard shape
        :return:
        """
        pass

    @classmethod
    @abc.abstractmethod
    def __normalize(cls):
        """
        normalize data

        :return:
        """

    @property
    def raw(self):
        """
        pretty print raw array for debugging
        :return: array elements rounded in decimal 5
        """

        def foo(x):
            if x is None:
                return
            return round(x, 5)

        return np.vectorize(foo)(self.view(np.ndarray)).__str__()
