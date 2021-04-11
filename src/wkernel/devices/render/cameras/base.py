import weakref
import gkernel.dtype.geometric as gt
from gkernel.dtype.nongeometric.matrix.primitive import ScaleMat
from wkernel.devices.render._base import *
from .dolly import *
from .parts import *
import glfw


class CameraFactory:

    def __init__(self, manager):
        self.__manager = weakref.ref(manager)
        self.__fdim = None
        self.__fshape = None

    def set_lrbt_dimension(self, l, r, b, t, near, far):
        """
        attach lrbt frustum dimension
        :return:
        """
        self.__fdim = l, r, b, t, near, far
        return self

    def set_hfov_dimension(self, hfov, aspect_ratio, near, far):
        """
        attach horizontal field of view frustum dimension
        :return:
        """
        r = near * np.tan(hfov / 2)
        l = -r
        t = r / aspect_ratio
        b = -t
        self.__fdim = l, r, b, t, near, far
        return self

    def set_frustum_shape(self, fshape: ('o', 'p')):
        """
        attach orthogonal frustum type
        :return:
        """
        if not (isinstance(fshape, str) and fshape in ('o', 'p')):
            raise ValueError

        self.__fshape = fshape
        return self

    def create(self):
        if not (self.__fdim and self.__fshape):
            raise ValueError('camera needs dimension and type')

        camera = Camera(
            body=CameraBody(*self.__fdim, fshape=self.__fshape),
            tripod=CameraTripod(),
            manager=self.__manager())
        self.__manager()._appendnew_device(camera)
        return camera


