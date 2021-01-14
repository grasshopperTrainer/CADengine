import numpy as np
from .error import StructuredDtypeError


class _UniformPusher:
    """
    Pushed array into OpenGL program to given location
    """
    def __init__(self, locations):
        """

        :param locations: uniform locations of a program
        """
        self.__locations = locations

    def push_all(self, cpu_bffr):
        """
        push data into bound ogl program

        :param cpu_bffr: `_CPUBffr`, data to push into ogl program
        :return:
        """

        for name, size, dtype, stride in cpu_bffr.interleave_props:
            loc = self.__locations[name]

    def numpy_dtype_translator(self, size, dtype):
        """
        translated ndarray dtype into uniform pusher

        :return: Opengl uniform pusher method
        """

