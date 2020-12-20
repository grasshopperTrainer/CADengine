from JINTFP import *
from gkernel.dtype.nongeometric.matrix import MoveMat, RotXMat, RotYMat, RotZMat, TrnsfMats
from gkernel.dtype.geometric.primitive import Pln, Vec
from my_patterns import Singleton


class CameraNode(NodeBody):
    """
    Node related to camera
    """
    pass


class _CameraBodyBuilder(CameraNode):
    """
    Define camera body properties from given attribute
    """

    left = Output()
    right = Output()
    bottom = Output()
    top = Output()
    near = Output()
    far = Output()

    hfov = Output()
    vfov = Output()
    aspect_ratio = Output()


class FovCamera(_CameraBodyBuilder):
    """
    Camera defined by:

    horizontal field of view(hfov)
    distance of near far plane
    ratio of width/height of near cliping plane
    """
    hfov = Input()
    near = Input()
    far = Input()
    aspect_ratio = Input()

    def calculate(self, hfov, near, far, ratio):
        r = near * np.tan(hfov / 2)
        l = -r
        t = r / ratio
        b = -t
        vfov = 2 * np.arctan(np.tan(hfov / 2) / ratio)
        return l, r, b, t, near, far, hfov, vfov, ratio


class LrbtCamera(_CameraBodyBuilder):
    """
    Camera defined by:

    Left, Right, Bottom, Top and near, far
    """
    in0_left = Input()
    in1_right = Input()
    in2_bottom = Input()
    in3_top = Input()
    in4_near = Input()
    in5_far = Input()

    def calculate(self, l, r, b, t, n, f):
        hfov = np.arcsin(r / np.sqrt(r ** 2 + n ** 2))
        ratio = r / t
        vfov = 2 * np.arctan(np.tan(hfov / 2) / ratio)

        return l, r, b, t, n, f, hfov, vfov, ratio


class _FrustumShape(CameraNode):
    """
    Projection matrix calculator
    """
    in0_left = Input()
    in1_right = Input()
    in2_bottom = Input()
    in3_top = Input()
    in4_near = Input()
    in5_far = Input()

    out0_matrix = Output()


class OrthFrustum(_FrustumShape):
    """
    Orthogonal projection matrix calculator
    """

    def calculate(self, l, r, b, t, n, f):
        proj_mat = np.eye(4)
        if l == -r and b == -t:
            proj_mat[0, 0] = 1 / r
            proj_mat[1, 1] = 1 / t
            proj_mat[2, (2, 3)] = -2 / (f - n), -(f + n) / (f - n)
            proj_mat[3] = 0, 0, 0, 1
        else:
            proj_mat[0, (0, 3)] = 2 / (r - l), -(r + l) / (r - l)
            proj_mat[1, (1, 3)] = 2 / (t - b), -(t + b) / (t - b)
            proj_mat[2, (2, 3)] = -2 / (f - n), -(f + n) / (f - n)
            proj_mat[3] = 0, 0, 0, 1

        return proj_mat


class PrspFrustum(_FrustumShape):
    """
    Perspective projection matrix calculator
    """

    def calculate(self, l, r, b, t, n, f):
        proj_mat = np.eye(4)
        if l == -r and b == -t:
            proj_mat[0, 0] = n / r
            proj_mat[1, 1] = n / t
            proj_mat[2, (2, 3)] = -(f + n) / (f - n), -2 * f * n / (f - n)
            proj_mat[3] = 0, 0, -1, 0
        else:
            proj_mat[0, (0, 2)] = 2 * n / (r - l), (r + l) / (r - l)
            proj_mat[1, (1, 2)] = 2 * n / (t - b), (t + b) / (t - b)
            proj_mat[2, (2, 3)] = -(f + n) / (f - n), -2 * f * n / (f - n)
            proj_mat[3] = 0, 0, -1, 0
        return proj_mat


class CameraBody(CameraNode):
    """
    Defines viewing shape.
    """
    left = Output()
    right = Output()
    bottom = Output()
    top = Output()
    near = Output()
    far = Output()

    hfov = Output()
    vfov = Output()
    aspect_ratio = Output()

    PM = Output()

    def __init__(self, body_builder: _CameraBodyBuilder, frustrum_shape: _FrustumShape):
        super().__init__()
        # incase two are not connected
        frustrum_shape.left = body_builder.left
        frustrum_shape.right = body_builder.right
        frustrum_shape.bottom = body_builder.bottom
        frustrum_shape.top = body_builder.top
        frustrum_shape.near = body_builder.near
        frustrum_shape.far = body_builder.far

        self._body_builder = body_builder
        self._frustum_shape = frustrum_shape

    def calculate(self):
        return *self._body_builder.output_values, self._frustum_shape.out0_matrix

    @property
    def builder(self):
        return self._body_builder

    @property
    def dim(self):
        """
        return frustrum dimension
        :return:
        """
        return self.left.r, self.right.r, self.bottom.r, self.top.r, self.near.r, self.far.r


