"""
Conventions:
1. if a component has no input but single output, given value is the output named 'val_out'
1. Components can have relationship only inside ComplexComponent
1. Vertex, Buffer, Attribute, Array = vrtx, bffr, attr, arry
"""


import numpy as np
import heapq
from collections import namedtuple, deque, OrderedDict
from collections.abc import Iterable
import weakref as wr
import inspect
import warnings
if __name__ != '__main__':
    from ..data_types import *


class NodeSpvr:
    """
    Supervisor of nodes

    Stores relationship and hierarchy between nodes
    Only cares relationship between
    """

    def __init__(self, inst):
        self._graph = {}
        self._needto_update = wr.WeakSet()

        self._graph[inst] = {'dist':0, 'rels':{}}
        self._needto_update.add(inst)

    def _relate(self, this_node, out_name, inp_name, right_node):
        """
        Write down relationship

        Literally imagine two nodes connected by a line,
        of which two ends from left to right are the output and the input of two nodes.
        :param this_node: node pushing data to right
        :param out_name: attribute name of left node's output interface
        :param inp_name: attribute name of right node's input interface
        :param right_node: node accepting data from left
        :return:
        """
        self.rels(this_node).setdefault(out_name, {}).setdefault(right_node, set()).add(inp_name)

    def build_rel(self, out, inp):
        """
        Build relationship between two nods via interfaces

        :param out:
        :param inp:
        :return:
        """

        l_supv, r_supv = out.intf_holder._node_spvr, inp.intf_holder._node_spvr
        # two graphs are islands so need to be merged beforehand
        is_merged = False

        if l_supv != r_supv:
            # simply update dict and assign new supervisor to instances(nodes)
            l_supv._graph.update(r_supv._graph)
            for node in r_supv._graph:
                node._node_spvr = l_supv
            is_merged = True

        # check distance and update if needed
        supv = l_supv
        l_node, r_node = out.intf_holder, inp.intf_holder

        # loop check ?
        # check only relationships is being built within an island
        # and right is before left
        if not is_merged:
            for nxt_node in supv._node_rightward(r_node):
                if nxt_node == l_node:
                    warnings.warn("Trying to make a look. Connection not accepted")
                    return
                if supv.dist(nxt_node) > supv.dist(l_node):
                    break

        # write relationship and calculate distance,
        # push value, push r_node to update que as new value has been just pushed
        supv._relate(l_node, out.intf_name, inp.intf_name, r_node)
        supv._graph[r_node]['dist'] = max((self.dist(r_node), supv.dist(l_node) + 1))
        supv.push_needto_update(r_node)

        # update distance of all r_node's rightward
        # no need to align nodes. just que
        que = deque([r_node])

        while que:
            node = que.popleft()
            this_dist = supv.dist(node)
            for o, i, r_node in supv._node_full_rels(node):
                if this_dist >= supv.dist(r_node):
                    supv._graph[r_node]['dist'] = this_dist + 1
                    que.append(r_node)

    def disconnect(self, instance, intf):
        """
        Remove all connections of which one end is given interface
        :param instance:
        :param intf:
        :return:
        """
        # !Q does disconnection affect dist of nodes?
        # it doesn't violate hierarchy but could be cleaned to maintain dist understandable?
        # TODO: algorithm for maintaining nodes' (attr) dist relatively close
        if intf.intf_sign in (Input, Inout):
            for node, dist_rels in self._graph.items():
                for out, rights in dist_rels['rels'].items():
                    for right, inps in rights.items():
                        if right != instance:
                            continue
                        if intf.intf_name in inps:
                            inps.remove(intf.intf_name)
                            if not inps:
                                del rights[right]
                            break

        elif intf.intf_sign == Output:
            d = self.rels(instance)
            if intf.intf_name in d:
                for inp, rights in d.items():
                    for right, inps in rights.items():
                        for inp in inps:
                            # reset r_node's input into default value
                            delattr(right, inp)
                del d[intf]
        else:
            raise NotImplementedError
        self.push_needto_update(instance)

    def push_needto_update(self, instance):
        """
        Push into need to upadate que

        Needing to update means node's (def) operate has to executed to update output value.
        :param instance:
        :return:
        """
        self._needto_update.add(instance)

    def dist(self, node):
        """
        Hierarchial identifier

        Closer to 0 means it has to be calculated beforehand.
        Higher means it has to be calculated later.
        :param node:
        :return:
        """
        return self._graph[node]['dist']

    def rels(self, node):
        """
        Return info dict describing rightward nodes of this node
        :param node:
        :return:
        """
        return self._graph[node]['rels']

    def update_tomake_updated(self, side, target_node=None):
        """
        Build update graph then push values consequently

        From update_que, find all nodes needing update in rightward order
        then for each execute (def) operate and push outputs rightward
        :return:
        """

        # adding i for dist(n) being the same
        # !Q is _update_que node that has run (def) operate or that has to run operate?
        for nxt_node in self._node_rightward(self._needto_update):
            # print('of', target_node)
            # print('     ', nxt_node, target_node, self.dist(nxt_node), self.dist(target_node))
            # if asking for input:
            # 1. leave it as needing to update
            # 2. don't try to generate output
            if nxt_node == target_node and side in (Input, Inout):
                break

            # all nodes before end_node can be calculated even if it doesn't affect end_node's value
            if self.dist(nxt_node) > self.dist(target_node):
                break

            if nxt_node in self._needto_update: # reset que
                self._needto_update.remove(nxt_node)

            nxt_node.calculate()  # run to update outputs
            # push outputs to next node
            for out, inp, r_node in self._node_full_rels(nxt_node):
                self.push_value(nxt_node, out, inp, r_node)

            # if asking for output:
            # 1. terminate after (def) operate run to generate fresh outputs
            if nxt_node == target_node and side == Output:
                # push next of nxt_node needto update and stop updating
                for out, inp, r_node in self._node_full_rels(nxt_node):
                    # if rights connected to inout
                    if getattr(nxt_node, out).intf_sign == Inout:
                        continue
                    self._needto_update.add(r_node)
                break

    def push_value(self,push_from, out, inp, push_into):
        """
        Passing intf value to next intf

        ! don't mix interface value setting and interface value pushing
        :param push_from:
        :param out:
        :param inp:
        :param push_into:
        :return:
        """
        getattr(push_into, inp)._intf_obj = getattr(push_from, out)._intf_obj

    def _graph_full_rels(self):
        """
        Generator of all relationships

        :param node: relationship of
        :return: Generator('full_rel_info', ('output', 'input', 'right_node'))
        """
        np = namedtuple('graph_full_rels', ('dist', 'node', 'output', 'input', 'right_node'))
        for node, dist_rels in self._graph.items():
            for dist, rels in dist_rels.items():
                for out, rights in rels.items():
                    for right, inps in rights.items():
                        for inp in inps:
                            yield np(dist, node, out, inp, right)

    def _node_full_rels(self, node):
        """
        Generator relationships of given node

        :param node: relationship of
        :return: Generator('node_full_rels', ('output', 'input', 'right_node'))
        """
        np = namedtuple('node_full_rels', ('output', 'input', 'right_node'))
        for out, rights in self._graph[node]['rels'].items():
            for right, inps in rights.items():
                for inp in inps:
                    yield np(out, inp, right)

    def _node_rightward(self, roots):
        """
        Generator of rightward nodes

        Returns rightwards nodes of given roots in hierarchical order
        :param roots: Nodes tracking from. Multiple nodes can be given.
        :return: Generator
        """

        if isinstance(roots, Iterable):
            heap = list([(self.dist(n), i, n) for i, n in enumerate(roots)])
            entry = len(roots)
            visited = set(roots)
        else:
            heap = [(self.dist(roots), 0, roots)]
            entry = 1
            visited = {roots}

        heapq.heapify(heap)
        while heap:
            dist, _, node = heapq.heappop(heap)
            yield node
            for out, rights in self.rels(node).items():
                for right, ins in rights.items():
                    if right not in visited:
                        heapq.heappush(heap, (self.dist(right), entry, right))
                        visited.add(right)
                        entry += 1

    def __len__(self):
        return len(self._graph)

