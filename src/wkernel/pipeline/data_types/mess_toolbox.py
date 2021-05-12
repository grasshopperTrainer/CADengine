"""
Small util I don't know yet where they belong to.

In the end, this module should be empty
"""

import numpy as np
import OpenGL.GL as gl


def np_gl_type_convert(dtype):
    # bool
    if dtype == np.bool:
        return gl.GL_BOOL

    # int
    elif dtype in (np.int8, np.byte):
        return gl.GL_BYTE
    elif dtype == np.uint8:
        return gl.GL_UNSIGNED_BYTE
    elif dtype == np.uint16:
        return gl.GL_SHORT
    elif dtype == np.uint16:
        return gl.GL_UNSIGNED_SHORT
    elif dtype in (np.int, np.int32):
        return gl.GL_INT
    elif dtype == np.uint32:
        return gl.GL_UNSIGNED_INT

    # float
    elif dtype == np.float16:
        return gl.GL_HALF_FLOAT
    elif dtype in (np.float, np.float32):
        return gl.GL_FLOAT
    elif dtype == np.float64:
        return gl.GL_DOUBLE

    raise AttributeError

# tester
if __name__ == '__main__':
    a = np.float32
    print(np.byte == np.int8, np.int8 == np.byte)