from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200, 200, 'f', monitor=None, shared=None)

window1.viws.append(0.25,0.25,0.5,0.5)

@window1.run_all(lyr = window1.lyrs[0], viw=window1.viws[1], cam=window1.cams[0])
def a():
    w = window1
    # raw data
    vertex = [[-0.8, -0.8, 0], [0.8, -0.8, 0], [-0.8, 0.8, 0], [0.8, 0.8, 0]]
    vertex = comp.ConSingleNamedData('coord', vertex, 'f')
    index = comp.ConSingleNamedData('indx', (0, 1, 2, 3), 'uint')

    # opengl objects
    vao = comp.ConVertexArray(w)
    vbo = comp.ConVertexBuffer(w)
    ibo = comp.ConIndexBuffer(w)

    # push raw data into buffers
    vertex_pusher = comp.PushBufferData(w, vbo.out0_vrtx_bffr, vertex.out0_ndata)
    data_vbo = vertex_pusher.out0_data_bffr
    data_ibo = comp.PushBufferData(w, ibo.out0_indx_bffr, index.out0_ndata).out0_data_bffr

    # make vertex attribut buffers(VABO?) and index buffer(IBO) known to VAO
    enhancer = comp.EnhanceVertexArray(w)
    enhancer.set_inputs(vao.vrtx_arry, data_vbo, data_ibo)

    # check component graph refreshing
    new_vertex = [[-0.8, -0.8, 0], [0.8, -0.8, 0], [-0.8, 0.8, 0], [0.5, 0.5, 0]]
    vertex_pusher.in1_data = comp.ConSingleNamedData('coord', new_vertex, 'f').out0_ndata

    # draw
    de = comp.RenderElement(w, enhancer.out0_vrtx_arry, data_ibo, w.gl.GL_TRIANGLE_STRIP)
    de.out0_render_result

Window.run_all()