# This approach failed as initializing superclass without knowing what it is impossible
# class IntfObj:
#     _wrapper_classes = {}
#     def __new__(cls, instance, name, sign, value):
#         if type(value) in cls._wrapper_classes:
#             typ = cls._wrapper_classes[type(value)]
#         else:
#             if value is None:
#                 clsname = f"intf_{type(value).__name__}"
#                 typ = type(clsname, (_IntfObj, ), {})
#             else:
#                 clsname = f"intf_{type(value).__name__}"
#                 typ = type(clsname, (_IntfObj, type(value)), {})
#             cls._wrapper_classes[value] = typ
#         print(typ, typ.__mro__)
#
#         inst = typ(instance, name, sign, value)
#         return inst


class IntfObj:
    """
    Wrapper storing additional properties to wrapped type

    From interface's view, instance of this is not assigned to another or removed until
    the intf is __delete__ -> meaning resetting to default value.
    """

    def __init__(self, instance, name, sign, value):
        """
        Store interface properties
        :param instance:
        :param name:
        :param sign:
        :param value:
        :return:
        """
        self._intf_holder = instance
        self._intf_is_deleted = False
        self._intf_name = name
        self._intf_sign = sign
        self._intf_obj = value  # real value wrapped

    def __str__(self):
        return f"< {self._intf_sign.__name__} : {type(self._intf_obj).__name__} : {self._intf_obj} >"

    @property
    def intf_name(self):
        return self._intf_name

    @property
    def intf_holder(self):
        return self._intf_holder
        # ins = self._intf_holder()
        # if ins is None:
        #     raise NotImplementedError
        # return ins

    @property
    def intf_sign(self):
        return self._intf_sign

    @property
    def intf_is_deleted(self):
        return self._intf_is_deleted

    @property
    def real_value(self):
        return self._intf_obj
    @property
    def r(self):
        """
        Return real wrapped object(value)

        :return:
        """
        return self._intf_obj

    def isinstance(self, typ):
        """
        Could not find way wrapping isinstance(obj, typ). Use this for now.

        :param typ:
        :return:
        """
        return isinstance(self._intf_obj, typ)

    def __radd__(self, other):
        if isinstance(other, IntfObj):
            return self.real_value.__radd__(other._intf_obj)
        return self.real_value.__radd__(other)

    def __add__(self, other):
        if isinstance(other, IntfObj):
            return self._intf_obj.__add__(other._intf_obj)
        return self.real_value.__add__(other)

    def __sub__(self, other):
        if isinstance(other, IntfObj):
            return self._intf_obj.__sub__(other._intf_obj)
        return self._intf_obj.__sub__(other)

    def __truediv__(self, other):
        if isinstance(other, IntfObj):
            return self._intf_obj.__truediv__(other._intf_obj)
        return self._intf_obj.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, IntfObj):
            return self._intf_obj.__floordiv__(other._intf_obj)
        return self._intf_obj.__floordiv__(other)

    def __mul__(self, other):
        if isinstance(other, IntfObj):
            return self._intf_obj.__mul__(other._intf_obj)
        return self._intf_obj.__mul__(other)


    def __iter__(self):
        return self.r.__iter__()


    def __next__(self):
        return self.r.__next__()

    def __getitem__(self, item):
        return self._intf_obj.__getitem__(item)

    def __getattr__(self, item):
        return getattr(self._intf_obj, item)


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

        self._accepted_typs = typs if isinstance(typs, (tuple, list)) else (typs, )

        if self._has_siblings:
            self._record_name = f'_{self.__class__.__name__}_{self._name}_{self.SIBLING_POSTFIX}_0'
        else:
            self._record_name = f"_{self.__class__.__name__}_{self._name}"

        self._def_val = def_val

    @property
    def has_siblings(self):
        return self._has_siblings

    def __set__(self, instance, value):
        """
        !!! only input triggers (def) push to update que

        :param instance:
        :param value:
        :return:
        """


    def __get__(self, instance, owner) -> IntfObj:
        """
        Getting input value

        !!! Getting input and output triggers (def) update
        1. make value up-to-date by telling node supervisor to update
        2. return intf value

        :param instance:
        :param owner:
        :return:
        """
        self._check_init(instance)
        instance._node_spvr.update_tomake_updated(type(self), instance)
        return getattr(instance, self._record_name)

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
        instance._node_spvr.disconnect(instance, getattr(instance, self._record_name))
        intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
        setattr(instance, self._record_name, intf_obj)

    def _check_init(self, instance):
        # moved into (class) Node's (def) __new__
        pass
        # """
        # Initiate interface
        #
        # 1. add attribute into the instance
        # 2. add signature's attribute set, e.g. _inputs, into the instance
        # 3. add node grapher to the instance
        # :param instance:
        # :return:
        # """
        # # add attribute
        # if not hasattr(instance, self._record_name):
        #     # 1 use default value if there isn't one
        #     intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
        #     setattr(instance, self._record_name, intf_obj)
        #
        #     # 2 collect instance attr_name, then set with sign
        #     typ_dict = instance.__dict__.setdefault('_intfs', OrderedDict())
        #     intf_dict = typ_dict.setdefault(type(self).__name__, OrderedDict())
        #     sib_list = intf_dict.setdefault(self._name, []) # make sibling list ahead
        #
        # # 3 add node grapher if there isn't
        # if not hasattr(instance, '_node_spvr'):
        #     setattr(instance, '_node_spvr', NodeSpvr(instance))

    def _set_intfobj(self, instance, value):
        """
        Sets value into IntfObj

        by differenciating raw and IntfObj value.
        :param instance: instance that holds interface pushing value into
        :param value: value to push
        :return:
        """
        intf_to_update = getattr(instance, self._record_name)

        if isinstance(value, IntfObj):   # new value is passed by another intf
            intf_to_update._intf_obj = value._intf_obj
        else:   # new value is a raw value
            intf_to_update._intf_obj = value

    def _typecheck(self, v):
        """
        Type check before setting value
        :param v:
        :return:
        """
        if not self._accepted_typs: # if not given, all type accepted
            return True
        else:
            v = v.r if isinstance(v, IntfObj) else v
            if callable in self._accepted_typs:
                if callable(v) :
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

    def __set__(self, instance, value):
        """
        Handles assigning python primitive to InterfaceValueContainer

        :param instance:
        :param value:
        :return:
        """
        self._typecheck(value)
        intf = getattr(instance, self._record_name)
        if isinstance(value, IntfObj):
            if value.intf_sign == Input: # if connecting input -> input interfaces
                raise AttributeError("direction should be (output) -> (input)")
            elif value.intf_sign == Output: # correct connection
                # rebuild relationship as relating is in default monopoly
                instance._node_spvr.disconnect(instance, intf)
                instance._node_spvr.build_rel(value, intf)
            elif value.intf_sign == Inout:
                instance._node_spvr.disconnect(instance, intf)
        else:
            # using inout node or putting raw value
            pass
        instance._node_spvr.push_needto_update(instance)
        self._set_intfobj(instance, value)

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
            new_intf._record_name = f"_{self.__class__.__name__}_{new_intf._name}"
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

    def __set__(self, instance, value):
        """
        Sets output value

        Only one case is accepted :
        Instance's internal operation trying to set value to the output
        else, output value of node is not allowed to be set as it's always the result of the node's (def) operate.
        And as (def) operate will only be run by (obj) _node_spvr, there is no need to set rightward to be updated.

        :param instance: Node
        :param value:
        :return:
        """
        self._typecheck(value)
        self._check_init(instance)
        # guess if assigning value is called inside the node
        calling_frame = inspect.currentframe().f_back
        frameinfo = inspect.getframeinfo(calling_frame)
        local_attr = inspect.getargvalues(calling_frame).locals
        # 3 guesses:
        # guess if the node has attribute named of function setting value in
        # guess if that attribute is a method
        # guess if 'self' is in local arg and is the node
        if hasattr(instance, frameinfo.function):
            if inspect.ismethod(getattr(instance, frameinfo.function)):
                if 'self' in local_attr and local_attr['self'] == instance:
                    self._set_intfobj(instance, value)
                    # if node's output is updated, right of it has to have values in and set to update
                    # pushing is needed for the case (def) operate is executed explicitly?
                    # or can't it be executed that way? -> it can't i suppose
                    # instance._node_spvr.push_rightward_update_que(instance, getattr(instance, self._record_name))
                    return
        raise AttributeError("Output can't be set explicitly")


