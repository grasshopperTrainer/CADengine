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
    a = Input('a')
    b = Input('b')
    r = Output('r')

    def __init__(self):
        pass

    def operate(self):
        self.r = self.a + self.b