import abc

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
        return super().__str__()

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
        if np.isclose(self, other, atol=ATOL).all():
            return True
        return False
