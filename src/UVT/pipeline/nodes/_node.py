"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
1. Vertex, Buffer, Attribute, Array = vrtx, bffr, attr, arry
"""

import heapq
import traceback
import warnings
from collections import namedtuple, deque, OrderedDict
import inspect
from math import inf, isinf
from UVT.patterns import FamilyMember
if __name__ != '__main__':
    from ..data_types import *


class NullValue:
    """
    Null value

    For unable calculation
    """
    def __str__(self):
        return "NULL"


class NodeMember(FamilyMember):
    pass

class NodeInterfaceGroup(NodeMember):
    """
    Member to group Node Interfaces
    """
    def __init__(self, name):
        super().__init__()
        self._name = name

    def __getitem__(self, item):
        if isinstance(self.fm_get_parent(0), NodeBody):
            return self.fm_get_child(item)
        else:
            return self.fm_get_parent(item)

    def __iter__(self):
        if isinstance(self.fm_get_parent(0), NodeBody):
            return iter(self.fm_all_children())
        else:
            return iter(self.fm_all_parents())

    def __str__(self):
        return f"<node_{'output' if self.fm_has_parent() else 'input'}_group : '{self._name}'>"

    def __repr__(self):
        return self.__str__()

class NodeInterface(NodeMember):
    """
    Delivers interface value with needed metadata

    Wraps output data and delivers to input or not. Should be released after that. No other function.
    """

    def __init__(self, name, value):
        """
        Store interface properties
        :param instance:
        :param name:
        :param sign:
        :param value:
        :return:
        """
        super().__init__()
        self._name = name
        self._value = value

    def __str__(self):
        return f"<node_intf '{self._name}' : {self._value}>"

    def __repr__(self):
        return self.__str__()


class NodeBody(NodeMember):
    """
    Node Body
    Inheritable for subclassing Node class

    """

    _NULL = NullValue

    def __init__(self):
        super().__init__()
        # create relationship between node body and node interface
        self._calculated = False
        self._calculation_status = ''
        self._intfs = {}
        self._inputgroups = {}
        self._outputgroups = {}
        for c in reversed(self.__class__.__mro__):
            if hasattr(c, '__dict__'):
                for k, v in c.__dict__.items():
                    if isinstance(v, IntfDescriptor):
                        intfgroup = NodeInterfaceGroup(v._name)
                        intf = NodeInterface(f"{v._name}_0", v._def_val)
                        self._intfs[v._name] = intfgroup
                        if isinstance(v, (Input, Inout)):
                            self._inputgroups[v._name] = intfgroup
                            intfgroup.fm_append_parent(intf)
                            self.fm_append_parent(intfgroup)
                        elif isinstance(v, Output):
                            self._outputgroups[v._name] = intfgroup
                            intfgroup.fm_append_child(intf)
                            self.fm_append_child(intfgroup)

    def print_status(self):
        if self._calculation_status:
            print('\033[93m')
            print(f"calculation fail of {self} :")
            print(self._calculation_status)
            print('\033[0m')
    def _set_calculated(self):
        """
        Raise flag this node need output value update
        :return:
        """
        self._calculated = True

    def _reset_calculated(self):
        """
        Raise Flag this node output value updated
        :return:
        """
        self._calculated = False

    def _is_calculated(self):
        """
        Return update flag
        :return:
        """
        return self._calculated

    def _recalculate_upstream(self, _visited=None):
        if _visited is None:
            _visited = set()
        if self._is_calculated():
            return
        for member in self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.PARENT_ITERATOR(), 5), NodeBody)):
            if member not in _visited:
                _visited.add(member)
                member._recalculate_upstream(_visited)
        # set beforehand not to trigger infinite loop while calling itself's input when `calculate()`
        self._set_calculated()
        try:
            self.calculate()
        except Exception as e:
            for output in self.outputs:
                output._value = self._NULL()
            self._calculation_status = e
            self.print_status()
        else:
            self._calculation_status = ''
        finally:
            self._push_output_downstream()

    def _push_output_downstream(self):
        for output in self.outputs:
            for child in output.fm_all_children():
                child._value = output._value

    def calculate(self):
        """
        Execution of the component

        e.g. for (class) Add component, this method would actually
        add two numeric inputs and cache it into output interface.
        :return:
        """
        raise NotImplementedError

    def refresh(self):
        """
        Forces recalculation by calling outputs
        :return:
        """
        self._node_spvr.push_needto_update(self)
        self._node_spvr.update_tomake_updated(side=Output, target_node=self)

    def refresh_all(self):
        """

        :return:
        """
        raise NotImplementedError


    def _get_desc(self, intf_name):
        for cls in self.__class__.__mro__:
            if intf_name in cls.__dict__:
                return cls, cls.__dict__[intf_name]

        raise AttributeError(f"The component has no such interface '{intf_name}'")

    @property
    def inputs(self):
        for group in self._outputgroups.values():
            for output in group:
                yield output

    @property
    def outputs(self):
        for group in self._outputgroups.values():
            for output in group:
                yield output

    @property
    def intfs(self):
        return self._intfs

    def __str__(self):
        return f"<Node '{type(self).__name__}'>"

    def __repr__(self):
        return self.__str__()


class IntfDescriptor:
    """
    Interface node for input and output

    To control setting value
    """
    SIBLING_POSTFIX = 'sib'

    def __init__(self, def_val=None, has_siblings=False, typs=()):
        # parse initing code line identify name
        c = inspect.getframeinfo(inspect.currentframe().f_back).code_context[0]
        self._name = c.split(self.__class__.__name__)[0].strip().split('=')[0].strip()

        self._has_siblings = has_siblings
        self._siblings = {}
        # if self._has_siblings:
        #     self._cache_name = f'_{self.__class__.__name__}_{self._name}_{self.SIBLING_POSTFIX}_0'
        # else:
        #     self._cache_name = f"_{self.__class__.__name__}_{self._name}"

        self._def_val = def_val

        self._accepted_typs = typs if isinstance(typs, (tuple, list)) else (typs,)

    @property
    def has_siblings(self):
        return self._has_siblings

    def __set__(self, instance, value):
        raise NotImplementedError

    def __get__(self, instance, owner) -> NodeInterface:
        raise NotImplementedError

    def __delete__(self, instance):
        """
        Disconnection from output

        1. Remove connection in node graph
        2. Reset with default value

        :param instance:
        :return:
        """
        print('DELETING', instance, self._name)
        self._check_init(instance)
        instance._node_spvr.disconnect(instance, getattr(instance, self._cache_name))
        intf_obj = NodeInterface(instance, self._name, type(self), self._def_val)
        setattr(instance, self._cache_name, intf_obj)

    def _set_intfobj(self, instance, value):
        """
        Sets value into IntfObj

        by differenciating raw and IntfObj value.
        :param instance: instance that holds interface pushing value into
        :param value: value to push
        :return:
        """
        intf_to_update = getattr(instance, self._cache_name)

        if isinstance(value, NodeInterface):  # new value is passed by another intf
            intf_to_update._intf_obj = value._intf_obj
        else:  # new value is a raw value
            intf_to_update._intf_obj = value

    def _typecheck(self, v):
        """
        Type check before setting value
        :param v:
        :return:
        """
        if not self._accepted_typs:  # if not given, all type accepted
            return True
        else:
            v = v.r if isinstance(v, NodeInterface) else v
            if callable in self._accepted_typs:
                if callable(v):
                    return True
                elif isinstance(v, tuple(t for t in self._accepted_typs if t != callable)):
                    return True
            elif isinstance(v, self._accepted_typs):
                return True
            raise TypeError(f"{self.__class__.__name__} interface '{self._name}' accepts {self._accepted_typs}")


class Input(IntfDescriptor):
    """
    Designate input value
    """

    def __set__(self, instance: NodeBody, value):
        """
        Accepts output or raw value

        :param instance:
        :param value:
        :return:
        """
        if instance._is_calculated():
            # push needing refresh sign downstream
            for child in instance.fm_iter_member(instance.TYPEFILTER_ITOR(instance.PREORDER_ITOR(instance.CHILDREN_ITOR()), NodeBody)):
                child._reset_calculated()
        instance._reset_calculated()

        my_intf = instance._inputgroups[self._name].fm_get_parent(0)
        # by default relationship is monopoly so clear connection bidirectionally
        my_intf.fm_clear_parent()
        # make relationship
        if isinstance(value, NodeInterface):
            # set relationship between interface
            # by default direct setting goes to idx 0 of intf group
            my_intf.fm_append_parent(value)
            value = value._value
        my_intf._value = value

    def __get__(self, instance: NodeBody, value):
        """
        When input value asked make it up to date.
        :param instance:
        :param value:
        :return:
        """
        instance._recalculate_upstream()
        return instance._inputgroups[self._name][0]._value

    def add_sibling(self, instance, owner):
        """
        Add sibling input

        There might be cases where number of inputs is not identified initially.
        To address this kind of situation, it is possible to add input siblings.
        Sibling inputs a list of interfaces, which is understood to have same characteristics.
        Builder of a component can address to this interface while writing (def) operate via
        (attr) self._intfs.

        :param owner: Owner class of intf that has siblings
        :return:
        """
        if self._has_siblings:
            new_intf = self.__class__(def_val=self._def_val, has_siblings=False)
            idx = 1
            while idx in self._siblings:
                idx += 1
            new_intf._name = f"{self._name}_{self.SIBLING_POSTFIX}_{idx}"
            new_intf._cache_name = f"_{self.__class__.__name__}_{new_intf._name}"
            setattr(owner, new_intf._name, new_intf)
            self._siblings[idx] = new_intf._name

            # registering
            if isinstance(self, Input):
                if self._name in instance.inputs:
                    # both as a sibling and input
                    instance.inputs[new_intf._name] = []
                    instance.inputs[self._name].append(new_intf._name)
                else:
                    raise
            elif isinstance(self, Output):
                raise NotImplementedError
            else:
                raise TypeError
            return new_intf._name
        else:
            raise AttributeError(f"The interface does not have any siblings")


class Output(IntfDescriptor):
    """
    Output Interface

    Manages setting getting deleting output value
    """

    def __set__(self, instance: NodeBody, value):
        """
        Sets output value

        Do not explicitly set value. Value should be set via `calculate` method.
        :param instance: Node
        :param value:
        :return:
        """
        if isinstance(value, NodeInterface):
            # for compound node, setting output with internal node's output
            value = value._value
        instance._outputgroups[self._name][0]._value = value

    def __get__(self, instance: NodeBody, owner):
        """
        Returns output value by wrapping with `IntfDeliverer`
        :param instance:
        :param owner:
        :return:
        """
        instance._recalculate_upstream()
        return instance._outputgroups[self._name][0]


class Inout(Input):
    """
    Special interface to handle connecting compound component's input to its internal component.
    """
    pass


if __name__ == '__main__':
    class A(NodeBody):
        a = Input()
        b = Input()
        c = Input()
        oup = Output()

        def __init__(self, sign):
            super().__init__()
            self._sign = sign

        def calculate(self):
            print('cals', self, self.a)
            r = ''
            if self.a is not None:
                r += self.a
            if self.b is not None:
                r += self.b
            if self.c is not None:
                r += self.c
            self.oup = r

        def __str__(self):
            return f"<obj {self._sign}>"

        def __repr__(self):
            return self.__str__()


    m = {i: A(f"_{i}_") for i in 'abcdefghijklmn'}
    m['a'].a = 'A'
    m['b'].a = 10
    m['c'].a = m['a'].oup
    m['d'].a = m['a'].oup
    m['d'].b = m['b'].oup
    print(m['b'].oup)
    print(m['d'].oup)
    print()
    m['b'].a = '10'
    print(m['d'].oup)
    m['e'].a = 'C'
    m['f'].a = m['c'].oup
    m['f'].b = m['d'].oup
    m['g'].a = m['f'].oup
    m['g'].b = m['d'].oup
    m['g'].c = m['e'].oup
    print()
    print(m['g'].oup)
    #
    print('-----------------------------')

    m['a'].a = '0'
    # m['b'].a = '1'
    # m['c'].a = '2'
    print(m['g'].oup)
    m['a'].a = 'M'
    print(m['g'].oup)
    print()
    m['b'].a = '1'
    m['d'].a = 'D'
    print(m['g'].oup)
    print('+++++++++++++++++++++')
    m['e'].a = '3'
    m['a'].a = 'Z'
    print(m['e'].a)
    print(m['g'].oup)
    print(m['b'].oup)
