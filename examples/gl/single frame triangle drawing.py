from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200,200, 'f', monitor=None, shared=None)

with window1 as w:
    vertex = [[-1, -1, 0], [1, -1, 0], [0, 1, 0], [1,1,0]]
    va = comp.ConOpenglData('coord', vertex, 'f')
    vbo = comp.ConVertexBuffer(w)
    vao = comp.ConVertexArray(w)
    #
    buffer_pusher = comp.PushBufferData(w)
    enabler = comp.EnableVertexAttribute(w)

    buffer_pusher.in1_data = va.gl_data
    buffer_pusher.in0_bffr = vbo.vrtx_bffr
    enabler.vrtx_arry = vao.vrtx_arry
    enabler.vrtx_attr = va.gl_data
    #
    joiner = comp.JoinVrtxArryVrtxBffr(w)
    joiner.vrtx_arry = vao.vrtx_arry
    joiner.vrtx_bffr = vbo.vrtx_bffr

    tri_drawer = comp.DrawTriangle(w, joiner.vrtx_arry_out, comp.Bound(1,4))

    # tri_drawer.vrtx_arry = joiner.vrtx_arry_out

    print(tri_drawer.render_attempt)

Window.run(1)