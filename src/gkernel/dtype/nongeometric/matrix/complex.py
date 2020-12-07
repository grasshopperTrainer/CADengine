from .basic import Mat4
import numpy as np


class TrnsfMat(Mat4):
    """
    Transformation matrix
    """

    @property
    def I(self):
        raise NotImplementedError('inverse not defined')


class CompoundTrnsfMat(TrnsfMat):
    """
    Ordered transformation matrices

    Useful retrieving intermediate transformation matrix
    of getting inverse of all transformation.
    """
    type_nickname = 'CM'

    def __init__(self, matrices=[]):
        self._matrices = matrices

    def append(self, matrix):
        """
        Append matrix for compound transformation
        :param matrix: matrix used to translate
        :return:
        """
        self._matrices.append(matrix)

    def append_all(self, *matrices):
        """
        Append matrices with given order
        :param matrices: matrices for transformation
        :return:
        """
        self._matrices += list(matrices)

    @property
    def M(self):
        m = EyeMat4()
        for mat in self._matrices:
            m = mat * m
        return m

    @property
    def I(self):
        """
        Inverse of all transformation matrix
        :return:
        """
        return CompoundTrnsfMat([m.I for m in reversed(self._matrices)])

    def copy(self):
        return CompoundTrnsfMat(self._matrices.copy())

    def __str__(self):
        return f"<Matrices of: {[m.type_nickname for m in self._matrices]}>"


class MoveMat(TrnsfMat):
    """
    Translation matrix (move)
    """
    type_nickname = 'M'

    def __init__(self, x=0, y=0, z=0):
        mat = np.eye(4)
        mat[:3, 3] = x, y, z
        super().__init__(mat)

    @property
    def x(self):
        return self._data[0, 3]

    @property
    def y(self):
        return self._data[1, 3]

    @property
    def z(self):
        return self._data[2, 3]

    @property
    def I(self):
        return MoveMat(-self.x, -self.y, -self.z)


class ScaleMat(TrnsfMat):
    """
    Scale matrix
    """
    type_nickname = 'S'

    def __init__(self, x=1, y=1, z=1):
        mat = np.array([[x, 0, 0, 0],
                        [0, y, 0, 0],
                        [0, 0, z, 0],
                        [0, 0, 0, 1]])
        super().__init__(mat)

    @property
    def x(self):
        return self._data[0, 0]

    @property
    def y(self):
        return self._data[1, 1]

    @property
    def z(self):
        return self._data[2, 2]

    @property
    def I(self):
        return ScaleMat(1 / self.x, 1 / self.y, 1 / self.z)


class RotXMat(TrnsfMat):
    """
    Rotate x matrix
    """
    type_nickname = 'RX'

    def __init__(self, angle=0):
        mat = np.array([[1, 0, 0, 0],
                        [0, np.cos(angle), np.sin(angle), 0],
                        [0, np.sin(angle), np.cos(angle), 0],
                        [0, 0, 0, 1]])
        super().__init__(mat)
        self._angle = angle

    @property
    def I(self):
        return RotXMat(-self._angle)


class RotYMat(TrnsfMat):
    """
    Rotate y matrix
    """
    type_nickname = 'RY'

    def __init__(self, angle=np.pi / 2):
        mat = np.array([[np.cos(angle), 0, np.sin(angle), 0],
                        [0, 1, 0, 0],
                        [np.sin(angle), 0, np.cos(angle), 0],
                        [0, 0, 0, 1]])
        super().__init__(mat)
        self._angle = angle

    @property
    def I(self):
        return RotXMat(-self._angle)


class RotZMat(TrnsfMat):
    """
    Rotate z matrix
    """
    type_nickname = 'RZ'

    def __init__(self, angle=np.pi / 2):
        mat = np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                        [np.sin(angle), np.cos(angle), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])
        super().__init__(mat)
        self._angle = angle

    @property
    def I(self):
        return RotXMat(-self._angle)


class EyeMat4(Mat4):
    """
    4x4 Identity matrix
    """
    type_nickname = 'E'

    def __init__(self):
        mat = np.eye(4)
        super().__init__(mat)

    @property
    def I(self):
        return EyeMat4()
