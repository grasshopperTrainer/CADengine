"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
1. Vertex, Buffer, Attribute, Array = vrtx, bffr, attr, arry
"""

import inspect
from collections import deque
from my_patterns import FamilyMember


class NullValue:
    """
    Null value

    For unable calculation
    """
    def __init__(self, comment=''):
        self._comment = comment

    def __str__(self):
        return f"NULL value : {self._comment}"


class _NodeMember(FamilyMember):
    pass

class _NodeIntfGroup(_NodeMember):
    """
    Member grouping Node Interfaces
    """
    def __init__(self, name, def_val, has_sibling_intf):
        super().__init__()
        self._name = name
        self._def_val = def_val
        self._has_sibling_intf = has_sibling_intf
        self._next_sibling_id = 1

    def __getitem__(self, item):
        return self.interfaces[item]

    def __iter__(self):
        return iter(self.interfaces)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.interfaces)

    def append_new_intf(self):
        pass
    def set_intf_value(self, *args):
        pass

    def append_sibling_intf(self, value):
        """
        Add sibling interface.
        :param value:
        :return:
        """
        if not self._has_sibling_intf:
            raise Exception("appending interface not allowed")
        self.append_new_intf()
        self.set_intf_value(len(self.interfaces)-1, value)
        self.node_body._reset_calculated()

        self._next_sibling_id += 1

    def remove_sibling_intf(self, idx):
        if idx == 0:
            raise IndexError("can't remove default interface")
        self.fm_remove_relationship(self, self.interfaces[idx])


class _InputIntfGroup(_NodeIntfGroup):
    def __init__(self, name, def_val, has_sibling_intf):
        super().__init__(name, def_val, has_sibling_intf)
        self.fm_append_member(parent=_InputIntf(name=f"{name}_0", value=def_val), child=self)

    def __str__(self):
        return f"<input_intf_group : '{self._name}'>"

    @property
    def interfaces(self):
        return self.fm_all_parents()

    @property
    def node_body(self):
        return self.fm_get_child(0)

    @property
    def intf_typ(self):
        return type(self.fm_get_parent(0))

    def append_new_intf(self):
        new_intf = self.intf_typ(f"{self._name}_{self._next_sibling_id}", self._def_val)
        self.fm_append_member(new_intf, self)

    def set_intf_value(self, idx, value):
        intf = self.interfaces[idx]
        # by default relationship is monopoly so clear connection bidirectionally
        intf.fm_clear_parent()
        # make relationship
        if isinstance(value, _NodeIntf):
            # set relationship between interface
            # by default direct setting goes to idx 0 of intf group
            intf.fm_append_member(parent=value, child=intf)
            value = value._value
        intf._value = value


class _OutputIntfGroup(_NodeIntfGroup):
    def __init__(self, name, def_val, has_sibling_intf):
        super().__init__(name, def_val, has_sibling_intf)
        self.fm_append_member(parent=self, child=_OutputIntf(name=f"{name}_0", value=def_val))

    def __str__(self):
        return f"<output_intf_group : '{self._name}'>"

    @property
    def interfaces(self):
        return self.fm_all_children()

    @property
    def node_body(self):
        return self.fm_get_parent(0)

    @property
    def intf_typ(self):
        return type(self.fm_get_child(0))

    def append_new_intf(self):
        new_intf = self.intf_typ(f"{self._name}_{self._next_sibling_id}", self._def_val)
        self.fm_append_member(parent=self, child=new_intf)


class _NodeIntf(_NodeMember):
    """
    Contains value with needed metadata for value delivery.
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

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.group.interfaces[item]

    def __len__(self):
        return len(self.group)

    @property
    def r(self):
        return self._value

    def append_sibling_intf(self, value=NullValue()):
        self.group.append_sibling_intf(value)

    def remove_sibling_intf(self, idx):
        self.group.remove_sibling_intf(idx)


class _InputIntf(_NodeIntf):
    """
    Container of input value
    """
    def __str__(self):
        return f"<input_intf '{self._name}' : {self._value}>"

    @property
    def group(self):
        return self.fm_get_child(0)


class _OutputIntf(_NodeIntf):
    """
    Container of output value
    """
    def __str__(self):
        return f"<output_intf '{self._name}' : {self._value}>"

    @property
    def group(self):
        return self.fm_get_parent(0)


