from gkernel.dtype.geometric import Vec, Pnt, Lin, ZVec, ZeroVec


class Dolly:
    """
    Dolly parent
    """
    pass


class FpsDolly(Dolly):

    def __init__(self):
        self.move_speed = 2
        self.view_speed = 0.005
        # should it be at upper?

        self.__last_v = Vec(0, 0, 0)

    def callbacked_move_tripod(self, keyboard, tripod, **kwargs):
        """
        move tripod

        callback intended to be used with window per frame callback
        :param keyboard:
        :param tripod:
        :param kwargs: to accept args provided by glfw key callback handler if registered in it
        :return:
        """
        # left right back forward create delta vector
        x, y, z = tripod.plane.axes
        dvec = ZeroVec()
        for c, v in zip(('a', 's', 'd', 'w', 'e', 'q'), (-x, z, x, -z, ZVec(), -ZVec())):
            if keyboard.get_key_status(c)[0]:
                dvec += v

        dvec.as_vec().amplify(self.move_speed)
        tripod.move(dvec)

    def callbacked_move_camera(self, glfw_window, xpos, ypos, mouse, tripod, window):
        """
        move camera frustum with cursor move

        :param window:
        :param xpos:
        :param ypos:
        :param mouse:
        :return:
        """
        xpos, ypos = mouse.cursor_pos_perframe
        v = Vec.from_pnts(Pnt(*mouse.cursor_center()), Pnt(xpos, ypos)) * self.view_speed  # cursor delta
        v = (self.__last_v + v)/2
        self.__last_v = v
        # rotate vertically and horizontally
        if abs(v.y) > 0.01:
            tripod.pitch(v.y)
        if abs(v.x) > 0.01:
            axis = Lin.from_pnt_vec(tripod.plane.origin, Vec(0, 0, 1))
            tripod.rotate_along(axis, -v.x)

        mouse.cursor_goto_center()

