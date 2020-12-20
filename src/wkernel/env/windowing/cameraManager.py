from .window_properties import *
from gkernel.dtype.geometric.primitive import Pln, Vec, Pnt, Lin, Ray
from gkernel.dtype.nongeometric.matrix import MoveMat, RotZMat, ScaleMat
from .bits import *



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

    def __init__(self, camera):
        self._camera = camera
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
            self._camera.tripod.move_along_axis('x', -self.move_speed)
        elif char == 'd':
            self._camera.tripod.move_along_axis('x', self.move_speed)
        elif char == 's':
            self._camera.tripod.move_along_axis('z', self.move_speed)
        elif char == 'w':
            self._camera.tripod.move_along_axis('z', -self.move_speed)
        # ascend descend
        elif char == 'q':
            self._camera.tripod.move(Vec(0, 0, -self.move_speed))
        elif char == 'e':
            self._camera.tripod.move(Vec(0, 0, self.move_speed))

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
            v = Vec.pnt2(Pnt(*self._last_cursor_pos), Pnt(xpos, ypos))* self.view_speed  # cursor delta
            self._camera.tripod.pitch(v.y)           # rotate vertically
            self._camera.tripod.rotate_along(Vec(x=0, y=0, z=1), v.x)
            # self._camera.tripod.yaw(-v.x * self.view_speed)
            # # rotate horizontally around world y axis
            # plane = self._camera.tripod.in_plane.r
            # ox, oy, oz = plane.origin.xyz
            #
            # new_plane = MoveMat(ox, oy, oz) * RotZMat(v.x * -self.view_speed) * MoveMat(-ox, -oy, -oz) * plane
            # self._camera.tripod.in_plane = new_plane

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
        self._dolly = FpsDolly(self)

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
        sm = ScaleMat(x=r-l, y=t-b)
        mm = MoveMat(x=(r+l)/2, y=(t+b)/2, z=-n)
        frustum_point = mm*sm*Pnt(x=param_x, y=param_y, z=0)
        frustum_point = Pnt(x=param_x, y=param_y, z=0)*sm*mm
        # print(frustum_point)
        # raise
        # define ray and cast into world space
        ray = Ray([0,0,0], frustum_point.xyz)

        return self.tripod.VM.r*ray

    def __enter__(self):
        CameraCurrentStack().append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CameraCurrentStack().pop()


class CameraManager(RenderTargetManager):
    def __init__(self, window):
        super().__init__(window)
        r, t = window._glyph.width.r / 2, window._glyph.height.r / 2
        # self.append_new_orthogonal(-r, r, -t, t, 1, 10000)
        self.new_perspective(np.radians(50), 1, 10000, window._glyph.aspect_ratio)

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
