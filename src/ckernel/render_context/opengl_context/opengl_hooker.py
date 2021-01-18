import importlib
# for code completion
import OpenGL.GL as gl
from OpenGL.GL import *
from .ogl_entities import OGLEntity, _Prgrm, _Bffr, _Shdr, _VrtxArry

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
        _context[0].get_current().entities.registry.register(obj)
        return obj
    return __wrapper

# creator wrappers
@__creator
def glCreateProgram():
    return _Prgrm(gl.glCreateProgram())

@__creator
def glCreatShader(typ):
    return _Shdr(gl.glCreateShader(typ))

@__creator
def glGenBuffers(n):
    return _Bffr(gl.glGenBuffers(n))

@__creator
def glGenVertexArrays(n):
    return _VrtxArry(gl.glGenVertexArrays(n))

# def __deleter(func):
#     def __wrapper(*args, **kwargs):
#         args = [arg.id if isinstance(arg, OGLEntity) else arg for arg in args]
#         kwargs = {k: arg.id if isinstance(arg, OGLEntity) else arg for k, arg in kwargs.items()}
#         func(*args, **kwargs)
#
#     return __wrapper