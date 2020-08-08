from ._GeomDataType import *


class Vec(GeomDataType):
    def __init__(self, x=1, y=0, z=0):
        super().__init__(np.array((x, y, z, 0)).reshape((4, 1)))

    def __sub__(self, other):
        if isinstance(other, Vec):
            v = Vec()
            v._data = self._data - other._data
            return v
        else:
            raise NotImplementedError

    def cross(self, other):
        d = np.cross(self._data[:3], other._data[:3], axis=0)
        return Vec(*d.flatten())

    def amplify(self, magnitude):
        self.normalize()
        self._data *= magnitude

    def normalize(self):
        self._data = self._data/self.length

    @property
    def length(self):
        x, y, z, _ = self._data.T[0]
        return np.sqrt(x**2 + y**2 + z**2)

    @property
    def xyz(self):
        return self._data.T[0][:3]


class Pnt(GeomDataType, MatrixLikeData):
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
    def x_axis(self):
        return Vec(*self._data[:, 1].flatten()[:3])

    @property
    def y_axis(self):
        return Vec(*self._data[:, 2].flatten()[:3])

    @property
    def z_axis(self):
        return Vec(*self._data[:, 3].flatten()[:3])

    @property
    def components(self):
        return self.origin, self.x_axis, self.y_axis, self.z_axis


class Line(GeomDataType):
    def __init__(self):
        raise NotImplementedError

    pass
