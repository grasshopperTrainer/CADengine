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
