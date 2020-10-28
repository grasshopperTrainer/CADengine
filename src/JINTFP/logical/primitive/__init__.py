from .._logical_nodes import *


class Equal(LogicalNode):
    in0_a = Input()
    in1_b = Input()
    out0_result = Output()

    def calculate(self, a, b):
        return (a == b,)
