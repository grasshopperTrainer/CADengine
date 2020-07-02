from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200,200, 'f', monitor=None, shared=None)

with window1 as w:
    vertex = [[-1, -1, 0], [1, -1, 0], [0, 1, 0], [1,1,0]]
    vertex = comp.ConOpenglData('coord', vertex, 'f')
    index = comp.ConOpenglData('indx', (0,1,2,0,2,3), 'uint')
    vao = comp.ConVertexArray(w)
    vbo = comp.ConVertexBuffer(w)
    ibo = comp.ConIndexBuffer(w)

    data_vbo = comp.PushBufferData(w, vbo.vrtx_bffr, vertex.gl_data).data_bffr
    data_ibo = comp.PushBufferData(w, ibo.indx_bffr, index.gl_data).data_bffr

    enhancer = comp.EnhanceVertexArray(w)
    # tri_drawer = comp.DrawTriangle(w, joiner.vrtx_arry_out, comp.Bound(1,4))
    # print(tri_drawer.render_attempt)

Window.run(1)