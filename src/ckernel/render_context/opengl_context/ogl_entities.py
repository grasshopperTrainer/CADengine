"""
! controlled through `opengl_hooker`
these are simple wrappers for OpenGL objects purposed for abstraction of
common operations like binding, deleting
"""
import abc
import ckernel.render_context.opengl_context.opengl_hooker as gl


class OGLEntity(metaclass=abc.ABCMeta):
    """
    OpenGL id holder.
    """
    def __init__(self, id):
        self.__id = id

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

    @abc.abstractmethod
    def delete(self):
        """
        delete obl object
        :return:
        """
        pass


# use under bar
class _Program(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def bind(self):
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


class _Shader(OGLEntity):
    def __init__(self, typ, id):
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
        If shader is only for a single program, deletion is advised after successful program link.
        :return:
        """
        gl.glDeleteShader(self)

    def __str__(self):
        return f"<Shader: {self.__id}>"


class _Buffer(OGLEntity):
    def __init__(self, id):
        self.__id = id
        self.__target = None
        self.__usage = gl.GL_DYNAMIC_DRAW

    def __str__(self):
        return f"<Buffer: {self.__id}>"

    def bind(self):
        gl.glBindBuffer(self.__target, self.__id)

    def delete(self):
        gl.glDeleteBuffers(1, self)

    def push_all(self, cpu_bffr):
        """
        push whole data of given array into ogl buffer

        :param cpu_bffr: `_CPUBffr`, data to push into ogl buffer
        :return:
        """
        self.bind()
        gl.glBufferData(target=self.__target,
                        size=cpu_bffr.bytesize,
                        data=cpu_bffr.array,
                        usage=self.__usage)
        # unbinding needed? does vao affected by vbo binding before its binding?

    def set_target(self, target):
        self.__target = target

    def set_usage(self, usage):
        self.__usage = usage


class _VertexArray(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def bind(self):
        gl.glBindVertexArray(self.__id)

    def unbind(self):
        gl.glBindVertexArray(0)

    def delete(self):
        gl.glDeleteVertexArrays(1, self)

    def __str__(self):
        return f"<VAO: {self.__id}>"