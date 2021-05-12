import gkernel.dtype.geometric as gt
from .shapes.base import Shape

"""
Model is simply a data structure storing shapes
"""


class AModel(Shape):
    def __init__(self, modeler):
        """
        Shape tree.
        Simply record shape set. Compared with BModeler,
        this does not support winged edge data structure
        """
        self.__modeler = modeler
        self.__plane = gt.Pln()

    @property
    def modeler(self):
        return self.__modeler

    @property
    def plane(self):
        return self.__plane

    def update_viewer_cache(self, shape, arg_name, value):
        self.__modeler.update_viewer_cache(shape, arg_name, value)

    def __dataset_size__(self):
        return 0