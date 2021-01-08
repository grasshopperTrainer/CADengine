from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_renderer.opengl_hooker as hooked_opengl
from .context_stack import OpenglContextStack


class OpenglContext(Renderer):
    def __init__(self, context):
        self._cntxt_manager = context

    def __enter__(self):
        """
        put context in stack then make it current

        :return:
        """
        OpenglContextStack.put_current(self)
        with self._cntxt_manager.glfw as glfw:
            glfw.make_context_current()
        return hooked_opengl

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        need to releas window bound by make_context_current

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        OpenglContextStack.pop_current()
        # return binding
        with OpenglContextStack.get_current()._cntxt_manager.glfw as glfw:
            glfw.make_context_current()

