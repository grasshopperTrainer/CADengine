from mkernel.shapes.base import GeoShape
from mkernel.global_id_provider import GIDP
import numpy as np


class SimpleGeoShape(GeoShape):
    """
    Those using single vertex block and single index block
    """

    def __init__(self, model, vrtx_block, indx_block, goid):
        self._model = model
        self._vrtx_block = vrtx_block
        self._indx_block = indx_block
        self.__goid = goid

        self._geo = None
        self._clr = None

        self.__do_render_id = True

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, v):
        self._vrtx_block['vtx'] = v.T
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
        self._vrtx_block['clr'] = v
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
            self._vrtx_block['oid'] = self.__goid
        else:
            self._vrtx_block['oid'] = 0, 0, 0, 0

    def delete(self):
        self._vrtx_block.release()
        self._indx_block.release()

        GIDP().deregister(self)
        self._model.remove_shape(self)

        for k, v in self.__dict__.items():
            setattr(self, k, None)
