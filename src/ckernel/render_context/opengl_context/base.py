import threading
import weakref
from ckernel.render_context._renderer import Renderer
import ckernel.render_context.opengl_context.opengl_hooker as hooked_opengl
from .context_stack import GlobalOGLContextStack
from global_tools.trackers import TypewiseTracker
import ckernel.glfw_context.glfw_hooker as glfw


class ContextCounter:
    """
    counter like a hotel counter

    Render threads are the visitors and they have the exact room, context, for the request.
    Counter should only assign a single room to a single visitor.
    Visitor willing to have the room has to wait in que.
    """
    __que = weakref.WeakKeyDictionary()  # __queue[context] = [condition ,waiting count]
    __lock = threading.Lock()

    @classmethod
    def checkin(cls, context):
        """
        request for the room

        wait until context is free
        :param context:
        :return:
        """
        if context in cls.__que:
            with cls.__lock:
                condition, count = cls.__que[context]
            with condition:
                cls.__que[context][1] = count + 1
                condition.wait()
        else:
            with cls.__lock:
                condition = threading.Condition()
                cls.__que[context] = [condition, 0]
        return context

    @classmethod
    def checkout(cls, context):
        """
        return a context

        :param context:
        :return:
        """
        with cls.__lock:
            if cls.__que[context][1] == 0:  # no thread is waiting for the context
                del cls.__que[context]
            else:
                condition, count = cls.__que[context]
                with condition:
                    cls.__que[context][1] = count - 1
                    condition.notify(1)  # wake one up


class OGLSubContext(Renderer):
    def __init__(self, cntxt_manager):
        """
        OpenGL context binder object

        Use context manager protocol to bind OGL context before calling any gl functions.
        Context manager will also automatically block thread if requested context is used by another thread.
        :param cntxt_manager:
        """
        self.__manager = cntxt_manager
        self.__entity_tracker = TypewiseTracker()

    def __enter__(self):
        """
        put context in stack then make it current

        1. report to GlobalOGLContextStack for shortcut access
        2. report to ContextCounter so context is not called simultaneously by more than one thread
        3. bind by calling glfw.make_context_current()

        :return: gl object for calling gl functions
        """
        latest = GlobalOGLContextStack.get_current()
        GlobalOGLContextStack.put_current(self)
        if latest is not self:  # repetition doesnt need redundant binding
            with self.__manager.glfw as glfw_window:  # just reporting to glfw subcontext and getting glfw_window object
                ContextCounter.checkin(self)  # 2. ask for context
                glfw.make_context_current(glfw_window)  # 3. actual binding
        return hooked_opengl

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        release OGL context binding

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        GlobalOGLContextStack.pop_current()  # removing self
        last = GlobalOGLContextStack.get_current()
        if last and last is self:
            pass
        else:
            if last:  # return to latest binding
                with last.manager.glfw as glfw_window:
                    glfw.make_context_current(glfw_window)
            else:
                glfw.make_context_current(None)
            ContextCounter.checkout(self)  # return possession

    @property
    def is_none(self):
        return False

    @property
    def entity_tracker(self) -> TypewiseTracker:
        return self.__entity_tracker

    @property
    def manager(self):
        return self.__manager
