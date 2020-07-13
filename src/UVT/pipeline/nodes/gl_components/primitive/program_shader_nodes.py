from ..opengl_node import *
import UVT.hooked.openglHooked as gl
from UVT.pipeline.data_types.gl_data_types import PrgrmObj, _ShdrObj, VrtxShdrObj, FrgmtShdrObj


class ConPrgrm(OpenglNode):
    """
    Generate OpenGL Program object
    """
    out0_prgrm = Output()

    def calculate(self):
        self.out0_prgrm = PrgrmObj(gl.glCreateProgram())


class ConVrtxShdr(OpenglNode):
    """
    Generate OpenGL Vertex Shader Object
    """

    out0_vrtx_shdr = Output()

    def calculate(self):
        self.out0_vrtx_shdr = VrtxShdrObj(gl.glCreateShader(gl.GL_VERTEX_SHADER))


class ConFrgmtShdr(OpenglNode):
    """
    Generate OpenGL Fragment Shader Object
    """

    out0_frgmt_shdr = Output()

    def calculate(self):
        self.out0_frgmt_shdr = FrgmtShdrObj(gl.glCreateShader(gl.GL_FRAGMENT_SHADER))


class CompileShdr(OpenglNode):
    """
    Compile and Attach shader shader
    """

    in0_shdr = Input(typs=_ShdrObj)
    in1_source = Input(typs=str)
    out0_shdr = Output()

    def __init__(self, shader, source):
        super().__init__()
        self.in0_shdr = shader
        self.in1_source = source

    def calculate(self):
        id = self.in0_shdr.id
        gl.glShaderSource(id, self.in1_source)
        gl.glCompileShader(id)
        if not gl.glGetShaderiv(id, gl.GL_COMPILE_STATUS):
            raise Exception("Shader compile FAIL")
        self.out0_shdr = self.in0_shdr


class DeleteShdr(OpenglNode):
    """
    Delete OpenGL Shader Object
    """
    in0_shdr = Input()

    def __init__(self, shdr):
        self.in0_shdr = shdr

    def calculate(self):
        gl.glDeleteShader(self.in0_shdr.r.id)
        self.in0_shdr.r._id = None


class UsePrgrm(OpenglNode):
    """
    Bind OpenGL Program Object
    """
