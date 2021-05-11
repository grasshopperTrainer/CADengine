import numpy as np
import abc
from collections import namedtuple
import ctypes

from ckernel.render_context.opengl_context.entities.meta.base import OGLMetaEntity
from ckernel.render_context.opengl_context.bffr_cache import BffrCache
from ckernel.render_context.opengl_context.translators import npdtype_to_gldtype
from ckernel.constants import PRIMITIVE_RESTART_VAL as PRV
import ckernel.render_context.opengl_context.opengl_hooker as gl

from .error import *


class _MetaBffr(OGLMetaEntity, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def target(self):
        """
        ! abstract attribute

        :return: gl render target constant, ex) gl.GL_ARRAY_BUFFER, gl.GL_ELEMENT_ARRAY_BUFFER
        """
        pass

    @property
    @abc.abstractmethod
    def cache(self) -> BffrCache:
        """
        :return: cache instance.
        """

    def push_cache(self):
        self.get_concrete().push_cache()


class MetaVrtxBffr(_MetaBffr):
    """
    Buffer of GL_ARRAY_BUFFER target
    """

    def __init__(self, attr_desc: np.dtype, attr_locs: (list, tuple)):
        """

        :param attr_desc: attribute description for ogl prgrm in ndarray dtype format
                          ! use same dtype of CPUBffr cooperating
        :param attr_locs: (Int, ...), describe each field's attribute location of glsl prgrm
        """
        # check attribute description being numpy dtype
        if not (isinstance(attr_desc, np.dtype) and attr_desc.fields is not None):
            raise StructuredDtypeError
        self.__attr_desc = attr_desc

        # check attribute location
        if not (isinstance(attr_locs, (tuple, list)) and all(isinstance(l, int) for l in attr_locs)):
            raise TypeError('attr_loc should be (tuple, list) of int value')
        if len(set(attr_locs)) != len(attr_locs):
            raise ValueError('attr_loc has to have unique values')
        if len(self.__attr_desc.fields) != len(attr_locs):
            raise ValueError('all attribute has to have location value')
        self.__attr_locs = attr_locs
        # cache shareness
        # deoide whether to use single cache for all entities per context
        self.__cache = BffrCache(attr_desc, attr_locs)

    def _create_entity(self):
        """
        :return:
        """
        bffr = gl.glGenBuffers(1)
        bffr.set_target(self.target)
        bffr.set_cache(self.__cache)
        return bffr

    @property
    def target(self):
        return gl.GL_ARRAY_BUFFER

    @property
    def attr_loc(self):
        return self.__attr_locs

    @property
    def attr_props(self):
        """
        set of property describing interleaveness of the array

        :return: list(namedtuple(),...)
        """
        tuples = []
        ntuple = namedtuple('interleave_prop', 'name, loc, size, dtype, stride, offset')
        stride = self.__attr_desc.itemsize
        for (name, (dtype, offset)), loc in zip(self.__attr_desc.fields.items(), self.__attr_locs):
            # for shape 1 not having subdtype
            if dtype.subdtype is None:
                size = 1
            else:
                dtype, shape = dtype.subdtype
                size = 1
                for s in shape:
                    size *= s
            tuples.append(ntuple(name, loc, size, dtype, stride, offset))
        return tuple(tuples)

    @property
    def cache(self):
        return self.__cache


class MetaIndxBffr(_MetaBffr):
    """
    Buffer of GL_ELEMENT_ARRAY_BUFFER
    """

    def __init__(self, dtype: str):
        """

        :param dtype: str, describe IBO dtype, one of (uint, ushort, ubyte)
        """
        self.__cache = BffrCache(np.dtype([('idx', dtype)]), (0,), def_val=PRV)
        self.__cache.fill_array(PRV)

    @property
    def target(self):
        return gl.GL_ELEMENT_ARRAY_BUFFER

    @property
    def cache(self):
        return self.__cache

    def _create_entity(self):
        """
        :return:
        """
        bffr = gl.glGenBuffers(1)
        bffr.set_target(self.target)
        bffr.set_cache(self.__cache)
        return bffr


class MetaVrtxArry(OGLMetaEntity):

    def __init__(self, *bffrs, indx_bffr=None):
        """

        :param bffrs: ! OGLBffrFactory not OGLBffr
        """
        self.__bffr_factories = []
        self.__bffr_factories += list(bffrs)
        self.__indx_bffr_factory = indx_bffr

    def _create_entity(self):
        """
        create vertex array and bind attribute pointers
        :return:
        """
        vao = gl.glGenVertexArrays(1)
        with vao:
            # for each buffer, bind attribute pointer in order
            for bffr_fct in self.__bffr_factories:
                with bffr_fct.get_concrete():
                    for _, loc, size, dtype, stride, offset in bffr_fct.attr_props:
                        gldtype = npdtype_to_gldtype(dtype)
                        offset_ptr = ctypes.c_void_p(offset)
                        print(_, loc, size, (dtype, gldtype), stride, (offset, offset_ptr))

                        gl.glEnableVertexAttribArray(loc)  # ! dont forget
                        if gldtype in (gl.GL_BYTE, gl.GL_UNSIGNED_BYTE, gl.GL_SHORT, gl.GL_UNSIGNED_SHORT, gl.GL_INT,
                                       gl.GL_UNSIGNED_INT):
                            gl.glVertexAttribIPointer(loc,  # index
                                                      size,  # size
                                                      gldtype,  # type
                                                      stride,  # stride
                                                      offset_ptr)  # pointer
                        elif gldtype == gl.GL_DOUBLE:
                            gl.glVertexAttribLPointer(loc,
                                                      size,
                                                      gldtype,
                                                      stride,
                                                      offset_ptr)
                        elif gldtype == gl.GL_BOOL:  # but shader is uncompilable with bool type...
                            gl.glVertexAttribIPointer(loc,
                                                      size,
                                                      gl.GL_UNSIGNED_BYTE,
                                                      stride,
                                                      offset_ptr)
                        else:
                            gl.glVertexAttribPointer(index=loc,
                                                     size=size,
                                                     type=gldtype,
                                                     normalized=gl.GL_FALSE,
                                                     stride=stride,
                                                     pointer=offset_ptr)  # ! must feed c_void_p
            # bind ibo with vao
            if self.__indx_bffr_factory:
                ibo = self.__indx_bffr_factory.get_concrete()
                ibo.bind()
        return vao

    def attach_arry_bffr(self, bffr):
        self.__bffr_factories.append(bffr)
