import gkernel.dtype.geometric.primitive as gt
from mkernel.model.shapes.base import Shape


class Pln(Shape):
    def __init__(self, geo: gt.Pln):
        self.parent.update_viewer_cache(self, 'goid', self.goid.as_rgb_float())
        self._geo = self.geo = geo
        self._len = self.len = 0.25  # think it as % of ndc

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, val):
        self._geo = val
        t = val.T
        self.parent.update_viewer_cache(self, 'ori', t[0])
        self.parent.update_viewer_cache(self, 'x', t[1])
        self.parent.update_viewer_cache(self, 'y', t[2])
        self.parent.update_viewer_cache(self, 'z', t[3])

    @property
    def len(self):
        return self._len

    @len.setter
    def len(self, val):
        self._len = val
        self.parent.update_viewer_cache(self, 'len', val)

    @staticmethod
    def __dataset_size__():
        return 1
