from gkernel.dtype.geometric import Vec, Pnt, Lin, ZVec, ZeroVec, XVec, YVec, MoveMat
import weakref as wr
from itertools import repeat
import glfw


class Dolly:
    """
    Dolly parent
    """
    pass


class FpsDolly(Dolly):
    """
    collection of callbacks for moving camera
    """

    def __init__(self, window, camera, cursor):
        self.__camera = wr.ref(camera)
        self.__cursor = wr.ref(cursor)

        with window.context.glfw as glfw_window:
            glfw.set_input_mode(glfw_window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        self.__move_spd = 2
        self.__move_boost = 4
        window.append_predraw_callback(self.__update_move, keyboard=window.devices.keyboard)

        mpapf = 100  # max pixel acceleration per frame
        maapf = 1  # max angle acceleration per frame
        self.__rot_acc_lim = (-mpapf, mpapf)
        self.__rot_acc_unit = maapf / mpapf  # acceleration unit for 1 pixel cursor move
        self.__rot_acc = Vec(0, 0, 0)
        self.__rot_vel = Vec(0, 0, 0)
        self.__rot_fric = 4
        window.append_predraw_callback(self.__update_rot)
        window.devices.mouse.append_cursor_pos_callback(self.__update_rot_acc)

    @property
    def camera(self):
        o = self.__camera()
        return o if o else self.delete()

    @property
    def cursor(self):
        o = self.__cursor()
        return o if o else self.delete()

    @property
    def move_spd(self):
        return self.__move_spd

    @move_spd.setter
    def move_spd(self, v):
        self.__move_spd = v

    @property
    def move_boost(self):
        self.__move_boost

    @move_boost.setter
    def move_boost(self, v):
        self.__move_boost = v

    def delete(self):
        raise NotImplementedError

    def __update_move(self, keyboard, **kwargs):
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
            if keyboard.get_key_status(c):
                dvec += v
        dvec = dvec.as_vec().amplify(self.__move_spd)
        if keyboard.get_key_status('lshift'):
            dvec *= self.__move_boost
        self.camera.tripod.move(dvec)

    def __update_rot_acc(self, glfw_window, xpos, ypos, mouse):
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
        x, y = map(lambda lim, c: max(lim[0], min(c, lim[1])), repeat(self.__rot_acc_lim), v.xy)  # clamping
        self.__rot_acc = Vec(x, y, 0) * self.__rot_acc_unit  # mapping

    def __update_rot(self):
        self.__rot_vel = (self.__rot_vel + self.__rot_acc) / self.__rot_fric  # simple friction
        self.__rot_acc = Vec(0, 0, 0)  # reset acceleration
        if self.__rot_vel.length < 0.001:  # stop if velocity is too small
            self.__rot_vel = Vec(0, 0, 0)
        else:  # move camera
            # rotate vertically and horizontally
            tripod = self.camera.tripod
            tripod.pitch(self.__rot_vel.y)
            axis = Lin.from_pnt_vec(tripod.plane.origin, Vec(0, 0, 1))
            tripod.rotate_around(axis, -self.__rot_vel.x)


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
        self.__pa = 0.005
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
        if k.get_key_status('lshift') and m.get_button_status(2):  # actuator
            d = (self.__prf - self.camera.tripod.plane.origin).length
            acc = (pos - self.__pp) * d * self.__pa
            self.__panning = True
        else:
            acc = Vec(0, 0, 0)
            self.__prf = None
            self.__panning = False

        # update camera move
        self.__pv = (self.__pv + acc) * self.__pf
        if 0.001 < self.__pv.length:
            self.camera.tripod.move_local(self.__pv)
        else:
            self.__pv = Vec(0, 0, 0)

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
        if not k.get_key_status('lshift') and m.get_button_status(2) and self.__orf is not None:  # actuator
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