class CameraTripod(CameraNode):
    """
    Camera property defining camera orientaiton;

    including camera position and camera direction combined within camera_plane
    """
    in_plane = Input(def_val=Pln())

    out_plane = Output()
    VM = Output()

    def __init__(self):
        super().__init__()

    def calculate(self, pln):
        return pln, self._calc_vm(pln)

    def _calc_vm(self, pln):
        """
        Calculate view matrix from self._camera_plane
        :return:
        """
        eye, xaxis, yaxis, zaxis = pln.components
        # calculate view_mat
        # cant explain calculation, scrapped from internet
        matrix = np.eye(4)
        matrix[0, :3] = xaxis.xyz
        matrix[1, :3] = yaxis.xyz
        matrix[2, :3] = zaxis.xyz
        matrix[:3, 3] = Vec.dot(-xaxis,eye), Vec.dot(-yaxis, eye), Vec.dot(-zaxis, eye)
        return matrix

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
        zaxis = at - eye                # vector from eye to at
        zaxis /= zaxis.length    # normalize
        xaxis = Vec.cross(zaxis, up)         # find perpendicular of z and up(y) -> x
        xaxis /= xaxis.length    # normalize
        yaxis = Vec.cross(xaxis, zaxis)      # find true up
        zaxis *= -1                     # reverse z
        self.in_plane = Pln.from_components(eye, xaxis, yaxis, zaxis)

    def rotate_along(self, axis: Vec, rad):
        """
        rotate along given axis

        :param axis:
        :param rad:
        :return:
        """
        # 1. MoveMat of camera to world origin
        # 2. RotMat of axis to world z
        # 3. RotZMat of given rad
        # 4. apply inverse of 1->2 to resulted plane of 3
        origin = self.in_plane.r.origin
        to_origin = MoveMat(*(-origin).xyz)
        axis.vec.trnsf_to_z
        self.in_plane = to_origin.I * RotZMat(rad) * to_origin * self.in_plane.r

    def yaw(self, rad):
        """
        rotate along y axis
        :return:
        """
        origin, camerax, cameray, cameraz = self.in_plane.r.components
        new_x = camerax.amplify(np.cos(rad), copy=True) + cameraz.amplify(np.sin(rad), copy=True)
        new_z = cameray.cross(new_x)
        self.in_plane = Pln(origin.xyz, new_x.xyz, cameray.xyz, new_z.xyz)

    def pitch(self, rad):
        """
        rotate along x axis
        :return:
        """
        origin, camerax, cameray, cameraz = self.in_plane.r.components
        new_y = cameray.amplify(np.cos(rad), copy=True) + cameraz.amplify(np.sin(rad), copy=True)
        new_z = Vec.cross(camerax, new_y)
        self.in_plane = Pln(origin.xyz, camerax.xyz, new_y.xyz, new_z.xyz)

    def roll(self, rad):
        """
        rotate along z axis
        :return:
        """
        raise NotImplementedError

    def move(self, vec: Vec):
        """
        Move camera using vector
        :return:
        """
        tm = MoveMat(*vec.xyz)
        self.in_plane = tm*self.in0_plane.r

    def move_along_axis(self, axis, magnitude):
        """
        Move camera using camera plane's axis
        :param axis:
        :return:
        """
        axis = self.in0_plane.r.components[{'x':1, 'y':2, 'z':3}[axis]]
        axis.amplify(magnitude)
        tm = MoveMat(*axis.xyz)
        self.in_plane = tm*self.in0_plane.r

    def orient(self, pos):
        """
        position camera to given position
        :param pos:
        :return:
        """

    @property
    def plane(self):
        return self.out_plane

@Singleton
class GetCurrentCamera(CameraNode):
    in0_current_camera = Input()

    body_left = Output()
    body_right = Output()
    body_bottom = Output()
    body_top = Output()
    body_near = Output()
    body_far = Output()
    body_hfov = Output()
    body_vfov = Output()
    body_aspect_ratio = Output()
    body_PM = Output()

    tripod_plane = Output()
    tripod_VM = Output()

    def __init__(self):
        super().__init__()
        self.in0_current_camera = CameraCurrentStack().out0_current_camera

    def calculate(self, camera):
        return *camera.body.output_values, *camera.tripod.output_values


@Singleton
class CameraCurrentStack(CameraNode):
    _current_stack = []
    out0_current_camera = Output()

    def __init__(self):
        super().__init__()

    def calculate(self):
        if self._current_stack:
            return self._current_stack[-1]
        return None

    def append(self, cam):
        self._current_stack.append(cam)
        self.refresh()

    def pop(self):
        self._current_stack.pop()
        self.refresh()
