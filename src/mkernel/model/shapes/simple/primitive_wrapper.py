from gkernel.color.primitive import ClrRGBA
from .base import SimpleGeoShape


class Ray(SimpleGeoShape):

    @staticmethod
    def __dataset_size__():
        return 2


class Pnt(SimpleGeoShape):

    def __init__(self, geo):
        super().__init__(geo, clr=(1, 1, 1, 1))
        self._frm = self.frm = 's'
        self._dia = self.dia = 10

    @property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, val):
        self.parent.update_viewer_cache(self, 'dia', val)

    @property
    def frm(self):
        return self._frm

    @frm.setter
    def frm(self, val):
        self.parent.update_viewer_cache(self, 'frm', val)

    @staticmethod
    def __dataset_size__():
        return 1

    def __del__(self):
        print("shape Pnt gc")


class Vec(SimpleGeoShape):

    @staticmethod
    def __dataset_size__():
        return 1


class Lin(SimpleGeoShape):
    def __init__(self, geo):
        super().__init__(geo, clr=(1, 1, 1, 1))
        self._thk = self.thk = 1

    @property
    def thk(self):
        return self._thk

    @thk.setter
    def thk(self, val):
        self._thk = val
        self.parent.update_viewer_cache(self, 'thk', val)

    @staticmethod
    def __dataset_size__():
        return 2


class Tgl(SimpleGeoShape):
    def __init__(self, geo):
        super().__init__(geo, clr=(1, 1, 1, 1))

        self._clr_fill = self.clr_fill = ClrRGBA(1, 1, 1, 1)
        self._clr_edge = self.clr_edge = ClrRGBA(0, 0, 0, 1)
        self._edge_thk = self.edge_thk = 0.5

    @property
    def clr(self):
        return self._clr_fill, self._clr_edge

    @clr.setter
    def clr(self, val):
        self.clr_fill = val
        self.clr_edge = val

    @property
    def clr_fill(self):
        return self._clr_fill

    @clr_fill.setter
    def clr_fill(self, val):
        """
        set fill color

        :param val: color value, in default color format is RGBA
        :return:
        """
        self._clr_fill = val
        self.parent.update_viewer_cache(self, 'clr_fill', val)

    @property
    def clr_edge(self):
        return self._clr_edge

    @clr_edge.setter
    def clr_edge(self, val):
        """
        set edge color

        :param val: color value, in default color format is RGBA
        :return:
        """
        self._clr_edge = val
        self.parent.update_viewer_cache(self, 'clr_edge', val)

    @property
    def edge_thk(self):
        return self._edge_thk

    @edge_thk.setter
    def edge_thk(self, val):
        self._edge_thk = val
        self.parent.update_viewer_cache(self, 'edge_thk', val)

    @staticmethod
    def __dataset_size__():
        return 3


class Plin(SimpleGeoShape):
    def __init__(self, geo):
        """

        :param vs: number of vertices coordinate that form polyline
        """
        super().__init__(geo, clr=(1, 1, 1, 1))
        self.__thk = self.thk = 1

    @property
    def thk(self):
        return self.__thk

    @thk.setter
    def thk(self, val):
        self.__thk = val
        self.parent.update_viewer_cache(self, 'thk', val)

    def __dataset_size__(self):
        return self.geo.shape[0]
