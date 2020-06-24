import numpy as np

"""
Conventions:
1. if a component has no input but single output, given value is the output named 'value'

"""

class InterfaceValueContainer:
    """
    Value container used to hold interface value
    """
    def __init__(self, kind, value):
        self._kind = kind
        self._value = value

    def __str__(self):
        return f"< {self._kind.upper()} : {self._value} >"

    def __add__(self, other):
        if isinstance(other, InterfaceValueContainer):
            return self._value + other._value
        elif isinstance(other, (int, float)):
            return self._value + other
        else:
            raise NotImplementedError

class Interface:
    """
    Interface node for input and output

    To control setting value
    """

    def __init__(self, name, default_value):
        self._name = f'_{name}'
        self._default_value = default_value

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer
        :param instance:
        :param value:
        :return:
        """
        # maintain InterfaceValueContainer instance when possible
        if hasattr(instance, self._name):
            getattr(instance, self._name)._value = value
        else:
            setattr(instance, self._name, InterfaceValueContainer(self._kind, value))

    def __get__(self, instance, owner):
        return instance.__dict__.setdefault(self._name, InterfaceValueContainer(self._kind, self._default_value))

    def __delete__(self, instance):
        """
        Returns attribute value to assigned default value

        :param instance:
        :return:
        """
        setattr(instance, self._name, InterfaceValueContainer(self._kind, self._default_value))


class Input(Interface):
    """
    Designate input value
    """
    _kind = 'input'


class Output(Interface):
    """
    Designate output value
    """
    _kind = 'output'


class AssignedInput(Interface):
    """
    Designate assigned(special) input
    """
    _kind = 'assigned_input'


class WindowInput(AssignedInput):
    def __init__(self):
        self._name = f'_{self._kind}_window'


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
    value = Output('value', 0)

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
