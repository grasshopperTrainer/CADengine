from .._opengl import *
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
        return VertexArrayObject(gl.glGenVertexArrays(1))

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
        super().__init__()
        self.in0_name = attr_name
        self.in1_data = data
        self.in2_dtype = dtype

    def calculate(self, name, data, dtype):
        # define size
        if isinstance(data[0], (tuple, list)):
            size = len(data[0])
        else:
            size = len(data)

        # define data type
        if isinstance(dtype, str):
            dtype = np.dtype([(name, dtype, size)])
        else:
            raise NotImplementedError

        # format values
        if isinstance(data, Iterable):
            if isinstance(data[0], Iterable):
                value = [tuple([tuple(chunk)]) for chunk in data]
                arr = np.array(value, dtype=dtype)

            else:
                value = tuple([tuple(data)])
                arr = np.array(value, dtype=dtype)
        else:
            raise NotImplementedError
        return NamedData(arr)


class EnhanceVertexArray(VertexArrayComponent):
    """
    Make bond between vertex array, vertex buffer
    """
    in0_vrtx_arry = Input()
    in1_vrtx_data_bffr = Input(has_siblings=True)
    in2_indx_data_bffr = Input()
    out0_vrtx_arry = Output()

    def calculate(self, vrtx_arry, vrtx_data_bffr, indx_data_bffr):
        gl.glBindVertexArray(vrtx_arry.id)
        idx = 0
        # bind all given attribute data in given order
        for bffred_attr in vrtx_data_bffr:
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

        if indx_data_bffr is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indx_data_bffr.bffr.id)

        gl.glBindVertexArray(0)

        return vrtx_arry

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
#         opengl.glBindVertexArray(self.vrtx_arry.id)
#         for i, (name, size, dtype, stride, offset) in enumerate(self.vrtx_attr.properties):
#             dtype = np_gl_type_convert(dtype)             # convert into OpenGL type
#             offset = None if offset == 0 else offset    # None acts like 'void int'?
#
#             opengl.glEnableVertexAttribArray(i)
#             opengl.glVertexAttribPointer(
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
#         opengl.glBindVertexArray(self.vrtx_arry.id)
#         opengl.glBindBuffer(self.vrtx_bffr.kind, self.vrtx_bffr.id)
#         self.vrtx_arry_out = self.vrtx_arry