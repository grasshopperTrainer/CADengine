"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
1. Vertex, Buffer, Attribute, Array = vrtx, bffr, attr, arry
"""


import numpy as np
import heapq
from collections import namedtuple
import weakref as wr
from ..data_types import *


class IntfObj:
    """
    Wrapper storing additional properties to wrapped type
    """

    def __init__(self, instance, name, kind, value):
        """
        Store interface properties
        :param instance:
        :param name:
        :param kind:
        :param value:
        :return:
        """
        self._intf_instance = wr.ref(instance)
        self._intf_is_updated = True
        self._intf_is_deleted = False
        self._intf_name = name
        self._intf_kind = kind
        self._intf_obj = value  # real value wrapped

    def __str__(self):
        return f"< {self._intf_kind} : {self._intf_obj} >"

    @property
    def intf_name(self):
        return self._intf_name

    @property
    def intf_holder(self):
        ins = self._intf_is_updated()
        if ins is None:
            raise NotImplementedError
        return ins

    @property
    def intf_is_updated(self):
        return self._intf_is_updated

    @property
    def intf_kind(self):
        return self._intf_kind

    @property
    def intf_is_deleted(self):
        return self._intf_is_deleted

    @property
    def real_value(self):
        return self._intf_obj

    def __add__(self, other):
        return self.real_value.__add__(other)

    def __sub__(self, other):
        return self.real_value.__sub__(other)

    def __truediv__(self, other):
        return self.real_value.__truediv__(other)

    def __floordiv__(self, other):
        return self.real_value.__floordiv__(other)

    def __mul__(self, other):
        return self.real_value.__mul__(other)


# class IntfObjType(type):
#     """
#     Interface wrapped type builder
#
#     Builds new type inheriting type of wrapped value.
#     By doing this the wrapped object can fully respond like the original object.
#     It can evan pass (def) isinstance query.
#     """
#     _type_class = {}
#
#     def __new__(cls, ori_obj):
#         if ori_obj is None:
#             return None
#         ori_typ = type(ori_obj)
#         # to have single class wrapping a type
#         if ori_typ in cls._type_class:
#             return cls._type_class[ori_typ]
#
#         # else build new and force inherit (class) IntfObj that holds additional prop as interface
#         clsname = f"Intf_{ori_typ.__name__.capitalize()}"
#         bases = (ori_typ, IntfObj)
#
#         clss = super().__new__(cls, clsname, bases, {})
#         if issubclass(clss, (int, float, list, tuple, set, dict)):
#             clss.__init__ = ori_typ.__init__
#         else:
#             clss.__init__ = IntfObj.__init__
#
#         # register
#         cls._type_class[ori_typ] = clss
#         return clss
#
#     # def __init__(self, *args, **kwargs):
#     #     self._wrapper_instance = None
#     #     self._wrapper_name = None
#     #     self._wrapper_kind = None
#     #     self._wrapper_value = None


class Interface:
    """
    Interface node for input and output

    To control setting value
    """

    def __init__(self, name, def_val):
        self._name = name
        self._record_name = f'_{self._kind}_{name}'
        self._def_val = def_val

    def _init_interface(self, instance):
        """
        Guarantee there is the attribute and record of attributes
        :param instance:
        :return:
        """
        if not hasattr(instance, self._record_name):
            if self._def_val is None:
                intf_obj = None

            if self._def_val is not None:
                # build Interface Object type and object
                intf_obj = self._build_intf_obj(instance, self._def_val)
            instance.__dict__.setdefault('_' + self._kind + 's', set()).add(self._record_name)
            setattr(instance, self._record_name, intf_obj)

    def _build_intf_obj(self, instance, val):
        return IntfObj(instance, self._name, self._kind, val)

    def _set_output_need_update(self, instance):
        """
        Set all outputs updated
        :param instance:
        :return:
        """
        if hasattr(instance, '_outputs'):
            for att_name in instance._outputs:
                instance.__dict__[att_name]._intf_is_updated = True
                # getattr(instance, att_name)._intf_need_update = True

    def _update_upstream(self, instance):
        """
        Follows chain of interface backward and update values
        :param instance:
        :return:
        """
        need_calc = False
        # look through all inputs and check if any update has been made
        for attr_name in instance.__dict__.get('_inputs', []):
            intf_obj = getattr(instance, attr_name)
            if intf_obj.intf_is_updated:
                getattr(intf_obj.intf_holder, intf_obj.intf_name)  # recursion
                intf_obj._intf_is_updated = False
                need_calc = True

        for attr_name in instance.__dict__.get('_outputs', []):
            intf_obj = getattr(instance, attr_name)
            if intf_obj.intf_is_updated:
                need_calc = True

        if need_calc:
            instance.operate()  # operate is an assigned name
            # set all outputs updated
            self._set_output_need_update(instance)


