from ._component import Component, Input, Output
from ..data_types import Bound


class DataComponent(Component):
    pass


class ConBound(DataComponent):
    start = Input(0)
    end = Input(1)
    value_out = Output(Bound())

    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self.value_out = Bound(start, end)