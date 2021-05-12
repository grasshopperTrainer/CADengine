import os
from collections import defaultdict
import numpy as np
import ckernel.render_context.opengl_context.opengl_hooker as gl
from ..base import OGLMetaEntity
from ..error import *

from .shdr_parser import SimpleShdrParser
from .shdr_parser import VrtxAttrSchema, UfrmSchema
from global_tools.lazy import lazyProp
from ckernel.render_context.opengl_context.context_stack import get_current_ogl
from ckernel.render_context.opengl_context.entities.meta.frame import MetaFrameBffr


class MetaPrgrm(OGLMetaEntity):

    def __init__(self, vrtx_path=None, geom_path=None, frgm_path=None):
        """
        currently only supporsts vertex and fragment shaders

        When other shaders are needed, attribute has to be appended.
        :param vrtx_path:
        :param frgm_path:
        """
        self.__shdr_srcs = defaultdict(str)
        if vrtx_path is not None:
            self.__read_source(vrtx_path, gl.GL_VERTEX_SHADER)
        if geom_path is not None:
            self.__read_source(geom_path, gl.GL_GEOMETRY_SHADER)
        if frgm_path is not None:
            self.__read_source(frgm_path, gl.GL_FRAGMENT_SHADER)

    def __enter__(self):
        super().enter()
        # bind draw buffers
        frame = get_current_ogl().entity_stacker[MetaFrameBffr].peek_if()
        if frame:
            self.draw_bffr.bind()
        return self

    @lazyProp
    def vrtx_attr_schema(self) -> VrtxAttrSchema:
        return SimpleShdrParser.parse_vrtx_attrs(self.__shdr_srcs[gl.GL_VERTEX_SHADER][0])

    @lazyProp
    def ufrm_schema(self) -> UfrmSchema:
        return SimpleShdrParser.parse_uniforms(*[s for s, n in self.__shdr_srcs.values()])

    @lazyProp
    def frgm_outputs(self):
        return SimpleShdrParser.parse_frgm_outputs(*self.__shdr_srcs[gl.GL_FRAGMENT_SHADER])

    @lazyProp
    def draw_bffr(self):
        return self.frgm_outputs.create_draw_bffr()

    @lazyProp
    def __uniform_cache(self):
        return self.ufrm_schema.create_bffr_cache(size=1)

    @lazyProp
    def uniforms(self):
        return self.__uniform_cache.request_block(size=1)

    def __read_source(self, file_path, shdr_type):
        """
        read and store source data as string

        :param file_path: source file path
        :param shdr_type: string key for self.__shdr_srcs dict
        :return:
        """
        with open(file_path, mode='r') as file:
            name = os.path.split(file.name)[-1]
            self.__shdr_srcs[shdr_type] = (file.read(), name)

    def _create_entity(self):
        """
        compile shaders and create prgrm
        :return:
        """
        if not self.__shdr_srcs:
            raise ShaderCompileError('no shaders to compile')

        prgrm = gl.glCreateProgram()

        # create, compile, attach shaders
        shdrs = []
        for shdr_type, (src, name) in self.__shdr_srcs.items():
            if src:
                shdr = gl.glCreateShader(shdr_type)
                gl.glShaderSource(shdr, src)
                gl.glCompileShader(shdr)
                if not gl.glGetShaderiv(shdr, gl.GL_COMPILE_STATUS):
                    raise ShaderCompileError(shdr_type, name)
                gl.glAttachShader(prgrm, shdr)
                shdrs.append(shdr)
        # validate prgrm
        gl.glLinkProgram(prgrm)
        if not gl.glGetProgramiv(prgrm, gl.GL_LINK_STATUS):
            raise PrgrmLinkError(shdrs)

        # deleted used shaders if all is successful
        for shdr in shdrs:
            gl.glDeleteShader(shdr)
        return prgrm

    def push_uniforms(self):
        with self:
            self.__push_ufrms(self.__uniform_cache)

    def push_external_ufrm_cache(self, cache):
        with self:
            self.__push_ufrms(cache)

    def __push_ufrms(self, bffr_cache):
        """
        push data into bound ogl prgrm

        :param bffr_cache: `_BffrCache`, data to push into ogl prgrm
        :return:
        """
        for name, loc, shape, dtype, _, _ in bffr_cache.field_props:
            func = self.__parse_ufrm_func(shape, dtype)
            count = len(bffr_cache.array)
            transpose = gl.GL_TRUE
            value = bffr_cache.array[name]
            is_matrix = len(shape) == 2
            if is_matrix:
                func(loc, count, transpose, value)
            else:
                func(loc, count, value)

    @staticmethod
    def __parse_ufrm_func(shape, dtype):
        """
        translated ndarray dtype into OpenGL uniform function

        :param shape: shape of uniform data
        :param dtype: type of uniform data
        :return: Opengl uniform pusher method
        """
        # parse matrix
        if len(shape) == 1:
            m = ''
        else:
            m = 'Matrix'

        # parse dimension
        if shape == (1,):
            d = '1'
        elif shape == (2,):
            d = '2'
        elif shape == (3,):
            d = '3'
        elif shape == (4,):
            d = '4'

        elif shape == (2, 2):
            d = '2'
        elif shape == (3, 3):
            d = '3'
        elif shape == (4, 4):
            d = '4'

        elif shape == (3, 2):
            d = '2x3'
        elif shape == (2, 3):
            d = '3x2'
        elif shape == (4, 2):
            d = '2x4'
        elif shape == (2, 4):
            d = '4x2'
        elif shape == (4, 3):
            d = '3x4'
        elif shape == (3, 4):
            d = '4x3'
        else:
            raise NotImplementedError

        # parse dtype
        if dtype == np.float32:
            t = 'f'
        elif dtype == np.int32:
            t = 'i'
        else:
            raise NotImplementedError
        return eval(f"gl.glUniform{m}{d}{t}v")

    # attachers
    def attach_vrtx_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_VERTEX_SHADER)

    def attach_frgm_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_FRAGMENT_SHADER)

    def attach_geom_shdr(self, shader_path):
        self.__read_source(shader_path, gl.GL_GEOMETRY_SHADER)
