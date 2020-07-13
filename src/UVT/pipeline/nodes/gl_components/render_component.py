from .opengl_node import *
from .primitive.buffer_nodes import *
from .primitive.vertex_array_components import *
from .primitive.render_nodes import *

#
# class ConVrtxArrySet(OpenglNode):
#     out0_vrtx_arry = Output()
#     out1_vrtx_bffr = Output()
#     out2_indx_bffr = Output()
#
#     def __init__(self):
#         super().__init__()
#
#     def calculate(self):
#         self.out0_vrtx_arry = ConVertexArray().out0_vrtx_arry
#         self.out1_vrtx_arry = ConVertexBuffer().out0_vrtx_bffr
#         self.out2_vrtx_arry = ConIndexBuffer().out0_indx_bffr
