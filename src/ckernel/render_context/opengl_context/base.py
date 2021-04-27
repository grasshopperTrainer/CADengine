import threading
import weakref
from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_context.opengl_hooker as hooked_opengl
from .context_stack import GlobalOGLContextStack
from ckernel.tools.stacker import TypewiseStacker
import ckernel.glfw_context.glfw_hooker as glfw


class ContextCounter:
    """
    counter like hotel counter
    render threads are the visitors and want context as a room
    counter should only assign a room to a thread
    threads willing to have the room(context) has to wait in que
    """
    __que = weakref.WeakKeyDictionary()  # [context] = waiting count
    __que_lock = threading.Lock()

    @classmethod
    def checkin(cls, context):
        """
        render thread want to use a context
        mark context in use and wait-mark if the context is already in use

        :param context: requested
        :return:
        """
        cls.__que_lock.acquire()
        if context in cls.__que:
            condition, count = cls.__que[context]
            with condition:
                cls.__que[context][1] = count + 1
                cls.__que_lock.release()
                condition.wait()
        else:   # context is not used by any
            condition = threading.Condition()
            cls.__que[context] = [condition, 0]
            cls.__que_lock.release()
        return context

    @classmethod
    def checkout(cls, context):
        """
        render thread return the context

        :param context:
        :return:
        """
        cls.__que_lock.acquire()
        if cls.__que[context][1] == 0:  # no thread is waiting for the context
            del cls.__que[context]
            cls.__que_lock.release()
        else:
            condition, count = cls.__que[context]
            with condition:
                cls.__que[context][1] = count - 1
                cls.__que_lock.release()
                condition.notify()  # wake one up


class OGLSubContext(Renderer):
    def __init__(self, cntxt_manager):
        """

        __entities: !not fully supported! better context know of its entities so
        those could be removed when context itself is removed
        :param cntxt_manager:
        """
        self.__manager = cntxt_manager
        self.__entity_stacker = TypewiseStacker()
        self.__lock = threading.Lock()

    def __enter__(self):
        """
        put context in stack then make it current

        1. report to GlobalStack for shortcut access
        2. report to ContextCounter so thread doesnt call context in bound(at another thread)
        :return:
        """
        latest = GlobalOGLContextStack.get_current()
        GlobalOGLContextStack.put_current(self)
        if latest is not self:  # repetition doesnt require redundant binding
            with self.__manager.glfw as glfw_window:  # just reporting to glfw subcontext and getting glfw_window object
                ContextCounter.checkin(self)  # 2. ask for context
                glfw.make_context_current(glfw_window)
        return hooked_opengl

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        need to release window bound by make_context_current

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        GlobalOGLContextStack.pop_current()  # removing self
        # return binding
        last = GlobalOGLContextStack.get_current()
        if last and last is self:
            pass
        else:
            if last:
                with last.manager.glfw as glfw_window:
                    glfw.make_context_current(glfw_window)
            else:
                glfw.make_context_current(None)
            ContextCounter.checkout(self)

    @property
    def is_none(self):
        return False

    @property
    def entity_stacker(self):
        return self.__entity_stacker

    @property
    def manager(self):
        return self.__manager
