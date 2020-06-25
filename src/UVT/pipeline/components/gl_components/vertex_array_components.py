from .._component import *
from .gl_component import OpenglComponent
from ..mess_toolbox import np_gl_type_convert
import OpenGL.GL as opengl


class VertexArrayComponent(OpenglComponent):
    pass

class ConVertexArray(VertexArrayComponent):
    """
    Contructs vertex array object
    """
    window = Input('window', None)
    vrtx_arry = Output('vrtx_arry', None)
    _kind = opengl.GL_VERTEX_ARRAY

    def operate(self):
        self.vrtx_arry = VertexArrayObject(self.gl.glGenVertexArrays(1))


class ConSingleVertexAttribute(VertexArrayComponent):
    """
    Constructs vertex attribute

    :param attr_name: name of the attribute
    :param value: iterable values
    :param dtype: data type
    :param vattro: vertex attribute object
    """
    attr_name = Input('attr_name', None)
    value = Input('value', None)
    dtype = Input('dtype', None)
    vrtx_attr = Output('vrtx_attr', None)

    def __init__(self, attr_name, value, dtype):
        self.attr_name = attr_name
        self.value = value
        self.dtype = dtype

    # @log_execution
    def operate(self):
        # define size
        if isinstance(self.value[0], (tuple, list)):
            size = len(self.value[0])
        else:
            size = 1

        # define data type
        if isinstance(self.dtype, str):
            dtype = np.dtype([(self.attr_name, self.dtype, size)])
        else:
            raise NotImplementedError

        # format values
        value = [tuple([tuple(chunk)]) for chunk in self.value]
        arr = np.array(value, dtype=dtype)

        self.vrtx_attr = VertexAttribObject(arr)


class EnableVertexAttribute(VertexArrayComponent):
    """
    Push vertex attribute properties into vertex array
    """
    vrtx_attr = Input('vrtx_attr', None)
    vrtx_arry = Input('vrtx_arry', None)
    vrtx_arry_out = Output('vrtx_arry', None)

    def operate(self):
        """
        Binds vertex array and enables, sets vertex attrib pointer
        :return:
        """
        self.gl.glBindVertexArray(self.vrtx_arry.id)
        for i, (name, size, dtype, stride, offset) in enumerate(self.vrtx_attr.properties):
            dtype = np_gl_type_convert(dtype)             # convert into OpenGL type
            offset = None if offset == 0 else offset    # None acts like 'void int'?

            self.gl.glEnableVertexAttribArray(i)
            self.gl.glVertexAttribPointer(
                index=i,
                size=size,
                type=dtype,
                normalized=False,
                stride=stride,
                pointer=offset
            )

class JoinVrtxArryVrtxBffr(VertexArrayComponent):
    """
    Make vertex array know vertex buffer
    """

    vrtx_arry = Input('vrtx_arry', None)
    vrtx_bffr = Input('vrtx_bffr', None)
    vrtx_arry_out = Output('vrtx_brrf_out', None)

    def operate(self):
        self.gl.glBindVertexArray(self.vrtx_arry.id)
        self.gl.glBindBuffer(self.vrtx_bffr.kind, self.vrtx_bffr.id)
