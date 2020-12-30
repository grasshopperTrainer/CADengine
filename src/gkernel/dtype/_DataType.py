import numpy as np

# what is good min val?
ATOL = 1e-6

class ArrayLikeData(np.ndarray):
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

    @property
    def arr(self):
        return super().__str__()

    def __getitem__(self, item):
        return self.view(np.ndarray)[item]

    def __eq__(self, other):
        """
        logical equation

        :param other: other vector
        :return: bool
        """
        if not isinstance(other, self.__class__):
            return False
        elif np.isclose(self, other, atol=ATOL).all():
            return True
        else:
            return False
