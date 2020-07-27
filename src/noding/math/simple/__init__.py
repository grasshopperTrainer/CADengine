from .._math_nodes import *



class Add(MathNode):
    in0_a = Input()
    in1_b = Input(has_siblings=True)

    out0_result = Output()

    def calculate(self, a, b):
        return sum((a, *b))


class Subtract(MathNode):
    in0_a = Input()
    in0_b = Input()

    out0_result = Output()

    def calculate(self, a, b):
        return a - b


class Divide(MathNode):
    in0_a = Input()
    in1_b = Input()

    out0_result = Output()

    def calculate(self, a, b):
        return a / b


class Multiply(MathNode):
    in0_a = Input()
    in1_b = Input(has_siblings=True)

    out0_result = Output()

    def calculate(self, a, b):
        result = a
        for i in b:
            a *= i
        return result


