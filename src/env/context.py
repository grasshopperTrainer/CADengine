import glfw
import OpenGL.GL as gl

class My_glfw_gl:
    """Class for launching GLFW context and testing GL behavior on it."""
    gl_object_shareness = {} # whether shared glfw contexts actually share gl objects
    gl_VAO_children_binding = {} # whether vao binding binds object bounded to VAO ex) ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER

    gl_version = None
    gl_renderer = None
    gl_vendor = None
    glfw_version = None

    is_glfw_inited = False

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
            cls.is_glfw_inited = True
        else:
            raise Exception('Can not initiate glfw')

        # not to display and window while going through multiple tests
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        # two windows needed for testing shareness properties
        window1 = glfw.create_window(1,1,'first', monitor=None, share=None)
        window2 = glfw.create_window(1,1,'first', monitor=None, share=window1)

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
            cls.gl_object_shareness[key] = True
            if val == opengl_objects[1][key]:
                cls.gl_object_shareness[key] = False
            front_blank = " "*(len(result_strings[1]) - len(key) - 3)
            result_strings.append(f'{front_blank}{key} : {"SHARED" if cls.gl_object_shareness[key] else "NOT SHARED"}')

        # store some info
        cls.glfw_version = glfw.get_version_string()
        cls.gl_version = gl.glGetString(gl.GL_VERSION)
        cls.gl_version = gl.glGetString(gl.GL_RENDERER)
        cls.gl_version = gl.glGetString(gl.GL_VENDOR)
        result_strings.append('\n    Some basic info :')
        result_strings.append(f'       glfw_version : {cls.glfw_version}')
        result_strings.append(f'         gl_version : {cls.gl_version}')
        result_strings.append(f'        gl_renderer : {cls.gl_renderer}')
        result_strings.append(f'          gl_vendor : {cls.gl_vendor}')

        result_strings.append('\n    VAO children binding :')
        # TODO actual testing needed
        cls.gl_VAO_children_binding['array_buffer'] = True
        cls.gl_VAO_children_binding['element_array_buffer'] = False
        for key, val in cls.gl_VAO_children_binding.items():
            result_strings.append(f'{" "*(24-len(key))}{key} : {val}')

        for win in window1, window2: glfw.destroy_window(win)
        result_strings.append('\nGLFW context specification check done')

        # print resuts:
        for row in result_strings:
            print(row)
        print()

if __name__ == '__main__':
    My_glfw_gl.spec_check()