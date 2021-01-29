import numpy as np
import ckernel.render_context.opengl_context.opengl_hooker as gl


def npdtype_to_gldtype(dtype):
    """
    translates numpy dtype into OpenGL dtype
    :param dtype:
    :return:
    """
    if not isinstance(dtype, np.dtype):
        raise TypeError

    # decompress dtype
    if dtype.fields is None:
        is_simple = True
        dtypes = [dtype]
    else:
        is_simple = False
        dtypes = []
        for _, (dtype, _) in dtype.fields.items():
            dtypes.append(dtype)

    results = []
    for dt in dtypes:
        if dt == np.bool:
            results.append(gl.GL_BOOL)

        elif dt == np.byte:
            results.append(gl.GL_BYTE)
        elif dt == np.ubyte:
            results.append(gl.GL_UNSIGNED_BYTE)

        elif dt in (np.short, np.int16):
            results.append(gl.GL_SHORT)
        elif dt in (np.ushort, np.uint16):
            results.append(gl.GL_UNSIGNED_SHORT)
        elif dt in (np.int, np.int32):
            results.append(gl.GL_INT)
        elif dt in (np.uint, np.uint32):
            results.append(gl.GL_UNSIGNED_INT)

        elif dt == np.float16:
            results.append(gl.GL_HALF_FLOAT)
        elif dt == np.float32:
            results.append(gl.GL_FLOAT)
        elif dt == np.float64:
            results.append(gl.GL_DOUBLE)
        else:
            raise ValueError('incomprehensible numpy dtype', dt)
    # unpack if singular
    return results[0] if is_simple else results