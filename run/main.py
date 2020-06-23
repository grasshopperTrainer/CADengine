from UVT import Window
from UVT.pipeline import Pipeline, comp
import glfw
import numpy as np

window1 = Window.new_window(200,200, 'f', monitor=None, shared=None)
# window2 = Window.new_window(1000,1000, 's', monitor=None, shared=window1)

with window1 as w:
    ppl = Pipeline(w)
    vao = comp.VertexArray()

    vbo = comp.VertexBuffer()
    vertex = comp.FloatVector([-1.0, -1.0, 0.0,
                            1.0, -1.0, 0.0,
                            0.0, 1.0, 0.0])
    ppl.relate(vertex, 'value', 'data', vbo)

    # vbo.input_data(vertex)
    #
    # ibo = components.IndexBuffer(w)
    # ibo.input_data([0,1,2])
    #
    # vao.bind()
    # vbo.bind()
    # w.gl.glDrawArrays(w.gl.GL_LINES, 0, 3)

Window.run()