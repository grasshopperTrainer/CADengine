from .window_properties import *
from GeomKernel.dataTypes import Plane, Vector
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
        self._tripod = tripod
        self._dolly = None

    def calculate(self):
        return *self._body.output_values, *self._tripod.output_values

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

    def callback(self, *args):
        print('dolly reading', args)
        super().callback(args)