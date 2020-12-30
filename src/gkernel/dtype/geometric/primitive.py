from .._DataType import ArrayLikeData
from gkernel.dtype.nongeometric.matrix import TrnsfMats, RotXMat, RotYMat, RotZMat, MoveMat

import numpy as np

import copy
from math import sqrt
import warnings
from numbers import Number
import abc


class Mat1(ArrayLikeData):

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

    def __neg__(self):
        """
        not to negate fourth(w)
        :return:
        """
        obj = super().__neg__()
        obj[3, 0] = -obj[3, 0]
        return obj

    def __mul__(self, other):
        if isinstance(other, Number):  # amplify
            return super().__mul__(other)
        elif not isinstance(other, Mat1):  # multiplying else unknown
            raise TypeError
        elif isinstance(self, other.__class__):  # multiplying point to point unknown
            raise TypeError
        else:  # multiplying point to vector or vise versa
            return self.dot(other.T)


class VecConv(metaclass=abc.ABCMeta):
    """
    Interface for vector convertable
    """
    @abc.abstractmethod
    def as_vec(self):
        pass


class LinConv(metaclass=abc.ABCMeta):
    """
    Interface for line convertalbe
    """
    @abc.abstractmethod
    def as_lin(self):
        pass


class PntConv(metaclass=abc.ABCMeta):
    """
    Interface for point convertable
    """
    @abc.abstractmethod
    def as_pnt(self):
        pass


class Ray(ArrayLikeData, VecConv, LinConv):
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
        return Pnt(*self[:3, 0])

    @property
    def normal(self):
        return Vec(*self[:3, 1])

    @classmethod
    def from_pnt_vec(cls, origin, normal):
        """
        create new ray from ray origin and normal

        :param origin: Pnt ray origin
        :param normal: Vec ray direction
        :return:
        """

        return cls(origin.xyz, normal.xyz)

    def as_vec(self):
        return self.normal

    def as_lin(self):
        """
        convert Ray into Line

        :return: Lin instance with length 1
        """
        return Lin.from_pnt_vec(self.origin, self.normal)

    def __str__(self):
        return f"<Ray from {self.origin}>"

    def describe(self):
        return f"<<Ray from:{self.origin} heading:{self.normal}"


