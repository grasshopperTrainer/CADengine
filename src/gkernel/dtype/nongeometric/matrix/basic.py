from .._NoneGeomDataType import *


class Mat4(MatrixLikeData):
    type_nickname = 'M4'

    def __mul__(self, other):
        if isinstance(other, Mat4):
            return Mat4(self._data.dot(other._data))
        else:
            arr = self._data.dot(other._data)
            try:
                return other.__class__.from_row(arr)
            except:
                return Mat4(arr)

    def __str__(self):
        return f"<Mat4\n{self._data}>"