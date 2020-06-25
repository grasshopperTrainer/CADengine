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
    a = Input('a', 0)
    b = Input('b', 0)
    vlaue_out = Output('value_out', 0)

    def __init__(self):
        pass

    def operate(self):
        self.vlaue_out = self.a + self.b