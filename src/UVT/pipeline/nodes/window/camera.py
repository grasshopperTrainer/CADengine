from noding import *
from GeomKernel.dataTypes import *


class CameraNode(NodeBody):
    """
    Node related to camera
    """
    pass


class _CameraBodyBuilder(CameraNode):
    """
    Define camera body properties from given attribute
    """

    out0_left = Output()
    out1_right = Output()
    out2_bottom = Output()
    out3_top = Output()
    out4_near = Output()
    out5_far = Output()

    out6_hfov = Output()
    out7_vfov = Output()
    out8_aspect_ratio = Output()


class FovCamera(_CameraBodyBuilder):
    """
    Camera defined by:

    horizontal field of view(hfov)
    distance of near far plane
    ratio of width/height of near cliping plane
    """
    in0_hfov = Input()
    in1_near = Input()
    in2_far = Input()
    in3_ratio = Input()

    def calculate(self, hfov, near, far, ratio, typ, input_degree=True):
        r = near * np.tan(np.radians(hfov) / 2)
        l = -r
        t = r / ratio
        b = -t

        hfov = np.radians(hfov) if input_degree else hfov
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
        hfov = np.arcsin(r/np.sqrt(r**2+n**2))
        ratio = r/t
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
            proj_mat[2, (2, 3)] = -2/(f-n), -(f+n)/(f-n)
            proj_mat[3] = 0, 0, 0, 1
        else:
            proj_mat[0, (0, 3)] = 2 / (r-l), -(r+l)/(r-l)
            proj_mat[1, (1, 3)] = 2 / (t-b), -(t+b)/(t-b)
            proj_mat[2, (2, 3)] = -2/(f-n), -(f+n)/(f-n)
            proj_mat[3] = 0, 0, 0, 1
        return proj_mat


class PrspFrustum(_FrustumShape):
    """
    Perspective projection matrix calculator
    """

    def calculate(self, l, r, b, t, n, f):
        proj_mat = np.eye(4)
        if l == -r and b == -t:
            proj_mat[0, 0] = n/r
            proj_mat[1, 1] = n/t
            proj_mat[2, (2, 3)] = -(f+n)/(f-n), -2*f*n/(f-n)
            proj_mat[3] = 0, 0, -1, 0
        else:
            proj_mat[0, (0, 2)] = 2*n/(r-l), (r+l)/(r-l)
            proj_mat[1, (1, 2)] = 2*n/(t-b), (t+b)/(t-b)
            proj_mat[2, (2, 3)] = -(f+n)/(f-n), -2*f*n/(f-n)
            proj_mat[3] = 0, 0, -1, 0
        return proj_mat

class CameraBody(CameraNode):
    out0_left = Output()
    out1_right = Output()
    out2_bottom = Output()
    out3_top = Output()
    out4_near = Output()
    out5_far = Output()

    out6_hfov = Output()
    out7_vfov = Output()
    out8_aspect_ratio = Output()

    out9_PM = Output()

    def __init__(self, body_builder:_CameraBodyBuilder, frustrum_shape:_FrustumShape):
        super().__init__()
        # incase two are not connected
        frustrum_shape.in0_left = body_builder.out0_left
        frustrum_shape.in1_right = body_builder.out1_right
        frustrum_shape.in2_bottom = body_builder.out2_bottom
        frustrum_shape.in3_top = body_builder.out3_top
        frustrum_shape.in4_near = body_builder.out4_near
        frustrum_shape.in5_far = body_builder.out5_far

        self._body_builder = body_builder
        self._frustum_shape = frustrum_shape

    def calculate(self):
        return *self._body_builder.output_values, self._frustum_shape.out0_matrix

    @property
    def builder(self):
        return self._body_builder


class CameraTripod(CameraNode):
    """
    Camera property defining camera orientaiton;

    including camera position and camera direction combined in camera_plane
    """
    out0_plane = Output()
    out1_VM = Output()
    def __init__(self):
        super().__init__()
        self._plane = Plane()

    def calculate(self):
        return self._plane, self._calc_vm()

    def _calc_vm(self):
        """
        Calculate view matrix from self._camera_plane
        :return:
        """
        eye, xaxis, yaxis, zaxis = self._plane.components

        # calculate view_mat
        matrix = np.eye(4)
        matrix[0, :3] = xaxis._data.flatten()[:3]
        matrix[1, :3] = yaxis._data.flatten()[:3]
        matrix[2, :3] = zaxis._data.flatten()[:3]
        matrix[:3, 3] = -xaxis * eye, -yaxis * eye, -zaxis * eye
        return matrix

    def lookat(self, eye, at, up):
        if all(isinstance(i, tuple) for i in (eye, at, up)):
            eye = Vector(*eye)
            at = Vector(*at)
            up = Vector(*up)
        else:
            raise NotImplementedError
        # calculate plane
        zaxis = at - eye
        zaxis = zaxis / np.linalg.norm(zaxis)
        xaxis = zaxis.cross(up)
        xaxis = xaxis / np.linalg.norm(xaxis)
        yaxis = xaxis.cross(zaxis)
        zaxis *= -1
        self._plane = Plane.from_vectors(eye, xaxis,yaxis,zaxis)


    def yaw(self):
        """
        rotate along y axis
        :return:
        """

    def pitch(self):
        """
        rotate along x axis
        :return:
        """

    def roll(self):
        """
        rotate along z axis
        :return:
        """
        pass

    def move(self, vec):
        """
        Move camera using vector
        :return:
        """

    def orient(self, pos):
        """
        position camera to given position
        :param pos:
        :return:
        """

