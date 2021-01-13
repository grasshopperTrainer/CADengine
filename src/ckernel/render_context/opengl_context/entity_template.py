import abc
import weakref
from ckernel.render_context.opengl_context.context_stack import OpenglContextStack, OpenglUnboundError
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .entities import OGLEntity
from collections import defaultdict
from .error import *
import numpy as np



class OpenglEntityTemplate(metaclass=abc.ABCMeta):
    """
    Template knows properties and context relationship of Entities.
    """
    def __init__(self):
        """
        call by super to initiate self.__context_entity
        """
        self.__context_entity = weakref.WeakKeyDictionary()

    def get_entity(self):
        """
        return correct entity for the context

        Lazy initiating.
        If context is not given, entity of current context will be returned.
        :return: entity for current context
        """
        context = OpenglContextStack.get_current()
        if context.is_none:
            raise OpenglUnboundError
        # return if exists already
        if context in self.__context_entity:
            return self.__context_entity[context]
        # if not, create new and store
        with context:
            entity = self._create_entity()
            if not isinstance(entity, OGLEntity):
                raise Exception('creator method is not wrapped, check opengl_hooked')
            self.__context_entity[context] = entity
        return entity

    # does template having opengl operations good?
    # should template be exposed as concrete entity of should it simply manage entities?
    # explicity is preferred but maybe whole communication with gpu can be objectified more, being implicit here.
    @abc.abstractmethod
    def bind(self):
        """
        get context entity and bind

        Binding might need extra target input, so subclass has to implements its own.
        In any case, entity per context has to be retrived, so get_entity has to be called first
        :return:
        """
        self.get_entity().bind()

    @abc.abstractmethod
    def _create_entity(self):
        """
        called by self.get_entity(), create new entity for given context

        Implemented method assuming context is bound.
        :return: newly created entity
        """


# what if there are templates and reald entity and
# polymorphism over context is delt inside template?
class OGLPrgrmTemp(OpenglEntityTemplate):

    def __init__(self, vrtx_path=None, frgm_path=None):
        """
        currently only supporsts vertex and fragment shaders

        When other shaders are needed, attribute has to be appended.
        :param vrtx_path:
        :param frgm_path:
        """
        super().__init__()
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

    def bind(self):
        self.get_entity().bind()


class OGLArryBffrTemp(OpenglEntityTemplate):

    def __init__(self):
        super().__init__()
        self.__bffr_type = gl.GL_ARRAY_BUFFER

    def _create_entity(self):
        """
        :return:
        """
        return gl.glGenBuffers(1)

    def bind(self):
        self.get_entity().bind(self.__bffr_type)
