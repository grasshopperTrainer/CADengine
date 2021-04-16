import abc
import warnings
from math import sqrt
from numbers import Number
import numpy as np

from global_tools.singleton import Singleton
from global_tools.lazy import lazyProp
from gkernel.constants import DTYPE
from gkernel.dtype.nongeometric.matrix.primitive import TrnsfMats, RotXMat, RotYMat, RotZMat, MoveMat
from gkernel.array_like import ArrayLikeData
from gkernel.constants import ATOL


class Mat1(ArrayLikeData):

    def __getattr__(self, item):
        """
        some additional attribute automation

        :param item:
        :return:
        """
        if not (set(item) - {'x', 'y', 'z', 'w'}):
            d = dict(zip('xyzw', self[:, 0].tolist()))
            vs = tuple(d[c] for c in item)
            return vs[0] if len(vs) == 1 else vs
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if set(key).issubset(set('xyzw')):
            d = dict(zip('xyzw', range(4)))

            # check for key, value match
            if len(key) == 1:
                if hasattr(value, '__iter__'):
                    raise ValueError()
                else:
                    value = (value, )
            elif not hasattr(value, '__iter__'):
                raise ValueError()

            # fix value
            for char, val in zip(key, value):
                self[d[char], 0] = val
            return
        return super().__setattr__(key, value)

    # as Pnt and Vec is closely related in arithmetic calculation
    # all is defined here in inherited class
    def __neg__(self):
        """
        not to negate fourth(w)
        :return:
        """
        obj = super().__neg__()
        obj[3, 0] = -obj[3, 0]
        return obj

    def __lt__(self, other):
        """
        less then
        :param other:
        :return:
        """
        if self == other:
            return False

        if np.isclose(self.x, other.x, atol=ATOL):
            if self.y < other.y:
                return True
            else:
                return False
        elif self.x < other.x:
            return True
        else:
            return False

    def __gt__(self, other):
        """
        greater than
        :param other:
        :return:
        """
        if self == other:
            return False

        if np.isclose(self.x, other.x, atol=ATOL):
            if self.y > other.y:
                return True
            else:
                return False
        elif self.x > other.x:
            return True
        else:
            return False

    def __add__(self, other):
        """
        retain constant type casting in between Vec and Pnt addition

        :param other:
        :return:
        """
        if isinstance(self, Vec):
            if isinstance(other, Vec):
                return super().__add__(other)
            elif isinstance(other, Pnt):
                return other.__add__(self)
        elif isinstance(self, Pnt):
            if isinstance(other, Vec):
                return super().__add__(other)
        raise ArithmeticError(f'{self.__class__.__name__}, {other.__class__.__name__} add unknown')

    def __sub__(self, other):
        """
        retain constant type casting in between Vec and Pnt subtraction

        :param other:
        :return:
        """
        if isinstance(self, Vec):
            if isinstance(other, Vec):
                return super().__sub__(other)
            elif isinstance(other, np.ndarray):
                if not other.shape:  # singular unit
                    # compare components
                    return self[:3] - other
                else:
                    raise NotImplementedError
        elif isinstance(self, Pnt):
            if isinstance(other, Pnt):
                return super().__sub__(other).view(Vec)
            elif isinstance(other, Vec):
                return super().__sub__(other)
        raise ArithmeticError(f'{self.__class__.__name__}, {other.__class__.__name__} sub unknown')

    def __mul__(self, other):
        """
        only scalar multiplication on the right is accepted

        :param other: scalar
        :return:
        """
        if isinstance(self, Vec) and isinstance(other, Number):  # amplify
            return super().__mul__(other)
        if isinstance(self, Vec) and isinstance(other, Vec):
            return super().__mul__(other)
        raise TypeError(f'{self.__class__.__name__}, {other.__class__.__name__} mul unknown')

    def __truediv__(self, other):
        """
        ! primitive doesn't support value assignment

        :param other:
        :return: ! returns new primitive
        """
        if isinstance(self, Vec) and isinstance(other, Number):
            return super().__truediv__(other)
        elif isinstance(self, Vec) and isinstance(other, Vec):
            return super().__truediv__(other)
        raise TypeError(f'{self.__class__.__name__}, {other.__class__.__name__} div unknown')

    # all __i~__ return new object
    def __iadd__(self, other):
        """
        ! primitive doesn't support value assignment

        :param other:
        :return: ! returns new primitive
        """
        if isinstance(self, Vec):
            if isinstance(other, Vec):
                return self.__add__(other)
            elif isinstance(other, Pnt):
                return other.__add__(self)
        elif isinstance(self, Pnt):
            if isinstance(other, Vec):
                return self.__add__(other)
        raise ArithmeticError(f'{self.__class__.__name__}, {other.__class__.__name__} iadd unknown')

    def __isub__(self, other):
        """
        ! primitive doesn't support value assignment

        :param other:
        :return: ! returns new primitive
        """
        if isinstance(self, Vec):
            if isinstance(other, Vec):
                return super().__sub__(other)
        elif isinstance(self, Pnt):
            if isinstance(other, Pnt):
                return super().__sub__(other).view(Vec)
            elif isinstance(other, Vec):
                return super().__sub__(other)
        raise ArithmeticError(f'{self.__class__.__name__}, {other.__class__.__name__} isub unknown')

    def __imul__(self, other):
        """
        ! primitive doesn't support value assignment

        :param other:
        :return: ! returns new primitive
        """
        if isinstance(self, Vec) and isinstance(other, Number):
            return super().__mul__(other)
        raise TypeError(f'{self.__class__.__name__}, {other.__class__.__name__} imul unknown')

    def __itruediv__(self, other):
        """
        ! primitive doesn't support value assignment

        :param other:
        :return: ! returns new primitive
        """
        try:
            return super(Mat1, self).__truediv__(other)
        except:
            raise TypeError(f'{self.__class__.__name__}, {other.__class__.__name__} idiv unknown')


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
                         [1, 0]], dtype=DTYPE).view(cls)

    def __array_finalize__(self, obj):
        """
        to normalize ray normal

        :param obj:
        :return:
        """
        self[:, [1]] = Vec.normalize(self.normal)

    def __str__(self):
        return f"<Ray from {self.origin}>"

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
        :return: new Ray object
        """
        return cls(origin.xyz, normal.xyz)

    @classmethod
    def from_pnts(cls, s, e):
        """
        create new ray from two points

        :param s: origin of ray
        :param e: destination point which forms ray normal connected with origin
        :return: new Ray object
        """
        return Ray(s.xyz, (e - s).xyz)

    def as_vec(self):
        return self.normal

    def as_lin(self):
        """
        convert Ray into Line

        :return: Lin instance with length 1
        """
        return Lin.from_pnt_vec(self.origin, self.normal)

    def reverse(self):
        """
        reverse self: simply ray heading opposite direction

        :return:
        """
        self[:3, 1] = -self[:3, 1]
        return self


class Vec(Mat1, VecConv, PntConv):

    def __new__(cls, x=1, y=0, z=0):
        return np.array([[x],
                         [y],
                         [z],
                         [0]], dtype=DTYPE).view(cls)

    def __array_finalize__(self, obj):
        """
        :param obj:
        :atrib _is_new: flag for newly set. used to indicate when cache clean is needed.
        :atrib _length: length of vector
        :return:
        """
        self.__clean_cache = True
        self.__length = None
        self.__s = Pnt(0, 0, 0)

    def __str__(self):
        return f"<{self.__class__.__name__} : {[round(n, 3) for n in self[:3, 0]]}>"

    def __truediv__(self, other):
        """
        overridden to preserve w value of array

        :param other:
        :return:
        """
        obj = super().__truediv__(other)
        if isinstance(other, Number):
            obj[3, 0] = 0
        return obj

    def __setitem__(self, key, value):
        """
        overridden to indicate cache clean needed

        resetting all values with [:] doesn't work as a ndarray subclass
        seems like there need something to use templating.
        Anyway for now, just giving x, y, z, xyz setter instead.
        :param key:
        :param value:
        :return:
        """
        super().__setitem__(key, value)
        self.__clean_cache = True

    @property
    def vertices(self):
        self.__e = self.as_pnt()
        return self.__s, self.__e

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

    def normalize(self):
        """
        return normalized
        :return:
        """
        if self.is_zero():
            return self
        return self / self.length

    def amplify(self, magnitude):
        """
        return amplified of self

        :param magnitude:
        :return: copy of self amplified
        """
        return self.normalize() * magnitude

    def pnts_share_side(self, *pnts):
        """
        check if given points are on the same side

        :param pnts: points to be tested
        :return: bool or None - for odd result
        """
        # cant define sideness
        if np.isclose(0, self.length, atol=ATOL):
            return None

        rep = None
        s, e = self.vertices
        for pnt in pnts:
            if not isinstance(pnt, Pnt):
                raise TypeError(pnt)
            normal = Vec.cross(Vec.from_pnts(pnt, s), Vec.from_pnts(pnt, e))
            # odd case, point on the border
            if normal == 0:
                return None

            if rep is None:
                rep = normal
            else:
                if Vec.dot(rep, normal) < 0:
                    return False
        return True

    def is_zero(self):
        """
        boolean for self being zero vector
        :return:
        """
        return np.isclose(self, 0, atol=ATOL).all()

    def is_parallel_with(self, vec):
        """
        check if self is parallel with given vector
        :param vec:
        :return:
        """
        return True if Vec.cross(self, vec) == 0 else False

    def is_oposite_with(self, vec):
        """
        check if self is oposite with given vector
        :param vec:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def trnsf_to_x(cls, vec):
        """
        calculate transformation matrix for aligning self to axis x
        :return: compoud transformation matrix (TransfMats)
        """
        axis = Vec(1, 0, 0)
        if vec.is_parallel_with(axis):
            return TrnsfMats()
        v_on_zx = vec.project_on_yz()
        if v_on_zx == 0:
            ry = RotYMat(0)
        else:
            rot_dir = 1 if Vec.cross(v_on_zx, axis).y > 0 else -1  # to determine direction of rotation
            ry = RotYMat(Vec.angle_between(axis, v_on_zx) * rot_dir)

        v_on_xy = ry * vec
        if v_on_xy == 0:
            rz = RotZMat(0)
        else:
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
        v_on_yz = vec.project_on_yz()
        if v_on_yz == 0:
            rx = RotXMat(0)
        else:
            rot_dir = 1 if Vec.cross(v_on_yz, axis).x > 0 else -1  # to determine direction of rotation
            rx = RotXMat(Vec.angle_between(axis, v_on_yz) * rot_dir)

        v_on_xy = rx * vec
        if v_on_xy == 0:
            rz = RotZMat(0)
        else:
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
        v_on_yz = vec.project_on_yz()
        if v_on_yz == 0:
            rx = RotXMat(0)
        else:
            rot_dir = 1 if Vec.cross(v_on_yz, axis).x > 0 else -1  # to determine direction of rotation
            rx = RotXMat(Vec.angle_between(axis, v_on_yz) * rot_dir)

        v_on_zx = rx * vec
        if v_on_zx == 0:
            ry = RotYMat(0)
        else:
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

    def __projected_on(self, plane):
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

    def project_on_xy(self):
        """
        vector projected on xy plane
        :return: copy of projected self
        """
        return self.__projected_on('xy')

    def project_on_yz(self):
        """
        vector projected on yz plane
        :return: copy of projected self
        """
        return self.__projected_on('yz')

    def project_on_zx(self):
        """
        vector projected on zx plane
        :return: copy of projected self
        """
        return self.__projected_on('zx')

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
        return self.view(Vec)

    def as_pnt(self):
        return Pnt(*self.xyz)

    def as_lin(self):
        return Lin(s=(0, 0, 0), e=self.xyz)


