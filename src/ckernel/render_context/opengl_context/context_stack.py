from .none_context import OGLNoneContext
import threading
from global_tools.singleton import Singleton
import weakref


# this is simply a shortcut
# dont know context binding is a common thing so placing class for opengl
class GlobalOGLContextStack:
    """
    Global gate class for tracking stack currency
    """
    __stacks = {}

    @classmethod
    def get_current(cls):
        """
        return current context

        :return:
        """
        if cls.__get_thread_stack():
            return cls.__get_thread_stack()[-1]
        return None

    @classmethod
    def put_current(cls, context):
        """
        add current to the stack

        :param context:
        :return:
        """
        cls.__get_thread_stack().append(context)

    @classmethod
    def pop_current(cls):
        """
        remove top context

        To return context to idle, None context is never removed
        :return:
        """
        if cls.__get_thread_stack():
            context = cls.__get_thread_stack().pop()
            return context

    @classmethod
    def __get_thread_stack(cls):
        tid = threading.get_ident()
        if tid not in cls.__stacks:
            cls.__stacks[tid] = []
        return cls.__stacks[tid]


def get_current_ogl():
    return GlobalOGLContextStack.get_current()


class OpenglUnboundError(Exception):
    """
    exception for no bound opengl context

    Raised when current opengl context is None.
    """
    pass
