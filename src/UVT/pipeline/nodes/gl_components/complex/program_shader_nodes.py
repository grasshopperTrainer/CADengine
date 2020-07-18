from ..opengl_node import *
from ..primitive.program_shader_nodes import *
import UVT.hooked.openglHooked as gl

class ConShdrPrgrm(OpenglNodeBody):

    in0_vrtx_shdr_src = Inout(typs=str)
    in1_frgmt_shdr_src = Inout(typs=str)
    out0_prgrm = Output(typs=PrgrmObj)

    def __init__(self, vrtx_shdr_src, frgmt_shdr_src):
        super().__init__()
        self.in0_vrtx_shdr_src = vrtx_shdr_src
        self.in1_frgmt_shdr_src = frgmt_shdr_src

    def calculate(self):
        vso = ConVrtxShdr().out0_vrtx_shdr
        fso = ConFrgmtShdr().out0_frgmt_shdr
        vso = CompileShdr(vso, self.in0_vrtx_shdr_src).out0_shdr
        fso = CompileShdr(fso, self.in1_frgmt_shdr_src).out0_shdr

        po = ConPrgrm().out0_prgrm
        gl.glAttachShader(po.r.id, vso.id)
        gl.glAttachShader(po.r.id, fso.id)
        gl.glLinkProgram(po.r.id)
        if not gl.glGetProgramiv(po.r.id, gl.GL_LINK_STATUS):
            raise Exception("Program Shader link FAIL")
        DeleteShdr(vso)
        DeleteShdr(fso)
        self.out0_prgrm = po
