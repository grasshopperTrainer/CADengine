from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
from mkernel.global_id_provider import GIDP
import numpy as np

"""
! shpae is a renderable thing.
! not all geometry is natively shape.
! think of plane. Its a geometric data but is not !seen!.
! it should be rendered as a box or collection of lines
! `Ray` is also natively not a `Shape`. It may has to be rendered simply as a long `line`.
! distinction: 'native shape, nonnative shape'
"""

import abc
#
#
# class Shape(metaclass=abc.ABCMeta):
#     @abc.abstractmethod
#     def delete(self):
#         """
#         explicitly release all attributes
#
#         :return:
#         """
#         pass
#
#     def delete_force(self):
#         """
#         explicitly release all attributes
#         and try to remove all references
#
#         :return:
#         """
#         raise NotImplementedError
#
#
# class NongeoShape(Shape):
#     pass


class MetaShape(type):
    def __new__(cls, name, base, dic):
        """
        metaclass for shape, add property for goid and model

        :param name:
        :param base:
        :param dic:
        """
        my_type = super().__new__(cls, name, base, dic)
        # add hidden property
        my_type.__model = None
        my_type.__goid = None
        my_type.goid = property(fget=cls.goid)
        my_type.model = property(fget=cls.model)
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
        obj.__model = kwargs.pop('model')
        obj.__goid = GIDP().register_entity(obj)
        obj.__init__(*args, **kwargs)
        return obj

    @staticmethod
    def goid(self):
        return self.__goid

    @staticmethod
    def model(self):
        return self.__model
