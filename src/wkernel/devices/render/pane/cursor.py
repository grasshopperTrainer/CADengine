import weakref as wr

import gkernel.dtype.geometric as gt
import gkernel.dtype.nongeometric.matrix as mx


class Cursor:
    """
    artificial? window independent pane cursor
    """

    def __init__(self, mouse):
        self.__mouse = wr.ref(mouse)
        self.__SM = mx.TrnsfMats()
        self.__MM = mx.TrnsfMats()

        self.__pos_prev = gt.Vec(0, 0, 0)
        self.__pos = gt.Vec(0, 0, 0)
        self.__accel = gt.Vec(0, 0, 0)

    def set_offset(self, xpos, ypos):
        """
        set offset for cursor

        use pane's position to set pane's bottom left as cursor origin
        :return:
        """
        self.__MM = gt.MoveMat(-xpos, -ypos, 0)

    def set_mapping(self, sdomain, tdomain):
        """
        map cursor pos

        :param sdomain: source domain
        :param tdomain: target domain
        :return:
        """

        raise NotImplementedError

    @property
    def pos(self):
        pos_current = self.__mouse().cursor_pos_instant

        self.__accel = pos_current - self.__pos_prev
        self.__pos_prev = pos_current
        print(self.__pos, self.__accel)
        self.__pos += self.__accel
        return self.__pos


    @pos.setter
    def pos(self, v):
        """
        set cursor pos

        :param v: x, y coordinate
        :return:
        """
