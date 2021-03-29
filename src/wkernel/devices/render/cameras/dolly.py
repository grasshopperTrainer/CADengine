from gkernel.dtype.geometric import Vec, Pnt, Lin, ZVec, ZeroVec, XVec, YVec, MoveMat
import weakref as wr
from itertools import repeat
import numpy as np


class Dolly:
    """
    Dolly parent
    """
    pass


class FpsDolly(Dolly):
    """
    collection of callbacks for moving camera
    """

    def __init__(self, camera, cursor):
        self.move_speed = 2
        self.view_speed = 0.005

        self.__camera = wr.ref(camera)
        self.__cursor = wr.ref(cursor)

        self.__acceleration = Vec(0, 0, 0)
        # max pixel acceleration per frame
        mpapf = 100
        self.__acc_limit = (-mpapf, mpapf)
        # max angle acceleration per frame
        # meaning max acceleration gained can't overcome 1 degree
        maapf = 1
        # acceleration unit for 1 pixel cursor move
        self.__acc_unit = maapf / mpapf
        self.__velocity = Vec(0, 0, 0)
        # self.__velocity_threshold = 3.14 / 1800  # about 1/10 degree
        self.__friction = 4

    @property
    def camera(self):
        o = self.__camera()
        return o if o else self.delete()

    @property
    def cursor(self):
        o = self.__cursor()
        return o if o else self.delete()

    def delete(self):
        raise NotImplementedError

    def callbacked_move_tripod(self, keyboard, **kwargs):
        """
        move tripod

        callback intended to be used with window per frame callback
        :param keyboard:
        :param kwargs: to accept args provided by glfw key callback handler if registered in it
        :return:
        """
        # left right back forward create delta vector
        x, y, z = self.camera.tripod.plane.axes
        dvec = ZeroVec()
        for c, v in zip(('a', 's', 'd', 'w', 'e', 'q'), (-x, z, x, -z, ZVec(), -ZVec())):
            if keyboard.get_key_status(c)[0]:
                dvec += v

        dvec.as_vec().amplify(self.move_speed)
        self.camera.tripod.move(dvec)

    def callbacked_update_acceleration(self, glfw_window, xpos, ypos, mouse):
        """
        update camera move acceleration

        :param glfw_window:
        :param xpos:
        :param ypos:
        :param mouse:
        :return:
        """

        # calculate acceleration
        v = self.cursor.accel
        x, y = map(lambda lim, c: max(lim[0], min(c, lim[1])), repeat(self.__acc_limit), v.xy)  # clamping
        self.__acceleration = Vec(x, y, 0) * self.__acc_unit  # mapping
        # mouse.cursor_goto_center()

    def casllbacked_update_camera(self):
        self.__velocity = (self.__velocity + self.__acceleration) / self.__friction  # simple friction
        self.__acceleration = Vec(0, 0, 0)  # reset acceleration
        if self.__velocity.length < self.__acc_unit:  # stop if velocity is too small
            self.__velocity = Vec(0, 0, 0)
        else:  # move camera
            # rotate vertically and horizontally
            tripod = self.camera.tripod
            tripod.pitch(self.__velocity.y)
            axis = Lin.from_pnt_vec(tripod.plane.origin, Vec(0, 0, 1))
            tripod.rotate_around(axis, -self.__velocity.x)


