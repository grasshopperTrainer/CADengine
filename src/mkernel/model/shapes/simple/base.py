from mkernel.model.shapes.base import MetaShape
from mkernel.model.tree import ModelNode
import weakref as wr


class GeoShape(ModelNode, metaclass=MetaShape):
    def __init__(self, parent, geo, clr):
        super().__init__(parent)
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

