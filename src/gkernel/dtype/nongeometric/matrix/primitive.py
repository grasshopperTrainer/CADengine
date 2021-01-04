import copy

from .._NoneGeomDataType import *


class Mat4(ArrayLikeData):
    type_nickname = 'M4'


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

    def __neg__(self):
        return self.I

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
                arr = np.dot(self, other, out=other.copy())
                return arr
            except Exception as e:
                raise ArithmeticError("cant multiply")
            # try casting result into class on the right
            # if arr.shape == other.shape:
            #     try:
            #         return arr.view(other.__class__)
            #     except:
            #         raise Exception(f"result is not like {other.__class__.__name__}")
            # else:
            #     raise TypeError


class TrnsfMats(TrnsfMat):
    """
    Ordered transformation matrices

    Useful retrieving intermediate transformation matrix
    of getting inverse of all transformation.
    """
    type_nickname = 'CM'

    def __new__(cls, matrices=[]):
        obj = super(TrnsfMats, cls).__new__(cls, shape=(4, 4))  # default transformation matrix that does nothing
        obj._matrices = matrices  # stacked matrix for inverse
        obj._merge()
        return obj

    def __array_finalize__(self, obj):
        """
        copies matrix stack of original if obj is one of its kind
        and update self as merged

        :param obj:
        :return:
        """
        if obj is None:
            self._matrices = []
        elif isinstance(obj, self.__class__):
            self._matrices = copy.deepcopy(obj._matrices)  # deepcopying? what if its a view?
            self._merge()

    def _merge(self):
        """
        merge matrices and set it as self's value
        :return:
        """
        # update as merged array
        arr = np.eye(4)
        for m in self._matrices:
            arr = m.dot(arr)
        self[:] = arr

    def append(self, matrix):
        """
        Append matrix for compound transformation

        append matrix into list and update value of self
        :param matrix: matrix used to translate
        :return:
        """
        self[:] = matrix * self  # be careful for the applying order
        self._matrices.append(matrix)

    def append_all(self, *matrices):
        """
        Append matrices with given order

        :param matrices: matrices for transformation
        :return:
        """
        for mat in matrices:
            self[:] = mat * self
        self._matrices += list(matrices)

    @property
    def I(self):
        """
        Inverse of all transformation matrix
        :return:
        """
        return TrnsfMats([m.I for m in reversed(self._matrices)])

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
    def xyz(self):
        return self[:3, 3]

    @property
    def I(self):
        return MoveMat(-self.x, -self.y, -self.z)

    def __str__(self):
        return f"<MoveMat {[round(v, 3) for v in self.xyz]}>"

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


class SingleRotMat(TrnsfMat):
    """
    Rotation matrix around one of xyz axis
    """

    _angle = 0  # rotation angle

    @property
    def angle(self):
        return self._angle

    def __array_finalize__(self, other):
        if other is None:
            return
        elif isinstance(other, self.__class__):
            self._angle = other._angle
        else:
            pass

    @property
    def I(self):
        return self.__class__(-self._angle)


class RotXMat(SingleRotMat):
    """
    Rotate x matrix
    """
    type_nickname = 'RX'

    def __new__(cls, angle=0):
        obj = np.array([[1, 0, 0, 0],
                        [0, np.cos(angle), -np.sin(angle), 0],
                        [0, np.sin(angle), np.cos(angle), 0],
                        [0, 0, 0, 1]], dtype=float).view(cls)
        obj._angle = angle
        return obj

    def __str__(self):
        return f"<RotXMat: {self._angle}>"


class RotYMat(SingleRotMat):
    """
    Rotate y matrix
    """
    type_nickname = 'RY'

    def __new__(cls, angle=np.pi / 2):
        obj = np.array([[np.cos(angle), 0, np.sin(angle), 0],
                        [0, 1, 0, 0],
                        [-np.sin(angle), 0, np.cos(angle), 0],
                        [0, 0, 0, 1]], dtype=float).view(cls)
        obj._angle = angle
        return obj

    def __str__(self):
        return f"<RotYMat: {self._angle}>"


class RotZMat(SingleRotMat):
    """
    Rotate z matrix
    """
    type_nickname = 'RZ'

    def __new__(cls, angle=np.pi / 2):
        obj = np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                        [np.sin(angle), np.cos(angle), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]], dtype=float).view(cls)
        obj._angle = angle
        return obj

    def __str__(self):
        return f"<RotZMat: {self._angle}>"


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
