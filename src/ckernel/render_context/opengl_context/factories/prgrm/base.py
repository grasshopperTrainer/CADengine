from collections import defaultdict
import ckernel.render_context.opengl_context.opengl_hooker as gl

from ..base import OGLEntityFactory
from ..error import *

from .shdr_parser import SimpleShdrParser
from .shdr_parser import VrtxAttrSchema, UfrmSchema


class PrgrmFactory(OGLEntityFactory):

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
        # glsl parameter skemas
        self.__va_skema = None
        self.__uf_skema = None

    @property
    def vrtxattr_schema(self) -> VrtxAttrSchema:
        return self.__initget_prgrm_params()[0]

    @property
    def ufrm_schema(self) -> UfrmSchema:
        return self.__initget_prgrm_params()[1]

    def __initget_prgrm_params(self):
        """
        return program parameters or initiate and return

        :return: (VrtxAttrSkema, UfrmSkema)
        """
        if self.__va_skema is None:
            self.__va_skema = SimpleShdrParser.parse_vrtx_attrs(self.__shdr_srcs[gl.GL_VERTEX_SHADER][1])
            self.__uf_skema = SimpleShdrParser.parse_uniforms(*[s for n, s in self.__shdr_srcs.values()])
        return self.__va_skema, self.__uf_skema

    def __read_source(self, file_path, shdr_type):
        """
        read and store source data as string

        :param file_path: source file path
        :param shdr_type: string key for self.__shdr_srcs dict
        :return:
        """
        with open(file_path, mode='r') as file:
            self.__shdr_srcs[shdr_type] = (file.name, file.read())

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
        for shdr_type, (name, src) in self.__shdr_srcs.items():
            if src:
                shdr = gl.glCreateShader(shdr_type)
                gl.glShaderSource(shdr, src)
                gl.glCompileShader(shdr)
                if not gl.glGetShaderiv(shdr, gl.GL_COMPILE_STATUS):
                    raise ShaderCompileError(name, shdr_type)
                gl.glAttachShader(prgrm, shdr)
                shdrs.append(shdr)
        # validate prgrm
        gl.glLinkProgram(prgrm)
        if not gl.glGetProgramiv(prgrm, gl.GL_LINK_STATUS):
            raise PrgrmLinkError(shdrs)

        # check for enforced layout declaration just once
        # checking it after link success reduces work
        va, uf = self.__initget_prgrm_params()
        prgrm.attach_vrtxattr_skema(va)
        prgrm.attach_ufrm_skema(uf)

        # deleted used shaders if all is successful
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
