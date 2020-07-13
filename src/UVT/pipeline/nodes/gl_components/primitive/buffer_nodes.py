from ..._node import *
from ..opengl_node import OpenglNode
from UVT.hooked import gl, glfw

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
    data = Input(None)
    out0_vrtx_bffr = Output(None)
    _kind = opengl.GL_ARRAY_BUFFER

    def calculate(self):
        self.out0_vrtx_bffr = VertexBufferObject(gl.glGenBuffers(1))


class ConIndexBuffer(BufferComponent):
    data = Input(None)
    out0_indx_bffr = Output(None)
    _kind = opengl.GL_ELEMENT_ARRAY_BUFFER

    def calculate(self):
        self.out0_indx_bffr = IndexBufferObject(gl.glGenBuffers(1))


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

    def calculate(self):
        gl.glBindBuffer(self.in0_bffr.kind, self.in0_bffr.id)
        gl.glBufferData(self.in0_bffr.kind,
                        self.in1_data.bytesize,
                        self.in1_data.data,
                        gl.GL_STATIC_DRAW)
        self.out0_data_bffr = DataBufferObject(self.in0_bffr, self.in1_data)


# class ConIndexBuffer(ConVertexBuffer):
#     def __init__(self, window: Window):
#         if window._windows.get_current() == window:
#             self._id = window.gl.glGenBuffers(1)
#         self._kind = window.gl.GL_ELEMENT_ARRAY_BUFFER
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
