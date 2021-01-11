from collections import deque
import glfw as raw_glfw
import OpenGL.GL as gl
from .render_context.opengl_context.context import OpenglContext
from ckernel.glfw_context.context import GLFWContext
from .glfw_context.none_context import GLFWNoneContext

import weakref
#
#
# class Logger:
#     """
#     Log container.
#     """
#
#     def __init__(self, size=1000, do_log=True, prefix='', sufix=''):
#         """
#         :param size: max length of logging record. Infinite if given -1.
#         :param do_log: Switch for logging.
#         """
#         self._is_logging = do_log
#         self._size = size
#         self._record = deque()
#         self._prefix = prefix
#         self._sufix = sufix
#
#     def log(self, message):
#         """
#         Log message
#         :param message:
#         :return:
#         """
#         if len(self._record) == self._size:
#             self._record.popleft()
#         self._record.append(f"{self._prefix}{message}{self._sufix}")
#
#     @property
#     def is_logging(self):
#         return self._is_logging
#
#     @is_logging.setter
#     def is_logging(self, v):
#         if not isinstance(v, bool):
#             raise TypeError()
#         self._is_logging = v


class ContextMaster:
    """
    Draws tree structure of contexts

    To deal with glfw context's constrain, like event poll only being run in main thread, it is required to
    have whole view of contexts if glfw is running.
    This class organizes contexts into tree like structure. Root is singleton of current tree and children are
    metacontext. Grandchildren would be ContextManager then.

    Deals with global initiation of context
    """

    __opengl_spec = {'info': {}, 'shareness': {}, 'vao_binding': {}}
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
        cls.__spec_check()
        cls.__is_context_launched = True

    @classmethod
    def __spec_check(cls):
        """
        Tests GL behavior on GLFW context.

        Tested subjects are such as :
        GL object shareness
        GL vertax array objects' children binding
        basic glfw-opengl info

        :return: None
        """
        result_strings = ['GLFW context specification result:', ]

        # not to display and window while going through multiple tests
        raw_glfw.window_hint(raw_glfw.VISIBLE, raw_glfw.FALSE)
        # two windows needed for testing shareness
        window1 = raw_glfw.create_window(1, 1, 'first', monitor=None, share=None)
        window2 = raw_glfw.create_window(1, 1, 'first', monitor=None, share=window1)
        raw_glfw.window_hint(raw_glfw.VISIBLE, raw_glfw.TRUE)

        # check object shareness
        result_strings.append('\n    GL object shareness :')
        opengl_objects = []  # opengl objects used in testing
        for win in window1, window2:
            dic = {}
            opengl_objects.append(dic)

            raw_glfw.make_context_current(win)  # objects below belongs to this window
            dic['buffer'] = gl.glGenBuffers(1)
            dic['vertex_array'] = gl.glGenVertexArrays(1)
            dic['program'] = gl.glCreateProgram()  # program and shader share ID
            dic['shader'] = gl.glCreateShader(gl.GL_VERTEX_SHADER)  # so this results 2
            dic['texture'] = gl.glGenTextures(1)
            dic['render_buffer'] = gl.glGenRenderbuffers(1)
            dic['frame_buffer'] = gl.glGenFramebuffers(1)

        # logic is simple : if window2 object's index is 2 not 1
        # means window2 shared object with window1
        for key, val in opengl_objects[0].items():
            cls.__opengl_spec['shareness'][key] = True
            if val == opengl_objects[1][key]:
                cls.__opengl_spec['shareness'][key] = False
            front_blank = " " * (len(result_strings[1]) - len(key) - 3)
            result_strings.append(
                f'{front_blank}{key} : {"SHARED" if cls.__opengl_spec["shareness"][key] else "NOT SHARED"}')

        # store some info
        cls.__opengl_spec["info"]["gl_version"] = gl.glGetString(gl.GL_VERSION)
        cls.__opengl_spec["info"]["gl_renderer"] = gl.glGetString(gl.GL_RENDERER)
        cls.__opengl_spec["info"]["gl_vendor"] = gl.glGetString(gl.GL_VENDOR)
        result_strings.append('\n    Some basic info :')
        result_strings.append(f'         gl_version : {cls.__opengl_spec["info"]["gl_version"]}')
        result_strings.append(f'        gl_renderer : {cls.__opengl_spec["info"]["gl_renderer"]}')
        result_strings.append(f'          gl_vendor : {cls.__opengl_spec["info"]["gl_vendor"]}')

        result_strings.append('\n    VAO children binding :')

        cls.__opengl_spec['vao_binding']['array_buffer'] = True
        # ibo visibility test
        gl.glBindVertexArray(opengl_objects[0]['vertex_array'])
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, opengl_objects[0]['buffer'])
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(opengl_objects[0]['vertex_array'])
        vao_ibo_binding = gl.glGetInteger(gl.GL_ELEMENT_ARRAY_BUFFER_BINDING) == opengl_objects[0]['buffer']
        cls.__opengl_spec['vao_binding']['element_array_buffer'] = vao_ibo_binding

        for key, val in cls.__opengl_spec['vao_binding'].items():
            result_strings.append(f'{" " * (24 - len(key))}{key} : {val}')

        for win in window1, window2: raw_glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check DONE')

        # print resuts:
        for row in result_strings:
            print(row)
        print()

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
        remove window from view

        Release window object from traction so it could be destroied and collected by gc.

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
        return bool(self.__context_set)

    @classmethod
    def _checkbuild_meta(cls, context, shared):
        """
        find `MetaContext` and build if nonexistent

        :param context: to check context of
        :param shared: shared window
        :return:
        """
        if shared is None:
            return cls(context)
        else:
            for mc in ContextMaster.iter_meta_context():
                if mc.is_member_window(shared):
                    mc._add_context(context)
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

    def _add_context(self, context):
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
        :param share:
        """
        ContextMaster.checkinit_context()
        self.__meta_context = MetaContext._checkbuild_meta(self, share)
        self.__window = weakref.ref(window)
        self.__glfw_context = GLFWContext(width, height, title, monitor, share)
        self.__renderer_context = OpenglContext(self)
        self.__init_local_setting()
        # self._gl_logger = Logger(size=1000, do_log=True, prefix='OpenGL_', sufix='')

    def __init_local_setting(self):
        """
        initial local glfw, gl(can it be locasl?) settings
        :return:
        """
        pass

    @property
    def gl(self):
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