class Input(Interface):
    """
    Designate input value
    """
    _kind = 'input'

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer
        :param instance:
        :param value:
        :return:
        """
        self._init_interface(instance)

        if isinstance(value, IntfObj):  # if connecting output input interfaces
            if value.intf_kind == 'input':
                raise AttributeError("direction should be (output) -> (input)")
            instance.__dict__[self._record_name] = value
            value._intf_is_updated = True
        else:  # if putting raw value
            setattr(instance, self._record_name, self._build_intf_obj(instance, value))

        # mark outputs updated so inputs referensing it can triger (def) operate
        self._set_output_need_update(instance)

    def __get__(self, instance, owner) -> IntfObj:
        self._init_interface(instance)
        # if interface is deleted replace it with default value
        intf_obj = getattr(instance, self._record_name)
        if intf_obj.intf_is_deleted:
            setattr(instance, self._record_name, self._build_intf_obj(instance, self._def_val))
            return getattr(instance, self._record_name)
        # input could have been set to update by its holder
        if intf_obj.intf_holder != instance and intf_obj.intf_is_updated:
            self._update_upstream(intf_obj.intf_holder)

        return intf_obj

    def __delete__(self, instance):
        """
        Disconnection from input

        Returns attribute value to assigned default value
        :param instance:
        :return:
        """
        intf_obj = IntfObj(instance, self._name, self._kind, self._def_val)
        instance.__dict__.setdefault('_' + self._kind + 's', set()).add(self._name)
        setattr(instance, self._record_name, intf_obj)

        # make all outputs updated so it calculates when called
        self._set_output_need_update(instance)


class Output(Interface):
    """
    Designate output value
    """
    _kind = 'output'

    def __set__(self, instance, value):
        self._init_interface(instance)
        # calling within component to set the result of operation
        if instance == getattr(instance, self._record_name).intf_holder:
            value = value.real_value if isinstance(value, IntfObj) else value
            getattr(instance, self._record_name)._intf_obj = value
        else:
            raise AttributeError("Output can't be set explicitly")

    def __get__(self, instance, owner):
        """
        Update output value by recursively looking all Input values
        :param instance:
        :param owner:
        :return:
        """
        self._init_interface(instance)
        self._update_upstream(instance)
        intf_obj = getattr(instance, self._record_name)
        intf_obj._intf_is_updated = False
        return intf_obj

    def __delete__(self, instance):
        """
        Disconnection from output

        1. raise removed flag of intf object so when it's called by another holder,
        it would remove old one and reset with its default value
        2. return output value to pre defined default value

        :param instance:
        :return:
        """

        intf_to_remove = getattr(instance, self._record_name)
        intf_to_remove._intf_is_deleted = True
        setattr(instance, self._record_name, self._build_intf_obj(instance, self._def_val))



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

    # def __new__(cls, *args, **kwargs):
    #     ins = super().__new__(cls)
    #     ins._initiate_interface()
    #     return ins

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
        setattr(self.__class__, interface._record_name, interface)
        getattr(self, interface._record_name)

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

