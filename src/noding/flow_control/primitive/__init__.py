from .._flow_control_nodes import *
from collections import deque



class Stream(FlowControlNode):
    in0_idx = Input(def_val=0, typs=int)
    in1_data = Input()
    out0_data = Output(has_siblings=True)

    def calculate(self, idx, data):
        out = [NullValue() for i in range(len(self.out0_data))]
        out[idx] = data
        return out



class Gate(FlowControlNode):
    in0_idx = Input(def_val=0, typs=int)
    in1_data = Input(has_siblings=True)
    out0_data = Output()

    def __init__(self, idx):
        super().__init__()
        self.in0_idx = idx

    def calculate(self, idx, data):
        return data[idx]


class Conveyor(FlowControlNode):
    in0_size = Input(def_val=1, typs=int)
    in1_data = Input()
    out0_data = Output()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._que = deque()

    def calculate(self, size, data):
        if size <= len(self._que):
            poped = self._que.pop()
        else:
            poped = None
        self._que.appendleft(data)

        return (poped,)
