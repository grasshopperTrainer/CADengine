from ._GeomDataTypeNode import *


class Vector(GeomDataType):
    def __init__(self, x=1,y=0,z=0):
        self._data = np.array((x,y,z,0)).reshape((4,1))

    def __sub__(self, other):
        if isinstance(other, Vector):
            v = Vector()
            v._data = self._data - other._data
            return v
        else:
            raise NotImplementedError

    def __mul__(self, other):
        if isinstance(other, (Vector, Point)):
            return np.dot(self._data.T, other._data)[0,0]
        elif isinstance(other, (float, int)):
            v = Vector()
            v._data = self._data*other
            return v
        else:
            raise NotImplementedError

    def __truediv__(self, other):
        v = Vector()
        v._data = self._data / other
        return v

    def __neg__(self):
        v = Vector()
        v._data = -1 * self._data
        return v

    def cross(self, other):
        d = np.cross(self._data[:3], other._data[:3], axis=0)
        return Vector(*d.flatten())


class Point(GeomDataType):
    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self._data = np.array((x,y,z,1)).reshape((4,1))


class Plane(GeomDataType):

    @classmethod
    def from_vectors(cls,o, x, y, z):
        p = Plane()
        p._data = np.hstack((o._data, x._data, y._data, z._data))
        return p

    def __init__(self,o=(0,0,0), x=(1, 0, 0), y=(0, 1, 0), z=(0, 0, 1)):
        self._data = np.array((o, x, y, z)).T
        self._data = np.vstack([self._data, (1, 0, 0, 0)])

    @property
    def origin(self):
        return Point(*self._data[:,0].flatten()[:3])

    @property
    def x_axis(self):
        return Vector(*self._data[:,1].flatten()[:3])

    @property
    def y_axis(self):
        return Vector(*self._data[:,2].flatten()[:3])

    @property
    def z_axis(self):
        return Vector(*self._data[:,3].flatten()[:3])

    @property
    def components(self):
        return self.origin, self.x_axis, self.y_axis, self.z_axis