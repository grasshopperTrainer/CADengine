from .primitive import *
from numbers import Number
from ..geometric._GeomDataType import GeomDataType

class TrnsfMat(Mat4):
    """
    Transformation matrix
    """

    def __mul__(self, other):
        if isinstance(other, TrnsfMat):
            return TrnsfMat(self._data.dot(other._data))
        elif isinstance(other, GeomDataType):
            return other.new_from_raw(self._data.dot(other._data))


class CompoundTrnsfMat(TrnsfMat):
    pass


class TrnslMat(TrnsfMat):
    """
    Translation matrix (move)
    """
    def __init__(self, x=0,y=0,z=0):
        mat = np.eye(4)
        mat[:3, 3] = x, y, z
        super().__init__(mat)

    @property
    def I(self):
        return self.__class__(*self._data[:3, 3])


class RotMat(TrnsfMat):
    """
    Rotation matrix
    """
    def __init__(self, axis='x', angle=np.pi/2):
        if axis not in 'xyz':
            raise ValueError("axis should be str indication one of 'x y z'")
        self._axis = axis
        mat = np.eye(4)
        if axis == 'x':
            mat[(1,1,2,2),(1,2,1,2)] = np.cos(angle), -np.sin(angle), np.sin(angle), np.cos(angle)
        elif axis == 'y':
            mat[(0,0,2,2),(0,2,0,2)] = np.cos(angle), np.sin(angle), -np.sin(angle), np.cos(angle)
        elif axis == 'z':
            mat[(0,0,1,1),(0,1,0,1)] = np.cos(angle), -np.sin(angle), np.sin(angle), np.cos(angle)
        super().__init__(mat)

    @property
    def I(self):
        return self.new_from_raw(self._data.T)


class EyeMat4(Mat4):
    """
    4x4 Identity matrix
    """
    def __init__(self):
        mat = np.eye(4)
        super().__init__(mat)
