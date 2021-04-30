from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
import numpy as np
from mkernel.model.tree import ModelNode


"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""

class MetaShape(type):
    def __new__(cls, name, base, dic):
        """
        metaclass for shape, add property for goid and model

        :param name:
        :param base:
        :param dic:
        """
        if '__dataset_size__' not in dic:
            raise AttributeError(f"<{name}> must provide method '__dataset_size__'")

        my_type = super().__new__(cls, name, base, dic)
        # add hidden property
        my_type.__goid = None
        my_type.goid = property(fget=cls.goid)
        return my_type

    def __call__(cls, *args, **kwargs):
        """
        add implicit attributes

        :param args:
        :param kwargs:
        :return:
        """
        obj = cls.__new__(cls)
        # force attribute
        obj.__goid = GIDP().register_entity(obj)
        obj.__init__(*args, **kwargs)
        return obj

    @staticmethod
    def goid(self):
        return self.__goid


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
        self.parent.update_viewer_cache(self, 'geo', val)

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