class Pnt(Mat1, VecConv, PntConv):
    """
    Point
    """

    def __new__(cls, x=0, y=0, z=0):
        obj = super().__new__(cls, shape=(4, 1), dtype=DTYPE)
        obj[:, 0] = x, y, z, 1
        return obj

    def __str__(self):
        return f"<Pnt : {[round(n, 3) for n in self[:3, 0]]}>"

    def __repr__(self):
        return self.__str__()

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


class _NamedVec(Vec):
    """
    Named vector: special vectors
    """

    def __setitem__(self, key, value):
        """
        deny value modification as a special vector, presumably, wont need any change

        this method should never be called
        :param key:
        :param value:
        :return:
        """
        raise ValueError('Named Vector dosnt accept modification')

    """
    simply cast current into common class Vec
    view is safe as calculation will yield new object always
    this formatting may be dealt inside Vec's arithmetic magic methods but think this way is closer to OPP concept 
    """

    def __array_prepare__(self, out, context):
        """
        need for preventing __i~__ methods assigning updated values into self

        no need to view as Vec as it is impossible to control arithmetic output of Vec
        without overriding all function. Yet this function simply copies the output when needed
        and tosses the responsibility for returning Vec object to __array_wrap__
        :param out:
        :param context:
        :return:
        """
        if isinstance(out, self.__class__):
            return np.array(out)
        return out

    def __array_wrap__(self, obj, context):
        """
        to cast all calculation result into Vec

        chained with __array_prepare__ return resulted as primitive Vec instance
        :param obj:
        :param context:
        :return:
        """
        return obj.view(Vec)


