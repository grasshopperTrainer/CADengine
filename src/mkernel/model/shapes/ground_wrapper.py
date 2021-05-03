from .base import Shape
from gkernel.color.primitive import ClrRGBA


class Ground(Shape):
    def __init__(self, color):
        self._clr = self.clr = ClrRGBA(*color)

    @property
    def clr(self):
        return self._clr

    @clr.setter
    def clr(self, val):
        self._clr = val
        self.parent.update_viewer_cache(self, 'clr', val)

    @staticmethod
    def __dataset_size__():
        return 4