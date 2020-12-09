import weakref as wr
from collections import namedtuple, deque
from collections.abc import Iterable
import inspect
import warnings
import heapq

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

    def _relate(self, this_node, out, inp, right_node):
        """
        Write down relationship

        Literally imagine two nodes connected by a line,
        of which two ends from left to right are the output and the input of two nodes.
        :param this_node:
        :param out:
        :param inp:
        :param right_node:
        :return:
        """
        self.rels(this_node).setdefault(out, {}).setdefault(right_node, set()).add(inp)

    def build_rel(self, out, inp):
        """
        Build relationship between two nods via interfaces

        :param out:
        :param inp:
        :return:
        """

        l_supv, r_supv = out.intf_holder._comp_spvr, inp.intf_holder._comp_spvr
        # two graphs are islands so need to be merged beforehand
        is_merged = False
        if l_supv != r_supv:
            # simply update dict and assign new supervisor to instances(nodes)
            l_supv._graph.update(r_supv._graph)
            for node in r_supv._graph:
                node._comp_spvr = l_supv
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
        supv._relate(l_node, out, inp, r_node)
        supv._graph[r_node]['dist'] = supv.dist(l_node) + 1
        inp._intf_obj = out._intf_obj
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
        if intf.intf_sign == Input:
            print('disconnection', instance, intf)
            for node, dist_rels in self._graph.items():
                for out, rights in dist_rels['rels'].items():
                    for right, inps in rights.items():
                        if intf in inps:
                            inps.remove(intf)
                            if not inps:
                                del rights[right]
                            break

        elif intf.intf_sign == Output:
            d = self.rels(instance)
            if intf in d:
                for inp, rights in d.items():
                    for right, inps in rights.items():
                        for inp in inps:
                            # reset r_node's input into default value
                            delattr(right, inp.intf_name)
                del d[intf]
        else:
            NotImplementedError
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

    def update_tomake_updated(self, target_node=None):
        """
        Build update graph then push values consequently

        From update_que, find all nodes needing update in rightward order
        then for each execute (def) operate and push outputs rightward
        :return:
        """
        # adding i for dist(n) being the same
        # !Q is _update_que node that has run (def) operate or that has to run operate?
        for nxt_node in self._node_rightward(self._needto_update):
            # all nodes before end_node can be calculated even if it doesn't affect end_node's value
            if self.dist(nxt_node) > self.dist(target_node):
                break
            if nxt_node in self._needto_update: # reset que
                self._needto_update.remove(nxt_node)
            nxt_node.calculate()  # run to update outputs
            # push outputs to next node
            for out, inp, r_node in self._node_full_rels(nxt_node):
                inp._intf_obj = out._intf_obj

            if nxt_node == target_node:
                # push next of nxt_node needto update and stop updating
                for out, inp, r_node in self._node_full_rels(nxt_node):
                    self._needto_update.add(r_node)
                break

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
        Generator of relationships of given node

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
        self._intf_holder = wr.ref(instance)
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
        ins = self._intf_holder()
        if ins is None:
            raise NotImplementedError
        return ins

    @property
    def intf_sign(self):
        return self._intf_sign

    @property
    def intf_is_deleted(self):
        return self._intf_is_deleted

    @property
    def real_value(self):
        return self._intf_obj

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

    def __getitem__(self, item):
        return self._intf_obj.__getitem__(item)

    def __getattr__(self, item):
        return getattr(self._intf_obj, item)


class IntfDescriptor:
    """
    Interface node for input and output

    To control setting value
    """

    def __init__(self, def_val):
        # parse initing code line identify name
        c = inspect.getframeinfo(inspect.currentframe().f_back).code_context[0]
        self._name = c.split(self.__class__.__name__)[0].strip().split('=')[0].strip()
        self._record_name = f'_{self.__class__.__name__}_{self._name}'
        self._def_val = def_val

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
        instance._comp_spvr.update_tomake_updated(type(self), instance)
        return getattr(instance, self._record_name)

    def __delete__(self, instance):
        """
        Disconnection from output

        1. Remove connection in node graph
        2. Reset with default value

        :param instance:
        :return:
        """
        self._check_init(instance)
        instance._comp_spvr.disconnect(instance, getattr(instance, self._record_name))
        intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
        setattr(instance, self._record_name, intf_obj)

    def _check_init(self, instance):
        """
        Initiate interface

        1. add attribute into the instance
        2. add signature's attribute set, e.g. _inputs, into the instance
        3. add node grapher to the instance
        :param instance:
        :return:
        """
        # add attriute
        if not hasattr(instance, self._record_name):
            # 1 use default value if there isn't one
            intf_obj = IntfObj(instance, self._name, type(self), self._def_val)
            setattr(instance, self._record_name, intf_obj)
            # 2 collect instance attr_name, then set with sign
            inst_dict = instance.__dict__.setdefault('_intfs', {})
            inst_dict.setdefault(self, set()).add(self._record_name)
        # 3 add node grapher if there isn't
        if not hasattr(instance, '_comp_spvr'):
            setattr(instance, '_comp_spvr', NodeSpvr(instance))


