from ._node import Node, Input, Output
from ..data_types import Bound


class DataNode(Node):
    pass


class ConBound(DataNode):
    start = Input(0)
    end = Input(1)
    value_out = Output(Bound())

    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self.value_out = Bound(start, end)