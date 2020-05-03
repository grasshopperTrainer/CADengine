from collections import deque
import time
import glfw
import OpenGL.GL as gl

class Logger:
    def __init__(self, size=1000, do_log=True):
        """
        Container for logging.
        :param size: max length of logging record. Infinite if given -1.
        :param do_log: Switch for logging.
        """
        self._is_logging = do_log
        self._size = size
        self._record = deque()

    def log(self, message):
        if len(self._record) == self._size:
            self._record.popleft()
        self._record.append(message)

    @property
    def is_logging(self):
        return self._is_logging
    @is_logging.setter
    def is_logging(self, v):
        if not isinstance(v, bool):
            raise TypeError()
        self._is_logging = v


class GL_controller:
    def __init__(self, root, logger):
        """
        Access gate into GL functions for logging and overriding.
        :param root: Unique context holding this instance.
        :param logger: Logging message container.
        """
        self._root = root
        self._logger = logger

    def __getattribute__(self, item):
        """
        Priorly For logging, controlling automated behaviour
        :param item:
        :return:
        """
        if hasattr(gl, item):
            # log
            object.__getattribute__(self, '_logger').log(f'GL <{item}> called')
            return gl.__dict__[item]
        try:
            return object.__getattribute__(self, item)
        except:
            raise AttributeError(f'No such GL attribute <{item}>')

    @property
    def log(self):
        return self._logger


class GLFW_controller:

    def __init__(self, logger, root=None):
        """
        Access gate into GLFW functions for logging and overriding.
        :param root: Unique context holding this instance.
        :param logger: Logging message container.
        """
        self._root = root
        self._logger = logger

    def __getattribute__(self, item):
        """
        Priorly For logging, controlling automated behaviour
        :param item:
        :return:
        """
        if hasattr(glfw, item):
            # log
            object.__getattribute__(self, '_logger').log(f'GLFW <{item}> called')
            return glfw.__dict__[item]
        try:
            return object.__getattribute__(self, item)
        except:
            raise AttributeError(f'No such GLFW attribute <{item}>')

    @property
    def log(self):
        return self._logger
    @property
    def global_log(self):
        return self._root._global_glfw._logger


class _global_glfw(type):
    """
    Metaclass for building view on class attributes.
    """

    @property
    def glfw(cls):
        return cls._global_glfw


class GLFW_GL_Context(metaclass=_global_glfw):
    """Class for launching GLFW context and testing GL behavior on it."""

    _global_glfw = GLFW_controller(Logger(size=100))    # for recording global glfw

    _gl_object_shareness = {} # whether shared glfw contexts actually share gl objects
    _gl_VAO_children_binding = {} # whether vao binding binds object bounded to VAO ex) ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER

    _gl_version = None
    _gl_renderer = None
    _gl_vendor = None
    _glfw_version = None

    _is_glfw_inited = False

    @classmethod
    def spec_check(cls):
        """
        Tests GL behavior on GLFW context.

        Tested subjects are such as :
        GL object shareness
        GL vertax array objects' children binding
        basic glfw-gl info

        :return: None
        """
        result_strings = ['GLFW context specification result:',]

        if glfw.init():
            cls._is_glfw_inited = True
        else:
            raise Exception('Can not initiate glfw')

        # not to display and window while going through multiple tests
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        # two windows needed for testing shareness properties
        window1 = glfw.create_window(1,1,'first', monitor=None, share=None)
        window2 = glfw.create_window(1,1,'first', monitor=None, share=window1)
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)

        # check object shareness
        result_strings.append('\n    GL object shareness :')
        opengl_objects = [] # opengl objects used in testing
        for win in window1, window2:
            dic = {}
            opengl_objects.append(dic)

            glfw.make_context_current(win) # objects below belongs to this window
            dic['buffer'] = gl.glGenBuffers(1)
            dic['vertex_array'] = gl.glGenVertexArrays(1)
            dic['program'] = gl.glCreateProgram()                  # program and shader share ID
            dic['shader'] = gl.glCreateShader(gl.GL_VERTEX_SHADER) # so this results 2
            dic['texture'] = gl.glGenTextures(1)
            dic['render_buffer'] = gl.glGenRenderbuffers(1)
            dic['frame_buffer'] = gl.glGenFramebuffers(1)

        # logic is simple : if window2 object's index is 2 not 1
        # means window2 shared object with window1
        for key, val in opengl_objects[0].items():
            cls._gl_object_shareness[key] = True
            if val == opengl_objects[1][key]:
                cls._gl_object_shareness[key] = False
            front_blank = " "*(len(result_strings[1]) - len(key) - 3)
            result_strings.append(f'{front_blank}{key} : {"SHARED" if cls._gl_object_shareness[key] else "NOT SHARED"}')

        # store some info
        cls._glfw_version = glfw.get_version_string()
        cls._gl_version = gl.glGetString(gl.GL_VERSION)
        cls._gl_renderer = gl.glGetString(gl.GL_RENDERER)
        cls._gl_vendor = gl.glGetString(gl.GL_VENDOR)
        result_strings.append('\n    Some basic info :')
        result_strings.append(f'       glfw_version : {cls._glfw_version}')
        result_strings.append(f'         gl_version : {cls._gl_version}')
        result_strings.append(f'        gl_renderer : {cls._gl_renderer}')
        result_strings.append(f'          gl_vendor : {cls._gl_vendor}')

        result_strings.append('\n    VAO children binding :')
        # TODO actual testing needed
        cls._gl_VAO_children_binding['array_buffer'] = True
        cls._gl_VAO_children_binding['element_array_buffer'] = False
        for key, val in cls._gl_VAO_children_binding.items():
            result_strings.append(f'{" "*(24-len(key))}{key} : {val}')

        for win in window1, window2: glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check DONE')

        # print resuts:
        for row in result_strings:
            print(row)
        print()

    @classmethod
    def is_glfw_initiated(cls):
        return cls._is_glfw_inited

    # def __getattr__(self, item):
    #     """
    #     Redirector to <glfw> module.
    #     :param item:
    #     :return:
    #     """
    #     if hasattr(glfw, item):
    #         return_val = glfw.__dict__[item]
    #         if self._logging:   # initially logging set at __init__ using **kwargs
    #             Logger.log((time.time(), str(self), item, str(return_val)))
    #         return return_val
    #     else:
    #         raise AttributeError(f"Neither <My_glfw_gl> nor <glfw> has such attribute '{item}'")


    def __init__(self, **kwargs):   # kwargs for some setting non default options
        if not self.is_glfw_initiated():
            self.spec_check()

        self._logger = Logger()
        self._gl = GL_controller(logger=self._logger, root=self)
        self._glfw = GLFW_controller(logger=self._logger, root=self)
        self._logger.is_logging = True
        if 'logging' in kwargs:
            self._logger.is_logging = kwargs['logging']

    @property
    def gl(self):
        return self._gl
    @gl.setter
    def gl(self, v):
        raise AttributeError('this is subordinate property')

    @property
    def glfw(self):
        return self._glfw
    @glfw.setter
    def glfw(self, v):
        raise AttributeError('this is subordinate property')


if __name__ == '__main__':
    print(GLFW_GL_Context.aaa)
    print(type(GLFW_GL_Context()))