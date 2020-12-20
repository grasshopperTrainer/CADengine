from gkernel.dtype.geometric._GeomDataType import *
from gkernel.dtype.nongeometric.matrix import TrnsfMats, RotXMat, RotYMat, RotZMat, MoveMat
import copy
from math import sqrt
import warnings


class Vectorlike(ArrayLikeData):

    @property
    def x(self):
        return self[0, 0]

    @property
    def y(self):
        return self[1, 0]

    @property
    def z(self):
        return self[2, 0]

    @property
    def xyz(self):
        return self.x, self.y, self.z

    # def __sub__(self, other):
    #     raw = self._data - other._data
    #     sign = raw[3, 0]
    #     if sign == 1:
    #         return Pnt.from_row(raw)
    #     elif sign == 0:
    #         return Vec.from_row(raw)
    #     else:
    #         raise NotImplementedError

    # def __add__(self, other):
    #     raw = self._data + other._data
    #     sign = raw[3, 0]
    #     if sign == 1:
    #         return Pnt.from_row(raw)
    #     elif sign == 0:
    #         return Vec.from_row(raw)
    #     else:
    #         raise NotImplementedError
    #
    # def __mul__(self, other):
    #     # do dot
    #     if isinstance(other, ArrayLikeData):
    #         return np.dot(self._data.T, other._data)[0, 0]
    #     # do simple mult
    #     elif isinstance(other, Number):
    #         v = self.__class__()
    #         v._data = self._data * other
    #         return v
    #     else:
    #         raise NotImplementedError
    def __mul__(self, other):
        # amplify
        if isinstance(other, Number):
            return super().__mul__(other)
        elif not isinstance(other, Vectorlike):
            # multiplying else unknown
            raise TypeError
        elif isinstance(self, other.__class__):
            # multiplying point to point unknown
            raise TypeError
        else:
            # multiplying point to vector or vise versa
            return self.dot(other.T)


class Vec(Vectorlike):

    def __new__(cls, x=1, y=0, z=0):
        return np.array([[x],
                         [y],
                         [z],
                         [0]], dtype=float).view(cls)

    def __str__(self):
        return f"<Vec : {[round(n, 3) for n in self[:3, 0]]}>"

    @classmethod
    def cross(cls, a, b):
        """
        cross product between two vectors

        ! cross product is anticommutative
        :param a: vector
        :param b: vector
        :return: new vector
        """
        # formula scrapped from wiki
        ax, ay, az = a.xyz
        bx, by, bz = b.xyz
        x = ay * bz - az * by
        y = az * bx - ax * bz
        z = ax * by - ay * bx
        return Vec(x, y, z)

    @classmethod
    def angle_between(cls, a, b):
        """
        angle between two vectors in domain of (0, pi)

        :param a: vector
        :param b: vector
        :return: in radian
        """
        return np.arccos(Vec.dot(a, b) / (a.length * b.length))

    @classmethod
    def dot(self, a, b):
        """
        calculate dot product between self and vec

        :param point:
        :return:
        """
        return np.dot(a.T, b)[0, 0]

    def amplify(self, magnitude, copy=False):
        if copy:
            self = self.copy()
        self.normalize()
        self[:] = self * magnitude
        if copy:
            return self

    def normalize(self):
        """
        normalize self

        :return: None if self is 0vector else self
        """
        if self.is_zero():
            warnings.warn("zero vector cant be normalized")
            return
        self[:] = self / self.length
        return self

    def is_zero(self):
        return True if self.xyz == (0, 0, 0) else False

    def normalized(self):
        """
        normalized self

        :return: copy of normalized self
        """

        return self / self.length

    def _projected_on(self, plane):
        """
        projection

        :param plane:
        :return:
        """
        vec = self.copy()
        if plane == 'xy':
            vec[2] = 0
        elif plane == 'yz':
            vec[0] = 0
        elif plane == 'zx':
            vec[1] = 0
        return vec

    def projected_on_xy(self):
        """
        vector projected on xy plane
        :return: copy of projected self
        """
        return self._projected_on('xy')

    def projected_on_yz(self):
        """
        vector projected on yz plane
        :return: copy of projected self
        """
        return self._projected_on('yz')

    def projected_on_zx(self):
        """
        vector projected on zx plane
        :return: copy of projected self
        """
        return self._projected_on('zx')

    @property
    def length(self):
        x, y, z, _ = self.T[0]
        return np.sqrt(x ** 2 + y ** 2 + z ** 2)

    @classmethod
    def pnt2(cls, tail, head):
        """
        Construct new vector from two points
        :return:
        """
        return head - tail

    # def __copy__(self):
    #     return self.

    # def __deepcopy__(self, memodict={}):
    #     return self.__class__.from_row(self._data.copy())

    # def copy(self):
    #     return copy.copy(self)


