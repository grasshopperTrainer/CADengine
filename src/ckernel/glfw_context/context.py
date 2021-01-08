import glfw as raw_glfw
import ckernel.glfw_context.glfw_hooker as hooked_glfw
from .context_stack import GLFWContextStack


class GLFWContext:
    def __init__(self, width, height, title, monitor, share):
        self._window = raw_glfw.create_window(width, height, title, monitor, share)

    def __enter__(self):
        GLFWContextStack.put_current(self._window)
        return hooked_glfw

    def __exit__(self, exc_type, exc_val, exc_tb):
        GLFWContextStack.pop_current()

