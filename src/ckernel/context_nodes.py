import weakref
import glfw as raw_glfw
import OpenGL.GL as gl
from .render_context.opengl_context.base import OGLSubContext
from ckernel.glfw_context.context import GLFWContext
from .glfw_context.none_context import GLFWNoneContext
from global_tools.singleton import Singleton


@Singleton
class ContextSpec:
    """
    Store opengl specification for outer access
    """

    # just for protection
    @property
    def OGL_VERSION(self):
        return self.__OGL_VERSION

    @property
    def OGL_RENDERER(self):
        return self.__OGL_RENDERER

    @property
    def OGL_VENDOR(self):
        return self.__OGL_VENDOR

    @property
    def SHARED_BUFFER(self):
        return self.__SHARED_BUFFER

    @property
    def SHARED_VERTEX_ARRAY(self):
        return self.__SHARED_VERTEX_ARRAY

    @property
    def SHARED_PROGRAM(self):
        return self.__SHARED_PROGRAM

    @property
    def SHARED_SHADER(self):
        return self.__SHARED_SHADER

    @property
    def SHARED_TEXTURE(self):
        return self.__SHARED_TEXTURE

    @property
    def SHARED_FRAME_BUFFER(self):
        return self.__SHARED_FRAME_BUFFER

    @property
    def SHARED_RENDER_BUFFER(self):
        return self.__SHARED_RENDER_BUFFER

    @property
    def VAO_VISIBLE_ARRAY(self):
        return self.__VAO_VISIBLE_ARRAY

    @property
    def VAO_VISIBLE_ELEMENT_ARRAY(self):
        return self.__VAO_VISIBLE_ELEMENT_ARRAY


    @classmethod
    def spec_check(cls):
        """
                Tests GL behavior on GLFW context.

                Tested subjects are such as :
                GL object shareness
                GL vertax array objects' children binding
                basic glfw-opengl info

                :return: None
                """
        result_strings = ['', 'GLFW context specification result :', ]

        # not to display and window while going through multiple tests
        raw_glfw.window_hint(raw_glfw.VISIBLE, raw_glfw.FALSE)
        # two windows needed for testing shareness
        window1 = raw_glfw.create_window(1, 1, 'first', monitor=None, share=None)
        window2 = raw_glfw.create_window(1, 1, 'first', monitor=None, share=window1)
        raw_glfw.window_hint(raw_glfw.VISIBLE, raw_glfw.TRUE)

        # check object shareness
        result_strings.append('')
        result_strings.append(f"{'GL object shareness':>33} :")
        objs = {}  # opengl objects used in testing
        for win in window1, window2:
            raw_glfw.make_context_current(win)  # objects below belongs to this window
            objs.setdefault('BUFFER', []).append(gl.glGenBuffers(1))
            objs.setdefault('VERTEX_ARRAY', []).append(gl.glGenVertexArrays(1))
            objs.setdefault('PROGRAM', []).append(gl.glCreateProgram())  # prgrm and shader share ID
            objs.setdefault('SHADER', []).append(gl.glCreateShader(gl.GL_VERTEX_SHADER))  # so this results 2
            objs.setdefault('TEXTURE', []).append(gl.glGenTextures(1))
            objs.setdefault('RENDER_BUFFER', []).append(gl.glGenRenderbuffers(1))
            objs.setdefault('FRAME_BUFFER', []).append(gl.glGenFramebuffers(1))

        # logic is simple : if window2 object's index is 2 not 1
        # means window2 shared object with window1
        for key, (a, b) in objs.items():
            arg_name = f"SHARED_{key}"
            setattr(cls, arg_name, not (a == b))
            result_strings.append(f'{key :>33} : {getattr(cls, arg_name)}')

        # ibo visibility test
        gl.glBindVertexArray(objs['VERTEX_ARRAY'][0])
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, objs['BUFFER'][0])
        # unbind all
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        # check visibility
        gl.glBindVertexArray(objs['VERTEX_ARRAY'][0])
        cls.__VAO_VISIBLE_ELEMENT_ARRAY = gl.glGetInteger(gl.GL_ELEMENT_ARRAY_BUFFER_BINDING) == objs['BUFFER'][0]
        cls.__VAO_VISIBLE_ARRAY = True

        result_strings.append('')
        result_strings.append(f"{'VAO visibility test' :>33} :")
        result_strings.append(f"{'ARRAY_VISIBLE' :>33} : {cls.__VAO_VISIBLE_ARRAY}")
        result_strings.append(f"{'ELEMENT_ARRAY_VISIBLE' :>33} : {cls.__VAO_VISIBLE_ELEMENT_ARRAY}")

        # store some info
        cls.__OGL_VERSION = gl.glGetString(gl.GL_VERSION)
        cls.__OGL_RENDERER = gl.glGetString(gl.GL_RENDERER)
        cls.__OGL_VENDOR = gl.glGetString(gl.GL_VENDOR)

        result_strings.append('')
        result_strings.append(f"{'Some basic info' :>33} :")
        result_strings.append(f"{'gl_version' :>33} : {cls.__OGL_VERSION}")
        result_strings.append(f"{'gl_renderer' :>33} : {cls.__OGL_RENDERER}")
        result_strings.append(f"{'gl_vendor' :>33} : {cls.__OGL_VENDOR}")

        for win in window1, window2: raw_glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check DONE')

        # print resuts:
        for row in result_strings:
            print(row)
        print()


