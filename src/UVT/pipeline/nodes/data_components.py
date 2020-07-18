from ._node import NodeBody, Input, Output
from ..data_types import Bound


class DataNodeBody(NodeBody):
    pass


class ConBound(DataNodeBody):
    start = Input(0)
    end = Input(1)
    value_out = Output(Bound())

    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self.value_out = Bound(start, end)