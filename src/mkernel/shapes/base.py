from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
import numpy as np

"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""

import abc


class Shape(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def delete(self):
        """
        explicitly release all attributes

        :return:
        """
        pass

    def delete_force(self):
        """
        explicitly release all attributes
        and try to remove all references

        :return:
        """
        raise NotImplementedError


class NongeoShape(Shape):
    pass


class GeoShape(Shape):
    """
    Those using single vertex block and single index block
    """

    def __init__(self, goid, vrtx_block=(), indx_block=()):
        if not all(isinstance(i, (list, tuple)) or i is None for i in (vrtx_block, indx_block)):
            raise TypeError
        self._vrtx_block = tuple(vrtx_block)
        self._indx_block = tuple(indx_block)
        self.__goid = goid

        self._geo = None
        self._clr = None

        self.__do_render_id = True

    @property
    def vrtx_block(self):
        if len(self._vrtx_block) == 1:
            return self._vrtx_block[0]
        return self._vrtx_block

    @property
    def indx_block(self):
        if len(self._indx_block) == 1:
            return self._indx_block[0]
        return self._indx_block

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, v):
        self._vrtx_block[0]['vtx'] = v.T
        if self._geo is None:
            self._geo = v
        else:
            self._geo[:] = v

    @property
    def clr(self):
        return self._clr

    @clr.setter
    def clr(self, v):
        if not isinstance(v, (list, tuple, np.ndarray)):
            raise TypeError
        self._vrtx_block[0]['clr'] = v
        if self._clr is None:
            self._clr = v
        else:
            self._clr[:] = v

    @property
    def do_render_id(self):
        return self.__do_render_id

    @do_render_id.setter
    def do_render_id(self, v):
        if not isinstance(v, bool):
            raise TypeError
        self.__do_render_id = v
        if v:
            self._vrtx_block[0]['oid'] = self.__goid
        else:
            self._vrtx_block[0]['oid'] = 0, 0, 0, 0

    def delete(self):
        for block in (*self._vrtx_block, *self._indx_block):
            block.release()

        GIDP().deregister(self)

        for k, v in self.__dict__.items():
            setattr(self, k, None)
