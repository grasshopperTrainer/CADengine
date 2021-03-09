from numbers import Number

import numpy as np

from gkernel.dtype.nongeometric.matrix import ViewMatrix, ProjectionMatrix, MoveMat, TrnsfMats, RotZMat
from gkernel.dtype.geometric import Vec, Pln
from global_tools.singleton import Singleton


class CameraTripod:
    """
    Camera property defining camera orientaiton;

    including camera position and camera direction combined within camera_plane
    """

    def __init__(self):
        self.__pln = Pln()

    @property
    def plane(self):
        return self.__pln

    @plane.setter
    def plane(self, p):
        if not isinstance(p, Pln):
            raise
        self.__pln = p

    @property
    def VM(self):
        """
        veiw matrix

        :return:
        """
        return ViewMatrix.from_pln(self.__pln)

    def lookat(self, eye, at, up):
        """
        move plane to look at from eye

        :param eye: to look from
        :param at: to look at
        :param up: direction of camera up
        :return:
        """
        if all(isinstance(i, tuple) for i in (eye, at, up)):
            eye = Vec(*eye)
            at = Vec(*at)
            up = Vec(*up)
        else:
            raise NotImplementedError
        # calculate plane
        zaxis = at - eye  # vector from eye to at
        zaxis /= zaxis.length  # normalize
        xaxis = Vec.cross(zaxis, up)  # find perpendicular of z and up(y) -> x
        xaxis /= xaxis.length  # normalize
        yaxis = Vec.cross(xaxis, zaxis)  # find true up
        zaxis *= -1  # reverse z
        self.__pln = Pln.from_ori_axies(eye, xaxis, yaxis, zaxis)

    def rotate_around(self, axis, rad):
        """
        rotate along given axis

        :param axis: to rotate along
        :param rad: radian value to rotate
        :return:
        """
        # 1. MoveMat of camera to world origin
        # 2. RotMat of axis to world z
        # 3. RotZMat of given rad
        # 4. apply inverse of 1->2 to resulted plane of 3
        axis = axis.as_lin()
        axis_o, axis_v = axis.start, axis.as_vec()
        axis_to_z = TrnsfMats([MoveMat(*(-axis_o).xyz), Vec.trnsf_to_z(axis_v)])
        self.__pln = axis_to_z.I * RotZMat(rad) * axis_to_z * self.__pln

    def yaw(self, rad):
        """
        rotate along y axis
        :return:
        """
        origin, camerax, cameray, cameraz = self.plane.components
        new_x = camerax.copy().amplify(np.cos(rad)) + cameraz.copy().amplify(np.sin(rad))
        new_z = Vec.cross(cameray, new_x)
        self.__pln = Pln(origin.xyz, new_x.xyz, cameray.xyz, new_z.xyz)

    def pitch(self, rad):
        """
        rotate along x axis
        :return:
        """
        origin, camerax, cameray, cameraz = self.plane.components
        new_y = cameray.copy().amplify(np.cos(rad)) + cameraz.copy().amplify(np.sin(rad))
        new_z = Vec.cross(camerax, new_y)
        self.__pln = Pln(origin.xyz, camerax.xyz, new_y.xyz, new_z.xyz)

    def roll(self, rad):
        """
        rotate along z axis
        :return:
        """
        raise NotImplementedError

    def move_local(self, pv):
        """
        move camera along its plane

        :param pv: panning vector, z will be ignored
        :return:
        """
        x, y, z = (v.amplify(amp) for v, amp in zip(self.__pln.axes, (-pv).xyz))
        self.move(x + y + z)

    def orbit(self):
        raise NotImplementedError

    def zoom(self):
        raise NotImplementedError

    def move(self, vec: Vec):
        """
        Move camera using vector
        :return:
        """
        tm = MoveMat(*vec.xyz)
        self.__pln = tm * self.__pln

    def orient(self, pos):
        """
        position camera to given position
        :param pos:
        :return:
        """
        raise NotImplementedError


class CameraBody:
    """
    Defines frustum shape.
    """

    def __init__(self, l, r, b, t, n, f, fshape: str):
        self.__dim = dict(zip('lrbtnf', (l, r, b, t, n, f)))
        if fshape not in ('o', 'p'):
            raise ValueError('frustum shape has to be one on (o:orthogonal, p:perspective)')
        self.__fshape = fshape  # frustum shape

    @property
    def PM(self):
        """
        projection matrix

        :return:
        """
        return ProjectionMatrix(*self.dim, self.__fshape)

    @property
    def hfov(self):
        """
        horizontal field of view

        :return:
        """
        h = self.__dim['n']
        l, r = self.__dim['l'], self.__dim['r']
        la = np.arccos(h / np.sqrt(h ** 2 + l ** 2))
        ra = np.arccos(h / np.sqrt(h ** 2 + r ** 2))
        return la + ra

    @property
    def vfov(self):
        """
        vertical field of view

        :return:
        """
        h = self.__dim['n']
        b, t = self.__dim['b'], self.__dim['t']
        ba = np.arccos(h / np.sqrt(h ** 2 + b ** 2))
        ta = np.arccos(h / np.sqrt(h ** 2 + t ** 2))
        return ba + ta

    @property
    def aspect_ratio(self):
        """
        ratio of width / height

        ! expression like 16:9
        :return:
        """
        l, r, b, t = (self.__dim[k] for k in 'lrbt')
        return (r - l) / (t - b)

    @property
    def near(self):
        return self.__dim['n']

    @property
    def far(self):
        return self.__dim['f']

    @property
    def dim(self):
        """
        return frustrum dimension
        :return:
        """
        return tuple(self.__dim[k] for k in 'lrbtnf')

    @dim.setter
    def dim(self, lrbtnf):
        if len(lrbtnf) != 6:
            raise ValueError('all 6 values of left right bottom top near far has to be given')
        for k, v in zip('lrbtnf', lrbtnf):
            if not isinstance(v, Number):
                raise TypeError
            self.__dim[k] = v

    @property
    def fshape(self):
        """
        frustum shape either 'o'(orthogonal) or 'p'(perspective)

        :return:
        """
        return self.__fshape
