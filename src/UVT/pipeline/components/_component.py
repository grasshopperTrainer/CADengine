import numpy as np
import heapq
from collections import namedtuple

from ..data_types import *

"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
"""


# class InterfaceValueContainer:
#     """
#     Value container used to hold interface value
#     """
#     def __init__(self, kind, value):
#         self._kind = kind
#         self._value = value
#
#     def __str__(self):
#         return f"< {self._kind.upper()} : {self._value} >"
#     #
#     # def __add__(self, other):
#     #     if isinstance(other, InterfaceValueContainer):
#     #         return self._value + other._value
#     #     elif isinstance(other, (int, float)):
#     #         return self._value + other
#     #     else:
#     #         raise NotImplementedError
#
#     def __getattribute__(self, item):
#         try:
#             return super().__getattribute__(item)
#         except:
#             return getattr(self._value, item)


class Interface:
    """
    Interface node for input and output

    To control setting value
    """

    def __init__(self, name, def_val):
        self._name = name
        self._inst_attr_name = f'_{self._kind}_{name}'
        self._default_value = def_val

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer
        :param instance:
        :param value:
        :return:
        """
        instance.__dict__[self._inst_attr_name] = value

    def __get__(self, instance, owner):
        return instance.__dict__.setdefault(self._inst_attr_name, self._default_value)

    def __delete__(self, instance):
        """
        Returns attribute value to assigned default value

        :param instance:
        :return:
        """
        setattr(instance, self._inst_attr_name, self._default_value)


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


class AssignedInterface(Interface):
    """
    Designate assigned(special) input
    """
    _kind = 'assigned_input'


class WindowInput(AssignedInterface):
    def __init__(self, window):
        super().__init__('window', window)


def log_execution(func):
    """
    Decorator for logging method execution result
    :return:
    """
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_execution_log'):
            setattr(self, '_execution_log', {})
        try:
            func(self, *args, **kwargs)
            self._execution_log[func.__name__] = 'god execution'
        except Exception as e:
            self._execution_log[func.__name__] = f'bad execution : {e}'
    return wrapper

class Component:
    """
    Component type

    """

    def __new__(cls, *args, **kwargs):
        ins = super().__new__(cls)
        ins._initiate_interface()
        return ins

    def _initiate_interface(self):
        """
        Initiate all interface so values are already stored inside the instance
        :return:
        """
        for n, v in self.__class__.__dict__.items():
            if isinstance(v, Interface):
                getattr(self, n)

    @log_execution
    def operate(self):
        """
        Execution of the component

        e.g. for (class) Add component, this method would actually
        add two numeric inputs and cache it into output interface.
        :return:
        """
        NotImplementedError

class Relationship:
    """
    Relationship between two components
    """
    def __init__(self, left, out, inp, right):
        if not (isinstance(out, str) and isinstance(inp, str)):
            raise TypeError
        self._left = left
        self._out = out
        self._inp = inp
        self._right = right

    def push_rightward(self):
        """
        Push left's output into right's input
        :return:
        """
        setattr(self._right, self._inp, getattr(self._left, self._out))

    @property
    def right(self):
        return self._right
    @property
    def left(self):
        return self._left

class ComplexComponent(Component):
    """
    Component that operates using other components
    Chain of operations

    built by components and relationships between them
    """

    def __init__(self):
        # if render_window is not None:
        #     self.render_window = Window(render_window)
        # else:
        #     self.render_window = None

        self._components = set()
        self._rels = {}
        self._ends = set(), set()   # left right ends

    def get_interface_values(self):
        """
        Return all interface
        :return: nampedtuple( attribute_name, interface type, cached value )
        """
        interface = namedtuple('interface', ('attr_name', 'intf_type', 'cached_val'))
        interfaces = []
        for attr_name, v in self.__class__.__dict__.items():
            if isinstance(v, Interface):
                interfaces.append(interface(attr_name, type(v), getattr(self, attr_name)))
        return tuple(interfaces)

    def register(self, comp):
        """
        Make component visible by pipeline

        Pass assigned input if there is one
        :param comp:
        :return:
        """
        for attr_name, typ, cached_val in self.get_interface_values():
            if hasattr(comp, attr_name):
                for cls in comp.__class__.__mro__:
                    if attr_name in cls.__dict__:
                        intr = cls.__dict__[attr_name]
                        if isinstance(intr, typ) and isinstance(intr, AssignedInterface):
                            setattr(comp, attr_name, cached_val)
                            break
        self._components.add(comp)
        return comp

    def add_interface(self, interface):
        """
        Add new interface using it as descriptor
        :param interface:
        :return:
        """
        setattr(self.__class__, interface._name, interface)
        getattr(self, interface._name)

    def relate(self, left, outp, inp, right):
        """
        Build relationship between two components via output and input interface

        Think of a line connecting two functions from left to right.
        :param left: component evaluated before
        :param outp: output of left
        :param inp: input of right
        :param right: component evaluated latter
        :return:
        """
        self._rels.setdefault(left, []).append(Relationship(left, outp, inp, right))
        # see if components are at ends
        if left not in self._components:
            self.register(left)
            self._ends[0].add(left)
        elif left in self._ends[1]:
            self._ends[1].remove(left)

        if right not in self._components:
            self.register(right)
            self._ends[1].add(right)
        elif right in self._ends[0]:
            self._ends[0].remove(right)

    def eval_full_hierarchy(self):
        """
        Align components from left to right

        So that all components can have updated inputs.
        :return: ((component, depth), ...)
        """
        # temporarily full build only
        record = {comp: 0 for comp in self._components}

        entry = len(self._ends[0])  # not to compare components, need unique id
        comps = [(0, i, comp) for i, comp in enumerate(self._ends[0])]
        heapq.heapify(comps)

        while comps:
            depth, _, comp = heapq.heappop(comps)
            if depth < record[comp]:    # there is a longer path
                continue

            for rel in self._rels.get(comp, []):
                if depth+1 > record[rel.right]:   # looking for longest path
                    record[rel.right] = depth + 1
                    heapq.heappush(comps, (depth+1, entry, rel.right))
                    entry += 1

        return sorted(record.items(), key=lambda x: x[1])

    def operate(self):
        """
        Calculate by passing values incrementally

        :return:
        """
        for comp, depth in self.eval_full_hierarchy():
            # calculate using current inputs
            comp.operate()
            # update outputs to related right components
            for relation in self._rels.get(comp, []):
                relation.push_rightward()


class DataComponent(Component):
    pass


class Integer(DataComponent):
    value_out = Output('value_out', 0)

    def __init__(self, value=0):
        self.value_out = value

    def operate(self, **kwargs):
        return self.value_out

class ConBound(DataComponent):
    start = Input('start', 0)
    end = Input('end', 1)
    value_out = Output('value_out', Bound())

    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self.value_out = Bound(start, end)