class Input(IntfDescriptor):
    """
    Designate input value
    """

    def __set__(self, instance, value):
        """
        Handles assigning python dd to InterfaceValueContainer

        :param instance:
        :param value:
        :return:
        """
        self._check_init(instance)

        if isinstance(value, IntfObj):  # if connecting node to node
            if value.intf_sign == Input: # if connecting input -> input interfaces
                raise AttributeError("direction should be (output) -> (input)")

            instance._comp_spvr.disconnect(instance, getattr(instance, self._record_name))
            instance._comp_spvr.build_rel(value, getattr(instance, self._record_name))

        else:  # if putting raw value
            self.__delete__(instance)   # existing connection has to be removed as this is explicit __set__
            getattr(instance, self._record_name)._intf_obj = value


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
        And as (def) operate will only be run by (obj) _comp_spvr, there is no need to set rightward to be updated.

        :param instance: Node
        :param value:
        :return:
        """
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
                    value = value.real_value if isinstance(value, IntfObj) else value
                    getattr(instance, self._record_name)._intf_obj = value
                    # if node's output is updated, right of it has to have values in and set to update
                    # pushing is needed for the case (def) operate is executed explicitly?
                    # or can't it be executed that way? -> it can't i suppose
                    # instance._comp_spvr.push_rightward_update_que(instance, getattr(instance, self._record_name))
                    return
        raise AttributeError("Output can't be set explicitly")



if __name__ == '__main__':

    class K:
        def __init__(self, a, b):
            self.a = a
            self.b = b


    class A:
        i = Input(None)
        o = Output(None)

        def operate(self):
            self.o = self.i
            print('operation A')


    class B:
        first_in = Input('')
        second_in = Input('')
        o = Output(0)

        def operate(self):
            print('operation B')
            self.o = self.first_in + self.second_in

    class Upper:
        i = Input(None)
        o = Output(None)

        def operate(self):
            print('operate Upper')
            self.o = self.i.upper()

    class FirstLast:
        i = Input(None)
        o1 = Output(None)
        o2 = Output(None)

        def operate(self):
            print('operate FirstLast')
            self.o1 = self.i[0]
            self.o2 = self.i[-1]

    class Join:
        i1 = Input(None)
        i2 = Input(None)
        o = Output(None)

        def operate(self):
            print('operate Join')
            self.o = self.i1 + self.i2


    def text_two_nodes():

        node1, node2 = A(), B()
        print(node1.i, node1.o)
        node1.i = 'first in_'
        print(node1.o)
        print()
        node2.first_in = node1.o
        print(node2._comp_spvr._needto_update)
        node2.second_in = node1.o
        print('inputing two values done')
        print()
        node1.i = 'other in'
        print(node2.o)
        node2.second_in = 'this is second in'
        print(node2.o)
        node1.i = node2.o
        print()
        print()
        del node1.o
        print(node2.first_in)
        print(node1.o)

    def test_three_nodes():
        u, fl, j = Upper(), FirstLast(), Join()
        u.i = 'abc'
        fl.i = u.o
        j.i1 = fl.o1
        j.i2 = fl.o2
        print(j.o)
        j.i2 = u.o
        print(j.i1, j.i2, j.o)
        del j.i1
        j.i1 = 'new'
        print(j.o)
        fl.i = 'fff'
        print('ddd')
        j.i2 = fl.o1
        print(j.i1, j.i2)
        print(u.o)
        print(j.o)
        print(j._comp_spvr._needto_update)
        print(j.o)
        u.i = 'ddddd'
        for i in j._comp_spvr._node_full_rels(u):
            print(i)
        print(u.o)
        j.i1 = j.i2 = u.o
        print(j.o)
        u.i = '233'
        j.i2 = fl.o1
        u.i = fl.i = 'kk'
        print(j.o)
        print()
        del u.i
        del j.i1, j.i2
        print(j.o)
    test_three_nodes()