class Pnt(Vectorlike):
    def __new__(cls, x=0, y=0, z=0):
        return np.array([[x],
                         [y],
                         [z],
                         [1]], dtype=float).view(Pnt)

    @classmethod
    def cast(self, v):
        if isinstance(v, Pnt):
            i = Pnt()
            i._data = v._data.copy()
            return i

        if isinstance(v, Vec):
            i = Pnt()
            i._data = v.copy()
            i._data[3, 0] = 1
            return i
        else:
            raise NotImplementedError

    def __str__(self):
        return f"<Pnt : {[round(n, 3) for n in self[:3, 0]]}>"


class Pln(ArrayLikeData):

    @classmethod
    def from_components(cls, o, x, y, z):
        """
        construct plane from its components

        :param o: origin
        :param x: xaxis
        :param y: yaxis
        :param z: zaxis
        :return:
        """
        p = Pln()
        # fill array
        for i, vec in enumerate([o, x, y, z]):
            p[:3, i] = vec[:3, 0] if isinstance(vec, Vectorlike) else vec
        return p

    def __new__(cls, o=(0, 0, 0), x=(1, 0, 0), y=(0, 1, 0), z=(0, 0, 1)):

        return np.array([[o[0], x[0], y[0], z[0]],
                         [o[1], x[1], y[1], z[1]],
                         [o[2], x[2], y[2], z[2]],
                         [1, 0, 0, 0]], dtype=float).view(cls)

    def __array_finalize__(self, obj):
        """
        Make vectors perpendicular, normalized and
        create transformation matrix into plane space

        vectors are made perpendicular by referencing vectors in xyz order
        :return:
        """
        # check for unit plane
        if (self.view(np.ndarray) == np.array([[0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [0, 0, 0, 1],
                                               [1, 0, 0, 0]])).all():
            self._trnsf_mats = TrnsfMats()
            return
        # make vectors normalized and perpendicular
        x, y = self.axis_x, self.axis_y
        z = Vec.cross(x, y)  # find z
        y = Vec.cross(z, x)  # find y
        x, y, z = [v.normalized() for v in (x, y, z)]
        plane = np.array([[0, x.x, y.x, z.x],
                          [0, x.y, y.y, z.y],
                          [0, x.z, y.z, z.z],
                          [1, 0, 0, 0]], dtype=float)
        # calculate 'plane to origin' rotation matrices
        # last rotation is of x so match axis x to unit x prior
        x_on_xy = x.projected_on_xy()
        dir_vec = Vec.cross(Vec(1, 0, 0), x_on_xy)
        if dir_vec.is_zero():
            rot_dir = 0
        elif dir_vec.z > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        rz = RotZMat(Vec.angle_between(Vec(1, 0, 0), x_on_xy) * rot_dir)

        plane = rz * plane
        x_on_zx = Vec(*plane[:3, 1])
        dir_vec = Vec.cross(Vec(1, 0, 0), x_on_zx)
        if dir_vec.is_zero():
            rot_dir = 0
        elif dir_vec.y > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        ry = RotYMat(Vec.angle_between(Vec(1, 0, 0), x_on_zx) * rot_dir)

        # axis x is aligned so lastly match axis y
        plane = ry * plane
        y_on_yz = Vec(*plane[:3, 2])
        dir_vec = Vec.cross(Vec(0, 1, 0), y_on_yz)
        if dir_vec.is_zero():
            rot_dir = 0
        elif dir_vec.x > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        rx = RotXMat(Vec.angle_between(Vec(0, 1, 0), y_on_yz) * rot_dir)

        to_origin = MoveMat(*(-self.origin).xyz)
        # found 'plane to origin' so 'origin to plane' is inverse of it
        self._trnsf_mats = TrnsfMats([to_origin, rz, ry, rx]).I

    def get_axis(self, sign: ('x', 'y', 'z')):
        sign = {'x': 1, 'y': 2, 'z': 3}[sign]
        v = Vec.from_row(self._data[:, sign:sign + 1])
        return v

    @property
    def origin(self):
        return Pnt(*self[:3, 0])

    @property
    def axis_x(self):
        return Vec(*self[:3, 1])

    @property
    def axis_y(self):
        return Vec(*self[:3, 2])

    @property
    def axis_z(self):
        return Vec(*self[:3, 3])

    @property
    def components(self):
        return self.origin, self.axis_x, self.axis_y, self.axis_z

    def __str__(self):
        return f"<Pln : {[round(n, 3) for n in self[:3, 0]]}>"


class Tgl(ArrayLikeData):
    """
    Tgl for 'triangle
    """

    def __new__(cls, v0=(0, 0, 0), v1=(10, 0, 0), v2=(0, 10, 0)):
        """
        described by three vertices
        :param v0:
        :param v1:
        :param v2:
        """
        return np.array([[v0[0], v1[0], v2[0]],
                         [v0[1], v1[1], v2[1]],
                         [v0[2], v1[2], v2[2]],
                         [1, 1, 1]], dtype=float).view(cls)

    @property
    def v0(self):
        """
        vertex 0
        :return:
        """
        return Pnt.from_row(np.reshape(self._data[:4, 0], [4, 1]))

    @property
    def v1(self):
        """
        vertex 1
        :return:
        """
        return Pnt.from_row(np.reshape(self._data[:4, 1], [4, 1]))

    @property
    def v2(self):
        """
        vertex 2
        :return:
        """
        return Pnt.from_row(np.reshape(self._data[:4, 2], [4, 1]))

    @property
    def vertices(self):
        return self.v0, self.v1, self.v2

    @property
    def centroid(self):
        """
        average of vertices
        :return:
        """
        return Pnt.from_row(np.dot(self._data, [[1], [1], [1]]) / 3)

    def __str__(self):
        """
        triangle described by centroid
        :return:
        """
        return f"<Tgl {self.centroid}>"


class Ray(ArrayLikeData):
    """
    Ray is a line without ending
    """

    def __new__(cls, o=(0, 0, 0), v=(0, 0, 1)):
        """

        :param o: origin as a point
        :param v: direction as a vector
        """
        return np.array([[o[0], v[0]],
                         [o[1], v[1]],
                         [o[2], v[2]],
                         [1, 0]], dtype=float).view(cls)

    @property
    def origin(self):
        return Pnt(*self[:3, 0].tolist())

    @property
    def heading(self):
        return Vec(*self[:3, 1].tolist())

    def __str__(self):
        return f"<Ray from {self.origin}>"

    def describe(self):
        return f"<<Ray from:{self.origin} heading:{self.heading}"


class Lin(ArrayLikeData):

    def __new__(cls, p0=(0, 0, 0), p1=(0, 0, 1)):
        """
        define line from two coordinate
        :param p0: xyz coord of starting vertex
        :param p1: xyz coord of ending vertex
        """
        return np.array([[p0[0], p1[0]],
                         [p0[1], p1[1]],
                         [p0[2], p1[2]],
                         [1, 1]], dtype=float).view(cls)

    @classmethod
    def from_two_pnt(cls, start: Pnt, end: Pnt):
        """
        create line using start, end vertex
        :param start: starting vertex of line
        :param end: ending vertex of line
        :return:
        """
        return Lin(start.xyz, end.xyz)

    def length(self):
        """
        of line
        :return:
        """
        summed = 0
        for i in range(3):
            summed += pow(self._data[i, 0] - self._data[i, 1], 2)
        return sqrt(summed)

    def __str__(self):
        return f"<Lin {round(self.length(), 3)}>"
