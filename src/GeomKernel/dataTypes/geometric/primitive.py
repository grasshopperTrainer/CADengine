from ._GeomDataType import *
from ..nongeometric.complex import TrnsfMat

import copy


class Vectorlike(GeomDataType):

    @property
    def x(self):
        return self._data[0][0]
    @property
    def y(self):
        return self._data[1][0]
    @property
    def z(self):
        return self._data[2][0]

    @property
    def xyz(self):
        return self._data.T[0][:3]

    def __sub__(self, other):
        raw = self._data - other._data
        sign = raw[3, 0]
        if sign == 1:
            return Pnt.new_from_raw(raw)
        elif sign == 0:
            return Vec.new_from_raw(raw)
        else:
            raise NotImplementedError

    def __add__(self, other):
        raw = self._data + other._data
        sign = raw[3, 0]
        if sign == 1:
            return Pnt.new_from_raw(raw)
        elif sign == 0:
            return Vec.new_from_raw(raw)
        else:
            raise NotImplementedError


class Vec(Vectorlike):
    def __init__(self, x=1, y=0, z=0):
        super().__init__(np.array((x, y, z, 0)).reshape((4, 1)))

    def __sub__(self, other):
        if isinstance(other, Vec):
            v = Vec()
            v._data = self._data - other._data
            return v
        else:
            raise NotImplementedError

    def __str__(self):
        return f"<Vec : {[round(n, 3) for n in self._data[:3, 0]]}>"

    def __repr__(self):
        return self.__str__()

    def cross(self, other):
        d = np.cross(self._data[:3], other._data[:3], axis=0)
        return Vec(*d.flatten())

    def amplify(self, magnitude, copy=False):
        if copy:
            self = self.copy()
        self.normalize()
        self._data *= magnitude
        if copy:
            return self

    def normalize(self):
        self._data = self._data/self.length

    @property
    def length(self):
        x, y, z, _ = self._data.T[0]
        return np.sqrt(x**2 + y**2 + z**2)

    @classmethod
    def pnt2(cls, tail, head):
        """
        Construct new vector from two points
        :return:
        """
        return head - tail

    def __copy__(self):
        return self.__class__.new_from_raw(self._data)

    def __deepcopy__(self, memodict={}):
        return self.__class__.new_from_raw(self._data.copy())

    def copy(self):
        return copy.copy(self)


class Pnt(Vectorlike):
    def __init__(self, x=0, y=0, z=0):
        super().__init__(np.array((x, y, z, 1)).reshape((4, 1)))

    @classmethod
    def cast(self, v):
        if isinstance(v, Pnt):
            i = Pnt()
            i._data = v._data.copy()
            return i

        if isinstance(v, Vec):
            i = Pnt()
            i._data = v._data.copy()
            i._data[3, 0] = 1
            return i
        else:
            raise NotImplementedError


class Pln(GeomDataType):
    @classmethod
    def from_components(cls, o, x, y, z):
        p = Pln()
        p._data = np.hstack((Pnt.cast(o)._data, x._data, y._data, z._data))
        return p

    def __init__(self, o=(0, 0, 0), x=(1, 0, 0), y=(0, 1, 0), z=(0, 0, 1)):
        arr = np.array((o, x, y, z)).T
        arr = np.vstack([arr, (1, 0, 0, 0)])
        super().__init__(arr)

    @property
    def origin(self):
        return Pnt(*self._data[:, 0].flatten()[:3])

    def get_axis(self, sign: ('x', 'y', 'z')):
        sign = {'x': 1, 'y': 2, 'z': 3}[sign]
        v = Vec.new_from_raw(self._data[:, sign:sign+1])
        return v

    @property
    def origin(self):
        return Pnt.new_from_raw(self._data[:, :1])

    @property
    def axis_x(self):
        return Vec(*self._data[:, 1].flatten()[:3])

    @property
    def axis_y(self):
        return Vec(*self._data[:, 2].flatten()[:3])

    @property
    def axis_z(self):
        return Vec(*self._data[:, 3].flatten()[:3])

    @property
    def components(self):
        return self.origin, self.axis_x, self.axis_y, self.axis_z

    def __rmul__(self, other):
        print('dddd')
        if isinstance(other, TrnsfMat):
            return self.new_from_raw(other._data.dot(self._data))


class Line(GeomDataType):

    def __init__(self):
        raise NotImplementedError

    pass
