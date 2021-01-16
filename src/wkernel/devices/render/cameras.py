from gkernel.dtype.geometric.primitive import Pnt, Lin, Ray, ZeroVec, ZVec
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat
from ._base import *
from wkernel.pipeline.nodes.window.camera import *


class CameraFactory:
    @classmethod
    def new_camera(cls, pool, fov_lrbt, orth_prsp, *args):
        if fov_lrbt == 'fov':
            definer = FovCamera(*args)
        elif fov_lrbt == 'lrbt':
            definer = LrbtCamera(*args)
        else:
            raise

        if orth_prsp == 'orth':
            frustum = OrthFrustum(*definer.output_intfs)
        elif orth_prsp == 'prsp':
            frustum = PrspFrustum(*definer.output_intfs)
        else:
            raise
        camera = Camera(CameraBody(definer, frustum), CameraTripod(), pool)
        return camera


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
        return self.tripod.in_plane.r.trnsf_mat * ray

    def __enter__(self):
        """
        initiating camera

        :return:
        """
        CameraCurrentStack().append(self)
        # if isinstance(self._dolly, FpsDolly):   # hide cursor to use virtual space
        #     glfw.set_input_mode(self.manager.window.glfw_window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CameraCurrentStack().pop()


class CameraManager(RenderDeviceManager):
    def __init__(self, window):
        super().__init__(window)
        r, t = window.glyph.width.r / 2, window.glyph.height.r / 2
        # self.append_new_orthogonal(-r, r, -t, t, 1, 10000)
        self.new_perspective(np.radians(50), 0.1, 10000, window.glyph.aspect_ratio)

    def __getitem__(self, item) -> Camera:
        """
        Returns camera object
        :param item: index of cameras
        :return: Camera object
        """
        return self._devices[item]

    def new_orthogonal(self, left, right, bottom, top, near, far):
        new_cam = CameraFactory.new_camera(self, 'lrbt', 'orth', left, right, bottom, top, near, far)
        self._appendnew_device(new_cam)

    def new_perspective(self, fov, near, far, ratio):
        new_cam = CameraFactory.new_camera(self, 'fov', 'prsp', fov, near, far, ratio)
        self._appendnew_device(new_cam)

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