class Vec(Mat1, VecConv, PntConv):

    def __new__(cls, x=1, y=0, z=0):
        return np.array([[x],
                         [y],
                         [z],
                         [0]], dtype=float).view(cls)

    def __array_finalize__(self, obj):
        """
        :param obj:
        :atrib _is_new: flag for newly set. used to indicate when cache clean is needed.
        :atrib _length: length of vector
        :return:
        """
        self.__clean_cache = True
        self.__length = None

    def __str__(self):
        return f"<Vec : {[round(n, 3) for n in self[:3, 0]]}>"

    def __truediv__(self, other):
        """
        overridden to preserve w value of array

        :param other:
        :return:
        """
        obj = super().__truediv__(other)
        if isinstance(other, Number):
            obj[3, 0] = 1
        return obj

    def __setitem__(self, key, value):
        """
        overridden to indicate cache clean needed

        :param key:
        :param value:
        :return:
        """
        super().__setitem__(key, value)
        self.__clean_cache = True

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

    @classmethod
    def amplified(cls, vec, magnitude):
        """
        return amplified vector

        :param vec:
        :param magnitude:
        :return: copy of amplified vec
        """
        return vec.normalize().amplify(magnitude)

    def amplify(self, magnitude):
        """
        amplify self

        :param self:
        :param magnitude:
        :return:
        """
        self.normalize()
        self[:] = self * magnitude
        return self

    def normalize(self):
        """
        normalize self

        :return: None if self is 0vector else self
        """
        if self.is_zero():
            warnings.warn("zero vector cant be normalized")
            return self
        self[:] = self / self.length
        return self

    def is_zero(self):
        """
        boolean for self being zero vector
        :return:
        """
        return True if self.xyz == (0, 0, 0,) else False

    def is_parallel_with(self, vec):
        """
        check if self is parallel with given vector
        :param vec:
        :return:
        """
        return True if Vec.cross(self, vec)[0] == 0 else False

    def is_oposite_with(self, vec):
        """
        check if self is oposite with given vector
        :param vec:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def normalized(cls, vec):
        """
        normalized self

        :return: copy of normalized vector
        """

        return vec / vec.length

    @classmethod
    def trnsf_to_x(cls, vec):
        """
        calculate transformation matrix for aligning self to axis x
        :return: compoud transformation matrix (TransfMats)
        """
        axis = Vec(1, 0, 0)
        if vec.is_parallel_with(axis):
            return TrnsfMats()
        v_on_zx = vec.projected_on_yz()
        rot_dir = 1 if Vec.cross(v_on_zx, axis).y > 0 else -1  # to determine direction of rotation
        ry = RotYMat(Vec.angle_between(axis, v_on_zx) * rot_dir)

        v_on_xy = ry * vec
        rot_dir = 1 if Vec.cross(v_on_xy, axis).z > 0 else -1
        rz = RotZMat(Vec.angle_between(axis, v_on_xy) * rot_dir)
        return TrnsfMats([ry, rz])

    @classmethod
    def trnsf_to_y(cls, vec):
        """
        calculate transformation matrix for aligning self to axis y
        :return: compoud transformation matrix (TransfMats)
        """
        axis = Vec(0, 1, 0)
        if vec.is_parallel_with(axis):
            return TrnsfMats()
        v_on_yz = vec.projected_on_yz()
        rot_dir = 1 if Vec.cross(v_on_yz, axis).x > 0 else -1  # to determine direction of rotation
        rx = RotXMat(Vec.angle_between(axis, v_on_yz) * rot_dir)

        v_on_xy = rx * vec
        rot_dir = 1 if Vec.cross(v_on_xy, axis).z > 0 else -1
        rz = RotZMat(Vec.angle_between(axis, v_on_xy) * rot_dir)
        return TrnsfMats([rx, rz])

    @classmethod
    def trnsf_to_z(cls, vec):
        """
        calculate transformation matrix for aligning self to axis z
        :return: compoud transformation matrix (TransfMats)
        """
        axis = Vec(0, 0, 1)
        if vec.is_parallel_with(axis):
            return TrnsfMats()
        v_on_yz = vec.projected_on_yz()
        rot_dir = 1 if Vec.cross(v_on_yz, axis).x > 0 else -1  # to determine direction of rotation
        rx = RotXMat(Vec.angle_between(axis, v_on_yz) * rot_dir)

        v_on_zx = rx * vec
        rot_dir = 1 if Vec.cross(v_on_zx, axis).y > 0 else -1
        ry = RotYMat(Vec.angle_between(axis, v_on_zx) * rot_dir)
        return TrnsfMats([rx, ry])

    def align_with_vec(self, vec):
        """
        calculate transformation matrix for aligning self to given vector
        :param vec:
        :return:
        """
        raise NotImplementedError

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

    @classmethod
    def from_pnts(cls, tail, head):
        """
        Construct new vector from two points

        :return:
        """
        return head - tail

    @classmethod
    def from_pnt(cls, point):
        """
        create new vector from point

        :param point:
        :return:
        """
        return Vec(*point.xyz)

    def __recal_cache(self):
        """
        recalculate cached values

        :return:
        """
        x, y, z = self.xyz
        self.__length = np.sqrt(x ** 2 + y ** 2 + z ** 2)

    @property
    def length(self):
        # if self.__clean_cache:
        x, y, z, _ = self.T[0]
        self.__length = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        return self.__length
        # else:
        #     return self.__length

    def as_vec(self):
        return self

    def as_pnt(self):
        return Pnt(*self.xyz)

    def as_lin(self):
        return Lin(p0=(0, 0, 0), p1=self.xyz)


class Pnt(Mat1, VecConv, PntConv):
    """
    Point
    """

    def __new__(cls, x=0, y=0, z=0):
        return np.array([[x],
                         [y],
                         [z],
                         [1]], dtype=float).view(cls)

    def __sub__(self, other):
        """
        to return `Vec` from two points
        :param other:
        :return:
        """
        r = super().__sub__(other)
        if isinstance(other, Pnt):
            return r.view(Vec)
        else:
            return r

    def __str__(self):
        return f"<Pnt : {[round(n, 3) for n in self[:3, 0]]}>"

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

    def as_vec(self):
        return Vec(*self.xyz)

    def as_pnt(self):
        return self

    def intersect(self, ray: Ray):
        """
        ray point intersection

        :param ray: ray to intersect with
        :return: self as an intersection point else None
        """
        # 0 cross product means parallel
        ray_to_pnt = self - ray.origin
        if Vec.cross(ray.normal, ray_to_pnt).is_zero():
            return self
        else:
            return None


class NamedVec(Vec):
    """
    Named vector
    """
    def __new__(cls, vec_like):
        return vec_like.as_vec().view(cls)


class Xax(NamedVec):
    """
    Vector as x axis
    """
    def __str__(self):
        return f"<Xax {[round(n, 3) for n in self[:3, 0]]}>"


class Yax(NamedVec):
    """
    Vector as y axis
    """
    def __str__(self):
        return f"<Yax {[round(n, 3) for n in self[:3, 0]]}>"


class Zax(NamedVec):
    """
    Vector as z axis
    """
    def __str__(self):
        return f"<Zax {[round(n, 3) for n in self[:3, 0]]}>"


class Pln(ArrayLikeData, PntConv):

    @classmethod
    def from_ori_axies(cls, o, x, y, z):
        """
        construct plane from its components

        :param o: origin
        :param x: xaxis
        :param y: yaxis
        :param z: zaxis
        :return:
        """
        return Pln(o.xyz, x.xyz, y.xyz, z.xyz)

    def __new__(cls, o=(0, 0, 0), x=(1, 0, 0), y=(0, 1, 0), z=(0, 0, 1)):

        return np.array([[o[0], x[0], y[0], z[0]],
                         [o[1], x[1], y[1], z[1]],
                         [o[2], x[2], y[2], z[2]],
                         [1, 0, 0, 0]], dtype=float).view(cls)

    def __array_finalize__(self, obj):
        """
        standarization? of plane

        1. Make vectors perpendicular, normalized and
        2. create transformation matrix into plane space
        !vectors are made perpendicular by referencing vectors in xyz order!
        :return:
        """
        # check for unit plane
        if (self.view(np.ndarray) == np.array([[0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [0, 0, 0, 1],
                                               [1, 0, 0, 0]])).all():
            self._trnsf_mat = TrnsfMats()
            return
        # make vectors normalized and perpendicular
        x, y = self.axis_x, self.axis_y
        z = Vec.cross(x, y)  # find z
        y = Vec.cross(z, x)  # find y
        x, y, z = [Vec.normalized(v) for v in (x, y, z)]
        plane = np.array([[0, x.x, y.x, z.x],
                          [0, x.y, y.y, z.y],
                          [0, x.z, y.z, z.z],
                          [1, 0, 0, 0]], dtype=float)
        # apply normalized
        self[:4, 1:4] = np.array([x, y, z]).T

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
        self._trnsf_mat = TrnsfMats([to_origin, rz, ry, rx]).I

    def get_axis(self, sign: ('x', 'y', 'z')):
        sign = {'x': 1, 'y': 2, 'z': 3}[sign]
        v = Vec.from_row(self._data[:, sign:sign + 1])
        return v

    def as_pnt(self):
        return self.origin

    @property
    def origin(self) -> Pnt:
        return Pnt(*self[:3, 0])

    @property
    def axis_x(self) -> Vec:
        return Vec(*self[:3, 1])

    @property
    def axis_y(self) -> Vec:
        return Vec(*self[:3, 2])

    @property
    def axis_z(self) -> Vec:
        return Vec(*self[:3, 3])

    @property
    def components(self):
        return self.origin, self.axis_x, self.axis_y, self.axis_z

    @property
    def trnsf_mat(self):
        """
        return transformation matrix(origin -> plane)
        :return:
        """
        return self._trnsf_mat

    def __str__(self):
        return f"<Pln : {[round(n, 3) for n in self[:3, 0]]}>"

    @classmethod
    def from_lin_pnt(cls, line, point, axis_of='x'):
        """
        construct plane from line and vertex on it

        :param line: axis on the plane
        :param point: point on the plane
        :param axis_of: #optional# tell what input axis is
        :return: plane
        """
        if point in (line.start, line.end):
            raise ValueError("point is the start or end of the line")
        if axis_of == 'x':
            y_axis = point.as_vec()
            return Pln.from_ori_axies(line.start, line.as_vec(), y_axis, Vec(0, 0, 1))
        else:
            raise NotImplementedError

    def intersect(self, ray: Ray):
        """
        ray plane intersection

        referenced from Scratchapixel 2.0 :
        https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection

        :param ray: to intersect with
        :return: Pnt if intersects else None
        """
        # 0 dot means perpendicular and
        # ray perpendicular plane normal means they are parallel
        plane_normal = self.axis_z
        ray_normal = ray.normal
        denom = Vec.dot(plane_normal, ray_normal)
        if abs(denom) < ATOL:  # check if value is 0
            return None
        # if not ray is not parallel with plane
        # check if ray is pointing at plane, not away
        ray_to_origin = self.origin - ray.origin
        # scalar distance describing intersection point from ray origin
        dist = Vec.dot(plane_normal, ray_to_origin) / denom
        if dist >= 0:
            return ray.origin + ray_normal.amplify(dist)
        else:
            return None

    @classmethod
    def is_coplanar(cls, a, b):
        """
        coplanar planes have same origin and normal but not other two axes

        :param a: first plane
        :param b: second plane
        :return: bool
        """
        return True if a.origin == b.origin and a.axis_z == b.axis_z else False

    def pnt_is_on(self, point):
        """
        check if given point is on the plane
        :param point:
        :return:
        """
        if Vec.dot(self.axis_z, point.as_vec()) == 0:
            return True
        else:
            return False

    def pnt_dist(self, point):
        """
        calculate shortest distance from point to plane

        :param point: point to calculate distance from
        :return: float distance
        """
        # find projected on normal
        return abs(Vec.dot(self.axis_z, point.as_vec())/self.axis_z.length)

    def pnt_shortest(self, point):
        """
        find closest point to plane

        :param point: Pnt to drop from
        :return: Pnt on Pln
        """
        d = Vec.dot(self.axis_z, point.as_vec())/self.axis_z.length
        return point + self.axis_z.amplify(d)

    @classmethod
    def from_ori_norm(cls, origin, normal, axis=None):
        """
        construct new plane from origin and normal

        :param origin: plane origin
        :param normal: plane normal
        :param axis: optional, axis to use as peripheral axis
        :return:
        """
        if isinstance(axis, Xax):
            # find axis y
            axis_y = Vec.cross(normal, axis)
            axis_x = Vec.cross(axis_y, normal)
            return Pln.from_ori_axies(o=origin, x=axis_x, y=axis_y, z=normal)
        elif isinstance(axis, Yax):
            # find axis x
            axis_x = Vec.cross(normal, axis)
            axis_y = Vec.cross(normal, axis_x)
            return Pln.from_ori_axies(o=origin, x=axis_x, y=axis_y, z=normal)
        elif isinstance(axis, Zax):
            raise TypeError("z axis cant relate with normal, normal means axis z")
        else:
            raise TypeError("optional axis argument should be wrapped first")


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


# should this eventually moved into `complex`?
class Lin(ArrayLikeData, VecConv):

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
    def from_pnts(cls, start: Pnt, end: Pnt):
        """
        create line using start, end vertex
        :param start: starting vertex of line
        :param end: ending vertex of line
        :return:
        """
        return Lin(start.xyz, end.xyz)

    @classmethod
    def from_pnt_vec(cls, start: Pnt, direction: Vec):
        """
        create line from start and direction

        :param start: starting vertex of line
        :param direction: ending vertex relative to start
        :return:
        """
        return Lin(start.xyz, (start + direction).xyz)

    @classmethod
    def coplanar(cls, a, b):
        """
        check if two lines are on the same plane

        :param a: first line
        :param b: second line
        :return: bool
        """
        # make two plane
        a0, a1, b0, b1 = a.vertices, b.vertices
        av = a1 - a0
        # normal(z) will be calculated from input x, y axis so put trash value
        p0 = Pln.from_ori_axies(o=a0, x=av, y=b0 - a0, z=Vec())
        p1 = Pln.from_ori_axies(o=a0, x=av, y=b1 - a0, z=Vec())
        if not p0 == p1:
            return

    @property
    def length(self):
        """
        of line
        :return:
        """
        summed = 0
        for i in range(3):
            summed += pow(self[i, 0] - self[i, 1], 2)
        return sqrt(summed)

    def reversed(self):
        """
        create new Lin reversed

        :return: new reversed Lin
        """

        return self.__class__(self.end.xyz, self.start.xyz)

    def reverse(self):
        """
        reverse self

        :return: self reversed
        """
        self[:] = np.roll(self, shift=1, axis=1)
        return self

    @property
    def start(self):
        return Pnt(*self[:3, 0])

    @property
    def end(self):
        return Pnt(*self[:3, 1])

    def pnt_at(self, t):
        """
        return Point at parameter t

        :param t: in between 0(start), 1(end). is compatible values under, above (0, 1)
        :return:
        """
        if not isinstance(t, Number):
            raise

        return self.start + self.as_vec()*t

    def as_vec(self):
        return self.end - self.start

    def as_lin(self):
        return self

    def intx_ray(self, ray):
        """
        ray line intersection

        refer to: https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect/565282#565282

        :param ray: ray to intersect with
        :return: point if intersects else None
        """

        r = self.as_vec()   # line's vector
        s = ray.normal      # ray's vector
        p, q = self.start, ray.origin
        pq_vec = q - p

        pq_r_norm = Vec.cross(pq_vec, r)
        r_s_norm = Vec.cross(r, s)
        if r_s_norm.is_zero(): # means line and ray is parallel
            if pq_r_norm.is_zero(): # means collinearity. notice parallel != collinear
                # may be three cases
                # 1. ray covers whole line -> return line itself
                # 2. ray covers line fragment -> return new line fragment
                # 3. ray covers no line -> return None
                n, m = Vec.dot(pq_vec, r), Vec.dot(pq_vec, s)
                line_param = n / r.length**2
                if 0 <= line_param <= 1:    # ray starts at on the line
                    if (line_param == 0 and m >= 0) or (line_param == 1 and m < 0): # 1.
                        return self
                    else:   # 2.
                        start = self.start + r*line_param
                        end = self.end if m >= 0 else self.start
                        return Lin.from_pnts(start, end)
                else:
                    if line_param < 0 and m < 0:   # 1.
                        return self
                    elif line_param > 1 and m < 0:
                        return self.reversed()
                    else:   # 3.
                        return None
            else:
                return None
        else:   # may be point intersection or not
            param_l = Vec.cross(pq_vec, s).length/Vec.cross(r, s).length
            param_r = Vec.cross(pq_vec, r).length/Vec.cross(r, s).length
            if param_l == 0:
                return self.start
            elif param_l == 1:
                return self.end
            elif 0 < param_l < 1:
                lin_intx_pnt = self.start + r*param_l
                pnt_intx_lin = ray.origin + s*param_r
                # check for coplanarity here
                if lin_intx_pnt == pnt_intx_lin:
                    return lin_intx_pnt
                else:
                    return None
            else:
                return None

    @classmethod
    def is_coplanar(cls, a, b):
        """
        check coplanarity between two lines

        :param a: first line convertable
        :param b: second line convertable
        :return: bool
        """
        # build plane with line and vertex then check if another vertex is on it
        a, b = a.as_lin(), b.as_lin()
        plane = Pln.from_lin_pnt(a, b.start)
        return plane.pnt_is_on(b.end)

    def __str__(self):
        return f"<Lin {round(self.length, 5)}>"


# casting into
def pnt(obj):
    """
    as point
    :return:
    """
    try:
        return obj.as_pnt()
    except Exception as e:
        raise e


def vec(obj):
    """
    as vector
    :return:
    """
    try:
        return obj.as_vec()
    except Exception as e:
        raise e


def lin(obj):
    """
    as line
    :return:
    """
    try:
        return obj.as_lin()
    except Exception as e:
        raise e