@Singleton
class ZeroVec(_NamedVec):
    """
    Zero Vector
    """

    def __new__(cls):
        return super().__new__(cls, 0, 0, 0)


@Singleton
class XVec(_NamedVec):
    """
    x unit vector
    """

    def __new__(cls):
        return super().__new__(cls, 1, 0, 0)


@Singleton
class YVec(_NamedVec):
    """
    y unit vector
    """

    def __new__(cls):
        return super().__new__(cls, 0, 1, 0)


@Singleton
class ZVec(_NamedVec):
    """
    z unit vector
    """

    def __new__(cls):
        return super().__new__(cls, 0, 0, 1)


class _AsVec(Vec):
    """
    vector wrapper that represents special characteristics
    """

    def __new__(cls, vec_like):
        return vec_like.as_vec().view(cls)


class Xax(_AsVec):
    """
    Vector as x axis
    """


class Yax(_AsVec):
    """
    Vector as y axis
    """


class Zax(_AsVec):
    """
    Vector as z axis
    """


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
        obj = super().__new__(cls, shape=(4, 4), dtype=DTYPE)
        obj[:3, (0, 1, 2, 3)] = np.array([o, x, y, z]).T
        obj[3] = 1, 0, 0, 0
        obj.__normalize()
        return obj

    def __normalize(self):
        """
        standarization? of plane

        1. Make vectors perpendicular, normalized and
        2. create transformation matrix into plane space
        !vectors are made perpendicular by referencing vectors in xyz order!
        :param arr: array in np.ndarray type
        :return:
        """
        if (self.view(np.ndarray) == [[0, 1, 0, 0],
                                      [0, 0, 1, 0],
                                      [0, 0, 0, 1],
                                      [1, 0, 0, 0]]).all():
            # unit plane transformation matrix equals to eye(4) matrix
            self._trnsf_mat = TrnsfMats()
            return
        # make vectors normalized and perpendicular
        x, y = self.axis_x, self.axis_y

        if Vec.cross(x, y) == 0:
            raise ValueError('cant define plane with parallel axes')
        z = Vec.cross(x, y)  # find z
        y = Vec.cross(z, x)  # find y
        x, y, z = [v.normalize() for v in (x, y, z)]
        self[:, 1:] = np.array([x, y, z]).T
        # calculate 'plane to origin' rotation matrices
        # last rotation is of x so match axis x to unit x prior
        plane = np.array([[0, x.x, y.x, z.x],
                          [0, x.y, y.y, z.y],
                          [0, x.z, y.z, z.z],
                          [1, 0, 0, 0]], dtype=DTYPE)
        x_on_xy = x.project_on_xy()
        dir_vec = Vec.cross(XVec(), x_on_xy)
        if dir_vec.is_zero():
            if Vec.dot(XVec(), x_on_xy) < 0:
                rot_dir = 1
            else:
                rot_dir = 0
        elif dir_vec.z > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        rz = RotZMat(Vec.angle_between(Vec(1, 0, 0), x_on_xy) * rot_dir)

        plane = rz * plane
        x_on_zx = Vec(*plane[:3, 1])
        dir_vec = Vec.cross(XVec(), x_on_zx)
        if dir_vec.is_zero():
            if Vec.dot(XVec(), x_on_zx) < 0:
                rot_dir = 1
            else:
                rot_dir = 0
        elif dir_vec.y > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        ry = RotYMat(Vec.angle_between(Vec(1, 0, 0), x_on_zx) * rot_dir)

        # axis x is aligned so lastly match axis y
        plane = ry * plane
        y_on_yz = Vec(*plane[:3, 2])
        dir_vec = Vec.cross(YVec(), y_on_yz)
        if dir_vec.is_zero():  # parallel, need opposite checking
            if Vec.dot(YVec(), y_on_yz) < 0:  # opposite
                rot_dir = 1
            else:
                rot_dir = 0
        elif dir_vec.x > 0:
            rot_dir = -1
        else:
            rot_dir = 1
        rx = RotXMat(Vec.angle_between(YVec(), y_on_yz) * rot_dir)

        to_origin = MoveMat(*(-self.origin).xyz)

        # found 'plane to origin' so 'origin to plane' is inverse of it
        self._trnsf_mat = TrnsfMats([to_origin, rz, ry, rx]).I

    def __array_finalize__(self, obj):
        """

        :return:
        """
        if obj is None:
            return
        """
        dont know when this can happen:
        1.  happens when copying plane:
            Somehow copy() internally circumvents Pln.__new__ and creates Pln with eye(4) value 
        """

        if isinstance(obj, self.__class__):
            self[:] = obj
            self.__normalize()
        elif isinstance(obj, np.ndarray):
            # self already has resulting value, need to check array correctness
            if self.validate_array(self):
                self.__normalize()
            else:
                raise ValueError('given is not Pln-like')
        else:
            raise

    @classmethod
    def validate_array(cls, arr):
        """
        check if raw array is Pln like

        :param arr: np.ndarray or 2D list
        :return:
        """
        if isinstance(arr, (tuple, list)):
            arr = np.array(arr)

        if isinstance(arr, np.ndarray) and arr.shape == (4, 4) and (arr[3] == (1, 0, 0, 0)).all():
            return True
        return False

    def orient(self, obj, ref_pln):
        """
        orient given geometric object to this plane

        :param obj:
        :param ref_pln: Pln, reference plane
        :return:
        """
        pln = self.TM * ref_pln
        return pln.TM * obj

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
    def axes(self):
        return self.axis_x, self.axis_y, self.axis_z

    @property
    def components(self):
        return self.origin, self.axis_x, self.axis_y, self.axis_z

    @property
    def TM(self):
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
            o, x = line.vertices
            x = x - o
            y = point - o

            return Pln.from_ori_axies(o, x, y, ZVec())
        else:
            raise NotImplementedError

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

    def lin_is_on(self, lin):
        """
        check if given line is on the plane
        :param lin:
        :return:
        """
        norm = self.axis_z
        if Vec.dot(norm, lin.start) == 0 and Vec.dot(norm, lin.end) == 0:
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
        return abs(Vec.dot(self.axis_z, point.as_vec()) / self.axis_z.length)

    def pnt_shortest(self, point):
        """
        find closest point to plane

        :param point: Pnt to drop from
        :return: Pnt on Pln
        """
        d = Vec.dot(self.axis_z, point.as_vec()) / self.axis_z.length
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
        obj = super().__new__(cls, shape=(4, 3), dtype=DTYPE)
        obj[:] = [[v0[0], v1[0], v2[0]],
                  [v0[1], v1[1], v2[1]],
                  [v0[2], v1[2], v2[2]],
                  [1, 1, 1]]
        return obj

    @property
    def v0(self):
        """
        vertex 0
        :return:
        """
        return Pnt(*self[:3, 0])

    @property
    def v1(self):
        """
        vertex 1
        :return:
        """
        return Pnt(*self[:3, 1])

    @property
    def v2(self):
        """
        vertex 2
        :return:
        """
        return Pnt(*self[:3, 2])

    @property
    def vertices(self):
        return self.v0, self.v1, self.v2

    @property
    def normal(self):
        return Vec.cross(self.v1 - self.v0, self.v2 - self.v0)

    @property
    def pln(self):
        return Pln.from_lin_pnt(Lin.from_pnts(self.v0, self.v1), self.v2)

    @property
    def centroid(self):
        """
        average of vertices
        :return:
        """
        return Pnt.from_row(np.dot(self, [[1], [1], [1]]) / 3)

    def __str__(self):
        """
        triangle described by centroid
        :return:
        """
        return f"<Tgl {self.centroid}>"

    def reverse(self):
        """
        reverse self's vertices

        :return: self
        """
        self[:, (1, 2)] = self[:, (2, 1)]
        return self

    @classmethod
    def from_pnts(cls, v0, v1, v2):
        """
        create triangle by vertices

        :param v0:
        :param v1:
        :param v2:
        :return:
        """
        return cls(*[v.xyz for v in (v0, v1, v2)])


