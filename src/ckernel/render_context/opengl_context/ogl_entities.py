"""
! controlled through `opengl_hooker`
these are simple wrappers for OpenGL objects purposed for abstraction of
common operations like binding, deleting
"""
import abc
import numpy as np
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .context_stack import get_current_ogl
from ckernel.context_spec import ContextSpec


class OGLEntity(metaclass=abc.ABCMeta):
    """
    OpenGL id holder.
    """
    def __init__(self, id):
        self.__id = id

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        """
        :return: id of ogl object
        """
        # for class using '_Name' pattern
        return getattr(self, f"{self.__class__.__name__}__id")


    @abc.abstractmethod
    def bind(self):
        """
        bind ogl object
        :return:
        """
        pass

    # not abstractmethod
    def unbind(self):
        """
        unbind ogl object

        ! default policy is 'bind-only' so this method is not for all but
        for example, vertex array object needs unbind to be safe from oncoming buffer bindings
        :return:
        """
        pass

    @abc.abstractmethod
    def delete(self):
        """
        delete obl object
        :return:
        """
        pass

    @property
    @abc.abstractmethod
    def is_shared(self):
        """
        return if entity is shared along shared context
        :return:
        """
        pass

    # binding context implement into context manager
    def __enter__(self):
        et = get_current_ogl().entity_tracker

        if not et.stack.is_empty(self.__class__) and et.stack.peek(self.__class__) == self:
            et.stack.push(self)
        else:
            et.stack.push(self)
            self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        et = get_current_ogl().entity_tracker
        et.stack.pop(self.__class__)
        # control over matryoshka context
        # follow bind-only policy
        if not et.stack.is_empty(self.__class__):
            entity = et.stack.peek(self.__class__)
            entity.bind()
        else:
            # only if there is no entity to return binding
            self.unbind()


# use under bar
class _Prgrm(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def __str__(self):
        return f"<Program: {self.__id}>"

    def bind(self):
        """
        bind prgrm

        Use after ogl context binding
        :return:
        """
        gl.glUseProgram(self.__id)

    def delete(self):
        gl.glDeleteProgram(self)

    @property
    def is_shared(self):
        return ContextSpec().SHARED_PROGRAM


class _Shdr(OGLEntity):
    def __init__(self, id, typ):
        self.__id = id
        self.__typ = typ

    def bind(self):
        """
        no bind

        :return:
        """
        pass

    def delete(self):
        """
        delete
        If shader is only for a single prgrm, deletion is advised after successful prgrm link.
        :return:
        """
        gl.glDeleteShader(self)

    def __str__(self):
        return f"<Shader: {self.__id}>"

    @property
    def is_shared(self):
        return ContextSpec().SHARED_SHADER


class _Bffr(OGLEntity):
    def __init__(self, id):
        self.__id = id
        self.__target = None
        self.__usage = gl.GL_DYNAMIC_DRAW
        self.__cache = None

    def __str__(self):
        return f"<Buffer: {self.__id}>"

    # @property
    # def cache(self):
    #     return self.__cache

    def bind(self):
        gl.glBindBuffer(self.__target, self.__id)

    def delete(self):
        gl.glDeleteBuffers(1, self)

    def push_cache(self):
        """
        push whole data of given array into ogl buffer

        :return:
        """
        if self.__cache is None:
            raise NotImplementedError

        with self as bffr:
            gl.glBufferData(target=bffr.__target,
                            size=self.__cache.active_bytesize,
                            data=self.__cache.array,
                            usage=bffr.__usage)
            # unbinding needed? does vao affected by vbo binding before its binding?

    def set_target(self, target):
        self.__target = target

    def set_usage(self, usage):
        self.__usage = usage

    def set_cache(self, cache):
        self.__cache = cache

    @property
    def is_shared(self):
        return ContextSpec().SHARED_BUFFER


class _VrtxArry(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def __str__(self):
        return f"<VAO: {self.__id}>"

    def bind(self):
        gl.glBindVertexArray(self.__id)

    def unbind(self):
        gl.glBindVertexArray(0)

    def delete(self):
        gl.glDeleteVertexArrays(1, self)

    @property
    def is_shared(self):
        return ContextSpec().SHARED_VERTEX_ARRAY


class _FrameBffr(OGLEntity):
    def __init__(self, id, target):
        self.__id = id
        self.__target = None

    def __str__(self):
        return f"<FrameBffr: {self.__id}>"

    def set_target(self, target):
        self.__target = target

    def bind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def delete(self):
        gl.glDeleteFramebuffers(1, self.__id)

    @property
    def is_shared(self):
        return ContextSpec().SHARED_FRAME_BUFFER


class _RenderBffr(OGLEntity):
    def __init__(self, id, target):
        self.__id = id
        self.__target = target

    def __str__(self):
        return f"<RenderBffr: {self.__id}>"

    def bind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.__id)

    def unbind(self):
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

    def delete(self):
        raise NotImplementedError

    @property
    def is_shared(self):
        return ContextSpec().SHARED_RENDER_BUFFER


class _Texture(OGLEntity):
    def __init__(self, id):
        self.__id = id
        self.__target = None

    def __str__(self):
        return f"<Texture: {self.__id}>"

    def set_target(self, target):
        self.__target = target

    def bind(self):
        if not self.__target:
            raise ValueError('texture target e.g. GL_TEXTURE_2D not set')
        gl.glBindTexture(self.__target, self.__id)

    def unbind(self):
        gl.glBindTexture(self.__target, 0)

    def delete(self):
        gl.glDeleteTextures(self.__target)

    @property
    def is_shared(self):
        return ContextSpec().SHARED_TEXTURE