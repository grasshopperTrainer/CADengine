import numpy as np

# for code completion
import OpenGL.GL as gl
from OpenGL.GL import *
from ckernel.render_context.opengl_context.entities.ogl_entities import OGLEntity, _Prgrm, _Bffr, _Shdr, _VrtxArry, _FrameBffr, _Texture, _RenderBffr
from global_tools.enum import EnumVal

# _context = []
# _context.append(getattr(importlib.import_module('ckernel.render_context.opengl_context.context_stack'),
#                                     'OGLContextStack'))
def _hook(obj):
    def wrapper(*args, **kwargs):
        # lazy import
        # if not _context:
        #     _context.append(getattr(importlib.import_module('ckernel.render_context.opengl_context.context_stack'),
        #                             'OGLContextStack'))

        # translate entities into ogl id
        # TODO remove acceptance of raw id when structure is mature enough
        iargs = []
        for arg in args:
            if isinstance(arg, OGLEntity):
                iargs.append(arg.id)
            elif isinstance(arg, EnumVal):
                iargs.append(arg.v)
            else:
                iargs.append(arg)

        ikwargs = {}
        for k, arg in kwargs.items():
            if isinstance(arg, OGLEntity):
                ikwargs[k] = arg
            elif isinstance(arg, EnumVal):
                ikwargs[k] = arg.v
            else:
                ikwargs[k] = arg
        return obj(*iargs, **ikwargs)
    return wrapper


for i in dir(gl):
    if i.startswith('gl'):
        locals()[i] = _hook(getattr(gl, i))

def __creator(func):
    def __wrapper(*args, **kwargs):
        typ, ids, *args = func(*args, **kwargs)
        objs = []
        if not isinstance(ids, np.ndarray):
            ids = [ids, ]
        for id in ids:
            obj = typ(id, *args)
            objs.append(obj)
            # GlobalOGLContextStack.get_current().entities.registry.register(obj)
        return objs[0] if len(objs) == 1 else objs

    return __wrapper

# creator wrappers
@__creator
def glCreateProgram() -> _Prgrm:
    return _Prgrm, gl.glCreateProgram()

@__creator
def glCreateShader(typ) -> _Shdr:
    return _Shdr, gl.glCreateShader(typ), typ

@__creator
def glGenBuffers(n) -> _Bffr:
    return _Bffr, gl.glGenBuffers(n)

@__creator
def glGenVertexArrays(n) -> _VrtxArry:
    return _VrtxArry, gl.glGenVertexArrays(n)

@__creator
def glGenFramebuffers(n, target) -> _FrameBffr:
    return _FrameBffr, gl.glGenFramebuffers(n), target

@__creator
def glGenTextures(n) -> _Texture:
    return _Texture, gl.glGenTextures(n)

@__creator
def glGenRenderbuffers(n) -> _RenderBffr:
    return _RenderBffr, gl.glGenRenderbuffers(n), gl.GL_RENDERBUFFER

# def __deleter(func):
#     def __wrapper(*args, **kwargs):
#         args = [arg.id if isinstance(arg, OGLEntity) else arg for arg in args]
#         kwargs = {k: arg.id if isinstance(arg, OGLEntity) else arg for k, arg in kwargs.items()}
#         func(*args, **kwargs)
#
#     return __wrapper