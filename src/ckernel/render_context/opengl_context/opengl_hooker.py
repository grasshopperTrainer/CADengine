import importlib
# for code completion
import OpenGL.GL as gl
from OpenGL.GL import *
from .entities import OGLEntity, _OGLPrgrm, _OGLBffr, _OGLShdr

_context = []


def _hook(obj):
    def wrapper(*args, **kwargs):
        # lazy import
        if not _context:
            _context.append(getattr(importlib.import_module('ckernel.render_context.opengl_context.context_stack'),
                                    'OpenglContextStack'))

        # translate entities into ogl id
        # TODO remove acceptance of raw id when structure is mature enough
        args = [arg.id if isinstance(arg, OGLEntity) else arg for arg in args]
        kwargs = {k: arg.id if isinstance(arg, OGLEntity) else arg for k, arg in kwargs.items()}
        return obj(*args, **kwargs)
    return wrapper


for i in dir(gl):
    if i.startswith('gl'):
        locals()[i] = _hook(getattr(gl, i))

def __creator(func):
    def __wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)
        _context[0].get_current().append_entity(obj)
        return obj
    return __wrapper

# creator wrappers
@__creator
def glCreateProgram():
    return _OGLPrgrm(gl.glCreateProgram())

@__creator
def glCreatShader(typ):
    return _OGLShdr(gl.glCreateShader(typ))

# @__creator
# def glCreateBuffers(n):
#     return _OGLBffr(gl.glCreateBuffers(n))

@__creator
def glGenBuffers(n):
    return _OGLBffr(gl.glGenBuffers(n))