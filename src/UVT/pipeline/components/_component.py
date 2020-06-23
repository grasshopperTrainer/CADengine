import numpy as np

"""
Conventions:
1. if a component has no input but single output, given value is the output named 'value'

"""


class Interface:
    """
    Interface node for input and output

    """

    def __init__(self, name):
        self._name = f'_{self.PREFIX}_{name}'

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __get__(self, instance, owner):
        return instance.__dict__.setdefault(self._name, None)


class Input(Interface):
    PREFIX = 'input'


class Output(Interface):
    PREFIX = 'output'

class AssignedInput(Input):
    PREFIX = 'assigned_input'

class WindowInput(AssignedInput):
    def __init__(self):
        self._name = f'_{self.PREFIX}_window'


class Component:
    """
    Component type
    """

    def input_placeholder(self):
        pass

    def output_placeholder(self):
        pass

    def operate(self):
        NotImplementedError


class DataComponent(Component):
    pass


class Integer(DataComponent):
    value = Output('value')

    def __init__(self, value=0):
        self.value = value

    def operate(self, **kwargs):
        return self.value


class Bound(DataComponent):

    def __init__(self, start=None, end=None):
        start = 0 if start is None else start
        end = 0 if end is None else end
        self._data = np.array([start, end])

    def __len__(self):
        return self._data[1] - self._data[0]

    @property
    def start(self):
        return self._data[0]

    @property
    def end(self):
        return self._data[1]
