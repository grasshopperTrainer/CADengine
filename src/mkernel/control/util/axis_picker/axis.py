from mkernel.model.shapes.base import Shape
from mkernel.global_id_provider import GIDP


class Axis(Shape):
    def __init__(self, geo):
        self.viewer.update_cache(self, 'goid', self.goid.as_rgb_float())

        self._geo = self.geo = geo
        self._thk = self.thk = 16  # pixel thickness

    @property
    def geo(self):
        return self._geo

    @geo.setter
    def geo(self, ray):
        self._geo = ray
        self.viewer.update_cache(self, 'ori', ray.origin.T)
        self.viewer.update_cache(self, 'dir', ray.as_vec().T)

    @property
    def thk(self):
        return self._thk

    @thk.setter
    def thk(self, v):
        self._thk = v
        self.viewer.update_cache(self, 'thk', v)

    def __dataset_size__(self):
        return 1
