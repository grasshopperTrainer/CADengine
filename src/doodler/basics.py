import wkernel.hooked.openglHooked as gl
import wkernel.pipeline.nodes as node
from global_tools import Singleton
from wkernel.env.components.bits import DrawInterface


@Singleton
class TriangleDrawer(DrawInterface):
    def __init__(self):
        # generation
        self._vao = node.ConVertexArray().out0_vrtx_arry
        self._vbo = node.ConVertexBuffer().out0_vrtx_bffr
        self._ibo = node.ConIndexBuffer().out0_indx_bffr

        with open('C:/Users/dingo/OneDrive/prgrm_dev/pyopengl2/src/wkernel/res/glsl/simple_vrtx_shdr.glsl', 'r') as f:
            vs_source = f.read()
        with open('C:/Users/dingo/OneDrive/prgrm_dev/pyopengl2/src/wkernel/res/glsl/simple_frgmt_shdr.glsl', 'r') as f:
            fs_source = f.read()
        prgrm = node.ConShdrPrgrm(vrtx_shdr_src=vs_source, frgmt_shdr_src=fs_source).out0_prgrm
        # pushing data
        self._con_vrtx_data = node.ConSingleNamedData('vertex', ((0, 0, 0), (0, 0, 0), (0, 0, 0)), 'f')
        vrtx_data_bffr = node.PushBufferData(self._vbo, self._con_vrtx_data.out0_ndata).out0_data_bffr
        index = node.ConSingleNamedData('index', (0, 1, 2), 'uint').out0_ndata
        indx_data_bffr = node.PushBufferData(self._ibo, index).out0_data_bffr

        # pushing uniform
        uniform_pusher = node.PushUniform()
        uniform_pusher.in0_prgrm =prgrm
        uniform_pusher.in1_data = node.ConSingleNamedData('color', (1, 0, 1, 1), 'f').out0_ndata
        prgrm = uniform_pusher.out0_prgm

        # pushing matrises
        pm = node.GetCurrentCamera().body_PM
        vm = node.GetCurrentCamera().tripod_VM
        ndata = node.JoinNamedData()
        ndata.in0_ndata = node.ConSingleNamedData('PM', pm, 'f').out0_ndata
        ndata.in0_ndata.append_sibling_intf(node.ConSingleNamedData('VM', vm, 'f').out0_ndata)
        ndata = ndata.out0_ndata
        uniform_pusher = node.PushUniform(prgrm, ndata)
        prgrm = uniform_pusher.out0_prgm
        # print(uniform_pusher.in1_data.r._data)

        # enhance once and make renderer listen to vrtx_data_bffr
        node.EnhanceVertexArray(self._vao, vrtx_data_bffr, indx_data_bffr).refresh()
        listener = node.Listener()
        listener.in0_listento = vrtx_data_bffr
        listener.in0_listento.append_sibling_intf(self._vao)
        listener.out0_listened.append_sibling_intf()

        self._renderer = node.RenderArray(listener.out0_listened_1, prgrm, gl.GL_TRIANGLES)

    def _set_vertex(self, v0, v1, v2):
        self._con_vrtx_data.in1_data = v0, v1, v2

    def draw(self):
        self._renderer.refresh()

    def setup(self):
        pass


def triangle(v0, v1, v2):
    TriangleDrawer()._set_vertex(v0, v1, v2)
    TriangleDrawer().draw()
