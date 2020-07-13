from UVT.patterns import SingletonClass
from UVT.env.draw_bit import DrawBit
import UVT.hooked.openglHooked as gl
import UVT.pipeline.nodes as node


class TriangleDrawer(DrawBit, SingletonClass):
    def __init__(self):
        # generation
        self._vao = node.ConVertexArray().out0_vrtx_arry
        self._vbo = node.ConVertexBuffer().out0_vrtx_bffr
        self._ibo = node.ConIndexBuffer().out0_indx_bffr
        with open('C:/Users/dingo/OneDrive/prgrm_dev/pyopengl2/src/UVT/res/glsl/simple_vrtx_shdr.glsl', 'r') as f:
            vs_source = f.read()
        with open('C:/Users/dingo/OneDrive/prgrm_dev/pyopengl2/src/UVT/res/glsl/simple_frgmt_shdr.glsl', 'r') as f:
            fs_source = f.read()
        prgrm = node.ConShdrPrgrm(vrtx_shdr_src=vs_source, frgmt_shdr_src=fs_source).out0_prgrm

        # pushing data
        self._con_vrtx_data = node.ConOpenglData('vertex', ((0,0,0), (0,0,0), (0,0,0)), 'f')
        vrtx_data_bffr = node.PushBufferData(self._vbo, self._con_vrtx_data.out0_gl_data).out0_data_bffr
        index = node.ConOpenglData('index', (0,1,2), 'uint').out0_gl_data
        indx_data_bffr = node.PushBufferData(self._ibo, index).out0_data_bffr
        # binding
        vao = node.EnhanceVertexArray(self._vao, vrtx_data_bffr, indx_data_bffr).out0_vrtx_arry

        # rendering
        self._renderer = node.RenderArray(vao, prgrm=prgrm, mode=gl.GL_TRIANGLES)

    def _set_vertex(self, v0, v1, v2):
        self._con_vrtx_data.in1_data = v0, v1, v2

    def draw(self):
        self._renderer.refresh()

def triangle(v1, v2, v3):
    TriangleDrawer()._set_vertex(v1, v2, v3)
    TriangleDrawer().draw()

