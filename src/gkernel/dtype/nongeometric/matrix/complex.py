from .basic import Mat4
import numpy as np
from numbers import Number


class TrnsfMat(Mat4):
    """
    Transformation matrix
    """

    @property
    def I(self):
        raise NotImplementedError('inverse not defined')

    @property
    def str(self):
        return super().__str__()

    def __mul__(self, other):
        """
        dot transformation matrices

        multiplying transformation matrices will produce anonymous tranf matrix
        while multiplying with vector like data will produce its new instance

        :param other:
        :return:
        """
        # combine transformation matrix
        if isinstance(other, TrnsfMat):
            return self.dot(other).view(TrnsfMat)
        else:
            # try calculating
            try:
                arr = self.dot(other)
            except Exception as e:
                raise ArithmeticError("cant multiply")
            # try casting result into class on the right
            if arr.shape == other.shape:
                try:
                    return arr.view(other.__class__)
                except:
                    raise Exception(f"result is not like {other.__class__.__name__}")
            else:
                raise TypeError


# class UnknownTrnsfMat(TrnsfMat):
#     """
#     transformation matrix that is not well defined
#     """
#
#     def __init__(self,
#                  a0=1, a1=0, a2=0, a3=0,
#                  b0=0, b1=1, b2=0, b3=0,
#                  c0=0, c1=0, c2=1, c3=0,
#                  d0=0, d1=0, d2=0, d3=1):
#         if any(not isinstance(v, Number) for v in [a0, a1, a2, a3,
#                                                    b0, b1, b2, b3,
#                                                    c0, c1, c2, c3,
#                                                    d0, d1, d2, d3]):
#             raise TypeError
#
#         arr = np.array([[a0, a1, a2, a3],
#                         [b0, b1, b2, b3],
#                         [c0, c1, c2, c3],
#                         [d0, d1, d2, d3]])
#         super().__init__(arr)


class StackedMat(TrnsfMat):
    """
    Ordered transformation matrices

    Useful retrieving intermediate transformation matrix
    of getting inverse of all transformation.
    """
    type_nickname = 'CM'

    def __new__(cls, matrices=[]):
        obj = np.eye(4).view(cls)
        obj._matrices = []
        return obj

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
        return StackedMat([m.I for m in reversed(self._matrices)])

    def copy(self):
        return StackedMat(self._matrices.copy())

    def __str__(self):
        return f"<Matrices of: {[m.type_nickname for m in self._matrices]}>"


class MoveMat(TrnsfMat):
    """
    Translation matrix (move)
    """
    type_nickname = 'M'

    def __new__(cls, x=0, y=0, z=0):
        return np.array([[1, 0, 0, x],
                         [0, 1, 0, y],
                         [0, 0, 1, z],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def x(self):
        return self[0, 3]

    @property
    def y(self):
        return self[1, 3]

    @property
    def z(self):
        return self[2, 3]

    @property
    def I(self):
        return MoveMat(-self.x, -self.y, -self.z)

    def __str__(self):
        return f"<MoveMat {self.x, self.y, self.z}>"

    # def __array_finalize__(self, obj):
    #     if obj is None: return obj


class ScaleMat(TrnsfMat):
    """
    Scale matrix
    """
    type_nickname = 'S'

    def __new__(cls, x=1, y=1, z=1):
        return np.array([[x, 0, 0, 0],
                         [0, y, 0, 0],
                         [0, 0, z, 0],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def x(self):
        return self[0, 0]

    @property
    def y(self):
        return self[1, 1]

    @property
    def z(self):
        return self[2, 2]

    @property
    def I(self):
        return ScaleMat(1 / self.x, 1 / self.y, 1 / self.z)

    def __str__(self):
        return f"<ScaleMat {self.x, self.y, self.z}>"


class RotXMat(TrnsfMat):
    """
    Rotate x matrix
    """
    type_nickname = 'RX'

    def __new__(cls, angle=0):
        return np.array([[1, 0, 0, 0],
                         [0, np.cos(angle), np.sin(angle), 0],
                         [0, np.sin(angle), np.cos(angle), 0],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def I(self):
        return RotXMat(-self._angle)


class RotYMat(TrnsfMat):
    """
    Rotate y matrix
    """
    type_nickname = 'RY'

    def __new__(cls, angle=np.pi / 2):
        return np.array([[np.cos(angle), 0, np.sin(angle), 0],
                         [0, 1, 0, 0],
                         [np.sin(angle), 0, np.cos(angle), 0],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def I(self):
        return RotXMat(-self._angle)


class RotZMat(TrnsfMat):
    """
    Rotate z matrix
    """
    type_nickname = 'RZ'

    def __new__(cls, angle=np.pi / 2):
        return np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                         [np.sin(angle), np.cos(angle), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def I(self):
        return RotXMat(-self._angle)


class EyeMat4(Mat4):
    """
    4x4 Identity matrix
    """
    type_nickname = 'E'

    def __new__(cls):
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=float).view(cls)

    @property
    def I(self):
        return EyeMat4()

    def __str__(self):
        return f"<EyeMat>"

    def __setitem__(self, key, value):
        raise Exception("properties of Eye matrix cant be assigned")
