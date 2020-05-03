import time
import glfw
import OpenGL.GL as gl

class GLFW_logger:
    _glfw_log = []

    @classmethod
    def log(cls, v):
        cls._glfw_log.append(v)

class _global_glfw(type):

    def __getattr__(cls, item):

        """
        Redirector directing to global <glfw> methods.
        :param item:
        :return:
        """
        if hasattr(glfw, item):
            return_val = glfw.__dict__[item]
            if False:   # initially logging set at __init__ using **kwargs
                GLFW_logger.log((time.time(), '', item, str(return_val)))
            return return_val
        else:
            raise AttributeError(f"<glfw> has such attribute '{item}'")

class My_glfw(metaclass=_global_glfw):
    """Class for launching GLFW context and testing GL behavior on it."""

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

    def __getattr__(self, item):
        """
        Redirector to <glfw> module.
        :param item:
        :return:
        """
        if hasattr(glfw, item):
            return_val = glfw.__dict__[item]
            if self._logging:   # initially logging set at __init__ using **kwargs
                GLFW_logger.log((time.time(), str(self), item, str(return_val)))
            return return_val
        else:
            raise AttributeError(f"Neither <My_glfw_gl> nor <glfw> has such attribute '{item}'")


    def __init__(self, **kwargs):   # kwargs for some setting non default options
        if not self.is_glfw_initiated():
            self.spec_check()

        self._logging = True if 'logging' in kwargs else False

if __name__ == '__main__':
    print(My_glfw.aaa)
    print(type(My_glfw()))