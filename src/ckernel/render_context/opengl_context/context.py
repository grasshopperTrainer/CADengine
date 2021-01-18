from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_context.opengl_hooker as hooked_opengl
from .context_stack import OGLContextStack
from global_tools.trackers import TypewiseTracker


class OGLSubContext(Renderer):
    def __init__(self, cntxt_manager):
        """

        __entities: !not fully supported! better context know of its entities so
        those could be removed when context itself is removed
        :param cntxt_manager:
        """
        self._cntxt_manager = cntxt_manager
        self.__entity_tracker = TypewiseTracker()

    def __enter__(self):
        """
        put context in stack then make it current

        :return:
        """
        if OGLContextStack.get_current() == self:    # remove duplicated binding
            OGLContextStack.put_current(self)
        else:
            OGLContextStack.put_current(self)
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
        OGLContextStack.pop_current()
        # return binding
        with OGLContextStack.get_current()._cntxt_manager.glfw as glfw:
            glfw.make_context_current()

    @property
    def is_none(self):
        return False

    @property
    def entities(self):
        return self.__entity_tracker

    @property
    def manager(self):
        return self._cntxt_manager
