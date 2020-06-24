from ._component import *
import inspect
import numpy as np
import OpenGL.GL as opengl
import glfw


class OpenglComponent(Component):
    """
    OpenGL component type
    """

    @property
    def is_generated(self) -> bool:
        """
        Check if component is generated inside the context.
        :return:
        """
        if self._id is None:
            return False
        return True

    @property
    def is_renderable(self):
        raise NotImplementedError


class OpenglDataComponent(OpenglComponent):
    """
    Parent for data components using numpy array
    """
    value = Output('value', None)

    def __init__(self, data):
        if isinstance(data, (tuple, list)):
            self.value = np.array(data, dtype=self._dtype)
        elif isinstance(data, np.array):
            raise NotImplementedError

    @property
    def bytesize(self):
        if self.value is None:
            return 0
        return self.value.itemsize * self.value.size

    @property
    def itemsize(self):
        return self.value.itemsize

    @property
    def size(self):
        return self.value.size

    @property
    def is_renderable(self):
        return False


class FloatVector(OpenglDataComponent):
    _dtype = 'f'


class UnsignedIntVector(OpenglDataComponent):
    _dtype = 'uint'


class Window(OpenglComponent):
    window = Output('window', None)
    def __init__(self, w):
        self.window = w


class BufferComponent(OpenglComponent):
    """
    Buffer for Buffer component.

    Organizes creation of new buffer component.
    These classes have '(OpenGL)_id' attribute.
    """

    _children = {}
    _data_to_push = None
    _id = None

    def __str__(self):
        return f"<'{self.__class__.__name__}' of id : {self._id}>"

    @property
    def id(self):
        if not hasattr(self, '_id'):
            raise NotImplementedError
        return self._id

    @property
    def window(self):
        return self._window

    @property
    def kind(self):
        return self._kind

    @property
    def data_to_push(self):
        return self._data_to_push
    @data_to_push.setter
    def data_to_push(self, data):
        self._data_to_push = data

    def build(*args, **kwargs):
        raise NotImplementedError

    def bind(*args, **kwargs):
        raise NotImplementedError

    def input_data(*args, **kwargs):
        raise NotImplementedError

    def push_data(self):
        for k, v in self._children.items():
            if v is not None:
                v.push_data()

    @property
    def is_renderable(self):
        return False


class VertexArray(BufferComponent):
    window = Input('window', None)
    vbo = Input('vbo', None)
    ibo = Input('ibo', None)
    vao = Output('vao', None)

    def __init__(self):
        self._kind = opengl.GL_VERTEX_ARRAY

    def build(self):
        if not self.window.is_current:
            return

        # update data in gpu
        self.bind()
        self.push_data()
        self.window.gl.glEnableVertexAttribArray(0)
        self._children['vbo'].bind()
        self.window.gl.glVertexAttribPointer(
            index=0,
            size=3,
            type=self.window.gl.GL_FLOAT,
            normalized=self.window.gl.GL_FALSE,
            stride=0,
            pointer=None
        )



    def bind(self):
        self.window.gl.glBindVertexArray(self._id)


class VertexBuffer(BufferComponent):

    window = WindowInput()
    data = Input('data', None)
    vbo = Output('vbo', None)

    def __init__(self):
        self._kind = opengl.GL_ARRAY_BUFFER

    def bind(self):
        self.window.gl.glBindBuffer(self._kind, self._id)

    def input_data(self, data):
        data = FloatVector(self.window, data)
        self.data_to_push = data

    def push_data(self):
        for k, v in self._children:
            v.push_data()

        if self.data_to_push is None:
            pass
        else:
            self.bind()
            self.window.gl.glBufferData(self.kind,
                                        self.data_to_push.bytesize,
                                        self.data_to_push.value,
                                        self.window.gl.GL_STATIC_DRAW)


class IndexBuffer(VertexBuffer):
    def __init__(self, window: Window):
        if window._windows.get_current() == window:
            self._id = window.gl.glGenBuffers(1)
        self._kind = window.gl.GL_ELEMENT_ARRAY_BUFFER
        self._window = window

    def input_data(self, data):
        data = UnsignedIntVector(self.window, data)
        self.data_to_push = data


class RenderComponent(OpenglComponent):
    """
    Renderable components

    Render trigered by Window._run -> Pipeline.render -> RenderComponent.render
    """
    @property
    def is_renderable(self):
        return True

    def render(self):
        raise NotImplementedError


class DrawArrayComponent(RenderComponent):
    """
    Render components of glDrawArrays()
    """
    _kind = None


class DrawTriangle(DrawArrayComponent):
    """
    glDrawArrays(GL_TRIANGLES, ...)
    """

    _kind = opengl.GL_TRIANGLES

    def __init__(self):
        self._vao = None
        self._index_bound = Bound(0, 3)

    def render(self, w: Window):
        w.gl.glDrawArrays(self._kind, self._index_bound[0], self._index_bound[1]-self._index_bound[0])
        w.gl.glDisableVertexAttribArray(self._vao)


class Program(OpenglComponent):
    pass


class ShaderComponent(RenderComponent):
    pass

class FragmentShader(ShaderComponent):
    pass


class VertexShader(ShaderComponent):
    pass

