from global_tools.singleton import Singleton
import glfw
import OpenGL.GL as gl


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
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        # two windows needed for testing shareness
        window1 = glfw.create_window(1, 1, 'first', monitor=None, share=None)
        window2 = glfw.create_window(1, 1, 'first', monitor=None, share=window1)
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE)

        # check object shareness
        result_strings.append('')
        result_strings.append(f"{'GL object shareness':>33} :")
        objs = {}  # opengl objects used in testing
        for win in window1, window2:
            glfw.make_context_current(win)  # objects below belongs to this window
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

        for win in window1, window2: glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check DONE')

        # print resuts:
        for row in result_strings:
            print(row)
        print()