class Inout(Input):
    """
    Special interface to handle connecting compound component's input to its internal component.
    """
    pass


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


class Node:
    """
    Component type

    """
    
    def __new__(cls, *args, **kwargs):
        """
        Initiate interface

        1. add node grapher to the instance
        2. add attribute into the instance
        3. add signature's attribute set, e.g. _inputs, into the instance
        :param args:
        :param kwargs:
        """

        ins = super().__new__(cls)

        # 1 add node grapher
        ins._node_spvr = NodeSpvr(ins)

        # 2 add interface attribute looking mro backward to correctly override
        for c in reversed(cls.__mro__):
            if hasattr(c, '__dict__'):
                for k, v in c.__dict__.items():
                    if isinstance(v, (Input, Output, Inout)):
                        intf_obj = IntfObj(ins, v._name, type(v), v._def_val)
                        setattr(ins, v._record_name, intf_obj)

                        # 2 collect instance attr_name, then set with sign
                        typ_dict = ins.__dict__.setdefault('_intfs', OrderedDict())
                        intf_dict = typ_dict.setdefault(type(v).__name__, OrderedDict())
                        sib_list = intf_dict.setdefault(k, []) # make sibling list ahead

        return ins

    @log_execution
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

    def add_sibling_interface(self, intf: IntfObj):
        owner, desc = self._get_desc(intf.intf_name)
        desc.add_sibling(self, owner)

    def _get_desc(self, intf_name):
        for cls in self.__class__.__mro__:
            if intf_name in cls.__dict__:
                return cls, cls.__dict__[intf_name]

        raise AttributeError(f"The component has no such interface '{intf_name}'")

    def siblings_of(self, intf):
        n = intf.intf_name
        if n in self.inputs:
            return list(self.inputs[n])
        elif n in self.outputs:
            return list(self.outputs[n])
        else:
            raise AttributeError(f"no such interface '{n}'")

    @property
    def inputs(self):
        if not hasattr(self, 'inputs_defaulted'):
            # defaulting
            for cls in reversed(type(self).__mro__):
                if hasattr(cls, '__dict__'):
                    for k, v in cls.__dict__.items():
                        if isinstance(v, Input):
                            getattr(self, k)

        return self.interfaces.get('Input', {})

    def set_inputs(self, *value):
        for intf_name, v in zip(self.inputs, value):
            setattr(self, intf_name, v)


    @property
    def outputs(self):
        return self.interfaces.get('Output', {})

    @property
    def interfaces(self):
        return self.__dict__.get('_intfs', {})

    def __str__(self):
        return f"< Comp '{type(self).__name__}' >"

    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    class Adder(Node):
        i = Input('')
        o = Output('')

        def operate(self):
            self.o = '_' + self.i.r + '_'


    class Join(Node):
        a = Input('')
        b = Input('')
        o = Output('')

        def operate(self):
            print('operate join')
            self.o = self.a + self.b

    class Up(Node):
        a = Input('')
        o = Output('')

        def operate(self):
            print('operate up')
            self.o = self.a.r.upper()

    class Operator(Node):
        a = Inout(def_val='', has_siblings=False, typs=str)
        o = Output()
        def __init__(self):
            self.join = Join()
            self.up = Up()

            # self.join.a = self.a
            # self.join.b = self.up.o

        def operate(self):
            self.join.a = self.a
            self.up.a = self.a
            self.join.b = self.up.o

            self.o = self.join.o

    a = Adder()
    a.i = 'hey'
    o = Operator()

    o.a = a.o
    # o.a = 'ddd'
    # print(o.join.a, o.join.b, o.join.o)
    print(o.o)
    print()
    # o.a = 'kkk'
    print(o.o)
    print(o._node_spvr._needto_update)
    print(o.up.o)
    print(o.o)
    # o.a = 'jjk'
    a.i = 'key'
    print('----------------------------')
    o.a = 'hii'

    #
    print(o.o)
    # #
    o.a = a.o
    a.i = 'ddd'
    for k, v in a._node_spvr._graph.items():
        print(k, v)
    #
    # print(a._node_spvr._needto_update)
    print('++++++++++++++++++++++++++++')

    print(o.o)
    for k, v in a._node_spvr._graph.items():
        print(k, v)

    a.i = 'err'

    print(o.o)
    a.i = 'eee'
    print(o.join.o)
    a.i = 'ike'
    o.a = 'eee'
    print(o.o)
    print(a.o)
    a.i = 'efj'
    print(a.o)
    print(o.o)
    print(o.up.o)
