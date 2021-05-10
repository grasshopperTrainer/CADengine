from ..base import Shape
import numpy as np


class SimpleGeoShape(Shape):
    def __init__(self, geo, clr):
        print(self.goid.as_rgb_uint(), self.goid.as_raw())
        self.parent.update_viewer_cache(self, 'goid', self.goid.as_rgb_uint())
        self._geo = self.geo = geo
        self._clr = self.clr = clr
        self._active_goid = 1

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
    def active_goid(self):
        return self._active_goid

    @active_goid.setter
    def active_goid(self, val):
        booled = bool(val)
        self._active_goid = booled
        self.parent.update_viewer_cache(self, 'active_goid', int(booled))

    def __dataset_size__(self):
        """
        :return: size of allocated dynamic memory for storing this shape
        """
        pass
