"""
! controlled through `opengl_hooker`
these are simple wrappers for OpenGL objects purposed for abstraction of
common operations like binding, deleting
"""
import abc
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .context_stack import get_current_context


class OGLEntity(metaclass=abc.ABCMeta):
    """
    OpenGL id holder.
    """
    def __init__(self, id):
        self.__id = id

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
    def _bind(self):
        """
        bind ogl object
        :return:
        """
        pass

    # not abstractmethod
    def _unbind(self):
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

    # binding context implement into context manager
    def __enter__(self):
        entity_stack = get_current_context().entities.stack
        if not entity_stack.is_empty(self.__class__) and entity_stack.get_current(self.__class__) == self:
            entity_stack.push(self)
        else:
            entity_stack.push(self)
            self._bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        entities = get_current_context().entities
        entities.stack.pop(self.__class__)
        # control over matryoshka context
        # follow bind-only policy
        if not entities.stack.is_empty(self.__class__):
            entity = entities.stack.get_current_byclass(self.__class__)
            entity.bind()
        else:
            # only if there is no entity to return binding
            self._unbind()


# use under bar
class _Prgrm(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def _bind(self):
        """
        bind program

        Use after ogl context binding
        :return:
        """
        gl.glUseProgram(self.__id)

    def delete(self):
        gl.glDeleteProgram(self)

    def __str__(self):
        return f"<Program: {self.__id}>"


class _Shdr(OGLEntity):
    def __init__(self, typ, id):
        self.__id = id
        self.__typ = typ

    def _bind(self):
        """
        no bind

        :return:
        """
        pass

    def delete(self):
        """
        delete
        If shader is only for a single program, deletion is advised after successful program link.
        :return:
        """
        gl.glDeleteShader(self)

    def __str__(self):
        return f"<Shader: {self.__id}>"


class _Bffr(OGLEntity):
    def __init__(self, id):
        self.__id = id
        self.__target = None
        self.__usage = gl.GL_DYNAMIC_DRAW

    def __str__(self):
        return f"<Buffer: {self.__id}>"

    def _bind(self):
        gl.glBindBuffer(self.__target, self.__id)

    def delete(self):
        gl.glDeleteBuffers(1, self)

    def push_all(self, cpu_bffr):
        """
        push whole data of given array into ogl buffer

        :param cpu_bffr: `_CPUBffr`, data to push into ogl buffer
        :return:
        """
        with self as bffr:
            gl.glBufferData(target=bffr.__target,
                            size=cpu_bffr.bytesize,
                            data=cpu_bffr.array,
                            usage=bffr.__usage)
            # unbinding needed? does vao affected by vbo binding before its binding?

    def set_target(self, target):
        self.__target = target

    def set_usage(self, usage):
        self.__usage = usage


class _VrtxArry(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def _bind(self):
        gl.glBindVertexArray(self.__id)

    def _unbind(self):
        gl.glBindVertexArray(0)

    def delete(self):
        gl.glDeleteVertexArrays(1, self)

    def __str__(self):
        return f"<VAO: {self.__id}>"