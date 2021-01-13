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
class _OGLPrgrm(OGLEntity):
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
        gl.glDeleteProgram(self.__id)


class _OGLShdr(OGLEntity):
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
        gl.glDeleteShader(self.__id)


class _OGLBffr(OGLEntity):
    def __init__(self, id):
        self.__id = id

    def bind(self, bffr_trgt):
        gl.glBindBuffer(bffr_trgt, self.__id)

    def delete(self):
        gl.glDeleteBuffers(1, self.__id)