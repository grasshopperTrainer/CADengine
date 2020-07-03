from .._component import *
from .gl_component import OpenglComponent
import OpenGL.GL as opengl
from collections.abc import Iterable


class VertexArrayComponent(OpenglComponent):
    pass

class ConVertexArray(VertexArrayComponent):
    """
    Contructs vertex array object
    """
    window = Input(None)
    vrtx_arry = Output(None)
    _kind = opengl.GL_VERTEX_ARRAY

    def operate(self):
        self.vrtx_arry = VertexArrayObject(self.gl.glGenVertexArrays(1))


class ConOpenglData(VertexArrayComponent):
    """
    Data to be used as openGL data

    :param attr_name: name of data
    :param value: iterable values
    :param dtype: data type
    :param vattro: vertex attribute object
    """
    name = Input(None)
    data = Input(None)
    dtype = Input(None)
    gl_data = Output(None)

    def __init__(self, attr_name, value, dtype):
        self.name = attr_name
        self.data = value
        self.dtype = dtype

    # @log_execution
    def operate(self):
        # define size
        if isinstance(self.data.r[0], (tuple, list)):
            size = len(self.data.r[0])
        else:
            size = len(self.data.r)

        # define data type
        if self.dtype.isinstance(str):
            dtype = np.dtype([(self.name.r, self.dtype.r, size)])
        else:
            raise NotImplementedError

        # format values
        if isinstance(self.data.r, Iterable):
            if isinstance(self.data[0], Iterable):
                value = [tuple([tuple(chunk)]) for chunk in self.data]
                arr = np.array(value, dtype=dtype)
            else:
                value = tuple([tuple(self.data.r)])
                arr = np.array(value, dtype=dtype)
        else:
            raise NotImplementedError
        self.gl_data = NamedData(arr)


class EnhanceVertexArray(VertexArrayComponent):
    """
    Make bond between vertex array, vertex buffer
    """
    in0_vrtx_arry = Input()
    in1_vrtx_data_bffr = Input(has_siblings=True)
    in2_indx_data_bffr = Input()
    out0_vrtx_arry = Output()

    def operate(self):
        self.gl.glBindVertexArray(self.in0_vrtx_arry.id)
        idx = 0
        # bind all given attribute data in given order
        for bffred_attr in (self.in1_vrtx_data_bffr, *self.siblings_of(self.in1_vrtx_data_bffr)):
            self.gl.glBindBuffer(self.gl.GL_ARRAY_BUFFER, bffred_attr.id)
            for name, size, dtype, stride, offset in bffred_attr.properties:
                self.gl.glEnableVertexAttribArray(idx)
                self.gl.glVertexAttribPointer(
                    index=idx,
                    size=size,
                    type=dtype,
                    normalized=False,
                    stride=stride,
                    pointer=offset
                )
                idx += 1
        if self.in2_indx_data_bffr.r is not None:
            self.gl.glBindBuffer(self.gl.GL_ELEMENT_ARRAY_BUFFER, self.in2_indx_data_bffr.id)
            # print('dddddddddddddddddddddd')
            # self.gl.glEnableVertexAttribArray(0)
            # for name, size, dtype, stride, offset in self.in2_indx_data_bffr.properties:
            #     print(dtype, type(dtype))
            #     print(name, size, dtype, stride, offset)
            #     self.gl.glVertexAttribPointer(
            #         index=0,
            #         size=size,
            #         type=dtype,
            #         normalized=False,
            #         stride=stride,
            #         pointer=offset
            #     )
        self.gl.glBindVertexArray(0)

        self.out0_vrtx_arry = self.in0_vrtx_arry


class EnableVertexAttribute(VertexArrayComponent):
    """
    Push vertex attribute properties into vertex array
    """
    vrtx_attr = Input(None)
    vrtx_arry = Input(None)
    vrtx_arry_out = Output(None)

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

    vrtx_arry = Input(None)
    vrtx_bffr = Input(None)
    vrtx_arry_out = Output(None)

    def operate(self):
        self.gl.glBindVertexArray(self.vrtx_arry.id)
        self.gl.glBindBuffer(self.vrtx_bffr.kind, self.vrtx_bffr.id)
        self.vrtx_arry_out = self.vrtx_arry