from .._opengl import *
from ..primitive.program_shader_nodes import *

class ConShdrPrgrm(OpenglNode):

    in0_vrtx_shdr_src = Inout(typs=str)
    in1_frgmt_shdr_src = Inout(typs=str)
    out0_prgrm = Output(typs=PrgrmObj)

    def __init__(self, vrtx_shdr_src, frgmt_shdr_src):
        super().__init__()
        self.in0_vrtx_shdr_src = vrtx_shdr_src
        self.in1_frgmt_shdr_src = frgmt_shdr_src

    def calculate(self, vrtx_shdr_src, frgmt_shdr_src):
        vso = ConVrtxShdr().out0_vrtx_shdr
        fso = ConFrgmtShdr().out0_frgmt_shdr
        vso = CompileShdr(vso, vrtx_shdr_src).out0_shdr
        fso = CompileShdr(fso, frgmt_shdr_src).out0_shdr

        po = ConPrgrm().out0_prgrm
        gl.glAttachShader(po.r.id, vso.r.id)
        gl.glAttachShader(po.r.id, fso.r.id)
        gl.glLinkProgram(po.r.id)
        if not gl.glGetProgramiv(po.r.id, gl.GL_LINK_STATUS):
            raise Exception("Program Shader link FAIL")
        DeleteShdr(vso)
        DeleteShdr(fso)
        return po.r
