from UVT import Window
import UVT.pipeline as comp
import glfw
import numpy as np

window1 = Window.new_window(200,200, 'f', monitor=None, shared=None)

with window1 as w:
    pipeline = comp.ComplexComponent()
    pipeline.add_interface(comp.WindowInput(w))

    vertex = [[-1, -1, 0], [1, -1, 0], [0, 1, 0]]
    vrtx_attr = comp.ConSingleVertexAttribute('coord', vertex, 'f')
    vbo = comp.ConVertexBuffer()
    vao = comp.ConVertexArray()

    buffer_pusher = comp.PushBufferData()
    enabler = comp.EnableVertexAttribute()

    pipeline.relate(vrtx_attr, 'vrtx_attr', 'vrtx_attr', buffer_pusher)
    pipeline.relate(vbo, 'vrtx_bffr', 'vrtx_bffr', buffer_pusher)
    pipeline.relate(vao, 'vrtx_arry', 'vrtx_arry', enabler)
    pipeline.relate(vrtx_attr, 'vrtx_attr', 'vrtx_attr', enabler)

    joiner = comp.JoinVrtxArryVrtxBffr()
    pipeline.relate(vao, 'vrtx_arry', 'vrtx_arry', joiner)
    pipeline.relate(vbo, 'vrtx_bffr', 'vrtx_bffr', joiner)
    tri_drawer = comp.DrawTriangle()
    pipeline.relate(joiner, 'vrtx_arry', 'vrtx_arry', tri_drawer)

    pipeline.operate()

Window.run(1)