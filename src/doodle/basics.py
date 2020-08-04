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
        # flow control : check if shape differed thus needing enhancing
        current_shape = node.DeconNamedData(self._con_vrtx_data.out0_gl_data).out7_shape
        prev_shape = Conveyor(1, current_shape).out0_data
        self.eq = Equal(current_shape, prev_shape)
        is_shape_same = self.eq.out0_result

        stream = Stream(is_shape_same, vrtx_data_bffr)
        stream.out0_data.append_sibling_intf()
        # binding
        vao = node.EnhanceVertexArray(self._vao, stream.out0_data, indx_data_bffr).out0_vrtx_arry
        # flow control
        gate = Gate(is_shape_same)
        gate.in1_data = vao
        gate.in1_data.append_sibling_intf(self._vao)

        # rendering
        self._renderer = node.RenderArray(gate.out0_data, prgrm, gl.GL_TRIANGLES)

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