class CadDolly(Dolly):
    """
    sketchup like dolly
    """

    def __init__(self, window, camera, cursor, def_offset):
        self.__camera = wr.ref(camera)
        self.__cursor = wr.ref(cursor)
        self.__window = wr.ref(window)

        self.__def_offset = def_offset

        self.__panning = False
        self.__prf = Pnt(0, 0, 0)
        # percentage describing how much of distance between camera,
        # cursor target is applied to panning distance
        self.__pa = 0.001
        self.__pf = 0.25
        self.__pv = Vec(0, 0, 0)
        self.__pp = Vec(0, 0, 0)
        window.append_predraw_callback(self.__apply_panning)

        self.__zooming = False
        self.__zrf = None
        self.__zd = Vec(1, 0, 0)
        self.__za = Vec(0, 0, 0)
        self.__zv = Vec(0, 0, 0)
        self.__zf = 0.25
        window.append_predraw_callback(self.__apply_zooming)
        self.cursor.append_mouse_scroll_callback(self.__update_zoom_accel)

        self.__orbiting = False
        self.__orf = Pnt(0, 0, 0)
        self.__ov = Vec(0, 0, 0)
        self.__of = 0.25
        self.__op = Vec(0, 0, 0)
        # one 1 pixel move derives 1*-0.05 radian orbiting
        # which is about 2.8 degree
        self.__oa = -0.05
        window.append_predraw_callback(self.__apply_orbit)

        window.devices.keyboard.append_key_callback(self.__reset_pos)

    @property
    def camera(self):
        c = self.__camera()
        if c:
            return c
        raise NotImplementedError

    @property
    def cursor(self):
        c = self.__cursor()
        if c:
            return c
        raise NotImplementedError

    @property
    def window(self):
        w = self.__window()
        if w:
            return w
        raise NotImplementedError

    @property
    def __cam_off_ref(self):
        """
        use camera offset reference point if reference is not given

        :return:
        """
        o, _, __, z = self.camera.tripod.plane.components
        return o + z.project_on_xy().amplify(-self.__def_offset)

    def __apply_panning(self):
        """
        apply panning camera transformation
        :return:
        """
        pos = self.window.devices.mouse.pos_instant
        if self.__prf is None:
            self.__prf = self.__cam_off_ref

        k, m = self.window.devices.keyboard, self.window.devices.mouse
        if k.get_key_status('lshift')[0] == 1 and m.get_button_status(2):  # actuator
            d = (self.__prf - self.camera.tripod.plane.origin).length
            acc = (pos - self.__pp) * d * self.__pa
        else:
            acc = Vec(0, 0, 0)

        self.__pv = (self.__pv + acc) * self.__pf
        if 0.001 < self.__pv.length:
            self.__panning = True
            self.camera.tripod.move_local(self.__pv)
        else:
            self.__panning = False
            self.__pv = Vec(0, 0, 0)

        self.__prf = None
        self.__pp = pos

    def __apply_zooming(self):
        """
        apply zooming camera

        :return:
        """
        self.__zv = (self.__zv + self.__za) * self.__zf  # simple acceleration/frictional velocity

        self.__za = Vec(0, 0, 0)
        if 1 < abs(self.__zv.y):
            self.__zooming = True
            if self.__zrf is None:
                self.__zd = -self.camera.tripod.plane.axis_z
            else:
                self.__zd = self.__zrf - self.camera.tripod.plane.origin

            self.camera.tripod.move(self.__zd.amplify(self.__zv.y))
        else:
            self.__zv = Vec(0, 0, 0)
            self.__zooming = False

        self.__zrf = None

    def __update_zoom_accel(self, glfw_window, xoff, yoff, cursor):
        """
        update zoom acceleration when callbacked by scroll move

        :param glfw_window:
        :param xoff: scroll left right
        :param yoff: scroll top bottom
        :param cursor:
        :return:
        """
        if self.__zrf is not None:
            d = (self.__zrf - self.camera.tripod.plane.origin).length
            # adaptive acceleration related to camera, cursor target distance
            if yoff < 0:  # zoom out
                self.__za += Vec(0, yoff * d)
            else:  # zoom in
                self.__za += Vec(0, yoff * d * 0.5)
        else:  # if zoom target is not given use camera origin - world origin distance as default magnitude
            self.__za += Vec(0, yoff * self.camera.tripod.plane.origin.as_vec().length * 0.5)

    def __apply_orbit(self):
        """
        apply orbiting camera

        :return:
        """
        pos = self.window.devices.mouse.pos_instant
        acc = (pos - self.__op) * self.__oa
        self.__op = pos

        if self.__orf is None:
            self.__orf = self.__cam_off_ref

        self.__ov = (self.__ov + acc) * self.__of
        k, m = self.window.devices.keyboard, self.window.devices.mouse
        if k.get_key_status('lshift')[0] == 0 and m.get_button_status(2) and self.__orf is not None:  # actuator
            self.__orbiting = True  # to fix orbiting target
            self.camera.tripod.rotate_around(Lin.from_pnt_vec(self.__orf, ZVec()), self.__ov.x)
            haxis = -self.camera.tripod.plane.axis_x.project_on_xy()  # maintain camera up
            self.camera.tripod.rotate_around(Lin.from_pnt_vec(self.__orf, haxis), self.__ov.y)
        else:
            self.__orbiting = False
            self.__orf = None

    def set_ref_point(self, x, y, z):
        """
        update camera modifying reference point

        ! all three modifications has to have separate record
        :param x: coord x
        :param y: coord y
        :param z: coord z
        :return:
        """
        pos = Pnt(x, y, z)
        if not self.__orbiting:
            self.__orf = pos
        # if not self.__zooming:
        self.__zrf = pos
        if not self.__panning:
            self.__prf = pos

    def __reset_pos(self, glfw_window, key, scancode, action, mods, keyboard):
        """
        for debugging, reset position with 'shift + z'

        :param glfw_window:
        :param key:
        :param scancode:
        :param action:
        :param mods:
        :param keyboard:
        :return:
        """
        if action and keyboard.get_char(key, mods) == 'Z':  # actuator
            o, _, __, z = self.camera.tripod.plane.components
            # horizontal move on camera origin z
            new_o = Pnt(*z.project_on_xy().amplify(self.__def_offset).xy, o.z)
            mm = MoveMat(*(new_o - o).xyz)
            # update new plane
            self.camera.tripod.plane = mm * self.camera.tripod.plane
