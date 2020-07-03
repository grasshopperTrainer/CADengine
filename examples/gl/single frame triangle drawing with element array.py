from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200,200, 'f', monitor=None, shared=None)

with window1 as w:
    vertex = [[-0.8, -0.8, 0], [0.8, -0.8, 0], [-0.8, 0.8, 0], [0.8,0.8,0]]
    vertex = comp.ConOpenglData('coord', vertex, 'f')
    index = comp.ConOpenglData('indx', (0,1,2,3), 'uint')
    vao = comp.ConVertexArray(w)
    vbo = comp.ConVertexBuffer(w)
    ibo = comp.ConIndexBuffer(w)

    data_vbo = comp.PushBufferData(w, vbo.vrtx_bffr, vertex.gl_data).out0_data_bffr
    data_ibo = comp.PushBufferData(w, ibo.indx_bffr, index.gl_data).out0_data_bffr

    enhancer = comp.EnhanceVertexArray(w)
    enhancer.set_inputs(vao.vrtx_arry, data_vbo, data_ibo)

    # print(enhancer.out0_vrtx_arry)
    de = comp.DrawElement(w, enhancer.out0_vrtx_arry, data_ibo, w.gl.GL_TRIANGLE_STRIP)
    # tri_drawer = comp.DrawTriangle(w, enhancer.out0_vrtx_arry, comp.Bound(1,4))
    print(de.out0_render_result)

Window.run(1)