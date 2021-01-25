"""
! controlled through `opengl_hooker`
these are simple wrappers for OpenGL objects purposed for abstraction of
common operations like binding, deleting
"""
import abc
import numpy as np
import ckernel.render_context.opengl_context.opengl_hooker as gl
from .context_stack import get_current_ogl


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

    # binding context implement into context manager
    def __enter__(self):
        entity_stack = get_current_ogl().entities.stack
        if not entity_stack.is_empty(self.__class__) and entity_stack.get_current(self.__class__) == self:
            entity_stack.push(self)
        else:
            entity_stack.push(self)
            self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        entities = get_current_ogl().entities
        entities.stack.pop(self.__class__)
        # control over matryoshka context
        # follow bind-only policy
        if not entities.stack.is_empty(self.__class__):
            entity = entities.stack.get_current(self.__class__)
            entity.bind()
        else:
            # only if there is no entity to return binding
            self.unbind()


# use under bar
class _Prgrm(OGLEntity):
    def __init__(self, id):
        self.__id = id
        self.__vrtxattr_skema = None
        self.__ufrm_skema = None

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

    def push_ufrms(cls, bffr_cache):
        """
        push data into bound ogl prgrm

        :param bffr_cache: `_BffrCache`, data to push into ogl prgrm
        :param prgrm: `_Prgrm`, data to push into ogl prgrm
        :return:
        """
        for name, loc, shape, dtype, _, _ in bffr_cache.field_props:
            func = cls.parse_ufrm_func(shape, dtype)
            count = len(bffr_cache.array)
            transpose = gl.GL_TRUE
            value = bffr_cache.array[name]
            is_matrix = len(shape) == 2
            if is_matrix:
                func(loc, count, transpose, value)
            else:
                func(loc, count, value)

    @staticmethod
    def parse_ufrm_func(shape, dtype):
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

    def attach_vrtxattr_skema(self, vrtxattr_skema):
        """
        store skema of vertex attribute of the program

        :param vrtxattr_skema: VrtxAttrSkema,
        :return:
        """
        self.__vrtxattr_skema = vrtxattr_skema

    def attach_ufrm_skema(self, ufrm_skema):
        """
        store skema of uniforms of the program

        :param ufrm_skema: UfrmSkema,
        :return:
        """
        self.__ufrm_skema = ufrm_skema


class _Shdr(OGLEntity):
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
        If shader is only for a single prgrm, deletion is advised after successful prgrm link.
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
                            size=self.__cache.bytesize,
                            data=self.__cache.array,
                            usage=bffr.__usage)
            # unbinding needed? does vao affected by vbo binding before its binding?

    def set_target(self, target):
        self.__target = target

    def set_usage(self, usage):
        self.__usage = usage

    def set_cache(self, cache):
        self.__cache = cache


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
