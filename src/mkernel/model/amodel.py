import gkernel.dtype.geometric as gt

"""
Model is simply a data structure storing shapes
"""


class AModel:
    def __init__(self, modeler):
        """
        Shape tree.
        Simply record shape set. Compared with BModeler,
        this does not support winged edge data structure
        """
        self.__modeler = modeler
        self.__shapes = set()
        self.__plane = gt.Pln()

    @property
    def shapes(self):
        return self.__shapes

    @property
    def plane(self):
        return self.__plane

    def update_viewer_cache(self, shape, arg_name, value):
        self.__modeler.update_viewer_cache(shape, arg_name, value)
