from .window_properties import *
from GeomKernel.dataTypes import Pln, Vec
from .bits import KeyCallbackBit


class Cameras(RenderTargetPool):
    def __init__(self, window):
        super().__init__(window)
        r, t = window.width/2, window.height/2
        self.append_new_orthogonal(-r, r, -t, t, 1, 10000)

    def append_new_orthogonal(self, left, right, bottom, top, near, far):
        new_cam = CameraFactory.new_camera(self, 'lrbt', 'orth', left, right, bottom, top, near, far)
        self.append_new_target(new_cam)

    def append_new_perspective(self, fov, near, far, ratio):
        new_cam = CameraFactory.new_camera(self, 'fov', 'prsp', fov, near, far, ratio)
        self.append_new_target(new_cam)

    def set_fps_dolly(self, camera):
        camera._dolly = FpsDolly(self.fm_get_parent(0), camera)

    def set_dolly(self, camera, dolly):
        camera._dolly = dolly


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
            frustum = OrthFrustum(*definer.output_intfs.values())
        elif orth_prsp == 'prsp':
            frustum = PrspFrustum(*definer.output_intfs.values())
        else:
            raise
        camera = Camera(pool, CameraBody(definer, frustum), CameraTripod())
        return camera


class Camera(RenderTarget):
    """
    Camera

    Camera consists of Two parts; camera body, camera orientation(position)
    """

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

    def __init__(self, pool, body:CameraBody, tripod:CameraTripod):
        super().__init__(pool)
        self._body = body
        self.body_left = body.out0_left
        self.body_right = body.out1_right
        self.body_bottom = body.out2_bottom
        self.body_top = body.out3_top
        self.body_near = body.out4_near
        self.body_far = body.out5_far
        self.body_hfov = body.out6_hfov
        self.body_vfov = body.out7_vfov
        self.body_aspect_ratio = body.out8_aspect_ratio
        self.body_PM = body.out9_PM

        self._tripod = tripod
        self.tripod_plane = tripod.out0_plane
        self.tripod_VM = tripod.out1_VM
        self._dolly = None

    # def calculate(self):
    #     return self.output_values
    #     print('calcam')
    #     return None

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


class FpsDolly(KeyCallbackBit):

    def __init__(self, window, camera):
        super().__init__(window)
        self._camera = camera
        self.move_speed = 1
        self.view_speed = 1

    def callback(self, window, key, scancode, action, mods):
        print('dolly reading', self.get_char(key, mods))
        # left right back forward
        if self.get_char(key, mods) == 'a':
            self._camera.tripod.move_along_axis('x', -self.move_speed)
        elif self.get_char(key, mods) == 'd':
            self._camera.tripod.move_along_axis('x', self.move_speed)
        elif self.get_char(key, mods) == 's':
            self._camera.tripod.move_along_axis('z', self.move_speed)
        elif self.get_char(key, mods) == 'w':
            self._camera.tripod.move_along_axis('z', -self.move_speed)
        # ascend descend
        elif self.get_char(key, mods) == 'q':
            self._camera.tripod.move_along_axis('y', -self.move_speed)
        elif self.get_char(key, mods) == 'e':
            self._camera.tripod.move_along_axis('y', self.move_speed)

        super().callback(key, scancode, action, mods)