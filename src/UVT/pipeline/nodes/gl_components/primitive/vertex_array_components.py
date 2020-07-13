from ..._node import *
from ..opengl_node import OpenglNode
from UVT.hooked import gl, glfw
from collections.abc import Iterable


class VertexArrayComponent(OpenglNode):
    pass

class ConVertexArray(VertexArrayComponent):
    """
    Contructs vertex array object
    """
    out0_vrtx_arry = Output(None)
    _kind = opengl.GL_VERTEX_ARRAY

    def calculate(self):
        self.out0_vrtx_arry = VertexArrayObject(gl.glGenVertexArrays(1))


class ConOpenglData(VertexArrayComponent):
    """
    Data to be used as openGL data

    :param attr_name: name of data
    :param value: iterable values
    :param dtype: data type
    :param vattro: vertex attribute object
    """
    in0_name = Input(None)
    in1_data = Input(None)
    in2_dtype = Input(None)
    out0_gl_data = Output(None)

    def __init__(self, attr_name, data, dtype):
        self.in0_name = attr_name
        self.in1_data = data
        self.in2_dtype = dtype

    def calculate(self):
        # define size
        if isinstance(self.in1_data.r[0], (tuple, list)):
            size = len(self.in1_data.r[0])
        else:
            size = len(self.in1_data.r)

        # define data type
        if self.in2_dtype.isinstance(str):
            dtype = np.dtype([(self.in0_name.r, self.in2_dtype.r, size)])
        else:
            raise NotImplementedError

        # format values
        if isinstance(self.in1_data.r, Iterable):
            if isinstance(self.in1_data[0], Iterable):
                value = [tuple([tuple(chunk)]) for chunk in self.in1_data]
                arr = np.array(value, dtype=dtype)
            else:
                value = tuple([tuple(self.in1_data.r)])
                arr = np.array(value, dtype=dtype)
        else:
            raise NotImplementedError
        self.out0_gl_data = NamedData(arr)


class EnhanceVertexArray(VertexArrayComponent):
    """
    Make bond between vertex array, vertex buffer
    """
    in0_vrtx_arry = Input()
    in1_vrtx_data_bffr = Input(has_siblings=True)
    in2_indx_data_bffr = Input()
    out0_vrtx_arry = Output()

    def __init__(self, vrtx_arry, vrtx_data_bffr, indx_data_bffr):
        super().__init__()
        self.in0_vrtx_arry = vrtx_arry
        self.in1_vrtx_data_bffr = vrtx_data_bffr
        self.in2_indx_data_bffr = indx_data_bffr

    def calculate(self):
        gl.glBindVertexArray(self.in0_vrtx_arry.id)
        idx = 0
        # bind all given attribute data in given order
        for bffred_attr in (self.in1_vrtx_data_bffr, *self.siblings_of(self.in1_vrtx_data_bffr)):
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, bffred_attr.bffr.id)
            for name, size, dtype, stride, offset in bffred_attr.data.properties:
                gl.glEnableVertexAttribArray(idx)
                gl.glVertexAttribPointer(
                    index=idx,
                    size=size,
                    type=dtype,
                    normalized=False,
                    stride=stride,
                    pointer=offset
                )
                idx += 1

        if self.in2_indx_data_bffr.r is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.in2_indx_data_bffr.bffr.id)

        gl.glBindVertexArray(0)

        self.out0_vrtx_arry = self.in0_vrtx_arry

#
# class EnableVertexAttribute(VertexArrayComponent):
#     """
#     Push vertex attribute properties into vertex array
#     """
#     vrtx_attr = Input(None)
#     vrtx_arry = Input(None)
#     vrtx_arry_out = Output(None)
#
#     def calculate(self):
#         """
#         Binds vertex array and enables, sets vertex attrib pointer
#         :return:
#         """
#         gl.glBindVertexArray(self.vrtx_arry.id)
#         for i, (name, size, dtype, stride, offset) in enumerate(self.vrtx_attr.properties):
#             dtype = np_gl_type_convert(dtype)             # convert into OpenGL type
#             offset = None if offset == 0 else offset    # None acts like 'void int'?
#
#             gl.glEnableVertexAttribArray(i)
#             gl.glVertexAttribPointer(
#                 index=i,
#                 size=size,
#                 type=dtype,
#                 normalized=False,
#                 stride=stride,
#                 pointer=offset
#             )
#
#
# class JoinVrtxArryVrtxBffr(VertexArrayComponent):
#     """
#     Make vertex array know vertex buffer
#     """
#
#     vrtx_arry = Input(None)
#     vrtx_bffr = Input(None)
#     vrtx_arry_out = Output(None)
#
#     def calculate(self):
#         gl.glBindVertexArray(self.vrtx_arry.id)
#         gl.glBindBuffer(self.vrtx_bffr.kind, self.vrtx_bffr.id)
#         self.vrtx_arry_out = self.vrtx_arry