class ContextMaster:
    """
    Draws tree structure of contexts

    To deal with glfw context's constrain, like event poll only being run in main thread, it is required to
    have whole view of contexts if glfw is running.
    This class organizes contexts into tree like structure. Root is singleton of current tree and children are
    metacontext. Grandchildren would be ContextManager then.

    Deals with global initiation of context
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
        ContextSpec().spec_check()
        cls.__is_context_launched = True

    @classmethod
    def _add_meta_context(cls, mc):
        """
        track meta context
        :param mc:
        :return:
        """
        cls.__context_tree.add(mc)

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
        for mc in cls.iter_meta_context():
            for c in mc.iter_contexts():
                if c.window == window:
                    c._destroy()  # how to define module private in python
                    mc._remove_context(c)
                    if mc.is_empty:
                        mc._destroy()
                        cls._remove_meta_context(mc)
                    return True
        raise Exception('window set to be removed not found')

    @classmethod
    def _remove_meta_context(cls, meta_context):
        """
        release meta context from tracking

        :param meta_context:
        :return:
        """
        cls.__context_tree.remove(meta_context)


class MetaContext:
    """
    Represent shared context

    Even shared context has to have separate contexts. Primarily, all windows have distinct glfw context
    as window property is all different; ex. size position, title, etc. Whats common is OpenGL State machine.
    Yet Even State machine is not totally 'shared'. Vertex array buffer is not shared among Contexts.
    So, every window has to have unique context built of a pair of sub context; glfw_cntx, opengl_ctnx.
    In such a situation this Meta~ class binds contexts that are shared which, hopefully in the future implementation,
    would provide functionality of auto complete shrareness amongst shared OpenGL contexts.

    This class is medium container of shared contexts.
    """

    def __init__(self, context):
        """
        ! do not call from outside. Access only allowed by `MetaContext.checkbuild_meta()`
        """
        self.__context_set = weakref.WeakSet()
        self.__context_set.add(context)
        ContextMaster._add_meta_context(self)

    @property
    def is_empty(self):
        """
        check if MetaContext has tracking context

        :return:
        """
        return not bool(self.__context_set)

    @classmethod
    def _checkbuild_meta(cls, window, shared):
        """
        find `MetaContext` and build if nonexistent

        :param window: to check context of
        :param shared: shared window
        :return:
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

    def _remove_context(self, context):
        """
        release context from tracking

        :param context:
        :return:
        """
        if context not in self.__context_set:
            raise ValueError('context not insdie this metacontext')
        self.__context_set.remove(context)

    def _destroy(self):
        """
        release resource for gc

        :return:
        """
        self.__context_set.clear()
        self.__context_set = None


class ContextManager:
    """
    Class combination of GLFWContext and OpenGLContext.

    !
    naming seems to be off the point viewing from `ContextTree` object as leaf has a name of 'Manager' but is
    appropriate viewing from `Window` object
    !
    """

    def __init__(self, width, height, title, monitor, share, window):  # kwargs for some setting non default options
        """
        Context manager manages two contexts; glfw and renderer. Currently on OpenglRenderer is supported.

        Context manager has to handle consistency among shared windows.
        Shared windows mean shared renderer_context(at least in case of opengl).
        Context here means state machine(in GPU) that maintains certain state.
        But be carefull as not every aspect of Opengl entity is shared among shared windows, those are set to be shared
        by creating glfw window.
        Shared windows share renderer_context but to not share glfw context as every context has its own glfw property
        like own window name, position, size etc.

        To check shareness, window has to see through this cls registry and grasp renderer of shared parend window.
        below is args needed creating glfw context
        :param width:
        :param height:
        :param title:
        :param monitor:
        :param share: Window, mother
        """
        ContextMaster.checkinit_context()
        self.__meta_context = MetaContext._checkbuild_meta(self, share)
        self.__window = weakref.ref(window)
        if share:
            share = share.context.glfw_window
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

    raw_glfw = raw_glfw

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

    def _destroy(self):
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