class Camera(RenderDevice):
    """
    Camera

    Camera consists of Two parts; camera body, camera orientation(position)
    """

    def __init__(self, body, tripod, manager):
        super().__init__(manager)
        self.__body = body
        self.__tripod = tripod
        self.__dolly = None

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super().__exit__(exc_type, exc_val, exc_tb)

    @property
    def body(self) -> CameraBody:
        return self.__body

    @property
    def tripod(self) -> CameraTripod:
        return self.__tripod

    @property
    def dolly(self):
        return self.__dolly

    @property
    def near_clipping_face(self):
        """
        return frustum near clipping face in WCS

        :return: Plin
        """
        pln = self.tripod.plane
        l, r, b, t, n, f = self.body.dim
        face = gt.Plin((l, b, -n), (r, b, -n), (r, t, -n), (l, t, -n))
        return pln.TM * face

    @property
    def far_clipping_face(self):
        """
        return frustum far clipping face in WCS

        :return: Plin
        """
        pln = self.tripod.plane
        l, r, b, t, n, f = self.body.dim
        if self.body.fshape == 'p':
            d = f - n
            # far face dimensions
            l, r, b, t = [(i * d) / n + i for i in (l, r, b, t)]
        face = gt.Plin((l, b, -f), (r, b, -f), (r, t, -f), (l, t, -f))
        return pln.TM * face

    def attach_dolly(self, dolly):
        """
        Assign dolly
        :param dolly:
        :return:
        """
        if not isinstance(dolly, Dolly):
            raise TypeError
        self.__dolly = dolly

    def detach_dolly(self):
        """
        Remove dolly

        :return: dolly for manager to handle callback detachment
        """
        if self.__dolly is None:
            raise ValueError('no dolly to detach')
        d = self.__dolly
        self.__dolly = None
        return d

    def frusrum_ray(self, param_x, param_y):
        """
        return ray crossing near frustum at given param

        param 0,0 points at the center of frustum
        :param param_x: in domain(0., 1.)
        :param param_y: in domain(0., 1.)
        :return:
        """
        l, r, b, t, n, f = self.body.dim
        # convert normalized into near frustum space
        sm = ScaleMat(x=r - l, y=t - b)
        # .5 to compensate origin difference between OpenGL space and pane space
        offset = MoveMat(-.5, -.5, -n)
        frustum_point = sm * offset * Pnt(x=param_x, y=param_y, z=0)
        ray = gt.Ray([0, 0, 0], frustum_point.xyz)
        return self.tripod.plane.TM * ray

    def focus_pane(self, pane, focus, clip_off):
        """
        modify frustum to tightly wrap pane's '2D plane'
        '2D plane': is a 2D(0-z) coordinate space of size of a pane
                    e.g. if pane's size is (100, 500) and focus is (0, 0, 0), camera will face that focus
                    so that 2D plane of given size centered at the focus will tightly fit in viewing boundaries

        ! this method may cause modification in camera's dimension
        :param pane: Pane, for the frustum to wrap
        :param focus: (x, y, z), position to head camera look-at vector
                        ! z value matters in case fshape is 'p'
        :param clip_off: Number, z offset of near clipping plane from the focus
        :return:
        """

        if self.body.fshape == 'o':
            # modify body
            hw, hh = (d // 2 for d in pane.size.xy)
            l, r, b, t, n, f = self.body.dim
            clip_d = f - n
            self.body.dim = -hw, hw, -hh, hh, focus[2] + clip_off, n + clip_d
            # modify tripod
            self.tripod.lookat(eye=(focus[0], focus[1], focus[2] + clip_off), at=focus, up=(0, 1, 0))
        else:
            # modify body
            # calculate new clipping plane size
            w, h = pane.size.xy
            cpw = w - 2 * (clip_off / np.tan((np.pi - self.body.hfov) / 2))
            cph = h - 2 * (clip_off / np.tan((np.pi - self.body.vfov) / 2))
            # calculate new near
            l, r, b, t, n, f = self.body.dim
            clip_d = f - n
            near = (cpw / 2) / np.tan(self.body.hfov / 2)
            far = near + clip_d
            self.body.dim = -cpw / 2, cpw / 2, -cph / 2, cph / 2, near, far

            # modify tripod
            x, y, z = focus
            newz = z + clip_off + near
            self.tripod.lookat(eye=(x, y, newz), at=focus, up=(0, 1, 0))


class _Camera(Camera):

    def __enter__(self) -> Camera:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CameraManager(RenderDeviceManager):

    def __init__(self, device_master):
        super().__init__(device_master)

        c = self.factory.set_hfov_dimension(
            hfov=np.radians(50),
            aspect_ratio=self.window.glyph.aspect_ratio.r,
            near=5,
            far=100_000).set_frustum_shape('p').create()
        c.tripod.lookat(eye=(0, 0, 100), at=(0, 0, 0), up=(0, 1, 0))
        self.master.tracker.stack.set_base(c)

    def __getitem__(self, item) -> _Camera:
        return super(CameraManager, self).__getitem__(item)

    @property
    def factory(self):
        return CameraFactory(self)

    @property
    def device_type(self):
        return Camera

    # TODO: need camera dolly connector? should it take all the responsibilities? who has to know about dolly?
    def attach_fps_dolly(self, camera_id, cursor_id):
        """
        attach FPS dolly to the camera

        FPS dolly replies to cursor, keyboard inputs
        asdw - move camera
        qe - ascend descend camera
        shift - boost movement
        mouse - rotate camera

        :param camera_id:
        :param cursor_id:
        :return:
        """
        camera = self[camera_id]
        cursor = self.master.cursors[cursor_id]
        return FpsDolly(self.window, camera, cursor)

    def attach_cad_dolly(self, camera_id, cursor_id, def_offset):
        """
        attach CAD like dolly

        CAD dolly supports three movement:
        pan, orbit, zoom conrolled by scroll, mouse center button and 'shift'

        :param camera_id:
        :param cursor_id:
        :param def_offset:
        :return:
        """
        camera = self[camera_id]
        cursor = self.master.cursors[cursor_id]
        return CadDolly(self.window, camera, cursor, def_offset)

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
            self.window.remove_predraw_callback(dolly.__move_tripod)
            self.window.devices.mouse.remove_cursor_pos_callback(dolly.__update_acceleration)
        else:
            raise NotImplementedError
