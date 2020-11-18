from .window_properties import *
from GeomKernel.dataTypes import Pln, Vec
from .bits import *


class Cameras(RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        r, t = window._glyph.width.r / 2, window._glyph.height.r / 2
        # self.append_new_orthogonal(-r, r, -t, t, 1, 10000)
        self.new_perspective(np.radians(50), 1, 10000, window._glyph.aspect_ratio)

    def new_orthogonal(self, left, right, bottom, top, near, far):
        new_cam = CameraFactory.new_camera(self, 'lrbt', 'orth', left, right, bottom, top, near, far)
        self._append_new_target(new_cam)

    def new_perspective(self, fov, near, far, ratio):
        new_cam = CameraFactory.new_camera(self, 'fov', 'prsp', fov, near, far, ratio)
        self._append_new_target(new_cam)


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
    def body(self):
        return self._body

    @property
    def tripod(self):
        return self._tripod

    @property
    def dolly(self):
        return self._dolly

    def __enter__(self):
        CameraCurrentStack().append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        CameraCurrentStack().pop()


class FpsDolly:

    def __init__(self, camera):
        self._camera = camera
        self.move_speed = 10
        self.view_speed = 0.01
        # should it be at upper?
        self._keyboard = camera.manager.window.devices.keyboard.set_key_callback(self.key_callback)
        self._cursor = camera.manager.window.devices.mouse.set_cursor_pos_callback(self.cursorpos_callback)

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
        # cursor movement vector
        v = Vec.pnt2(Pnt(*mouse.last_pos), Pnt(xpos, ypos))
        # rotate vertically
        self._camera.tripod.pitch(-v.y * self.view_speed)
        # rotate horizontally around world z axis
        p = self._camera.tripod.in0_plane.r
        new_plane = TrnslMat(*p.origin.xyz) * RotMat('z', v.x * -self.view_speed) * TrnslMat(*-p.origin.xyz) * p
        self._camera.tripod.in0_plane = new_plane
