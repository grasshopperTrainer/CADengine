from .._opengl import *
from ....data_types import NamedData


class DeconNamedData(OpenglNode):
    """
    Reveals property of NameData type
    """

    in0_data = Input(typs=NamedData)
    out0_raw_data = Output()
    out1_names = Output()
    out2_sizes = Output()
    out3_types = Output()
    out4_strides = Output()
    out5_offsets = Output()
    out6_bytesize = Output()
    out7_shape = Output()

    def calculate(self, data: NamedData):
        flipped = [[] for i in range(len(data.properties[0]))]
        for props in data.properties:
            for i, lis in enumerate(flipped):
                lis.append(props[i])
        return data.data, *[tuple(lis) for lis in flipped], data.bytesize, data.shape
