from .._component import *
from .gl_component import OpenglComponent
import inspect
import numpy as np
import OpenGL.GL as opengl
import glfw





class BufferComponent(OpenglComponent):
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
    data = Input('data', None)
    vrtx_bffr = Output('vrtx_bffr', None)
    _kind = opengl.GL_ARRAY_BUFFER

    def operate(self):
        self.vrtx_bffr = VertexBufferObject(self.gl.glGenBuffers(1))


class PushBufferData(BufferComponent):
    """
    Push value into a buffer using properties assigned in vertex attribute object
    """
    vrtx_attr = Input('vrtx_attr', None)
    vrtx_bffr = Input('vrtx_bffr', None)
    vrtx_attr_out = Output('vrtx_attr_out', None)
    vrtx_bffr_out = Output('vrtx_bffr_out', None)

    def operate(self):
        print(self.vrtx_bffr, self.vrtx_attr)
        self.gl.glBindBuffer(self.vrtx_bffr.kind, self.vrtx_bffr.id)
        self.gl.glBufferData(self.vrtx_bffr.kind,
                             self.vrtx_attr.bytesize,
                             self.vrtx_attr.value,
                             self.gl.GL_STATIC_DRAW)

        self.vrtx_attr_out = self.vrtx_attr
        self.vrtx_bffr_out = self.vrtx_bffr

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
