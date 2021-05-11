from ..base import Shape
import numpy as np


class SimpleGeoShape(Shape):
    def __init__(self, geo, clr):
        self.parent.update_viewer_cache(self, 'goid', self.goid.as_rgb_float())
        self.parent.update_viewer_cache(self, 'goid_flag', True)
        self._geo = self.geo = geo
        self._clr = self.clr = clr
        self._goid_flag = True

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, val):
        self._geo = val
        self.parent.update_viewer_cache(self, 'geo', val.T)

    @property
    def clr(self):
        return self._clr

    @clr.setter
    def clr(self, val):
        self._clr = val
        self.parent.update_viewer_cache(self, 'clr', val)

    @property
    def goid_flag(self):
        return self._goid_flag

    @goid_flag.setter
    def goid_flag(self, val):
        booled = bool(val)
        self._goid_flag = booled
        self.parent.update_viewer_cache(self, 'goid_flag', int(booled))

    def __dataset_size__(self):
        """
        :return: size of allocated dynamic memory for storing this shape
        """
        pass
