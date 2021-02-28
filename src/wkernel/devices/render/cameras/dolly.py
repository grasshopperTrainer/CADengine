from gkernel.dtype.geometric import Vec, Pnt, Lin, ZVec, ZeroVec
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

    def __init__(self, camera):
        self.move_speed = 2
        self.view_speed = 0.005

        self.__camera = wr.ref(camera)

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
        if self.__camera():
            return self.__camera()
        else:
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
        v = Vec.from_pnts(Pnt(*mouse.cursor_center()), Pnt(xpos, ypos))  # acc vector
        x, y = map(lambda lim, c: max(lim[0], min(c, lim[1])), repeat(self.__acc_limit), v.xy)  # clamping
        self.__acceleration = Vec(x, y, 0) * self.__acc_unit  # mapping
        # reset cursor pos
        mouse.cursor_goto_center()

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
            tripod.rotate_along(axis, -self.__velocity.x)
