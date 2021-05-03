from ..base import Shape

class SimpleGeoShape(Shape):
    def __init__(self, geo, clr):
        self.parent.update_viewer_cache(self, 'goid', self.goid)
        self._geo = self.geo = geo
        self._clr = self.clr = clr

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

    def __dataset_size__(self):
        """
        :return: size of allocated dynamic memory for storing this shape
        """
        pass
