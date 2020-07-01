from ._component import *


class MathComponents(Component):
    """
    Math operation components
    """
    pass


class Add(MathComponents):
    """
    Basic two number addition
    """
    a = Input(0)
    b = Input(0)
    vlaue_out = Output(0)

    def __init__(self):
        pass

    def operate(self):
        self.vlaue_out = self.a + self.b