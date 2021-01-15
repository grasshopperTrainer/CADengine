import numpy as np
from collections import defaultdict, namedtuple

import ckernel.render_context.opengl_context.opengl_hooker as gl

from .error import *
from .entity_factory import OGLEntityFactory
from .bffr_cache import BffrCache


"""
these are most likely intended to be used as descriptors
"""


class PrgrmFactory(OGLEntityFactory):

    def __init__(self, vrtx_path=None, frgm_path=None, is_descriptor=True):
        """
        currently only supporsts vertex and fragment shaders

        When other shaders are needed, attribute has to be appended.
        :param vrtx_path:
        :param frgm_path:
        """
        super().__init__(is_descriptor)
        self.__shdr_srcs = defaultdict(None)
        self.__read_source(vrtx_path, gl.GL_VERTEX_SHADER)
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
        prgrm = gl.glCreateProgram()

        # create, compile, attach shaders
        shdrs = []
        for shdr_type, src in self.__shdr_srcs.items():
            if src is not None:
                shdr = gl.glCreateShader(shdr_type)
                gl.glShaderSource(shdr, src)
                gl.glCompileShader(shdr)
                if not gl.glGetShaderiv(shdr, gl.GL_COMPILE_STATUS):
                    raise ShaderCompileError()
                gl.glAttachShader(prgrm, shdr)
                shdrs.append(shdr)

        gl.glLinkProgram(prgrm)
        if not gl.glGetProgramiv(prgrm, gl.GL_LINK_STATUS):
            raise PrgrmLinkError()

        # deleted used shaders
        for shdr in shdrs:
            gl.glDeleteShader(shdr)
        return prgrm


class BffrFactory(OGLEntityFactory):

    def __init__(self, attr_desc, is_descriptor=True):
        """

        :param attr_desc: attribute description for ogl program in ndarray dtype format
                          ! use same dtype of CPUBffr cooperating

        :param is_descriptor: bool, determine whether to create entity per context
                               ! If False, it is likely returned entity will cause context error.
                               Make it False under provision of user-controlled context binding.
        """
        super().__init__(is_descriptor)
        try:
            np.dtype(attr_desc)
        except Exception as e:
            raise e
        self.__attr_desc = np.dtype(attr_desc)  # normalize

    @property
    def target(self):
        return getattr(self, f"_{self.__class__.__name__}__target")

    def _create_entity(self):
        """
        :return:
        """
        obj = gl.glGenBuffers(1)
        obj.set_target(self.target)
        return obj

    @property
    def interleave_props(self):
        """
        set of property describing interleaveness of the array

        :return: list(namedtuple(),...)
        """
        tuples = []
        np = namedtuple('interleave_prop', 'name, size, dtype, stride')
        for name, (dtype, stride) in self.__attr_desc.fields.items():
            dtype, shape = dtype.subdtype
            tuples.append(np(name, shape[0], dtype, stride))
        return tuple(tuples)


class ArryBffrFactory(BffrFactory):
    """
    Descriptor

    Buffer of GL_ARRAY_BUFFER target
    """
    __target = gl.GL_ARRAY_BUFFER


class VrtxArryFactory(OGLEntityFactory):

    def __init__(self, *bffr_facs, is_descriptor=True):
        """

        :param bffr_facs: ! OGLBffrFactory not OGLBffr
        :param is_descriptor:
        """
        super().__init__(is_descriptor)
        self.__bffr_facs = bffr_facs

    def _create_entity(self):
        """
        create vertex array and bind attribute pointers
        :return:
        """
        attr_idx = 0
        vao = gl.glGenVertexArrays(1)
        with vao:
            # for each buffer, bind attribute pointer in order
            for bffr_fct in self.__bffr_facs:
                with bffr_fct.get_entity():
                    for _, size, dtype, stride in bffr_fct.interleave_props:
                        gl.glVertexAttribPointer(index=attr_idx,
                                                 size=size,
                                                 type=self.numpy_dtype_translator(dtype),
                                                 normalized=False,
                                                 stride=stride,
                                                 pointer=0)
                        attr_idx += 1
        return vao

    @staticmethod
    def numpy_dtype_translator(dtype):
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
            raise ValueError('incomprehensible numpy dtype')


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
        super().__init__(is_descriptor)
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