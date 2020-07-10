import importlib
# for code completion
import OpenGL.GL as gl
from OpenGL.GL import *


_windows = []


def _hook(obj):
    def wrapper(*args, **kwargs):
        # lazy import
        if not _windows:
            _windows.append(getattr(importlib.import_module('UVT.env.windows'), 'Windows'))
        _windows[0]().get_current()._context_manager.log_gl(obj.__name__)
        return obj(*args, **kwargs)
    return wrapper


for i in dir(gl):
    if i.startswith('gl'):
        locals()[i] = _hook(getattr(gl, i))