class NodeBody(_NodeMember):
    """
    Node Body
    Inheritable for subclassing Node class

    """

    _NULL = NullValue

    def __init__(self, *args, **kwargs):
        super().__init__()
        # create relationship between node body and node interface
        self._calculated = False
        self._calculation_status = ''

        input_dict, output_dict = {}, {}
        # to override in correct order
        for c in reversed(self.__class__.__mro__):
            if hasattr(c, '__dict__'):
                for k, v in c.__dict__.items():
                    if isinstance(v, (Input, Inout)):
                        input_dict[v._name] = v
                    elif isinstance(v, Output):
                        output_dict[v._name] = v
        for name, v in input_dict.items():
            self.fm_append_member(parent=_InputIntfGroup(name, v._def_val, v._has_siblings), child=self)

        for name, v in output_dict.items():
            self.fm_append_member(parent=self, child=_OutputIntfGroup(name, v._def_val, v._has_siblings))

        # input __init__ ing convention
        i = 0
        for name, group in self.inputgroups.items():
            try:
                setattr(self, name, args[i])
                i += 1
            except IndexError as e:
                break
            except Exception as e:
                raise

        for k, v in kwargs.items():
            setattr(self, k, v)

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

    def _reset_calc_downstream(self, visited=None):
        """
        Reset child's calculation
        :return:
        """
        if visited == None:
            visited = set()
        if self._is_calculated():
            self._reset_calculated()
            for child in self.child_nodes:
                if child not in visited:
                    visited.add(child)
                    child._reset_calc_downstream(visited)

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
        for member in self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.PARENT_ITOR(), 5), NodeBody)):
            if member not in _visited:
                _visited.add(member)
                member._recalculate_upstream(_visited)
        # set beforehand not to trigger infinite loop while calling itself's input when `calculate()`
        self._set_calculated()
        try:
            self._run_calculateion()
        except Exception as e:
            # set all outputs NULL
            for group in self.outputgroups.values():
                for output in group:
                    output._value = self._NULL()
            # record status
            self._calculation_status = e
            self.print_status()
        else:
            self._calculation_status = ''
        finally:
            self._push_output_downstream()

    def _run_calculateion(self):
        # build input
        inputs = []
        for group in self.inputgroups.values():
            if group._has_sibling_intf:
                inputs.append(tuple(intf.r for intf in group))
            else:
                inputs.append(group[0].r)
        # calculate
        results = self.calculate(*inputs)
        if not isinstance(results, (list, tuple)):
            results = [results]

        results = deque(results)
        # setting calculation result
        for group in self.outputgroups.values():
            for intf in group:
                if results:
                    intf._value = results.popleft()
                else:
                    intf._value = NullValue('not enough value to unpack')

    def _push_output_downstream(self):
        for groups in self.outputgroups.values():
            for output in groups:
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
        self._reset_calculated()
        self._recalculate_upstream()

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
    def inputgroups(self):
        return {i._name:i for i in self.fm_all_parents()}

    @property
    def outputgroups(self):
        return {i._name:i for i in self.fm_all_children()}

    @property
    def interfaces(self):
        return {i._name:i for i in self.fm_all_parents()+self.fm_all_children()}

    @property
    def parent_nodes(self):
        return self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.PARENT_ITOR(), 5), NodeBody))

    @property
    def child_nodes(self):
        return self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.CHILDREN_ITOR(), 5), NodeBody))

    def __str__(self):
        return f"<Node '{type(self).__name__}'>"

    def __repr__(self):
        return self.__str__()


class _IntfDescriptor:
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

    def __get__(self, instance, owner) -> _NodeIntf:
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
        intf_obj = _NodeIntf(instance, self._name, type(self), self._def_val)
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

        if isinstance(value, _NodeIntf):  # new value is passed by another intf
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
            v = v.r if isinstance(v, _NodeIntf) else v
            if callable in self._accepted_typs:
                if callable(v):
                    return True
                elif isinstance(v, tuple(t for t in self._accepted_typs if t != callable)):
                    return True
            elif isinstance(v, self._accepted_typs):
                return True
            raise TypeError(f"{self.__class__.__name__} interface '{self._name}' accepts {self._accepted_typs}")


class Input(_IntfDescriptor):
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
        self._typecheck(value)
        instance._reset_calc_downstream()
        intf_group = instance.inputgroups[self._name]
        intf_group.set_intf_value(0, value)

    def __get__(self, instance: NodeBody, owner):
        """
        When input value asked make it up to date.
        :param instance:
        :param value:
        :return:
        """
        # don't run this node's calculation as only output is affected by calculation.
        for upper_node in instance.parent_nodes:
            upper_node._recalculate_upstream()
        return instance.inputgroups[self._name][0]


class Output(_IntfDescriptor):
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
        raise
        if isinstance(value, _NodeIntf):
            # for compound node, setting output with internal node's output
            value = value._value
        instance.outputgroups[self._name][0]._value = value

    def __get__(self, instance: NodeBody, owner):
        """
        Returns output value by wrapping with `IntfDeliverer`
        :param instance:
        :param owner:
        :return:
        """
        instance._recalculate_upstream()
        return instance.outputgroups[self._name][0]


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
