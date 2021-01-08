from .._opengl import *
import OpenGL.GL as gl

import inspect
import numpy as np
import glfw





class BufferComponent(OpenglNode):
    """
    Buffer for Buffer component.

    Organizes creation of new buffer component.
    These classes have '(OpenGL)_id' attribute.
    """
    _kind = None

    # def __str__(self):
    #     return f"<'{self.__class__.__name__}' of id : {self.id}>"

    @property
    def is_renderable(self):
        return False


class ConVertexBuffer(BufferComponent):
    out0_vrtx_bffr = Output(None)
    _kind = gl.GL_ARRAY_BUFFER

    def calculate(self):
        return VertexBufferObject(gl.glGenBuffers(1))


class ConIndexBuffer(BufferComponent):
    out0_indx_bffr = Output(None)
    _kind = opengl.GL_ELEMENT_ARRAY_BUFFER

    def calculate(self):
        return IndexBufferObject(gl.glGenBuffers(1))


class PushBufferData(BufferComponent):
    """
    Push value into a buffer using properties assigned in vertex attribute object
    """
    in0_bffr = Input()
    in1_data = Input()
    out0_data_bffr = Output()

    def __init__(self, vrtx_bffr=None, vrtx_attr=None):
        super().__init__()
        self.in0_bffr = vrtx_bffr
        self.in1_data = vrtx_attr

    def calculate(self, bffr, data):
        gl.glBindBuffer(bffr.kind, bffr.id)
        gl.glBufferData(bffr.kind,
                        data.bytesize,
                        data.data,
                        gl.GL_STATIC_DRAW)
        return DataBufferObject(bffr, data)


# class ConIndexBuffer(ConVertexBuffer):
#     def __init__(self, window: Window):
#         if window._windows.get_current() == window:
#             self._id = window.opengl.glGenBuffers(1)
#         self._kind = window.opengl.GL_ELEMENT_ARRAY_BUFFER
#         self._window = window
#
#     def input_data(self, data):
#         data = ConUnsignedIntVector(self.window, data)
#         self.data_to_push = data


# class Program(OpenglComponent):
#     pass
#
#
# class ShaderComponent(RenderComponent):
#     pass
#
#
# class FragmentShader(ShaderComponent):
#     pass
#
#
# class VertexShader(ShaderComponent):
#     pass
