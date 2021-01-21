import numpy as np
from collections import namedtuple

import ckernel.render_context.opengl_context.opengl_hooker as gl

from ckernel.render_context.opengl_context.factories.error import *
from ckernel.render_context.opengl_context.factories.base import OGLEntityFactory
from ckernel.render_context.opengl_context.bffr_cache import BffrCache
import ctypes
import abc

"""
these are most likely intended to be used as descriptors
"""



class BffrFactory(OGLEntityFactory, metaclass=abc.ABCMeta):

    def __init__(self, attr_desc, attr_loc):
        """

        :param attr_desc: attribute description for ogl prgrm in ndarray dtype format
                          ! use same dtype of CPUBffr cooperating
        :param attr_loc: (Int, ...), describe each field's attribute location in glsl prgrm
        """
        # check attribute description being numpy dtype
        if not (isinstance(attr_desc, np.dtype) and attr_desc.fields is not None):
            raise StructuredDtypeError
        self.__attr_desc = attr_desc

        # check attribute location
        if not (isinstance(attr_loc, (tuple, list)) and all(isinstance(l, int) for l in attr_loc)):
            raise TypeError('attr_loc should be (tuple, list) of int value')
        if len(set(attr_loc)) != len(attr_loc):
            raise ValueError('attr_loc has to have unique values')
        if len(self.__attr_desc.fields) != len(attr_loc):
            raise ValueError('all attribute has to have location value')
        self.__attr_loc = attr_loc

    @property
    @abc.abstractmethod
    def target(self):
        """
        ! abstract attribute

        :return: gl render target constant, ex) gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER
        """
        pass

    @property
    def attr_loc(self):
        return self.__attr_loc

    def _create_entity(self):
        """
        :return:
        """
        obj = gl.glGenBuffers(1)
        obj.set_target(self.target)
        return obj

    @property
    def attr_props(self):
        """
        set of property describing interleaveness of the array

        :return: list(namedtuple(),...)
        """
        tuples = []
        ntuple = namedtuple('interleave_prop', 'name, loc, size, dtype, stride, offset')
        stride = self.__attr_desc.itemsize
        for (name, (dtype, offset)), loc in zip(self.__attr_desc.fields.items(), self.__attr_loc):
            # for shape 1 not having subdtype
            if dtype.subdtype is not None:
                dtype, shape = dtype.subdtype
            else:
                shape = (1,)
            tuples.append(ntuple(name, loc, shape[0], dtype, stride, offset))
        return tuple(tuples)


class VrtxBffrFactory(BffrFactory):
    """
    Descriptor

    Buffer of GL_ARRAY_BUFFER target
    """

    @property
    def target(self):
        return gl.GL_ARRAY_BUFFER


class VrtxArryFactory(OGLEntityFactory):

    def __init__(self, *bffr_facs):
        """

        :param bffr_facs: ! OGLBffrFactory not OGLBffr
        """
        self.__bffr_factories = []
        self.__bffr_factories += list(bffr_facs)

    def _create_entity(self):
        """
        create vertex array and bind attribute pointers
        :return:
        """
        vao = gl.glGenVertexArrays(1)
        with vao:
            # for each buffer, bind attribute pointer in order
            for bffr_fct in self.__bffr_factories:
                with bffr_fct.get_entity():
                    for _, loc, size, dtype, stride, offset in bffr_fct.attr_props:
                        gl.glEnableVertexAttribArray(loc)  # ! dont forget
                        gl.glVertexAttribPointer(index=loc,
                                                 size=size,
                                                 type=self.translate_ndtype(dtype),
                                                 normalized=gl.GL_FALSE,
                                                 stride=stride,
                                                 pointer=ctypes.c_void_p(offset))  # ! must feed c_void_p
        return vao

    @staticmethod
    def translate_ndtype(dtype):
        """
        translates numpy dtype into OpenGL dtype
        :param dtype:
        :return:
        """
        if not isinstance(dtype, np.dtype):
            raise TypeError

        if dtype == np.bool:
            return gl.GL_BOOL

        elif dtype == np.byte:
            return gl.GL_BYTE
        elif dtype == np.ubyte:
            return gl.GL_UNSIGNED_BYTE

        elif dtype in (np.short, np.int16):
            return gl.GL_SHORT
        elif dtype in (np.ushort, np.uint16):
            return gl.GL_UNSIGNED_SHORT
        elif dtype in (np.int, np.int32):
            return gl.GL_INT
        elif dtype in (np.uint, np.uint32):
            return gl.GL_UNSIGNED_INT

        elif dtype == np.float16:
            return gl.GL_HALF_FLOAT
        elif dtype == np.float32:
            return gl.GL_FLOAT
        elif dtype == np.float64:
            return gl.GL_DOUBLE

        else:
            raise ValueError('incomprehensible numpy dtype', dtype)

    def attach_arry_bffr(self, bffr):
        self.__bffr_factories.append(bffr)


class BffrCacheFactory(OGLEntityFactory):
    """
    Provide `_CPUBffr` object
    """

    def __init__(self, dtype, size):
        """
        create master array

        :param dtype: (list, tuple), numpy structured dtype description
        """
        # check dtype description
        if not (isinstance(dtype, np.dtype) and dtype.fields is not None):
            raise StructuredDtypeError
        self.__dtype = dtype
        self.__cache_size = size

    def _create_entity(self):
        return BffrCache(self.__dtype, size=self.__cache_size)
