"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
1. Vertex, Buffer, Attribute, Array = vrtx, bffr, attr, arry
"""

import inspect
from collections import deque, OrderedDict
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


class MaintainCachedValue:
    """
    Tells to maintain already CachedValue
    """
    pass


class _NodeMember(FamilyMember):

    def __init__(self):
        super().__init__()
        # calculation flags
        self._calculated = False
        self._calculation_status = ''
        self._calculate_permanent = False

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
        return self._calculated

    def set_calc_permanent(self):
        self._calculate_permanent = True
        self._calculated = False

    def reset_calc_permanent(self):
        self._calculate_permanent = False

    def _run_calculation(self):
        raise NotImplementedError

    def _reset_calc_downstream(self, visited=None, debug =''):
        """
        Reset child's calculation
        :return:
        """
        if visited == None:
            visited = set()
        if self._is_calculated():
            self._reset_calculated()
            for child in self.fm_all_children():
                if child not in visited:
                    visited.add(child)
                    child._reset_calc_downstream(visited, debug=debug + '    ')

    def _calculated_upstream(self, _visited=None, debug=''):
        """
        calculated upstream to get up-to-date result

        :param _visited:
        :param debug:
        :return:
        """
        # print("CALC", debug, self, self._is_calculated())
        # initiate recursion
        if _visited is None:
            _visited = set()
        # base condition
        if self._is_calculated():
            # self._push_value_downstrem()
            # if isinstance(self, _OutputIntf):
            #     for i in self.fm_all_children():
            #         i._value = self._value
            return True
        # if no parent node exist
        is_parent_recalculated = True
        for member in self.fm_all_parents():
            if not isinstance(member, _NodeMember):
                continue
            if member not in _visited:
                _visited.add(member)
                # check if parent is calculated after calculation
                # if not, it means parent is set to be calculated permanently so
                # self as child should reset calculated
                is_parent_recalculated = is_parent_recalculated and member._calculated_upstream(_visited, debug=debug+'   ')
        # set beforehand not to trigger infinite loop while calling itself's input inside `calculate()`
        self._set_calculated()
        self._run_calculation()

        # if node is set to permanent recalculation reset calculated downstream
        if self._calculate_permanent or not is_parent_recalculated:
            self._reset_calculated()
        else:
            self._set_calculated()
        return self._is_calculated()


class _NodeIntf(_NodeMember):
    """
    Contains cached value
    """

    def __init__(self, name, def_val, allow_sibling, typs=()):
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
        self._def_val = def_val
        self._value = def_val

        # attributes for recording group of interface
        self._family_name = self._name
        self._sibling_intf_allowed = allow_sibling
        self._next_sibling_id = 1

        # for typechecking
        self._typs = typs if isinstance(typs, (tuple, list)) else (typs,)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.group.interfaces[item]

    def __len__(self):
        return len(self.group)

    @property
    def family_name(self):
        """
        Return first interface of its kind

        Returns self if interface has no other siblings
        else return the origin of interface-group
        :return:
        """
        return self._family_name

    @property
    def name(self):
        return self._name

    @property
    def r(self):
        return self._value

    @property
    def sibling_intf_allowed(self):
        return self._sibling_intf_allowed

    def get_calculated_value(self):
        self._calculated_upstream()
        return self._value

    def set_provoke_value(self, value):
        """
        Set value method to be overriden

        Type check before setting value
        :param value:
        :return:
        """
        if not self._typs:  # if not given, all type accepted
            return True
        else:
            v = value.r if isinstance(value, _NodeIntf) else value
            if callable in self._typs:
                if callable(v):
                    return True
                elif isinstance(v, tuple(t for t in self._typs if t != callable)):
                    return True
            elif isinstance(v, self._typs):
                return True
            raise TypeError(f"{self.__class__.__name__} interface '{self._name}' accepts {self._typs}, not {v}")
        # actual setting is described inside overriden method

    def append_sibling_intf(self, value=NullValue('sibling intf no def value')):
        """
        Append interface that forms group with existing one
        :param value:
        :return:
        """
        # build new sibling interface
        sibling_name = f"{self._name}_{self._next_sibling_id}"
        sibling_intf = self.__class__(sibling_name, self._def_val, allow_sibling=True, typs=self._typs)
        sibling_intf._family_name = self._name
        self._next_sibling_id += 1
        # set value
        sibling_intf.set_provoke_value(value)
        # make body know interface
        # and add descriptor to handle node connecting convention
        if isinstance(self, _InputIntf):
            body = self.fm_get_child(0)
            self.fm_append_member(parent=sibling_intf, child=body)
            body.append_descriptor(Input(self._def_val, has_siblings=False, typs=self._typs, name=sibling_name))
        else:
            body = self.fm_get_parent(0)
            self.fm_append_member(parent=body, child=sibling_intf)
            body.append_descriptor(Output(self._def_val, has_siblings=False, typs=self._typs, name=sibling_name))
            print('appending output', self, body, body.fm_all_children())
            body._reset_calculated()

    def remove_sibling_intf(self, idx):
        raise NotImplementedError


class _InputIntf(_NodeIntf):
    """
    Container of input value
    """

    def __str__(self):
        return f"<input_intf '{self._name}' : {self._value}>"

    @property
    def group(self):
        return self.fm_get_child(0)

    def set_provoke_value(self, value):
        """
        Set interface value

        whilst building relationship
        and reseting calculted flag
        :param value:
        :return:
        """
        super().set_provoke_value(value)
        # by default relationship is monopoly so clear connection bidirectionally
        self.fm_clear_parent()
        # make relationship
        if isinstance(value, _NodeIntf):
            # set relationship between interface
            # by default direct setting goes to idx 0 of intf group
            self.fm_append_member(parent=value, child=self)
            value = value._value
        self._value = value
        self._reset_calc_downstream()

    def _run_calculation(self):
        """
        Nothing to do
        :return:
        """
        pass


class _OutputIntf(_NodeIntf):
    """
    Container of output value
    """

    def __str__(self):
        return f"<output_intf '{self._name}' : {self._value}>"

    @property
    def group(self):
        return self.fm_get_parent(0)

    def set_provoke_value(self, value):
        """
        Set value and do not build relationship even it's possible
        :param value:
        :return:
        """
        super().set_provoke_value(value)
        if isinstance(value, _NodeIntf):
            # pattern of delegating my output to internal node's output
            if isinstance(value, _OutputIntf):
                # remove relationship between body -> interface
                # this mono directional relationship needed as interface is a spec of body
                self.fm_remove(self.fm_get_parent(0), self.PARENT)
                # make stream between value -> interface
                self.fm_append_member(parent=value, child=self)
            # extract value
            value = value._value
        # set value
        self._value = value
        self._reset_calc_downstream()

    def _run_calculation(self):
        """
        Just push value downstream
        :return:
        """
        for i in self.fm_all_children():
            i._value = self._value


class _SiblingIntf(FamilyMember):
    def __init__(self, intf):
        super().__init__()
        self._intf = intf


class _SiblingElderIntf(_SiblingIntf):
    pass


class _SiblingYoungerIntf(_SiblingIntf):
    pass


class NodeBody(_NodeMember):
    """
    Node Body
    Inheritable for subclassing Node class

    """

    _NULL = NullValue

    def __init__(self, *args, **kwargs):
        super().__init__()

        # create relationship between node body and node interface

        input_dict, output_dict = {}, {}
        # to override in correct order
        for c in reversed(self.__class__.__mro__):
            if hasattr(c, '__dict__'):
                for k, v in c.__dict__.items():
                    if isinstance(v, (Input, Inout)):
                        input_dict[v._name] = v
                    elif isinstance(v, Output):
                        output_dict[v._name] = v
        for intf_name, v in input_dict.items():
            self.fm_append_member(parent=_InputIntf(intf_name, v._def_val, v._has_siblings, v._typs), child=self)

        for intf_name, v in output_dict.items():
            self.fm_append_member(parent=self, child=_OutputIntf(intf_name, v._def_val, v._has_siblings, v._typs))

        # input __init__ ing convention
        i = 0
        for intf in self.input_intfs:
            try:
                setattr(self, intf.name, args[i])
                i += 1
            except IndexError as e:
                break
            except Exception as e:
                raise e

        for k, v in kwargs.items():
            setattr(self, k, v)

    def print_status(self):
        if self._calculation_status:
            print('\033[93m')
            print(f"calculation fail of {self} :")
            print(self._calculation_status)
            print('\033[0m')

    def _run_calculation(self):
        # build input
        input_vs = OrderedDict()
        for intf in self.input_intfs:
            if intf.sibling_intf_allowed:
                input_vs.setdefault(intf.family_name, []).append(intf.get_calculated_value())
            else:
                input_vs[intf] = intf.get_calculated_value()
        # calculate
        try:
            results = self.calculate(*input_vs.values())
        except Exception as e:
            # set all outputs NULL
            results = [NullValue(f"calculation fail of {self}")] * len(list(self.output_intfs))
            # record status
            self._calculation_status = e
            self.print_status()
            raise e
        else:
            # wrap singular result
            results = [results] if not isinstance(results, (list, tuple)) else list(results)
            self._calculation_status = ''
        finally:
            # push calculation result downstream
            results = deque(results)
            for intf in self.output_intfs:
                # reset updated as input has been taken in consideration
                # intf._reset_calculated()
                # setting calculation result
                v = results.popleft() if results else NullValue('not enough number of values from calculation')
                intf.set_provoke_value(v)

    def calculate(self):
        """
        Execution of the component

        e.g. for (class) Add component, this method would actually
        add two numeric inputs and cache it into output interface.
        :return:
        """
        pass

    def refresh(self):
        """
        Forces recalculation by calling outputs
        :return:
        """
        # self._reset_calculated()
        self._reset_calc_downstream()
        self._calculated_upstream()

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
    def input_intfs(self):
        """
        Return input interface list
        :return:
        """
        return tuple(self.fm_iter_member(self.TYPEFILTER_ITOR(self.PARENT_ITOR(), _NodeMember)))

    @property
    def input_values(self):
        """
        Return all cached input values
        :return:
        """
        return (inp._value for inp in self.fm_all_parents())

    def get_input_intf(self, key):
        """
        Search and return by name or index of input interface
        :param key: name or index
        :return:
        """
        if isinstance(key, str):
            for i in self.input_intfs:
                if i.name == key:
                    return i
        elif isinstance(key, int):
            return self.input_intfs[key]
        raise KeyError

    @property
    def output_intfs(self):
        """
        Return output interface list
        :return:
        """
        return tuple(self.fm_iter_member(self.TYPEFILTER_ITOR(self.CHILDREN_ITOR(), _NodeMember)))

    def get_output_intf(self, key):
        """
        Search and return by name or index of output interface
        :param key: name or index
        :return:
        """
        if isinstance(key, str):
            for i in self.output_intfs:
                if i.name == key:
                    return i
        elif isinstance(key, int):
            return self.output_intfs[key]
        raise KeyError

    def get_intf(self, key):
        try:
            return self.get_input_intf(key)
        except KeyError:
            return self.get_output_intf(key)

    @property
    def output_values(self):
        """
        Returns all updated output values

        :return:
        """
        recalced_vs = []
        for i in self.output_intfs:
            i._calculated_upstream()
            recalced_vs.append(i._value)
        return recalced_vs

    @property
    def parent_nodes(self):
        return self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.PARENT_ITOR(), 3), NodeBody))

    @property
    def child_nodes(self):
        return self.fm_iter_member(self.TYPEFILTER_ITOR(self.LEVEL_ITOR(self.CHILDREN_ITOR(), 3), NodeBody))

    def __str__(self):
        return f"<Node '{type(self).__name__}'>"

    def __repr__(self):
        return self.__str__()

    def append_descriptor(self, descriptor):
        setattr(self.__class__, descriptor._name, descriptor)


class _IntfDescriptor:
    """
    Interface node for input and output

    To control setting value
    """
    SIBLING_POSTFIX = 'sib'

    def __init__(self, def_val=None, has_siblings=False, typs=(), name=None):
        if name is None:
            # parse initing code line identify name
            c = inspect.getframeinfo(inspect.currentframe().f_back).code_context[0]
            # info to be used creating actual interface object
            self._name = c.split(self.__class__.__name__)[0].strip().split('=')[0].strip()
        elif isinstance(name, str):
            self._name = name
        else:
            raise TypeError
        self._has_siblings = has_siblings
        self._def_val = def_val
        self._typs = typs

    @property
    def has_siblings(self):
        return self._has_siblings

    def __set__(self, instance, value):
        raise NotImplementedError


    def __get__(self, instance: NodeBody, owner):
        """
        Returns output value by wrapping with `IntfDeliverer`
        :param instance:
        :param owner:
        :return:
        """
        intf = instance.get_intf(self._name)
        intf._calculated_upstream()
        return intf

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
        intf = instance.get_input_intf(self._name)
        intf.set_provoke_value(value)


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
        intf = instance.get_output_intf(self._name)
        intf.set_provoke_value(value)

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
