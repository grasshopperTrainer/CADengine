from mkernel.model.shapes.base import MetaShape


class GeoShape(metaclass=MetaShape):
    def __init__(self, geo, clr):
        self._geo = self.geo = geo
        self._clr = self.clr = clr

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, val):
        self._geo = val
        self.model.update_viewer_cache(self, 'geo', val.T)

    @property
    def clr(self):
        return self._clr

    @clr.setter
    def clr(self, val):
        self._clr = val
        self.model.update_viewer_cache(self, 'clr', val)