class Lin(ArrayLikeData, VecConv):

    def __new__(cls, s=(0, 0, 0), e=(0, 0, 1)):
        """
        define line from two coordinate
        :param s: xyz coord of starting vertex
        :param e: xyz coord of ending vertex
        """
        cls.validate_3d_coordinate(s, e)
        obj = super().__new__(cls, shape=(4, 2), dtype=DTYPE)
        obj[:3, 0] = s
        obj[:3, 1] = e
        obj[3] = 1, 1

        obj.__s = None
        obj.__e = None
        return obj

    def __bool__(self):
        """

        :return:
        """
        return self.length != 0

    def __str__(self):
        return f"<Lin,{self.length}>"

    @classmethod
    def from_pnts(cls, s: Pnt, e: Pnt):
        """
        create line using start, end vertex
        :param s: starting vertex of line
        :param e: ending vertex of line
        :return:
        """
        obj = Lin(s.xyz, e.xyz)
        # to maintain interior consistency
        setattr(obj, f"_{cls.__name__}__s", s)
        setattr(obj, f"_{cls.__name__}__e", e)
        return obj

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

    @lazyProp
    def length(self):
        """
        of line
        :return:
        """
        summed = 0
        for i in range(3):
            summed += pow(self[i, 0] - self[i, 1], 2)
        return sqrt(summed)

    @lazyProp
    def start(self):
        self.__s = Pnt(*self[:3, 0])
        return self.__s

    @lazyProp
    def end(self):
        self.__e = Pnt(*self[:3, 1])
        return self.__e

    @property
    def vertices(self):
        return self.start, self.end

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

    def pnt_at(self, t):
        """
        return Point at parameter t

        :param t: in between 0(start), 1(end). is compatible values under, above (0, 1)
        :return:
        """
        if not isinstance(t, Number):
            raise

        return self.start + self.as_vec() * t

    def as_vec(self):
        return self.end - self.start

    def as_lin(self):
        return self

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

    def pnts_share_side(self, *pnts):
        """
        check if given points are on the same side

        :param pnts: points to be tested
        :return: bool or None - for odd result
        """
        # cant define sideness
        if np.isclose(0, self.length, atol=ATOL):
            return None

        rep = None
        s, e = self.vertices
        for pnt in pnts:
            if not isinstance(pnt, Pnt):
                raise TypeError(pnt)
            normal = Vec.cross(Vec.from_pnts(pnt, s), Vec.from_pnts(pnt, e))
            # odd case, point on the border
            if normal == 0:
                return None

            if rep is None:
                rep = normal
            else:
                if Vec.dot(rep, normal) < 0:
                    return False
        return True

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
