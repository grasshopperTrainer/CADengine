from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_renderer.opengl_hooker as hooked_opengl
from ckernel.glfw_context.none_context import NoneContextManager


class OpenglRenderer(Renderer):
    def __init__(self, context):
        self._cntxt_manager = context

    def __enter__(self):
        """
        put context in stack then make it current

        :return:
        """
        OpenglContextStack._put_current(self)
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
        OpenglContextStack._pop_current()
        # return binding
        with OpenglContextStack._get_current()._cntxt_manager.glfw as glfw:
            glfw.make_context_current()


class OpenglNoneContext(OpenglRenderer):

    def __init__(self):
        self._cntxt_manager = NoneContextManager()


# dont know context binding is a common thing so placing class for opengl
class OpenglContextStack:
    # reserve None context as first element
    __stack = [OpenglNoneContext()]

    @classmethod
    def _get_current(cls):
        """
        return current context

        :return:
        """
        return cls.__stack[-1]

    @classmethod
    def _put_current(cls, context):
        """
        add current to the stack

        :param context:
        :return:
        """
        cls.__stack.append(context)

    @classmethod
    def _pop_current(cls):
        """
        remove top context

        To return context to idle, None context is never removed
        :return:
        """
        if 1 < len(cls.__stack):
            cls.__stack.pop()
