from gkernel.dtype.geometric import Vec, Pnt, Lin, ZVec, ZeroVec, XVec, YVec
import weakref as wr
from itertools import repeat


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

    def __init__(self, window, camera, cursor):
        self.__camera = wr.ref(camera)
        self.__cursor = wr.ref(cursor)
        self.__window = wr.ref(window)

        self.__pan_amp = 0.2
        self.__pan_prev = Vec(0, 0, 0)
        window.append_predraw_callback(self.__update_pan)

        self.__zoom_accel = Vec(0, 0, 0)
        self.__zoom_velocity = Vec(0, 0, 0)
        self.__zoom_friction = 0.25
        self.__zoom_amp = 10
        window.append_predraw_callback(self.__update_zoom)
        self.cursor.append_mouse_scroll_callback(self.__update_scroll_offset)

        self.__orbiting = False
        self.__oorigin = Pnt(0, 0, 0)
        self.__oaccel = Vec(0, 0, 0)
        self.__ovelocity = Vec(0, 0, 0)
        self.__ofriction = 0.25
        self.__oamp = -0.05
        self.__opos = Vec(0, 0, 0)
        self.cursor.append_cursor_pos_callback(self.__update_orbit_accel)
        window.append_predraw_callback(self.__update_orbit)

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

    def __update_pan(self):
        k, m = self.window.devices.keyboard, self.window.devices.mouse
        pos = self.cursor.pos_global

        if k.get_key_status('lshift')[0] == 1 and m.get_button_status(2):
            self.camera.tripod.move_local((pos - self.__pan_prev)*self.__pan_amp)

        self.__pan_prev = pos

    def __update_zoom(self):
        self.__zoom_velocity = (self.__zoom_velocity + self.__zoom_accel) * self.__zoom_friction
        self.camera.tripod.move_local(Vec(0, 0, self.__zoom_velocity.y))
        self.__zoom_accel = Vec(0, 0, 0)

    def __update_scroll_offset(self, glfw_window, xoff, yoff, cursor):
        self.__zoom_accel += Vec(xoff, yoff)*self.__zoom_amp

    def __update_orbit_accel(self, glfw_window, xpos, ypos, cursor):
        pos = Vec(xpos, ypos)
        self.__oaccel = (pos - self.__opos) * self.__oamp
        self.__opos = pos

    def __update_orbit(self):
        self.__ovelocity = (self.__ovelocity + self.__oaccel) * self.__ofriction
        self.__oaccel = Vec(0, 0, 0)
        if self.window.devices.keyboard.get_key_status('lshift')[0] == 0 and self.window.devices.mouse.get_button_status(2):
            self.__orbiting = True
            self.camera.tripod.rotate_around(Lin.from_pnt_vec(self.__oorigin, ZVec()), self.__ovelocity.x)
            haxis = -self.camera.tripod.plane.axis_x.project_on_xy()
            self.camera.tripod.rotate_around(Lin.from_pnt_vec(self.__oorigin, haxis), self.__ovelocity.y)
        else:
            self.__orbiting = False

    def set_orbit_origin(self, x, y, z):
        if not self.__orbiting:
            self.__oorigin = Pnt(x, y, z)