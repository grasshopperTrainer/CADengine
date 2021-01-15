import weakref
import warnings

import numpy as np

import ckernel.render_context.opengl_context.opengl_hooker as gl


class UniformPusher:
    """
    Pushed array into OpenGL program to given location
    """
    # (OGLPrgrm, {name:loc}) caching
    # weak ref is enough -> loosing cache is not critical, can be restored.
    # So to be conservative, better not leave memory leak possibility.
    __uniform_meta = weakref.WeakKeyDictionary()

    def __init__(self):
        warnings.warn('no instance methods. Better access it as static method wrapper')

    @classmethod
    def push_all(cls, ufrm_data, prgrm):
        """
        push data into bound ogl program

        :param ufrm_data: `_BffrCache`, data to push into ogl program
        :param prgrm: `_Prgrm`, data to push into ogl program
        :return:
        """
        d = cls.__uniform_meta.setdefault(prgrm, cls.__getreg_uniform_loc(ufrm_data, prgrm))
        for name, shape, dtype, _ in ufrm_data.field_props:
            func, loc = d[name]
            count = shape[0] if len(shape) == 1 else shape[0]*shape[1]
            transpose = True
            value = ufrm_data.array[name]
            is_matrix = len(shape) == 2

            if is_matrix:
                func(loc, count, transpose, value)
            else:
                func(loc, count, value)

    @classmethod
    def __getreg_uniform_loc(cls, cpu_bffr, prgrm):
        """
        get, or reg and get, uniform location of a program

        :param prgrm: program to find location of uniforms
        :return:
        """
        d = {}
        for name, shape, dtype, _ in cpu_bffr.field_props:
            loc = gl.glGetAttribLocation(prgrm, name)   # or better store function too?
            func = cls.parse_ufrm_func(shape, dtype)
            d[name] = (func, loc)
        return d

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
