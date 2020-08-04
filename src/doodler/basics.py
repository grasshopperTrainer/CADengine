from my_patterns import SingletonClass
from UVT.env.draw_bit import DrawBit
import UVT.hooked.openglHooked as gl
import UVT.pipeline.nodes as node
from noding.flow_control import Stream, Gate, Conveyor
from noding.logical import Equal
import numpy as np
from UVT.env.windows import Windows


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
        self._con_vrtx_data = node.ConOpenglData('vertex', ((0, 0, 0), (0, 0, 0), (0, 0, 0)), 'f')
        vrtx_data_bffr = node.PushBufferData(self._vbo, self._con_vrtx_data.out0_gl_data).out0_data_bffr
        index = node.ConOpenglData('index', (0, 1, 2), 'uint').out0_gl_data
        indx_data_bffr = node.PushBufferData(self._ibo, index).out0_data_bffr

        # pushing uniform
        self._uniform_pusher = node.PushUniform()
        self._uniform_pusher.in0_prgrm =prgrm
        self._uniform_pusher.in1_data = node.ConOpenglData('color', (1,0,1,1), 'f').out0_gl_data
        prgrm = self._uniform_pusher.out0_prgm

        # enhance once and make renderer listen to vrtx_data_bffr
        node.EnhanceVertexArray(self._vao, vrtx_data_bffr, indx_data_bffr).refresh()
        listener = node.Listener()
        listener.in0_listento = vrtx_data_bffr
        listener.in0_listento.append_sibling_intf(self._vao)
        listener.out0_listened.append_sibling_intf()
        # rendering
        self._renderer = node.RenderArray(listener.out0_listened_1, prgrm, gl.GL_TRIANGLES)

    def _set_vertex(self, v0, v1, v2):
        self._con_vrtx_data.in1_data = v0, v1, v2

    def draw(self):
        self._renderer.refresh()


def triangle(v1, v2, v3):
    # make matrix of vertex
    v = np.array([v1, v2, v3])
    v = np.transpose(v)
    v = np.vstack((v, [1, 1, 1]))

    vm = Windows.get_current().cameras.current_target().tripod_VM.r
    pm = Windows.get_current().cameras.current_target().body_PM.r

    v = np.dot(vm, v)
    v = np.dot(pm, v)
    # set back to list
    v[:,0] = v[:,0]/v[3,0]
    v[:,1] = v[:,1]/v[3,1]
    v[:,2] = v[:,2]/v[3,2]
    v = np.transpose(v[:3])
    v = v.tolist()
    TriangleDrawer()._set_vertex(*v)
    TriangleDrawer().draw()
