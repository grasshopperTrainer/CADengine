"""
this seems to be too much... maybe not too much
"""

from .context_stack import GLFWContextStack
import ckernel.glfw_context.glfw_hooker as hooked_glfw


class NoneContextManager:
    @property
    def glfw(self):
        return GLFWNoneContext()


class GLFWNoneContext:
    """
    context to use None
    """
    def __enter__(self):
        GLFWContextStack.put_current(None)
        return hooked_glfw

    def __exit__(self, exc_type, exc_val, exc_tb):
        GLFWContextStack.pop_current()
