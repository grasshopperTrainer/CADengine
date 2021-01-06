import importlib
# for code completion
import glfw
from glfw import *


_windows = []


def _hook(obj):
    def wrapper(*args, **kwargs):
        # lazy import
        if not _windows:
            _windows.append(getattr(importlib.import_module('wkernel.env.windows'), 'Windows'))
        if _windows[0]().get_current() is None:
            pass
        else:
            _windows[0]().get_current()._context_manager.log_glfw(obj.__name__)
        return obj(*args, **kwargs)
    return wrapper


for i in dir(glfw):
    if callable(getattr(glfw, i)):
        locals()[i] = _hook(getattr(glfw, i))

# override after this point
init = glfw.init
get_current_context = glfw.get_current_context