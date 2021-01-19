import numpy as np
from collections import defaultdict, namedtuple

import ckernel.render_context.opengl_context.opengl_hooker as gl

from .error import *
from .entity_factory import OGLEntityFactory
from .bffr_cache import BffrCache
import ctypes
import abc

"""
these are most likely intended to be used as descriptors
"""


class PrgrmFactory(OGLEntityFactory):

    def __init__(self, vrtx_path=None, geom_path=None, frgm_path=None):
        """
        currently only supporsts vertex and fragment shaders

        When other shaders are needed, attribute has to be appended.
        :param vrtx_path:
        :param frgm_path:
        """
        self.__shdr_srcs = defaultdict(None)
        if vrtx_path is not None:
            self.__read_source(vrtx_path, gl.GL_VERTEX_SHADER)
        if geom_path is not None:
            self.__read_source(geom_path, gl.GL_GEOMETRY_SHADER)
        if frgm_path is not None:
            self.__read_source(frgm_path, gl.GL_FRAGMENT_SHADER)

    def __read_source(self, file_path, shdr_type):
        """
        read and store source data as string

        :param file_path: source file path
        :param shdr_type: string key for self.__shdr_srcs dict
        :return:
        """
        with open(file_path, mode='r') as file:
            self.__shdr_srcs[shdr_type] = file.read()

    def _create_entity(self):
        """
        compile shaders and create program
        :return:
        """
        if not self.__shdr_srcs:
            raise ShaderCompileError('no shaders to compile')

        prgrm = gl.glCreateProgram()

        # create, compile, attach shaders
        shdrs = []
        for shdr_type, src in self.__shdr_srcs.items():
            if src is not None:
                shdr = gl.glCreateShader(shdr_type)
                gl.glShaderSource(shdr, src)
                gl.glCompileShader(shdr)
                if not gl.glGetShaderiv(shdr, gl.GL_COMPILE_STATUS):
                    raise ShaderCompileError(shdr_type)
                gl.glAttachShader(prgrm, shdr)
                shdrs.append(shdr)

        gl.glLinkProgram(prgrm)
        if not gl.glGetProgramiv(prgrm, gl.GL_LINK_STATUS):
            raise PrgrmLinkError(shdrs)

        # deleted used shaders
        for shdr in shdrs:
            gl.glDeleteShader(shdr)
        return prgrm

    # attachers
    def attach_vrtx_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_VERTEX_SHADER)

    def attach_frgm_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_FRAGMENT_SHADER)

    def attach_geom_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_GEOMETRY_SHADER)


class BffrFactory(OGLEntityFactory, metaclass=abc.ABCMeta):

    def __init__(self, attr_desc, attr_loc):
        """

        :param attr_desc: attribute description for ogl program in ndarray dtype format
                          ! use same dtype of CPUBffr cooperating
        :param attr_loc: (Int, ...), describe each field's attribute location in glsl program
        """
        # check attribute description
        try:
            self.__attr_desc = np.dtype(attr_desc)
        except Exception as e:
            raise e
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


class ArryBffrFactory(BffrFactory):
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
                                                 size=4,
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

    def __init__(self, dtype, size, is_descriptor=True):
        """
        create master array

        :param dtype: (list, tuple), numpy structured dtype description
        :param is_descriptor:
        """
        # check dtype description
        try:
            self.__dtype = np.dtype(dtype)
            if self.__dtype.fields is None:
                raise StructuredDtypeError
        except:
            raise StructuredDtypeError
        self.__cache_size = size

    def _create_entity(self):
        return BffrCache(self.__dtype, size=self.__cache_size)
