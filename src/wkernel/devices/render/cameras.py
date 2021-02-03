from gkernel.dtype.geometric.primitive import Pnt, Lin, Ray, ZeroVec, ZVec
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat
from ._base import *
from wkernel.pipeline.nodes.window.camera import *


class Dolly:
    """
    Dolly parent
    """
    pass


class FpsDolly(Dolly):

    def __init__(self):
        self.move_speed = 10
        self.view_speed = 0.01
        # should it be at upper?

        self._last_cursor_pos = None

    def callbacked_move_tripod(self, keyboard, tripod, **kwargs):
        """
        move tripod

        callback intended to be used with window per frame callback
        :param keyboard:
        :param tripod:
        :param kwargs: to accept args provided by glfw key callback handler if registered in it
        :return:
        """
        # left right back forward create delta vector
        x, y, z = tripod.in_plane.r.axes
        dvec = ZeroVec()
        for c, v in zip(('a', 's', 'd', 'w', 'e', 'q'), (-x, z, x, -z, ZVec(), -ZVec())):
            if keyboard.get_key_status(c)[0]:
                dvec += v

        dvec.as_vec().amplify(self.move_speed)
        tripod.move(dvec)

    def callbacked_move_camera(self, window, xpos, ypos, mouse, tripod):
        """
        move camera frustum with cursor move

        :param window:
        :param xpos:
        :param ypos:
        :param mouse:
        :return:
        """
        v = Vec.from_pnts(Pnt(*mouse.cursor_center()), Pnt(xpos, ypos)) * self.view_speed  # cursor delta
        # rotate vertically and horizontally
        if abs(v.y) > 0.01:
            tripod.pitch(v.y)
        if abs(v.x) > 0.01:
            axis = Lin.from_pnt_vec(tripod.in_plane.r.origin, Vec(0, 0, 1))
            tripod.rotate_along(axis, -v.x)

        mouse.cursor_goto_center()


class Camera(RenderDevice):
    """
    Camera

    Camera consists of Two parts; camera body, camera orientation(position)
    """

    def __init__(self, body: CameraBody, tripod: CameraTripod, manager):
        super().__init__(manager)

        self._body = body
        self._tripod = tripod
        self._dolly = None

    @property
    def body(self) -> CameraBody:
        return self._body

    @property
    def tripod(self) -> CameraTripod:
        return self._tripod

    @property
    def dolly(self):
        return self._dolly

    def attach_dolly(self, dolly):
        """
        Assign dolly
        :param dolly:
        :return:
        """
        if not isinstance(dolly, Dolly):
            raise TypeError
        self._dolly = dolly

    def detach_dolly(self):
        """
        Remove dolly

        :return: dolly for manager to handle callback detachment
        """
        if self._dolly is None:
            raise ValueError('no dolly to detach')
        d = self._dolly
        self._dolly = None
        return d

    def frusrum_ray(self, param_x, param_y):
        """
        return ray crossing near frustum at given param

        param 0,0 points at the center of frustum
        :param param_x: in domain(-1.0, 1.0)
        :param param_y: in domain(-1.0, 1.0)
        :return:
        """
        l, r, b, t, n, f = self.body.dim
        # convert normalized into near frustum space
        sm = ScaleMat(x=r - l, y=t - b)
        mm = MoveMat(x=(r + l) / 2, y=(t + b) / 2, z=-n)
        offset = MoveMat(-.5, -.5)  # to compensate origin difference between OpenGL space and pane space
        frustum_point = mm * sm * offset * Pnt(x=param_x, y=param_y, z=0)
        ray = Ray([0, 0, 0], frustum_point.xyz)
        return self.tripod.in_plane.r.TM * ray


class CameraManager(RenderDeviceManager):

    def __init__(self, device_master):
        super().__init__(device_master)
        r, t = self.window.glyph.width.r / 2, self.window.glyph.height.r / 2

        # meta_entities
        self.__perspective_fac = CameraFactory(self)

        # self.append_new_orthogonal(-r, r, -t, t, 1, 10000)
        self.factory.prsp_from_hfov(hfov=np.radians(50),
                                    ratio=self.window.glyph.aspect_ratio,
                                    near=0.1,
                                    far=10000)

    @property
    def device_type(self):
        return Camera

    @property
    def factory(self):
        return self.__perspective_fac

    # TODO: need camera dolly connector? should it take all the responsibilities? who has to know about dolly?
    def attach_fps_dolly(self, camera_id):
        """
        attach dolly to the camera

        :param camera_id:
        :return:
        """
        camera = self[camera_id]
        dolly = FpsDolly()
        camera.attach_dolly(dolly)
        # handling callback
        self.window.append_predraw_callback(dolly.callbacked_move_tripod,
                                            keyboard=self.window.devices.keyboard,
                                            tripod=camera.tripod)
        self.window.devices.mouse.append_cursor_pos_callback(dolly.callbacked_move_camera,
                                                             tripod=camera.tripod)

    def detach_dolly(self, camera_id):
        """
        detach dolly from a camera

        by disconnecting camera and dolly then removing callbacks
        :param camera_id:
        :return:
        """
        dolly = self[camera_id].detach_dolly()
        # handling callback. temporary patching
        if isinstance(dolly, FpsDolly):
            self.window.remove_predraw_callback(dolly.callbacked_move_tripod)
            self.window.devices.mouse.remove_cursor_pos_callback(dolly.callbacked_move_camera)
        else:
            raise NotImplementedError


class CameraFactory:
    def __init__(self, manager):
        self.__manager = manager

    # perspective
    def prsp_from_hfov(self, hfov, ratio, near, far):
        """
        perspective camera defined by field of view and ratio value
        :param hfov: Number, radian, horizontal field of view
        :param ratio: Number, ratio of width/height ex) 16/9
        :param near: Number, frustum near for clipping
        :param far: Number, frustum far for clipping
        :return:
        """
        definer = FovCamera(hfov, ratio, near, far)
        frustum = PrspFrustum(*definer.output_intfs)
        camera = Camera(CameraBody(definer, frustum), CameraTripod(), self.__manager)
        self.__manager.appendnew_device(camera)
        return camera

    def prsp_from_lrbt(self, left, right, bottom, top, near, far):
        """
        perspective camera defined by frustum near plane dimension

        (0, 0) is a common center of frustum dimension
        :param left: Number, left boundary value
        :param right: Number, right boundary value
        :param bottom: Number, bottom boundary value
        :param top: Number, top boundary value
        :param near: Number, frustum near for clipping
        :param far: Number, frustum far clipping
        :return:
        """
        definer = LrbtCamera(left, right, bottom, top, near, far)
        frustum = PrspFrustum(*definer.output_intfs)
        camera = Camera(CameraBody(definer, frustum), CameraTripod(), self.__manager)
        self.__manager.appendnew_device(camera)
        return camera

    # orthogonal
    def orth_from_lrbt(self, left, right, bottom, top, near, far):
        """
        orthogonal camera defined by frustum near plane dimension

        (0, 0) is a common center of frustum dimension
        :param left: Number, left boundary value
        :param right: Number, right boundary value
        :param bottom: Number, bottom boundary value
        :param top: Number, top boundary value
        :param near: Number, frustum near for clipping
        :param far: Number, frustum far clipping
        :return:
        """
        definer = LrbtCamera(left, right, bottom, top, near, far)
        frustum = OrthFrustum(*definer.output_intfs)
        camera = Camera(CameraBody(definer, frustum), CameraTripod(), self.__manager)
        self.__manager.appendnew_device(camera)
        return camera
