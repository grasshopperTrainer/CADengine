from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200, 200, 'f', monitor=None, shared=None)

with window1 as w:
    # raw data
    vertex = [[-0.8, -0.8, 0], [0.8, -0.8, 0], [-0.8, 0.8, 0], [0.8, 0.8, 0]]
    vertex = comp.ConOpenglData('coord', vertex, 'f')
    index = comp.ConOpenglData('indx', (0, 1, 2, 3), 'uint')

    # opengl objects
    vao = comp.ConVertexArray(w)
    vbo = comp.ConVertexBuffer(w)
    ibo = comp.ConIndexBuffer(w)

    # push raw data into buffers
    vertex_pusher = comp.PushBufferData(w, vbo.vrtx_bffr, vertex.out0_gl_data)
    data_vbo = vertex_pusher.out0_data_bffr
    data_ibo = comp.PushBufferData(w, ibo.indx_bffr, index.out0_gl_data).out0_data_bffr

    # make vertex attribut buffers(VABO?) and index buffer(IBO) known to VAO
    enhancer = comp.EnhanceVertexArray(w)
    enhancer.set_inputs(vao.vrtx_arry, data_vbo, data_ibo)

    # check component graph refreshing
    new_vertex = [[-0.8, -0.8, 0], [0.8, -0.8, 0], [-0.8, 0.8, 0], [0.5, 0.5, 0]]
    vertex_pusher.in1_data = comp.ConOpenglData('coord', new_vertex, 'f').out0_gl_data

    # draw
    de = comp.DrawElement(w, enhancer.out0_vrtx_arry, data_ibo, w.gl.GL_TRIANGLE_STRIP)
    print(de.out0_render_result)

Window.run(1)
