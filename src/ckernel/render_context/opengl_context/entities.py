"""
! controll entities only through context
"""
import abc
import ckernel.render_context.opengl_context.opengl_hooker as gl


class OGLEntity(metaclass=abc.ABCMeta):
    """
    OpenGL id holder.
    """
    @property
    def id(self):
        """
        :return: id of ogl object
        """
        # for class using '_Name' pattern
        return getattr(self, f"{self.__class__.__name__}__id")

    # do not provide unbind, default policy is 'bind-only'
    @abc.abstractmethod
    def bind(self):
        """
        bind ogl object
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


# use under bar
class _OGLPrgrm(OGLEntity):
    def __init__(self):
        self.__id = gl.glCreateProgram()

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
    def __init__(self, typ):
        self.__id = gl.glCreateShader(typ)
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