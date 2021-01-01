from gkernel.dtype.geometric.primitive import Vec, Pnt, Lin, Ray
from gkernel.dtype.nongeometric.matrix import MoveMat, ScaleMat
from .window_properties import *


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


class FpsDolly:

    def __init__(self, camera, tripod):
        self._camera = camera
        self._tripod = tripod
        self.move_speed = 10
        self.view_speed = 0.01
        # should it be at upper?
        self._keyboard = camera.manager.window.devices.keyboard.set_key_callback(self.key_callback)
        self._cursor = camera.manager.window.devices.mouse.set_cursor_pos_callback(self.cursorpos_callback)
        self._last_cursor_pos = None

    def key_callback(self, window, key, scancode, action, mods, keyboard):
        # left right back forward
        char = keyboard.get_char(key, mods)
        if char == 'a':
            self._tripod.move_along_axis('x', -self.move_speed)
        elif char == 'd':
            self._tripod.move_along_axis('x', self.move_speed)
        elif char == 's':
            self._tripod.move_along_axis('z', self.move_speed)
        elif char == 'w':
            self._tripod.move_along_axis('z', -self.move_speed)
        # ascend descend
        elif char == 'q':
            self._tripod.move(Vec(0, 0, -self.move_speed))
        elif char == 'e':
            self._tripod.move(Vec(0, 0, self.move_speed))

    def cursorpos_callback(self, window, xpos, ypos, mouse):
        """
        move camera frustum with cursor move

        :param window:
        :param xpos:
        :param ypos:
        :param mouse:
        :return:
        """
        if self._last_cursor_pos is not None:
            v = Vec.of_two_pnt(Pnt(*self._last_cursor_pos), Pnt(xpos, ypos)) * self.view_speed  # cursor delta
            # rotate vertically and horizontally
            self._tripod.pitch(v.y)
            axis = Lin.of_pnt_vec(self._tripod.in_plane.r.origin, Vec(0, 0, 1))
            self._tripod.rotate_along(axis, -v.x)

        self._last_cursor_pos = xpos, ypos


class Camera(RenderTarget):
    """
    Camera

    Camera consists of Two parts; camera body, camera orientation(position)
    """

    def __init__(self, body: CameraBody, tripod: CameraTripod, pool):
        super().__init__(pool)

        self._body = body
        self._tripod = tripod
        self._dolly = None

    def set_fps_dolly(self, window):
        self._dolly = FpsDolly(self, self._tripod)

    def set_dolly(self, dolly):
        self._dolly = dolly

    @property
    def body(self) -> CameraBody:
        return self._body

    @property
    def tripod(self) -> CameraTripod:
        return self._tripod

    @property
    def dolly(self):
        return self._dolly

    def ray_frustum(self, param_x, param_y):
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
        frustum_point = mm * sm * Pnt(x=param_x, y=param_y, z=0)
        frustum_point = Pnt(x=param_x, y=param_y, z=0) * sm * mm
        # print(frustum_point)
        # raise
        # define ray and cast into world space
        ray = Ray([0, 0, 0], frustum_point.xyz)

        return self.tripod.VM.r * ray

    def __enter__(self):
        CameraCurrentStack().append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CameraCurrentStack().pop()


class CameraManager(RenderTargetManager):
    def __init__(self, window):
        super().__init__(window)
        r, t = window.glyph.width.r / 2, window.glyph.height.r / 2
        # self.append_new_orthogonal(-r, r, -t, t, 1, 10000)
        self.new_perspective(np.radians(50), 1, 10000, window.glyph.aspect_ratio)

    def __getitem__(self, item) -> Camera:
        """
        Returns camera object
        :param item: index of cameras
        :return: Camera object
        """
        return self._targets[item]

    def new_orthogonal(self, left, right, bottom, top, near, far):
        new_cam = CameraFactory.new_camera(self, 'lrbt', 'orth', left, right, bottom, top, near, far)
        self._append_new_target(new_cam)

    def new_perspective(self, fov, near, far, ratio):
        new_cam = CameraFactory.new_camera(self, 'fov', 'prsp', fov, near, far, ratio)
        self._append_new_target(new_cam)
