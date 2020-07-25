from collections import deque
import time
import glfw
import OpenGL.GL as gl


class Logger:
    """
    Log container.
    """

    def __init__(self, size=1000, do_log=True, prefix='', sufix=''):
        """
        :param size: max length of logging record. Infinite if given -1.
        :param do_log: Switch for logging.
        """
        self._is_logging = do_log
        self._size = size
        self._record = deque()
        self._prefix = prefix
        self._sufix = sufix

    def log(self, message):
        """
        Log message
        :param message:
        :return:
        """
        if len(self._record) == self._size:
            self._record.popleft()
        self._record.append(f"{self._prefix}{message}{self._sufix}")

    @property
    def is_logging(self):
        return self._is_logging
    @is_logging.setter
    def is_logging(self, v):
        if not isinstance(v, bool):
            raise TypeError()
        self._is_logging = v


class ContextManager:
    """Class for launching GLFW context and testing GL behavior on it."""

    _gl_object_shareness = {} # whether shared glfw contexts actually share opengl objects
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
        basic glfw-opengl info

        :return: None
        """
        result_strings = ['GLFW context specification result:',]

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

        cls._gl_VAO_children_binding['array_buffer'] = True
        # ibo visibility test
        gl.glBindVertexArray(opengl_objects[0]['vertex_array'])
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, opengl_objects[0]['buffer'])
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(opengl_objects[0]['vertex_array'])
        vao_ibo_binding = gl.glGetInteger(gl.GL_ELEMENT_ARRAY_BUFFER_BINDING) == opengl_objects[0]['buffer']
        cls._gl_VAO_children_binding['element_array_buffer'] = vao_ibo_binding

        for key, val in cls._gl_VAO_children_binding.items():
            result_strings.append(f'{" "*(24-len(key))}{key} : {val}')

        for win in window1, window2: glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check DONE')

        # print resuts:
        for row in result_strings:
            print(row)
        print()

    @classmethod
    def init_setting(cls):
        """
        Initial setting of GLFW, openGL
        :return:
        """
        pass

    @classmethod
    def is_glfw_initiated(cls):
        return cls._is_glfw_inited

    def __init__(self, **kwargs):   # kwargs for some setting non default options
        if not self.is_glfw_initiated():
            if not glfw.init():
                raise Exception('Can not initiate glfw')
            self.__class__._is_glfw_inited = True
            self.spec_check()
            self.init_setting()

        self._gl_logger = Logger(size=1000, do_log=True, prefix='OpenGL_', sufix='')
        self._glfw_logger = Logger(size=1000, do_log=True, prefix='GLFW_', sufix='')

    def log_gl(self, mesg):
        self._gl_logger.log(mesg)

    def log_glfw(self, mesg):
        self._glfw_logger.log(mesg)


if __name__ == '__main__':
    print(ContextManager.aaa)
    print(type(ContextManager()))