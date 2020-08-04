from .._opengl import *

class ConPrgrm(OpenglNode):
    """
    Generate OpenGL Program object
    """
    out0_prgrm = Output()

    def calculate(self):
        return PrgrmObj(gl.glCreateProgram())


class ConVrtxShdr(OpenglNode):
    """
    Generate OpenGL Vertex Shader Object
    """

    out0_vrtx_shdr = Output()

    def calculate(self):
        return VrtxShdrObj(gl.glCreateShader(gl.GL_VERTEX_SHADER))


class ConFrgmtShdr(OpenglNode):
    """
    Generate OpenGL Fragment Shader Object
    """

    out0_frgmt_shdr = Output()

    def calculate(self):
        return FrgmtShdrObj(gl.glCreateShader(gl.GL_FRAGMENT_SHADER))


class CompileShdr(OpenglNode):
    """
    Compile and Attach shader shader
    """

    in0_shdr = Input(typs=ShdrObj)
    in1_source = Input(typs=str)
    out0_shdr = Output()

    def __init__(self, shader, source):
        super().__init__()
        self.in0_shdr = shader
        self.in1_source = source

    def calculate(self, shdr, source):
        id = shdr.id
        gl.glShaderSource(id, source)
        gl.glCompileShader(id)
        if not gl.glGetShaderiv(id, gl.GL_COMPILE_STATUS):
            raise Exception("Shader compile FAIL")
        return self.in0_shdr.r


class DeleteShdr(OpenglNode):
    """
    Delete OpenGL Shader Object
    """
    in0_shdr = Input()

    def __init__(self, shdr):
        super().__init__()
        self.in0_shdr = shdr

    def calculate(self, shdr):
        gl.glDeleteShader(shdr.r.id)
        shdr.r._id = None


class UsePrgrm(OpenglNode):
    """
    Bind OpenGL Program Object
    """

class PushUniform(OpenglNode):
    in0_prgrm = Input()
    in1_data = Input()

    out0_prgm = Output()

    def calculate(self, prgrm, data):
        gl.glUseProgram(prgrm.id)
        for name, size, type, stride, offset, sub_data in data.properties:
            loc = gl.glGetUniformLocation(prgrm.id, name)
            if type == gl.GL_FLOAT:
                if size == 1:
                    gl.glUniform1f(loc, *sub_data)
                elif size == 2:
                    gl.glUniform2f(loc, *sub_data)
                elif size == 3:
                    gl.glUniform3f(loc, *sub_data)
                elif size == 4:
                    gl.glUniform4f(loc, *sub_data)
            else:
                raise

        return prgrm