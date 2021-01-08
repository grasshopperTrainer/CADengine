import importlib
# for code completion
import glfw
from glfw import *


# naming scope problem exists. storing single class
__glfw_context = []


def _hook(obj):
    def wrapper(*args, **kwargs):
        # lazy import
        if not __glfw_context:
            __glfw_context.append(getattr(importlib.import_module('ckernel.glfw_context.context_stack'), 'GLFWContextStack'))
        return obj(__glfw_context[0]._get_current(), *args, **kwargs)
    return wrapper


for i in dir(glfw):
    if callable(getattr(glfw, i)):
        locals()[i] = _hook(getattr(glfw, i))


# override after this point
init = glfw.init
get_current_context = glfw.get_current_context