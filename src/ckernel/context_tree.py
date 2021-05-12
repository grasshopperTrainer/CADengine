import weakref
import glfw as raw_glfw
import OpenGL.GL as gl
from .render_context.opengl_context.base import OGLSubContext
from ckernel.glfw_context.context import GLFWContext
from .glfw_context.none_context import GLFWNoneContext
from .context_spec import ContextSpec


# these are node classes for drawing context tree
class ContextMaster:
    """
    The singular root for context tree.
    From here context tree is built: ContextMaster -> MetaContext -> ContextManager -> (GLFWContext, OGLContext, window)

    To deal with glfw contexting constrain, like event poll only being run in main thread,
    it is required to have a whole view of contexts in a process.
    Some functions are provided for launching and managing window crowd.

    ! Deals with global initiation of context
    """

    __is_context_launched = False
    __context_tree = weakref.WeakSet()
    glfw = raw_glfw

    @classmethod
    def checkinit_context(cls):
        """
        check initiation and init if not

        :return:
        """
        if cls.__is_context_launched:
            return
        if not raw_glfw.init():
            raise Exception('glfw init error')
        # check and record machine specific properties
        ContextSpec().spec_check()
        cls.__is_context_launched = True

    @classmethod
    def add_meta_context(cls, mc):
        """
        track meta context

        :param mc:
        :return:
        """
        cls.__context_tree.add(mc)

    @classmethod
    def remove_meta_context(cls, meta_context):
        """
        release meta context from tracking

        :param meta_context:
        :return:
        """
        cls.__context_tree.remove(meta_context)

    @classmethod
    def iter_meta_context(cls):
        """
        iter `MetaContext` inisde tree

        :return:
        """
        for mc in cls.__context_tree:
            yield mc

    @classmethod
    def iter_all_windows(cls):
        """
        return generator for all windows in a process

        :return:
        """
        for mc in cls.iter_meta_context():
            for c in mc.iter_contexts():
                yield c.window

    @classmethod
    def has_window(cls):
        """
        check if any window is there

        :return:
        """
        return bool(cls.__context_tree)

    @classmethod
    def remove_window(cls, window):
        """
        remove window

        Release window object from traction so it could be destroyed and collected by gc.
        1. release all resources of window
        2. remove it from meta context
        3. if meta is emptied by it, remove meta

        :param window: `Window` removed
        :return:
        """
        context = window.context
        mcontext = context.meta_context
        context.destroy()
        mcontext.remove_context(context)
        if mcontext.is_empty:
            mcontext.destroy()
            cls.remove_meta_context(mcontext)


class MetaContext:
    """
    Context node for shared context.

    ! doesn't do much for now, but is here to expand shared context functionality.
    """

    def __init__(self, context):
        """
        ! private, do not call from outside. Access only allowed by `MetaContext.checkbuild_meta()`
        """
        self.__context_set = weakref.WeakSet()
        self.__context_set.add(context)
        ContextMaster.add_meta_context(self)

    @property
    def is_empty(self):
        """
        check if MetaContext has tracking context

        :return:
        """
        return not bool(self.__context_set)

    @classmethod
    def checkbuild_meta(cls, window, shared):
        """
        find `MetaContext` and build if nonexistent and return

        :param window: to check context of
        :param shared: shared window
        :return: MetaContext instance
        """
        if shared is None:
            return cls(window)
        else:
            for mc in ContextMaster.iter_meta_context():
                if mc.is_member_window(shared):
                    mc.add_context_manager(window)
                    return mc
        raise Exception('context tree inconsistency error')

    def is_member_context(self, context):
        """
        check if given context is a member of this meta context
        :param context:
        :return:
        """
        return context in self.__context_set

    def is_member_window(self, window):
        """
        check if given window is a member of this meta context

        :param window:
        :return:
        """
        for cntxt in self.__context_set:
            if cntxt.window == window:
                return True
        return False

    def iter_contexts(self):
        """
        generator for all child contexts of this meta context
        :return:
        """
        for c in self.__context_set:
            yield c

    def add_context_manager(self, context):
        """
        track context
        :param contest:
        :return:
        """
        self.__context_set.add(context)

    def remove_context(self, context):
        """
        release context from tracking

        :param context:
        :return:
        """
        if context not in self.__context_set:
            raise ValueError('context not insdie this metacontext')
        self.__context_set.remove(context)

    def destroy(self):
        """
        release resource for gc

        :return:
        """
        self.__context_set.clear()
        self.__context_set = None


class ContextManager:
    """
    Container class of GLFWContex and OpenGLContext.
    ! this is a node class of the context tree rooting from `ContextMaster`.
    """

    def __init__(self, width, height, title, monitor, share, window):
        """
        Each render window(window area created by glfw) has to have its own context manager.
        Context manager holds arguments related to render context.

        Arguments can be grouped into two:
        1. arguments for binding render context
        'binding render context' means declaration that has to be made before calling rendering functions.
        Declaration has two perpose, a) to actually gain access to the render context,
        otherwise `OpenGL` library(or actual hardware?) will deny render call and through error.
        b) to record currently bound context so user can use a global shortcut provided by `GlobalOGLContextStack`
        User has to use python context management context with `glfw` and `gl` argument for the access declaration
        and currency recording.

        2. arguments for routing into context tree
        The instance is returned when user asks current context to `GlobalOGLContextStack`.
        As an access point to the main window structure, arguments as `window`, `gl`, `glfw` etc.
        are here to be used by the user.

        :param width:
        :param height:
        :param title:
        :param monitor:
        :param share: Window, mother
        """
        self.__window = weakref.ref(window)
        # for singular `glfw` initiation
        ContextMaster.checkinit_context()
        # have a meta node grouping shared contexts
        self.__meta_context = MetaContext.checkbuild_meta(self, share)
        if share:
            share = share.context.glfw_window
        # store `glfw`'s window object for `glfw.make_context_current()`
        self.__glfw_context = GLFWContext(width, height, title, monitor, share)
        self.__renderer_context = OGLSubContext(self)

        self.__init_local_setting()

    def __init_local_setting(self):
        """
        initial local glfw, gl(can it be locasl?) settings
        :return:
        """
        pass

    @property
    def gl(self) -> gl:
        return self.__renderer_context

    @property
    def glfw(self):
        return self.__glfw_context

    @property
    def glfw_window(self):
        return self.__glfw_context._window

    @property
    def context_master(self):
        return ContextMaster

    @property
    def meta_context(self):
        return self.__meta_context

    @property
    def window(self):
        return self.__window()

    def destroy(self):
        """
        releas resources for gc

        ! In module use only.
        :return:
        """
        self.__meta_context = None
        self.__window = None
        self.__glfw_context = None
        self.__renderer_context = None

    def get_context_of(self, window):
        raise NotImplementedError


class NoneContextManager:
    @property
    def glfw(self):
        return GLFWNoneContext()
